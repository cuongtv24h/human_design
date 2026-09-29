"""GET /api/v1/knowledge — tra cứu trực tiếp kho knowledge/ + docs/ cho Coach/Admin.

Khác chatbot: gọi thẳng `search_knowledge_hits` (cùng scoring) — không qua LLM,
không tốn token, kết quả có cấu trúc để hiển thị danh sách.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request

from ..assistant_tools import docs_chunks, knowledge_chunks, search_knowledge_hits
from ..deps import current_user
from ..models import User

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
