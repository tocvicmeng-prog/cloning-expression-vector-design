"""
module_id: engine.sequence_analysis.digest
file: src/engine/sequence_analysis/digest.py
task_id: T-503

Restriction digest simulation.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import pairwise

from domain.sequence import SequenceRecord
from engine.sequence_analysis.compatible_ends import FragmentEnd
from engine.sequence_analysis.find_sites import RestrictionEnzyme, RestrictionSite, find_sites


@dataclass(frozen=True, order=True)
class RestrictionFragment:
    start: int
    end: int
    sequence: str
    left_end: FragmentEnd
    right_end: FragmentEnd

    @property
    def length(self) -> int:
        return len(self.sequence)


@dataclass(frozen=True)
class RestrictionDigest:
    topology: str
    sites: tuple[RestrictionSite, ...]
    fragments: tuple[RestrictionFragment, ...]

    @property
    def band_lengths(self) -> tuple[int, ...]:
        return tuple(sorted((fragment.length for fragment in self.fragments), reverse=True))


def digest(
    sequence: str | SequenceRecord,
    enzymes: Iterable[RestrictionEnzyme],
    *,
    topology: str | None = None,
) -> RestrictionDigest:
    body = sequence.sequence.body if isinstance(sequence, SequenceRecord) else sequence.upper()
    resolved_topology = topology or (
        sequence.topology if isinstance(sequence, SequenceRecord) else "linear"
    )
    sites = tuple(
        site for enzyme in enzymes for site in find_sites(body, enzyme, topology=resolved_topology)
    )
    cut_points = sorted({site.cut_position % len(body) for site in sites})
    fragments = _fragments(body, cut_points, sites, topology=resolved_topology)
    return RestrictionDigest(
        topology=resolved_topology, sites=tuple(sorted(sites)), fragments=fragments
    )


def _fragments(
    body: str,
    cut_points: list[int],
    sites: tuple[RestrictionSite, ...],
    *,
    topology: str,
) -> tuple[RestrictionFragment, ...]:
    if not cut_points:
        return (
            RestrictionFragment(
                start=0,
                end=len(body),
                sequence=body,
                left_end=FragmentEnd("blunt"),
                right_end=FragmentEnd("blunt"),
            ),
        )
    end_by_cut = {site.cut_position % len(body): site.enzyme.right_end for site in sites}
    if topology == "linear":
        boundaries = [0, *[point for point in cut_points if 0 < point < len(body)], len(body)]
        return tuple(
            RestrictionFragment(
                start=left,
                end=right,
                sequence=body[left:right],
                left_end=end_by_cut.get(left, FragmentEnd("blunt")),
                right_end=end_by_cut.get(right % len(body), FragmentEnd("blunt")),
            )
            for left, right in pairwise(boundaries)
            if right > left
        )
    circular_boundaries = (*cut_points, cut_points[0] + len(body))
    fragments: list[RestrictionFragment] = []
    for left, right in pairwise(circular_boundaries):
        if right <= left:
            continue
        sequence = (body + body)[left:right]
        fragments.append(
            RestrictionFragment(
                start=left % len(body),
                end=right % len(body),
                sequence=sequence,
                left_end=end_by_cut.get(left % len(body), FragmentEnd("blunt")),
                right_end=end_by_cut.get(right % len(body), FragmentEnd("blunt")),
            )
        )
    return tuple(fragments)


__all__ = [
    "RestrictionDigest",
    "RestrictionFragment",
    "digest",
]
