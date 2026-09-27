"""Unit tests cho block renderer (không cần DB)."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.reporting.blocks import (  # noqa: E402
    BLOCK_VARIABLES,
    build_block_context,
    extract_variables,
    render_block,
)

CHART = {
    "type": "Generator", "strategy": "To Respond", "authority": "Sacral", "profile": "1/3",
    "definition": "Single Definition", "incarnation_cross": "Right Angle Cross of Test",
    "cross_type": "Right Angle", "defined_centers": ["Sacral", "G", "Throat"],
    "defined_channels": [[20, 34], [1, 8]], "all_activated_gates": [1, 8, 10, 20, 34],
}
SUBJECT = {"name": "An", "birth_date": "1990-05-15", "birth_time": "08:30",
           "timezone": "+07:00", "birth_place": "Hòa Bình"}


def _ctx(org=None):
    return build_block_context(CHART, SUBJECT, org)


def test_variables_and_vn_labels():
    md, warnings = render_block("Chào {{subject.name}} ({{subject.birth_place}}), bạn là {{chart.type_vn}}.", _ctx())
    assert warnings == []
    assert "Chào An (Hòa Bình)" in md
    assert "Generator" in render_block("{{chart.type}}", _ctx())[0]
    assert render_block("{{chart.defined_centers_count}}", _ctx())[0] == "3"
    assert "20-34" in render_block("{{chart.defined_channels}}", _ctx())[0]


def test_unknown_variable_warns_and_renders_empty():
    md, warnings = render_block("A{{chart.khong_co}}B{{subject.name}}", _ctx())
    assert md == "ABAn"
    assert len(warnings) == 1 and "khong_co" in warnings[0]


def test_if_blocks():
    ctx = _ctx()
    assert render_block("{{#if chart.hanging_gates}}có{{/if}}", ctx)[0] == "có"
    assert render_block("{{#if chart.type}}T{{/if}}{{#if subject.unknown}}X{{/if}}", ctx)[0] == "T"
    _, warnings = render_block("{{#if subject.unknown}}X{{/if}}", ctx)
    assert warnings and "unknown" in warnings[0]


def test_each_over_scalars_and_dicts():
    assert render_block("{{#each chart.hanging_gates}}[{{this}}]{{/each}}", _ctx())[0] == "[10]"
    md, warnings = render_block("{{#each chart.hanging_gates_detail}}{{this.gate}}:{{this.center}};{{/each}}", _ctx())
    assert warnings == [] and md.startswith("10:")
    assert "G" in md or "Sacral" in md
    md, warnings = render_block("{{#each chart.type}}x{{/each}}", _ctx())
    assert md == "" and warnings


def test_org_vars_and_unclosed_tag():
    md, warnings = render_block("LH {{org.hotline}}", _ctx({"hotline": "1900 6868"}))
    assert md == "LH 1900 6868" and warnings == []
    md, warnings = render_block("{{#if chart.type}}mở", _ctx())
    assert "mở" in md and any("đóng" in w for w in warnings)


def test_extract_variables_and_docs_cover_context():
    assert extract_variables("{{subject.name}} {{#each chart.hanging_gates}}{{this.gate}}{{/each}}{{this}}") == {
        "subject.name", "chart.hanging_gates"}
    documented = {v["path"] for v in BLOCK_VARIABLES if not v["path"].startswith("org.")}
    ctx = _ctx()
    for path in documented:
        node = ctx
        for part in path.split("."):
            assert part in node, path
            node = node[part]
