"""BodyGraph v5 (template routing): định tuyến xác định, độc lập màu sắc."""

from __future__ import annotations

import math
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import hd_bodygraph as B  # noqa: E402


def _synth_chart(defined=((10, 20), (20, 34), (1, 8)), red_gates=frozenset()):
    """Chart giả: đủ field cho generate_bodygraph_svg, không cần ephemeris."""
    gates = {}
    for g1, g2 in defined:
        gates[g1] = gates[g2] = True
    pg, dg = {}, {}
    for i, pl in enumerate(B.PLANETS):
        g = sorted(gates)[i % max(len(gates), 1)] if gates else 10
        if g in red_gates:
            dg[pl] = {"gate": g, "line": 1}
        else:
            pg[pl] = {"gate": g, "line": 1}
    centers = {B.GATES[g]["c"] for g in gates}
    return {
        "defined_centers": sorted(centers), "defined_channels": [tuple(sorted(c)) for c in defined],
        "personality_gates": pg, "design_gates": dg,
        "type": "Generator", "authority": "Sacral", "definition": "Single",
        "profile": "1/3", "incarnation_cross": "Test Cross", "strategy": "Wait",
    }


def _channel_paths(svg):
    """Mọi path `d` trong 2 group kênh (hình học thuần, chưa tính màu)."""
    out = []
    for gid in ("channels-open", "channels-defined"):
        m = re.search(rf'<g id="{gid}">(.*?)</g>\s*<g id=', svg, re.S)
        if not m:
            m = re.search(rf'<g id="{gid}">(.*)', svg, re.S)
        for d in re.findall(r'<path d="([^"]+)"', m.group(1)[: len(m.group(1))]):
            out.append(d)
    return out


# --- hình học xác định ---------------------------------------------------------

def test_routes_cover_all_channels_and_hit_anchors():
    assert len(B.CHANNELS_36) == 36
    for g1, g2 in B.CHANNELS_36:
        pts = B._route(g1, g2)
        assert len(pts) >= 2
        assert pts[0] == pytest.approx(B.GATES[g1]["a"])
        assert pts[-1] == pytest.approx(B.GATES[g2]["a"])


def test_routes_deterministic_and_reverse_symmetric():
    for g1, g2 in B.CHANNELS_36:
        assert B._route(g1, g2) == B._route(g1, g2)
        if not B._via(g1, g2):
            continue  # route thẳng: tiếp tuyến 2 đầu khác nhau theo pháp tuyến cổng
        fwd = B._route(g1, g2)
        rev = B._route(g2, g1)
        assert len(fwd) == len(rev)
        for p, q in zip(fwd, reversed(rev)):
            assert p == pytest.approx(q)


def test_no_route_crosses_foreign_center():
    def inside(x, y, cfg):
        if "circle" in cfg:
            cx, cy, rr = cfg["circle"]
            return math.hypot(x - cx, y - cy) < rr - 6
        poly, ok = cfg["poly"], False
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):
                ok = not ok
        return ok

    for g1, g2 in B.CHANNELS_36:
        own = {B.GATES[g1]["c"], B.GATES[g2]["c"]}
        pts = B._route(g1, g2)
        total = B._cum(pts)[-1]
        acc = 0.0
        for a, b in zip(pts, pts[1:]):
            acc += B._seg_len(a, b)
            if acc < 30 or acc > total - 30:
                continue
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            for cname, cfg in B.CENTERS.items():
                if cname not in own:
                    assert not inside(mx, my, cfg), f"{(g1, g2)} xuyên {cname}"


def test_crossing_budget():
    def xseg(p1, p2, p3, p4):
        def o(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        d1, d2, d3, d4 = o(p3, p4, p1), o(p3, p4, p2), o(p1, p2, p3), o(p1, p2, p4)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    routes = {ch: B._route(*ch) for ch in B.CHANNELS_36}
    n = 0
    chs = list(routes)
    for i in range(len(chs)):
        for j in range(i + 1, len(chs)):
            if set(chs[i]) & set(chs[j]):
                continue
            A, Bp = routes[chs[i]][::3], routes[chs[j]][::3]
            if any(xseg(a1, a2, b1, b2)
                   for a1, a2 in zip(A, A[1:]) for b1, b2 in zip(Bp, Bp[1:])):
                n += 1
    assert n <= 12, f"quá nhiều điểm cắt: {n}"


def test_stubs_stay_short():
    for g1, g2 in B.CHANNELS_36:
        pts = B._route(g1, g2)
        total = B._cum(pts)[-1]
        want = min(B.STUB_LEN, total * 0.38)
        assert B._cum(B._head(pts, want))[-1] == pytest.approx(want, abs=0.5)
        assert B._cum(B._tail(pts, want))[-1] == pytest.approx(want, abs=0.5)
        assert want <= B.STUB_LEN + 0.01


# --- màu sắc độc lập hình học ---------------------------------------------------

def test_activation_does_not_change_geometry():
    ch = ((10, 20), (20, 34), (34, 57), (1, 8), (19, 49))
    all_black = _synth_chart(ch, red_gates=frozenset())
    some_red = _synth_chart(ch, red_gates=frozenset({20, 34, 1, 49}))
    a = _channel_paths(B.generate_bodygraph_svg(all_black, name="A"))
    b = _channel_paths(B.generate_bodygraph_svg(some_red, name="B"))
    assert len(a) == len(b) > 36
    assert a == b


def test_svg_mentions_all_channels():
    svg = B.generate_bodygraph_svg(_synth_chart(), name="T", open_mode="gray")
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    for g1, g2 in B.CHANNELS_36:
        assert f"Kênh {g1}–{g2}" in svg or f"Kênh {g2}–{g1}" in svg or f"Cổng {g1}" in svg


def test_open_modes_only_draw_hanging():
    # 1 kênh định nghĩa (10-20) -> 4 kênh treo chạm 10/20, còn lại tắt hẳn.
    for mode, white in (("white", True), ("gray_hanging", False), ("none", False)):
        svg = B.generate_bodygraph_svg(_synth_chart(((10, 20),)), name="T", open_mode=mode)
        if mode == "none":
            assert "<title>Kênh" not in svg
        else:
            assert svg.count("(cổng treo)") == 4
            assert "(mở)" not in svg
        assert ('stroke="#FFFFFF"' in svg) == white
