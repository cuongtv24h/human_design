"""Admin API /api/v1: auth, permissions, clients, reports, exports (SQLite temp DB)."""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fastapi.testclient import TestClient  # noqa: E402

from backend.api.cli import ensure_admin  # noqa: E402
from backend.api.main import create_app  # noqa: E402
from backend.api.settings import Settings  # noqa: E402

H = {"X-HD-Request": "1"}
PASSWORD = "matkhau-123"
CLIENT = {
    "full_name": "Nguyễn Văn A",
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "birth_place": "Hòa Bình",
    "consent": True,
}


@pytest.fixture()
def app(tmp_path):
    application = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'api.sqlite3'}",
                                      artifact_dir=str(tmp_path / "artifacts"), secret_key="test-secret"))
    ensure_admin(application.state.db, "admin@example.com", PASSWORD, "Quản trị")
    return application


def login(app, email="admin@example.com", password=PASSWORD) -> TestClient:
    client = TestClient(app)
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password}, headers=H)
    assert response.status_code == 200, response.text
    return client


def test_login_logout_and_me(app):
    anon = TestClient(app)
    assert anon.get("/api/v1/auth/me").status_code == 401
    bad = anon.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "sai"}, headers=H)
    assert bad.status_code == 401
    assert bad.headers["content-type"].startswith("application/problem+json")
    assert "mật khẩu" in bad.json()["detail"]

    client = login(app)
    cookie = client.cookies.get("hd_session")
    assert cookie
    me = client.get("/api/v1/auth/me").json()
    assert me["role"] == "admin" and me["org_name"]
    assert client.post("/api/v1/auth/logout", headers=H).status_code == 204
    reuse = TestClient(app)
    reuse.cookies.set("hd_session", cookie)
    assert reuse.get("/api/v1/auth/me").status_code == 401


def test_csrf_header_required_for_mutations(app):
    client = login(app)
    response = client.post("/api/v1/clients", json=CLIENT)
    assert response.status_code == 403
    assert "CSRF" in response.json()["detail"]


def test_client_crud_requires_consent_and_valid_birth(app):
    client = login(app)
    no_consent = client.post("/api/v1/clients", json={**CLIENT, "consent": False}, headers=H)
    assert no_consent.status_code == 422
    bad_date = client.post("/api/v1/clients", json={**CLIENT, "birth_date": "1990-02-30"}, headers=H)
    assert bad_date.status_code == 422
    bad_tz = client.post("/api/v1/clients", json={**CLIENT, "timezone": "Europe/Paris"}, headers=H)
    assert bad_tz.status_code == 422

    created = client.post("/api/v1/clients", json={**CLIENT, "timezone": "Asia/Ho_Chi_Minh"}, headers=H)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["timezone"] == "+07:00"
    assert body["birth_display"] == "15/05/1990 08:30 (giờ Việt Nam)"
    assert body["consent_at"]

    listing = client.get("/api/v1/clients", params={"q": "văn a"}).json()
    assert listing["total"] == 1
    patched = client.patch(f"/api/v1/clients/{body['id']}", json={"birth_time": "09:15"}, headers=H).json()
    assert patched["birth_time"] == "09:15"
    assert client.delete(f"/api/v1/clients/{body['id']}", headers=H).status_code == 204
    assert client.get(f"/api/v1/clients/{body['id']}").status_code == 404


def test_coach_only_sees_own_clients(app):
    admin = login(app)
    coach = admin.post("/api/v1/users", json={"email": "coach@example.com", "password": PASSWORD,
                                              "full_name": "Coach B", "role": "coach"}, headers=H)
    assert coach.status_code == 201
    admin_client = admin.post("/api/v1/clients", json=CLIENT, headers=H).json()

    coach_session = login(app, "coach@example.com")
    assert coach_session.get("/api/v1/users").status_code == 403
    assert coach_session.get(f"/api/v1/clients/{admin_client['id']}").status_code == 404
    own = coach_session.post("/api/v1/clients", json={**CLIENT, "full_name": "Trần Thị B"}, headers=H).json()
    assert [c["id"] for c in coach_session.get("/api/v1/clients").json()["items"]] == [own["id"]]
    assert admin.get("/api/v1/clients").json()["total"] == 2


def test_catalog_and_preview(app):
    client = login(app)
    catalog = client.get("/api/v1/catalog").json()
    assert {t["value"] for t in catalog["tiers"]} == {"free_basic", "deep_core"}
    assert catalog["timezone_default"] == "+07:00"
    assert len(catalog["sections_by_tier"]["operating_manual"]) == 5

    preview = client.post("/api/v1/reports/preview", json={
        "birth_date": "1990-05-15", "birth_time": "08:30", "full_name": "Nguyễn Văn A",
        "tier": "deep_core", "template": "operating_manual"}, headers=H)
    assert preview.status_code == 200, preview.text
    data = preview.json()
    assert data["summary"]["type"] == "Projector"
    assert data["summary"]["profile"] == "6/2"
    assert data["bodygraph_svg"].lstrip().startswith("<")
    assert "08:30 (giờ Việt Nam)" in data["markdown"]
    assert "UTC" not in data["markdown"]


def test_report_lifecycle_and_exports(app):
    client = login(app)
    person = client.post("/api/v1/clients", json=CLIENT, headers=H).json()
    created = client.post("/api/v1/reports", json={"client_id": person["id"], "tier": "free_basic",
                                                   "template": "sections", "domains": ["money"]}, headers=H)
    assert created.status_code == 201, created.text
    report = created.json()
    assert report["status"] == "ready" and report["version"] == 1
    assert report["summary"]["type_vn"] == "Người định hướng"
    assert report["sections"] and report["markdown"]

    rid = report["id"]
    md = client.get(f"/api/v1/reports/{rid}/markdown")
    assert md.status_code == 200 and "attachment" in md.headers["content-disposition"]
    html = client.get(f"/api/v1/reports/{rid}/infographic.html")
    assert html.status_code == 200 and "<html" in html.text.lower()
    assert "default-src 'none'" in html.headers["content-security-policy"]
    svg = client.get(f"/api/v1/reports/{rid}/bodygraph.svg")
    assert svg.headers["content-type"].startswith("image/svg+xml")

    pdf = client.get(f"/api/v1/reports/{rid}/pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    assert pdf.headers["content-type"] == "application/pdf"
    docx = client.get(f"/api/v1/reports/{rid}/docx")
    assert docx.status_code == 200 and docx.content[:2] == b"PK"
    assert ".docx" in docx.headers["content-disposition"]
    assert client.get(f"/api/v1/reports/{rid}/exe").status_code == 404
    # Pre-rendered after creation and cached per version on disk.
    cached = list((pathlib.Path(app.state.settings.artifact_dir) / rid).glob("v1-*"))
    assert {p.suffix for p in cached} == {".pdf", ".docx"}

    dash = client.get("/api/v1/dashboard").json()
    assert dash["clients"] == 1 and dash["reports_by_status"] == {"ready": 1}
    assert client.get(f"/api/v1/clients/{person['id']}/reports").json()["total"] == 1

    archived = client.post(f"/api/v1/reports/{rid}/archive", headers=H).json()
    assert archived["status"] == "archived"
    assert client.get("/api/v1/reports").json()["total"] == 0


def test_llm_mode_without_key_falls_back_in_background(app, monkeypatch):
    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = login(app)
    person = client.post("/api/v1/clients", json=CLIENT, headers=H).json()
    created = client.post("/api/v1/reports", json={"client_id": person["id"], "content_mode": "llm"}, headers=H)
    assert created.status_code == 201
    assert created.json()["status"] == "generating"
    # TestClient runs background tasks before returning; the report is now ready (template fallback).
    detail = client.get(f"/api/v1/reports/{created.json()['id']}").json()
    assert detail["status"] == "ready"
    assert detail["editor"] == "template (llm fallback)"
    assert any("LLM" in w for w in detail["warnings"])


# --- editor (P2) ------------------------------------------------------------

def _ready_report(client) -> str:
    person = client.post("/api/v1/clients", json=CLIENT, headers=H).json()
    report = client.post("/api/v1/reports", json={"client_id": person["id"], "tier": "free_basic",
                                                  "template": "sections"}, headers=H).json()
    return report["id"]


def test_editor_payload_hides_internal_times_and_has_glossary(app):
    client = login(app)
    rid = _ready_report(client)
    data = client.get(f"/api/v1/reports/{rid}/editor").json()
    assert data["report"]["version"] == 1
    assert [s["id"] for s in data["sections"]][0] == "summary"
    assert "birth_datetime" not in str(data["sections"]) and "birth_jd" not in str(data["sections"])
    assert any(g["title"].startswith("Loại năng lượng") for g in data["glossary"])


def test_section_save_facts_warning_versions_and_restore(app):
    client = login(app)
    rid = _ready_report(client)
    section = next(s for s in client.get(f"/api/v1/reports/{rid}/editor").json()["sections"]
                   if s["id"] == "type_strategy_authority")
    assert "Projector" in section["content_markdown"]

    check = client.post(f"/api/v1/reports/{rid}/sections/{section['id']}/check",
                        json={"content_markdown": "Bạn là người rất đặc biệt."}, headers=H).json()
    assert "Projector" in check["missing_facts"]

    saved = client.put(f"/api/v1/reports/{rid}/sections/{section['id']}",
                       json={"content_markdown": "Bạn là người rất đặc biệt.", "base_version": 1}, headers=H)
    assert saved.status_code == 200, saved.text
    body = saved.json()
    assert body["version"] == 2 and "Projector" in body["missing_facts"]
    assert any("mất sự kiện" in w for w in body["section"]["warnings"])  # warns, never blocks

    stale = client.put(f"/api/v1/reports/{rid}/sections/{section['id']}",
                       json={"content_markdown": "x", "base_version": 1}, headers=H)
    assert stale.status_code == 409

    detail = client.get(f"/api/v1/reports/{rid}").json()
    assert "Bạn là người rất đặc biệt." in detail["markdown"] and detail["version"] == 2
    history = client.get(f"/api/v1/reports/{rid}/revisions").json()
    assert [(r["version"], r["change_type"]) for r in history] == [(2, "manual_edit"), (1, "generate")]

    restored = client.post(f"/api/v1/reports/{rid}/revisions/1/restore", headers=H).json()
    assert restored["version"] == 3 and "Bạn là người rất đặc biệt." not in restored["markdown"]
    assert client.get(f"/api/v1/reports/{rid}/revisions").json()[0]["change_type"] == "restore:v1"
    # Files follow the new version.
    assert client.get(f"/api/v1/reports/{rid}/pdf").status_code == 200
    cached = sorted(p.name.split("-")[0] for p in (pathlib.Path(app.state.settings.artifact_dir) / rid).iterdir())
    assert cached == ["v3", "v3"]  # older versions pruned after the new one is pre-rendered


def test_llm_section_proposal(app, monkeypatch):
    client = login(app)
    rid = _ready_report(client)
    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    no_key = client.post(f"/api/v1/reports/{rid}/sections/summary/llm", headers=H)
    assert no_key.status_code == 503 and "HD_LLM_API_KEY" in no_key.json()["detail"]

    import backend.api.routers.editor as editor_router

    seen = {}

    def fake_edit(document, section_id, llm_configs, **kwargs):
        seen["section"] = section_id
        seen["model"] = llm_configs[0].model
        return "Bản AI viết lại, vẫn nhắc Projector.\n"

    monkeypatch.setattr(editor_router, "llm_edit_section", fake_edit)
    monkeypatch.setenv("HD_LLM_API_KEY", "sk-env-test")
    proposal = client.post(f"/api/v1/reports/{rid}/sections/summary/llm", headers=H).json()
    assert seen["section"] == "summary"
    assert proposal["draft"].startswith("Bản AI viết lại")
    assert client.get(f"/api/v1/reports/{rid}").json()["version"] == 1  # proposal is not saved


def test_regenerate_template_creates_new_version(app):
    client = login(app)
    rid = _ready_report(client)
    client.put(f"/api/v1/reports/{rid}/sections/summary", json={"content_markdown": "sửa tay", "base_version": 1},
               headers=H)
    regenerated = client.post(f"/api/v1/reports/{rid}/regenerate", json={}, headers=H).json()
    assert regenerated["version"] == 3 and "sửa tay" not in regenerated["markdown"]


def test_cookie_options_for_embedded_preview():
    assert Settings().cookie_options() == {"samesite": "lax", "secure": False}
    assert Settings(cookie_samesite="none").cookie_options() == {"samesite": "none", "secure": True}
    assert Settings(cookie_samesite="none").cookie_partitioned
    assert Settings(cookie_samesite="weird", cookie_secure=True).cookie_options() == {"samesite": "lax", "secure": True}


def test_partitioned_session_cookie(tmp_path):
    app = create_app(Settings(database_url=f"sqlite:///{tmp_path}/c.db", artifact_dir=str(tmp_path / "a"),
                              secret_key_file=str(tmp_path / "secret_key"),
                              cookie_samesite="none"))
    ensure_admin(app.state.db, "p@demo.vn", "12345678")
    response = TestClient(app).post("/api/v1/auth/login", json={"email": "p@demo.vn", "password": "12345678"}, headers=H)
    cookie = response.headers["set-cookie"]
    assert response.status_code == 200 and "SameSite=none" in cookie and "Secure" in cookie and cookie.endswith("Partitioned")


def test_embedded_preview_token_fallback(app):
    """Cross-site iframe previews may drop cookies: Bearer header / GET ?access_token= still work."""
    anon = TestClient(app)
    normal = anon.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD}, headers=H)
    assert "session_token" not in normal.json()  # top-level admin: cookie only

    embedded = TestClient(app).post("/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD},
                                    headers={**H, "X-HD-Embedded": "1"})
    token = embedded.json()["session_token"]
    no_cookie = TestClient(app)  # simulates the browser discarding the cookie
    assert no_cookie.get("/api/v1/auth/me").status_code == 401
    bearer = {"Authorization": f"Bearer {token}"}
    assert no_cookie.get("/api/v1/auth/me", headers=bearer).json()["email"] == "admin@example.com"
    person = no_cookie.post("/api/v1/clients", json=CLIENT, headers={**H, **bearer})
    assert person.status_code == 201
    rid = no_cookie.post("/api/v1/reports", json={"client_id": person.json()["id"], "tier": "free_basic",
                                                  "template": "sections"}, headers={**H, **bearer}).json()["id"]
    svg = no_cookie.get(f"/api/v1/reports/{rid}/bodygraph.svg?access_token={token}")
    assert svg.status_code == 200 and svg.headers["content-type"].startswith("image/svg")
    # Query token is never accepted for state-changing requests.
    assert no_cookie.post(f"/api/v1/reports/{rid}/archive?access_token={token}", headers=H).status_code == 401
    assert no_cookie.post("/api/v1/auth/logout", headers={**H, **bearer}).status_code == 204
    assert no_cookie.get("/api/v1/auth/me", headers=bearer).status_code == 401


def test_clients_order_recent(app):
    admin = login(app)
    a = admin.post("/api/v1/clients", json={**CLIENT, "full_name": "Khách A"}, headers=H).json()
    b = admin.post("/api/v1/clients", json={**CLIENT, "full_name": "Khách B"}, headers=H).json()
    c = admin.post("/api/v1/clients", json={**CLIENT, "full_name": "Khách C"}, headers=H).json()
    for cid in (b["id"], a["id"]):
        made = admin.post("/api/v1/reports", json={"client_id": cid, "tier": "free_basic",
                                                   "template": "sections", "domains": []}, headers=H)
        assert made.status_code == 201, made.text
    recent = [x["id"] for x in admin.get("/api/v1/clients", params={"order": "recent"}).json()["items"]]
    assert recent == [a["id"], b["id"], c["id"]]
    top5 = admin.get("/api/v1/clients", params={"order": "recent", "limit": 5}).json()["items"]
    assert len(top5) == 3
    # Mặc định cũ giữ nguyên: cập nhật gần nhất trước.
    default = [x["id"] for x in admin.get("/api/v1/clients").json()["items"]]
    assert default == [c["id"], b["id"], a["id"]]
    assert admin.get("/api/v1/clients", params={"order": "bogus"}).status_code == 422

    # Tương tác của user khác không chen vào top của mình; khách mới vẫn hiện trước.
    coach = admin.post("/api/v1/users", json={"email": "coach@example.com", "password": PASSWORD,
                                              "full_name": "Coach B", "role": "coach"}, headers=H)
    assert coach.status_code == 201
    session = login(app, "coach@example.com")
    d = session.post("/api/v1/clients", json={**CLIENT, "full_name": "Khách D"}, headers=H).json()
    made = session.post("/api/v1/reports", json={"client_id": d["id"], "tier": "free_basic",
                                                 "template": "sections", "domains": []}, headers=H)
    assert made.status_code == 201, made.text
    own = [x["id"] for x in session.get("/api/v1/clients", params={"order": "recent"}).json()["items"]]
    assert own == [d["id"]]
    recent2 = [x["id"] for x in admin.get("/api/v1/clients", params={"order": "recent"}).json()["items"]]
    assert recent2 == [a["id"], b["id"], d["id"], c["id"]]
