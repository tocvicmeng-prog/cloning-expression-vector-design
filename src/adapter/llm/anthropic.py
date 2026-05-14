"""
module_id: adapter.llm.anthropic
file: src/adapter/llm/anthropic.py
task_id: T-1201

Opt-in Anthropic Messages API adapter for structured constraint translation.
"""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from adapter.llm.openai import CloudLLMOptInRequired
from app.constraint_translator import TRANSLATION_JSON_SCHEMA, LLMTranslationUnavailable

ANTHROPIC_MESSAGES_ENDPOINT = "https://api.anthropic.com/v1/messages"
ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_VERSION = "2023-06-01"

HttpPost = Callable[[str, Mapping[str, str], Mapping[str, object]], Mapping[str, object]]


@dataclass(frozen=True, slots=True)
class AnthropicAdapterConfig:
    api_key: str
    model: str = ANTHROPIC_DEFAULT_MODEL
    endpoint: str = ANTHROPIC_MESSAGES_ENDPOINT
    anthropic_version: str = ANTHROPIC_VERSION
    cloud_opt_in: bool = False


class AnthropicLLMConstraintTranslator:
    name = "anthropic-messages-constraint-translator"
    version = "1"

    def __init__(
        self,
        config: AnthropicAdapterConfig,
        *,
        http_post: HttpPost | None = None,
    ) -> None:
        if not config.cloud_opt_in:
            raise CloudLLMOptInRequired("Anthropic adapter requires explicit per-session opt-in")
        if not config.api_key:
            raise ValueError("Anthropic API key cannot be empty")
        self._config = config
        self._http_post = http_post or _urllib_post

    @property
    def model_identifier(self) -> str:
        return f"anthropic:{self._config.model}"

    def translate(self, free_text: str, policy: Mapping[str, object]) -> dict[str, object]:
        response = self._http_post(
            self._config.endpoint,
            {
                "anthropic-version": self._config.anthropic_version,
                "content-type": "application/json",
                "x-api-key": self._config.api_key,
            },
            build_anthropic_messages_request(
                free_text,
                policy,
                model=self._config.model,
            ),
        )
        return _parse_anthropic_response(response)


def build_anthropic_messages_request(
    free_text: str,
    policy: Mapping[str, object],
    *,
    model: str = ANTHROPIC_DEFAULT_MODEL,
) -> dict[str, object]:
    return {
        "max_tokens": 1200,
        "messages": [
            {
                "content": free_text,
                "role": "user",
            }
        ],
        "model": model,
        "system": (
            "Translate free text into advisory structured constraints only. "
            "Return one JSON object matching the schema. "
            "Do not include operational protocol details, sequence assertions, or citations. "
            f"Policy: {json.dumps(dict(policy), sort_keys=True, separators=(',', ':'))}"
        ),
        "tool_choice": {"name": "emit_constraint_translation", "type": "tool"},
        "tools": [
            {
                "description": "Emit structured advisory constraints for user confirmation.",
                "input_schema": TRANSLATION_JSON_SCHEMA,
                "name": "emit_constraint_translation",
            }
        ],
    }


def _parse_anthropic_response(response: Mapping[str, object]) -> dict[str, object]:
    for item in _list(response.get("content"), "content"):
        if not isinstance(item, Mapping):
            continue
        if item.get("type") == "tool_use" and isinstance(item.get("input"), Mapping):
            return dict(item["input"])
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            return _json_object(str(item["text"]))
    raise LLMTranslationUnavailable("Anthropic response did not contain structured output")


def _json_object(raw_text: str) -> dict[str, object]:
    decoded = json.loads(raw_text)
    if not isinstance(decoded, dict):
        raise LLMTranslationUnavailable("LLM response JSON was not an object")
    return dict(decoded)


def _list(value: object, field_name: str) -> list[object]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise LLMTranslationUnavailable(f"{field_name} must be a list")
    return value


def _urllib_post(
    url: str,
    headers: Mapping[str, str],
    body: Mapping[str, object],
) -> Mapping[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        headers=dict(headers),
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20.0) as response:
        decoded = json.loads(response.read().decode("utf-8"))
    if not isinstance(decoded, dict):
        raise LLMTranslationUnavailable("Anthropic response was not a JSON object")
    return dict(decoded)


__all__ = [
    "ANTHROPIC_DEFAULT_MODEL",
    "ANTHROPIC_MESSAGES_ENDPOINT",
    "ANTHROPIC_VERSION",
    "AnthropicAdapterConfig",
    "AnthropicLLMConstraintTranslator",
    "build_anthropic_messages_request",
]
