"""GPT bridge (mcp/openapi_server.py): Bearer HD_GPT_TOKEN + fail-closed ở production."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fastapi.testclient import TestClient  # noqa: E402

import openapi_server  # noqa: E402


def test_dev_without_token_is_open(monkeypatch):
    """Môi trường dev (mặc định) chưa set token → bridge vẫn mở để test."""
    monkeypatch.delenv("HD_GPT_TOKEN", raising=False)
    monkeypatch.setenv("HD_ENV", "development")
    assert TestClient(openapi_server.app).get("/health").status_code == 200


def test_token_required_when_configured(monkeypatch):
    """Khi HD_GPT_TOKEN được set → 401 nếu thiếu/sai, 200 nếu đúng Bearer."""
    monkeypatch.setenv("HD_GPT_TOKEN", "sekrit-token-123")
    client = TestClient(openapi_server.app)
    assert client.get("/health").status_code == 401
    assert client.get("/health", headers={"Authorization": "Bearer sai"}).status_code == 401
    ok = client.get("/health", headers={"Authorization": "Bearer sekrit-token-123"})
    assert ok.status_code == 200


def test_production_without_token_fails_closed(monkeypatch):
    """HD_ENV=production mà thiếu HD_GPT_TOKEN → 503 mọi request (không mở toang)."""
    monkeypatch.delenv("HD_GPT_TOKEN", raising=False)
    monkeypatch.setenv("HD_ENV", "production")
    response = TestClient(openapi_server.app).get("/health")
    assert response.status_code == 503 and "HD_GPT_TOKEN" in response.json()["detail"]


def test_no_wildcard_cors_by_default(monkeypatch):
    """CORS mặc định tắt — không có header Access-Control-Allow-Origin dù gửi Origin."""
    monkeypatch.delenv("HD_GPT_TOKEN", raising=False)
    monkeypatch.delenv("HD_GPT_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("HD_ENV", "development")
    response = TestClient(openapi_server.app).get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers
