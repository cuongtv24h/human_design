"""Client LLM cho content_mode="llm" — chuẩn OpenAI-compatible, chỉ dùng stdlib.

Cấu hình qua biến môi trường (không bao giờ hard-code key):

- ``HD_LLM_API_KEY``  (fallback ``OPENAI_API_KEY``) — bắt buộc để bật LLM.
- ``HD_LLM_BASE_URL`` — mặc định ``https://api.openai.com/v1``; trỏ sang bất kỳ
  endpoint tương thích OpenAI (OpenRouter, Azure proxy, vLLM, Ollama...).
- ``HD_LLM_MODEL``    — mặc định ``gpt-4o-mini``.
- ``HD_LLM_TIMEOUT``  — giây, mặc định 120.
- ``HD_LLM_TEMPERATURE`` — mặc định 0.6 (đủ mềm để văn phong ấm, vẫn bám dữ liệu).

``transport`` cho phép test/tích hợp tiêm hàm gửi request thay cho HTTP thật.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Mapping

Transport = Callable[[str, Mapping[str, str], dict[str, Any], float], dict[str, Any]]

SYSTEM_MESSAGE = (
    "Bạn là biên tập viên báo cáo Human Design tiếng Việt. Làm đúng vai trò và "
    "quy tắc trong brief. Chỉ trả về MỘT object JSON hợp lệ dạng "
    '{"<section_id>": "<markdown>"} — không thêm lời dẫn ngoài JSON.'
)


class LLMError(RuntimeError):
    """Raised when the LLM is unavailable or returns unusable output."""


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    timeout: float = 120.0
    temperature: float = 0.6

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "LLMConfig | None":
        """Build config from env; ``None`` when no API key is configured."""
        source = os.environ if env is None else env
        api_key = source.get("HD_LLM_API_KEY") or source.get("OPENAI_API_KEY") or ""
        if not api_key.strip():
            return None
        return cls(
            api_key=api_key.strip(),
            base_url=(source.get("HD_LLM_BASE_URL") or cls.base_url).rstrip("/"),
            model=source.get("HD_LLM_MODEL") or cls.model,
            timeout=float(source.get("HD_LLM_TIMEOUT") or cls.timeout),
            temperature=float(source.get("HD_LLM_TEMPERATURE") or cls.temperature),
        )


def _http_transport(
    url: str, headers: Mapping[str, str], payload: dict[str, Any], timeout: float
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=dict(headers),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise LLMError(f"LLM HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise LLMError(f"Không kết nối được LLM: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LLMError("LLM trả về dữ liệu không phải JSON") from exc


def parse_llm_json(text: str) -> dict[str, str]:
    """Extract the ``{section_id: markdown}`` object from an LLM reply.

    Accepts bare JSON, fenced ```json blocks, or JSON surrounded by prose.
    """
    if not text or not text.strip():
        raise LLMError("LLM trả về nội dung rỗng")
    candidates = [text.strip()]
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        candidates.insert(0, fenced.group(1))
    start, end = text.find("{"), text.rfind("}")
    if 0 <= start < end:
        candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            drafts = {str(k): v for k, v in data.items() if isinstance(v, str) and v.strip()}
            if drafts:
                return drafts
    raise LLMError("Không đọc được JSON {section_id: markdown} từ phản hồi LLM")


def call_llm(
    brief: str,
    config: LLMConfig,
    transport: Transport | None = None,
) -> dict[str, str]:
    """Send the brief to the LLM and return parsed section drafts."""
    payload: dict[str, Any] = {
        "model": config.model,
        "temperature": config.temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": brief},
        ],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.api_key}",
    }
    response = (transport or _http_transport)(
        f"{config.base_url}/chat/completions", headers, payload, config.timeout
    )
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Phản hồi LLM thiếu choices[0].message.content") from exc
    return parse_llm_json(content or "")


def ping_llm(config: LLMConfig, transport: Transport | None = None) -> str:
    """Tiny request to verify key / URL / model ("Kiểm tra kết nối"). Returns the reply text."""
    payload: dict[str, Any] = {
        "model": config.model,
        "max_tokens": 5,
        "temperature": 0,
        "messages": [{"role": "user", "content": "Trả lời đúng một từ: OK"}],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {config.api_key}"}
    response = (transport or _http_transport)(
        f"{config.base_url}/chat/completions", headers, payload, min(config.timeout, 30.0)
    )
    try:
        return str(response["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Phản hồi LLM thiếu choices[0].message.content") from exc


__all__ = ["LLMConfig", "LLMError", "Transport", "call_llm", "parse_llm_json", "ping_llm"]
