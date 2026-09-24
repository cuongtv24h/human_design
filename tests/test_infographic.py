"""Infographic HTML report: self-contained, concise, key points only."""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.reporting import export_report  # noqa: E402
from backend.reporting.contract import ReportRequest  # noqa: E402
from backend.reporting.infographic import render_infographic_html, short  # noqa: E402
from backend.reporting.language_vn import CENTER_VN, vn_authority, vn_strategy  # noqa: E402
from backend.reporting.orchestrator import ReportOrchestrator  # noqa: E402

SUBJECT = {
    "name": "Nguyễn Văn A",
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "timezone": "+07:00",
    "birth_location": "Hòa Bình, Việt Nam",
}


def _document(tier: str = "deep_core", **subject):
    return ReportOrchestrator().run(
        ReportRequest.model_validate({"subject": {**SUBJECT, **subject}, "tier": tier})
    )


def _visible_text(html: str) -> str:
    html = re.sub(r"<svg.*?</svg>", " ", html, flags=re.S)
    html = re.sub(r"<(style|title)>.*?</\1>", " ", html, flags=re.S)
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def test_short_keeps_first_sentence_and_answers_questions():
    assert short("Một câu. Hai câu.") == "Một câu."
    assert short("Hỏi gì? Trả lời 'thế này.' Phần thừa.", 80) == "Hỏi gì? Trả lời 'thế này.'"
    long_text = "từ " * 100
    assert short(long_text, 40).endswith("…") and len(short(long_text, 40)) <= 40


def test_infographic_is_self_contained_and_carries_key_points():
    document = _document()
    html = render_infographic_html(document)
    chart = document.chart

    assert html.startswith("<!DOCTYPE html>") and '<html lang="vi">' in html
    assert "<script" not in html
    assert not re.search(r'(?:src|href)=["\']https?://', html), "no external assets"
    assert "<svg" in html  # inline BodyGraph

    text = _visible_text(html)
    assert "Nguyễn Văn A" in text and "1990-05-15" in text and "Hòa Bình" in text
    assert chart["type"] in text
    assert vn_strategy(chart["strategy"], chart["type"]) in text
    assert vn_authority(chart["authority"]) in text
    assert chart["profile"] in text
    for center in CENTER_VN.values():
        assert center in text
    assert f"{len(chart['defined_centers'])}/9" in text
    # Bilingual, polished — never raw calculator strings.
    assert " - " not in vn_strategy(chart["strategy"], chart["type"])
    assert chart["strategy"] not in text


def test_infographic_is_concise():
    text = _visible_text(render_infographic_html(_document()))
    assert len(text.split()) < 1000, "infographic must stay light on words"
    blocks = re.findall(r">([^<>]{1,})<", re.sub(r"<svg.*?</svg>", "", render_infographic_html(_document()), flags=re.S))
    assert max(len(b.strip()) for b in blocks if "{" not in b) <= 260


def test_tier_controls_deep_blocks_and_bodygraph_toggle():
    deep = _visible_text(render_infographic_html(_document("deep_core")))
    basic = _visible_text(render_infographic_html(_document("free_basic")))
    assert "Kênh (Channels)" in deep and "Incarnation Cross" in deep
    assert "Kênh (Channels)" not in basic and "Incarnation Cross" not in basic
    assert "<svg" not in render_infographic_html(_document("free_basic"), include_bodygraph=False)


def test_user_input_is_escaped():
    html = render_infographic_html(_document(name="<script>alert(1)</script>"))
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_many_charts_render_without_gaps():
    """Smoke across dates/times so every Type/Authority/Profile path is hit."""
    seen_types = set()
    for year in range(1960, 2020, 3):
        for hour in ("03:15", "14:40"):
            document = _document("deep_core", birth_date=f"{year}-0{1 + year % 9}-1{year % 9}", birth_time=hour)
            seen_types.add(document.chart["type"])
            html = render_infographic_html(document, include_bodygraph=False)
            values = re.findall(r'<div class="(?:tile-value|tile-note|sig-word|sig-note|c-hint|badge-vn)">([^<]*)</div>', html)
            assert values and all(v.strip() for v in values), (year, hour, values)
            assert "None" not in _visible_text(html)
    assert len(seen_types) >= 4


def test_export_writes_infographic_file(tmp_path):
    paths = export_report(_document("free_basic"), tmp_path, include_infographic=True)
    assert paths["infographic_html"].name.endswith("_infographic.html")
    assert "<!DOCTYPE html>" in paths["infographic_html"].read_text(encoding="utf-8")
    assert "infographic_html" not in export_report(_document("free_basic"), tmp_path / "x")


def test_gateways_serve_infographic(tmp_path, monkeypatch):
    import server
    from fastapi.testclient import TestClient

    import openapi_server

    monkeypatch.setattr(server, "REPORT_OUTPUT_DIR", str(tmp_path))
    result = server.generate_hd_infographic(birth_date="1990-05-15", birth_time="08:30", name="Nguyễn Văn A")
    assert "error" not in result, result
    assert pathlib.Path(result["file"]).exists() and "html" not in result

    client = TestClient(openapi_server.app)
    got = client.get("/reports/infographic.html", params={"birth_date": "1990-05-15", "birth_time": "08:30", "tier": "deep_core"})
    assert got.status_code == 200 and got.headers["content-type"].startswith("text/html")
    assert "Incarnation Cross" in got.text
    posted = client.post("/reports/infographic.html", json={"subject": SUBJECT})
    assert posted.status_code == 200 and "Nguyễn Văn A" in posted.text
    bad = client.get("/reports/infographic.html", params={"birth_date": "15/05/1990", "birth_time": "08:30"})
    assert bad.status_code == 422
