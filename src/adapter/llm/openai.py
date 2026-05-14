"""
module_id: adapter.llm.openai
file: src/adapter/llm/openai.py
task_id: T-1201

Opt-in OpenAI Responses API adapter for structured constraint translation.
"""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from app.constraint_translator import TRANSLATION_JSON_SCHEMA, LLMTranslationUnavailable

OPENAI_CONSTRAINT_TRANSLATOR_MODEL = "gpt-5.5"
OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"

HttpPost = Callable[[str, Mapping[str, str], Mapping[str, object]], Mapping[str, object]]


class CloudLLMOptInRequired(PermissionError):
    """Raised when a cloud adapter is constructed without explicit opt-in."""


@dataclass(frozen=True, slots=True)
class OpenAIAdapterConfig:
    api_key: str
    model: str = OPENAI_CONSTRAINT_TRANSLATOR_MODEL
    endpoint: str = OPENAI_RESPONSES_ENDPOINT
    cloud_opt_in: bool = False
    timeout_seconds: float = 20.0


class OpenAILLMConstraintTranslator:
    name = "openai-responses-constraint-translator"
    version = "1"

    def __init__(
        self,
        config: OpenAIAdapterConfig,
        *,
        http_post: HttpPost | None = None,
    ) -> None:
        if not config.cloud_opt_in:
            raise CloudLLMOptInRequired("OpenAI adapter requires explicit per-session opt-in")
        if not config.api_key:
            raise ValueError("OpenAI API key cannot be empty")
        self._config = config
        self._http_post = http_post or _urllib_post

    @property
    def model_identifier(self) -> str:
        return f"openai:{self._config.model}"

    def translate(self, free_text: str, policy: Mapping[str, object]) -> dict[str, object]:
        response = self._http_post(
            self._config.endpoint,
            {
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            build_openai_responses_request(
                free_text,
                policy,
                model=self._config.model,
            ),
        )
        return _parse_openai_response(response)


def build_openai_responses_request(
    free_text: str,
    policy: Mapping[str, object],
    *,
    model: str = OPENAI_CONSTRAINT_TRANSLATOR_MODEL,
) -> dict[str, object]:
    return {
        "input": [
            {
                "content": _system_prompt(policy),
                "role": "system",
            },
            {
                "content": free_text,
                "role": "user",
            },
        ],
        "model": model,
        "reasoning": {"effort": "low"},
        "text": {
            "format": {
                "name": "constraint_translation",
                "schema": TRANSLATION_JSON_SCHEMA,
                "strict": True,
                "type": "json_schema",
            },
            "verbosity": "low",
        },
    }


def _system_prompt(policy: Mapping[str, object]) -> str:
    allowed_fields = ", ".join(_string_list(policy.get("allowed_fields")))
    return (
        "Translate user free text into advisory structured constraints only. "
        "Return JSON matching the schema. Do not provide operational protocol steps, "
        "experimental conditions, sequence assertions, or citations. "
        f"Allowed fields: {allowed_fields}."
    )


def _parse_openai_response(response: Mapping[str, object]) -> dict[str, object]:
    raw_text = response.get("output_text")
    if isinstance(raw_text, str):
        return _json_object(raw_text)
    for output in _list(response.get("output"), "output"):
        if not isinstance(output, Mapping):
            continue
        for item in _list(output.get("content"), "content"):
            if not isinstance(item, Mapping):
                continue
            if item.get("type") == "refusal":
                raise LLMTranslationUnavailable(str(item.get("refusal", "OpenAI refusal")))
            text = item.get("text")
            if isinstance(text, str):
                return _json_object(text)
    raise LLMTranslationUnavailable("OpenAI response did not contain structured output text")


def _string_list(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError("allowed_fields must be a list")
    return [str(item) for item in value]


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
        raise LLMTranslationUnavailable("OpenAI response was not a JSON object")
    return dict(decoded)


__all__ = [
    "OPENAI_CONSTRAINT_TRANSLATOR_MODEL",
    "OPENAI_RESPONSES_ENDPOINT",
    "CloudLLMOptInRequired",
    "OpenAIAdapterConfig",
    "OpenAILLMConstraintTranslator",
    "build_openai_responses_request",
]
