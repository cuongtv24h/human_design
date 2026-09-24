"""Tests for the natural-Vietnamese narrative template (Operating Manual)."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from backend.reporting import language_vn
from backend.reporting.contract import ReportRequest, ReportTemplate
from backend.reporting.orchestrator import ReportOrchestrator

SUBJECT = {
    "name": "Khách hàng thử nghiệm",
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "timezone": "+07:00",
    "birth_location": "Hòa Bình, Việt Nam",
}

PART_IDS = [
    "part1_identity",
    "part2_decision_compass",
    "part3_burden_release",
    "part4_role_profile",
    "part5_field_application",
]


def _run(template="operating_manual", domains=None):
    payload: dict = {"subject": SUBJECT, "template": template}
    if domains:
        payload["domains"] = domains
    return ReportOrchestrator().run(ReportRequest.model_validate(payload))


def test_template_defaults_to_sections():
    request = ReportRequest.model_validate({"subject": SUBJECT})
    assert request.template is ReportTemplate.SECTIONS
    document = ReportOrchestrator().run(request)
    assert [section.id for section in document.sections] == [
        "summary",
        "type_strategy_authority",
        "profile_definition",
        "centers",
        "practical_actions",
    ]


def test_operating_manual_renders_five_parts_in_order():
    document = _run()

    assert [section.id for section in document.sections] == PART_IDS
    assert document.plan.definition_key == "operating_manual"
    assert document.title.startswith("Bản Thiết Kế Bản Thân")
    assert not document.warnings

    markdown = document.to_markdown()
    # Sponge metaphor for open centers (this chart has Heart + Sacral open).
    assert "bọt biển" in markdown
    # Type life name leads, raw calculator strings never appear verbatim.
    assert language_vn.TYPE_LANGUAGE[document.chart["type"]]["life_name"] in markdown
    assert document.chart["strategy"] not in markdown
    # Shared terminology layer: polished Vietnamese terms in the "Thuật ngữ:" lines,
    # not the raw bilingual calculator strings.
    assert language_vn.vn_strategy(document.chart["strategy"], document.chart["type"]) in markdown
    assert language_vn.vn_authority(document.chart["authority"]) in markdown
    assert "Thuật ngữ:" in markdown


def test_authority_compass_with_three_steps():
    document = _run()
    authority_key = language_vn.resolve_authority(document.chart["authority"])
    authority = language_vn.AUTHORITY_LANGUAGE[authority_key]

    markdown = document.to_markdown()
    assert authority["compass_name"] in markdown
    assert "Ba bước để 'nghe' la bàn" in markdown
    assert len(authority["steps"]) == 3
    for step in authority["steps"]:
        assert step in markdown
    assert authority["scenario_business"] in markdown
    assert authority["scenario_purchase"] in markdown


def test_open_centers_get_sponge_description_and_question():
    document = _run()
    order = [
        "Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral",
        "Solar Plexus", "Root",
    ]
    open_centers = [c for c in order if c not in set(document.chart["defined_centers"])]
    assert open_centers, "sample subject should have open centers"

    markdown = document.to_markdown()
    for center in open_centers:
        entry = language_vn.CENTER_LANGUAGE[center]
        assert entry["open_life"] in markdown
        assert entry["open_question"] in markdown


def test_profile_story_and_definition_rendered():
    document = _run()
    profile = document.chart["profile"]
    story = language_vn.PROFILE_STORIES[profile]
    markdown = document.to_markdown()

    assert story["story_name"] in markdown
    assert story["mistake_reframe"] in markdown
    assert language_vn.DEFINITION_LANGUAGE[document.chart["definition"]] in markdown


def test_seven_day_log_personalized_by_authority():
    document = _run()
    part5 = document.sections[4]
    assert part5.data["exercise_count"] == 3
    markdown = part5.content_markdown
    assert "Nghe tín hiệu" in markdown
    assert "Săn bọt biển" in markdown
    assert "Nhiên liệu đúng" in markdown
    assert "7 ngày" in markdown


def test_render_is_deterministic():
    first = _run()
    second = _run()
    assert [
        (section.id, section.content_markdown, section.data)
        for section in first.sections
    ] == [
        (section.id, section.content_markdown, section.data)
        for section in second.sections
    ]


def test_domains_attach_after_narrative_parts():
    document = _run(domains=["money"])

    assert [section.id for section in document.sections][:5] == PART_IDS
    assert document.sections[-1].id == "domain_money"
    assert document.sections[-1].order == 5
    assert not document.warnings
    assert document.to_markdown().count("## ") >= 6
