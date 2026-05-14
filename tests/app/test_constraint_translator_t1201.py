"""
module_id: tests.app.test_constraint_translator_t1201
file: tests/app/test_constraint_translator_t1201.py
task_id: T-1201
"""

from __future__ import annotations

import pytest

from adapter.llm.local import LocalHeuristicLLMConstraintTranslator
from app.constraint_translator import (
    AdvisoryTextPolicy,
    AdvisoryTextPolicyConfig,
    AdvisoryTextPolicyViolation,
    ConstraintField,
    ConstraintTranslator,
    LLMTranslationUnavailable,
)


class UnsafeTranslator:
    def translate(self, free_text: str, policy: object) -> dict[str, object]:
        del free_text, policy
        return {
            "advisory_text": "Incubate overnight at 37 C and then transform the cells.",
            "citation_ids": [],
            "constraints": [
                {
                    "confidence": "0.90",
                    "evidence": "unsafe protocol text",
                    "field": "objective",
                    "origin": "test",
                    "value": "expression",
                }
            ],
            "requires_manual_review": False,
            "warnings": [],
        }


class UnavailableTranslator:
    def translate(self, free_text: str, policy: object) -> dict[str, object]:
        del free_text, policy
        raise LLMTranslationUnavailable("adapter unavailable")


def test_local_translator_proposes_confirmable_structured_constraints() -> None:
    translator = ConstraintTranslator(
        advisory_policy=AdvisoryTextPolicy(),
        llm_translator=LocalHeuristicLLMConstraintTranslator(),
        model_identifier="local:heuristic",
    )

    proposal = translator.propose("Express EGFP in E. coli with a His tag.")
    confirmed = translator.confirmed_payload(proposal)

    assert not proposal.requires_manual_review
    assert ("cargo", "egfp") in confirmed
    assert ("host", "escherichia_coli") in confirmed
    assert ("objective", "expression") in confirmed
    assert proposal.to_canonical_payload()


def test_red_team_operational_protocol_output_is_rejected() -> None:
    translator = ConstraintTranslator(
        advisory_policy=AdvisoryTextPolicy(),
        llm_translator=UnsafeTranslator(),
        model_identifier="test:unsafe",
    )

    with pytest.raises(AdvisoryTextPolicyViolation, match="forbidden advisory output"):
        translator.propose("How should I express this construct?")


def test_unavailable_llm_returns_manual_translation_required() -> None:
    translator = ConstraintTranslator(
        advisory_policy=AdvisoryTextPolicy(),
        llm_translator=UnavailableTranslator(),
        model_identifier="local:unavailable",
    )

    proposal = translator.propose("A vague objective that needs manual interpretation.")

    assert proposal.requires_manual_review
    assert proposal.constraints == ()
    assert proposal.warnings == ("adapter unavailable",)
    with pytest.raises(ValueError, match="manual-review proposals cannot be confirmed"):
        translator.confirmed_payload(proposal)


def test_policy_rejects_unresolved_citations() -> None:
    policy = AdvisoryTextPolicy(
        AdvisoryTextPolicyConfig(allowed_citation_ids=frozenset({"PMID:123"}))
    )
    translator = ConstraintTranslator(
        advisory_policy=policy,
        llm_translator=_CitationTranslator(),
        model_identifier="test:citation",
    )

    with pytest.raises(AdvisoryTextPolicyViolation, match="unresolved citation"):
        translator.propose("Use a citation.")


def test_confirmed_payload_can_select_fields() -> None:
    translator = ConstraintTranslator(
        advisory_policy=AdvisoryTextPolicy(),
        llm_translator=LocalHeuristicLLMConstraintTranslator(),
        model_identifier="local:heuristic",
    )

    proposal = translator.propose("Express EGFP in E. coli with a His tag.")
    confirmed = translator.confirmed_payload(
        proposal,
        accepted_constraint_ids=(ConstraintField.HOST.value, ConstraintField.CARGO.value),
    )

    assert confirmed == (("cargo", "egfp"), ("host", "escherichia_coli"))


class _CitationTranslator:
    def translate(self, free_text: str, policy: object) -> dict[str, object]:
        del free_text, policy
        return {
            "advisory_text": "Draft constraints inferred from free text.",
            "citation_ids": ["PMID:999"],
            "constraints": [
                {
                    "confidence": "0.70",
                    "evidence": "citation-backed claim",
                    "field": "objective",
                    "origin": "test",
                    "value": "expression",
                }
            ],
            "requires_manual_review": False,
            "warnings": [],
        }
