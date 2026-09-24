"""P0-10 signed download links, P2-6 LLM settings, P3-1 share links."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from test_api_v1 import CLIENT, H, PASSWORD, app, login  # noqa: F401  (fixture re-export)

from backend.api.cli import ensure_admin
from backend.api.security import decrypt_value, encrypt_value, sign_token, verify_token


def _report(client) -> str:
    person = client.post("/api/v1/clients", json=CLIENT, headers=H).json()
    return client.post("/api/v1/reports", json={"client_id": person["id"], "tier": "free_basic",
                                                "template": "sections"}, headers=H).json()["id"]


def _coach(app, email="coach@example.com") -> TestClient:
    admin = login(app)
    admin.post("/api/v1/users", json={"email": email, "full_name": "Coach", "password": PASSWORD, "role": "coach"},
               headers=H)
    return login(app, email)


# --- tokens & encryption --------------------------------------------------------

def test_signed_token_roundtrip_expiry_and_tamper():
    token, exp = sign_token("s", "download", {"r": "abc"}, 300, now=1000)
    assert exp == 1300
    assert verify_token("s", "download", token, now=1200)["r"] == "abc"
    assert verify_token("s", "download", token, now=1301) is None  # expired
    assert verify_token("other", "download", token, now=1200) is None  # other secret
    assert verify_token("s", "share", token, now=1200) is None  # other purpose
    body, mac = token.split(".")
    assert verify_token("s", "download", body[:-2] + "xx." + mac, now=1200) is None
    assert verify_token("s", "download", "garbage", now=1200) is None


def test_encrypted_values():
    enc = encrypt_value("s1", "sk-secret-1234")
    assert "sk-secret" not in enc
    assert decrypt_value("s1", enc) == "sk-secret-1234"
    assert decrypt_value("s2", enc) is None


# --- P0-10 signed download links -------------------------------------------------

def test_signed_download_link_works_without_session(app):
    client = login(app)
    rid = _report(client)
    link = client.post(f"/api/v1/reports/{rid}/links", json={"format": "pdf"}, headers=H).json()
    assert link["url"].startswith("/api/v1/files/")
    expires = datetime.fromisoformat(link["expires_at"])
    assert timedelta(minutes=4) < expires - datetime.now(timezone.utc) <= timedelta(minutes=5)

    anon = TestClient(app)
    response = anon.get(link["url"])
    assert response.status_code == 200 and response.content.startswith(b"%PDF")
    assert "attachment" in response.headers["content-disposition"]
    assert response.headers["x-robots-tag"].startswith("noindex")

    svg = client.post(f"/api/v1/reports/{rid}/links", json={"format": "bodygraph_svg"}, headers=H).json()
    assert anon.get(svg["url"]).headers["content-type"].startswith("image/svg+xml")
    assert anon.get(link["url"][:-3] + "abc").status_code == 410
    assert client.post(f"/api/v1/reports/{rid}/links", json={"format": "exe"}, headers=H).status_code == 422

    client.post(f"/api/v1/reports/{rid}/archive", headers=H)
    assert anon.get(link["url"]).status_code == 410  # archived → no longer served


def test_signed_link_expires(app, monkeypatch):
    client = login(app)
    rid = _report(client)
    url = client.post(f"/api/v1/reports/{rid}/links", json={"format": "markdown"}, headers=H).json()["url"]
    import backend.api.security as security

    real = security.time.time
    monkeypatch.setattr(security.time, "time", lambda: real() + 301)
    assert TestClient(app).get(url).status_code == 410


# --- P2-6 LLM settings ---------------------------------------------------------------

def _provider(**overrides):
    body = {"name": "Chính", "base_url": "https://llm.example.com/v1/", "model": "gpt-4.1-mini",
            "temperature": 0.4, "timeout": 90, "enabled": True,
            "input_price": 0.15, "output_price": 0.6, "api_key": "sk-live-abcdef9876"}
    body.update(overrides)
    return body


def test_llm_settings_encrypted_masked_and_used(app, monkeypatch):
    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    admin = login(app)
    initial = admin.get("/api/v1/settings/llm").json()
    assert initial["key_source"] == "none" and initial["providers"] == []
    assert admin.post("/api/v1/settings/llm/test", headers=H).status_code == 409

    saved = admin.put("/api/v1/settings/llm", json={"providers": [_provider()]}, headers=H).json()
    assert saved["key_source"] == "database" and saved["updated_by"] == "admin@example.com"
    first = saved["providers"][0]
    assert (first["name"], first["key_hint"]) == ("Chính", "••••9876")
    assert first["base_url"] == "https://llm.example.com/v1" and first["has_key"] is True
    assert "sk-live" not in admin.get("/api/v1/settings/llm").text

    # Stored encrypted — the plaintext key never reaches the database or the audit log.
    db_path = app.state.settings.database_url.removeprefix("sqlite:///")
    with sqlite3.connect(db_path) as conn:
        dump = "\n".join(conn.iterdump())
    assert "sk-live-abcdef9876" not in dump and "api_key_enc" in dump

    # Keep the key when api_key is omitted.
    kept = admin.put("/api/v1/settings/llm",
                     json={"providers": [_provider(api_key=None, model="m2")]}, headers=H).json()
    assert kept["providers"][0]["key_hint"] == "••••9876" and kept["providers"][0]["model"] == "m2"

    seen = {}

    def transport(url, headers, payload, timeout):
        seen.update(url=url, auth=headers["Authorization"], model=payload["model"])
        return {"choices": [{"message": {"content": "OK"}}]}

    app.state.llm_transport = transport
    result = admin.post("/api/v1/settings/llm/test", json={}, headers=H).json()
    assert result["results"][0]["ok"] and result["results"][0]["model"] == "m2"
    assert seen == {"url": "https://llm.example.com/v1/chat/completions", "auth": "Bearer sk-live-abcdef9876",
                    "model": "m2"}

    def failing(url, headers, payload, timeout):
        from backend.reporting.llm_client import LLMError
        raise LLMError("LLM HTTP 401: invalid key")

    app.state.llm_transport = failing
    bad = admin.post("/api/v1/settings/llm/test", json={"provider_index": 0}, headers=H).json()
    assert not bad["results"][0]["ok"] and "401" in bad["results"][0]["detail"]

    # The editor now sees AI as available (from the DB key, no env var).
    rid = _report(admin)
    assert admin.get(f"/api/v1/reports/{rid}/editor").json()["llm_available"] is True

    cleared = admin.put("/api/v1/settings/llm", json={"providers": [_provider(api_key="")]}, headers=H).json()
    assert cleared["key_source"] == "none" and cleared["providers"][0]["has_key"] is False
    monkeypatch.setenv("HD_LLM_API_KEY", "sk-env-00001111")
    env_view = admin.get("/api/v1/settings/llm").json()
    assert env_view["key_source"] == "environment"


def test_llm_settings_admin_only_and_validation(app):
    coach = _coach(app)
    assert coach.get("/api/v1/settings/llm").status_code == 403
    assert coach.get("/api/v1/settings/llm/usage").status_code == 403
    admin = login(app)
    bad = admin.put("/api/v1/settings/llm",
                    json={"providers": [_provider(base_url="ftp://x.y/z")]}, headers=H)
    assert bad.status_code == 422
    too_many = admin.put("/api/v1/settings/llm",
                         json={"providers": [_provider(name=f"P{i}") for i in range(4)]}, headers=H)
    assert too_many.status_code == 422


def test_unreadable_key_after_secret_rotation(tmp_path, monkeypatch):
    from backend.api.main import create_app
    from backend.api.settings import Settings

    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    kwargs = {"database_url": f"sqlite:///{tmp_path}/r.db", "artifact_dir": str(tmp_path / "a")}
    first = create_app(Settings(secret_key="one", **kwargs))
    ensure_admin(first.state.db, "r@example.com", PASSWORD)
    c1 = login(first, "r@example.com")
    c1.put("/api/v1/settings/llm", json={"providers": [_provider(base_url="https://x.io/v1", model="m",
                                                                                api_key="sk-rotate-1234")]}, headers=H)
    second = create_app(Settings(secret_key="two", **kwargs))
    view = login(second, "r@example.com").get("/api/v1/settings/llm").json()
    assert view["providers"][0]["key_unreadable"] is True and view["key_source"] == "none"


# --- P3-1 share links ------------------------------------------------------------------

def test_share_link_lifecycle(app):
    client = login(app)
    rid = _report(client)
    created = client.post(f"/api/v1/reports/{rid}/shares", json={"formats": ["pdf", "docx"], "expires_days": 7,
                                                                 "label": "Gửi qua Zalo"}, headers=H)
    assert created.status_code == 201, created.text
    data = created.json()
    token = data["url"].removeprefix("/r/")
    assert data["share"]["status"] == "active" and data["share"]["formats"] == ["docx", "pdf"]
    assert token not in client.get(f"/api/v1/reports/{rid}/shares").text  # shown once, stored hashed

    anon = TestClient(app)
    page = anon.get(f"/api/v1/public/r/{token}")
    assert page.status_code == 200 and page.headers["x-robots-tag"].startswith("noindex")
    body = page.json()
    assert body["client_name"] == "Nguyễn Văn A" and body["subject_display"].startswith("15/05/1990")
    assert body["summary"]["type"] and body["formats"] == ["docx", "pdf"] and body["sections"]
    assert "birth_datetime" not in page.text and "warnings" not in page.text
    assert anon.get(f"/api/v1/public/r/{token}/pdf").content.startswith(b"%PDF")
    assert anon.get(f"/api/v1/public/r/{token}/markdown").status_code == 404  # not shared
    info = anon.get(f"/api/v1/public/r/{token}/infographic.html")
    assert info.status_code == 200 and "default-src 'none'" in info.headers["content-security-policy"]
    anon.get(f"/api/v1/public/r/{token}")
    listed = client.get(f"/api/v1/reports/{rid}/shares").json()[0]
    assert listed["view_count"] == 2 and listed["last_viewed_at"]

    assert anon.get("/api/v1/public/r/khong-ton-tai").status_code == 404
    revoked = client.post(f"/api/v1/shares/{listed['id']}/revoke", headers=H).json()
    assert revoked["status"] == "revoked"
    gone = anon.get(f"/api/v1/public/r/{token}")
    assert gone.status_code == 410 and "thu hồi" in gone.json()["detail"]
    assert anon.get(f"/api/v1/public/r/{token}/pdf").status_code == 410

    from backend.api.models import AuditLog
    with app.state.db.session_factory() as db:
        actions = {a.action for a in db.query(AuditLog).all()}
    assert {"share.create", "share.view", "share.download", "share.revoke"} <= actions


def test_share_expiry_and_permissions(app):
    admin = login(app)
    rid = _report(admin)
    data = admin.post(f"/api/v1/reports/{rid}/shares", json={"expires_days": 1}, headers=H).json()
    token = data["url"].removeprefix("/r/")
    assert data["share"]["formats"] == ["pdf"]

    # Expire it in the DB.
    db = app.state.db.session_factory()
    from backend.api.models import ShareLink
    share = db.get(ShareLink, data["share"]["id"])
    share.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()
    db.close()
    assert TestClient(app).get(f"/api/v1/public/r/{token}").status_code == 410
    assert admin.get(f"/api/v1/reports/{rid}/shares").json()[0]["status"] == "expired"

    coach = _coach(app)  # other coach: cannot see or revoke the admin's client share
    assert coach.get(f"/api/v1/reports/{rid}/shares").status_code == 404
    assert coach.post(f"/api/v1/shares/{data['share']['id']}/revoke", headers=H).status_code == 404
    assert admin.post(f"/api/v1/reports/{rid}/shares", json={"expires_days": 0}, headers=H).status_code == 422
