"""
module_id: domain.sequence
file: src/domain/sequence/feature.py
task_id: T-301

Feature and insertion-context value objects for annotated sequence records.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from domain.sequence.location import LocationV14
from domain.sequence.qualifier import Qualifier


@dataclass(frozen=True)
class FeatureV14:
    role: str
    qualifiers: tuple[Qualifier, ...]
    locations: tuple[LocationV14, ...]
    parent_sequence_id: str
    evidence: tuple[str, ...] = ()
    sub_features: tuple[FeatureV14, ...] = ()

    def __post_init__(self) -> None:
        if not self.role:
            raise ValueError("feature role cannot be empty")
        if not self.locations:
            raise ValueError("feature must have at least one location")
        if not self.parent_sequence_id:
            raise ValueError("feature parent_sequence_id cannot be empty")

    @property
    def ordered_qualifiers(self) -> tuple[Qualifier, ...]:
        return tuple(sorted(self.qualifiers, key=lambda qualifier: qualifier.order))


Feature = FeatureV14


@dataclass(frozen=True)
class InsertionContext:
    parent_node_id: str
    orientation: Literal["forward", "reverse"]
    junction_sequence: str
    scar: str | None
    phase_effect: int
    accepted_overhang_or_overlap: str | None
    insertion_point: LocationV14

    def __post_init__(self) -> None:
        if self.phase_effect not in {0, 1, 2}:
            raise ValueError("phase_effect must be 0, 1, or 2")
        if not self.parent_node_id:
            raise ValueError("parent_node_id cannot be empty")
