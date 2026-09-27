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
    assert post(theme="nope", style="dan_duong", deviation=10, session_id="s").status_code == 422
    assert post(theme="nguoc-dong", style="guide", deviation=10, session_id="s").status_code == 422
    assert post(theme="nguoc-dong", style="dan-duong", deviation=10, session_id="s").status_code == 422
    assert post(theme="nguoc-dong", style="dan_duong", deviation=101, session_id="s").status_code == 422
    assert post(theme="nguoc-dong", style="dan_duong", deviation=10, session_id=" ").status_code == 422
    r1 = post(theme="nguoc-dong", style="dan_duong", deviation=30, session_id="alice").json()
    assert r1["rank"] == 1
    r2 = post(theme="nguoc-dong", style="tam_guong", deviation=10, session_id="bob").json()
    assert r2["rank"] == 1
    r3 = post(theme="nguoc-dong", style="dan_duong", deviation=50, session_id="alice").json()
    assert r3["rank"] == 3  # alice chỉ tính điểm tốt nhất (30): bob 10, alice 30, lượt 50 đứng 3
    top = TestClient(app).get("/api/v1/public/game/scores?theme=nguoc-dong&limit=10").json()
    assert [(x["deviation"], x["style"]) for x in top] == [(10, "tam_guong"), (30, "dan_duong")]
    assert "session_id" not in top[0]  # ẩn danh: không lộ session
    assert c.get("/api/v1/public/game/scores?theme=nope").status_code == 422

def test_streak_flow(app):
    c = login(app)
    post = lambda sid: c.post("/api/v1/public/game/streak", json={"session_id": sid}, headers=H)
    assert post(" ").status_code == 422
    assert post("streaky").json() == {"streak": 1, "today_done": True}
    assert post("streaky").json() == {"streak": 1, "today_done": True}  # cùng ngày không tăng
    assert c.get("/api/v1/public/game/streak?session_id=streaky").json() == {"streak": 1, "today_done": True}
    assert c.get("/api/v1/public/game/streak?session_id=nobody").json() == {"streak": 0, "today_done": False}


def test_game_manager(app):
    admin = login(app)
    anon = TestClient(app)
    G = "/api/v1/game"
    assert anon.get(f"{G}/concepts").status_code == 401
    concepts = admin.get(f"{G}/concepts", headers=H).json()
    assert {"nguoc-dong", "thuong-vu", "linh-thu"} <= {c["slug"] for c in concepts}
    assert all(c["enabled"] and c["is_builtin"] for c in concepts)
    # Bật/tắt built-in; nội dung built-in không sửa được
    assert admin.patch(f"{G}/concepts/nguoc-dong", json={"enabled": False}, headers=H).json()["enabled"] is False
    assert admin.patch(f"{G}/concepts/nguoc-dong", json={"name": "X"}, headers=H).status_code == 422
    admin.patch(f"{G}/concepts/nguoc-dong", json={"enabled": True}, headers=H)
    # Concept custom: validate slug + đủ nội dung
    assert admin.post(f"{G}/concepts", json={"slug": "Bad Slug!", "name": "x"}, headers=H).status_code == 422
    assert admin.post(f"{G}/concepts", json={"slug": "nguoc-dong", "name": "x"}, headers=H).status_code == 422
    assert admin.post(f"{G}/concepts", json={"slug": "admin", "name": "x"}, headers=H).status_code == 422
    cc = admin.post(f"{G}/concepts", json={
        "slug": "tuoi-tho", "name": "Tuổi Thơ", "entry_label": "Chơi Tuổi Thơ",
        "entry_desc": "Về lại sân trường.", "icon": "🪁", "intro": "I", "bridge": "B"},
        headers=H).json()
    assert cc["enabled"] is False and cc["is_builtin"] is False
    assert admin.post(f"{G}/concepts", json={"slug": "tuoi-tho", "name": "y"}, headers=H).status_code in (409, 422)
    # Câu hỏi: phải đủ 4 đáp án đúng style
    bad = admin.post(f"{G}/questions", json={
        "concept_slug": "tuoi-tho", "title": "T", "sit": "S",
        "options": [{"t": "a", "s": "khoi_xuong"}]}, headers=H)
    assert bad.status_code == 422
    opts = [{"t": f"Đáp án {i}", "s": s} for i, s in
            enumerate(["khoi_xuong", "kien_tao", "dan_duong", "tam_guong"])]
    q = admin.post(f"{G}/questions", json={
        "concept_slug": "tuoi-tho", "title": "Tình huống", "sit": "Chi tiết",
        "options": opts}, headers=H).json()
    assert q["qid"].startswith("cx")
    assert admin.patch(f"{G}/questions/{q['id']}", json={"enabled": False}, headers=H).json()["enabled"] is False
    concepts = admin.get(f"{G}/concepts", headers=H).json()
    ct = next(c for c in concepts if c["slug"] == "tuoi-tho")
    assert (ct["custom_total"], ct["custom_enabled"]) == (1, 0)
    # Ẩn câu built-in
    assert admin.post(f"{G}/questions/disabled",
                      json={"concept_slug": "nguoc-dong", "qid": "nd001"}, headers=H).status_code == 200
    # Config công khai phản ánh đúng
    cfg = anon.get("/api/v1/public/game/config").json()
    by_slug = {c["slug"]: c for c in cfg["concepts"]}
    assert by_slug["tuoi-tho"]["name"] == "Tuổi Thơ"
    assert by_slug["tuoi-tho"]["enabled"] is False
    assert "nd001" in cfg["disabled_builtin"]["nguoc-dong"]
    assert cfg["custom_questions"].get("tuoi-tho", []) == []
    # Dọn: xóa câu hỏi + concept + bỏ ẩn
    assert admin.delete(f"{G}/questions/{q['id']}", headers=H).status_code == 200
    assert admin.delete(f"{G}/concepts/tuoi-tho", headers=H).status_code == 200
    assert admin.delete(f"{G}/concepts/nguoc-dong", headers=H).status_code == 422
    assert anon.get("/api/v1/public/game/config").json()["custom_questions"].get("tuoi-tho") is None
    assert admin.delete(f"{G}/questions/disabled?concept_slug=nguoc-dong&qid=nd001",
                        headers=H).status_code == 200
