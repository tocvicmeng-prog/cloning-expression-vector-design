"""
module_id: tests.fakes.biology.adapters
file: tests/fakes/biology/adapters.py
task_id: T-601a..k

Fixture-driven deterministic fakes for biology adapter ports.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy

Payload = dict[str, object]


class FixtureRnaFolder:
    def __init__(self, fixtures: Mapping[str, Mapping[str, object]]) -> None:
        self._fixtures = fixtures

    def fold(self, sequence: str) -> Payload:
        return _copy_fixture(self._fixtures, sequence)


class FixtureSplicePredictor:
    def __init__(self, fixtures: Mapping[str, Sequence[Mapping[str, object]]]) -> None:
        self._fixtures = fixtures

    def predict_splice_effects(self, sequence: str) -> list[Payload]:
        return [dict(item) for item in self._fixtures[sequence]]


class FixtureSignalPeptidePredictor:
    def __init__(self, fixtures: Mapping[str, Mapping[str, object]]) -> None:
        self._fixtures = fixtures

    def predict_signal_peptide(self, protein_sequence: str) -> Payload:
        return _copy_fixture(self._fixtures, protein_sequence)


class FixtureTIRPredictor:
    def __init__(self, fixtures: Mapping[str, Mapping[str, object]]) -> None:
        self._fixtures = fixtures

    def predict_tir(self, sequence: str, host_context: Mapping[str, object]) -> Payload:
        del host_context
        return _copy_fixture(self._fixtures, sequence)


class FixtureKozakScorer:
    def __init__(self, fixtures: Mapping[str, Mapping[str, object]]) -> None:
        self._fixtures = fixtures

    def score_kozak(self, sequence: str, host_context: Mapping[str, object]) -> Payload:
        del host_context
        return _copy_fixture(self._fixtures, sequence)


class FixtureCodonAlgorithm:
    def __init__(self, fixtures: Mapping[str, Mapping[str, object]]) -> None:
        self._fixtures = fixtures

    def optimise(self, coding_sequence_design: Mapping[str, object]) -> Payload:
        sequence = coding_sequence_design.get("sequence")
        if not isinstance(sequence, str):
            raise TypeError("fixture codon design requires a string sequence")
        return _copy_fixture(self._fixtures, sequence)


def _copy_fixture(fixtures: Mapping[str, Mapping[str, object]], key: str) -> Payload:
    if key not in fixtures:
        raise KeyError(f"no fixture registered for {key!r}")
    copied = deepcopy(fixtures[key])
    if not isinstance(copied, dict):
        raise TypeError("fixture payload must copy to a dict")
    return copied
