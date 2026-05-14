"""
module_id: app.constraint_translator
file: src/app/constraint_translator.py
task_id: T-1201

Free-text constraint translation with advisory-only LLM output policy.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Self

from domain.events.base import CanonicalPayload


class ConstraintTranslatorError(ValueError):
    """Base class for constraint-translator failures."""


class AdvisoryTextPolicyViolation(ConstraintTranslatorError):
    """Raised when LLM output violates the advisory text policy."""


class LLMTranslationUnavailable(ConstraintTranslatorError):
    """Raised by LLM adapters when translation cannot be produced safely."""


class ConstraintField(Enum):
    OBJECTIVE = "objective"
    HOST = "host"
    CARGO = "cargo"
    EXPRESSION = "expression"
    TAG = "tag"
    CLONING_CHEMISTRY = "cloning_chemistry"
    BIOSAFETY_TIER = "biosafety_tier"
    NOTES = "notes"


@dataclass(frozen=True, slots=True)
class StructuredConstraint:
    field: ConstraintField
    value: str
    confidence: str
    evidence: str
    origin: str = "llm_translation"

    def __post_init__(self) -> None:
        _require_non_empty(self.value, "constraint value")
        _require_confidence(self.confidence)
        _require_non_empty(self.evidence, "constraint evidence")
        _require_non_empty(self.origin, "constraint origin")

    def to_payload(self) -> dict[str, str]:
        return {
            "confidence": self.confidence,
            "evidence": self.evidence,
            "field": self.field.value,
            "origin": self.origin,
            "value": self.value,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        return cls(
            field=ConstraintField(_expect_str(payload, "field")),
            value=_expect_str(payload, "value"),
            confidence=_expect_str(payload, "confidence"),
            evidence=_expect_str(payload, "evidence"),
            origin=_expect_str(payload, "origin", default="llm_translation"),
        )


@dataclass(frozen=True, slots=True)
class TranslationProposal:
    proposal_id: str
    source_text: str
    advisory_text: str
    constraints: tuple[StructuredConstraint, ...]
    warnings: tuple[str, ...]
    citation_ids: tuple[str, ...]
    model_identifier: str
    prompt_template_version: str
    schema_version: str
    requires_manual_review: bool = False

    def __post_init__(self) -> None:
        _require_non_empty(self.proposal_id, "proposal_id")
        _require_non_empty(self.source_text, "source_text")
        _require_non_empty(self.advisory_text, "advisory_text")
        _require_non_empty(self.model_identifier, "model_identifier")
        _require_non_empty(self.prompt_template_version, "prompt_template_version")
        _require_non_empty(self.schema_version, "schema_version")

    def to_payload(self) -> dict[str, object]:
        return {
            "advisory_text": self.advisory_text,
            "citation_ids": list(self.citation_ids),
            "constraints": [constraint.to_payload() for constraint in self.constraints],
            "model_identifier": self.model_identifier,
            "prompt_template_version": self.prompt_template_version,
            "proposal_id": self.proposal_id,
            "requires_manual_review": self.requires_manual_review,
            "schema_version": self.schema_version,
            "source_text": self.source_text,
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_llm_payload(
        cls,
        payload: Mapping[str, object],
        *,
        proposal_id: str,
        source_text: str,
        model_identifier: str,
        prompt_template_version: str,
        schema_version: str,
    ) -> Self:
        return cls(
            proposal_id=proposal_id,
            source_text=source_text,
            advisory_text=_expect_str(payload, "advisory_text"),
            constraints=tuple(
                StructuredConstraint.from_payload(item)
                for item in _expect_mapping_list(payload, "constraints")
            ),
            warnings=tuple(
                _expect_str_item(item, "warning") for item in _list(payload, "warnings")
            ),
            citation_ids=tuple(
                _expect_str_item(item, "citation_id") for item in _list(payload, "citation_ids")
            ),
            model_identifier=model_identifier,
            prompt_template_version=prompt_template_version,
            schema_version=schema_version,
            requires_manual_review=_bool(payload, "requires_manual_review"),
        )

    def to_canonical_payload(self) -> CanonicalPayload:
        return (
            ("advisory_text", self.advisory_text),
            ("citation_ids_json", _json_text(list(self.citation_ids))),
            (
                "constraints_json",
                _json_text([constraint.to_payload() for constraint in self.constraints]),
            ),
            ("model_identifier", self.model_identifier),
            ("prompt_template_version", self.prompt_template_version),
            ("proposal_id", self.proposal_id),
            ("requires_manual_review", str(self.requires_manual_review).lower()),
            ("schema_version", self.schema_version),
            ("source_text", self.source_text),
            ("warnings_json", _json_text(list(self.warnings))),
        )


class LLMConstraintTranslatorPort(Protocol):
    def translate(self, free_text: str, policy: Mapping[str, object]) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class AdvisoryTextPolicyConfig:
    prompt_template_version: str = "constraint-translator-v1"
    schema_version: str = "constraint-translation-schema-v1"
    allowed_citation_ids: frozenset[str] = frozenset()
    allowed_fields: frozenset[ConstraintField] = frozenset(ConstraintField)
    max_advisory_chars: int = 800

    def to_payload(self) -> dict[str, object]:
        return {
            "allowed_citation_ids": sorted(self.allowed_citation_ids),
            "allowed_fields": sorted(field.value for field in self.allowed_fields),
            "forbidden_patterns": [pattern.pattern for pattern in FORBIDDEN_OUTPUT_PATTERNS],
            "max_advisory_chars": self.max_advisory_chars,
            "prompt_template_version": self.prompt_template_version,
            "schema_version": self.schema_version,
        }


class AdvisoryTextPolicy:
    def __init__(self, config: AdvisoryTextPolicyConfig | None = None) -> None:
        self._config = config or AdvisoryTextPolicyConfig()

    @property
    def config(self) -> AdvisoryTextPolicyConfig:
        return self._config

    def validate(self, advisory_text: str) -> dict[str, object]:
        return self.validate_advisory_text(advisory_text)

    def validate_advisory_text(self, advisory_text: str) -> dict[str, object]:
        violations = self._violations_in_text(advisory_text)
        if len(advisory_text) > self._config.max_advisory_chars:
            violations.append("advisory text exceeds configured length")
        if violations:
            raise AdvisoryTextPolicyViolation("; ".join(violations))
        return {"ok": True, "violations": []}

    def validate_translation_output(self, proposal: TranslationProposal) -> None:
        self.validate_advisory_text(proposal.advisory_text)
        for warning in proposal.warnings:
            self.validate_advisory_text(warning)
        for citation_id in proposal.citation_ids:
            if citation_id not in self._config.allowed_citation_ids:
                raise AdvisoryTextPolicyViolation(f"unresolved citation id: {citation_id}")
        for constraint in proposal.constraints:
            if constraint.field not in self._config.allowed_fields:
                raise AdvisoryTextPolicyViolation(
                    f"constraint field not allowed: {constraint.field.value}"
                )
            self.validate_advisory_text(constraint.value)
            self.validate_advisory_text(constraint.evidence)

    def _violations_in_text(self, text: str) -> list[str]:
        violations: list[str] = []
        for pattern in FORBIDDEN_OUTPUT_PATTERNS:
            if pattern.search(text):
                violations.append(f"forbidden advisory output matched: {pattern.pattern}")
        if _LONG_DNA_RE.search(text):
            violations.append("sequence-level DNA assertion is not allowed in advisory text")
        return violations


class ConstraintTranslator:
    def __init__(
        self,
        *,
        llm_translator: LLMConstraintTranslatorPort,
        advisory_policy: AdvisoryTextPolicy,
        model_identifier: str,
    ) -> None:
        self._llm_translator = llm_translator
        self._advisory_policy = advisory_policy
        self._model_identifier = model_identifier
        self._sequence = 0

    def propose(
        self,
        free_text: str,
        *,
        design_context: Mapping[str, object] | None = None,
    ) -> TranslationProposal:
        clean_text = free_text.strip()
        _require_non_empty(clean_text, "free_text")
        policy_payload = {
            **self._advisory_policy.config.to_payload(),
            "design_context": dict(design_context or {}),
        }
        proposal_id = self._next_proposal_id()
        try:
            payload = self._llm_translator.translate(clean_text, policy_payload)
        except LLMTranslationUnavailable as exc:
            return self._manual_review_proposal(proposal_id, clean_text, str(exc))
        proposal = TranslationProposal.from_llm_payload(
            payload,
            proposal_id=proposal_id,
            source_text=clean_text,
            model_identifier=self._model_identifier,
            prompt_template_version=self._advisory_policy.config.prompt_template_version,
            schema_version=self._advisory_policy.config.schema_version,
        )
        self._advisory_policy.validate_translation_output(proposal)
        return proposal

    def confirmed_payload(
        self,
        proposal: TranslationProposal,
        *,
        accepted_constraint_ids: Iterable[str] | None = None,
    ) -> CanonicalPayload:
        if proposal.requires_manual_review:
            raise ConstraintTranslatorError("manual-review proposals cannot be confirmed")
        constraints = proposal.constraints
        accepted = tuple(accepted_constraint_ids or ())
        if accepted:
            allowed = set(accepted)
            constraints = tuple(
                constraint for constraint in constraints if constraint.field.value in allowed
            )
        if not constraints:
            raise ConstraintTranslatorError("at least one structured constraint is required")
        return tuple(
            (constraint.field.value, constraint.value)
            for constraint in sorted(constraints, key=lambda item: item.field.value)
        )

    def _manual_review_proposal(
        self,
        proposal_id: str,
        source_text: str,
        reason: str,
    ) -> TranslationProposal:
        advisory_text = "Manual translation required; no structured constraint was inferred."
        return TranslationProposal(
            proposal_id=proposal_id,
            source_text=source_text,
            advisory_text=advisory_text,
            constraints=(),
            warnings=(reason,),
            citation_ids=(),
            model_identifier=self._model_identifier,
            prompt_template_version=self._advisory_policy.config.prompt_template_version,
            schema_version=self._advisory_policy.config.schema_version,
            requires_manual_review=True,
        )

    def _next_proposal_id(self) -> str:
        self._sequence += 1
        return f"llm-translation-{self._sequence:06d}"


TRANSLATION_JSON_SCHEMA: dict[str, object] = {
    "additionalProperties": False,
    "properties": {
        "advisory_text": {"type": "string"},
        "citation_ids": {"items": {"type": "string"}, "type": "array"},
        "constraints": {
            "items": {
                "additionalProperties": False,
                "properties": {
                    "confidence": {"type": "string"},
                    "evidence": {"type": "string"},
                    "field": {
                        "enum": [field.value for field in ConstraintField],
                        "type": "string",
                    },
                    "origin": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["confidence", "evidence", "field", "origin", "value"],
                "type": "object",
            },
            "type": "array",
        },
        "requires_manual_review": {"type": "boolean"},
        "warnings": {"items": {"type": "string"}, "type": "array"},
    },
    "required": [
        "advisory_text",
        "citation_ids",
        "constraints",
        "requires_manual_review",
        "warnings",
    ],
    "type": "object",
}

FORBIDDEN_OUTPUT_PATTERNS = (
    re.compile(r"\b(?:incubat(?:e|ion)|centrifug(?:e|ation)|heat[- ]shock)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:plate|grow|culture)\s+(?:overnight|for\s+\d+\s*(?:h|hr|hour))\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:pipette|aliquot|mix)\s+\d+(?:\.\d+)?\s*(?:ul|µl|ml)\b", re.IGNORECASE),
    re.compile(r"\b\d{2,3}\s*(?:deg\s*c|degrees\s*c|c)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:pcr cycling|restriction digest|ligation reaction|transformation protocol)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:pmid|doi)\s*[: ]\s*[\w./-]+", re.IGNORECASE),
)
_LONG_DNA_RE = re.compile(r"\b[ACGT]{24,}\b", re.IGNORECASE)


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty")


def _require_confidence(value: str) -> None:
    try:
        confidence = float(value)
    except ValueError as exc:
        raise ValueError("constraint confidence must be a decimal string") from exc
    if confidence < 0 or confidence > 1:
        raise ValueError("constraint confidence must be between 0 and 1")


def _expect_str(payload: Mapping[str, object], key: str, *, default: str | None = None) -> str:
    value = payload.get(key, default)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    return value


def _expect_str_item(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _list(payload: Mapping[str, object], key: str) -> list[object]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise TypeError(f"{key} must be a list")
    return value


def _expect_mapping_list(payload: Mapping[str, object], key: str) -> list[dict[str, object]]:
    parsed: list[dict[str, object]] = []
    for item in _list(payload, key):
        if not isinstance(item, Mapping):
            raise TypeError(f"{key} items must be objects")
        parsed.append(dict(item))
    return parsed


def _bool(payload: Mapping[str, object], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a boolean")
    return value


def _json_text(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


__all__ = [
    "TRANSLATION_JSON_SCHEMA",
    "AdvisoryTextPolicy",
    "AdvisoryTextPolicyConfig",
    "AdvisoryTextPolicyViolation",
    "ConstraintField",
    "ConstraintTranslator",
    "ConstraintTranslatorError",
    "LLMConstraintTranslatorPort",
    "LLMTranslationUnavailable",
    "StructuredConstraint",
    "TranslationProposal",
]
