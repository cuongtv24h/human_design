"""Transits & chu kỳ lớn (đề xuất cũ C).

- cycle_events(): Solar return hằng năm, Jupiter/Saturn return, Uranus
  opposition + return — ngày giờ tính bằng Swiss Ephemeris.
- transit_snapshot(): vị trí hành tinh transit tại thời điểm `asof` so với
  natal — cổng nào rơi vào trung tâm mở, transit nào nối điện từ
  (electromagnetic) với cổng treo natal.
- Chiron return (~50t) CHƯA tính: cần file ephemeris tiểu hành tinh ngoài
  phạm vi offline hiện tại; skill/KB ghi chú rõ giới hạn này.

Mọi datetime dùng chung quy ước với hd_calculator (UTC naive).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import swisseph as swe

from hd_calculator import (
    CHANNELS,
    GATE_TO_CENTER,
    calculate_hd_chart,
    get_all_planets,
    get_planet_longitude,
    julian_day,
)

# Đủ13 thiên thể như get_all_planets(): CÓ Earth (= Sun+180) và South Node
# (= North+180) — trước đây thiếu2 body này nên transit_snapshot() bỏ lỡ
# ~15% hit (Earth luôn đối đỉnh Sun — không thiếu được) và mất canal electromagnet.
TRANSIT_PLANETS = ("Sun", "Earth", "Moon", "North Node", "South Node",
                   "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                   "Uranus", "Neptune", "Pluto")


def _signed_diff(lon: float, target: float) -> float:
    return (lon - target + 180.0) % 360.0 - 180.0


def _refine_hit(planet_id: int, target: float, jd_guess: float,
                span: float = 2.0) -> float:
    """Mò ngày giờ giao hội/chính xác quanh điểm đoán (tinh dần 1d→0.02d)."""
    jd, step = jd_guess, 1.0
    while step >= 0.02:
        best_jd, best_diff = jd, 360.0
        t = jd - span * step * 2
        while t <= jd + span * step * 2:
            diff = abs(_signed_diff(get_planet_longitude(t, planet_id), target))
            if diff < best_diff:
                best_diff, best_jd = diff, t
            t += step
        jd, step = best_jd, step / 5.0
    return jd


def find_hits(planet_id: int, target: float, jd_start: float, jd_end: float,
              step: float = 5.0) -> list[float]:
    """Mọi lần chạm target trong khoảng (bắt cả nghịch hành chạm 3 lần)."""
    hits: list[float] = []
    prev_jd, prev_diff = jd_start, _signed_diff(get_planet_longitude(jd_start, planet_id), target)
    jd = jd_start + step
    while jd <= jd_end:
        diff = _signed_diff(get_planet_longitude(jd, planet_id), target)
        if prev_diff == 0 or diff == 0 or (prev_diff < 0) != (diff < 0):
            guess = prev_jd + step * abs(prev_diff) / (abs(prev_diff) + abs(diff) + 1e-9)
            hits.append(_refine_hit(planet_id, target, guess))
        prev_jd, prev_diff = jd, diff
        jd += step
    # Gộp hit trùng (nghịch hành quét lại cùng điểm trong <60 ngày)
    merged: list[float] = []
    for h in sorted(hits):
        if not merged or h - merged[-1] > 60:
            merged.append(h)
    return merged


def _jd_to_dt(jd: float) -> datetime:
    # UTC-naive như cũ; thay utcfromtimestamp() deprecated (py3.12)
    return datetime.fromtimestamp(
        (jd - 2440587.5) * 86400.0, tz=timezone.utc
    ).replace(tzinfo=None)


def cycle_events(birth_datetime: datetime, years_after: int = 85,
                 years_before: int = 0) -> list[dict]:
    """Các mốc chu kỳ lớn trong đời: Solar/Jupiter/Saturn return, Uranus opp/return."""
    birth_jd = julian_day(birth_datetime)
    natal_sun = get_planet_longitude(birth_jd, swe.SUN)
    natal_jup = get_planet_longitude(birth_jd, swe.JUPITER)
    natal_sat = get_planet_longitude(birth_jd, swe.SATURN)
    natal_ura = get_planet_longitude(birth_jd, swe.URANUS)
    events: list[dict] = []

    def add(hits, planet_id, name_en, name_vi, extra=""):
        for h in hits:
            events.append({"date": _jd_to_dt(h), "planet_id": planet_id,
                           "event_en": name_en, "event_vi": name_vi, "extra": extra})

    # Solar return: quanh sinh nhật mỗi năm (±6 ngày, bước 0.5d).
    for year in range(-years_before, years_after + 1):
        center = birth_jd + year * 365.25
        add(find_hits(swe.SUN, natal_sun, center - 6, center + 6, 0.5),
            swe.SUN, "Solar Return", "Sinh nhật năng lượng (Solar Return)",
            f"năm {year}" if year else "lúc sinh")

    # Jupiter return ~11.86 năm, Saturn return ~29.46 năm, Uranus ~84 năm.
    for k in range(1, 8):
        center = birth_jd + k * 11.86 * 365.25
        add(find_hits(swe.JUPITER, natal_jup, center - 400, center + 400, 10),
            swe.JUPITER, "Jupiter Return", "Jupiter Return (chu kỳ mở rộng)", f"lần {k}")
    for k in range(1, 4):
        center = birth_jd + k * 29.46 * 365.25
        add(find_hits(swe.SATURN, natal_sat, center - 500, center + 500, 12),
            swe.SATURN, "Saturn Return", "Saturn Return (trưởng thành)", f"lần {k}")
    opp = (natal_ura + 180.0) % 360.0
    add(find_hits(swe.URANUS, opp, birth_jd + 30 * 365.25, birth_jd + 55 * 365.25, 20),
        swe.URANUS, "Uranus Opposition", "Uranus đối đỉnh (~42t, giữa đời)", "")
    add(find_hits(swe.URANUS, natal_ura, birth_jd + 70 * 365.25, birth_jd + 95 * 365.25, 20),
        swe.URANUS, "Uranus Return", "Uranus Return (~84t)", "")

    events.sort(key=lambda e: e["date"])
    return events


def transit_snapshot(birth_datetime: datetime, asof: datetime | None = None) -> dict:
    """Ảnh transit tại `asof` (mặc định hiện tại UTC) so với natal."""
    asof = asof or datetime.now(tz=timezone.utc).replace(tzinfo=None)  # UTC-naive
    natal = calculate_hd_chart(birth_datetime)
    asof_jd = julian_day(asof)
    defined = set(natal["defined_centers"])
    channeled = {g for ch in natal["defined_channels"] for g in ch}
    hanging = set(natal["all_activated_gates"]) - channeled

    planets: dict[str, dict] = {}
    lons = get_all_planets(asof_jd)   # đủ13 body: Earth/South Node suy từ Sun/Node
    for name in TRANSIT_PLANETS:
        lon = lons[name]
        from hd_calculator import longitude_to_gate_line
        info = longitude_to_gate_line(lon)
        planets[name] = {"gate": info["gate"], "line": info["line"],
                         "longitude": round(lon, 2)}

    undefined_hits, electromagnetics = [], []
    for name, info in planets.items():
        center = GATE_TO_CENTER.get(info["gate"], "?")
        if center not in defined:
            undefined_hits.append({"planet": name, "gate": info["gate"],
                                   "line": info["line"], "center": center})
        for a, b in CHANNELS:
            mate = None
            if info["gate"] == a and b in hanging:
                mate = b
            elif info["gate"] == b and a in hanging:
                mate = a
            if mate is not None:
                electromagnetics.append(
                    {"planet": name, "transit_gate": info["gate"],
                     "natal_gate": mate, "channel": f"{min(a, b)}-{max(a, b)}",
                     "center": center})
    return {"birth_datetime": birth_datetime, "asof": asof, "planets": planets,
            "undefined_hits": undefined_hits, "electromagnetics": electromagnetics,
            "natal_type": natal["type"], "natal_profile": natal["profile"]}


def format_transit_report(snap: dict, events: list[dict] | None = None,
                          window_days: int = 370) -> str:
    """Tóm tắt transit tiếng Việt cho trợ lý/báo cáo."""
    lines = [f"Transit lúc {snap['asof']:%Y-%m-%d %H:%M} UTC "
             f"(natal {snap['natal_type']} {snap['natal_profile']}):"]
    hits = snap["undefined_hits"]
    if hits:
        lines.append(f"- {len(hits)} hành tinh transit rơi vào trung tâm mở natal:")
        for h in hits[:8]:
            lines.append(f"  · {h['planet']}: cổng {h['gate']}.{h['line']} → trung tâm mở {h['center']} (vùng điều kiện hóa hôm nay).")
    else:
        lines.append("- Không hành tinh nào rơi vào trung tâm mở.")
    elec = snap["electromagnetics"]
    if elec:
        lines.append(f"- {len(elec)} nối điện từ với cổng treo natal:")
        for e in elec[:8]:
            lines.append(f"  · {e['planet']} cổng {e['transit_gate']} nối cổng treo {e['natal_gate']} thành kênh {e['channel']}.")
    else:
        lines.append("- Không có nối điện từ với cổng treo natal.")
    if events is not None:
        asof, near = snap["asof"], []
        for ev in events:
            if timedelta(0) <= ev["date"] - asof <= timedelta(days=window_days):
                near.append(ev)
        if near:
            lines.append(f"- Mốc chu kỳ sắp tới (trong {window_days} ngày):")
            for ev in near[:6]:
                extra = f" {ev['extra']}" if ev["extra"] else ""
                lines.append(f"  · {ev['date']:%Y-%m-%d}: {ev['event_vi']}{extra}.")
    return "\n".join(lines)
