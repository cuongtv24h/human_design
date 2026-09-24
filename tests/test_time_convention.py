"""Quy ước thời gian: nhập & hiển thị giờ khai báo (giờ Việt Nam), tính bằng UTC.

Chuẩn: Việt Nam = UTC+07:00 cố định; KHÔNG tự áp offset lịch sử theo ngày sinh.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from hd_time import (  # noqa: E402
    display_birth,
    format_local,
    local_to_utc,
    normalize_offset,
    zone_label,
)


# --- Công thức: giờ khai báo − 7 giờ = UTC ------------------------------------

@pytest.mark.parametrize(
    ("date_text", "time_text", "expected_utc"),
    [
        ("1990-05-15", "08:30", datetime(1990, 5, 15, 1, 30)),
        ("1990-05-15", "00:30", datetime(1990, 5, 14, 17, 30)),  # lùi sang ngày hôm trước
        ("2000-01-01", "03:00", datetime(1999, 12, 31, 20, 0)),  # lùi sang năm trước
        ("2024-03-01", "06:59:30", datetime(2024, 2, 29, 23, 59, 30)),  # năm nhuận + giây
    ],
)
def test_vn_time_minus_seven_hours_is_utc(date_text, time_text, expected_utc):
    assert local_to_utc(date_text, time_text) == expected_utc


@pytest.mark.parametrize(
    ("date_text", "time_text"),
    [
        ("1945-06-01", "12:00"),  # tzdata: +09:00 — không áp
        ("1950-06-01", "12:00"),  # tzdata: +08:00 — không áp
        ("1962-10-28", "02:16"),  # miền Nam tzdata: +08:00 — không áp
        ("1974-12-31", "23:00"),
        ("1990-05-15", "08:30"),
    ],
)
def test_no_historical_offset_is_applied(date_text, time_text):
    """Mọi ngày sinh đều trừ đúng 7 giờ — kể cả giai đoạn tzdata ghi offset khác."""
    local = datetime.fromisoformat(f"{date_text}T{time_text}")
    assert (local - local_to_utc(date_text, time_text)).total_seconds() == 7 * 3600
    # Tên múi giờ Việt Nam cũng quy về +07:00 cố định, không đổi theo lịch sử.
    assert local_to_utc(date_text, time_text, "Asia/Ho_Chi_Minh") == local_to_utc(date_text, time_text)


def test_offset_normalization_and_rejections():
    for alias in ("", None, "+07:00", "+7", "+0700", "UTC+7", "GMT+7", "Asia/Ho_Chi_Minh", "Asia/Saigon", "VN"):
        assert normalize_offset(alias) == "+07:00"
    assert normalize_offset("+8") == "+08:00"
    assert normalize_offset("-05:30") == "-05:30"
    for bad in ("Europe/London", "abc", "+25:00", "+07:99"):
        with pytest.raises(ValueError):
            normalize_offset(bad)
    # Offset cố định khác vẫn được tôn trọng khi người gọi chủ động truyền (VD sinh ở nước ngoài).
    assert local_to_utc("1990-05-15", "08:30", "+08:00") == datetime(1990, 5, 15, 0, 30)


def test_display_is_exactly_the_declared_time():
    assert format_local("1990-05-15", "08:30") == "15/05/1990 08:30"
    assert display_birth("1990-05-15", "08:30") == "15/05/1990 08:30 (giờ Việt Nam)"
    assert display_birth("1990-05-15", "08:30", "+08:00") == "15/05/1990 08:30 (UTC+08:00)"
    assert zone_label("Asia/Ho_Chi_Minh") == "giờ Việt Nam"


# --- Mọi entry point dùng chung một quy ước -----------------------------------

def test_all_entry_points_compute_the_same_utc_and_chart():
    import server
    from hd_calculator import calculate_hd_chart
    from hd_cli import parse_datetime

    from backend.reporting.contract import ReportRequest
    from backend.reporting.orchestrator import ReportOrchestrator, _parse_birth_datetime

    expected = datetime(1962, 10, 28, 2, 16) - __import__("datetime").timedelta(hours=7)
    assert server.parse_birth_datetime("1962-10-28", "02:16") == expected
    assert _parse_birth_datetime("1962-10-28", "02:16", "+07:00") == expected
    assert parse_datetime("1962-10-28", "02:16", "+07:00")[0] == expected

    chart = calculate_hd_chart(expected)
    document = ReportOrchestrator().run(
        ReportRequest.model_validate({"subject": {"birth_date": "1962-10-28", "birth_time": "02:16"}})
    )
    mcp_chart = server.calculate_human_design_chart("1962-10-28", "02:16")
    for key in ("type", "authority", "profile", "definition", "incarnation_cross"):
        assert document.chart[key] == chart[key] == mcp_chart[key]


def test_request_validation_normalizes_or_rejects_timezone():
    from pydantic import ValidationError

    from backend.reporting.contract import ReportRequest

    subject = {"birth_date": "1990-05-15", "birth_time": "08:30"}
    assert ReportRequest.model_validate({"subject": subject}).subject.timezone == "+07:00"
    assert ReportRequest.model_validate({"subject": {**subject, "timezone": "+7"}}).subject.timezone == "+07:00"
    with pytest.raises(ValidationError):
        ReportRequest.model_validate({"subject": {**subject, "timezone": "Europe/London"}})


# --- Hiển thị: báo cáo, BodyGraph, infographic, brief LLM đều dùng giờ khai báo --

def test_every_display_surface_shows_declared_time_not_utc():
    from backend.reporting import build_llm_brief
    from backend.reporting.contract import ReportRequest
    from backend.reporting.export import bodygraph_svg
    from backend.reporting.infographic import render_infographic_html as infographic
    from backend.reporting.orchestrator import ReportOrchestrator

    document = ReportOrchestrator().run(
        ReportRequest.model_validate(
            {"subject": {"name": "A", "birth_date": "1990-05-15", "birth_time": "08:30"}, "tier": "deep_core"}
        )
    )
    declared = "15/05/1990 08:30 (giờ Việt Nam)"
    surfaces = {
        "markdown": document.to_markdown(),
        "bodygraph": bodygraph_svg(document),
        "infographic": infographic(document),
        "llm_brief": build_llm_brief(document),
    }
    assert "Ngày sinh: 15/05/1990 · Giờ sinh: 08:30 (giờ Việt Nam)" in surfaces["markdown"]
    for name in ("bodygraph", "infographic", "llm_brief"):
        assert declared in surfaces[name], name
    for name, text in surfaces.items():
        assert "01:30" not in text, f"{name} must not show the UTC time"
        assert "GMT" not in text, name
        assert "UTC+07:00" not in text, name
