"""Quy ước thời gian dùng chung cho mọi nơi tính và hiển thị giờ sinh.

Quy ước (chủ dự án chốt 2026-09-24):

1. **Nhập:** giờ sinh theo giờ Việt Nam, đúng như người dùng khai báo.
2. **Chuẩn:** múi giờ Việt Nam = **UTC+07:00 cố định**. Hệ thống **không** tự áp
   offset lịch sử theo ngày sinh (VD giai đoạn miền Nam dùng UTC+8 trước 1975) —
   tính đúng theo giờ người dùng khai báo.
3. **Tính toán:** Swiss Ephemeris cần thời điểm ở thang UT, nên
   ``UTC = giờ khai báo − 7 giờ``. Đây là bước nội bộ, không hiển thị.
4. **Hiển thị:** báo cáo, BodyGraph, infographic, PDF luôn hiển thị **giờ khai báo**
   (``15/05/1990 08:30 (giờ Việt Nam)``), không hiển thị giờ UTC.

API vẫn nhận một offset cố định khác (``+08:00``, ``-05:00``...) khi người gọi chủ
động truyền vào (VD người sinh ở nước ngoài). Tên múi giờ IANA chỉ được chấp nhận
cho Việt Nam (quy về +07:00); tên khác bị từ chối rõ ràng thay vì âm thầm đoán.

Module chỉ dùng thư viện chuẩn để mọi entry point (tools/, mcp/, backend/) import được.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

VN_UTC_OFFSET = "+07:00"
VN_TIME_LABEL = "giờ Việt Nam"

# Các cách gọi múi giờ Việt Nam → quy về +07:00 cố định (không dùng lịch sử tzdata).
_VN_ALIASES = {
    "",
    "vn",
    "vietnam",
    "viet nam",
    "ict",
    "asia/ho_chi_minh",
    "asia/saigon",
    "asia/hanoi",
    "utc+7",
    "gmt+7",
}

_OFFSET_RE = re.compile(r"^(?:utc|gmt)?\s*([+-])\s*(\d{1,2})(?::?(\d{2}))?$", re.IGNORECASE)


def normalize_offset(tz_text: str | None = None) -> str:
    """Return a canonical ``±HH:MM`` offset; Vietnam aliases and empty → ``+07:00``.

    Raises ``ValueError`` for anything that is not a fixed offset or a Vietnam alias.
    """
    raw = (tz_text or "").strip()
    if raw.lower() in _VN_ALIASES:
        return VN_UTC_OFFSET
    match = _OFFSET_RE.match(raw)
    if not match:
        raise ValueError(
            f"Múi giờ không hợp lệ: {tz_text!r}. Dùng offset cố định dạng +07:00 "
            "(mặc định giờ Việt Nam)."
        )
    sign, hours_text, minutes_text = match.groups()
    hours, minutes = int(hours_text), int(minutes_text or 0)
    if hours > 14 or minutes > 59:
        raise ValueError(f"Múi giờ ngoài phạm vi: {tz_text!r}")
    return f"{sign}{hours:02d}:{minutes:02d}"


def offset_timedelta(tz_text: str | None = None) -> timedelta:
    canonical = normalize_offset(tz_text)
    sign = 1 if canonical[0] == "+" else -1
    return sign * timedelta(hours=int(canonical[1:3]), minutes=int(canonical[4:6]))


def parse_local(date_text: str, time_text: str) -> datetime:
    """Parse the declared local birth date (``YYYY-MM-DD``) and time (``HH:MM[:SS]``)."""
    try:
        local_date = date.fromisoformat(str(date_text).strip())
    except ValueError as exc:
        raise ValueError(f"birth_date must be a valid YYYY-MM-DD date: {date_text}") from exc
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            parsed = datetime.strptime(str(time_text).strip(), fmt)
            return datetime.combine(local_date, parsed.time())
        except ValueError:
            continue
    raise ValueError("birth_time must use HH:MM or HH:MM:SS")


def local_to_utc(date_text: str, time_text: str, tz_text: str | None = VN_UTC_OFFSET) -> datetime:
    """Declared local time → naive UTC datetime used by ``calculate_hd_chart``."""
    local = parse_local(date_text, time_text)
    aware = local.replace(tzinfo=timezone(offset_timedelta(tz_text)))
    return aware.astimezone(timezone.utc).replace(tzinfo=None)


def format_local(date_text: str, time_text: str) -> str:
    """``1990-05-15``, ``08:30`` → ``15/05/1990 08:30`` (exactly the declared time)."""
    local = parse_local(date_text, time_text)
    pattern = "%d/%m/%Y %H:%M:%S" if local.second else "%d/%m/%Y %H:%M"
    return local.strftime(pattern)


def zone_label(tz_text: str | None = VN_UTC_OFFSET) -> str:
    """``giờ Việt Nam`` for +07:00, otherwise ``UTC±HH:MM``."""
    canonical = normalize_offset(tz_text)
    return VN_TIME_LABEL if canonical == VN_UTC_OFFSET else f"UTC{canonical}"


def display_birth(date_text: str, time_text: str, tz_text: str | None = VN_UTC_OFFSET) -> str:
    """Display string for reports/BodyGraph: ``15/05/1990 08:30 (giờ Việt Nam)``."""
    return f"{format_local(date_text, time_text)} ({zone_label(tz_text)})"


__all__ = [
    "VN_TIME_LABEL",
    "VN_UTC_OFFSET",
    "display_birth",
    "format_local",
    "local_to_utc",
    "normalize_offset",
    "offset_timedelta",
    "parse_local",
    "zone_label",
]
