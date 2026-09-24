"""Tests for the report standard.

Standard: subject info + auto-generated BodyGraph + content in one of two
modes — deterministic ``template`` (default) or ``llm`` (edited draft merged
over the calculated data with fact validation).
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from backend.reporting import (
    LLM_PERSONA,
    build_llm_brief,
    export_report,
    merge_llm_draft,
    validate_llm_draft,
)
from backend.reporting.contract import ContentMode, ReportRequest
from backend.reporting.orchestrator import ReportOrchestrator

SUBJECT = {
    "name": "Khách hàng thử nghiệm",
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "timezone": "+07:00",
    "birth_location": "Hòa Bình, Việt Nam",
}


def _run(**extra):
    payload: dict = {"subject": SUBJECT}
    payload.update(extra)
    return ReportOrchestrator().run(ReportRequest.model_validate(payload))


def test_content_mode_defaults_to_template_and_accepts_llm():
    assert ReportRequest.model_validate({"subject": SUBJECT}).content_mode is ContentMode.TEMPLATE
    document = _run(content_mode="llm")
    assert document.content_mode is ContentMode.LLM


def test_markdown_carries_subject_information_block():
    document = _run()
    markdown = document.to_markdown()
    assert "Ngày sinh: 15/05/1990" in markdown
    assert "Giờ sinh: 08:30 (giờ Việt Nam)" in markdown
    assert "Nơi sinh: Hòa Bình, Việt Nam" in markdown


def test_llm_brief_contains_persona_rules_source_data_and_glossary():
    document = _run(tier="deep_core")
    brief = build_llm_brief(document)
    assert "chuyên gia Human Design" in brief
    assert "nhà" in brief and "tư vấn" in brief
    assert "KHÔNG tính lại" in brief
    assert document.chart["type"] in brief
    assert document.chart["incarnation_cross"] in brief
    assert "Chờ lời mời" in brief  # polished strategy term in the glossary
    assert "```json" in brief


def test_validate_llm_draft_detects_missing_facts():
    document = _run()
    chart = document.chart
    template = "\n".join(s.content_markdown for s in document.sections)
    # The full deterministic markdown carries all facts.
    assert validate_llm_draft(chart, template) == []
    # A draft that drops the authority is flagged.
    stripped = template.replace("Quyền Cảm xúc", "cảm xúc nói chung")
    violations = validate_llm_draft(chart, stripped)
    assert any("quyền nội tại" in v for v in violations)


def test_merge_llm_draft_stamps_editor_and_keeps_warnings():
    document = _run()
    summary = next(s for s in document.sections if s.id == "summary")
    good_draft = summary.content_markdown + "\n\nBạn không đơn độc trên hành trình này."
    merged = merge_llm_draft(document, {"summary": good_draft}, editor_model="test-model")

    assert merged.provenance.editor == "llm:test-model"
    merged_summary = next(s for s in merged.sections if s.id == "summary")
    assert merged_summary.content_markdown.endswith("Bạn không đơn độc trên hành trình này.")
    assert not merged.warnings
    # The original document stays untouched.
    assert document.provenance.editor == "template"

    bad_draft = "Một bài viết rất hay nhưng không còn số liệu nào."
    merged_bad = merge_llm_draft(document, {"summary": bad_draft})
    assert merged_bad.provenance.editor == "llm"
    assert merged_bad.warnings
    assert any("sự kiện kỹ thuật" in w for w in merged_bad.warnings)


def test_export_writes_markdown_and_bodygraph_svg(tmp_path):
    document = _run()
    paths = export_report(document, tmp_path)

    assert paths["markdown"].exists()
    assert paths["bodygraph_svg"].exists()
    svg = paths["bodygraph_svg"].read_text(encoding="utf-8")
    assert svg.lstrip().startswith("<svg") or svg.lstrip().startswith("<?xml")
    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert "![BodyGraph](" in markdown
    assert "Ngày sinh: 15/05/1990" in markdown

    plain = export_report(document, tmp_path / "plain", include_bodygraph=False)
    assert "![BodyGraph](" not in plain["markdown"].read_text(encoding="utf-8")
