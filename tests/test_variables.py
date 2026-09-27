"""Variables/PHS: mũi tên, cặp Transference/Distraction, gắn vào chart."""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from hd_calculator import calculate_hd_chart  # noqa: E402
from hd_variables import (  # noqa: E402
    COGNITION,
    DETERMINATION,
    ENVIRONMENT,
    MOTIVATION,
    PERSPECTIVE,
    analyze_variables,
    arrow_of,
    format_variables_report,
)


def test_arrow_rule_tone_123_left_456_right():
    assert [arrow_of(t) for t in (1, 2, 3)] == ["L", "L", "L"]
    assert [arrow_of(t) for t in (4, 5, 6)] == ["R", "R", "R"]


def test_transfer_distraction_pairs_are_opposite():
    for c, m in MOTIVATION.items():
        assert abs(c - m["transference"]) == 3
        assert MOTIVATION[m["transference"]]["transference"] == c
    for c, v in PERSPECTIVE.items():
        assert abs(c - v["distraction"]) == 3
        assert PERSPECTIVE[v["distraction"]]["distraction"] == c


def test_tables_complete():
    assert len(DETERMINATION) == len(ENVIRONMENT) == 6
    assert len(MOTIVATION) == len(PERSPECTIVE) == len(COGNITION) == 6
    for table in (DETERMINATION, ENVIRONMENT):
        for c, row in table.items():
            assert row["L"] and row["R"] and row["tip"], c


def test_variables_follow_source_positions():
    chart = calculate_hd_chart(datetime(1990, 5, 15, 8, 30))
    v = analyze_variables(chart)
    assert v["determination"]["color"] == chart["design_gates"]["Sun"]["color"]
    assert v["determination"]["tone"] == chart["design_gates"]["Sun"]["tone"]
    assert v["environment"]["color"] == chart["design_gates"]["North Node"]["color"]
    assert v["motivation"]["color"] == chart["personality_gates"]["Sun"]["color"]
    assert v["perspective"]["color"] == chart["personality_gates"]["North Node"]["color"]
    assert v["cognition"]["tone"] == chart["design_gates"]["Sun"]["tone"]
    assert v["code"] == (
        f"D{v['determination']['arrow']}{v['environment']['arrow']}"
        f"-P{v['motivation']['arrow']}{v['perspective']['arrow']}"
    )
    report = format_variables_report(v)
    assert v["code"] in report and "Giác quan" in report


def test_chart_carries_variables_and_arrows_vary():
    codes = set()
    start = datetime(2000, 1, 1)
    for i in range(40):
        chart = calculate_hd_chart(start + timedelta(days=i * 9, hours=5))
        assert "variables" in chart and chart["variables"]["code"]
        codes.add(chart["variables"]["code"])
    assert len(codes) > 10  # mũi tên phân bố, không kẹt một mã
