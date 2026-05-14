"""
module_id: engine.validation.predicates.frame
file: src/engine/validation/predicates/frame.py
task_id: T-503

Reading-frame predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.validation_context import ValidationContext

START_CODONS = frozenset({"ATG", "GTG", "TTG"})
STOP_CODONS = frozenset({"TAA", "TAG", "TGA"})


def mr_10_reading_frame(context: ValidationContext, rule: ValidationRule) -> Severity:
    coding_sequences = _coding_sequences(context)
    if not coding_sequences:
        return Severity.INFO
    return (
        Severity.INFO
        if all(_valid_coding_sequence(sequence) for sequence in coding_sequences)
        else rule.severity
    )


def mr_11_tandem_stop(context: ValidationContext, rule: ValidationRule) -> Severity:
    coding_sequences = _coding_sequences(context)
    if not coding_sequences:
        return Severity.INFO
    return (
        Severity.INFO
        if all(sequence.endswith("TAATAA") for sequence in coding_sequences)
        else rule.severity
    )


def _coding_sequences(context: ValidationContext) -> tuple[str, ...]:
    raw = context.design_payload.get("coding_sequences", ())
    if not isinstance(raw, list | tuple):
        return ()
    return tuple(str(sequence).upper() for sequence in raw)


def _valid_coding_sequence(sequence: str) -> bool:
    if len(sequence) < 6 or len(sequence) % 3:
        return False
    if sequence[:3] not in START_CODONS or sequence[-3:] not in STOP_CODONS:
        return False
    internal_codons = (sequence[index : index + 3] for index in range(3, len(sequence) - 3, 3))
    return all(codon not in STOP_CODONS for codon in internal_codons)


FRAME_PREDICATES = {
    "mr_10": mr_10_reading_frame,
    "mr_11": mr_11_tandem_stop,
}


__all__ = [
    "FRAME_PREDICATES",
    "mr_10_reading_frame",
    "mr_11_tandem_stop",
]
