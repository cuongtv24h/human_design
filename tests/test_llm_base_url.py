"""Chống SSRF cho base_url LLM: https bắt buộc, chặn IP nội bộ/link-local, whitelist có kiểm soát."""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from test_api_v1 import H, app, login  # noqa: F401,E402  (fixture re-export)

from backend.reporting.llm_client import LLMError, _http_transport, validate_llm_base_url  # noqa: E402

EMPTY = frozenset()


# --- unit: validate_llm_base_url ----------------------------------------------

def test_public_https_allowed():
    assert validate_llm_base_url("https://api.openai.com/v1", EMPTY) == "https://api.openai.com/v1"


def test_public_http_rejected():
    with pytest.raises(ValueError, match="https"):
        validate_llm_base_url("http://api.openai.com/v1", EMPTY)


@pytest.mark.parametrize("url", [
    "http://10.0.0.5:8080/v1",        # RFC1918
    "https://192.168.1.50/v1",        # RFC1918 kể cả https
    "https://127.0.0.1:8001/v1",      # loopback
    "http://localhost:11434/v1",      # hostname loopback
    "https://[::1]/v1",               # IPv6 loopback
    "http://0.0.0.0/v1",              # unspecified
])
def test_private_and_loopback_rejected(url):
    with pytest.raises(ValueError):
        validate_llm_base_url(url, EMPTY)


def test_link_local_blocked_even_when_allowlisted():
    """169.254.x = metadata đám mây — không bao giờ được whitelist."""
    with pytest.raises(ValueError, match="link-local"):
        validate_llm_base_url("http://169.254.169.254/latest", frozenset({"169.254.169.254"}))


def test_allowlist_admits_local_router_with_http():
    """9router/Ollama trên LAN: nằm trong whitelist thì http:// IP nội bộ được qua."""
    allow = frozenset({"192.168.1.50:3456"})
    assert validate_llm_base_url("http://192.168.1.50:3456/v1", allow) == "http://192.168.1.50:3456/v1"
    with pytest.raises(ValueError):  # sai cổng → không nằm trong whitelist
        validate_llm_base_url("http://192.168.1.50:9999/v1", allow)


def test_allowlist_from_env(monkeypatch):
    monkeypatch.setenv("HD_LLM_ALLOWED_PRIVATE_HOSTS", " localhost:11434 , 10.1.2.3 ")
    assert validate_llm_base_url("http://localhost:11434/v1") == "http://localhost:11434/v1"
    assert validate_llm_base_url("http://10.1.2.3/v1") == "http://10.1.2.3/v1"
    with pytest.raises(ValueError):
        validate_llm_base_url("http://10.9.9.9/v1")  # không nằm trong whitelist


# --- lớp phòng thủ cuối: _http_transport không được mở socket tới URL bị chặn --

def test_transport_refuses_blocked_url_without_network():
    with pytest.raises(LLMError, match="SSRF"):
        _http_transport("http://169.254.169.254/latest/meta-data", {}, {}, 1.0)


# --- API: PUT /settings/llm -----------------------------------------------------

def _payload(base_url: str) -> dict:
    return {"providers": [{"name": "NCC test", "base_url": base_url, "model": "gpt-4o-mini",
                           "temperature": 0.6, "timeout": 60}]}


def test_put_llm_rejects_private_base_url(app):
    admin = login(app)
    bad = admin.put("/api/v1/settings/llm", json=_payload("http://10.0.0.5:8080/v1"), headers=H)
    assert bad.status_code == 422
    # Lỗi trỏ đúng trường + hướng dẫn cách bật (allowlist) cho admin.
    assert "base_url" in bad.text and "HD_LLM_ALLOWED_PRIVATE_HOSTS" in bad.text
    # Thử cả https:// tới IP nội bộ (vượt qua nhánh scheme) — vẫn bị chặn.
    bad2 = admin.put("/api/v1/settings/llm", json=_payload("https://10.0.0.5/v1"), headers=H)
    assert bad2.status_code == 422 and "IP nội bộ" in bad2.text


def test_put_llm_accepts_private_when_allowlisted(app, monkeypatch):
    monkeypatch.setenv("HD_LLM_ALLOWED_PRIVATE_HOSTS", "10.0.0.5:8080")
    admin = login(app)
    ok = admin.put("/api/v1/settings/llm", json=_payload("http://10.0.0.5:8080/v1"), headers=H)
    assert ok.status_code == 200
    assert ok.json()["providers"][0]["base_url"] == "http://10.0.0.5:8080/v1"
