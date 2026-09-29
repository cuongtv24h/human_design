"""Authority — property-test thứ tự ưu tiên + hồi quy nhánh đã dọn (dot 6).

Bối cảnh: bản cũ c5ce7e7 có nhánh chết/sai trong khối Heart. Đối chứng 2500 lá số
(seed 20260929, 2026-09-29): **2456 (98%) giống, 44 khác — đúng 2 pattern sửa có
chủ đích, không có khác biệt bất thường nào**:

  1. Kênh 25-51 (Heart–G):  cũ ghi nhãn ``Ego (Heart) - Manifested`` **SAI**
     → mới ``Ego (Heart) - Projected``  (28/44 ca)
  2. Kênh 21-45 (Heart–Throat): cũ không phân biệt (thường ``Ego (Heart)``)
     → mới ``Ego (Heart) - Manifested``  (16/44 ca)
  3. Nhánh chết ``Self-Projected nếu Projector`` khi Heart+G định nghĩa đã bị dọn
     (Heart định nghĩa → quyền quyết định thuộc Heart, kể cả Projector).

Test này khoá cả3 điều trên + toàn bộ thứ tự ưu tiên, KHÔNG cần ephemeris
(trừ phần E2E nhỏ cuối file).
"""

from __future__ import annotations

import itertools
import pathlib
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from hd_calculator import calculate_hd_chart, get_authority  # noqa: E402

CENTERS = ["Head", "Ajna", "Throat", "G", "Heart", "Sacral", "Solar Plexus", "Spleen", "Root"]

ALL_LABELS = {
    "Emotional - Solar Plexus",
    "Sacral",
    "Splenic",
    "Ego (Heart) - Manifested",
    "Ego (Heart) - Projected",
    "Ego (Heart)",
    "Self-Projected (G-Center)",
    "Mental - Environment / No Inner Authority",
    "Lunar - Reflector",
}


def _expected_no_channel(centers: set[str]) -> str:
    """Quy tắc HD (spec, không sao chép code) khi KHÔNG có kênh đặc biệt nào."""
    if "Solar Plexus" in centers:
        return "Emotional - Solar Plexus"
    if "Sacral" in centers:
        return "Sacral"
    if "Spleen" in centers:
        return "Splenic"
    if "Heart" in centers:
        return "Ego (Heart)"
    if "G" in centers:
        return "Self-Projected (G-Center)"
    if centers & {"Ajna", "Throat", "Head"}:
        return "Mental - Environment / No Inner Authority"
    return "Lunar - Reflector"


# --- 1. Property: MỌI tập center (2^9 = 512) tuân thủ thứ tự ưu tiên ------------

def test_every_center_subset_follows_priority():
    for r in range(len(CENTERS) + 1):
        for combo in itertools.combinations(CENTERS, r):
            centers = set(combo)
            got = get_authority(centers, [])
            assert got == _expected_no_channel(centers), sorted(centers)
            assert got in ALL_LABELS


def test_empty_centers_is_reflector():
    assert get_authority([], []) == "Lunar - Reflector"


def test_priority_emotional_beats_everything():
    """Solar Plexus thắng mọi center khác — kể cả khi Heart/G cùng định nghĩa."""
    full = set(CENTERS)
    assert get_authority(full, []) == "Emotional - Solar Plexus"
    assert get_authority(full, [(21, 45)]) == "Emotional - Solar Plexus"


def test_priority_sacral_beats_spleen_heart_g():
    centers = {"Sacral", "Spleen", "Heart", "G", "Throat"}
    assert get_authority(centers, [(21, 45)]) == "Sacral"


def test_priority_spleen_beats_heart_g():
    centers = {"Spleen", "Heart", "G", "Throat"}
    assert get_authority(centers, []) == "Splenic"


# --- 2. Nhánh Heart theo kênh (2 cặp kênh, cả2 thứ tự) --------------------------

def test_heart_channel_2145_is_manifested():
    base = {"Heart", "G", "Throat"}
    assert get_authority(base, [(21, 45)]) == "Ego (Heart) - Manifested"
    assert get_authority(base, [(45, 21)]) == "Ego (Heart) - Manifested"  # thứ tự đảo


def test_heart_channel_2551_is_projected_not_manifested():
    """Hồi quy nhãn SAI của bản cũ: 25-51 là Ego-PROJECTED, không phải Manifested."""
    base = {"Heart", "G", "Throat"}
    assert get_authority(base, [(25, 51)]) == "Ego (Heart) - Projected"
    assert get_authority(base, [(51, 25)]) == "Ego (Heart) - Projected"
    assert get_authority(base, [(25, 51)]) != "Ego (Heart) - Manifested"


def test_heart_other_channels_stay_plain_ego():
    """26-44 (kéo Spleen) / 40-37 (kéo Solar) không rơi vào Ego chi tiết ở đây —
    thật ra Spleen/Solar định nghĩa thì đã thắng ở nhánh trên; với mặt bằng
    Heart+G không kèm center khác, kênh lạ không đổi nhãn."""
    base = {"Heart", "G", "Throat"}
    assert get_authority(base, [(26, 44)]) == "Ego (Heart)"
    assert get_authority(base, [(40, 37)]) == "Ego (Heart)"


# --- 3. Nhánh chết đã dọn: Heart KHÔNG BAO GIỜ thành Self-Projected --------------

def test_get_authority_has_no_type_parameter():
    """Nhánh cũ phụ thuộc ``hd_type`` (``Self-Projected nếu Projector``) — khoá
    việc không được tái thêm tham số lá số vào hàm thuần."""
    import inspect

    assert list(inspect.signature(get_authority).parameters) == ["defined_centers", "defined_channels"]


def test_heart_beats_g_even_when_g_defined():
    """Heart+G, không kênh đặc biệt → Ego (Heart), KHÔNG phải Self-Projected
    (đúng lỗi cũ với Projector — dot 6 đã dọn)."""
    assert get_authority({"Heart", "G"}, []) == "Ego (Heart)"
    assert get_authority({"Heart", "G", "Root"}, []) == "Ego (Heart)"


# --- 4. E2E: calculate_hd_chart → get_authority nhất quán (có ephemeris) --------

def test_e2e_wiring_and_label_set():
    samples = [
        datetime(1990, 5, 15, 8, 30),
        datetime(1975, 11, 2, 14, 17),
        datetime(2000, 1, 1, 0, 0),
        datetime(1963, 12, 10, 5, 35),   # ví dụ từ đối chứng dot 6 (Projector)
        datetime(1949, 7, 1, 15, 39),    # ví dụ từ đối chứng dot 6 (Manifestor)
        datetime(1988, 7, 7, 7, 7),
        datetime(2011, 7, 26, 23, 58),
        datetime(1943, 9, 10, 9, 23),
    ]
    for dt in samples:
        chart = calculate_hd_chart(dt)
        assert chart["authority"] in ALL_LABELS, (dt, chart["authority"])
        assert chart["authority"] == get_authority(
            chart["defined_centers"], chart["defined_channels"]
        ), dt
