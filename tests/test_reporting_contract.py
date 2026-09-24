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
    assert "Type" in document.to_markdown()
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
