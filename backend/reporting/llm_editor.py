"""Lớp biên tập LLM cho báo cáo (ContentMode.LLM).

Chuẩn báo cáo (``docs/NARRATIVE_STANDARD.md``): mọi báo cáo gồm
(1) thông tin người được phân tích + (2) BodyGraph tự sinh và (3) nội dung
theo một trong hai chế độ:

- ``template``: renderer deterministic (mặc định).
- ``llm``: LLM biên tập lại nội dung TRÊN DỮ LIỆU NGUỒN ĐÃ TÍNH TOÁN, với vai
  trò nhà chuyên môn bộ môn + chuyên gia tư vấn/tâm lý, viết thấu cảm và tâm
  tình dẫn dắt.

Module này KHÔNG gọi LLM. Nó cung cấp:

- ``LLM_PERSONA`` / ``LLM_RULES``: vai trò và quy tắc cứng của LLM.
- ``build_llm_brief(document)``: gói prompt đầy đủ (vai trò, quy tắc, dữ liệu
  nguồn, cấu trúc + nội dung template tham chiếu, bảng thuật ngữ chuẩn).
- ``validate_llm_draft(chart, markdown)``: kiểm tra bản nháp LLM có giữ nguyên
  các sự kiện kỹ thuật đã tính hay không.
- ``merge_llm_draft(document, drafts)``: ghép bản nháp LLM vào document, ghi
  provenance ``editor`` và cảnh báo nếu vi phạm sự kiện.

Nguyên tắc bất biến: LLM chỉ diễn giải/kể chuyện — không tính lại gate,
channel, center, type, authority, profile, cross; không bịa số liệu.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .contract import ReportDocument, ReportSection
from .style import style_brief_block
from hd_time import display_birth  # noqa: E402  (tools/ on sys.path via contract)
from .language_vn import (
    AUTHORITY_VN,
    CENTER_VN,
    DEFINITION_VN,
    NOT_SELF_SIGNATURE,
    STRATEGY_VN,
    TYPE_VN,
    vn_authority,
    vn_definition,
    vn_strategy,
    vn_type,
)

LLM_PERSONA = """\
Bạn là một chuyên gia Human Design có nhiều năm thực hành, đồng thời là một nhà
tư vấn tâm lý giàu kinh nghiệm. Bạn viết báo cáo cho một người cụ thể — không
viết cho đám đông. Giọng viết của bạn:

- Thấu cảm trước, phân tích sau: bắt đầu từ điều người đọc đang cảm, rồi mới
  chỉ ra cơ chế trong thiết kế của họ, rồi mới đến hành động cụ thể.
- Tâm tình dẫn dắt: viết như một người thầy ngồi cạnh, không như sách giáo khoa.
- Tôn trọng sự thật kỹ thuật: mọi con số, tên Type/Authority/Center/Kênh/Cổng
  đều lấy nguyên từ dữ liệu nguồn đã tính — bạn chỉ được kể lại bằng ngôn ngữ
  đời sống, không được thay đổi hay tính lại.
"""

LLM_RULES: tuple[str, ...] = (
    "KHÔNG tính lại bất kỳ giá trị kỹ thuật nào (Type, Strategy, Authority, "
    "Profile, Definition, Centers, Channels, Gates, Cross). Dữ liệu nguồn là "
    "duy nhất đúng.",
    "KHÔNG bịa số liệu, thời điểm, dự đoán tương lai hay lời khuyên y tế/tài "
    "chính/pháp lý cụ thể; luôn giữ disclaimer tự quan sát.",
    "Thuật ngữ quan trọng dùng dạng song ngữ trau chuốt 'Đời sống (English "
    "Term)' theo bảng thuật ngữ chuẩn kèm theo; cấm chuỗi thô kiểu "
    "'Wait to Respond - Chờ để Đáp Ứng'.",
    "Giữ tỉ lệ ~70% hành vi thực tế / 30% khái niệm kỹ thuật.",
    "Mỗi phần giữ đúng tiêu đề và thứ tự trong cấu trúc được giao; chỉ viết "
    "lại nội dung bên trong.",
    "Trả về đúng định dạng JSON: {\"<section_id>\": \"<markdown mới>\"} cho "
    "những phần bạn biên tập.",
)


def _glossary_lines() -> str:
    lines = ["| Loại | Giá trị nguồn | Thuật ngữ chuẩn |", "| --- | --- | --- |"]
    for key, value in TYPE_VN.items():
        lines.append(f"| Type | {key} | {key} · {value} |")
    for key, value in STRATEGY_VN.items():
        lines.append(f"| Strategy | ({key}) | {value} |")
    for key, value in AUTHORITY_VN.items():
        lines.append(f"| Authority | {key} | {value} |")
    for key, value in DEFINITION_VN.items():
        lines.append(f"| Definition | {key} | {value} |")
    for key, value in CENTER_VN.items():
        lines.append(f"| Center | {key} | {value} |")
    for key, (not_self, signature) in NOT_SELF_SIGNATURE.items():
        lines.append(f"| Signature/Not-Self | {key} | {signature} / {not_self} |")
    return "\n".join(lines)


_INTERNAL_TIME_KEYS = frozenset({"birth_datetime", "birth_jd", "design_jd", "design_datetime"})

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"
#: Moi section dinh kem toi da tung nay ky tu tu kho tri thuc.
BRIEF_KNOWLEDGE_PER_SECTION = 1500
#: Tran ngan sach tri thuc cho ca brief (kiem soat chi phi token LLM).
BRIEF_KNOWLEDGE_BUDGET = 18_000


def brief_knowledge(section, max_chars=BRIEF_KNOWLEDGE_PER_SECTION):
    """Trich kho tri thuc cho mot section, dua tren knowledge_refs cua no."""
    chunks = []
    used = 0
    for ref in section.knowledge_refs:
        if "/" in ref or ".." in ref:
            continue
        try:
            text = (KNOWLEDGE_DIR / ref).read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if not text:
            continue
        # Ha cap heading trong trich dan de khoi dung so muc cua brief.
        text = "\n".join("#" + line if line.startswith("## ") else line for line in text.split("\n"))
        head = "[Kho tri thức: " + ref + "]\n" + text
        room = max_chars - used
        if room <= 0:
            break
        if len(head) > room:
            head = head[:room].rstrip() + "\n…(còn nữa trong kho)"
        chunks.append(head)
        used += len(head)
    return "\n\n".join(chunks)


def strip_internal_times(value: Any) -> Any:
    """Recursively drop UTC / Julian-day keys from data shown to people or LLMs."""
    if isinstance(value, Mapping):
        return {k: strip_internal_times(v) for k, v in value.items() if k not in _INTERNAL_TIME_KEYS}
    if isinstance(value, list):
        return [strip_internal_times(v) for v in value]
    return value


def build_llm_brief(document: ReportDocument, section_ids: Iterable[str] | None = None,
                    style: Mapping[str, Any] | None = None) -> str:
    """Assemble the complete, self-contained prompt bundle for the LLM editor.

    ``section_ids`` limits the rewrite to those sections (editor: "AI biên tập phần này");
    the other sections are still listed as context so tone and facts stay consistent.
    ``style`` (P2) is a ``style_profile`` snapshot from the report request; when present,
    a "## 8" voice section is appended to the brief.
    """
    only = set(section_ids) if section_ids is not None else None
    # Internal calculation times (UTC, Julian Day, Design time) stay out of the brief:
    # the report only ever shows the declared Vietnam time (tools/hd_time.py).
    source = {k: v for k, v in document.chart.items() if k not in _INTERNAL_TIME_KEYS}
    chart_json = json.dumps(source, ensure_ascii=False, indent=2, default=str)
    rules = "\n".join(f"{index}. {rule}" for index, rule in enumerate(LLM_RULES, 1))
    ordered = sorted(
        (s for s in document.sections if s.status == "included"),
        key=lambda item: item.order,
    )
    # Ngân sách tri thức: mỗi section được biên tập đều có phần, tối đa trần
    # chung. Ưu tiên section domain trước (nội dung template mỏng hơn core).
    budgeted = [s for s in ordered if only is None or s.id in only]
    allowance = min(BRIEF_KNOWLEDGE_PER_SECTION * len(budgeted), BRIEF_KNOWLEDGE_BUDGET)
    excerpts: dict[str, str] = {}
    knowledge_used = 0
    for section in sorted(budgeted, key=lambda s: (0 if s.id.startswith("domain_") else 1, s.order)):
        if knowledge_used >= allowance:
            break
        excerpt = brief_knowledge(section, BRIEF_KNOWLEDGE_PER_SECTION)
        if excerpt:
            excerpts[section.id] = excerpt
            knowledge_used += len(excerpt)
    structure_blocks = []
    for section in ordered:
        if only is not None and section.id not in only:
            structure_blocks.append(f"### Section `{section.id}` — {section.title} (chỉ để tham khảo, KHÔNG viết lại)")
            continue
        block = (
            f"### Section `{section.id}` — {section.title}\n\n"
            f"Nội dung template tham chiếu:\n\n{section.content_markdown.rstrip()}"
        )
        excerpt = excerpts.get(section.id)
        if excerpt:
            block += (
                "\n\nTài liệu tham khảo từ kho tri thức "
                "(chỉ dùng để diễn giải — mọi số liệu lấy từ dữ liệu nguồn mục 4):\n\n"
                f"{excerpt}"
            )
        structure_blocks.append(block)
    subject = document.subject
    parts = [
            "# BIÊN TẬP BÁO CÁO HUMAN DESIGN",
            "## 1. Vai trò của bạn",
            LLM_PERSONA.strip(),
            "## 2. Quy tắc bắt buộc",
            rules,
            "## 3. Người được phân tích",
            f"- Tên: {subject.name or '(chưa có tên)'}\n"
            f"- Sinh: {display_birth(subject.birth_date, subject.birth_time, subject.timezone)}"
            f" · Nơi sinh: {subject.birth_location or '(không rõ)'}\n"
            "- Khi nhắc tới giờ sinh, dùng đúng giờ khai báo ở trên; không quy đổi, không nêu giờ UTC.",
            "## 4. Dữ liệu nguồn đã tính toán (source of truth — KHÔNG tính lại)",
            f"```json\n{chart_json}\n```",
            "## 5. Cấu trúc báo cáo và nội dung template tham chiếu",
            "\n\n".join(structure_blocks),
            "## 6. Bảng thuật ngữ chuẩn (bắt buộc dùng đúng)",
            _glossary_lines(),
            "## 7. Định dạng trả về",
            'JSON: {"<section_id>": "<markdown mới>"} — chỉ gồm những phần bạn biên tập.'
            + ("" if only is None else " Chỉ biên tập: " + ", ".join(f"`{sid}`" for sid in sorted(only)) + "."),
    ]
    style_block = style_brief_block(style)
    if style_block:
        parts.append(style_block)
    return "\n\n".join(parts)


def _required_facts(chart: Mapping[str, Any]) -> list[tuple[str, str]]:
    chart_type = str(chart.get("type", ""))
    type_life = TYPE_VN.get(chart_type, "")
    return [
        (f"Type '{chart_type}'", chart_type),
        (f"tên đời sống của Type '{type_life}'", type_life),
        ("chiến lược sống chuẩn", vn_strategy(str(chart.get("strategy", "")), chart_type)),
        ("quyền nội tại chuẩn", vn_authority(str(chart.get("authority", "")))),
        (f"Profile '{chart.get('profile', '')}'", str(chart.get("profile", ""))),
        ("định nghĩa chuẩn", vn_definition(str(chart.get("definition", "")))),
        ("Incarnation Cross", str(chart.get("incarnation_cross", ""))),
    ]


def validate_llm_draft(chart: Mapping[str, Any], markdown: str) -> list[str]:
    """Check that an LLM draft keeps every calculated technical fact visible."""
    text = markdown or ""
    violations: list[str] = []
    for label, fact in _required_facts(chart):
        if fact and fact not in text:
            violations.append(f"bản nháp LLM thiếu sự kiện kỹ thuật: {label} ({fact})")
    return violations


def missing_facts(chart: Mapping[str, Any], baseline_markdown: str, markdown: str) -> list[str]:
    """Technical facts present in ``baseline_markdown`` but lost in ``markdown``.

    Used after LLM rewrites and manual edits: a section keeps every calculated fact
    (Type, Strategy, Authority, Profile…) that its generated version carried.
    """
    return sorted({fact for _, fact in _required_facts(chart)
                   if fact and fact in baseline_markdown and fact not in markdown})


def merge_llm_draft(
    document: ReportDocument,
    drafts: Mapping[str, str],
    editor_model: str = "",
) -> ReportDocument:
    """Merge LLM-edited markdown into a copy of the document.

    Each draft is validated against the calculated chart; violations are kept
    as warnings (never silently dropped), and provenance records the editor.
    """
    updated = document.model_copy(deep=True)
    by_id = {section.id: section for section in updated.sections}
    for section_id, draft in drafts.items():
        section = by_id.get(section_id)
        if section is None or section.status != "included":
            updated.warnings.append(f"LLM draft cho section không tồn tại: {section_id}")
            continue
        # Facts the deterministic section carried must survive the rewrite.
        missing = missing_facts(updated.chart, section.content_markdown, draft)
        section.content_markdown = draft
        if missing:
            violations = [
                f"bản nháp LLM làm mất sự kiện kỹ thuật của phần: {fact}" for fact in missing
            ]
            section.warnings.extend(violations)
            updated.warnings.extend(f"{section_id}: {violation}" for violation in violations)
    updated.provenance.editor = f"llm:{editor_model}" if editor_model else "llm"
    return updated


__all__ = [
    "LLM_PERSONA",
    "LLM_RULES",
    "build_llm_brief",
    "merge_llm_draft",
    "missing_facts",
    "strip_internal_times",
    "validate_llm_draft",
]
