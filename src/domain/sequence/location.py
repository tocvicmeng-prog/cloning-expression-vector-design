"""
module_id: domain.sequence
file: src/domain/sequence/location.py
task_id: T-301

Formal location algebra for linear, circular, compound, fuzzy, and remote locations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class LocationFuzziness(Enum):
    EXACT = "exact"
    BEFORE = "before"
    AFTER = "after"
    BETWEEN = "between"
    UNKNOWN = "unknown"


class CompoundLocationKind(Enum):
    JOIN = "join"
    ORDER = "order"
    BOND = "bond"
    GAP = "gap"


@dataclass(frozen=True)
class LocationV14:
    start: int
    end: int
    strand: Literal["+", "-", "."]
    phase: Literal[0, 1, 2, "."]
    start_fuzziness: LocationFuzziness = LocationFuzziness.EXACT
    end_fuzziness: LocationFuzziness = LocationFuzziness.EXACT
    circular_wrap: bool = False
    between_base: bool = False
    sub_locations: tuple[LocationV14, ...] = ()
    sub_kind: CompoundLocationKind | None = None
    complement_compound: bool = False
    remote_accession: str | None = None
    partial_at_5p: bool = False
    partial_at_3p: bool = False

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < 0:
            raise ValueError("location coordinates must be non-negative")
        if self.sub_locations and self.sub_kind is None:
            raise ValueError("compound locations require sub_kind")
        if self.sub_kind is not None and not self.sub_locations:
            raise ValueError("sub_kind requires sub_locations")
        if self.between_base and (
            self.end != self.start + 1
            or self.start_fuzziness is not LocationFuzziness.BETWEEN
            or self.end_fuzziness is not LocationFuzziness.BETWEEN
        ):
            raise ValueError("between-base locations must span adjacent bases with BETWEEN fuzz")

    def span_length(self, parent_length: int) -> int:
        if self.sub_locations:
            return sum(location.span_length(parent_length) for location in self.sub_locations)
        if self.between_base:
            return 0
        if self.circular_wrap:
            return parent_length - self.start + self.end
        return self.end - self.start

    def sequence_length_invariant_satisfied(self, parent_length: int) -> bool:
        if parent_length <= 0:
            return False
        if self.sub_locations:
            return all(
                location.sequence_length_invariant_satisfied(parent_length)
                for location in self.sub_locations
            )
        if self.start > parent_length or self.end > parent_length:
            return False
        if self.circular_wrap:
            return self.start > self.end and self.span_length(parent_length) <= parent_length
        return self.start <= self.end and self.span_length(parent_length) <= parent_length


Location = LocationV14
