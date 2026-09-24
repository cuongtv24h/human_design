"""Routes without a session: client share page data (P3) and 5-minute signed downloads (P0-10).

Nothing here is indexable (``X-Robots-Tag``) or cacheable by shared caches. Client-facing
payloads never include internal warnings, UTC datetimes or coach notes.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import client_ip, get_db
from ..files import file_response
from ..models import Organization, Report, ShareLink
from ..schemas import PublicReportOut, PublicSection
from ..security import hash_token, verify_token
from ..services import audit, chart_summary, load_document
from .shares import share_status

from hd_time import display_birth  # noqa: E402

router = APIRouter(tags=["public"])

NOINDEX = {"X-Robots-Tag": "noindex, nofollow", "Referrer-Policy": "no-referrer"}
GONE = "Link này đã hết hạn hoặc đã bị thu hồi. Vui lòng liên hệ người tư vấn để nhận link mới."


def _available(report: Report | None) -> bool:
    return bool(report and report.document and report.status != "archived"
                and report.client is not None and report.client.deleted_at is None)


def _share(db: Session, token: str) -> ShareLink:
    share = db.scalar(select(ShareLink).where(ShareLink.token_hash == hash_token(token)))
    if share is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo.")
    if share_status(share) != "active" or not _available(share.report):
        raise HTTPException(status_code=410, detail=GONE)
    return share


@router.get("/public/r/{token}", response_model=PublicReportOut)
def shared_report(token: str, request: Request, response: Response, db: Session = Depends(get_db)) -> PublicReportOut:
    share = _share(db, token)
    report = share.report
    document = load_document(report)
    share.view_count = (share.view_count or 0) + 1
    share.last_viewed_at = datetime.now(timezone.utc)
    audit(db, None, "share.view", "report", report.id, ip=client_ip(request), org_id=share.org_id, share_id=share.id)
    db.commit()
    response.headers.update({**NOINDEX, "Cache-Control": "private, no-store"})
    org = db.get(Organization, report.org_id)
    client = report.client
    return PublicReportOut(
        client_name=client.full_name,
        subject_display=display_birth(client.birth_date, client.birth_time, client.timezone),
        title=document.title,
        generated_at=document.provenance.generated_at,
        summary=chart_summary(document.chart),
        formats=list(share.formats or []),
        sections=[PublicSection(id=s.id, title=s.title, content_markdown=s.content_markdown)
                  for s in sorted(document.sections, key=lambda i: i.order) if s.status == "included"],
        org_name=org.name if org else "",
    )


@router.get("/public/r/{token}/infographic.html")
def shared_infographic(token: str, request: Request, db: Session = Depends(get_db)) -> Response:
    share = _share(db, token)
    return file_response(db, request.app.state.settings.artifact_dir, share.report, "infographic", False, NOINDEX)


@router.get("/public/r/{token}/{fmt}")
def shared_file(token: str, fmt: str, request: Request, db: Session = Depends(get_db)) -> Response:
    share = _share(db, token)
    if fmt not in (share.formats or []):
        raise HTTPException(status_code=404, detail="Định dạng này không được chia sẻ.")
    response = file_response(db, request.app.state.settings.artifact_dir, share.report, fmt, True, NOINDEX)
    audit(db, None, "share.download", "report", share.report_id, ip=client_ip(request), org_id=share.org_id,
          share_id=share.id, format=fmt)
    db.commit()
    return response


@router.get("/files/{token}")
def signed_file(token: str, request: Request, db: Session = Depends(get_db)) -> Response:
    """Signed, expiring direct download created by ``POST /reports/{id}/links``."""
    payload = verify_token(request.app.state.secret_key, "download", token)
    if payload is None:
        raise HTTPException(status_code=410, detail="Link tải đã hết hạn (5 phút) hoặc không hợp lệ — hãy tạo link mới.")
    report = db.get(Report, str(payload.get("r", "")))
    if not _available(report):
        raise HTTPException(status_code=410, detail="Báo cáo không còn khả dụng.")
    fmt = str(payload.get("f", ""))
    response = file_response(db, request.app.state.settings.artifact_dir, report, fmt, None, NOINDEX)
    audit(db, None, "report.export_link", "report", report.id, ip=client_ip(request), org_id=report.org_id,
          actor=payload.get("u"), format=fmt)
    db.commit()
    return response
