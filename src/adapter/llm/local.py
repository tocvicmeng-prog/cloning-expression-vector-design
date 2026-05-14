"""
module_id: adapter.llm.local
file: src/adapter/llm/local.py
task_id: T-1201

Deterministic local fallback for free-text constraint translation.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.constraint_translator import (
    FORBIDDEN_OUTPUT_PATTERNS,
    ConstraintField,
    LLMTranslationUnavailable,
)


class LocalHeuristicLLMConstraintTranslator:
    name = "local-heuristic-constraint-translator"
    version = "1"

    def translate(self, free_text: str, policy: Mapping[str, object]) -> dict[str, object]:
        del policy
        text = free_text.strip()
        lowered = text.lower()
        if any(pattern.search(text) for pattern in FORBIDDEN_OUTPUT_PATTERNS):
            raise LLMTranslationUnavailable(
                "free text appears to request operational protocol detail"
            )
        constraints: list[dict[str, str]] = []
        _maybe_add_constraint(
            constraints,
            lowered,
            ConstraintField.CARGO,
            {"egfp": "egfp", "gfp": "gfp", "luciferase": "luciferase"},
        )
        _maybe_add_constraint(
            constraints,
            lowered,
            ConstraintField.HOST,
            {
                "e. coli": "escherichia_coli",
                "ecoli": "escherichia_coli",
                "hek293": "hek293",
                "n. benthamiana": "nicotiana_benthamiana",
            },
        )
        _maybe_add_constraint(
            constraints,
            lowered,
            ConstraintField.OBJECTIVE,
            {
                "express": "expression",
                "expression": "expression",
                "clone": "cloning",
            },
        )
        _maybe_add_constraint(
            constraints,
            lowered,
            ConstraintField.TAG,
            {"his": "his_tag", "flag": "flag_tag", "ha tag": "ha_tag"},
        )
        _maybe_add_constraint(
            constraints,
            lowered,
            ConstraintField.BIOSAFETY_TIER,
            {"bsl-1": "BSL-1", "bsl-2": "BSL-2", "bsl-3": "BSL-3", "bsl-4": "BSL-4"},
        )
        if not constraints:
            raise LLMTranslationUnavailable("local translator found no supported constraints")
        return {
            "advisory_text": (
                "Draft constraints inferred from free text; user confirmation is required."
            ),
            "citation_ids": [],
            "constraints": constraints,
            "requires_manual_review": False,
            "warnings": [],
        }


def _maybe_add_constraint(
    constraints: list[dict[str, str]],
    lowered_text: str,
    field: ConstraintField,
    terms: Mapping[str, str],
) -> None:
    for needle, value in terms.items():
        if needle in lowered_text:
            constraints.append(
                {
                    "confidence": "0.80",
                    "evidence": f"matched free-text term '{needle}'",
                    "field": field.value,
                    "origin": "local_heuristic",
                    "value": value,
                }
            )
            return


__all__ = ["LocalHeuristicLLMConstraintTranslator"]
