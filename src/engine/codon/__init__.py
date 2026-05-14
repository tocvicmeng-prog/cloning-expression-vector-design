"""
module_id: engine.codon
file: src/engine/codon/__init__.py
task_id: T-701

Constraint-aware codon optimisation engine.
"""

from __future__ import annotations

from engine.codon.algorithms import (
    CODON_TO_AA,
    DEFAULT_CODON_USAGE_TABLE,
    cai_score,
    direct_repeat_count,
    gc_fraction,
    homopolymer_run_length,
    optimise_algorithm_once,
    translate,
    windowed_gc_fraction,
)
from engine.codon.optimiser import CodonOptimiser
from engine.codon.types import (
    CodingSequenceDesign,
    CodonAlgorithmName,
    CodonMetrics,
    CodonOptimisationResult,
    FunctionalRnaFeature,
    OptimisationStep,
    ProtectedInterval,
)

__all__ = [
    "CODON_TO_AA",
    "DEFAULT_CODON_USAGE_TABLE",
    "CodingSequenceDesign",
    "CodonAlgorithmName",
    "CodonMetrics",
    "CodonOptimisationResult",
    "CodonOptimiser",
    "FunctionalRnaFeature",
    "OptimisationStep",
    "ProtectedInterval",
    "cai_score",
    "direct_repeat_count",
    "gc_fraction",
    "homopolymer_run_length",
    "optimise_algorithm_once",
    "translate",
    "windowed_gc_fraction",
]
