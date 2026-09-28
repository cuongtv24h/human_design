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


def test_access_token_scoped_to_file_exports(app):
    """Query token KHÔNG còn xác thực endpoint dữ liệu tùy ý (chỉ route xuất file)."""
    embedded = TestClient(app).post("/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD},
                                    headers={**H, "X-HD-Embedded": "1"})
    token = embedded.json()["session_token"]
    anon = TestClient(app)
    # Trước sửa: GET /auth/me?access_token= → 200 (token lọt vào access log). Giờ phải 401.
    assert anon.get(f"/api/v1/auth/me?access_token={token}").status_code == 401
    assert anon.get(f"/api/v1/clients?access_token={token}").status_code == 401
    assert anon.get(f"/api/v1/reports?access_token={token}").status_code == 401
    # Route xuất file vẫn hoạt động (cover ở test_embedded_preview_token_fallback với bodygraph.svg).


def test_client_ip_prefers_real_ip_then_last_hop():
    """X-Real-IP (nginx) thắng; không có thì lấy phần tử CUỐI XFF — không bao giờ phần tử đầu."""
    from starlette.requests import Request

    from backend.api.deps import client_ip

    def req(headers: dict, client=("203.0.113.9", 1234)) -> Request:
        scope = {"type": "http", "http_version": "1.1", "method": "GET", "path": "/", "raw_path": b"/",
                 "query_string": b"", "scheme": "http", "server": ("127.0.0.1", 80), "client": client,
                 "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()]}
        return Request(scope)

    # Spoofed leftmost XFF bị bỏ qua khi có X-Real-IP (chuỗi nginx thật).
    spoof = {"X-Real-IP": "198.51.100.7", "X-Forwarded-For": "1.2.3.4, 198.51.100.7"}
    assert client_ip(req(spoof)) == "198.51.100.7"
    # Không có X-Real-IP: hop cuối cùng (do proxy thêm) thắng phần tử spoofed phía trước.
    assert client_ip(req({"X-Forwarded-For": "1.2.3.4, 198.51.100.7"})) == "198.51.100.7"
    # Không có header proxy: dùng peer trực tiếp.
    assert client_ip(req({})) == "203.0.113.9"


def test_docs_hidden_in_production(tmp_path):
    """Production không public /api/v1/docs lẫn /openapi.json."""
    application = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'prod.db'}",
                                      artifact_dir=str(tmp_path / "artifacts"), secret_key="test-secret",
                                      environment="production", auto_create_tables=True))
    client = TestClient(application)
    assert client.get("/api/v1/docs").status_code == 404
    assert client.get("/api/v1/openapi.json").status_code == 404
    assert client.get("/api/v1/health").status_code == 200  # health vẫn chạy để monitor


def test_load_dotenv_warns_on_permissive_file(tmp_path, caplog):
    """.env (chứa HD_SECRET_KEY + khóa LLM) group/other đọc được → phải cảnh báo chmod 600."""
    import backend.api.settings as settings_mod

    env_file = tmp_path / ".env"
    env_file.write_text("HD_PERM_PROBE=1\n", encoding="utf-8")
    try:
        env_file.chmod(0o644)
        with caplog.at_level("WARNING", logger="hd.settings"):
            settings_mod.load_dotenv(env_file)
        assert any("chmod 600" in r.getMessage() for r in caplog.records), "thiếu cảnh báo quyền lỏng lẻo"

        caplog.clear()
        env_file.chmod(0o600)
        with caplog.at_level("WARNING", logger="hd.settings"):
            settings_mod.load_dotenv(env_file)
        assert not [r for r in caplog.records if "chmod 600" in r.getMessage()]
    finally:
        import os as _os
        _os.environ.pop("HD_PERM_PROBE", None)


def test_cors_preflight_enumerates_methods_and_headers(tmp_path):
    """CORS (khi bật) chỉ cho method/header cần thiết — không wildcard (bảo vệ CSRF)."""
    application = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'cors.db'}",
                                      artifact_dir=str(tmp_path / "a"), secret_key="test-secret",
                                      cors_origins=("https://partner.example",)))
    client = TestClient(application)
    # Preflight hợp lệ: echo đúng allow-list, không wildcard.
    pre = client.options("/api/v1/auth/login", headers={
        "Origin": "https://partner.example",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,x-hd-request",
    })
    assert pre.status_code == 200
    allow_headers = pre.headers.get("access-control-allow-headers", "").lower()
    allow_methods = pre.headers.get("access-control-allow-methods", "").upper()
    assert "x-hd-request" in allow_headers and "content-type" in allow_headers
    assert allow_methods == "GET, POST, PATCH, PUT, DELETE, OPTIONS"
    # Preflight kèm header lạ (ngoài allow-list) → Starlette từ chối 400 → browser chặn.
    evil = client.options("/api/v1/auth/login", headers={
        "Origin": "https://partner.example",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,x-hd-request,x-evil-header",
    })
    assert evil.status_code == 400 and "x-evil-header" not in evil.headers.get("access-control-allow-headers", "").lower()
    # Origin không nằm trong allowlist → không có CORS header nào.
    outsider = client.options("/api/v1/auth/login", headers={
        "Origin": "https://evil.example",
        "Access-Control-Request-Method": "POST",
    })
    assert "access-control-allow-origin" not in outsider.headers


def test_login_ip_wide_rate_limit_blocks_spray(app):
    """Password-spray: 1 mật khẩu, nhiều email cùng IP — bucket IP thuần chặn ở lần 21."""
    anon = TestClient(app)
    for i in range(20):
        r = anon.post("/api/v1/auth/login",
                      json={"email": f"u{i}@spray.vn", "password": "mat-khau-sai"}, headers=H)
        assert r.status_code == 401, r.text   # mỗi email 1 bucket riêng → chưa chặn
    # Bucket IP (20 lỗi/15 phút) đầy → kể cả email mới cũng 429.
    blocked = anon.post("/api/v1/auth/login",
                        json={"email": "u21@spray.vn", "password": "sai"}, headers=H)
    assert blocked.status_code == 429
    # Đăng nhập đúng của admin cùng IP cũng bị tạm chặn cho tới khi bucket nguội
    # (chống dò pass từ IP đã gây 20 lỗi).
    assert anon.post("/api/v1/auth/login",
                     json={"email": "admin@example.com", "password": PASSWORD}, headers=H).status_code == 429


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


def test_user_update_and_password_reset(app):
    admin = login(app)
    coach = admin.post("/api/v1/users", json={"email": "coach@example.com", "password": PASSWORD,
                                              "full_name": "Coach B", "role": "coach"}, headers=H).json()
    assert coach["created_at"] and coach["last_login_at"] is None
    # Sửa tên + nâng quyền.
    updated = admin.patch(f"/api/v1/users/{coach['id']}", json={"full_name": "Coach Bee", "role": "admin"},
                          headers=H)
    assert updated.status_code == 200, updated.text
    assert updated.json()["full_name"] == "Coach Bee" and updated.json()["role"] == "admin"
    # Không được tự khóa / tự hạ quyền.
    me = admin.get("/api/v1/auth/me").json()
    assert admin.patch(f"/api/v1/users/{me['id']}", json={"role": "coach"}, headers=H).status_code == 422
    assert admin.patch(f"/api/v1/users/{me['id']}", json={"is_active": False}, headers=H).status_code == 422
    # Đặt lại mật khẩu → phiên cũ của coach bị đá, mật khẩu mới dùng được.
    session = login(app, "coach@example.com")
    assert session.get("/api/v1/auth/me").status_code == 200
    reset = admin.patch(f"/api/v1/users/{coach['id']}", json={"password": "mat-khau-moi-456"}, headers=H)
    assert reset.status_code == 200
    assert session.get("/api/v1/auth/me").status_code == 401
    assert login(app, "coach@example.com", "mat-khau-moi-456").get("/api/v1/auth/me").status_code == 200
    bad = admin.patch(f"/api/v1/users/{coach['id']}", json={"password": "ngan"}, headers=H)
    assert bad.status_code == 422


def test_user_delete(app):
    admin = login(app)
    me = admin.get("/api/v1/auth/me").json()
    mk = lambda email: admin.post("/api/v1/users", json={"email": email, "password": PASSWORD,
                                                         "full_name": email, "role": "coach"}, headers=H).json()
    empty, busy, reporter = mk("empty@example.com"), mk("busy@example.com"), mk("rp@example.com")
    # Không được tự xóa.
    assert admin.delete(f"/api/v1/users/{me['id']}", headers=H).status_code == 422
    # Còn khách hàng → 409.
    other = login(app, "busy@example.com")
    person = other.post("/api/v1/clients", json=CLIENT, headers=H)
    assert person.status_code == 201
    blocked = admin.delete(f"/api/v1/users/{busy['id']}", headers=H)
    assert blocked.status_code == 409 and "1 khách hàng" in blocked.json()["detail"]
    # Còn báo cáo → 409.
    session = login(app, "rp@example.com")
    person = session.post("/api/v1/clients", json=CLIENT, headers=H).json()
    made = session.post("/api/v1/reports", json={"client_id": person["id"], "tier": "free_basic",
                                                 "template": "sections", "domains": []}, headers=H)
    assert made.status_code == 201
    blocked = admin.delete(f"/api/v1/users/{reporter['id']}", headers=H)
    assert blocked.status_code == 409 and "1 báo cáo" in blocked.json()["detail"]
    # Tài khoản trống xóa được, không đăng nhập lại được.
    assert admin.delete(f"/api/v1/users/{empty['id']}", headers=H).status_code == 204
    anon = TestClient(app)
    gone = anon.post("/api/v1/auth/login", json={"email": "empty@example.com", "password": PASSWORD}, headers=H)
    assert gone.status_code == 401
    assert empty["id"] not in [u["id"] for u in admin.get("/api/v1/users").json()]
    # Admin này xóa admin kia vẫn được vì còn lại chính mình.
    admin2 = admin.post("/api/v1/users", json={"email": "admin2@example.com", "password": PASSWORD,
                                               "full_name": "Admin 2", "role": "admin"}, headers=H).json()
    as_admin2 = login(app, "admin2@example.com")
    assert as_admin2.delete(f"/api/v1/users/{me['id']}", headers=H).status_code == 204
    ids = [u["id"] for u in as_admin2.get("/api/v1/users").json()]
    assert me["id"] not in ids and admin2["id"] in ids


def test_change_own_password(app):
    first = login(app)
    second = login(app)
    assert first.post("/api/v1/auth/password", json={"current_password": "sai-mat-khau",
                                                      "new_password": "mat-khau-moi-789"}, headers=H).status_code == 401
    changed = first.post("/api/v1/auth/password", json={"current_password": PASSWORD,
                                                         "new_password": "mat-khau-moi-789"}, headers=H)
    assert changed.status_code == 204
    # Phiên hiện tại còn dùng được, phiên kia bị đá.
    assert first.get("/api/v1/auth/me").status_code == 200
    assert second.get("/api/v1/auth/me").status_code == 401
    anon = TestClient(app)
    old = anon.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD}, headers=H)
    assert old.status_code == 401
    new = anon.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "mat-khau-moi-789"},
                    headers=H)
    assert new.status_code == 200


def test_report_with_partner_composite(app):
    client = login(app)
    person = client.post("/api/v1/clients", json=CLIENT, headers=H).json()
    partner = {"name": "Trần Thị B", "birth_date": "1992-03-10", "birth_time": "14:20",
               "timezone": "+07:00"}
    preview = client.post("/api/v1/reports/preview", json={
        "client_id": person["id"], "tier": "deep_core", "template": "sections",
        "domains": ["relationship"], "partner": partner}, headers=H)
    assert preview.status_code == 200, preview.text
    assert "COMPOSITE 2 NGƯỜI" in preview.json()["markdown"]

    created = client.post("/api/v1/reports", json={
        "client_id": person["id"], "tier": "deep_core", "template": "sections",
        "domains": ["relationship"], "partner": partner}, headers=H)
    assert created.status_code == 201, created.text
    md = client.get(f"/api/v1/reports/{created.json()['id']}/markdown")
    assert md.status_code == 200
    assert "COMPOSITE 2 NGƯỜI" in md.text

    bad = client.post("/api/v1/reports/preview", json={
        "client_id": person["id"], "partner": {**partner, "birth_time": "25:00"}}, headers=H)
    assert bad.status_code == 422
