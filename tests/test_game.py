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

def test_funnel_counts(app):
    c = login(app)
    for name in ("game_start", "game_complete", "compare_view"):
        r = c.post("/api/v1/public/game/events",
                   json={"name": name, "theme": "nguoc-dong", "session_id": "s1"}, headers=H)
        assert r.status_code == 200, r.text
    rows = c.get("/api/v1/game/leads/funnel", headers=H).json()
    got = {(x["theme"], x["name"]): x["count"] for x in rows}
    assert got.get(("nguoc-dong", "game_start")) == 1
    assert got.get(("nguoc-dong", "compare_view")) == 1
    from fastapi.testclient import TestClient
    assert TestClient(app).get("/api/v1/game/leads/funnel").status_code == 401

def test_scores_flow(app):
    c = login(app)
    post = lambda **kw: c.post("/api/v1/public/game/scores", json=kw, headers=H)
    assert post(theme="nope", style="dan-duong", deviation=10, session_id="s").status_code == 422
    assert post(theme="nguoc-dong", style="guide", deviation=10, session_id="s").status_code == 422
    assert post(theme="nguoc-dong", style="dan-duong", deviation=101, session_id="s").status_code == 422
    assert post(theme="nguoc-dong", style="dan-duong", deviation=10, session_id=" ").status_code == 422
    r1 = post(theme="nguoc-dong", style="dan-duong", deviation=30, session_id="alice").json()
    assert r1["rank"] == 1
    r2 = post(theme="nguoc-dong", style="tam-guong", deviation=10, session_id="bob").json()
    assert r2["rank"] == 1
    r3 = post(theme="nguoc-dong", style="dan-duong", deviation=50, session_id="alice").json()
    assert r3["rank"] == 3  # alice chỉ tính điểm tốt nhất (30): bob 10, alice 30, lượt 50 đứng 3
    top = TestClient(app).get("/api/v1/public/game/scores?theme=nguoc-dong&limit=10").json()
    assert [(x["deviation"], x["style"]) for x in top] == [(10, "tam-guong"), (30, "dan-duong")]
    assert "session_id" not in top[0]  # ẩn danh: không lộ session
    assert c.get("/api/v1/public/game/scores?theme=nope").status_code == 422
