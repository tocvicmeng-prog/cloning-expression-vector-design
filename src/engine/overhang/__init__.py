"""
module_id: engine.overhang
file: src/engine/overhang/__init__.py
task_id: T-702

Golden Gate overhang fidelity scoring and set optimisation.
"""

from __future__ import annotations

from engine.overhang.dataset import (
    POTAPOV_2018_HIGH_FIDELITY_SETS,
    POTAPOV_2018_T4_LIGASE,
    PRYOR_2020_24_FRAGMENT_BENCHMARK,
    PRYOR_2020_GOLDEN_GATE,
    LigationFrequencyMatrix,
    OverhangBenchmark,
    all_overhang_candidates,
    canonical_overhang,
    is_palindromic,
    normalise_overhang,
    reverse_complement,
    score_overhang_set,
)
from engine.overhang.optimiser import OverhangSetOptimiser
from engine.overhang.types import (
    CrossReaction,
    OverhangDesignRequest,
    OverhangOptimisationResult,
    OverhangScore,
    OverhangSetScore,
)

__all__ = [
    "POTAPOV_2018_HIGH_FIDELITY_SETS",
    "POTAPOV_2018_T4_LIGASE",
    "PRYOR_2020_24_FRAGMENT_BENCHMARK",
    "PRYOR_2020_GOLDEN_GATE",
    "CrossReaction",
    "LigationFrequencyMatrix",
    "OverhangBenchmark",
    "OverhangDesignRequest",
    "OverhangOptimisationResult",
    "OverhangScore",
    "OverhangSetOptimiser",
    "OverhangSetScore",
    "all_overhang_candidates",
    "canonical_overhang",
    "is_palindromic",
    "normalise_overhang",
    "reverse_complement",
    "score_overhang_set",
]
