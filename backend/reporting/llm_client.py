"""Client LLM cho content_mode="llm" — chuẩn OpenAI-compatible, chỉ dùng stdlib.

Cấu hình qua biến môi trường (không bao giờ hard-code key):

- ``HD_LLM_API_KEY``  (fallback ``OPENAI_API_KEY``) — bắt buộc để bật LLM.
- ``HD_LLM_BASE_URL`` — mặc định ``https://api.openai.com/v1``; trỏ sang bất kỳ
  endpoint tương thích OpenAI (OpenRouter, Azure proxy, vLLM, Ollama...).
- ``HD_LLM_MODEL``    — mặc định ``gpt-4o-mini``.
- ``HD_LLM_TIMEOUT``  — giây, mặc định 120.
- ``HD_LLM_TEMPERATURE`` — mặc định 0.6 (đủ mềm để văn phong ấm, vẫn bám dữ liệu).
- ``HD_LLM_INPUT_PRICE`` / ``HD_LLM_OUTPUT_PRICE`` — USD / 1M token (tùy chọn,
  để tính chi phí; 0 = chưa biết giá).

Chuỗi fallback (nhiều nhà cung cấp) và thống kê chi phí nằm ở
``backend.reporting.service`` + ``backend.api.services``; module này chỉ lo
một lần gọi HTTP và đọc ``usage`` (số token) từ phản hồi.

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
    # Display name set by the admin ("OpenAI chính"); "" = derive from the model.
    name: str = ""
    # USD per 1M tokens (0 = unknown → cost is not computed).
    input_price: float = 0.0
    output_price: float = 0.0

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "LLMConfig | None":
        """Build config from env; ``None`` when no API key is configured."""
        source = os.environ if env is None else env
        api_key = source.get("HD_LLM_API_KEY") or source.get("OPENAI_API_KEY") or ""
        if not api_key.strip():
            return None

        def _price(key: str) -> float:
            try:
                return max(0.0, float(source.get(key) or 0.0))
            except (TypeError, ValueError):
                return 0.0

        return cls(
            api_key=api_key.strip(),
            base_url=(source.get("HD_LLM_BASE_URL") or cls.base_url).rstrip("/"),
            model=source.get("HD_LLM_MODEL") or cls.model,
            timeout=float(source.get("HD_LLM_TIMEOUT") or cls.timeout),
            temperature=float(source.get("HD_LLM_TEMPERATURE") or cls.temperature),
            name="Máy chủ",
            input_price=_price("HD_LLM_INPUT_PRICE"),
            output_price=_price("HD_LLM_OUTPUT_PRICE"),
        )


def display_provider(config: LLMConfig) -> str:
    """Short label for the UI: ``"<name> · <model>"`` (or just the model)."""
    return f"{config.name} · {config.model}" if config.name else config.model


@dataclass(frozen=True)
class LLMUsage:
    """Token counts reported by one ``chat/completions`` call (0 when unknown)."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""

    @classmethod
    def from_response(cls, response: Mapping[str, Any], fallback_model: str = "") -> "LLMUsage":
        usage = response.get("usage") or {}
        if not isinstance(usage, Mapping):
            usage = {}
        try:
            prompt = int(usage.get("prompt_tokens") or 0)
        except (TypeError, ValueError):
            prompt = 0
        try:
            completion = int(usage.get("completion_tokens") or 0)
        except (TypeError, ValueError):
            completion = 0
        model = str(response.get("model") or fallback_model or "")
        return cls(prompt_tokens=max(0, prompt), completion_tokens=max(0, completion), model=model)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def estimate_cost(usage: LLMUsage, input_price: float, output_price: float) -> float | None:
    """USD cost of one call; ``None`` when the provider has no known prices."""
    if input_price <= 0 and output_price <= 0:
        return None
    return usage.prompt_tokens / 1_000_000 * max(0.0, input_price) + \
        usage.completion_tokens / 1_000_000 * max(0.0, output_price)


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


def call_llm_with_usage(
    brief: str,
    config: LLMConfig,
    transport: Transport | None = None,
) -> tuple[dict[str, str], LLMUsage]:
    """Send the brief to the LLM; return ``(parsed section drafts, token usage)``."""
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
    return parse_llm_json(content or ""), LLMUsage.from_response(response, config.model)


def call_llm(
    brief: str,
    config: LLMConfig,
    transport: Transport | None = None,
) -> dict[str, str]:
    """Send the brief to the LLM and return parsed section drafts."""
    drafts, _ = call_llm_with_usage(brief, config, transport=transport)
    return drafts


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


class _StreamOptionsRejected(Exception):
    """The provider refused ``stream_options`` — retry without it."""


def _http_sse(url: str, headers: Mapping[str, str], payload: dict[str, Any], timeout: float,
              fallback_model: str):
    """Yield ``("delta", text)`` / ``("usage", LLMUsage)`` from a real SSE stream."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=dict(headers),
        method="POST",
    )
    try:
        response = urllib.request.urlopen(request, timeout=timeout)  # noqa: S310
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        if exc.code == 400 and "stream_options" in payload and "stream" in detail.lower():
            raise _StreamOptionsRejected(detail) from exc
        raise LLMError(f"LLM HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise LLMError(f"Không kết nối được LLM: {exc}") from exc
    usage = LLMUsage()
    try:
        with response:
            for raw_line in response:
                line = raw_line.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                for choice in obj.get("choices") or []:
                    delta = choice.get("delta") or {}
                    if delta.get("content"):
                        yield ("delta", str(delta["content"]))
                if obj.get("usage"):
                    usage = LLMUsage.from_response(obj, fallback_model)
    except (TimeoutError, OSError) as exc:
        raise LLMError(f"Đứt kết nối khi stream LLM: {exc}") from exc
    yield ("usage", usage)


def stream_chat_completion(
    messages: list[dict[str, str]],
    config: LLMConfig,
    transport: Transport | None = None,
    extra: Mapping[str, Any] | None = None,
):
    """Yield ``("delta", text)`` chunks then a final ``("usage", LLMUsage)``.

    With an injected dict ``transport`` (tests) the full reply is emulated as
    small chunks; otherwise a real ``stream: true`` SSE request is used.
    """
    payload: dict[str, Any] = {"model": config.model, "temperature": config.temperature,
                               "messages": messages, **(extra or {})}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {config.api_key}"}
    url = f"{config.base_url}/chat/completions"
    if transport is not None:
        response = transport(url, headers, payload, config.timeout)
        try:
            content = response["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("Phản hồi LLM thiếu choices[0].message.content") from exc
        for i in range(0, len(content), 24):
            yield ("delta", content[i:i + 24])
        yield ("usage", LLMUsage.from_response(response, config.model))
        return
    payload["stream"] = True
    payload["stream_options"] = {"include_usage": True}
    try:
        yield from _http_sse(url, headers, payload, config.timeout, config.model)
    except _StreamOptionsRejected:
        payload.pop("stream_options", None)
        yield from _http_sse(url, headers, payload, config.timeout, config.model)


__all__ = ["LLMConfig", "LLMError", "LLMUsage", "Transport", "call_llm", "call_llm_with_usage",
           "display_provider", "estimate_cost", "parse_llm_json", "ping_llm", "stream_chat_completion"]
