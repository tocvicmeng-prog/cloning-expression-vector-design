"""
module_id: engine.validation.predicates.premature_polya
file: src/engine/validation/predicates/premature_polya.py
task_id: T-602

Premature polyadenylation-signal predicates.
"""

from __future__ import annotations

from collections.abc import Sequence

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates.metric_helpers import metric_bool, payload_str
from engine.validation.validation_context import ValidationContext

POLYA_MOTIFS = ("AATAAA", "ATTAAA", "AGTAAA", "TATAAA")


def mr_15_premature_polya_scan(context: ValidationContext, rule: ValidationRule) -> Severity:
    detected = metric_bool(context, "biology.polya.premature_detected")
    if detected is not None:
        return rule.severity if detected else Severity.INFO
    sequences = _candidate_sequences(context)
    return rule.severity if any(_contains_polya(seq) for seq in sequences) else Severity.INFO


def _candidate_sequences(context: ValidationContext) -> tuple[str, ...]:
    candidates: list[str] = []
    for key in ("five_prime_utr", "mrna_sequence"):
        value = payload_str(context, key)
        if value:
            candidates.append(value)
    coding = context.design_payload.get("coding_sequences", ())
    if isinstance(coding, Sequence) and not isinstance(coding, str):
        candidates.extend(str(item) for item in coding if isinstance(item, str))
    return tuple(candidate.upper().replace("U", "T") for candidate in candidates)


def _contains_polya(sequence: str) -> bool:
    return any(motif in sequence for motif in POLYA_MOTIFS)


POLYA_PREDICATES = {
    "mr_15": mr_15_premature_polya_scan,
}


__all__ = [
    "POLYA_PREDICATES",
    "mr_15_premature_polya_scan",
]
