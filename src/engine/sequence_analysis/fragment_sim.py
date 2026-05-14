"""
module_id: engine.sequence_analysis.fragment_sim
file: src/engine/sequence_analysis/fragment_sim.py
task_id: T-503

Fragment simulation helpers.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from domain.sequence import SequenceRecord
from engine.sequence_analysis.digest import RestrictionDigest, digest
from engine.sequence_analysis.find_sites import RestrictionEnzyme


@dataclass(frozen=True)
class FragmentSimulation:
    digest: RestrictionDigest

    @property
    def ordered_fragment_lengths(self) -> tuple[int, ...]:
        return self.digest.band_lengths


def simulate_fragments(
    sequence: str | SequenceRecord,
    enzymes: Iterable[RestrictionEnzyme],
    *,
    topology: str | None = None,
) -> FragmentSimulation:
    return FragmentSimulation(digest=digest(sequence, enzymes, topology=topology))


__all__ = [
    "FragmentSimulation",
    "simulate_fragments",
]
