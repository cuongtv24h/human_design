"""P2: hồ sơ văn phong (B chính + A-lite) — trích xuất, snapshot, tiêm brief, đánh giá."""

import pytest

from test_api_v1 import CLIENT, H, PASSWORD, app, login  # noqa: F401  (tái dùng fixture app)

from backend.reporting.style import parse_style_profile, style_brief_block

PROFILE = {"tone": "Giọng ấm áp, gọi 'bạn'.", "rhythm": "Câu ngắn 8-15 từ.",
           "vocabulary": "Đời thường, ít thuật ngữ.", "structure": "Mở bằng quan sát.",
           "do": "Gọi 'bạn'\nKết bằng câu hỏi gợi mở", "dont": "Giọng sách giáo khoa",
           "excerpt": "Bạn không cần vội. Cơ hội đúng sẽ tự gõ cửa."}


def _doc():
    from backend.reporting.contract import ReportRequest
    from backend.reporting.orchestrator import ReportOrchestrator
    req = ReportRequest.model_validate({
        "subject": {"name": "T", "birth_date": "1990-05-15", "birth_time": "08:30",
                    "timezone": "+07:00", "birth_location": "Hòa Bình"},
        "tier": "deep_core", "template": "sections", "domains": []})
    return ReportOrchestrator().run(req)


def _tpl_with_samples(c, n=2, name="Mau style"):
    r = c.post("/api/v1/templates", json={"name": name, "sections": [{"type": "builtin", "ref": "summary"}]},
               headers=H)
    assert r.status_code == 201, r.text
    tid = r.json()["id"]
    for i in range(n):
        s = c.post(f"/api/v1/templates/{tid}/samples",
                   json={"title": f"Bai {i}", "body": "Noi dung mau phong cach rieng " * 20}, headers=H)
        assert s.status_code == 201, s.text
    return tid


def _activate(c, tid):
    r = c.patch(f"/api/v1/templates/{tid}", json={"status": "active"}, headers=H)
    assert r.status_code == 200, r.text


def _fake_llm(monkeypatch):
    import backend.api.services as svc
    from backend.reporting.llm_client import LLMConfig, LLMUsage

    def fake_brief(brief, config, transport=None, system=None):
        assert system is not None and "văn phong" in system
        assert "Bài mẫu 1" in brief and "Bài mẫu 2" in brief
        return dict(PROFILE), LLMUsage(prompt_tokens=10, completion_tokens=20, model="fake")

    monkeypatch.setattr(svc, "call_llm_with_usage", fake_brief)
    monkeypatch.setattr(svc, "org_llm_configs", lambda *a: [LLMConfig(api_key="k")])
    return svc


def test_parse_and_block_unit():
    with pytest.raises(ValueError):
        parse_style_profile({"tone": "", "excerpt": "Du dai nhung thieu tone " * 5}, 2)
    with pytest.raises(ValueError):
        parse_style_profile({"tone": "ok", "excerpt": "ngan"}, 2)
    full = parse_style_profile(PROFILE, 3)
    assert full["do"] == ["Gọi 'bạn'", "Kết bằng câu hỏi gợi mở"] and full["sample_count"] == 3

    assert style_brief_block(None) == ""
    assert style_brief_block({"profile": {}}) == ""
    block = style_brief_block({"template_name": "T", "profile": full})
    assert "## 8" in block and "Giọng ấm áp" in block and "KHÔNG dùng lại nội dung" in block
    assert "Bạn không cần vội" in block


def test_brief_includes_style_section():
    from backend.reporting.llm_editor import build_llm_brief
    doc = _doc()
    assert "## 8" not in build_llm_brief(doc)
    assert "## 8" not in build_llm_brief(doc, style={"profile": {}})
    brief = build_llm_brief(doc, style={"template_name": "T", "profile": parse_style_profile(PROFILE, 2)})
    assert "## 8" in brief and "Bạn không cần vội" in brief
    brief_one = build_llm_brief(doc, section_ids=[doc.sections[0].id],
                                style={"template_name": "T", "profile": parse_style_profile(PROFILE, 2)})
    assert "## 8" in brief_one


def test_analyze_requires_two_samples(app):
    c = login(app)
    tid = _tpl_with_samples(c, 0)
    r = c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H)
    assert r.status_code == 422 and "2 bài mẫu" in r.text
    c.post(f"/api/v1/templates/{tid}/samples", json={"title": "B", "body": "x" * 100}, headers=H)
    assert c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H).status_code == 422


def test_analyze_no_llm_configured(app, monkeypatch):
    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    r = c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H)
    assert r.status_code == 422 and "cấu hình AI" in r.text


def test_analyze_success_snapshot_and_stale(app, monkeypatch):
    _fake_llm(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    r = c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H)
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["style_status"] == "ready" and got["style_profile"]["tone"].startswith("Giọng ấm áp")
    assert got["style_profile"]["sample_count"] == 2

    _activate(c, tid)
    cat = c.get("/api/v1/catalog").json()
    assert any(t["value"] == got["key"] and t.get("has_style") for t in cat["templates"])
    cid = c.post("/api/v1/clients", json=CLIENT, headers=H).json()["id"]
    payload = {"client_id": cid, "tier": "deep_core", "template": got["key"],
               "content_mode": "template", "domains": []}
    assert c.post("/api/v1/reports", json=payload, headers=H).json()["id"]
    detail = c.get(f"/api/v1/reports/{c.post('/api/v1/reports', json=payload, headers=H).json()['id']}").json()
    assert detail["style_used"] is True
    off = c.post("/api/v1/reports", json={**payload, "use_style": False}, headers=H).json()
    assert c.get(f"/api/v1/reports/{off['id']}").json()["style_used"] is False

    c.post(f"/api/v1/templates/{tid}/samples", json={"title": "Moi", "body": "y" * 100}, headers=H)
    assert c.get(f"/api/v1/templates/{tid}").json()["style_status"] == "stale"


def test_manual_profile_edit(app):
    c = login(app)
    tid = _tpl_with_samples(c, 1)
    r = c.patch(f"/api/v1/templates/{tid}", json={"style_profile": {
        "tone": "Tự viết.", "excerpt": "Trích dẫn thủ công đủ dài cho qua kiểm tra."}}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["style_status"] == "ready"
    assert r.json()["style_profile"]["tone"] == "Tự viết."
    r = c.patch(f"/api/v1/templates/{tid}", json={"style_profile": {}}, headers=H)
    assert r.json()["style_status"] == "none"


def test_duplicate_copies_style(app, monkeypatch):
    _fake_llm(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H)
    dup = c.post(f"/api/v1/templates/{tid}/duplicate", headers=H).json()
    assert dup["style_status"] == "ready" and dup["style_profile"]["tone"].startswith("Giọng ấm áp")


def test_style_rating(app, monkeypatch):
    _fake_llm(monkeypatch)
    c = login(app)
    tid = _tpl_with_samples(c, 2)
    key = c.post(f"/api/v1/templates/{tid}/analyze-style", headers=H).json()["key"]
    _activate(c, tid)
    cid = c.post("/api/v1/clients", json=CLIENT, headers=H).json()["id"]
    payload = {"client_id": cid, "tier": "deep_core", "template": key,
               "content_mode": "template", "domains": []}
    rid = c.post("/api/v1/reports", json=payload, headers=H).json()["id"]
    r = c.patch(f"/api/v1/reports/{rid}/style-rating", json={"rating": 1}, headers=H)
    assert r.status_code == 200 and r.json()["style_rating"] == 1
    r = c.patch(f"/api/v1/reports/{rid}/style-rating", json={"rating": 0}, headers=H)
    assert r.json()["style_rating"] is None
    assert c.patch(f"/api/v1/reports/{rid}/style-rating", json={"rating": 5}, headers=H).status_code == 422
    plain = c.post("/api/v1/reports", json={**payload, "template": "sections"}, headers=H).json()["id"]
    r = c.patch(f"/api/v1/reports/{plain}/style-rating", json={"rating": 1}, headers=H)
    assert r.status_code == 422


def test_llm_generation_receives_style(app, monkeypatch):
    import backend.api.services as svc
    from backend.reporting.llm_client import LLMConfig, LLMUsage

    seen = {}

    def fake(brief, config, transport=None, system=None):
        if "Phân tích văn phong" in brief:
            return dict(PROFILE), LLMUsage(prompt_tokens=1, completion_tokens=1, model="fake")
        seen["brief"] = brief
        return {"summary": "BẢN VIẾT THEO VĂN PHONG MẪU."}, LLMUsage(
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
        "content_mode": "llm", "domains": []}, headers=H).json()["id"]
    detail = c.get(f"/api/v1/reports/{rid}").json()
    assert detail["status"] == "ready" and detail["style_used"] is True
    assert "## 8" in seen["brief"] and "Bạn không cần vội" in seen["brief"]
    assert "BẢN VIẾT THEO VĂN PHONG MẪU" in detail["markdown"]
