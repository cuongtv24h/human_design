"""Share links for clients (plan P3-1): create / list / revoke. Token shown once, stored hashed."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import client_ip, current_user, get_db
from ..models import ShareLink, User
from ..schemas import ShareCreate, ShareCreated, ShareOut
from ..security import hash_token
from ..services import audit, get_report_or_404

router = APIRouter(tags=["shares"])


def _aware(value: datetime | None) -> datetime | None:
    return value if value is None or value.tzinfo else value.replace(tzinfo=timezone.utc)


def share_status(share: ShareLink, now: datetime | None = None) -> str:
    if share.revoked_at is not None:
        return "revoked"
    if _aware(share.expires_at) <= (now or datetime.now(timezone.utc)):
        return "expired"
    return "active"


def share_out(share: ShareLink) -> ShareOut:
    return ShareOut(id=share.id, report_id=share.report_id, label=share.label, formats=list(share.formats or []),
                    expires_at=_aware(share.expires_at), revoked_at=_aware(share.revoked_at),
                    view_count=share.view_count, last_viewed_at=_aware(share.last_viewed_at),
                    created_at=_aware(share.created_at), status=share_status(share))


@router.post("/reports/{report_id}/shares", response_model=ShareCreated, status_code=201)
def create_share(report_id: str, payload: ShareCreate, request: Request, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> ShareCreated:
    report = get_report_or_404(db, user, report_id)
    if report.status == "archived" or not report.document:
        raise HTTPException(status_code=409, detail="Chỉ chia sẻ được báo cáo đã sẵn sàng (chưa lưu trữ).")
    token = secrets.token_urlsafe(24)
    share = ShareLink(report_id=report.id, org_id=report.org_id, created_by=user.id, token_hash=hash_token(token),
                      label=payload.label.strip(), formats=sorted(set(payload.formats)),
                      expires_at=datetime.now(timezone.utc) + timedelta(days=payload.expires_days))
    db.add(share)
    db.flush()
    audit(db, user, "share.create", "report", report.id, ip=client_ip(request), share_id=share.id,
          formats=share.formats, expires_days=payload.expires_days)
    db.commit()
    return ShareCreated(share=share_out(share), url=f"/r/{token}")


@router.get("/reports/{report_id}/shares", response_model=list[ShareOut])
def list_shares(report_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ShareOut]:
    report = get_report_or_404(db, user, report_id)
    rows = db.scalars(select(ShareLink).where(ShareLink.report_id == report.id)
                      .order_by(ShareLink.created_at.desc())).all()
    return [share_out(s) for s in rows]


@router.post("/shares/{share_id}/revoke", response_model=ShareOut)
def revoke_share(share_id: int, request: Request, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> ShareOut:
    share = db.get(ShareLink, share_id)
    if share is None or share.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy link chia sẻ.")
    get_report_or_404(db, user, share.report_id)  # coach: only own clients' reports
    if share.revoked_at is None:
        share.revoked_at = datetime.now(timezone.utc)
        audit(db, user, "share.revoke", "report", share.report_id, ip=client_ip(request), share_id=share.id)
        db.commit()
    return share_out(share)
