"""
module_id: engine.codon.optimiser
file: src/engine/codon/optimiser.py
task_id: T-701

Lexicographic-priority fixed-point codon optimiser.
"""

from __future__ import annotations

from collections.abc import Mapping

from engine.codon.algorithms import (
    cai_score,
    changed_codons,
    direct_repeat_count,
    gc_fraction,
    homopolymer_run_length,
    normalise_dna,
    optimise_algorithm_once,
    remove_avoided_motif_once,
    translate,
    unresolved_motifs,
    windowed_gc_fraction,
)
from engine.codon.types import (
    CodingSequenceDesign,
    CodonMetrics,
    CodonOptimisationResult,
    OptimisationStep,
    ProtectedInterval,
)


class CodonOptimiser:
    def optimise(self, design: CodingSequenceDesign) -> CodonOptimisationResult:
        original = normalise_dna(design.sequence)
        protected = _validated_protected_intervals(original, design.all_protected_intervals)
        current = original
        history: list[OptimisationStep] = []
        converged = False

        for iteration in range(1, design.max_iterations + 1):
            proposed = optimise_algorithm_once(
                current,
                algorithm=design.algorithm,
                usage_table=design.host_codon_usage,
                protected_intervals=protected,
                target_gc_fraction=design.target_gc_fraction,
            )
            proposed = _restore_protected_slices(original, proposed, protected)
            proposed = remove_avoided_motif_once(
                proposed,
                avoid_motifs=design.avoid_motifs,
                protected_intervals=protected,
                usage_table=design.host_codon_usage,
            )
            proposed = _restore_protected_slices(original, proposed, protected)
            unresolved = unresolved_motifs(proposed, design.avoid_motifs)
            history.append(
                OptimisationStep(
                    iteration=iteration,
                    sequence=proposed,
                    changed_codons=changed_codons(current, proposed),
                    unresolved_motifs=unresolved,
                )
            )
            if proposed == current:
                converged = True
                current = proposed
                break
            current = proposed

        return CodonOptimisationResult(
            algorithm=design.algorithm,
            input_sequence=original,
            sequence=current,
            protein=translate(current),
            protein_preserved=translate(original) == translate(current),
            converged=converged,
            iterations=len(history),
            metrics_before=_metrics(original, design.host_codon_usage),
            metrics_after=_metrics(current, design.host_codon_usage),
            protected_intervals_preserved=_protected_slices_match(original, current, protected),
            unresolved_motifs=unresolved_motifs(current, design.avoid_motifs),
            history=tuple(history),
        )


def _metrics(sequence: str, usage_table: Mapping[str, float]) -> CodonMetrics:
    windowed = windowed_gc_fraction(sequence, window_size=min(50, max(1, len(sequence))))
    return CodonMetrics(
        cai=cai_score(sequence, usage_table),
        gc_fraction=round(gc_fraction(sequence), 4),
        max_windowed_gc_fraction=max(windowed),
        homopolymer_run_length=homopolymer_run_length(sequence),
        direct_repeat_count=direct_repeat_count(sequence),
    )


def _validated_protected_intervals(
    sequence: str,
    intervals: tuple[ProtectedInterval, ...],
) -> tuple[ProtectedInterval, ...]:
    for interval in intervals:
        if interval.end > len(sequence):
            raise ValueError("protected interval exceeds sequence length")
    return intervals


def _restore_protected_slices(
    original: str,
    proposed: str,
    intervals: tuple[ProtectedInterval, ...],
) -> str:
    if len(original) != len(proposed):
        raise ValueError("optimised sequence changed length")
    if not intervals:
        return proposed
    letters = list(proposed)
    for interval in intervals:
        letters[interval.start : interval.end] = original[interval.start : interval.end]
    return "".join(letters)


def _protected_slices_match(
    original: str,
    optimised: str,
    intervals: tuple[ProtectedInterval, ...],
) -> bool:
    return all(
        original[interval.start : interval.end] == optimised[interval.start : interval.end]
        for interval in intervals
    )


__all__ = ["CodonOptimiser"]
