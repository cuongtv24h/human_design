"""`/api/v1/settings/llm` — AI provider fallback chain for the organization (admin only).

Up to 3 providers (primary + 2 fallbacks). Each API key is write-only: stored
Fernet-encrypted with the server secret and never returned (only ``••••1234``).
Without any stored provider the ``HD_LLM_*`` environment variables still apply.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.reporting.llm_client import LLMConfig, LLMError, ping_llm

from ..deps import client_ip, get_db, require_admin
from ..models import Organization, User
from ..schemas import (
    LlmProviderOut, LlmSettingsIn, LlmSettingsOut, LlmTestIn, LlmTestItem, LlmTestOut, LlmUsageOut,
)
from ..security import encrypt_value, mask_secret
from ..services import (
    audit, decrypt_provider_key, env_llm_defaults, llm_usage_stats, org_llm_configs, stored_providers,
)

router = APIRouter(prefix="/settings", tags=["settings"])


def _num(value: Any, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _view(org: Organization, secret: str) -> LlmSettingsOut:
    stored = org.llm_settings or {}
    defaults = env_llm_defaults()
    providers: list[LlmProviderOut] = []
    for index, entry in enumerate(stored_providers(org)):
        key, unreadable = decrypt_provider_key(entry, secret)
        providers.append(LlmProviderOut(
            index=index,
            name=(entry.get("name") or f"Nhà cung cấp {index + 1}").strip(),
            base_url=entry.get("base_url") or defaults.base_url,
            model=((entry.get("model") or defaults.model) or "").strip(),
            temperature=_num(entry.get("temperature"), defaults.temperature),
            timeout=_num(entry.get("timeout"), defaults.timeout),
            enabled=entry.get("enabled", True) is not False,
            has_key=bool(key),
            key_hint=mask_secret(key) if key else "",
            key_unreadable=unreadable,
            input_price=max(0.0, _num(entry.get("input_price"), 0.0)),
            output_price=max(0.0, _num(entry.get("output_price"), 0.0)),
        ))
    if any(p.has_key for p in providers):
        source = "database"
    elif LLMConfig.from_env() is not None:
        source = "environment"
    else:
        source = "none"
    updated_at = stored.get("updated_at")
    return LlmSettingsOut(
        providers=providers,
        key_source=source,  # type: ignore[arg-type]
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
    existing = stored_providers(org)
    entries: list[dict[str, Any]] = []
    key_changes: list[str] = []
    for index, item in enumerate(payload.providers):
        old = existing[index] if index < len(existing) else {}
        encrypted = old.get("api_key_enc") or ""
        change = "unchanged"
        if item.api_key is not None:
            if item.api_key.strip():
                encrypted = encrypt_value(secret, item.api_key.strip())
                change = "set"
            else:
                encrypted = ""
                change = "cleared"
        entries.append({
            "name": item.name,
            "base_url": item.base_url,
            "model": item.model,
            "temperature": item.temperature,
            "timeout": item.timeout,
            "api_key_enc": encrypted,
            "enabled": item.enabled,
            "input_price": item.input_price,
            "output_price": item.output_price,
        })
        key_changes.append(f"{item.name}={change}")
    org.llm_settings = {"providers": entries, "updated_by": user.email,  # new dict => SQLAlchemy sees it
                        "updated_at": datetime.now(timezone.utc).isoformat()}
    audit(db, user, "settings.llm", "organization", org.id, ip=client_ip(request),
          providers=[e["name"] for e in entries], key=key_changes)  # never the keys themselves
    db.commit()
    return _view(org, secret)


@router.post("/llm/test", response_model=LlmTestOut)
def test_llm(request: Request, payload: LlmTestIn | None = None, user: User = Depends(require_admin),
             db: Session = Depends(get_db)) -> LlmTestOut:
    """Send a 5-token request with the saved configuration (one or every provider)."""
    configs = org_llm_configs(db, user.org_id, request.app.state.secret_key)
    wanted = (payload.provider_index if payload else None)
    if wanted is not None:
        if wanted >= len(configs):
            raise HTTPException(status_code=404, detail="Không có nhà cung cấp này (có thể chưa có khóa hoặc đã tắt).")
        targets = [(wanted, configs[wanted])]
    else:
        targets = list(enumerate(configs))
    if not targets:
        raise HTTPException(status_code=409, detail="Chưa có khóa API — hãy nhập khóa rồi lưu trước khi kiểm tra.")
    results: list[LlmTestItem] = []
    for index, config in targets:
        started = time.perf_counter()
        try:
            reply = ping_llm(config, transport=request.app.state.llm_transport)
            ok, detail = True, f"Kết nối thành công. Mô hình trả lời: “{reply[:60]}”"
        except LLMError as exc:
            ok, detail = False, f"Không kết nối được: {str(exc)[:300]}"
        latency = int((time.perf_counter() - started) * 1000)
        results.append(LlmTestItem(index=index, name=config.name or f"Nhà cung cấp {index + 1}",
                                   model=config.model, ok=ok, latency_ms=latency, detail=detail))
    audit(db, user, "settings.llm_test", "organization", user.org_id, ip=client_ip(request),
          ok=all(r.ok for r in results), tested=[r.name for r in results])
    db.commit()
    return LlmTestOut(results=results)


@router.get("/llm/usage", response_model=LlmUsageOut)
def get_llm_usage(days: int = Query(30, ge=1, le=365), user: User = Depends(require_admin),
                  db: Session = Depends(get_db)) -> LlmUsageOut:
    """Token + cost statistics for the fallback chain (admin only)."""
    return LlmUsageOut.model_validate(llm_usage_stats(db, user.org_id, days))
