"""
module_id: tests.fakes.biology
file: tests/fakes/biology/__init__.py
task_id: T-601a..k
"""

from __future__ import annotations

from tests.fakes.biology.adapters import (
    FixtureCodonAlgorithm,
    FixtureKozakScorer,
    FixtureRnaFolder,
    FixtureSignalPeptidePredictor,
    FixtureSplicePredictor,
    FixtureTIRPredictor,
)

__all__ = [
    "FixtureCodonAlgorithm",
    "FixtureKozakScorer",
    "FixtureRnaFolder",
    "FixtureSignalPeptidePredictor",
    "FixtureSplicePredictor",
    "FixtureTIRPredictor",
]
