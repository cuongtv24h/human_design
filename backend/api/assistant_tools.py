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
    "nhiêu sao hay hoặc nếu thì mà còn được bị sẽ đang đã hãy là theo nói".split())


def fold_vi(text: str) -> str:
    """Lowercase + bỏ dấu tiếng Việt để khớp từ khóa tolerant."""
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("đ", "d")


def _raw_terms(query: str) -> list[str]:
    # Lọc stopword TRƯỚC khi bỏ dấu ("chờ" khác "cho", "nói" là stopword).
    return [t for t in re.findall(r"[a-z0-9đá-ỹâăêôơư]+", (query or "").lower())
            if len(t) >= 2 and t not in _STOPWORDS]


def _terms(query: str) -> list[str]:
    return [fold_vi(t) for t in _raw_terms(query)]


def _build_fold1_table() -> dict[int, str]:
    table: dict[int, str] = {}
    for code in range(0x20, 0x2500):
        ch = chr(code)
        decomp = unicodedata.normalize("NFD", ch)
        if len(decomp) == 2 and unicodedata.category(decomp[1]) == "Mn":
            base = decomp[0]
            if "a" <= base <= "z":
                table[code] = base
    table[ord("đ")] = "d"
    return table


_FOLD1_TABLE = _build_fold1_table()


def _fold1(text: str) -> str:
    """Bỏ dấu GIỮ NGUYÊN độ dài (để ánh xạ vị trí khớp về đoạn gốc)."""
    return text.lower().translate(_FOLD1_TABLE)


def _norm(text: str) -> str:
    """Chuẩn hóa để khớp: dấu câu -> khoảng trắng, gộp khoảng trắng."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text)).strip()


# Cụm từ tương đương (đã bỏ dấu): cách hỏi khác nhau nhưng cùng ý. Đối xứng
# 2 chiều — suy ra tự động bên dưới. Chỉ dùng cụm ít gây nhiễu (tránh từ ngắn
# như "con", "tim" vì khớp lung tung do đếm chuỗi con).
_PHRASE_EQUIV_PAIRS = [
    ("diem manh", ["uu diem", "so truong", "the manh", "strength", "strengths", "tai nang"]),
    ("diem yeu", ["diem mu", "han che", "thach thuc", "weakness", "yeu diem"]),
    ("diem mu", ["blind spot", "blindspot", "diem mu"]),
    ("chien luoc", ["strategy", "strategies"]),
    ("tham quyen", ["authority", "authorities"]),
    ("cam xuc", ["emotional", "emotion", "cam tinh"]),
    ("trung tam", ["center", "centre", "centers"]),
    ("kenh", ["channel", "channels"]),
    ("cong", ["gate", "gates"]),
    ("loai", ["type", "types"]),
    ("ho so", ["profile", "profiles"]),
    ("thap gia", ["cross", "incarnation cross"]),
    ("dinh nghia", ["definition", "dinh hinh"]),
    ("tinh yeu", ["love", "moi quan he", "relationship", "hon nhan"]),
    ("moi quan he", ["relationship", "quan he"]),
    ("tien bac", ["money", "tai chinh", "wealth", "tien"]),
    ("tai chinh", ["finance", "wealth"]),
    ("suc khoe", ["health", "healthy"]),
    ("con cai", ["tre em", "children", "child"]),
    ("tre em", ["children", "child"]),
    ("nuoi day con", ["tre em", "con cai", "day con"]),
    ("day con", ["tre em"]),
    ("su nghiep", ["nghe nghiep", "cong viec", "career", "nghe"]),
    ("nghe nghiep", ["career", "occupation"]),
    ("cong viec", ["job", "work", "career"]),
    ("giai dieu kien", ["deconditioning", "de-conditioning"]),
    ("dieu kien hoa", ["conditioning"]),
    ("ra quyet dinh", ["decision", "decisions"]),
    ("chu ky", ["signature"]),
    ("cho dap ung", ["wait to respond", "wait for a response", "responding"]),
    ("cho loi moi", ["wait for the invitation", "invitation"]),
    ("thong bao", ["inform", "informing"]),
    ("cay dang", ["bitterness", "bitter"]),
    ("that vong", ["frustration", "disappointment"]),
    ("thoa man", ["satisfaction", "satisfied"]),
    ("tuc gian", ["anger", "angry"]),
    ("binh an", ["peace", "peaceful"]),
    ("ngac nhien", ["surprise", "surprised"]),
    ("lach", ["spleen"]),
    ("hong", ["throat", "co hong"]),
    ("goc", ["root"]),
]

_PHRASE_EQUIV: dict[str, list[str]] = {}
for _key, _vals in _PHRASE_EQUIV_PAIRS:
    _PHRASE_EQUIV.setdefault(_key, []).extend(v for v in _vals if v not in _PHRASE_EQUIV.get(_key, []))
    for _v in _vals:
        if _key not in _PHRASE_EQUIV.setdefault(_v, []):
            _PHRASE_EQUIV[_v].append(_key)


def _phrases(terms: list[str]) -> list[str]:
    """Cụm 2-3 từ liên tiếp + cả câu (để thưởng khớp nguyên văn)."""
    out: list[str] = []
    for n in (2, 3):
        for i in range(len(terms) - n + 1):
            out.append(" ".join(terms[i:i + n]))
    if len(terms) > 3:
        out.append(" ".join(terms))
    return out


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
        sections: list[str] = []
        for line in text.splitlines():
            if line.startswith("## ") and current:
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if "".join(current).strip():
            sections.append("\n".join(current).strip())
        for section in sections:
            for part in _split_big(section):
                chunks.append((path.name, title, part))
    return chunks


def _split_big(section: str, limit: int = 2000) -> list[str]:
    """Chẻ mục quá dài theo đoạn văn — chunk 10KB nuốt mọi từ khóa, kém chính xác."""
    if len(section) <= limit:
        return [section]
    parts, buf = [], ""
    for para in re.split(r"\n\s*\n", section):
        para = para.strip()
        if not para:
            continue
        if len(para) > limit:  # đoạn đơn quá dài: cắt cứng
            if buf.strip():
                parts.append(buf.strip())
                buf = ""
            parts.extend(para[i:i + limit] for i in range(0, len(para), limit))
        elif len(buf) + len(para) + 2 > limit and buf.strip():
            parts.append(buf.strip())
            buf = para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
    if buf.strip():
        parts.append(buf.strip())
    return parts or [section]


def _word_pattern(s: str) -> re.Pattern:
    # Nguyên từ (không trúng "con" trong "conditioning"); từ đơn cho phép
    # thêm "s" (Type/Types, channel/channels). Cụm từ khớp chính xác.
    tail = "s?" if " " not in s else ""
    return re.compile(r"(?<!\w)" + re.escape(s) + tail + r"(?!\w)")


def _snippet(chunk: str, anchors: list[str], size: int = 1400) -> str:
    """Cửa sổ `size` ký tự quanh cụm khớp dày nhất (thay vì cắt đầu chunk)."""
    if len(chunk) <= size:
        return chunk
    space = _fold1(chunk)  # cùng độ dài với chunk -> vị trí khớp dùng được ngay
    pats = [_word_pattern(a) for a in {_norm(a) for a in anchors} if a]
    offsets = sorted(m.start() for p in pats for m in p.finditer(space))
    if not offsets:
        return chunk[:size]
    best, best_count, j = 0, 0, 0
    for i, off in enumerate(offsets):
        j = max(j, i)
        while j + 1 < len(offsets) and offsets[j + 1] - off <= size - 300:
            j += 1
        if j - i + 1 > best_count:
            best, best_count = off, j - i + 1
    start = max(0, best - 300)
    return chunk[start:start + size]


def search_knowledge(query: str, top_k: int = 3) -> tuple[str, str]:
    raws = _raw_terms(query)
    terms = [fold_vi(t) for t in raws]
    if not terms:
        return "Từ khóa quá ngắn, hãy hỏi cụ thể hơn.", ""
    phrases = _phrases(terms)
    raw_of = dict(zip(phrases, _phrases(raws)))
    raw_by_fold: dict[str, set[str]] = {}
    for r, t in zip(raws, terms):
        raw_by_fold.setdefault(t, set()).add(_norm(r))
    items = set(phrases) | set(terms)
    equivs = {e for item in items for e in _PHRASE_EQUIV.get(item, [])}
    needles = {_norm(s) for s in items} | {_norm(e) for e in equivs}
    pats = {s: _word_pattern(s) for s in needles}
    pats1 = {_norm(r): _word_pattern(_norm(r)) for r in set(raws)}
    for pr in set(raw_of.values()):
        pats1.setdefault(_norm(pr), _word_pattern(_norm(pr)))

    def C(text: str, s: str) -> int:
        return len(pats[s].findall(text))

    def C1(text: str, s: str) -> int:
        return len(pats1[s].findall(text))

    chunks = []
    for filename, title, chunk in knowledge_chunks():
        full = f"{title}\n{chunk}"
        chunks.append((filename, title, chunk, _norm(fold_vi(full)), _norm(full.lower()),
                       _norm(fold_vi(title)), _norm(title.lower())))
    # Bỏ từ xuất hiện ở >60% số chunk ("cho", "mỗi"...). Cụm nguyên văn vẫn
    # được tính — chỉ bỏ điểm từ lẻ.
    if len(terms) > 2:
        n_chunks = max(len(chunks), 1)
        active = [
            t for t in terms
            if sum(1 for c in chunks if pats[t].search(c[3])) <= 0.6 * n_chunks
        ] or terms
    else:
        active = terms
    scored: list[tuple[float, str, str, str, list[str]]] = []
    for filename, title, chunk, fm, t1, ft, t1t in chunks:
        # 2 tầng: đúng dấu (10đ) = từ điển tương đương (10đ, "type"~"loại") >
        # chỉ khớp bỏ dấu (3đ, vì "lời/lợi", "mời/mỗi" nhập nhằng).
        cov, eff_hits, title_pts = 0, 0.0, 0
        all_tier1 = len(active) >= 2
        for t in active:
            variants = raw_by_fold.get(t, set())
            c1 = max([C1(t1, v) for v in variants] + [0])
            if c1:
                cov += 10
                eff_hits += c1
            else:
                eq_hits = sum(C(fm, _norm(e)) for e in _PHRASE_EQUIV.get(t, []))
                if eq_hits:
                    cov += 10
                    eff_hits += min(eq_hits, 3)
                else:
                    cf = C(fm, t)
                    if cf:
                        cov += 3
                        eff_hits += 0.3 * cf
                    all_tier1 = False
            if max([C1(t1t, v) for v in variants] + [0]):
                title_pts += 5
            elif pats[t].search(ft):
                title_pts += 2
        if cov == 0:
            continue
        density = min(eff_hits / (len(fm) / 1000 + 1), 10)
        score = cov + density + title_pts + (8 if all_tier1 else 0)
        # Cụm nguyên văn: dài trước, cụm con bị nuốt ("chờ lời mời" nuốt
        # "lời mời"); đúng dấu 12đ, chỉ khớp bỏ dấu 6đ.
        ordered = sorted(set(raw_of), key=len, reverse=True)
        matched: list[str] = []
        layer = 0
        for pf in ordered:
            if " " not in pf or any(pf in m for m in matched):
                continue
            if C1(t1, _norm(raw_of[pf])):
                layer += 12
                matched.append(pf)
            elif C(fm, pf):
                layer += 6
                matched.append(pf)
        # Cụm + từ khác đứng gần nhau (<400 ký tự): đúng ngữ cảnh.
        if matched:
            in_phrase = set()
            for m in matched:
                in_phrase.update(m.split())
            prox_terms = [t for t in active
                          if t not in in_phrase
                          and any(pats1[v].search(t1) for v in raw_by_fold.get(t, ()))]
            spans = [mm.start() for m in matched for mm in pats1[_norm(raw_of[m])].finditer(t1)]
            if prox_terms and spans:
                near = [mm.start() for t in prox_terms for v in raw_by_fold[t]
                        for mm in pats1[v].finditer(t1)]
                if any(abs(s - n) <= 400 for s in spans for n in near):
                    layer += 8
        for e in equivs:
            if pats[_norm(e)].search(fm):
                layer += 4
        equiv_title = sum(1 for e in equivs if pats[_norm(e)].search(ft))
        score += min(layer + min(equiv_title, 2) * 4, 24)
        if score < 11:  # chỉ trúng 1 từ lẻ, yếu — bỏ để khỏi nhiễu
            continue
        scored.append((score, filename, title, chunk, list(active) + matched + list(equivs)))
    scored.sort(key=lambda item: -item[0])
    if not scored:
        return f"Không tìm thấy gì cho “{query}” trong kho kiến thức.", ""
    parts, sources = [], []
    for _, filename, title, chunk, anchors in scored[:top_k]:
        parts.append(f"[{title} — {filename}]\n{_snippet(chunk, anchors)}")
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
