"""Contract and orchestration tests for the Admin/Coach report pipeline."""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from backend.reporting.contract import (
    DomainName,
    ReportRequest,
    ReportTier,
)
from backend.reporting.orchestrator import ReportOrchestrator


SUBJECT = {
    "name": "Khách hàng thử nghiệm",
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "timezone": "+07:00",
    "birth_location": "Hòa Bình, Việt Nam",
}


def test_report_request_deduplicates_domains_and_rejects_unknown_fields():
    request = ReportRequest.model_validate(
        {"subject": SUBJECT, "domains": ["money", "money", "decision"]}
    )

    assert request.tier is ReportTier.FREE_BASIC
    assert request.domains == [DomainName.MONEY, DomainName.DECISION]

    with pytest.raises(ValueError):
        ReportRequest.model_validate({"subject": {**SUBJECT, "unexpected": True}})
    with pytest.raises(ValueError):
        ReportRequest.model_validate({"subject": {**SUBJECT, "birth_time": "25:00"}})


def test_free_basic_report_has_chart_snapshot_plan_and_markdown():
    document = ReportOrchestrator().run(ReportRequest(subject=SUBJECT))

    assert document.tier is ReportTier.FREE_BASIC
    assert document.plan.definition_key == "free_basic"
    assert [section.id for section in document.sections] == [
        "summary",
        "type_strategy_authority",
        "profile_definition",
        "centers",
        "practical_actions",
    ]
    assert document.chart["type"]
    assert document.input_snapshot["subject"]["birth_date"] == SUBJECT["birth_date"]
    assert document.provenance.calculator_version
    markdown = document.to_markdown()
    assert "Type" in markdown
    # Display markdown uses the shared polished terminology — raw bilingual
    # calculator strings never reach the rendered report.
    from backend.reporting.language_vn import vn_authority, vn_strategy

    assert document.chart["strategy"] not in markdown
    assert document.chart["authority"] not in markdown
    assert vn_strategy(document.chart["strategy"], document.chart["type"]) in markdown
    assert vn_authority(document.chart["authority"]) in markdown
    # The complete contract must be serializable for persistence or an API.
    assert '"schema_name":"human_design.report"' in document.model_dump_json()


def test_deep_core_domain_is_normalized_and_keeps_provenance():
    request = ReportRequest.model_validate(
        {
            "subject": SUBJECT,
            "tier": "deep_core",
            "domains": ["money", "decision"],
        }
    )
    document = ReportOrchestrator().run(request)

    section_ids = [section.id for section in document.sections]
    assert "channels_gates" in section_ids
    assert "domain_money" in section_ids
    assert "domain_decision" in section_ids
    assert document.plan.tier is ReportTier.DEEP_CORE
    assert document.plan.domains == [DomainName.MONEY, DomainName.DECISION]
    assert document.sections[-1].source_tools == [
        "analyze_decision",
        "format_decision_report",
    ]
    assert document.sections[-2].data["money_analysis"]
    assert "13_money_wealth_full_map.md" in document.provenance.knowledge_refs
    assert not document.warnings


def test_deep_core_channels_and_cross_are_explained():
    request = ReportRequest.model_validate({"subject": SUBJECT, "tier": "deep_core"})
    document = ReportOrchestrator().run(request)

    from backend.reporting.language_vn import CROSS_FRAMING, vn_channel

    channels_section = next(s for s in document.sections if s.id == "channels_gates")
    cross_section = next(s for s in document.sections if s.id == "cross")

    # Every defined channel gets its bilingual name + life sentence.
    assert document.chart["defined_channels"]
    for gate1, gate2 in document.chart["defined_channels"]:
        lang = vn_channel(gate1, gate2)
        assert lang, f"missing language entry for channel {gate1}-{gate2}"
        assert lang["name"] in channels_section.content_markdown
        assert lang["life"] in channels_section.content_markdown
    assert "Cổng treo (Hanging Gates)" in channels_section.content_markdown

    # The cross section frames the meaning, not just the technical label.
    assert CROSS_FRAMING in cross_section.content_markdown
    assert document.chart["cross_type"] in cross_section.content_markdown


def test_relationship_domain_accepts_partner_snapshot():
    request = ReportRequest.model_validate(
        {
            "subject": SUBJECT,
            "tier": "deep_core",
            "domains": ["relationship"],
            "partner": {
                "name": "Đối tác",
                "birth_date": "1991-06-16",
                "birth_time": "09:30",
                "timezone": "+07:00",
            },
        }
    )
    document = ReportOrchestrator().run(request)

    relationship = next(section for section in document.sections if section.id == "domain_relationship")
    assert relationship.status == "included"
    assert document.partner is not None
    assert document.input_snapshot["partner"]["name"] == "Đối tác"
    assert relationship.data["relationship_analysis"]
