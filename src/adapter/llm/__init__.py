"""
module_id: adapter.llm
file: src/adapter/llm/__init__.py
task_id: T-1201

LLM adapters for advisory constraint translation.
"""

from __future__ import annotations

from adapter.llm.anthropic import (
    ANTHROPIC_DEFAULT_MODEL,
    ANTHROPIC_MESSAGES_ENDPOINT,
    ANTHROPIC_VERSION,
    AnthropicAdapterConfig,
    AnthropicLLMConstraintTranslator,
)
from adapter.llm.local import LocalHeuristicLLMConstraintTranslator
from adapter.llm.openai import (
    OPENAI_CONSTRAINT_TRANSLATOR_MODEL,
    OPENAI_RESPONSES_ENDPOINT,
    CloudLLMOptInRequired,
    OpenAIAdapterConfig,
    OpenAILLMConstraintTranslator,
)

__all__ = [
    "ANTHROPIC_DEFAULT_MODEL",
    "ANTHROPIC_MESSAGES_ENDPOINT",
    "ANTHROPIC_VERSION",
    "OPENAI_CONSTRAINT_TRANSLATOR_MODEL",
    "OPENAI_RESPONSES_ENDPOINT",
    "AnthropicAdapterConfig",
    "AnthropicLLMConstraintTranslator",
    "CloudLLMOptInRequired",
    "LocalHeuristicLLMConstraintTranslator",
    "OpenAIAdapterConfig",
    "OpenAILLMConstraintTranslator",
]
