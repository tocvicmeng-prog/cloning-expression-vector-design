"""
module_id: engine.sequence_analysis.design_diagnostic
file: src/engine/sequence_analysis/design_diagnostic.py
task_id: T-503

Diagnostic digest design.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations

from domain.sequence import SequenceRecord
from engine.sequence_analysis.digest import digest
from engine.sequence_analysis.find_sites import RestrictionEnzyme


@dataclass(frozen=True)
class WrongCloneModel:
    name: str
    sequence: str | SequenceRecord
    topology: str = "circular"


@dataclass(frozen=True)
class DiagnosticDigestDesign:
    enzymes: tuple[RestrictionEnzyme, ...]
    correct_bands: tuple[int, ...]
    wrong_clone_bands: dict[str, tuple[int, ...]]

    @property
    def distinguishes_all(self) -> bool:
        return all(bands != self.correct_bands for bands in self.wrong_clone_bands.values())


def design_diagnostic_digest(
    correct_clone: str | SequenceRecord,
    wrong_clones: Iterable[WrongCloneModel],
    enzymes: Iterable[RestrictionEnzyme],
    *,
    topology: str = "circular",
    max_enzymes: int = 2,
) -> DiagnosticDigestDesign | None:
    wrong_tuple = tuple(wrong_clones)
    enzyme_tuple = tuple(enzymes)
    for size in range(1, max_enzymes + 1):
        for enzyme_group in combinations(enzyme_tuple, size):
            correct_bands = digest(correct_clone, enzyme_group, topology=topology).band_lengths
            wrong_bands = {
                clone.name: digest(
                    clone.sequence, enzyme_group, topology=clone.topology
                ).band_lengths
                for clone in wrong_tuple
            }
            design = DiagnosticDigestDesign(
                enzymes=enzyme_group,
                correct_bands=correct_bands,
                wrong_clone_bands=wrong_bands,
            )
            if design.distinguishes_all:
                return design
    return None


__all__ = [
    "DiagnosticDigestDesign",
    "WrongCloneModel",
    "design_diagnostic_digest",
]
