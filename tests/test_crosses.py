"""Đợt 4: bảng 192 Incarnation Crosses — đủ mục, đúng cơ học, engine đặt tên chuẩn."""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from hd_calculator import calculate_hd_chart  # noqa: E402
from hd_crosses import CROSSES, PROFILES, get_cross, quarter_of, verify  # noqa: E402


def test_table_has_192_with_clean_mechanics():
    assert len(CROSSES) == 192
    assert verify() == []


def test_every_gate_has_all_three_geometries():
    for gate in range(1, 65):
        for geom in ("RAX", "LAX", "JX"):
            entry = get_cross(gate, geom)
            assert entry["gates"][0] == gate
            assert entry["name_vi"] and entry["meaning_vi"]


def test_jx_lax_share_gates_rax_differs():
    for gate in range(1, 65):
        assert get_cross(gate, "JX")["gates"] == get_cross(gate, "LAX")["gates"]
        assert get_cross(gate, "RAX")["gates"][2] != get_cross(gate, "JX")["gates"][2]


def test_quarter_coverage():
    assert {quarter_of(g) for g in range(1, 65)} == {1, 2, 3, 4}


def test_engine_names_cross_from_table():
    seen = set()
    start = datetime(2000, 1, 1)
    for i in range(60):
        chart = calculate_hd_chart(start + timedelta(days=i * 6, hours=7))
        p_gate = chart["personality_gates"]["Sun"]["gate"]
        geom = {"Right Angle": "RAX", "Left Angle": "LAX"}.get(chart["cross_type"], "JX")
        expected = f"{chart['cross_type']} Cross of {get_cross(p_gate, geom)['name_en']}"
        assert chart["incarnation_cross"] == expected
        assert chart["profile"] in PROFILES[geom]
        seen.add(geom)
    assert seen == {"RAX", "LAX", "JX"}


def test_knowledge_file_lists_all_192():
    text = (ROOT / "knowledge" / "08_192_incarnation_crosses_chi_tiet.md").read_text(encoding="utf-8")
    assert text.count("#### Sun ") == 64
    for (gate, geom), entry in CROSSES.items():
        assert f"**{geom} {entry['name_en']}" in text, (gate, geom)
