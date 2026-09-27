"""Transits & chu kỳ: Solar/Saturn/Uranus return, snapshot, assistant tool."""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from hd_transits import (  # noqa: E402
    TRANSIT_PLANETS,
    cycle_events,
    format_transit_report,
    transit_snapshot,
)

BIRTH = datetime(1990, 5, 15, 1, 30)  # 08:30 +07:00


def _by_name(events, name):
    return sorted(e["date"] for e in events if e["event_en"] == name)


def test_solar_returns_land_on_birthdays():
    dates = _by_name(cycle_events(BIRTH, years_after=5), "Solar Return")
    assert len(dates) >= 5
    for d in dates[1:]:
        assert (d.month, d.day) in ((5, 14), (5, 15), (5, 16)), d


def test_outer_planet_milestones_near_expected_ages():
    events = cycle_events(BIRTH)
    saturn1 = _by_name(events, "Saturn Return")[0]
    assert 28 * 365 < (saturn1 - BIRTH).days < 31 * 365
    ura_opp = _by_name(events, "Uranus Opposition")[0]
    assert 38 * 365 < (ura_opp - BIRTH).days < 46 * 365


def test_snapshot_is_deterministic_and_well_formed():
    asof = datetime(2026, 9, 28, 0, 0)
    a = transit_snapshot(BIRTH, asof)
    b = transit_snapshot(BIRTH, asof)
    assert a == b
    assert set(a["planets"]) == set(TRANSIT_PLANETS)
    for info in a["planets"].values():
        assert 1 <= info["gate"] <= 64 and 1 <= info["line"] <= 6
    for e in a["electromagnetics"]:
        assert 1 <= e["transit_gate"] <= 64 and 1 <= e["natal_gate"] <= 64
    text = format_transit_report(a, cycle_events(BIRTH))
    assert "Transit lúc 2026-09-28" in text and "Solar Return" in text


def test_assistant_tool_transits():
    from backend.api.assistant_tools import calculate_transits, make_executor
    text, source = calculate_transits("1990-05-15", "08:30", "+07:00", "2026-09-28")
    assert "Transit cho 1990-05-15" in text and "Swiss Ephemeris" in source
    bad, _ = calculate_transits("15/05/1990", "08:30", "+07:00")
    assert "chưa đúng" in bad
    out, _ = make_executor(None, None)("calculate_transits", {"birth_date": "1990-05-15",
                                                              "birth_time": "08:30"})
    assert "Transit cho" in out
