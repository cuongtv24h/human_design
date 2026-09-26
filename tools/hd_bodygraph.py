#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Human Design BodyGraph SVG Generator — v3.0 PREMIUM
====================================================
Style tham khảo bản in premium (HumanDesignApp):
  • Nền giấy ấm + sắc tố pastel, shadow mềm cho từng Center
  • Head/Ajna/Heart/Spleen/Solar = tam giác, G = thoi, Throat/Root = vuông bo góc,
    Sacral = HÌNH TRÒN (khác biệt lớn so với bản cũ)
  • Kênh ĐỊNH NGHĨA vẽ dày như "dải băng": Đen = Personality, Đỏ = Design,
    Cả hai = nửa đen nửa đỏ, Đen+Đỏ cùng lúc = vân sọc chéo
  • Số cổng kích hoạt nằm trong BADGE TRÒN (viền màu), cổng tĩnh in mờ chìm trong Center
  • Cột 2 lá số (Personality ☉ Đen / Design ☉ Đỏ) dạng card 2 panel có biểu tượng hành tinh
  • Header tên + Type + Authority + Definition + Profile + Cross, mũi tên aura cho Manifestor

API giữ nguyên:
    from hd_bodygraph import generate_bodygraph_svg
    svg = generate_bodygraph_svg(chart, name="...", birth_local_str="...")

CLI:
    python3 hd_bodygraph.py --date 1984-11-01 --time 19:15 --tz +07:00 \
        --name "Dương Thị Thu Huyền" --place "Vĩnh Phúc" --out bg.svg --png bg.png
"""

import sys
import os
import math
import argparse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart

# ---------------------------------------------------------------------------
# Bố cục trang
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = 1200, 1660
CHART_DX, CHART_DY = 60, 190          # dời sơ đồ để chừa header + card 2 bên

INK = "#232227"
RED = "#C62828"
PAPER = "#FBF8F1"
FONT = "DejaVu Sans, Verdana, Geneva, sans-serif"

# ---------------------------------------------------------------------------
# 9 TRUNG TÂM — hình học + màu (màu theo bản premium)
# ---------------------------------------------------------------------------
CENTERS = {
    "Head":   {"poly": [(500, 52), (412, 162), (588, 162)], "r": 10,
               "color": "#EFC230", "tcol": "#4A3800",
               "name": "HEAD", "nl": (500, 112), "fs": 13, "badge": 12},
    "Ajna":   {"poly": [(412, 198), (588, 198), (500, 308)], "r": 10,
               "color": "#5FA05A", "tcol": "#FFFFFF",
               "name": "AJNA", "nl": (500, 255), "fs": 13, "badge": 12},
    "Throat": {"poly": [(412, 352), (588, 352), (588, 522), (412, 522)], "r": 22,
               "color": "#8A6A4F", "tcol": "#FFFFFF",
               "name": "THROAT", "nl": (500, 438), "fs": 14, "badge": 12},
    "G":      {"poly": [(500, 572), (608, 690), (500, 808), (392, 690)], "r": 24,
               "color": "#DFCE3E", "tcol": "#3D3200",
               "name": "G", "nl": (500, 700), "fs": 15, "badge": 12},
    "Heart":  {"poly": [(652, 572), (652, 688), (748, 630)], "r": 10,
               "color": "#C4674A", "tcol": "#FFFFFF",
               "name": "HEART", "nl": (700, 555), "fs": 12, "outside": "middle", "badge": 10.5},
    "Spleen": {"poly": [(315, 588), (315, 792), (180, 690)], "r": 12,
               "color": "#C39A63", "tcol": "#3B2A12",
               "name": "SPLEEN", "nl": (268, 662), "fs": 10.5, "badge": 10.5},
    "Sacral": {"circle": (500, 958, 96),
               "color": "#C8503C", "tcol": "#FFFFFF",
               "name": "SACRAL", "nl": (500, 986), "fs": 13, "badge": 12},
    "Solar Plexus": {"poly": [(662, 868), (662, 1052), (772, 960)], "r": 10,
                     "color": "#B98B4E", "tcol": "#FFFFFF",
                     "name": "SOLAR PLEXUS", "nl": (750, 1085), "fs": 12, "outside": "middle", "badge": 10.5},
    "Root":   {"poly": [(412, 1128), (588, 1128), (588, 1302), (412, 1302)], "r": 22,
               "color": "#4A3B33", "tcol": "#FFFFFF",
               "name": "ROOT", "nl": (500, 1216), "fs": 14, "badge": 12},
}

# ---------------------------------------------------------------------------
# 64 CỔNG: center, anchor (điểm kênh cắm vào), label (vị trí in số - nằm trong Center)
# ---------------------------------------------------------------------------
GATES = {
    # ---------------- Head ----------------
    64: {"c": "Head", "a": (446, 162), "l": (446, 146)},
    61: {"c": "Head", "a": (500, 162), "l": (500, 146)},
    63: {"c": "Head", "a": (554, 162), "l": (554, 146)},
    # ---------------- Ajna ----------------
    47: {"c": "Ajna", "a": (450, 198), "l": (452, 222)},
    24: {"c": "Ajna", "a": (500, 198), "l": (500, 222)},
    4:  {"c": "Ajna", "a": (550, 198), "l": (548, 222)},
    17: {"c": "Ajna", "a": (452, 250), "l": (476, 268)},
    11: {"c": "Ajna", "a": (548, 250), "l": (524, 268)},
    43: {"c": "Ajna", "a": (500, 308), "l": (500, 288)},
    # ---------------- Throat ----------------
    62: {"c": "Throat", "a": (448, 352), "l": (446, 376)},
    23: {"c": "Throat", "a": (500, 352), "l": (500, 376)},
    56: {"c": "Throat", "a": (552, 352), "l": (554, 376)},
    16: {"c": "Throat", "a": (412, 406), "l": (444, 404)},
    20: {"c": "Throat", "a": (412, 472), "l": (444, 466)},
    45: {"c": "Throat", "a": (588, 400), "l": (556, 404)},
    35: {"c": "Throat", "a": (588, 448), "l": (556, 448)},
    12: {"c": "Throat", "a": (588, 494), "l": (556, 474)},
    31: {"c": "Throat", "a": (446, 522), "l": (446, 500)},
    8:  {"c": "Throat", "a": (500, 522), "l": (500, 500)},
    33: {"c": "Throat", "a": (554, 522), "l": (554, 500)},
    # ---------------- G ----------------
    1:  {"c": "G", "a": (474, 600), "l": (476, 634)},
    13: {"c": "G", "a": (526, 600), "l": (524, 634)},
    7:  {"c": "G", "a": (408, 706), "l": (430, 700)},
    25: {"c": "G", "a": (599, 700), "l": (568, 712)},
    10: {"c": "G", "a": (438, 740), "l": (452, 750)},
    46: {"c": "G", "a": (544, 758), "l": (536, 742)},
    15: {"c": "G", "a": (486, 793), "l": (478, 780)},
    2:  {"c": "G", "a": (500, 808), "l": (500, 791)},
    # ---------------- Heart ----------------
    21: {"c": "Heart", "a": (656, 580), "l": (674, 598)},
    51: {"c": "Heart", "a": (652, 632), "l": (666, 636)},
    26: {"c": "Heart", "a": (658, 680), "l": (684, 652)},
    40: {"c": "Heart", "a": (712, 660), "l": (714, 644)},
    # ---------------- Spleen ----------------
    48: {"c": "Spleen", "a": (315, 592), "l": (296, 616)},
    57: {"c": "Spleen", "a": (315, 640), "l": (292, 644)},
    44: {"c": "Spleen", "a": (315, 690), "l": (292, 686)},
    50: {"c": "Spleen", "a": (315, 740), "l": (290, 720)},
    32: {"c": "Spleen", "a": (275, 778), "l": (280, 754)},
    28: {"c": "Spleen", "a": (237, 752), "l": (258, 728)},
    18: {"c": "Spleen", "a": (200, 714), "l": (238, 700)},
    # ---------------- Sacral (vòng tròn) ----------------
    14: {"c": "Sacral", "a": (500, 864), "l": (500, 898)},
    5:  {"c": "Sacral", "a": (462, 872), "l": (468, 914)},
    29: {"c": "Sacral", "a": (538, 872), "l": (532, 914)},
    34: {"c": "Sacral", "a": (424, 900), "l": (444, 942)},
    27: {"c": "Sacral", "a": (420, 1002), "l": (440, 996)},
    59: {"c": "Sacral", "a": (596, 958), "l": (556, 954)},
    42: {"c": "Sacral", "a": (446, 1032), "l": (470, 1016)},
    9:  {"c": "Sacral", "a": (554, 1032), "l": (530, 1016)},
    3:  {"c": "Sacral", "a": (500, 1054), "l": (500, 1026)},
    # ---------------- Solar Plexus ----------------
    36: {"c": "Solar Plexus", "a": (666, 872), "l": (688, 898)},
    22: {"c": "Solar Plexus", "a": (686, 888), "l": (708, 916)},
    37: {"c": "Solar Plexus", "a": (706, 906), "l": (720, 942)},
    6:  {"c": "Solar Plexus", "a": (662, 936), "l": (686, 952)},
    49: {"c": "Solar Plexus", "a": (662, 978), "l": (682, 982)},
    55: {"c": "Solar Plexus", "a": (662, 1018), "l": (678, 1012)},
    30: {"c": "Solar Plexus", "a": (672, 1046), "l": (676, 1034)},
    # ---------------- Root ----------------
    53: {"c": "Root", "a": (448, 1128), "l": (448, 1152)},
    60: {"c": "Root", "a": (500, 1128), "l": (500, 1152)},
    52: {"c": "Root", "a": (552, 1128), "l": (552, 1146)},
    54: {"c": "Root", "a": (412, 1180), "l": (440, 1180)},
    38: {"c": "Root", "a": (412, 1232), "l": (440, 1232)},
    58: {"c": "Root", "a": (412, 1282), "l": (440, 1282)},
    19: {"c": "Root", "a": (588, 1172), "l": (560, 1182)},
    39: {"c": "Root", "a": (588, 1220), "l": (560, 1220)},
    41: {"c": "Root", "a": (588, 1268), "l": (560, 1268)},
}

# ---------------------------------------------------------------------------
# 36 KÊNH (theo cặp cổng chuẩn) + waypoint uốn tránh Center
# ---------------------------------------------------------------------------
CHANNELS_36 = [
    (64, 47), (61, 24), (63, 4),
    (17, 62), (43, 23), (11, 56),
    (35, 36), (12, 22), (16, 48),
    (20, 10), (20, 34), (20, 57),
    (31, 7), (8, 1), (33, 13), (21, 45),
    (2, 14), (15, 5), (25, 51), (46, 29),
    (26, 44), (40, 37),
    (18, 58), (28, 38), (32, 54), (50, 27),
    (34, 10), (34, 57), (10, 57),
    (3, 60), (9, 52), (42, 53), (59, 6),
    (30, 41), (49, 19), (39, 55),
]

CHANNEL_NAMES = {
    (64, 47): "Abstraction", (61, 24): "Awareness", (63, 4): "Logic",
    (17, 62): "Acceptance", (43, 23): "Structuring", (11, 56): "Curiosity",
    (35, 36): "Transitoriness", (12, 22): "Openness", (16, 48): "Wavelength",
    (20, 10): "Awakening", (20, 34): "Charisma", (20, 57): "Brainwave",
    (31, 7): "Alpha", (8, 1): "Inspiration", (33, 13): "Prodigal",
    (21, 45): "Money Line", (2, 14): "Keeper of the Keys", (15, 5): "Rhythm",
    (25, 51): "Initiation", (46, 29): "Discovery", (26, 44): "Surrender",
    (40, 37): "Community", (18, 58): "Judgement", (28, 38): "Struggle",
    (32, 54): "Transformation", (50, 27): "Preservation", (34, 10): "Conviction",
    (34, 57): "Power", (10, 57): "Perfected Form", (3, 60): "Mutation",
    (9, 52): "Concentration", (42, 53): "Maturation", (59, 6): "Mating",
    (30, 41): "Recognition", (49, 19): "Synthesis", (39, 55): "Emoting",
}

PLANETS = ["Sun", "Earth", "Moon", "North Node", "South Node", "Mercury",
           "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

GLYPH = {"Sun": "☉", "Earth": "⊕", "Moon": "☽", "North Node": "☊", "South Node": "☋",
         "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
         "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"}
PLANET_VN = {"Sun": "Mặt Trời", "Earth": "Trái Đất", "Moon": "Mặt Trăng",
             "North Node": "Bắc Giao", "South Node": "Nam Giao", "Mercury": "Thủy tinh",
             "Venus": "Kim tinh", "Mars": "Hỏa tinh", "Jupiter": "Mộc tinh",
             "Saturn": "Thổ tinh", "Uranus": "Thiên Vương", "Neptune": "Hải Vương",
             "Pluto": "Diêm Vương"}

PROFILE_SHORT = {
    "1/3": "Investigator / Martyr", "1/4": "Investigator / Opportunist",
    "2/4": "Hermit / Opportunist", "2/5": "Hermit / Heretic",
    "3/5": "Martyr / Heretic", "3/6": "Martyr / Role Model",
    "4/6": "Opportunist / Role Model", "4/1": "Opportunist / Investigator",
    "5/1": "Heretic / Investigator", "5/2": "Heretic / Hermit",
    "6/2": "Role Model / Hermit", "6/3": "Role Model / Martyr",
}

# ---------------------------------------------------------------------------
# Tiện ích
# ---------------------------------------------------------------------------


def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(c1, c2, t):
    a, b = _hex2rgb(c1), _hex2rgb(c2)
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _lighten(c, t):
    return _mix(c, "#FFFFFF", t)


def _darken(c, t):
    return _mix(c, "#000000", t)


def _seg_len(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def _cum(pts):
    d = [0.0]
    for i in range(len(pts) - 1):
        d.append(d[-1] + _seg_len(pts[i], pts[i + 1]))
    return d


def _at(pts, cum, frac):
    total = cum[-1]
    t = max(0.0, min(1.0, frac)) * total
    for i in range(len(pts) - 1):
        if cum[i + 1] >= t:
            L = cum[i + 1] - cum[i]
            k = 0.0 if L == 0 else (t - cum[i]) / L
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k,
                    pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)
    return pts[-1]


def _pl(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def _path_of(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def _stroke(d, color, w, opacity=1.0, extra=""):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.1f}" '
            f'stroke-linecap="round" stroke-linejoin="round" stroke-opacity="{opacity:.2f}" {extra}/>')


# ---------------------------------------------------------------------------
# Vẽ
# ---------------------------------------------------------------------------


def _gate_badge(x, y, g, act, r=12.0):
    """Badge tròn cho số cổng kích hoạt."""
    if act == "B":
        return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFDF6" stroke="#C9C2B2" stroke-width="1"/>'
                f'<path d="M {x - r} {y} A {r} {r} 0 0 1 {x + r} {y}" fill="none" stroke="{INK}" stroke-width="2.6"/>'
                f'<path d="M {x + r} {y} A {r} {r} 0 0 1 {x - r} {y}" fill="none" stroke="{RED}" stroke-width="2.6"/>'
                f'<text x="{x:.1f}" y="{y + r * 0.45:.1f}" text-anchor="middle" font-size="{r * 1.16:.1f}" '
                f'font-weight="bold" fill="#4A2A22">{g}</text>')
    col = INK if act == "P" else RED
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFDF6" stroke="{col}" stroke-width="2.4"/>'
            f'<text x="{x:.1f}" y="{y + r * 0.45:.1f}" text-anchor="middle" font-size="{r * 1.16:.1f}" '
            f'font-weight="bold" fill="{col}">{g}</text>')


def _esc(t):
    """Escape ký tự XML cho text content."""
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _wrap_text(text, max_chars):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _wrap_items(items, max_chars):
    """Gói danh sách thành dòng 'A · B · C', không treo dấu · đầu/cuối dòng."""
    lines, cur = [], ""
    for item in items:
        piece = item if not cur else cur + " · " + item
        if len(piece) <= max_chars:
            cur = piece
        else:
            if cur:
                lines.append(cur)
            cur = item
    if cur:
        lines.append(cur)
    return lines


def _panel_open(x, y, w, h, title, subtitle="", title_fs=12.5, title_ls=2.2):
    s = (f'<rect x="{x + 5}" y="{y + 7}" width="{w}" height="{h}" rx="18" fill="#000" opacity="0.07" filter="url(#soft)"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#FFFDF7" stroke="#DED7C6" stroke-width="1.5"/>'
         f'<text x="{x + 22}" y="{y + 36}" font-size="{title_fs}" font-weight="bold" letter-spacing="{title_ls}" fill="#2B2A26">{_esc(title)}</text>')
    if subtitle:
        s += f'<text x="{x + 22}" y="{y + 55}" font-size="11" fill="#9A9384">{subtitle}</text>'
    s += f'<line x1="{x + 18}" y1="{y + 66}" x2="{x + w - 18}" y2="{y + 66}" stroke="#E7DFCE" stroke-width="1"/>'
    return s


def _section_head(x, y, text, color="#8A8578"):
    return (f'<text x="{x}" y="{y}" font-size="10.5" font-weight="bold" letter-spacing="2" '
            f'fill="{color}">{_esc(text)}</text>')


NOT_SELF_SIGNATURE = {
    "Manifestor": ("Tức giận (Anger)", "Bình an (Peace)"),
    "Generator": ("Thất vọng (Frustration)", "Thỏa mãn (Satisfaction)"),
    "Manifesting Generator": ("Thất vọng + Tức giận", "Thỏa mãn + Bình an"),
    "Projector": ("Cay đắng (Bitterness)", "Thành công (Success)"),
    "Reflector": ("Thất vọng (Disappointment)", "Ngạc nhiên (Surprise)"),
}


# ---------------------------------------------------------------------------
# ENGINE ĐỊNH TUYẾN v5 — TEMPLATE CỐ ĐỊNH cho từng kênh
#   • Mỗi kênh có hành lang (via points) thiết kế sẵn, tuân thủ làn:
#       - cặp dọc trung tâm: đi thẳng / cong nhẹ, tách làn song song
#       - cụm trái (Spleen): làn trong x≈340-400, làn ngoài x≈240-330
#       - cụm phải (Heart/Solar): làn trong x≈605-660
#       - 26-44: luồn khe G–Sacral rồi lên Spleen (như bản cổ điển)
#   • Cùng 1 dữ liệu chart → cùng 1 hình học (không random, không phụ thuộc
#     trạng thái kích hoạt). Màu sắc chỉ là lớp style phủ lên route này.
#   • Stub cổng treo: đoạn ngắn cố định (STUB_LEN px) từ đầu route, không bao
#     giờ chạy xa khỏi Center.
# ---------------------------------------------------------------------------
STUB_LEN = 64.0               # độ dài nhánh cổng treo (px, chart space)

# Via points theo đúng thứ tự (g1, g2) trong CHANNELS_36; chiều ngược tự đảo.
# Kênh vắng mặt = đi thẳng bằng 1 đường Bezier (đã kiểm tra không xuyên Center).
ROUTE_VIA = {
    (35, 36): [(606, 545), (620, 645), (628, 735), (640, 810)],
    (12, 22): [(624, 516), (642, 610), (650, 710), (658, 800), (670, 862)],
    (20, 10): [(415, 545), (390, 650), (394, 712)],
    (20, 34): [(385, 545), (352, 640), (345, 760), (362, 838), (388, 862)],
    (31, 7):  [(418, 605), (404, 662)],
    (21, 45): [(648, 530), (626, 470)],
    (15, 5):  [(476, 834)],
    (46, 29): [(543, 832)],
    (26, 44): [(648, 742), (618, 798), (560, 838), (500, 850), (470, 850),
               (430, 830), (388, 795), (350, 748)],
    (18, 58): [(240, 900), (290, 1080), (340, 1210)],
    (28, 38): [(290, 920), (330, 1060), (365, 1170)],
    (32, 54): [(330, 900), (360, 1030), (385, 1120)],
    (50, 27): [(350, 860), (380, 940)],
    (34, 57): [(412, 832), (398, 762), (374, 702), (340, 664)],
    (10, 57): [(372, 712), (338, 676)],
    (30, 41): [(668, 1140), (662, 1230), (625, 1260)],
    (39, 55): [(640, 1120), (650, 1060)],
}
for _k in list(ROUTE_VIA):
    ROUTE_VIA[(_k[1], _k[0])] = list(reversed(ROUTE_VIA[_k]))


def _via(g1, g2):
    return ROUTE_VIA.get((g1, g2), [])


def _centroid(cfg):
    if "circle" in cfg:
        return cfg["circle"][:2]
    xs = [p[0] for p in cfg["poly"]]
    ys = [p[1] for p in cfg["poly"]]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


CENTER_CENTROID = {k: _centroid(v) for k, v in CENTERS.items()}


def _unit(a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(vx, vy) or 1.0
    return (vx / L, vy / L)


def _normal(g):
    ax, ay = GATES[g]["a"]
    cx, cy = CENTER_CENTROID[GATES[g]["c"]]
    return _unit((cx, cy), (ax, ay))


def _leave(g_from, g_to):
    """Hướng kênh rời cổng (route thẳng)."""
    n = _normal(g_from)
    u = _unit(GATES[g_from]["a"], GATES[g_to]["a"])
    vx, vy = 0.38 * n[0] + 0.62 * u[0], 0.38 * n[1] + 0.62 * u[1]
    L = math.hypot(vx, vy) or 1.0
    return (vx / L, vy / L)


def _bez(P0, C1, C2, P3, n=54):
    out = []
    for i in range(n + 1):
        t = i / n
        m = 1 - t
        x = m ** 3 * P0[0] + 3 * m * m * t * C1[0] + 3 * m * t * t * C2[0] + t ** 3 * P3[0]
        y = m ** 3 * P0[1] + 3 * m * m * t * C1[1] + 3 * m * t * t * C2[1] + t ** 3 * P3[1]
        out.append((x, y))
    return out


def _hermite(pts, t0, tn, n_per=30):
    """Spline C1 qua các điểm; tiếp tuyến 2 đầu chỉ định."""
    m = len(pts)
    T = [None] * m
    T[0], T[-1] = t0, tn
    for i in range(1, m - 1):
        T[i] = ((pts[i + 1][0] - pts[i - 1][0]) * 0.5, (pts[i + 1][1] - pts[i - 1][1]) * 0.5)
    out = []
    for i in range(m - 1):
        P0, P1 = pts[i], pts[i + 1]
        C1 = (P0[0] + T[i][0] / 3, P0[1] + T[i][1] / 3)
        C2 = (P1[0] - T[i + 1][0] / 3, P1[1] - T[i + 1][1] / 3)
        seg = _bez(P0, C1, C2, P1, n_per)
        out += seg[1:] if out else seg
    return out


def _route(g1, g2):
    """Polyline mượt cho kênh g1→g2 — hoàn toàn xác định từ ROUTE_VIA.

    Cùng cặp cổng luôn cho cùng 1 hình học, bất kể trạng thái kích hoạt.
    """
    A, B = GATES[g1]["a"], GATES[g2]["a"]
    via = _via(g1, g2)
    if via:
        pts = [A] + list(via) + [B]
        n0, nn = _normal(g1), _normal(g2)
        k0 = min(46.0, _seg_len(pts[0], pts[1]) * 0.7)
        kn = min(46.0, _seg_len(pts[-1], pts[-2]) * 0.7)
        return _hermite(pts, (n0[0] * k0, n0[1] * k0),
                         (-nn[0] * kn, -nn[1] * kn), n_per=14)
    d0, d1 = _leave(g1, g2), _leave(g2, g1)
    dist = math.hypot(B[0] - A[0], B[1] - A[1])
    k = min(0.30 * dist, 90)
    return _bez(A, (A[0] + d0[0] * k, A[1] + d0[1] * k),
                (B[0] - d1[0] * k, B[1] - d1[1] * k), B, 40)


def _head(pts, px):
    """Đoạn đầu route dài `px` (nhánh cổng treo) — không bao giờ chạy xa."""
    if px <= 0:
        return [pts[0], pts[0]]
    out, acc = [pts[0]], 0.0
    for a, b in zip(pts, pts[1:]):
        L = _seg_len(a, b)
        if acc + L >= px:
            k = (px - acc) / L if L else 0.0
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            return out
        acc += L
        out.append(b)
    return out


def _tail(pts, px):
    """Đoạn cuối route dài `px` (nhánh cổng treo phía bên kia)."""
    return list(reversed(_head(list(reversed(pts)), px)))


def _cut(pts, f0, f1):
    cum = _cum(pts)
    out = [_at(pts, cum, f0)]
    for i in range(1, len(pts) - 1):
        f = cum[i] / cum[-1]
        if f0 < f < f1:
            out.append(pts[i])
    out.append(_at(pts, cum, f1))
    clean = [out[0]]
    for p in out[1:]:
        if _seg_len(p, clean[-1]) > 0.05:
            clean.append(p)
    return clean


def _ribbon(pts, kind, w, act=None, stub=False):
    """Dải kênh phẳng: viền mảnh + thân màu."""
    d = _path_of(pts)
    o = []
    if kind == "open":
        # Kênh mở chỉ là nét mảnh chìm để dải màu (định nghĩa/cổng treo) nổi rõ.
        o.append(_stroke(d, "#D3CEC0", w, 1.0))
        return o
    if kind == "white":
        # Dải trắng kênh treo (kiểu app mẫu): nổi rõ nhưng trung tính.
        o.append(_stroke(d, "#000000", w + 3.0, 0.08))
        o.append(_stroke(d, "#DCD6C4", w + 1.2, 1.0))
        o.append(_stroke(d, "#FFFFFF", w, 1.0))
        return o
    base = INK if kind == "P" else RED
    if stub:
        o.append(_stroke(d, _darken(base, 0.40), w + 1.6, 1.0))
        o.append(_stroke(d, "url(#hatch)" if act == "B" else base, w, 1.0))
        return o
    o.append(_stroke(d, "#000000", w + 3.4, 0.10))
    o.append(_stroke(d, _darken(base, 0.42), w + 1.7, 1.0))
    o.append(_stroke(d, "url(#hatch)" if act == "B" else base, w, 1.0))
    return o


def _defs():
    return f'''<defs>
  <linearGradient id="page" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0" stop-color="#FCFAF4"/><stop offset="0.45" stop-color="#F7F3E9"/>
    <stop offset="1" stop-color="#EFEADC"/>
  </linearGradient>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/>
    <stop offset="0.62" stop-color="#FFFFFF" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
  </radialGradient>
  <pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="9" height="9" fill="{RED}"/>
    <line x1="0" y1="0" x2="0" y2="9" stroke="{INK}" stroke-width="4.6"/>
  </pattern>
  <pattern id="hatchsoft" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="14" height="14" fill="#DCD8CC"/>
    <line x1="0" y1="0" x2="0" y2="14" stroke="#F4F1E8" stroke-width="7"/>
  </pattern>
  <filter id="soft" x="-20%" y="-20%" width="150%" height="150%">
    <feGaussianBlur stdDeviation="6"/>
  </filter>
  <radialGradient id="blobA" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#BBD7D8" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#BBD7D8" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="blobB" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#E9D9AE" stop-opacity="0.5"/>
    <stop offset="1" stop-color="#E9D9AE" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="blobC" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#D9C7E0" stop-opacity="0.4"/>
    <stop offset="1" stop-color="#D9C7E0" stop-opacity="0"/>
  </radialGradient>
</defs>'''


def _shape_path(cfg):
    """Trả về path 'd' của center (bo góc cho đa giác)."""
    if "circle" in cfg:
        return None
    pts, r = cfg["poly"], cfg.get("r", 0)
    if r <= 0:
        return "M " + " L ".join("%.1f %.1f" % p for p in pts) + " Z"
    n = len(pts)
    segs = []
    for i in range(n):
        p_prev, p, p_next = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        L1 = _seg_len(p_prev, p) or 1
        L2 = _seg_len(p, p_next) or 1
        r1, r2 = min(r, L1 * 0.42), min(r, L2 * 0.42)
        a = (p[0] + (p_prev[0] - p[0]) / L1 * r1, p[1] + (p_prev[1] - p[1]) / L1 * r1)
        b = (p[0] + (p_next[0] - p[0]) / L2 * r2, p[1] + (p_next[1] - p[1]) / L2 * r2)
        segs.append((a, p, b))
    d = "M %.1f %.1f" % segs[0][0]
    for i, (a, p, b) in enumerate(segs):
        d += " Q %.1f %.1f %.1f %.1f" % (p[0], p[1], b[0], b[1])
        nxt = segs[(i + 1) % len(segs)][0]
        d += " L %.1f %.1f" % nxt
    return d + " Z"


def generate_bodygraph_svg(chart, name="", birth_local_str="", utc_str="",
                           place_str="", mode="full", open_mode="white"):
    defined_centers = set(chart["defined_centers"])
    defined_ch = {(min(a, b), max(a, b)) for a, b in chart["defined_channels"]}
    p_gates = {d["gate"] for d in chart["personality_gates"].values()}
    d_gates = {d["gate"] for d in chart["design_gates"].values()}

    def act_of(g):
        p, d = g in p_gates, g in d_gates
        if p and d:
            return "B"
        return "P" if p else ("D" if d else None)

    order = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]
    on = [c for c in order if c in defined_centers]

    chart = dict(chart)
    for _k in ("type", "authority", "definition", "profile", "incarnation_cross", "strategy"):
        if chart.get(_k):
            chart[_k] = _esc(chart[_k])
    name, birth_local_str, place_str, utc_str = map(_esc, (name, birth_local_str, place_str, utc_str))

    S = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PAGE_W} {PAGE_H}" '
         f'width="{PAGE_W}" height="{PAGE_H}" font-family="{FONT}">']
    S.append(_defs())
    S.append(f'<rect width="{PAGE_W}" height="{PAGE_H}" fill="url(#page)"/>')
    S.append(f'<ellipse cx="250" cy="330" rx="420" ry="380" fill="url(#blobA)" opacity="0.30"/>')
    S.append(f'<ellipse cx="1010" cy="1290" rx="440" ry="420" fill="url(#blobB)" opacity="0.34"/>')
    S.append(f'<ellipse cx="215" cy="1430" rx="380" ry="330" fill="url(#blobC)" opacity="0.26"/>')

    # ======================= HEADER =======================
    C_LABEL = "#8A8578"
    C_TITLE = "#2B2A26"
    S.append(f'<text x="60" y="96" font-size="46" font-weight="bold" fill="{C_TITLE}" '
             f'letter-spacing="0.5">{name or "Human Design Chart"}</text>')
    y = 132
    if birth_local_str:
        S.append(f'<text x="60" y="{y}" font-size="16" fill="#6E6A60">{birth_local_str}'
                 + (f'  •  {place_str}' if place_str else '')
                 + (f'  •  GMT {utc_str}' if utc_str else '') + '</text>')
    S.append(f'<line x1="60" y1="{y + 16}" x2="470" y2="{y + 16}" stroke="#DAD4C4" stroke-width="1.5"/>')

    stats = [("TYPE", chart["type"], 25, "#2B2A26", True),
             ("AUTHORITY", chart["authority"], 18, "#4A4740", False),
             ("DEFINITION", chart["definition"], 18, "#4A4740", False),
             ("PROFILE", f'{chart["profile"]}   {PROFILE_SHORT.get(chart["profile"], "")}',
              18, "#4A4740", False),
             ("INCARNATION CROSS", chart["incarnation_cross"], 17, "#6E6A60", False)]
    yy = y + 52
    for lab, val, fs, col, bold in stats:
        S.append(f'<text x="60" y="{yy - 13}" font-size="10.5" letter-spacing="2" fill="{C_LABEL}">{lab}</text>')
        S.append(f'<text x="60" y="{yy + 8}" font-size="{fs}" fill="{col}"'
                 + (' font-weight="bold"' if bold else '') + f'>{val}</text>')
        yy += 46
    yy += 2
    S.append(f'<text x="60" y="{yy}" font-size="10.5" letter-spacing="2" fill="{C_LABEL}">STRATEGY</text>')
    yy += 21
    for line in _wrap_text(chart.get("strategy", ""), 44):
        S.append(f'<text x="60" y="{yy}" font-size="12.5" fill="#7B766B">{line}</text>')
        yy += 19

    # ================= Card 2 lá số =================
    S.append('<g id="planets-card">')
    card_x, card_y, card_w, card_h = 878, 46, 316, 512
    S.append(f'<rect x="{card_x + 6}" y="{card_y + 8}" width="{card_w}" height="{card_h}" rx="18" '
             f'fill="#000" opacity="0.10" filter="url(#soft)"/>')
    S.append(f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="18" '
             f'fill="#FFFDF7" stroke="#DED7C6" stroke-width="1.6"/>')
    panel_w = (card_w - 42) / 2
    for idx, (key, title, sub, color) in enumerate(
            [("p", "PERSONALITY", "Ý thức · Đen", INK), ("d", "DESIGN", "Vô thức · Đỏ", RED)]):
        px = card_x + 14 + idx * (panel_w + 14)
        S.append(f'<rect x="{px}" y="{card_y + 14}" width="{panel_w}" height="{card_h - 28}" rx="12" '
                 f'fill="#FBF8EF" stroke="#EAE3D2" stroke-width="1.2"/>')
        S.append(f'<text x="{px + panel_w / 2}" y="{card_y + 44}" text-anchor="middle" font-size="14" '
                 f'font-weight="bold" letter-spacing="2.4" fill="{color}">{title}</text>')
        S.append(f'<text x="{px + panel_w / 2}" y="{card_y + 63}" text-anchor="middle" font-size="11.5" '
                 f'fill="#9A9384">{sub}</text>')
        S.append(f'<line x1="{px + 14}" y1="{card_y + 76}" x2="{px + panel_w - 14}" y2="{card_y + 76}" '
                 f'stroke="#E7DFCE" stroke-width="1"/>')
        gdict = chart["personality_gates"] if key == "p" else chart["design_gates"]
        ry = card_y + 104
        for pl in PLANETS:
            d = gdict.get(pl)
            gl = f'{d["gate"]}.{d["line"]}' if d else "–"
            S.append(f'<text x="{px + 16}" y="{ry}" font-size="16" fill="{color}" opacity="0.9">{GLYPH[pl]}</text>')
            if d:
                S.append(f'<text x="{px + 42}" y="{ry}" font-size="16.5" font-weight="bold" fill="{color}">{gl}</text>')
            else:
                S.append(f'<text x="{px + 42}" y="{ry}" font-size="15" fill="#C3BCAE">{gl}</text>')
            S.append(f'<text x="{px + panel_w - 12}" y="{ry}" text-anchor="end" font-size="9.5" '
                     f'fill="#B3AB9B">{PLANET_VN[pl]}</text>')
            ry += 31.5
    S.append('</g>')

    # ================= Panel trái A: cổng kích hoạt =================
    keys = [g for g in range(1, 65) if act_of(g)]
    pa_x, pa_y, pa_w = 24, 560, 190
    cols = 4
    rows = (len(keys) + cols - 1) // cols
    pa_h = 118 + rows * 40
    S.append('<g id="panel-gates">')
    S.append(_panel_open(pa_x, pa_y, pa_w, pa_h, "CỔNG KÍCH HOẠT", f"{len(keys)} cổng có năng lượng", title_ls=2.0))
    for i, g in enumerate(keys):
        cx = pa_x + 36 + (i % cols) * 42
        cy = pa_y + 104 + (i // cols) * 40
        S.append(_gate_badge(cx, cy, g, act_of(g), 12.5))
    S.append('</g>')

    # ================= Panel trái B: điểm mạnh & điểm mù =================
    pb_x, pb_y, pb_w, pb_h = 24, pa_y + pa_h + 26, 190, 330
    S.append('<g id="panel-strength">')
    S.append(_panel_open(pb_x, pb_y, pb_w, pb_h, "TÀI NĂNG & ĐIỂM MÙ", "● tài năng · ○ bài học",
                         title_fs=11, title_ls=1))
    ry = pb_y + 96
    S.append(_section_head(pb_x + 20, ry, "ĐỊNH NGHĨA"))
    ry += 20
    for line in _wrap_items(on, 20):
        S.append(f'<text x="{pb_x + 22}" y="{ry}" font-size="12" fill="#3A3833">{line}</text>')
        ry += 19
    ry += 16
    S.append(_section_head(pb_x + 20, ry, "MỞ · BÀI HỌC"))
    ry += 20
    off_c = [c for c in order if c not in defined_centers]
    off_lines = _wrap_items(off_c, 20) if off_c else ["Tất cả đã định nghĩa"]
    for line in off_lines:
        S.append(f'<text x="{pb_x + 22}" y="{ry}" font-size="12" fill="#3A3833">{line}</text>')
        ry += 19
    S.append('</g>')

    # ================= Panel 2: Bản đồ định nghĩa =================
    px2, py2, pw2, ph2 = 878, 576, 316, 486
    S.append('<g id="panel-definition">')
    S.append(_panel_open(px2, py2, pw2, ph2, "BẢN ĐỒ ĐỊNH NGHĨA",
                         f'{len(defined_ch)}/36 kênh  ·  {len(defined_centers)}/9 trung tâm định nghĩa'))
    ry = py2 + 96
    S.append(_section_head(px2 + 22, ry, f"KÊNH ĐỊNH NGHĨA ({len(defined_ch)}/36)"))
    ry += 22
    for g1, g2 in CHANNELS_36:
        key = (min(g1, g2), max(g1, g2))
        if key not in defined_ch:
            continue
        a1, a2 = act_of(g1), act_of(g2)
        cname = CHANNEL_NAMES.get((g1, g2)) or CHANNEL_NAMES.get((g2, g1), "")
        act = "B" if (a1 == "B" or a2 == "B" or {a1, a2} == {"P", "D"}) else (a1 or a2)
        if act == "B":
            dot = (f'<circle cx="{px2 + 28}" cy="{ry - 4}" r="6.5" fill="#FFFDF6" stroke="#C9C2B2"/>'
                   f'<path d="M {px2 + 21.5} {ry - 4} A 6.5 6.5 0 0 1 {px2 + 34.5} {ry - 4}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
                   f'<path d="M {px2 + 34.5} {ry - 4} A 6.5 6.5 0 0 1 {px2 + 21.5} {ry - 4}" fill="none" stroke="{RED}" stroke-width="2.2"/>')
        else:
            col = INK if act == "P" else RED
            dot = f'<circle cx="{px2 + 28}" cy="{ry - 4}" r="6.5" fill="{col}"/>'
        S.append(dot)
        S.append(f'<text x="{px2 + 44}" y="{ry}" font-size="12.5" font-weight="bold" fill="#3A3833">'
                 f'{min(g1, g2)}–{max(g1, g2)}</text>')
        S.append(f'<text x="{px2 + 104}" y="{ry}" font-size="12" fill="#6E6A60">{cname}</text>')
        ry += 25
    ry += 14
    S.append(_section_head(px2 + 22, ry, f"TRUNG TÂM ĐỊNH NGHĨA ({len(defined_centers)}/9)"))
    ry += 22
    for i in range(0, len(on), 2):
        S.append(f'<text x="{px2 + 26}" y="{ry}" font-size="12" fill="#4A4740">'
                 + "   ·   ".join(on[i:i + 2]) + '</text>')
        ry += 21
    ry += 14
    hang = [g for g in sorted(set(p_gates) | set(d_gates))
            if not any((g in (c1, c2) and (c2 if g == c1 else c1) in (set(p_gates) | set(d_gates)))
                       for c1, c2 in CHANNELS_36)]
    S.append(_section_head(px2 + 22, ry, f"CỔNG TREO ({len(hang)})"))
    ry += 22
    ht = "   ".join(str(g) for g in hang) if hang else "Không có — mọi cổng đều nằm trong kênh định nghĩa"
    for line in _wrap_text(ht, 26):
        S.append(f'<text x="{px2 + 26}" y="{ry}" font-size="12" fill="#4A4740">{line}</text>')
        ry += 20
    S.append('</g>')

    # ================= Panel 3: Sống đúng thiết kế =================
    px3, py3, pw3, ph3 = 878, 1080, 316, 400
    S.append('<g id="panel-living">')
    S.append(_panel_open(px3, py3, pw3, ph3, "SỐNG ĐÚNG THIẾT KẾ",
                         f'{chart["type"]}  ·  {chart["profile"]}'))
    ns, sg = NOT_SELF_SIGNATURE.get(chart["type"], ("—", "—"))
    rows3 = [("CHIẾN LƯỢC", chart.get("strategy", "")),
             ("THẨM QUYỀN", chart["authority"]),
             ("NOT-SELF", ns), ("CHỮ KÝ", sg),
             ("CHỮ THẬP", chart.get("incarnation_cross", ""))]
    ry = py3 + 96
    for lab, val in rows3:
        S.append(_section_head(px3 + 22, ry, lab))
        ry += 20
        for line in _wrap_text(val, 32):
            S.append(f'<text x="{px3 + 26}" y="{ry}" font-size="12.5" fill="#3A3833">{line}</text>')
            ry += 19
        ry += 11
    S.append('</g>')


    # ================= SƠ ĐỒ =================
    S.append(f'<g transform="translate({CHART_DX},{CHART_DY})">')
    S.append('<ellipse cx="500" cy="700" rx="430" ry="560" fill="url(#halo)" opacity="0.75"/>')

    W = 12.0                      # bề rộng kênh định nghĩa
    W_OPEN = 2.6                  # bề rộng kênh mở (nét mảnh chìm)
    W_WHITE = 11.0                # bề rộng dải trắng kênh treo (kiểu app mẫu)
    W_STUB = 10.0                 # bề rộng nhánh cổng treo
    ROUTES = {ch: _route(*ch) for ch in CHANNELS_36}
    BADGE_R = {k: v.get("badge", 12) for k, v in CENTERS.items()}

    # ---------- Lớp 1: kênh mở (dải trắng đan nhau) ----------
    # open_mode: "gray" = nét xám mọi kênh mở; "gray_hanging" = nét xám chỉ
    # kênh treo; "white" = dải trắng chỉ kênh treo (kiểu app mẫu); "none" = bỏ.
    S.append('<g id="channels-open">')
    if open_mode != "none":
        for g1, g2 in CHANNELS_36:
            key = (min(g1, g2), max(g1, g2))
            if key in defined_ch:
                continue
            hanging = act_of(g1) or act_of(g2)
            if open_mode in ("white", "gray_hanging") and not hanging:
                continue
            cname = CHANNEL_NAMES.get((g1, g2)) or CHANNEL_NAMES.get((g2, g1), "")
            tag = "(cổng treo)" if hanging else "(mở)"
            S.append(f'<g><title>Kênh {g1}–{g2} • {cname} {tag}</title>')
            if open_mode == "white":
                lines = _ribbon(ROUTES[(g1, g2)], "white", W_WHITE)
            else:
                lines = _ribbon(ROUTES[(g1, g2)], "open",
                                W_OPEN if mode == "full" else W_OPEN * 0.8)
            for line in lines:
                S.append(line)
            S.append('</g>')
    S.append('</g>')

    # ---------- Lớp 2: kênh định nghĩa + cổng treo ----------
    S.append('<g id="channels-defined">')
    for g1, g2 in CHANNELS_36:
        pts = ROUTES[(g1, g2)]
        key = (min(g1, g2), max(g1, g2))
        a1, a2 = act_of(g1), act_of(g2)
        cname = CHANNEL_NAMES.get((g1, g2)) or CHANNEL_NAMES.get((g2, g1), "")
        segs = []
        if key in defined_ch:
            # 2 nửa cùng 1 hình học, chỉ khác màu theo nguồn kích hoạt.
            segs = [(_cut(pts, 0.0, 0.5), a1 or "P", g1, False),
                    (_cut(pts, 0.5, 1.0), a2 or "P", g2, False)]
        else:
            total = _cum(pts)[-1]
            stub = min(STUB_LEN, total * 0.38)
            if a1:
                segs.append((_head(pts, stub), a1, g1, True))
            if a2:
                segs.append((_tail(pts, stub), a2, g2, True))
        for sub, act, gate, is_stub in segs:
            if len(sub) < 2:
                continue
            lbl = "Personality" if act == "P" else ("Design" if act == "D" else "Personality + Design")
            S.append(f'<g><title>Cổng {gate} · {cname} · {lbl}</title>')
            for line in _ribbon(sub, act if act != "B" else "P",
                                W_STUB if is_stub else W, act, stub=is_stub):
                S.append(line)
            S.append('</g>')
    S.append('</g>')

    # ---------- Lớp 3: 9 Center ----------
    S.append('<g id="centers">')
    for cname, cfg in CENTERS.items():
        defined = cname in defined_centers
        if "circle" in cfg:
            cx, cy, rr = cfg["circle"]
            d = None
            base = f'<circle cx="{cx}" cy="{cy}" r="{rr}"'
        else:
            d = _shape_path(cfg)
            base = f'<path d="{d}"'
        S.append(f'<g><title>{cname} — ' + ('ĐỊNH NGHĨA' if defined else 'MỞ') + '</title>')
        if defined:
            col = cfg["color"]
            gid = "grad" + cname.replace(" ", "")
            S.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0.25" y2="1">'
                     f'<stop offset="0" stop-color="{_lighten(col, 0.22)}"/>'
                     f'<stop offset="1" stop-color="{_darken(col, 0.08)}"/></linearGradient>')
            if d is None:
                cx, cy, rr = cfg["circle"]
                S.append(f'<circle cx="{cx + 3}" cy="{cy + 6}" r="{rr}" fill="#000" opacity="0.13" filter="url(#soft)"/>')
            else:
                S.append(f'<path d="{d}" transform="translate(3,6)" fill="#000" opacity="0.13" filter="url(#soft)"/>')
            S.append(base + f' fill="url(#{gid})" stroke="{_darken(col, 0.34)}" stroke-width="2.6"/>')
            tcol = cfg["tcol"]
        else:
            S.append(base + ' fill="#FFFFFF" stroke="#AFB5B0" stroke-width="2.3"/>')
            tcol = "#8C918C"
        anchor = cfg.get("outside")
        lcol = tcol if not anchor else ("#8F6A4A")
        halo = (' paint-order="stroke" stroke="#F8F4EA" stroke-width="4"'
                ' stroke-linejoin="round"' if anchor else "")
        S.append(f'<text x="{cfg["nl"][0]}" y="{cfg["nl"][1]}" text-anchor="{anchor or "middle"}" '
                 f'font-size="{cfg["fs"]}" font-weight="bold" letter-spacing="{1.4 if not anchor else 0.6}" '
                 f'fill="{lcol}"{halo}>{cfg["name"]}</text>')
        S.append('</g>')
    S.append('</g>')

    # ---------- Lớp 4: số cổng ----------
    S.append('<g id="gate-numbers">')
    for g in range(1, 65):
        act = act_of(g)
        lx, ly = GATES[g]["l"]
        if act:
            S.append(_gate_badge(lx, ly, g, act, BADGE_R[GATES[g]["c"]]))
        else:
            S.append(f'<text x="{lx:.1f}" y="{ly + 2:.1f}" text-anchor="middle" font-size="12.5" '
                     f'fill="#B7B2A4">{g}</text>')
    S.append('</g>')

    # ---------- Mũi tên aura ----------
    if str(chart["type"]).startswith("Manifest"):
        S.append('<g id="aura-arrows" opacity="0.75">')
        S.append('<path d="M 442 44 L 414 30 L 414 58 Z" fill="#8C8578"/>')
        S.append('<path d="M 558 44 L 586 30 L 586 58 Z" fill="#8C8578"/>')
        S.append('</g>')

    S.append('</g>')  # end chart group

    # ================= LEGEND + FOOTER =================
    ly = 1532
    S.append(f'<g id="legend" font-size="12.5" fill="#565349">')
    items = [("square_dark", "Trung tâm Định nghĩa"), ("square_open", "Trung tâm Mở"),
             ("dot_p", "Personality · Ý thức"), ("dot_d", "Design · Vô thức"),
             ("dot_b", "Cả hai (P + D)"), ("hatch", "Kênh Đen + Đỏ")]
    widths = [200, 142, 186, 158, 136, 158]
    GAP = 24
    x = (PAGE_W - (sum(widths) + GAP * 5)) / 2
    S.append(f'<line x1="70" y1="{ly - 44}" x2="{PAGE_W - 70}" y2="{ly - 48}" stroke="#DAD4C4" stroke-width="1.2"/>')
    for (kind, label), w in zip(items, widths):
        if kind == "square_dark":
            S.append(f'<rect x="{x}" y="{ly - 13}" width="17" height="17" rx="4" fill="#B98B4E" stroke="#8A6A4F"/>')
        elif kind == "square_open":
            S.append(f'<rect x="{x}" y="{ly - 13}" width="17" height="17" rx="4" fill="#FFF" stroke="#B9BFBB"/>')
        elif kind == "dot_p":
            S.append(f'<circle cx="{x + 8}" cy="{ly - 4}" r="8" fill="#FFFDF6" stroke="{INK}" stroke-width="2.4"/>')
            S.append(f'<text x="{x + 8}" y="{ly + 1}" text-anchor="middle" font-size="10" font-weight="bold" fill="{INK}">10</text>')
        elif kind == "dot_d":
            S.append(f'<circle cx="{x + 8}" cy="{ly - 4}" r="8" fill="#FFFDF6" stroke="{RED}" stroke-width="2.4"/>')
            S.append(f'<text x="{x + 8}" y="{ly + 1}" text-anchor="middle" font-size="10" font-weight="bold" fill="{RED}">10</text>')
        elif kind == "dot_b":
            S.append(f'<circle cx="{x + 8}" cy="{ly - 4}" r="8" fill="#FFFDF6" stroke="#C9C2B2"/>')
            S.append(f'<path d="M {x} {ly - 4} A 8 8 0 0 1 {x + 16} {ly - 4}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
            S.append(f'<path d="M {x + 16} {ly - 4} A 8 8 0 0 1 {x} {ly - 4}" fill="none" stroke="{RED}" stroke-width="2.4"/>')
        else:
            S.append(f'<line x1="{x}" y1="{ly - 4}" x2="{x + 22}" y2="{ly - 4}" stroke="url(#hatch)" stroke-width="11" stroke-linecap="round"/>')
        S.append(f'<text x="{x + (32 if kind == "hatch" else 26)}" y="{ly + 1}">{label}</text>')
        x += w + GAP
    S.append('</g>')
    S.append(f'<text x="{PAGE_W / 2}" y="{ly + 58}" text-anchor="middle" font-size="12.5" fill="#A29C8E">'
             f'Human Design System · Tính bằng Swiss Ephemeris · "Đừng tin, hãy thử nghiệm" — Ra Uru Hu</text>')
    S.append(f'<text x="{PAGE_W / 2}" y="{ly + 80}" text-anchor="middle" font-size="11" fill="#BDB7A9">'
             f'BodyGraph Engine v5.1.1 (template routing) · {chart.get("definition", "")} · {len(defined_ch)}/36 kênh định nghĩa · '
             f'{len(defined_centers)}/9 trung tâm định nghĩa</text>')
    S.append('</svg>')
    return "\n".join(S)



def main():
    ap = argparse.ArgumentParser(description="Vẽ BodyGraph SVG (v5.1.1)")
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--tz", default="+07:00")
    ap.add_argument("--name", default="")
    ap.add_argument("--place", default="")
    ap.add_argument("--out", required=True, help="File .svg xuất ra")
    ap.add_argument("--png", default="", help="(tuỳ chọn) xuất luôn .png")
    ap.add_argument("--mode", default="full", choices=["full", "focus"])
    args = ap.parse_args()

    from hd_time import display_birth, local_to_utc
    # Tính bằng UTC; hiển thị đúng giờ khai báo (quy ước tools/hd_time.py).
    dt_utc = local_to_utc(args.date, args.time, args.tz)

    chart = calculate_hd_chart(dt_utc)
    birth_local = f"Sinh {display_birth(args.date, args.time, args.tz)}"
    svg = generate_bodygraph_svg(chart, name=args.name or "Human Design Chart",
                                 birth_local_str=birth_local,
                                 place_str=args.place, mode=args.mode)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK - {args.out} ({len(svg) // 1024} KB)")
    if args.png:
        try:
            import cairosvg
            cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=args.png,
                             output_width=900, background_color="#FFFFFF")
            print(f"OK - {args.png}")
        except (ImportError, OSError) as exc:
            print(f"!! CairoSVG/libcairo chưa sẵn sàng, bỏ qua --png: {exc}")


if __name__ == "__main__":
    main()
