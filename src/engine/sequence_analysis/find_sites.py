"""
module_id: engine.sequence_analysis.find_sites
file: src/engine/sequence_analysis/find_sites.py
task_id: T-503

Topology-aware restriction site finding with IUPAC ambiguity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from domain.sequence import SequenceRecord
from engine.sequence_analysis.compatible_ends import FragmentEnd, reverse_complement

IUPAC_BASES: dict[str, frozenset[str]] = {
    "A": frozenset({"A"}),
    "C": frozenset({"C"}),
    "G": frozenset({"G"}),
    "T": frozenset({"T"}),
    "R": frozenset({"A", "G"}),
    "Y": frozenset({"C", "T"}),
    "S": frozenset({"G", "C"}),
    "W": frozenset({"A", "T"}),
    "K": frozenset({"G", "T"}),
    "M": frozenset({"A", "C"}),
    "B": frozenset({"C", "G", "T"}),
    "D": frozenset({"A", "G", "T"}),
    "H": frozenset({"A", "C", "T"}),
    "V": frozenset({"A", "C", "G"}),
    "N": frozenset({"A", "C", "G", "T"}),
}
BLUNT_END = FragmentEnd("blunt")


@dataclass(frozen=True, order=True)
class RestrictionEnzyme:
    name: str
    recognition_site: str
    cut_index: int
    right_end: FragmentEnd = BLUNT_END

    def __post_init__(self) -> None:
        recognition_site = self.recognition_site.upper()
        if not self.name:
            raise ValueError("restriction enzyme name cannot be empty")
        if not recognition_site:
            raise ValueError("recognition site cannot be empty")
        if any(base not in IUPAC_BASES for base in recognition_site):
            raise ValueError("recognition site contains unsupported IUPAC symbols")
        if not 0 <= self.cut_index <= len(recognition_site):
            raise ValueError("cut_index must lie within the recognition site")
        object.__setattr__(self, "recognition_site", recognition_site)

    @classmethod
    def from_cut_notation(
        cls: type[Self],
        name: str,
        cut_notation: str,
        *,
        right_end: FragmentEnd | None = None,
    ) -> Self:
        if cut_notation.count("^") != 1:
            raise ValueError("cut notation must contain exactly one '^'")
        recognition_site = cut_notation.replace("^", "")
        return cls(
            name=name,
            recognition_site=recognition_site,
            cut_index=cut_notation.index("^"),
            right_end=BLUNT_END if right_end is None else right_end,
        )


@dataclass(frozen=True, order=True)
class RestrictionSite:
    enzyme: RestrictionEnzyme
    start: int
    end: int
    matched_sequence: str
    wraps_origin: bool = False
    strand: str = "+"

    @property
    def cut_position(self) -> int:
        return self.start + self.enzyme.cut_index


def find_sites(
    sequence: str | SequenceRecord,
    enzyme: RestrictionEnzyme,
    *,
    topology: str | None = None,
    include_reverse: bool = False,
) -> tuple[RestrictionSite, ...]:
    body = _sequence_body(sequence)
    resolved_topology = topology or _sequence_topology(sequence)
    if resolved_topology not in {"linear", "circular"}:
        raise ValueError("topology must be linear or circular")
    sites = list(_find_sites_on_strand(body, enzyme, topology=resolved_topology, strand="+"))
    if include_reverse:
        reverse_enzyme = RestrictionEnzyme(
            name=enzyme.name,
            recognition_site=reverse_complement(enzyme.recognition_site),
            cut_index=len(enzyme.recognition_site) - enzyme.cut_index,
            right_end=enzyme.right_end,
        )
        sites.extend(
            _find_sites_on_strand(body, reverse_enzyme, topology=resolved_topology, strand="-")
        )
    return tuple(sorted(set(sites), key=lambda site: (site.start, site.strand, site.enzyme.name)))


def _find_sites_on_strand(
    body: str,
    enzyme: RestrictionEnzyme,
    *,
    topology: str,
    strand: str,
) -> tuple[RestrictionSite, ...]:
    pattern_length = len(enzyme.recognition_site)
    search_body = body if topology == "linear" else body + body[: pattern_length - 1]
    limit = len(body) if topology == "circular" else len(body) - pattern_length + 1
    sites: list[RestrictionSite] = []
    for start in range(max(0, limit)):
        window = search_body[start : start + pattern_length]
        if len(window) == pattern_length and _matches(window, enzyme.recognition_site):
            end = start + pattern_length
            sites.append(
                RestrictionSite(
                    enzyme=enzyme,
                    start=start,
                    end=end % len(body) if end > len(body) else end,
                    matched_sequence=window,
                    wraps_origin=end > len(body),
                    strand=strand,
                )
            )
    return tuple(sites)


def _matches(window: str, pattern: str) -> bool:
    return all(
        base in IUPAC_BASES[pattern_base]
        for base, pattern_base in zip(window, pattern, strict=True)
    )


def _sequence_body(sequence: str | SequenceRecord) -> str:
    return sequence.sequence.body if isinstance(sequence, SequenceRecord) else sequence.upper()


def _sequence_topology(sequence: str | SequenceRecord) -> str:
    return sequence.topology if isinstance(sequence, SequenceRecord) else "linear"


__all__ = [
    "RestrictionEnzyme",
    "RestrictionSite",
    "find_sites",
]
