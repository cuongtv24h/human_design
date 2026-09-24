"""/api/v1/reports — preview, create (template sync / LLM background), view, export."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response
from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.reporting.contract import ContentMode, ReportRequest
from backend.reporting.export import bodygraph_svg
from backend.reporting.orchestrator import ReportOrchestrator

from ..deps import client_ip, current_user, get_db
from ..models import Client, Report, User
from ..files import file_response
from ..schemas import (
    CatalogSection, DownloadLinkIn, DownloadLinkOut, PreviewIn, PreviewOut, ReportCreate, ReportDetailOut, ReportList,
)
from ..security import sign_token
from ..services import (
    ARTIFACT_FORMATS, audit, chart_summary, create_report, get_client_or_404, get_report_or_404, report_detail,
    org_llm_config, report_summary, run_llm_generation, visible_reports, warm_artifacts,
)

from hd_time import display_birth  # noqa: E402

router = APIRouter(prefix="/reports", tags=["reports"])


def _values(payload) -> dict:
    return {"tier": payload.tier.value, "template": payload.template.value,
            "domains": [d.value for d in payload.domains]}


@router.post("/preview", response_model=PreviewOut)
def preview(payload: PreviewIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> PreviewOut:
    """Template-mode draft for the wizard's live preview. Nothing is stored."""
    if payload.client_id is not None:
        client = get_client_or_404(db, user, payload.client_id)
        subject = {"name": client.full_name, "birth_date": client.birth_date, "birth_time": client.birth_time,
                   "timezone": client.timezone, "birth_location": client.birth_place}
    elif payload.birth_date and payload.birth_time:
        subject = {"name": payload.full_name, "birth_date": payload.birth_date, "birth_time": payload.birth_time,
                   "timezone": payload.timezone, "birth_location": payload.birth_place}
    else:
        raise HTTPException(status_code=422, detail="Cần chọn khách hàng hoặc nhập ngày + giờ sinh.")
    try:
        request = ReportRequest.model_validate({"subject": subject, **_values(payload)})
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Dữ liệu không hợp lệ: {exc.errors()[0].get('msg')}") from exc
    document = ReportOrchestrator().run(request)
    s = document.subject
    return PreviewOut(
        subject_display=display_birth(s.birth_date, s.birth_time, s.timezone),
        summary=chart_summary(document.chart),
        sections=[CatalogSection(id=x.id, title=x.title) for x in sorted(document.sections, key=lambda i: i.order)],
        markdown=document.to_markdown(),
        bodygraph_svg=bodygraph_svg(document),
    )


@router.post("", response_model=ReportDetailOut, status_code=201)
def create(payload: ReportCreate, request: Request, background: BackgroundTasks,
           user: User = Depends(current_user), db: Session = Depends(get_db)) -> ReportDetailOut:
    client = get_client_or_404(db, user, payload.client_id)
    report = create_report(db, user, client, content_mode=payload.content_mode.value, **_values(payload))
    audit(db, user, "report.create", "report", report.id, ip=client_ip(request),
          content_mode=report.content_mode, tier=report.tier, template=report.template)
    db.commit()
    state = request.app.state
    if payload.content_mode is ContentMode.LLM:
        # Background task + heartbeat; interrupted jobs are resumed by backend/api/jobs.py.
        background.add_task(run_llm_generation, state.db.session_factory, report.id, user.email,
                            state.settings.artifact_dir, "generate",
                            org_llm_config(db, user.org_id, state.secret_key), state.settings.job_heartbeat_seconds)
    else:
        background.add_task(warm_artifacts, state.db.session_factory, state.settings.artifact_dir, report.id)
    return report_detail(report)


@router.get("", response_model=ReportList)
def list_reports(
    q: str = "", status: str = "", client_id: int | None = None,
    limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
    user: User = Depends(current_user), db: Session = Depends(get_db),
) -> ReportList:
    query = visible_reports(user)
    if status:
        query = query.where(Report.status == status)
    else:
        query = query.where(Report.status != "archived")
    if client_id is not None:
        query = query.where(Report.client_id == client_id)
    if q.strip():
        like = f"%{q.strip().lower()}%"
        query = query.where(or_(func.lower(Client.full_name).like(like), Report.id.like(like)))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(Report.created_at.desc()).limit(limit).offset(offset)).all()
    return ReportList(items=[report_summary(r) for r in rows], total=total)


@router.get("/{report_id}", response_model=ReportDetailOut)
def get_report(report_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ReportDetailOut:
    return report_detail(get_report_or_404(db, user, report_id))


@router.post("/{report_id}/archive", response_model=ReportDetailOut)
def archive(report_id: str, request: Request, user: User = Depends(current_user),
            db: Session = Depends(get_db)) -> ReportDetailOut:
    report = get_report_or_404(db, user, report_id)
    report.status = "archived"
    audit(db, user, "report.archive", "report", report.id, ip=client_ip(request))
    db.commit()
    return report_detail(report)


def _export(db: Session, request: Request, user: User, report_id: str, fmt: str, download: bool | None) -> Response:
    report = get_report_or_404(db, user, report_id)
    response = file_response(db, request.app.state.settings.artifact_dir, report, fmt, download)
    if "content-disposition" in response.headers:
        audit(db, user, "report.export", "report", report.id, ip=client_ip(request), format=fmt)
        db.commit()
    return response


@router.post("/{report_id}/links", response_model=DownloadLinkOut)
def download_link(report_id: str, payload: DownloadLinkIn, request: Request, user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> DownloadLinkOut:
    """Short-lived signed URL (plan P0-10, default 5 minutes) — works without a session cookie,
    e.g. to open on a phone or paste into Zalo for the client right now."""
    report = get_report_or_404(db, user, report_id)
    if not report.document:
        raise HTTPException(status_code=409, detail="Báo cáo chưa có nội dung.")
    state = request.app.state
    token, expires = sign_token(state.secret_key, "download",
                                {"r": report.id, "f": payload.format, "v": report.version, "u": user.id},
                                state.settings.download_link_seconds)
    audit(db, user, "report.link", "report", report.id, ip=client_ip(request), format=payload.format)
    db.commit()
    return DownloadLinkOut(url=f"/api/v1/files/{token}", expires_at=datetime.fromtimestamp(expires, timezone.utc))


@router.get("/{report_id}/markdown")
def markdown(report_id: str, request: Request, download: bool = True, user: User = Depends(current_user),
             db: Session = Depends(get_db)) -> Response:
    return _export(db, request, user, report_id, "markdown", download)


@router.get("/{report_id}/infographic.html")
def infographic(report_id: str, request: Request, download: bool = False, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> Response:
    return _export(db, request, user, report_id, "infographic", download)


@router.get("/{report_id}/bodygraph.svg")
def bodygraph(report_id: str, request: Request, download: bool = False, user: User = Depends(current_user),
              db: Session = Depends(get_db)) -> Response:
    return _export(db, request, user, report_id, "bodygraph_svg", download)


@router.get("/{report_id}/{fmt}")
def document_file(report_id: str, fmt: str, request: Request, download: bool = True,
                  user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    """PDF / DOCX built from the same ReportDocument as every other view."""
    if fmt not in ARTIFACT_FORMATS:
        raise HTTPException(status_code=404, detail="Định dạng không được hỗ trợ.")
    return _export(db, request, user, report_id, fmt, download)
