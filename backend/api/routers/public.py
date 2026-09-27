"""Routes without a session: client share page data (P3) and 5-minute signed downloads (P0-10).

Nothing here is indexable (``X-Robots-Tag``) or cacheable by shared caches. Client-facing
payloads never include internal warnings, UTC datetimes or coach notes.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from pydantic import ValidationError

from backend.reporting.contract import ReportRequest
from backend.reporting.orchestrator import ReportOrchestrator

from ..deps import client_ip, get_db
from ..files import file_response
from ..models import GameEvent, GameLead, GameScore, Organization, Report, ShareLink
from ..schemas import (GameChartIn, GameChartOut, GameEventIn, GameLeadIn, GameScoreIn,
                       GameScoreOut, PublicReportOut, PublicSection)
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

# --- game landing công khai (G1) ------------------------------------------------

_GAME_EVENT_NAMES = frozenset({"game_start", "game_complete", "bridge_view", "bridge_submit",
                               "share_click", "cta_click", "lead_submit", "compare_view",
                               "compare_done"})

_HITS: dict[tuple[str, str], list[float]] = {}


def _ratelimit(key: str, limit: int, window: float = 60.0):
    """Giới hạn tần suất theo IP cho endpoint công khai (bộ nhớ cục bộ; production cần redis)."""

    def dep(request: Request) -> None:
        ip = client_ip(request) or "unknown"
        now = time.monotonic()
        slot = (ip, key)
        hits = [t for t in _HITS.get(slot, []) if now - t < window]
        if len(hits) >= limit:
            raise HTTPException(status_code=429, detail="Bạn thao tác quá nhanh, thử lại sau ít phút.")
        hits.append(now)
        _HITS[slot] = hits

    return dep


@router.post("/public/game/chart", response_model=GameChartOut)
def game_chart(payload: GameChartIn, db: Session = Depends(get_db),
               _rl: None = Depends(_ratelimit("game_chart", 30))) -> GameChartOut:
    """Mini chart cho game landing (không cần đăng nhập)."""
    try:
        req = ReportRequest.model_validate({
            "subject": {"name": "Khách", "birth_date": payload.birth_date,
                        "birth_time": payload.birth_time, "timezone": payload.timezone,
                        "birth_location": payload.birth_place},
            "tier": "deep_core", "template": "sections", "domains": []})
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Ngày giờ sinh chưa hợp lệ.") from exc
    document = ReportOrchestrator().run(req)
    raw_centers = document.chart.get("defined_centers", []) or []
    return GameChartOut(
        summary=chart_summary(document.chart),
        centers=[c for c in raw_centers if isinstance(c, str)],
        subject_display=display_birth(payload.birth_date, payload.birth_time, payload.timezone))


@router.post("/public/game/events")
def game_event(payload: GameEventIn, db: Session = Depends(get_db),
               _rl: None = Depends(_ratelimit("game_events", 120))) -> dict:
    """Ghi sự kiện funnel ẩn danh (tên phải nằm trong danh sách cho phép)."""
    if payload.name not in _GAME_EVENT_NAMES:
        raise HTTPException(status_code=422, detail="Tên sự kiện không hợp lệ.")
    db.add(GameEvent(name=payload.name, theme=payload.theme[:32],
                     session_id=payload.session_id[:64]))
    db.commit()
    return {"ok": True}


@router.post("/public/game/leads")
def game_lead(payload: GameLeadIn, db: Session = Depends(get_db),
              _rl: None = Depends(_ratelimit("game_leads", 10))) -> dict:
    """Nhận thông tin khách muốn báo cáo đầy đủ (G1, không cần đăng nhập)."""
    if not payload.name.strip() or not payload.contact.strip():
        raise HTTPException(status_code=422, detail="Vui lòng nhập tên và số điện thoại/Zalo.")
    db.add(GameLead(
        name=payload.name.strip()[:80], contact=payload.contact.strip()[:120],
        birth_date=payload.birth_date[:10], birth_time=payload.birth_time[:8],
        birth_place=payload.birth_place[:120], timezone=payload.timezone[:10],
        theme=payload.theme[:32], quiz=dict(payload.quiz or {}), note=payload.note.strip()[:500]))
    db.commit()
    return {"ok": True}

_GAME_THEMES = frozenset({"nguoc-dong", "thuong-vu", "linh-thu"})
_GAME_STYLES = frozenset({"khoi-xuong", "kien-tao", "dan-duong", "tam-guong"})


def _week_start() -> datetime:
    """0h thứ Hai đầu tuần (UTC) — bảng vàng tính theo tuần."""
    now = datetime.now(timezone.utc)
    monday = now - timedelta(days=now.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


@router.post("/public/game/scores")
def game_score(payload: GameScoreIn, db: Session = Depends(get_db),
               _rl: None = Depends(_ratelimit("game_scores", 30))) -> dict:
    """Ghi điểm ẩn danh lên bảng vàng tuần (G3). Trả về thứ hạng hiện tại."""
    if payload.theme not in _GAME_THEMES:
        raise HTTPException(status_code=422, detail="Theme không hợp lệ.")
    if payload.style not in _GAME_STYLES:
        raise HTTPException(status_code=422, detail="Phong cách không hợp lệ.")
    if not 0 <= payload.deviation <= 100:
        raise HTTPException(status_code=422, detail="Độ lệch phải từ 0 đến 100.")
    if not payload.session_id.strip():
        raise HTTPException(status_code=422, detail="Thiếu session.")
    start = _week_start()
    db.add(GameScore(theme=payload.theme, style=payload.style, deviation=payload.deviation,
                     session_id=payload.session_id.strip()[:64]))
    db.commit()
    best = select(GameScore.session_id, func.min(GameScore.deviation).label("dev")).where(
        GameScore.theme == payload.theme, GameScore.created_at >= start).group_by(
        GameScore.session_id).subquery()
    better = db.scalar(select(func.count()).select_from(best).where(
        best.c.dev < payload.deviation)) or 0
    return {"ok": True, "rank": better + 1}


@router.get("/public/game/scores", response_model=list[GameScoreOut])
def game_scores(theme: str = "", limit: int = 10, db: Session = Depends(get_db)) -> list[GameScoreOut]:
    """Top bảng vàng tuần, mỗi session chỉ tính điểm tốt nhất (G3)."""
    if theme and theme not in _GAME_THEMES:
        raise HTTPException(status_code=422, detail="Theme không hợp lệ.")
    take = max(1, min(limit, 50))
    q = select(GameScore).where(GameScore.created_at >= _week_start())
    if theme:
        q = q.where(GameScore.theme == theme)
    q = q.order_by(GameScore.deviation.asc(), GameScore.id.asc()).limit(take * 5)
    seen: set[str] = set()
    out: list[GameScoreOut] = []
    for row in db.scalars(q):
        if row.session_id in seen:
            continue
        seen.add(row.session_id)
        out.append(GameScoreOut.model_validate(row, from_attributes=True))
        if len(out) >= take:
            break
    return out
