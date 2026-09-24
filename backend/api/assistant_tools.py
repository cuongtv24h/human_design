"""Công cụ của Trợ lý tra cứu: kiến thức, skills, tính chart, khách hàng, báo cáo.

Tìm kiếm dùng khớp từ khóa chuẩn hóa tiếng Việt (không dấu vẫn trúng), không cần
thư viện ngoài. Các tool dữ liệu (khách hàng/báo cáo) tôn trọng phân quyền:
coach chỉ thấy khách của mình.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.reporting.contract import ReportRequest, SubjectInput
from backend.reporting.language_vn import vn_authority, vn_definition, vn_strategy, vn_type
from backend.reporting.orchestrator import ReportOrchestrator

from .models import Client, User
from .services import get_client_or_404, get_report_or_404, report_summary, visible_clients

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = ROOT / "knowledge"
SKILLS_DIR = ROOT / "mcp" / "skills"

_STOPWORDS = frozenset(
    "là của và có cho về gì như thế nào trong với để các những một cái này kia đó ấy ơi ạ nhé không là gì bao "
    "nhiêu sao hay hoặc nếu thì mà còn được bị sẽ đang đã hãy là".split())


def fold_vi(text: str) -> str:
    """Lowercase + bỏ dấu tiếng Việt để khớp từ khóa tolerant."""
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("đ", "d")


def _terms(query: str) -> list[str]:
    # Lọc stopword TRƯỚC khi bỏ dấu ("chờ" khác "cho").
    raw = [t for t in re.findall(r"[a-z0-9đá-ỹâăêôơư]+", (query or "").lower())
           if len(t) >= 2 and t not in _STOPWORDS]
    return [fold_vi(t) for t in raw]


@lru_cache(maxsize=1)
def knowledge_chunks() -> list[tuple[str, str, str]]:
    """``(filename, title, chunk_text)`` — mỗi chunk là một mục ``##`` trong kho kiến thức."""
    chunks: list[tuple[str, str, str]] = []
    if not KNOWLEDGE_DIR.is_dir():
        return chunks
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
        current: list[str] = []
        for line in text.splitlines():
            if line.startswith("## ") and current:
                chunks.append((path.name, title, "\n".join(current).strip()))
                current = [line]
            else:
                current.append(line)
        if "".join(current).strip():
            chunks.append((path.name, title, "\n".join(current).strip()))
    return chunks


def search_knowledge(query: str, top_k: int = 4) -> tuple[str, str]:
    terms = _terms(query)
    if not terms:
        return "Từ khóa quá ngắn, hãy hỏi cụ thể hơn.", ""
    scored: list[tuple[float, str, str, str]] = []
    for filename, title, chunk in knowledge_chunks():
        folded = fold_vi(f"{title}\n{chunk}")
        hits = [folded.count(t) for t in terms]
        coverage = sum(1 for h in hits if h > 0)
        if coverage == 0:
            continue
        density = sum(hits) / (len(folded) / 1000 + 1)
        title_hits = sum(1 for t in terms if t in fold_vi(title))
        score = coverage * 10 + title_hits * 5 + min(density, 10)
        scored.append((score, filename, title, chunk))
    scored.sort(key=lambda item: -item[0])
    if not scored:
        return f"Không tìm thấy gì cho “{query}” trong kho kiến thức.", ""
    parts, sources = [], []
    for _, filename, title, chunk in scored[:top_k]:
        parts.append(f"[{title} — {filename}]\n{chunk[:900]}")
        if title not in sources:
            sources.append(title)
    return "\n\n---\n\n".join(parts), "Kho kiến thức: " + "; ".join(sources)


@lru_cache(maxsize=1)
def skill_files() -> list[tuple[str, str]]:
    """``(filename, title)`` của các skill phân tích."""
    skills: list[tuple[str, str]] = []
    if not SKILLS_DIR.is_dir():
        return skills
    for path in sorted(SKILLS_DIR.glob("*.md")):
        try:
            first = next((l for l in path.read_text(encoding="utf-8").splitlines() if l.startswith("#")), "")
        except OSError:
            continue
        skills.append((path.name, first.lstrip("# ").strip() or path.stem))
    return skills


def list_skills() -> tuple[str, str]:
    skills = skill_files()
    if not skills:
        return "Chưa có skill nào.", ""
    lines = [f"- {name}: {title}" for name, title in skills]
    return "Các skill hiện có:\n" + "\n".join(lines), ""


def read_skill(name: str) -> tuple[str, str]:
    want = fold_vi(name or "")
    digits = "".join(c for c in want if c.isdigit())
    for filename, title in skill_files():
        folded = fold_vi(f"{filename} {title}")
        if (digits and filename.startswith(digits.zfill(2))) or (want and want in folded):
            try:
                text = (SKILLS_DIR / filename).read_text(encoding="utf-8")
            except OSError:
                return f"Không đọc được skill {filename}.", ""
            return text[:3500], f"Skill: {title}"
    return f"Không tìm thấy skill “{name}”. Dùng list_skills để xem danh sách.", ""


def _chart_summary_text(chart: Mapping[str, Any], header: str) -> str:
    chart_type = str(chart.get("type", ""))
    centers = chart.get("defined_centers", []) or []
    channels = [f"{a}-{b}" for a, b in (chart.get("defined_channels", []) or [])]
    lines = [
        header,
        f"- Type: {vn_type(chart_type, gloss=True)}",
        f"- Chiến lược sống: {vn_strategy(str(chart.get('strategy', '')), chart_type)}",
        f"- Quyền nội tại: {vn_authority(str(chart.get('authority', '')))}",
        f"- Profile: {chart.get('profile', '')} · Định nghĩa: {vn_definition(str(chart.get('definition', '')))}",
        f"- Chữ thập hóa thân: {chart.get('incarnation_cross', '')}",
        f"- Trung tâm xác định ({len(centers)}): {', '.join(str(c) for c in centers) or '—'}",
        f"- Kênh xác định ({len(channels)}): {', '.join(channels) or '—'}",
    ]
    return "\n".join(lines)


def calculate_chart(birth_date: str, birth_time: str, timezone: str = "+07:00") -> tuple[str, str]:
    try:
        subject = SubjectInput(name="", birth_date=(birth_date or "").strip(),
                               birth_time=(birth_time or "").strip(),
                               timezone=(timezone or "+07:00").strip())
    except ValidationError as exc:
        return f"Ngày/giờ sinh chưa đúng ({exc.errors()[0].get('msg')}). Cần birth_date YYYY-MM-DD và birth_time HH:MM.", ""
    request = ReportRequest.model_validate({"subject": subject.model_dump(), "tier": "free_basic",
                                            "template": "sections", "content_mode": "template"})
    chart = ReportOrchestrator().run(request).chart
    header = f"BodyGraph cho {subject.birth_date} {subject.birth_time} ({subject.timezone}):"
    return _chart_summary_text(chart, header), "Tính toán: BodyGraph (Swiss Ephemeris)"


def search_clients(db: Session, user: User, query: str) -> tuple[str, str]:
    like = f"%{(query or '').strip().lower()}%"
    rows = db.scalars(visible_clients(user).where(func.lower(Client.full_name).like(like))
                      .order_by(Client.full_name).limit(5)).all()
    if not rows:
        return f"Không tìm thấy khách hàng nào tên giống “{query}”.", ""
    lines = [f"- #{c.id} {c.full_name} — sinh {c.birth_date} {c.birth_time} ({c.timezone})" for c in rows]
    return "Khách hàng tìm thấy:\n" + "\n".join(lines), ""


def client_chart(db: Session, user: User, client_id: Any) -> tuple[str, str]:
    try:
        client = get_client_or_404(db, user, int(client_id))
    except (TypeError, ValueError):
        return "client_id phải là số (dùng search_clients để tìm).", ""
    request = ReportRequest.model_validate({
        "subject": {"name": client.full_name, "birth_date": client.birth_date,
                    "birth_time": client.birth_time, "timezone": client.timezone,
                    "birth_location": client.birth_place or ""},
        "tier": "deep_core", "template": "sections", "content_mode": "template"})
    chart = ReportOrchestrator().run(request).chart
    header = f"Chart của {client.full_name} (sinh {client.birth_date} {client.birth_time}):"
    return _chart_summary_text(chart, header), f"Khách hàng: {client.full_name}"


def report_info(db: Session, user: User, report_id: Any) -> tuple[str, str]:
    report = get_report_or_404(db, user, str(report_id or "").strip())
    summary = report_summary(report)
    lines = [f"Báo cáo {summary.id} — {summary.client_name}:",
             f"- Mức độ: {summary.tier} · Trình bày: {summary.template} · Nội dung: {summary.content_mode}",
             f"- Trạng thái: {summary.status} · Phiên bản: v{summary.version}"]
    if report.document:
        titles = [s.get("title", s.get("id")) for s in sorted(report.document.get("sections", []),
                                                              key=lambda s: s.get("order", 0))]
        lines.append(f"- Các mục ({len(titles)}): " + "; ".join(str(t) for t in titles[:12]))
        if report.document.get("provenance", {}).get("llm_provider"):
            lines.append(f"- Viết bởi: {report.document['provenance']['llm_provider']}")
    return "\n".join(lines), f"Báo cáo: {summary.client_name}"


def make_executor(db: Session, user: User):
    """Tool executor gắn quyền của user (coach chỉ thấy dữ liệu của mình)."""

    def execute(name: str, args: Mapping[str, Any]) -> tuple[str, str]:
        args = dict(args or {})
        try:
            if name == "search_knowledge":
                return search_knowledge(str(args.get("query", "")))
            if name == "list_skills":
                return list_skills()
            if name == "read_skill":
                return read_skill(str(args.get("name", "")))
            if name == "calculate_chart":
                return calculate_chart(str(args.get("birth_date", "")), str(args.get("birth_time", "")),
                                       str(args.get("timezone", "+07:00") or "+07:00"))
            if name == "search_clients":
                return search_clients(db, user, str(args.get("q", "")))
            if name == "client_chart":
                return client_chart(db, user, args.get("client_id"))
            if name == "report_info":
                return report_info(db, user, args.get("report_id"))
        except HTTPException as exc:
            detail = exc.detail if isinstance(exc.detail, str) else "Không có quyền."
            return detail, ""
        return (f"Công cụ “{name}” không tồn tại. Chỉ dùng: search_knowledge, list_skills, "
                "read_skill, calculate_chart, search_clients, client_chart, report_info."), ""

    return execute


__all__ = ["calculate_chart", "client_chart", "fold_vi", "knowledge_chunks", "list_skills", "make_executor",
           "read_skill", "report_info", "search_clients", "search_knowledge", "skill_files"]
