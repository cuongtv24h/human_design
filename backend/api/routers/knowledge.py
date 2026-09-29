"""GET /api/v1/knowledge — tra cứu trực tiếp kho knowledge/ + docs/ cho Coach/Admin.

Khác chatbot: gọi thẳng `search_knowledge_hits` (cùng scoring) — không qua LLM,
không tốn token, kết quả có cấu trúc để hiển thị danh sách.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..assistant_tools import (
    DOCS_DIR,
    KNOWLEDGE_DIR,
    _docs_allowed,
    docs_chunks,
    knowledge_chunks,
    search_knowledge_hits,
)
from .. import kb_pipeline
from ..deps import current_user, get_db, require_admin
from ..models import KnowledgeSubmission, User
from ..services import audit

router = APIRouter(tags=["knowledge"])


@router.get("/knowledge/search")
def knowledge_search(
    request: Request,
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(10, ge=1, le=20),
    source: Literal["all", "knowledge", "docs"] = "all",
    file: str = Query("", max_length=200),
    user: User = Depends(current_user),
) -> dict:
    """Tìm trong kho tri thức — cùng scoring với tool của chatbot (không tốn token).

    `file` để lọc đúng một file (kết hợp với `/knowledge/files` làm bộ lọc UI).
    """
    started = perf_counter()
    hits = search_knowledge_hits(q, top_k=limit, source=source, file=file or None)
    took_ms = round((perf_counter() - started) * 1000, 1)
    _log_search(request, user, q, source, file or "", len(hits), took_ms,
                [h["file"] for h in hits[:3]])
    return {
        "query": q,
        "hits": hits,
        "count": len(hits),
        "took_ms": took_ms,
    }


def _log_search(request: Request, user: User, q: str, source: str, file: str,
                count: int, took_ms: float, top_files: list[str]) -> None:
    """Ghi JSONL truy vấn (P3) — dữ liệu thật để quyết định vector/FTS5 sau 1–2 tháng.

    Ghi vào artifact_dir; mọi lỗi I/O nuốt lặng (log không được làm hỏng API).
    """
    try:
        base = Path(request.app.state.settings.artifact_dir)
        base.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user_id": user.id,
            "query": q,
            "source": source,
            "file": file,
            "count": count,
            "took_ms": took_ms,
            "top_files": top_files,
        }
        with (base / "knowledge_queries.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


@router.get("/knowledge/doc")
def knowledge_doc(
    file: str = Query(..., max_length=200),
    user: User = Depends(require_admin),
) -> dict:
    """Nộp nội dung 1 file md tri thức để ĐỌC TRỰC TIẾP (trang Đọc tài liệu — Admin only).

    knowledge/*.md: mọi file nội dung. docs/*.md: WHITELIST tri thức (loại deploy/
    hạ tầng). Chặn traversal bằng basename-only + không "..", không "/" (404 im lặng).
    """
    name = file.strip()
    if (not name.endswith(".md") or "/" in name or "\\" in name or ".." in name
            or Path(name).name != name):
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    if (KNOWLEDGE_DIR / name).is_file():
        path, source = KNOWLEDGE_DIR / name, "knowledge"
    elif _docs_allowed(name) and (DOCS_DIR / name).is_file():
        path, source = DOCS_DIR / name, "docs"
    else:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HTTPException(status_code=404, detail="Không đọc được tài liệu.") from exc
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), path.stem)
    return {"file": name, "title": title, "source": source, "text": text}


@router.get("/knowledge/files")
def knowledge_files(user: User = Depends(current_user)) -> dict:
    """Danh sách file kho tri thức (kèm số mục `##`) để lọc khi tra cứu."""
    seen: dict[str, dict] = {}
    for src, rows in (("knowledge", knowledge_chunks()), ("docs", docs_chunks())):
        for filename, title, _chunk in rows:
            entry = seen.setdefault(
                filename,
                {"file": filename, "title": title, "source": src, "sections": 0},
            )
            entry["sections"] += 1
    return {"files": sorted(seen.values(), key=lambda f: (f["source"], f["file"]))}


# ------------------------------------------------------------------ Phase A


class SubmissionIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content_md: str = Field(min_length=1)
    target_file: str = Field(default="", max_length=200)
    source_url: str = Field(default="", max_length=500)


class ApproveIn(BaseModel):
    content_md: str | None = None
    target_file: str | None = None


class RejectIn(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


def _pending_others(db: Session, org_id: int, exclude_id: int | None = None) -> list[tuple[str, str, str]]:
    """Bài pending chưa vào corpus — đưa vào dedupe để không nộp/duyệt trùng."""
    query = select(KnowledgeSubmission).where(
        KnowledgeSubmission.org_id == org_id,
        KnowledgeSubmission.status == "pending",
    )
    if exclude_id is not None:
        query = query.where(KnowledgeSubmission.id != exclude_id)
    return [(f"#{s.id} {s.title} (chưa duyệt)", "", s.content_md)
            for s in db.scalars(query)]


def _get_submission(db: Session, org_id: int, sub_id: int) -> KnowledgeSubmission:
    sub = db.get(KnowledgeSubmission, sub_id)
    if sub is None or sub.org_id != org_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài đóng góp.")
    return sub


def _submission_out(sub: KnowledgeSubmission, contributor: str = "") -> dict:
    return {
        "id": sub.id,
        "title": sub.title,
        "target_file": sub.target_file,
        "source_url": sub.source_url,
        "status": sub.status,
        "dedupe_report": sub.dedupe_report or {},
        "ai_notes": json.loads(sub.ai_notes) if sub.ai_notes else None,
        "reject_reason": sub.reject_reason,
        "contributor": contributor,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
        "decided_at": sub.decided_at.isoformat() if sub.decided_at else None,
    }


@router.post("/knowledge/submissions", status_code=201)
def create_submission(
    payload: SubmissionIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    """Coach/Admin đóng góp — sàng lọc TỰ ĐỘNG trước khi vào hàng chờ duyệt.

    Lỗi hard (rỗng/quá lớn/thiếu heading/lộ bí mật/trùng ≥90%) → 422, KHÔNG lưu.
    """
    errors = kb_pipeline.screen_content(payload.content_md)
    if payload.target_file and not kb_pipeline.safe_md_name(payload.target_file):
        errors.append("File đích không hợp lệ (chỉ tên file .md, không có thư mục).")
    if errors:
        raise HTTPException(status_code=422, detail=" ".join(errors))
    dedupe = kb_pipeline.dedupe_check(payload.content_md,
                                      extra_chunks=_pending_others(db, user.org_id))
    if dedupe["level"] == "hard":
        top = dedupe["matches"][0] if dedupe.get("matches") else {}
        raise HTTPException(
            status_code=422,
            detail=f"Nội dung trùng lặp {round(dedupe['max_similarity'] * 100)}% với "
                   f"`{top.get('file', '')}` ({top.get('section', '')}) — không cần nộp lại.",
        )
    sub = KnowledgeSubmission(
        org_id=user.org_id,
        contributor_id=user.id,
        title=payload.title.strip(),
        target_file=(payload.target_file or "").strip(),
        content_md=payload.content_md,
        source_url=payload.source_url.strip(),
        status="pending",
        dedupe_report=dedupe,
    )
    db.add(sub)
    db.flush()
    audit(db, user, "knowledge.submit", "kb_submission", str(sub.id))
    db.commit()
    return _submission_out(sub, contributor=user.full_name or user.email)


@router.get("/knowledge/submissions")
def list_submissions(
    status: str = Query("", max_length=12),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    """Coach chỉ thấy bài của mình; Admin thấy toàn bộ (lọc theo status tùy chọn)."""
    if status and status not in {"pending", "approved", "rejected"}:
        raise HTTPException(status_code=422, detail="Trạng thái không hợp lệ.")
    query = select(KnowledgeSubmission, User.email, User.full_name).join(
        User, KnowledgeSubmission.contributor_id == User.id
    ).where(KnowledgeSubmission.org_id == user.org_id)
    if user.role != "admin":
        query = query.where(KnowledgeSubmission.contributor_id == user.id)
    if status:
        query = query.where(KnowledgeSubmission.status == status)
    rows = db.execute(query.order_by(KnowledgeSubmission.created_at.desc())).all()
    items = [_submission_out(sub, contributor=full or email)
             for sub, email, full in rows]
    # pending lên trước để Admin thấy việc cần làm
    items.sort(key=lambda it: it["status"] != "pending")
    return {"items": items, "total": len(items)}


@router.get("/knowledge/submissions/{sub_id}")
def get_submission(
    sub_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    sub = _get_submission(db, user.org_id, sub_id)
    if user.role != "admin" and sub.contributor_id != user.id:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài đóng góp.")
    contributor = db.get(User, sub.contributor_id)
    out = _submission_out(sub, contributor=(contributor.full_name or contributor.email)
                          if contributor else "")
    out["preview"] = kb_pipeline.search_preview(sub.content_md, top_k=3)
    out["can_review"] = user.role == "admin" and sub.status == "pending"
    out["content_md"] = sub.content_md
    return out


@router.post("/knowledge/submissions/{sub_id}/approve")
def approve_submission(
    sub_id: int,
    payload: ApproveIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> dict:
    """Admin duyệt: re-screen (admin cũng có thể sửa nội dung) → xuất kho atomic
    + ghi sổ nguồn + audit. Hiệu lực search NGAY nhờ fingerprint cache."""
    sub = _get_submission(db, user.org_id, sub_id)
    if sub.status != "pending":
        raise HTTPException(status_code=422, detail="Bài này đã được xử lý trước đó.")
    content = payload.content_md if payload.content_md is not None else sub.content_md
    target = payload.target_file if payload.target_file is not None else sub.target_file
    errors = kb_pipeline.screen_content(content)
    if target and not kb_pipeline.safe_md_name(target):
        errors.append("File đích không hợp lệ.")
    if errors:
        raise HTTPException(status_code=422, detail=" ".join(errors))
    dedupe = kb_pipeline.dedupe_check(content,
                                      extra_chunks=_pending_others(db, user.org_id, exclude_id=sub.id))
    if dedupe["level"] == "hard":
        raise HTTPException(status_code=422,
                            detail="Nội dung trùng lặp với bài đang chờ duyệt khác — gộp bài rồi thử lại.")
    try:
        published = kb_pipeline.publish_content(content, target, sub.title)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    contributor = db.get(User, sub.contributor_id)
    label = (contributor.full_name or contributor.email) if contributor else "unknown"
    kb_pipeline.append_sources_log(published["file"], sub.title, sub.source_url, label)
    sub.content_md = content
    sub.target_file = published["file"]
    sub.status = "approved"
    sub.reviewer_id = user.id
    sub.decided_at = datetime.now(timezone.utc)
    sub.dedupe_report = dedupe
    audit(db, user, "knowledge.approve", "kb_submission", str(sub.id),
          meta={"file": published["file"], "mode": published["mode"]})
    db.commit()
    return {"submission": _submission_out(sub, contributor=label), "published": published}


@router.post("/knowledge/submissions/{sub_id}/reject")
def reject_submission(
    sub_id: int,
    payload: RejectIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> dict:
    sub = _get_submission(db, user.org_id, sub_id)
    if sub.status != "pending":
        raise HTTPException(status_code=422, detail="Bài này đã được xử lý trước đó.")
    sub.status = "rejected"
    sub.reject_reason = payload.reason.strip()
    sub.reviewer_id = user.id
    sub.decided_at = datetime.now(timezone.utc)
    audit(db, user, "knowledge.reject", "kb_submission", str(sub.id),
          meta={"reason": sub.reject_reason[:200]})
    db.commit()
    contributor = db.get(User, sub.contributor_id)
    return _submission_out(sub, contributor=(contributor.full_name or contributor.email)
                           if contributor else "")


# ------------------------------------------------------------------ Phase B


@router.post("/knowledge/submissions/{sub_id}/ai-review")
def ai_review_submission(
    sub_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> dict:
    """Chạy AI kiểm duyệt (phase B) — chỉ GỢI Ý, không tự quyết. Lỗi LLM = ran:false."""
    sub = _get_submission(db, user.org_id, sub_id)
    try:
        notes = kb_pipeline.run_ai_review(
            db, user.org_id, request.app.state.secret_key,
            request.app.state.llm_transport, sub.content_md,
        )
    except Exception:  # pragma: no cover — AI không được phá luồng duyệt
        notes = None
    if notes is not None:
        sub.ai_notes = json.dumps(notes, ensure_ascii=False)
        db.commit()
    return {"ran": notes is not None, "ai_notes": notes,
            "error": None if notes is not None else "Chưa chạy được (chưa cấu hình LLM hoặc LLM lỗi)."}


# ------------------------------------------------------------------ Phase C


@router.get("/knowledge/stats")
def knowledge_stats(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> dict:
    """Thống kê đóng góp + truy vấn thật 30 ngày (đọc P3 knowledge_queries.jsonl)."""
    rows = db.execute(
        select(KnowledgeSubmission.status).where(KnowledgeSubmission.org_id == user.org_id)
    ).all()
    counter = Counter(status for (status,) in rows)
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    log_path = Path(request.app.state.settings.artifact_dir) / "knowledge_queries.jsonl"
    queries, took, total = Counter(), [], 0
    if log_path.is_file():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rec = json.loads(line)
                ts = datetime.fromisoformat(rec["ts"])
            except (ValueError, KeyError):
                continue
            if ts >= cutoff:
                total += 1
                queries[rec.get("query", "").strip().lower()] += 1
                if isinstance(rec.get("took_ms"), (int, float)):
                    took.append(rec["took_ms"])
    return {
        "submissions": {
            "pending": counter.get("pending", 0),
            "approved": counter.get("approved", 0),
            "rejected": counter.get("rejected", 0),
            "total": sum(counter.values()),
        },
        "queries_30d": {
            "total": total,
            "avg_took_ms": round(sum(took) / len(took), 1) if took else None,
            "top": [{"query": q, "n": n} for q, n in queries.most_common(10) if q],
        },
    }


@router.post("/knowledge/dedupe-scan")
def dedupe_scan(user: User = Depends(require_admin)) -> dict:
    """Quét trùng lặp tích lũy toàn kho (phase C) — on-demand, không cần cron."""
    return kb_pipeline.full_dedupe_scan()
