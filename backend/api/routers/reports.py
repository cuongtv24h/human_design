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
from ..models import Client, Organization, Report, User
from ..files import file_response
from ..schemas import (
    ApplyStyleIn,
    CatalogSection, DownloadLinkIn, DownloadLinkOut, PreviewIn, PreviewOut, ReportCreate, ReportDetailOut, ReportList,
    StyleRatingIn,
)
from ..security import sign_token
from ..services import (
    ARTIFACT_FORMATS, audit, chart_summary, create_report, get_client_or_404, get_report_or_404,
    org_llm_configs, org_var_map, report_detail, report_summary, resolve_custom_template,
    resolve_template_style, run_llm_generation, visible_reports, warm_artifacts,
)

from hd_time import display_birth  # noqa: E402

router = APIRouter(prefix="/reports", tags=["reports"])


def _values(payload) -> dict:
    return {"tier": payload.tier.value, "template": payload.template,
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
    custom_template = resolve_custom_template(db, user, payload.template)
    if payload.template not in ("sections", "operating_manual") and custom_template is None:
        raise HTTPException(status_code=422, detail="Mẫu báo cáo không tồn tại hoặc chưa được duyệt.")
    options: dict = {}
    if custom_template is not None:
        org = db.get(Organization, user.org_id)
        options = {"custom_template": custom_template, "org_vars": org_var_map(org)}
    try:
        request = ReportRequest.model_validate({"subject": subject, **_values(payload), "options": options})
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
    custom_template = resolve_custom_template(db, user, payload.template)
    if payload.template not in ("sections", "operating_manual") and custom_template is None:
        raise HTTPException(status_code=422, detail="Mẫu báo cáo không tồn tại hoặc chưa được duyệt.")
    org = db.get(Organization, user.org_id)
    style_profile = resolve_template_style(db, user, payload.template) if payload.use_style else None
    report = create_report(db, user, client, content_mode=payload.content_mode.value,
                           custom_template=custom_template,
                           org_vars=org_var_map(org) if custom_template else None,
                           style_profile=style_profile,
                           **_values(payload))
    audit(db, user, "report.create", "report", report.id, ip=client_ip(request),
          content_mode=report.content_mode, tier=report.tier, template=report.template)
    db.commit()
    state = request.app.state
    if payload.content_mode is ContentMode.LLM:
        # Background task + heartbeat; interrupted jobs are resumed by backend/api/jobs.py.
        background.add_task(run_llm_generation, state.db.session_factory, report.id, user.email,
                            state.settings.artifact_dir, "generate",
                            llm_configs=org_llm_configs(db, user.org_id, state.secret_key),
                            heartbeat_seconds=state.settings.job_heartbeat_seconds)
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


@router.patch("/{report_id}/style-rating", response_model=ReportDetailOut)
def style_rating(report_id: str, payload: StyleRatingIn, request: Request,
                 user: User = Depends(current_user), db: Session = Depends(get_db)) -> ReportDetailOut:
    """Đánh giá văn phong AI của báo cáo (P2.3 tối thiểu)."""
    report = get_report_or_404(db, user, report_id)
    if not ((report.request or {}).get("options") or {}).get("style_profile"):
        raise HTTPException(status_code=422, detail="Báo cáo này không dùng văn phong mẫu.")
    report.style_rating = payload.rating if payload.rating != 0 else None
    audit(db, user, "report.style_rating", "report", report.id, ip=client_ip(request), rating=payload.rating)
    db.commit()
    return report_detail(report)


@router.post("/{report_id}/apply-style", response_model=ReportDetailOut)
def apply_style(report_id: str, request: Request, background: BackgroundTasks,
                user: User = Depends(current_user), db: Session = Depends(get_db),
                payload: ApplyStyleIn | None = None) -> ReportDetailOut:
    """Viết lại báo cáo cũ theo văn phong mẫu (P4, chạy nền như tạo mới)."""
    report = get_report_or_404(db, user, report_id)
    if report.status == "generating":
        raise HTTPException(status_code=409, detail="Báo cáo đang được tạo.")
    if report.status == "archived":
        raise HTTPException(status_code=409, detail="Báo cáo đã lưu trữ.")
    key = (payload.template_key if payload and payload.template_key else None) or report.template
    snapshot = resolve_template_style(db, user, (key or "").strip() or report.template)
    if snapshot is None:
        raise HTTPException(status_code=422, detail="Mẫu chưa có văn phong sẵn sàng (ready).")
    options = dict((report.request or {}).get("options") or {})
    options["style_profile"] = snapshot
    report.request = {**(report.request or {}), "content_mode": "llm", "options": options}
    report.content_mode = "llm"
    report.style_rating = None
    report.style_version = snapshot.get("style_version")
    try:
        ReportRequest.model_validate(report.request)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Báo cáo cũ không còn tương thích, tạo báo cáo mới.") from exc
    report.status, report.error = "generating", ""
    report.generation_attempts, report.job_heartbeat_at = 0, None
    audit(db, user, "report.apply_style", "report", report.id, ip=client_ip(request), template_key=key)
    db.commit()
    state = request.app.state
    background.add_task(run_llm_generation, state.db.session_factory, report.id, user.email,
                        state.settings.artifact_dir, "apply_style",
                        llm_configs=org_llm_configs(db, user.org_id, state.secret_key),
                        heartbeat_seconds=state.settings.job_heartbeat_seconds)
    return report_detail(report)


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
