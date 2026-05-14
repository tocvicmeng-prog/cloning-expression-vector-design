"""
module_id: engine.sequence_analysis.compatible_ends
file: src/engine/sequence_analysis/compatible_ends.py
task_id: T-503

Restriction-fragment end compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EndKind = Literal["5_prime", "3_prime", "blunt"]

DNA_COMPLEMENT = str.maketrans("ACGTRYSWKMBDHVN", "TGCAYRSWMKVHDBN")


@dataclass(frozen=True, order=True)
class FragmentEnd:
    kind: EndKind
    sequence: str = ""

    def __post_init__(self) -> None:
        sequence = self.sequence.upper()
        if self.kind == "blunt" and sequence:
            raise ValueError("blunt fragment ends cannot carry an overhang sequence")
        if self.kind != "blunt" and not sequence:
            raise ValueError("sticky fragment ends require an overhang sequence")
        object.__setattr__(self, "sequence", sequence)


@dataclass(frozen=True)
class EndCompatibility:
    left: FragmentEnd
    right: FragmentEnd
    compatible: bool
    reason: str


def compatible_ends(left: FragmentEnd, right: FragmentEnd) -> EndCompatibility:
    if left.kind == "blunt" or right.kind == "blunt":
        compatible = left.kind == right.kind == "blunt"
        reason = "both blunt" if compatible else "blunt/sticky mismatch"
        return EndCompatibility(left=left, right=right, compatible=compatible, reason=reason)
    if left.kind != right.kind:
        return EndCompatibility(
            left=left,
            right=right,
            compatible=False,
            reason="5-prime and 3-prime overhangs are not directly compatible",
        )
    compatible = left.sequence == reverse_complement(right.sequence)
    return EndCompatibility(
        left=left,
        right=right,
        compatible=compatible,
        reason="reverse-complementary overhangs" if compatible else "overhang mismatch",
    )


def reverse_complement(sequence: str) -> str:
    return sequence.upper().translate(DNA_COMPLEMENT)[::-1]


__all__ = [
    "EndCompatibility",
    "FragmentEnd",
    "compatible_ends",
    "reverse_complement",
]
