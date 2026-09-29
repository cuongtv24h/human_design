"""MG rule — PRESENCE + DIRECT (đối chứng nguồn; KHÔNG đổi code).

Kết luận audit đã chốt (chờ duyệt → nay thực thi **chỉ** comment + test):

- **Theo**: geneticmatrix, humandesigncollective (nguyên văn *"directly connects"*),
  freehumandesignchart → Manifesting Generator = Sacral định nghĩa **và** kênh
  **TRỰ TIẾP** (1 hop) nối Throat↔Motor.
- **Không theo** (thiểu số): jovian (*"pathway"*), humandesignhd (*"complete
  chain"*) — cho phép đường gián tiếp qua center trung gian.

Test chốt bằng **spec độc lập** (viết lại quy tắc từ nguồn, không sao chép code)
chạy trên 1250 lá số (1930–2028, seed cố định): 0 mismatch + đủ case phân biệt
(Generator có đường gián tiếp Throat→motor nhưng KHÔNG kênh trực tiếp — luật
jovian sẽ gọi là MG, code phải trả **Generator**).
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from hd_calculator import CHANNEL_TO_CENTERS, calculate_hd_chart  # noqa: E402

MOTORS = {"Heart", "Solar Plexus", "Sacral", "Root"}


def _has_direct_throat_motor(channels: list[tuple[int, int]]) -> bool:
    """PRESENCE: tồn tại kênh 1 hop Throat↔Motor (spec từ nguồn 'directly')."""
    for g1, g2 in channels:
        centers = CHANNEL_TO_CENTERS.get((g1, g2)) or CHANNEL_TO_CENTERS.get((g2, g1))
        if centers and "Throat" in centers and (set(centers) - {"Throat"}) & MOTORS:
            return True
    return False


def _has_indirect_path(channels: list[tuple[int, int]]) -> bool:
    """Đường Throat→motor DÀI ≥2 hop qua center trung gian (luật jovian)."""
    adj: dict[str, set[str]] = {}
    for g1, g2 in channels:
        centers = CHANNEL_TO_CENTERS.get((g1, g2)) or CHANNEL_TO_CENTERS.get((g2, g1))
        if centers:
            adj.setdefault(centers[0], set()).add(centers[1])
            adj.setdefault(centers[1], set()).add(centers[0])
    seen, stack = {"Throat"}, ["Throat"]
    hops = 0
    frontier = ["Throat"]
    while frontier and hops < 1:  # dừng ở mức trung gian — loại kênh trực tiếp
        nxt = []
        for node in frontier:
            for nb in adj.get(node, ()):
                if nb not in seen:
                    seen.add(nb)
                    nxt.append(nb)
        frontier = nxt
        hops += 1
    # Từ các trung gian đã tới (bỏ Throat), còn đường nào chạm motor không?
    stack = list(seen - {"Throat"})
    while stack:
        node = stack.pop()
        if node in MOTORS:
            return True
        for nb in adj.get(node, ()):
            if nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return False


def _expected_type(centers: set[str], channels: list[tuple[int, int]]) -> str:
    """Spec độc lập từ nguồn: Reflector / MG / Generator / Manifestor / Projector."""
    direct = _has_direct_throat_motor(channels)
    has_sacral = "Sacral" in centers
    if not centers:
        return "Reflector"
    if has_sacral:
        return "Manifesting Generator" if direct else "Generator"
    return "Manifestor" if direct else "Projector"


def _corpus() -> list[datetime]:
    """1250 ngày cố định — không random, không flaky."""
    out: list[datetime] = []
    for year in range(1930, 2030, 2):
        for ordinal in (1, 15) + tuple(range(30, 361, 15)):
            out.append(datetime.fromordinal(datetime(year, 1, 1).toordinal() + ordinal)
                       .replace(hour=7, minute=30))
    return out


def test_type_rule_matches_presence_direct_spec():
    """1250 lá số: code == spec — khoá toàn bộ5 nhánh type theo luật direct."""
    mg = indirect_generators = 0
    for dt in _corpus():
        chart = calculate_hd_chart(dt)
        expected = _expected_type(chart["defined_centers"], chart["defined_channels"])
        assert chart["type"] == expected, (dt, chart["type"], expected)
        if chart["type"] == "Manifesting Generator":
            mg += 1
        if (chart["type"] == "Generator"
                and _has_indirect_path(chart["defined_channels"])):
            indirect_generators += 1
    # Corpus phải VẬN HÀNH được cả2 nhánh quyết định:
    assert mg >= 100, mg  # direct MG có thật
    assert indirect_generators >= 1, (
        "corpus thiếu case Generator có đường gián tiếp — không khoá được luật direct"
    )


def test_indirect_path_generator_is_not_mg():
    """Case phân biệt (1930-01-02 đã dò thấy): Sacral + đường gián tiếp
    Throat→motor nhưng KHÔNG kênh trực tiếp → Generator, KHÔNG phải MG."""
    dt = datetime(1930, 1, 2, 7, 30)
    chart = calculate_hd_chart(dt)
    assert "Sacral" in chart["defined_centers"]
    assert not _has_direct_throat_motor(chart["defined_channels"])
    assert _has_indirect_path(chart["defined_channels"])
    assert chart["type"] == "Generator"
