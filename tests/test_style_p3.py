"""P3: viết thử văn phong, so sánh A/B, thống kê rating."""

import pytest

from test_api_v1 import CLIENT, H, app, login  # noqa: F401
from test_style import PROFILE, _activate, _tpl_with_samples

from backend.reporting.style import (DEFAULT_PREVIEW_TOPIC, build_style_preview_brief,
                                     parse_style_preview)


def _manual_profile(c, tid):
    r = c.patch(f"/api/v1/templates/{tid}", json={"style_profile": {
        "tone": PROFILE["tone"], "rhythm": PROFILE["rhythm"],
        "vocabulary": PROFILE["vocabulary"], "structure": PROFILE["structure"],
        "do": ["Gọi 'bạn'"], "dont": ["Giọng sách giáo khoa"],
        "excerpt": PROFILE["excerpt"]}}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["style_status"] == "ready"


def _fake_text(monkeypatch):
    import backend.api.services as svc
    from backend.reporting.llm_client import LLMConfig, LLMUsage
    seen = {}

    def fake(brief, config, transport=None, system=None):
        seen["brief"] = brief
        seen["system"] = system
        kind = "STYLED" if "TUÂN THỦ" in brief else "DEFAULT"
        return {"preview": f"[{kind}] Đoạn viết thử " + "rất hay " * 10}, LLMUsage(
            prompt_tokens=5, completion_tokens=30, model="fake")

    monkeypatch.setattr(svc, "call_llm_with_usage", fake)
    monkeypatch.setattr(svc, "org_llm_configs", lambda *a: [LLMConfig(api_key="k")])
    return seen


def test_preview_brief_and_parse_unit():
    with pytest.raises(ValueError):
        parse_style_preview({"preview": "ngắn"})
    assert parse_style_preview({"preview": "Đủ dài cho đoạn văn thử nghiệm. " * 3}).startswith("Đủ dài")
    prof = {"tone": "Giọng ấm", "rhythm": "", "vocabulary": "", "structure": "",
            "do": ["Gọi bạn"], "dont": []}
    styled = build_style_preview_brief("Chủ đề X", prof, styled=True)
    assert "TUÂN THỦ" in styled and "Giọng ấm" in styled and "Chủ đề X" in styled
    default = build_style_preview_brief("Chủ đề X", prof, styled=False)
    assert "TRUNG LẬP" in default and "Giọng ấm" not in default


def test_preview_requires_profile(app):
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    assert c.post(f"/api/v1/templates/{tid}/style-preview", headers=H).status_code == 422
    assert c.post(f"/api/v1/templates/{tid}/style-compare", headers=H).status_code == 422


def test_preview_no_llm_configured(app, monkeypatch):
    import backend.api.services as svc
    monkeypatch.setattr(svc, "org_llm_configs", lambda *a: [])
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    _manual_profile(c, tid)
    r = c.post(f"/api/v1/templates/{tid}/style-preview", headers=H)
    assert r.status_code == 422 and "cấu hình AI" in r.text


def test_preview_success_and_stale(app, monkeypatch):
    seen = _fake_text(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    _manual_profile(c, tid)
    r = c.post(f"/api/v1/templates/{tid}/style-preview", headers=H)
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["preview"].startswith("[STYLED]") and got["topic"] == DEFAULT_PREVIEW_TOPIC
    assert got["style_status"] == "ready" and got["provider"]
    assert "Giọng ấm áp" in seen["brief"] and "JSON" in seen["system"]
    r = c.post(f"/api/v1/templates/{tid}/style-preview", json={"topic": "Kênh 10-57"}, headers=H)
    assert r.json()["topic"] == "Kênh 10-57"
    c.post(f"/api/v1/templates/{tid}/samples", json={"title": "Mới", "body": "Thêm bài " * 30}, headers=H)
    assert c.post(f"/api/v1/templates/{tid}/style-preview", headers=H).json()["style_status"] == "stale"


def test_compare_success(app, monkeypatch):
    _fake_text(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    _manual_profile(c, tid)
    r = c.post(f"/api/v1/templates/{tid}/style-compare", headers=H)
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["default_text"].startswith("[DEFAULT]") and got["styled_text"].startswith("[STYLED]")
    assert got["default_text"] != got["styled_text"] and got["topic"] == DEFAULT_PREVIEW_TOPIC


def test_preview_llm_fails(app, monkeypatch):
    import backend.api.services as svc
    from backend.reporting.llm_client import LLMConfig, LLMError
    monkeypatch.setattr(svc, "org_llm_configs", lambda *a: [LLMConfig(api_key="k")])

    def boom(brief, config, transport=None, system=None):
        raise LLMError("down")

    monkeypatch.setattr(svc, "call_llm_with_usage", boom)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    _manual_profile(c, tid)
    assert c.post(f"/api/v1/templates/{tid}/style-preview", headers=H).status_code == 503


def test_style_stats(app, monkeypatch):
    _fake_text(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    _manual_profile(c, tid)
    key = c.get(f"/api/v1/templates/{tid}", headers=H).json()["key"]
    _activate(c, tid)
    cid = c.post("/api/v1/clients", json=CLIENT, headers=H).json()["id"]

    def _report(use_style=True):
        return c.post("/api/v1/reports", json={
            "client_id": cid, "tier": "deep_core", "template": key,
            "content_mode": "template", "domains": [], "use_style": use_style}, headers=H).json()["id"]

    r1, r2 = _report(), _report()
    c.patch(f"/api/v1/reports/{r1}/style-rating", json={"rating": 1}, headers=H)
    c.patch(f"/api/v1/reports/{r2}/style-rating", json={"rating": -1}, headers=H)
    r3 = _report(use_style=False)
    assert c.patch(f"/api/v1/reports/{r3}/style-rating", json={"rating": 1}, headers=H).status_code == 422
    stats = c.get(f"/api/v1/templates/{tid}/style-stats", headers=H).json()
    assert stats["up"] == 1 and stats["down"] == 1 and len(stats["reports"]) == 2
    assert {rep["report_id"] for rep in stats["reports"]} == {r1, r2}
    assert all(rep["client_name"] and rep["rating"] in (1, -1) for rep in stats["reports"])
    empty = _tpl_with_samples(c, 2, name="Mau trang")
    got = c.get(f"/api/v1/templates/{empty}/style-stats", headers=H).json()
    assert got["up"] == 0 and got["down"] == 0 and got["reports"] == []
