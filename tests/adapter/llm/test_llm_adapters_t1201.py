"""
module_id: tests.adapter.llm.test_llm_adapters_t1201
file: tests/adapter/llm/test_llm_adapters_t1201.py
task_id: T-1201
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from adapter.llm.anthropic import (
    ANTHROPIC_DEFAULT_MODEL,
    AnthropicAdapterConfig,
    AnthropicLLMConstraintTranslator,
    build_anthropic_messages_request,
)
from adapter.llm.openai import (
    OPENAI_CONSTRAINT_TRANSLATOR_MODEL,
    CloudLLMOptInRequired,
    OpenAIAdapterConfig,
    OpenAILLMConstraintTranslator,
    build_openai_responses_request,
)
from app.constraint_translator import AdvisoryTextPolicy


def test_openai_adapter_requires_cloud_opt_in() -> None:
    with pytest.raises(CloudLLMOptInRequired):
        OpenAILLMConstraintTranslator(OpenAIAdapterConfig(api_key="test-key"))


def test_anthropic_adapter_requires_cloud_opt_in() -> None:
    with pytest.raises(CloudLLMOptInRequired):
        AnthropicLLMConstraintTranslator(AnthropicAdapterConfig(api_key="test-key"))


def test_openai_request_uses_responses_structured_outputs() -> None:
    request = build_openai_responses_request(
        "Express EGFP in E. coli.",
        AdvisoryTextPolicy().config.to_payload(),
    )

    assert request["model"] == OPENAI_CONSTRAINT_TRANSLATOR_MODEL
    assert request["text"]["format"]["type"] == "json_schema"  # type: ignore[index]
    assert request["text"]["format"]["strict"] is True  # type: ignore[index]
    assert request["reasoning"] == {"effort": "low"}


def test_openai_adapter_parses_injected_response() -> None:
    calls: list[tuple[str, Mapping[str, str], Mapping[str, object]]] = []

    def post(
        url: str,
        headers: Mapping[str, str],
        body: Mapping[str, object],
    ) -> Mapping[str, object]:
        calls.append((url, headers, body))
        return {
            "output_text": (
                '{"advisory_text":"Draft constraints require user confirmation.",'
                '"citation_ids":[],"constraints":[{"confidence":"0.8","evidence":"input",'
                '"field":"host","origin":"openai","value":"escherichia_coli"}],'
                '"requires_manual_review":false,"warnings":[]}'
            )
        }

    adapter = OpenAILLMConstraintTranslator(
        OpenAIAdapterConfig(api_key="test-key", cloud_opt_in=True),
        http_post=post,
    )

    payload = adapter.translate("Express EGFP in E. coli.", {})

    assert payload["constraints"][0]["field"] == "host"  # type: ignore[index]
    assert calls[0][1]["Authorization"] == "Bearer test-key"


def test_anthropic_request_uses_forced_tool_schema() -> None:
    request = build_anthropic_messages_request(
        "Express EGFP in E. coli.",
        AdvisoryTextPolicy().config.to_payload(),
    )

    assert request["model"] == ANTHROPIC_DEFAULT_MODEL
    assert request["tool_choice"] == {"name": "emit_constraint_translation", "type": "tool"}
    assert request["tools"][0]["input_schema"]["type"] == "object"  # type: ignore[index]


def test_anthropic_adapter_parses_injected_tool_use() -> None:
    def post(
        url: str,
        headers: Mapping[str, str],
        body: Mapping[str, object],
    ) -> Mapping[str, object]:
        del url, headers, body
        return {
            "content": [
                {
                    "input": {
                        "advisory_text": "Draft constraints require user confirmation.",
                        "citation_ids": [],
                        "constraints": [
                            {
                                "confidence": "0.8",
                                "evidence": "input",
                                "field": "cargo",
                                "origin": "anthropic",
                                "value": "egfp",
                            }
                        ],
                        "requires_manual_review": False,
                        "warnings": [],
                    },
                    "type": "tool_use",
                }
            ]
        }

    adapter = AnthropicLLMConstraintTranslator(
        AnthropicAdapterConfig(api_key="test-key", cloud_opt_in=True),
        http_post=post,
    )

    payload = adapter.translate("Express EGFP in E. coli.", {})

    assert payload["constraints"][0]["value"] == "egfp"  # type: ignore[index]
