"""P4: lịch sử văn phong, sao chép, áp giọng cho báo cáo cũ, đóng dấu bản."""

from test_api_v1 import CLIENT, H, app, login  # noqa: F401
from test_style import PROFILE, _activate, _fake_llm, _tpl_with_samples
from test_style_p3 import _manual_profile

MANUAL_V2 = {"tone": "Giọng bản hai, trang trọng.", "rhythm": "Câu dài.",
             "vocabulary": "Hàn lâm.", "structure": "Mở bằng định nghĩa.",
             "do": ["Dùng thuật ngữ"], "dont": ["Tiếng lóng"], "excerpt": PROFILE["excerpt"]}


def test_history_records_versions_and_restore(app, monkeypatch):
    _fake_llm(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H)
    r = c.patch(f"/api/v1/templates/{tid}", json={"style_profile": MANUAL_V2}, headers=H)
    assert r.status_code == 200, r.text
    hist = c.get(f"/api/v1/templates/{tid}/style-history", headers=H).json()
    assert [h["version_no"] for h in hist] == [2, 1]
    assert [h["source"] for h in hist] == ["manual", "analyze"]
    assert all(h["created_by_name"] for h in hist)
    assert hist[1]["tone"].startswith("Giọng ấm áp")
    r = c.post(f"/api/v1/templates/{tid}/style-restore/1", headers=H)
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["style_profile"]["tone"].startswith("Giọng ấm áp") and got["style_status"] == "ready"
    hist = c.get(f"/api/v1/templates/{tid}/style-history", headers=H).json()
    assert [h["version_no"] for h in hist] == [3, 2, 1] and hist[0]["source"] == "restore"


def test_restore_marks_stale_when_samples_changed(app, monkeypatch):
    _fake_llm(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H)
    c.post(f"/api/v1/templates/{tid}/samples", json={"title": "Mới", "body": "Thêm bài " * 30}, headers=H)
    got = c.post(f"/api/v1/templates/{tid}/style-restore/1", headers=H).json()
    assert got["style_status"] == "stale" and got["style_profile"]["sample_count"] == 2


def test_restore_missing_version_404(app):
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    assert c.get(f"/api/v1/templates/{tid}/style-history", headers=H).json() == []
    assert c.post(f"/api/v1/templates/{tid}/style-restore/9", headers=H).status_code == 404


def test_copy_voice(app, monkeypatch):
    _fake_llm(monkeypatch)
    c = login(app)
    src = _tpl_with_samples(c, 2, name="Mau goc")
    c.post(f"/api/v1/templates/{src}/analyze-style", headers=H)
    dst = _tpl_with_samples(c, 0, name="Mau moi")
    other = _tpl_with_samples(c, 0, name="Mau trang")
    assert c.post(f"/api/v1/templates/{dst}/style-copy",
                  json={"from_template_id": other}, headers=H).status_code == 422
    r = c.post(f"/api/v1/templates/{dst}/style-copy", json={"from_template_id": src}, headers=H)
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["style_status"] == "ready" and got["style_profile"]["tone"].startswith("Giọng ấm áp")
    hist = c.get(f"/api/v1/templates/{dst}/style-history", headers=H).json()
    assert len(hist) == 1 and hist[0]["source"] == "copy"
    assert c.post(f"/api/v1/templates/{dst}/style-copy",
                  json={"from_template_id": dst}, headers=H).status_code == 422


def test_apply_style_rewrites_old_report(app, monkeypatch):
    import backend.api.services as svc
    from backend.reporting.llm_client import LLMConfig, LLMUsage
    seen = {}

    def fake(brief, config, transport=None, system=None):
        if "Phân tích văn phong" in brief:
            return dict(PROFILE), LLMUsage(prompt_tokens=1, completion_tokens=1, model="fake")
        seen["brief"] = brief
        return {"summary": "BẢN VIẾT LẠI THEO GIỌNG MẪU."}, LLMUsage(
            prompt_tokens=1, completion_tokens=1, model="fake")

    monkeypatch.setattr(svc, "call_llm_with_usage", fake)
    import backend.reporting.service as _rsvc
    monkeypatch.setattr(_rsvc, "call_llm_with_usage", fake)
    import backend.api.routers.reports as _rr
    monkeypatch.setattr(_rr, "org_llm_configs", lambda *a: [LLMConfig(api_key="k")])
    monkeypatch.setattr(svc, "org_llm_configs", lambda *a: [LLMConfig(api_key="k")])
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    key = c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H).json()["key"]
    _activate(c, tid)
    cid = c.post("/api/v1/clients", json=CLIENT, headers=H).json()["id"]
    rid = c.post("/api/v1/reports", json={
        "client_id": cid, "tier": "deep_core", "template": key,
        "content_mode": "template", "domains": [], "use_style": False}, headers=H).json()["id"]
    before = c.get(f"/api/v1/reports/{rid}").json()
    assert before["style_used"] is False and before["content_mode"] == "template"
    r = c.post(f"/api/v1/reports/{rid}/apply-style", headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "generating"
    detail = c.get(f"/api/v1/reports/{rid}").json()
    assert detail["status"] == "ready" and detail["style_used"] is True
    assert detail["style_version"] == 1 and detail["content_mode"] == "llm"
    assert detail["version"] == before["version"] + 1
    assert "BẢN VIẾT LẠI THEO GIỌNG MẪU" in detail["markdown"]
    assert "## 8" in seen["brief"]
    c.patch(f"/api/v1/reports/{rid}/style-rating", json={"rating": 1}, headers=H)
    c.post(f"/api/v1/reports/{rid}/apply-style", json={"template_key": key}, headers=H)
    assert c.get(f"/api/v1/reports/{rid}").json()["style_rating"] is None


def test_apply_style_gates(app, monkeypatch):
    _fake_llm(monkeypatch)
    c = login(app)
    bare = _tpl_with_samples(c, 2, name="Mau chua co giong")
    _activate(c, bare)
    key = c.get(f"/api/v1/templates/{bare}", headers=H).json()["key"]
    cid = c.post("/api/v1/clients", json=CLIENT, headers=H).json()["id"]
    rid = c.post("/api/v1/reports", json={
        "client_id": cid, "tier": "deep_core", "template": key,
        "content_mode": "template", "domains": []}, headers=H).json()["id"]
    assert c.post(f"/api/v1/reports/{rid}/apply-style", headers=H).status_code == 422
    assert c.post(f"/api/v1/reports/{rid}/apply-style",
                  json={"template_key": "khong-ton-tai"}, headers=H).status_code == 422
    c.post(f"/api/v1/reports/{rid}/archive", headers=H)
    assert c.post(f"/api/v1/reports/{rid}/apply-style", headers=H).status_code == 409


def test_stats_by_version(app, monkeypatch):
    from test_style_p3 import _fake_text
    _fake_text(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    _manual_profile(c, tid)
    key = c.get(f"/api/v1/templates/{tid}", headers=H).json()["key"]
    _activate(c, tid)
    cid = c.post("/api/v1/clients", json=CLIENT, headers=H).json()["id"]

    def _report():
        return c.post("/api/v1/reports", json={
            "client_id": cid, "tier": "deep_core", "template": key,
            "content_mode": "template", "domains": [], "use_style": True}, headers=H).json()["id"]

    r1 = _report()
    assert c.get(f"/api/v1/reports/{r1}").json()["style_version"] == 1
    c.patch(f"/api/v1/templates/{tid}", json={"style_profile": MANUAL_V2}, headers=H)
    r2 = _report()
    assert c.get(f"/api/v1/reports/{r2}").json()["style_version"] == 2
    c.patch(f"/api/v1/reports/{r1}/style-rating", json={"rating": 1}, headers=H)
    c.patch(f"/api/v1/reports/{r2}/style-rating", json={"rating": -1}, headers=H)
    stats = c.get(f"/api/v1/templates/{tid}/style-stats", headers=H).json()
    assert stats["up"] == 1 and stats["down"] == 1
    assert stats["by_version"] == [{"version": 1, "up": 1, "down": 0},
                                   {"version": 2, "up": 0, "down": 1}]
