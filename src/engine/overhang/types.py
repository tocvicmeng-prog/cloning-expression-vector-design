"""
module_id: engine.overhang.types
file: src/engine/overhang/types.py
task_id: T-702

Value objects for Golden Gate overhang set optimisation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrossReaction:
    """Predicted off-target ligation between two selected overhang pairs."""

    left: str
    right: str
    weight: float
    relative_to_left: float
    relative_to_right: float


@dataclass(frozen=True)
class OverhangScore:
    """Per-overhang contribution to an overall assembly fidelity score."""

    overhang: str
    correct_ligation_weight: float
    off_target_ligation_weight: float
    fidelity: float


@dataclass(frozen=True)
class OverhangSetScore:
    """Fidelity score for one overhang set."""

    overhangs: tuple[str, ...]
    fidelity: float
    per_overhang: tuple[OverhangScore, ...]
    cross_reactions: tuple[CrossReaction, ...]
    palindrome_count: int
    reverse_complement_conflict_count: int
    worst_pair_crosstalk: float

    @property
    def lowest_overhang_fidelity(self) -> float:
        if not self.per_overhang:
            return 0.0
        return min(score.fidelity for score in self.per_overhang)


@dataclass(frozen=True)
class OverhangDesignRequest:
    """Input contract for branch-and-bound overhang set selection."""

    set_size: int
    candidate_overhangs: tuple[str, ...] = ()
    required_overhangs: tuple[str, ...] = ()
    excluded_overhangs: tuple[str, ...] = ()
    minimum_fidelity: float = 0.0
    minimum_per_overhang_fidelity: float = 0.0
    max_pair_crosstalk: float = 0.02
    allow_palindromes: bool = False
    max_candidates: int = 48
    node_budget: int = 250_000

    def __post_init__(self) -> None:
        if self.set_size < 1:
            raise ValueError("set_size must be positive")
        _validate_probability(self.minimum_fidelity, "minimum_fidelity")
        _validate_probability(self.minimum_per_overhang_fidelity, "minimum_per_overhang_fidelity")
        if self.max_pair_crosstalk < 0.0:
            raise ValueError("max_pair_crosstalk must be non-negative")
        if self.max_candidates < self.set_size:
            raise ValueError("max_candidates must be at least set_size")
        if self.node_budget < 1:
            raise ValueError("node_budget must be positive")


@dataclass(frozen=True)
class OverhangOptimisationResult:
    """Search result plus diagnostics needed by downstream assembly planning."""

    score: OverhangSetScore
    dataset_name: str
    candidate_count: int
    nodes_visited: int
    pruned_branches: int
    exhaustive: bool
    warnings: tuple[str, ...] = ()

    @property
    def overhangs(self) -> tuple[str, ...]:
        return self.score.overhangs

    @property
    def fidelity(self) -> float:
        return self.score.fidelity

    @property
    def meets_thresholds(self) -> bool:
        return not self.warnings


def _validate_probability(value: float, field_name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")
