"""
module_id: engine.sequence_analysis.rank_directional
file: src/engine/sequence_analysis/rank_directional.py
task_id: T-503

Directional cloning site ranking.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from domain.sequence import SequenceRecord
from engine.sequence_analysis.find_sites import RestrictionEnzyme, find_sites


@dataclass(frozen=True, order=True)
class DirectionalCloningCandidate:
    score: int
    upstream_enzyme: RestrictionEnzyme
    downstream_enzyme: RestrictionEnzyme
    upstream_position: int
    downstream_position: int
    insert_free: bool


def rank_directional_cloning_sites(
    vector: str | SequenceRecord,
    insert: str | SequenceRecord,
    enzymes: Iterable[RestrictionEnzyme],
    *,
    topology: str = "circular",
) -> tuple[DirectionalCloningCandidate, ...]:
    enzyme_tuple = tuple(enzymes)
    vector_sites = {
        enzyme.name: find_sites(vector, enzyme, topology=topology) for enzyme in enzyme_tuple
    }
    insert_sites = {
        enzyme.name: find_sites(insert, enzyme, topology="linear") for enzyme in enzyme_tuple
    }
    unique_vector_enzymes = [
        enzyme
        for enzyme in enzyme_tuple
        if len(vector_sites[enzyme.name]) == 1 and not insert_sites[enzyme.name]
    ]
    candidates: list[DirectionalCloningCandidate] = []
    for upstream in unique_vector_enzymes:
        for downstream in unique_vector_enzymes:
            if upstream == downstream:
                continue
            upstream_position = vector_sites[upstream.name][0].start
            downstream_position = vector_sites[downstream.name][0].start
            if upstream_position == downstream_position:
                continue
            span = abs(downstream_position - upstream_position)
            candidates.append(
                DirectionalCloningCandidate(
                    score=span,
                    upstream_enzyme=upstream,
                    downstream_enzyme=downstream,
                    upstream_position=upstream_position,
                    downstream_position=downstream_position,
                    insert_free=True,
                )
            )
    return tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                -candidate.score,
                candidate.upstream_enzyme.name,
                candidate.downstream_enzyme.name,
            ),
        )
    )


__all__ = [
    "DirectionalCloningCandidate",
    "rank_directional_cloning_sites",
]
