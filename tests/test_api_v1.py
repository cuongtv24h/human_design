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
                                      artifact_dir=str(tmp_path / "artifacts")))
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
