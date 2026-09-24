"""/api/v1/settings/llm — AI provider configuration for the organization (plan P2-6, admin only).

The API key is write-only: stored Fernet-encrypted with the server secret and never returned
(only ``••••1234``). Without a stored key the HD_LLM_* environment variables still apply.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.reporting.llm_client import LLMError, ping_llm

from ..deps import client_ip, get_db, require_admin
from ..models import Organization, User
from ..schemas import LlmSettingsIn, LlmSettingsOut, LlmTestOut
from ..security import encrypt_value, mask_secret
from ..services import audit, env_llm_defaults, org_llm_config, stored_llm_key

from backend.reporting.llm_client import LLMConfig

router = APIRouter(prefix="/settings", tags=["settings"])


def _view(org: Organization, secret: str) -> LlmSettingsOut:
    stored = org.llm_settings or {}
    defaults = env_llm_defaults()
    key, unreadable = stored_llm_key(org, secret)
    env = LLMConfig.from_env()
    if key:
        source, hint = "database", mask_secret(key)
    elif env is not None:
        source, hint = "environment", mask_secret(env.api_key)
    else:
        source, hint = "none", ""
    updated_at = stored.get("updated_at")
    return LlmSettingsOut(
        base_url=stored.get("base_url") or defaults.base_url,
        model=stored.get("model") or defaults.model,
        temperature=float(stored["temperature"]) if stored.get("temperature") is not None else defaults.temperature,
        timeout=float(stored.get("timeout") or defaults.timeout),
        key_source=source, key_hint=hint, key_unreadable=unreadable,
        updated_by=stored.get("updated_by", ""),
        updated_at=datetime.fromisoformat(updated_at) if updated_at else None,
    )


@router.get("/llm", response_model=LlmSettingsOut)
def get_llm(request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)) -> LlmSettingsOut:
    return _view(db.get(Organization, user.org_id), request.app.state.secret_key)


@router.put("/llm", response_model=LlmSettingsOut)
def put_llm(payload: LlmSettingsIn, request: Request, user: User = Depends(require_admin),
            db: Session = Depends(get_db)) -> LlmSettingsOut:
    org = db.get(Organization, user.org_id)
    secret = request.app.state.secret_key
    stored = dict(org.llm_settings or {})
    stored.update(base_url=payload.base_url, model=payload.model, temperature=payload.temperature,
                  timeout=payload.timeout, updated_by=user.email,
                  updated_at=datetime.now(timezone.utc).isoformat())
    key_change = "unchanged"
    if payload.api_key is not None:
        if payload.api_key.strip():
            stored["api_key_enc"] = encrypt_value(secret, payload.api_key.strip())
            key_change = "set"
        else:
            stored.pop("api_key_enc", None)
            key_change = "cleared"
    org.llm_settings = stored  # new dict => SQLAlchemy sees the change
    audit(db, user, "settings.llm", "organization", org.id, ip=client_ip(request),
          base_url=payload.base_url, model=payload.model, key=key_change)  # never the key itself
    db.commit()
    return _view(org, secret)


@router.post("/llm/test", response_model=LlmTestOut)
def test_llm(request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)) -> LlmTestOut:
    """Send a 5-token request with the saved configuration."""
    config = org_llm_config(db, user.org_id, request.app.state.secret_key)
    if config is None:
        raise HTTPException(status_code=409, detail="Chưa có khóa API — hãy nhập khóa rồi lưu trước khi kiểm tra.")
    started = time.perf_counter()
    try:
        reply = ping_llm(config, transport=request.app.state.llm_transport)
        ok, detail = True, f"Kết nối thành công. Mô hình trả lời: “{reply[:60]}”"
    except LLMError as exc:
        ok, detail = False, f"Không kết nối được: {str(exc)[:300]}"
    latency = int((time.perf_counter() - started) * 1000)
    audit(db, user, "settings.llm_test", "organization", user.org_id, ip=client_ip(request), ok=ok)
    db.commit()
    return LlmTestOut(ok=ok, latency_ms=latency, model=config.model, detail=detail)
