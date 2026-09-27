"""G1 game landing: public chart/events/leads + admin leads."""

from fastapi.testclient import TestClient

from test_api_v1 import H, app, login  # noqa: F401

BIRTH = {"birth_date": "1990-05-15", "birth_time": "08:30",
         "timezone": "+07:00", "birth_place": "Hòa Bình"}


def test_public_chart(app):
    c = login(app)
    r = c.post("/api/v1/public/game/chart", json=BIRTH, headers=H)
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["summary"]["type"] and got["summary"]["authority"] and got["summary"]["profile"]
    assert 0 <= got["summary"]["defined_centers"] <= 9
    assert isinstance(got["centers"], list) and got["subject_display"]
    again = c.post("/api/v1/public/game/chart", json=BIRTH, headers=H).json()
    assert again["summary"]["type"] == got["summary"]["type"]
    bad = c.post("/api/v1/public/game/chart", json={**BIRTH, "birth_date": "15-05-1990"}, headers=H)
    assert bad.status_code == 422


def test_public_events(app):
    c = login(app)
    ok = c.post("/api/v1/public/game/events",
                json={"name": "game_start", "theme": "nguoc-dong", "session_id": "abc"}, headers=H)
    assert ok.status_code == 200, ok.text
    bad = c.post("/api/v1/public/game/events", json={"name": "hack", "theme": "", "session_id": ""}, headers=H)
    assert bad.status_code == 422


def test_leads_flow(app):
    c = login(app)
    r = c.post("/api/v1/public/game/leads", json={
        "name": "An", "contact": "0901234567", **BIRTH,
        "theme": "nguoc-dong", "quiz": {"style": "guide"}}, headers=H)
    assert r.status_code == 200, r.text
    assert c.post("/api/v1/public/game/leads", json={"name": "", "contact": "x"}, headers=H).status_code == 422
    items = c.get("/api/v1/game/leads", headers=H).json()
    assert any(x["contact"] == "0901234567" and x["status"] == "new" for x in items)
    lid = [x for x in items if x["contact"] == "0901234567"][0]["id"]
    assert c.patch(f"/api/v1/game/leads/{lid}", json={"status": "contacted"}, headers=H).json()["status"] == "contacted"
    assert TestClient(app).get("/api/v1/game/leads").status_code == 401
