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
from typing import Any, Mapping

from .contract import ReportDocument
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


def build_llm_brief(document: ReportDocument) -> str:
    """Assemble the complete, self-contained prompt bundle for the LLM editor."""
    # Internal calculation times (UTC, Julian Day, Design time) stay out of the brief:
    # the report only ever shows the declared Vietnam time (tools/hd_time.py).
    source = {k: v for k, v in document.chart.items() if k not in _INTERNAL_TIME_KEYS}
    chart_json = json.dumps(source, ensure_ascii=False, indent=2, default=str)
    rules = "\n".join(f"{index}. {rule}" for index, rule in enumerate(LLM_RULES, 1))
    structure_blocks = []
    for section in sorted(document.sections, key=lambda item: item.order):
        if section.status != "included":
            continue
        structure_blocks.append(
            f"### Section `{section.id}` — {section.title}\n\n"
            f"Nội dung template tham chiếu:\n\n{section.content_markdown.rstrip()}"
        )
    subject = document.subject
    return "\n\n".join(
        [
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
            'JSON: {"<section_id>": "<markdown mới>"} — chỉ gồm những phần bạn biên tập.',
        ]
    )


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
        original_facts = [
            fact
            for _, fact in _required_facts(updated.chart)
            if fact and fact in section.content_markdown
        ]
        missing = sorted(fact for fact in original_facts if fact not in draft)
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
    "validate_llm_draft",
]
