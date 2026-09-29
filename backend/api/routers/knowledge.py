"""GET /api/v1/knowledge — tra cứu trực tiếp kho knowledge/ + docs/ cho Coach/Admin.

Khác chatbot: gọi thẳng `search_knowledge_hits` (cùng scoring) — không qua LLM,
không tốn token, kết quả có cấu trúc để hiển thị danh sách.
"""

from __future__ import annotations

from time import perf_counter
from typing import Literal

from fastapi import APIRouter, Depends, Query

from ..assistant_tools import docs_chunks, knowledge_chunks, search_knowledge_hits
from ..deps import current_user
from ..models import User

router = APIRouter(tags=["knowledge"])


@router.get("/knowledge/search")
def knowledge_search(
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
    return {
        "query": q,
        "hits": hits,
        "count": len(hits),
        "took_ms": round((perf_counter() - started) * 1000, 1),
    }


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
