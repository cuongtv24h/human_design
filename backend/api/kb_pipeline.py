"""Pipeline đóng góp tri thức (A–C).

Sàng lọc TỰ ĐỘNG khi nộp: cấu trúc md, chống lộ bí mật (RAG-poisoning),
chống trùng lặp (shingle Jaccard vs corpus), preview relevancy bằng chính
engine search. Xuất kho: ghi file md atomic + tự ghi sổ KNOWLEDGE_SOURCES.
AI review (phase B): kiểm duyệt bằng LLM org — chỉ GỢI Ý, Admin quyết định.

Đường dẫn là module-level name để test monkeypatch về tmp (không ghi thật).
"""

from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

from sqlalchemy.orm import Session

from .assistant_tools import (
    _norm,
    fold_vi,
    knowledge_chunks,
    docs_chunks,
    search_knowledge_hits,
)

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = ROOT / "knowledge"
SOURCES_FILE = ROOT / "docs" / "KNOWLEDGE_SOURCES.md"

MAX_CONTENT_BYTES = 60_000
DUP_HARD = 0.90   # >= : trùng cứng → chặn nộp
DUP_SOFT = 0.70   # >= : gần trùng → cảnh báo Admin
MAX_PENDING_PER_USER = 5   # cap bài chờ duyệt / người (chống spam CPU+DB)
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

# Chặn dữ liệu nhạy cảm lọt vào kho (corpus được chatbot phục vụ cho mọi người).
_SECRET_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "khóa riêng SSH/PEM"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API key dạng sk-"),
    (re.compile(r"(?i)\b(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}"),
     "khóa bí mật dạng key=value"),
    (re.compile(r"(?i)/home/[a-z0-9_]+/"), "đường dẫn nội bộ máy chủ"),
    (re.compile(r"<script[\s>]"), "thẻ script HTML"),
]

_HEADING_RE = re.compile(r"(?m)^#{1,4} ")


def screen_content(content: str) -> list[str]:
    """Lỗi HARD — trả list rỗng thì đạt. Không bao giờ lưu nội dung bị chặn."""
    errors: list[str] = []
    if not content.strip():
        errors.append("Nội dung rỗng.")
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        errors.append(f"Nội dung quá lớn (tối đa {MAX_CONTENT_BYTES // 1000} KB).")
    if not _HEADING_RE.search(content):
        errors.append("Thiếu heading (dòng bắt đầu bằng # hoặc ##) — không chunk được để tìm kiếm.")
    for pattern, label in _SECRET_PATTERNS:
        if pattern.search(content):
            errors.append(f"Phát hiện dữ liệu nhạy cảm ({label}) — không được nộp vào kho tri thức.")
    return errors


def _shingles(text: str, n: int = 5) -> frozenset[tuple[str, ...]]:
    words = _norm(fold_vi(text)).split()
    if len(words) < n:
        return frozenset([tuple(words)]) if words else frozenset()
    return frozenset(tuple(words[i:i + n]) for i in range(len(words) - n + 1))


def _jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter) if inter else 0.0


def _section_of(chunk: str) -> str:
    for line in chunk.splitlines():
        if line.startswith("##"):
            return line.lstrip("#").strip()
    return ""


MIN_SECTION_WORDS = 15  # section quá ngắn (heading một dòng) không đủ ý nghĩa để chấm trùng


def _split_sections(text: str) -> list[str]:
    """Cắt theo heading (#/##) — cùng đơn vị với chunk kho."""
    return [s for s in re.split(r"(?m)(?=^#{1,4} )", text) if s.strip()] or [text.strip()]


def dedupe_check(content: str,
                 extra_chunks: list[tuple[str, str, str]] | None = None) -> dict[str, Any]:
    """So khớp TỪNG section của nội dung mới vs corpus (knowledge + docs) và
    extra_chunks (bài pending chưa xuất kho — chặn spam nộp trùng khi chờ duyệt).

    Trả {"max_similarity", "level" (none|soft|hard), "matches": [...≤5]}.
    """
    sections = _split_sections(content)
    corpus = [(f, t, c) for f, t, c in knowledge_chunks()] + \
             [(f, t, c) for f, t, c in docs_chunks()] + (extra_chunks or [])
    # Split MỌI nguồn theo section: pending là file đầy đủ, corpus thường đã là chunk.
    corpus_shingles = [(f, _section_of(sec), _shingles(sec))
                       for f, _t, c in corpus for sec in _split_sections(c)
                       if len(sec.split()) >= MIN_SECTION_WORDS]
    best, matches = 0.0, []
    for sec in sections:
        s = _shingles(sec)
        if not s or len(sec.split()) < MIN_SECTION_WORDS:
            continue
        for filename, section, cs in corpus_shingles:
            sim = _jaccard(s, cs)
            if sim > best:
                best = sim
            if sim >= DUP_SOFT:
                matches.append({"file": filename, "section": section, "similarity": round(sim, 3)})
    matches.sort(key=lambda m: -m["similarity"])
    level = "hard" if best >= DUP_HARD else ("soft" if best >= DUP_SOFT else "none")
    return {"max_similarity": round(best, 3), "level": level, "matches": matches[:5]}


def _preview_query(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("#"):
            q = line.lstrip("#").strip()
            if len(q.split()) >= 2:
                return q
    words = _norm(fold_vi(content)).split()
    return " ".join(words[:6])


def search_preview(content: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Top-N đối thủ hiện có với truy vấn lấy từ heading — Admin thấy bối cảnh duyệt."""
    query = _preview_query(content)
    if len(query.split()) < 2:
        return []
    return [
        {"file": h["file"], "title": h["title"], "section": h["section"],
         "score": h["score"], "snippet": h["snippet"]}
        for h in search_knowledge_hits(query, top_k=top_k, source="all")
    ]


def safe_md_name(name: str) -> bool:
    name = (name or "").strip()
    if not name or not name.endswith(".md") or CONTROL_CHARS.search(name):
        return False
    return "/" not in name and "\\" not in name and ".." not in name and Path(name).name == name


def valid_source_url(url: str) -> bool:
    """Chỉ nhận URL http/https có host — chặn javascript:/data:/... (click-XSS)."""
    if not url:
        return True
    if CONTROL_CHARS.search(url):
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def slugify(title: str) -> str:
    folded = fold_vi(title)
    slug = re.sub(r"[^a-z0-9]+", "_", folded).strip("_")
    return slug[:40] or "dong_gop"


def _strip_title_line(content: str, fallback: str) -> str:
    """Bỏ heading '# ' đầu (file đã có title) — giữ các section '## '."""
    lines = content.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# ") and not lines[0].startswith("## "):
        lines.pop(0)
    body = "\n".join(lines).strip()
    if not body:
        return ""
    first = next((ln for ln in body.splitlines() if ln.strip()), "")
    if not first.startswith("#"):
        body = f"## {fallback}\n\n{body}"
    return body


def publish_content(content: str, target_file: str, title: str) -> dict[str, Any]:
    """Ghi nội dung đã duyệt vào knowledge/ (atomic). Trả {"file", "mode"}.

    - File đích tồn tại → APPEND section (bỏ title-line, giữ ##).
    - Không tồn tại / rỗng → TẠO file mới đánh số tiếp (28_, 29_, ...).
    """
    body = _strip_title_line(content, title)
    if not body:
        raise ValueError("Nội dung rỗng sau khi chuẩn hóa.")
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    target = (target_file or "").strip()
    mode = "append"
    if safe_md_name(target) and (KNOWLEDGE_DIR / target).is_file():
        path = KNOWLEDGE_DIR / target
        merged = path.read_text(encoding="utf-8").rstrip() + "\n\n" + body + "\n"
        text = merged
    else:
        mode = "create"
        numbers = []
        for p in KNOWLEDGE_DIR.glob("*.md"):
            m = re.match(r"^(\d{2})_", p.name)
            if m:
                numbers.append(int(m.group(1)))
        next_num = max(numbers, default=-1) + 1
        path = KNOWLEDGE_DIR / f"{next_num:02d}_{slugify(title)}.md"
        text = f"# {title.strip()}\n\n{body}\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return {"file": path.name, "mode": mode}


def append_sources_log(filename: str, title: str, source_url: str, contributor: str) -> None:
    """Tự ghi sổ nguồn (quy tắc KNOWLEDGE_SOURCES.md) — atomic append đợt mới."""
    if not SOURCES_FILE.is_file():
        return
    text = SOURCES_FILE.read_text(encoding="utf-8")
    n_rounds = len(re.findall(r"(?m)^## Đợt ", text))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source = (source_url.strip() or f"Đóng góp nội bộ — {contributor}").replace("|", "\\|")
    row_title = title.replace("|", "\\|")
    block = (
        f"\n## Đợt {n_rounds + 1} — {today} (Đóng góp nội bộ)\n\n"
        "| # | Nguồn | Ngày | Điểm chính khai thác | File đích |\n"
        "|---|-------|------|----------------------|-----------|\n"
        f"| 1 | {source} | {today} | {row_title} | `{filename}` |\n"
    )
    tmp = SOURCES_FILE.with_suffix(".md.tmp")
    tmp.write_text(text.rstrip() + "\n" + block, encoding="utf-8")
    os.replace(tmp, SOURCES_FILE)


# ---------------------------------------------------------------- Phase B: AI

REVIEW_SYSTEM = (
    "Bạn là kiểm duyệt kho tri thức Human Design (tiếng Việt). Chỉ trả về JSON "
    "không markdown, đúng cấu trúc được yêu cầu. Không thêm chữ ngoài JSON."
)


def ai_review_brief(content: str, related: list[dict[str, Any]]) -> str:
    blocks = []
    for i, r in enumerate(related, 1):
        blocks.append(f"[{i}] {r['title']} — {r['file']}\n{r['snippet'][:1200]}")
    related_text = "\n\n".join(blocks) or "(không có trạng liên quan)"
    return (
        "Đây là NỘI DUNG MỚI được đề nghị bổ sung vào kho tri thức:\n\n"
        f"---\n{content[:6000]}\n---\n\n"
        f"3 trạng LIÊN QUAN NHẤT đã có trong kho:\n\n{related_text}\n\n"
        'Trả về JSON đúng 3 khóa (giá trị là chuỗi tiếng Việt, ngắn gọn):\n'
        '{"mâu thuẫn": "...", "trùng ý": "...", "ghi chú": "..."}\n'
        "- \"mâu thuẫn\": nội dung mới trái với trạng liên quan (nếu có, nếu không để trống).\n"
        '- "trùng ý": nói lại điều đã có (khác từ, cùng ý) — nêu trạng nguồn.\n'
        '- "ghi chú": chất lượng/văn phong/điều nên kiểm tra thêm.'
    )


def run_ai_review(db: Session, org_id: int, secret: str, transport, content: str) -> dict[str, Any] | None:
    """Gọi LLM org kiểm duyệt nội dung mới. Trả dict JSON notes, None nếu không chạy được.

    KHÔNG BAO GIỜ raise — AI chỉ là lớp hỗ trợ, lỗi LLM không chặn luồng duyệt.
    """
    from .services import org_llm_configs, save_llm_usages  # tránh cycle import
    from backend.reporting.llm_client import LLMError, call_llm_with_usage

    chain = org_llm_configs(db, org_id, secret)
    if not chain:
        return None
    config = chain[0]
    related = search_preview(content, top_k=3)
    brief = ai_review_brief(content, related)
    started = time.perf_counter()
    entries: list[dict[str, Any]] = []
    try:
        drafts, usage = call_llm_with_usage(brief, config, transport=transport, system=REVIEW_SYSTEM)
        entries.append({"config": config, "usage": usage, "ok": True, "error": "",
                        "latency_ms": int((time.perf_counter() - started) * 1000)})
        notes = {k: str(v) for k, v in drafts.items()}
        return notes
    except LLMError as exc:
        entries.append({"config": config, "usage": None, "ok": False, "error": str(exc),
                        "latency_ms": int((time.perf_counter() - started) * 1000)})
        return None
    finally:
        try:
            save_llm_usages(db, org_id, None, "kb_ai_review", entries)
            db.commit()
        except Exception:  # pragma: no cover — log usage không được phá luồng duyệt
            db.rollback()


def full_dedupe_scan(min_sim: float = DUP_SOFT, top: int = 20) -> dict[str, Any]:
    """Quét TOÀN BỘ cặp chunk (knowledge+docs) tìm trùng lặp tích lũy (phase C)."""
    started = time.perf_counter()
    corpus = knowledge_chunks() + docs_chunks()
    rows = [(f, _section_of(c), _shingles(c)) for f, _t, c in corpus
            if len(c.split()) >= MIN_SECTION_WORDS]
    pairs = []
    for i in range(len(rows)):
        fi, si, shi = rows[i]
        for j in range(i + 1, len(rows)):
            fj, sj, shj = rows[j]
            if fi == fj and si == sj:
                continue
            sim = _jaccard(shi, shj)
            if sim >= min_sim:
                pairs.append({"a": {"file": fi, "section": si}, "b": {"file": fj, "section": sj},
                              "similarity": round(sim, 3)})
    pairs.sort(key=lambda p: -p["similarity"])
    return {"chunks": len(rows), "pairs_found": len(pairs),
            "pairs": pairs[:top], "duration_ms": int((time.perf_counter() - started) * 1000)}
