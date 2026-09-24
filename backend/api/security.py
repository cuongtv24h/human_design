"""Passwords (Argon2), opaque session tokens (only SHA-256 stored), CSRF header."""

from __future__ import annotations

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

SESSION_COOKIE = "hd_session"
# Mutating requests must carry this header. Browsers cannot add custom headers
# cross-site without a CORS preflight (which is not granted), so this blocks CSRF.
CSRF_HEADER = "X-HD-Request"

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def new_session_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hash_token(token)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# --- server secret, signed links, encrypted settings -------------------------

import base64  # noqa: E402
import hmac  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

from cryptography.fernet import Fernet, InvalidToken  # noqa: E402


def resolve_secret_key(configured: str, fallback_file: Path) -> str:
    """``HD_SECRET_KEY`` if set; otherwise a random key persisted (0600) next to the data.

    Changing the key invalidates signed links and makes stored LLM keys unreadable.
    """
    if configured.strip():
        return configured.strip()
    if fallback_file.is_file():
        return fallback_file.read_text(encoding="utf-8").strip()
    fallback_file.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_urlsafe(48)
    fd = os.open(fallback_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(key)
    return key


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _mac(secret: str, purpose: str, body: str) -> str:
    return _b64(hmac.new(secret.encode(), f"{purpose}.{body}".encode(), hashlib.sha256).digest()[:24])


def sign_token(secret: str, purpose: str, payload: dict, ttl_seconds: int, now: float | None = None) -> tuple[str, int]:
    """Stateless, tamper-proof, expiring token (HMAC-SHA256). Returns ``(token, expires_epoch)``."""
    expires = int((now or time.time()) + ttl_seconds)
    body = _b64(json.dumps({**payload, "exp": expires}, separators=(",", ":")).encode())
    return f"{body}.{_mac(secret, purpose, body)}", expires


def verify_token(secret: str, purpose: str, token: str, now: float | None = None) -> dict | None:
    """Payload of a valid, unexpired token for ``purpose``; ``None`` otherwise."""
    try:
        body, mac = token.split(".", 1)
        if not hmac.compare_digest(mac, _mac(secret, purpose, body)):
            return None
        payload = json.loads(_unb64(body))
    except (ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or int(payload.get("exp", 0)) < (now or time.time()):
        return None
    return payload


def _fernet(secret: str) -> Fernet:
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(f"hd-settings:{secret}".encode()).digest()))


def encrypt_value(secret: str, value: str) -> str:
    return _fernet(secret).encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_value(secret: str, token: str) -> str | None:
    """``None`` when the value was encrypted with another server secret."""
    try:
        return _fernet(secret).decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError):
        return None


def mask_secret(value: str) -> str:
    return "••••" + value[-4:] if len(value) >= 8 else "••••"
