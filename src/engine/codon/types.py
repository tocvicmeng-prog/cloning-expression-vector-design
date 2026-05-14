"""
module_id: engine.codon.types
file: src/engine/codon/types.py
task_id: T-701

Codon optimisation value objects.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

CodonAlgorithmName = Literal["cai", "minmax", "charming", "avoid_only"]
CodonUsageTable = Mapping[str, float]


@dataclass(frozen=True)
class ProtectedInterval:
    start: int
    end: int
    reason: str = "protected"

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError("protected interval must satisfy 0 <= start < end")
        if not self.reason:
            raise ValueError("protected interval reason cannot be empty")

    def overlaps(self, start: int, end: int) -> bool:
        return start < self.end and self.start < end


@dataclass(frozen=True)
class FunctionalRnaFeature:
    start: int
    end: int
    feature_id: str

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError("functional RNA feature must satisfy 0 <= start < end")
        if not self.feature_id:
            raise ValueError("functional RNA feature id cannot be empty")

    def as_protected_interval(self) -> ProtectedInterval:
        return ProtectedInterval(
            start=self.start,
            end=self.end,
            reason=f"functional_rna:{self.feature_id}",
        )


@dataclass(frozen=True)
class CodingSequenceDesign:
    sequence: str
    algorithm: CodonAlgorithmName
    host_codon_usage: CodonUsageTable
    protected_intervals: tuple[ProtectedInterval, ...] = ()
    functional_rna_features: tuple[FunctionalRnaFeature, ...] = ()
    avoid_motifs: tuple[str, ...] = ()
    target_gc_fraction: float | None = None
    max_iterations: int = 5

    def __post_init__(self) -> None:
        if self.max_iterations < 1 or self.max_iterations > 5:
            raise ValueError("max_iterations must be between 1 and 5")
        if self.target_gc_fraction is not None and not 0 <= self.target_gc_fraction <= 1:
            raise ValueError("target_gc_fraction must be between 0 and 1")
        if not self.host_codon_usage:
            raise ValueError("host_codon_usage cannot be empty")

    @property
    def all_protected_intervals(self) -> tuple[ProtectedInterval, ...]:
        return (
            *self.protected_intervals,
            *(feature.as_protected_interval() for feature in self.functional_rna_features),
        )


@dataclass(frozen=True)
class CodonMetrics:
    cai: float
    gc_fraction: float
    max_windowed_gc_fraction: float
    homopolymer_run_length: int
    direct_repeat_count: int


@dataclass(frozen=True)
class OptimisationStep:
    iteration: int
    sequence: str
    changed_codons: int
    unresolved_motifs: tuple[str, ...]


@dataclass(frozen=True)
class CodonOptimisationResult:
    algorithm: CodonAlgorithmName
    input_sequence: str
    sequence: str
    protein: str
    protein_preserved: bool
    converged: bool
    iterations: int
    metrics_before: CodonMetrics
    metrics_after: CodonMetrics
    protected_intervals_preserved: bool
    unresolved_motifs: tuple[str, ...]
    history: tuple[OptimisationStep, ...]


__all__ = [
    "CodingSequenceDesign",
    "CodonAlgorithmName",
    "CodonMetrics",
    "CodonOptimisationResult",
    "CodonUsageTable",
    "FunctionalRnaFeature",
    "OptimisationStep",
    "ProtectedInterval",
]
