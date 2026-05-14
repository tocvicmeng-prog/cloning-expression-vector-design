"""
module_id: engine.assembly.base
file: src/engine/assembly/base.py
task_id: T-703

Shared assembly strategy contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import pairwise
from typing import Literal

from domain.sequence import DnaSequence, MoleculeType, SequenceRecord
from domain.types.assembly_plan import AssemblyPlanSummary
from domain.types.ids import AssemblyMethodId


@dataclass(frozen=True)
class AssemblyPart:
    """Minimal fragment input shared by all assembly strategies."""

    id: str
    sequence: str
    topology: Literal["linear", "circular"] = "linear"
    left_overhang: str = ""
    right_overhang: str = ""
    left_overlap: str = ""
    right_overlap: str = ""
    annotations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("assembly part id cannot be empty")
        sequence = self.sequence.strip().upper()
        if not sequence:
            raise ValueError("assembly part sequence cannot be empty")
        invalid = sorted(set(sequence) - set("ACGT"))
        if invalid:
            raise ValueError(f"assembly part sequence contains non-DNA bases: {''.join(invalid)}")
        object.__setattr__(self, "sequence", sequence)
        object.__setattr__(self, "left_overhang", self.left_overhang.strip().upper())
        object.__setattr__(self, "right_overhang", self.right_overhang.strip().upper())
        object.__setattr__(self, "left_overlap", self.left_overlap.strip().upper())
        object.__setattr__(self, "right_overlap", self.right_overlap.strip().upper())


@dataclass(frozen=True)
class PrimerDesign:
    name: str
    template_part_id: str
    sequence: str
    purpose: str

    def __post_init__(self) -> None:
        if not self.name or not self.template_part_id or not self.sequence or not self.purpose:
            raise ValueError("primer designs require name, part id, sequence, and purpose")


@dataclass(frozen=True)
class AssemblyValidation:
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @classmethod
    def ok(cls, warnings: tuple[str, ...] = ()) -> AssemblyValidation:
        return cls(valid=True, warnings=warnings)

    @classmethod
    def fail(cls, *errors: str, warnings: tuple[str, ...] = ()) -> AssemblyValidation:
        return cls(valid=False, errors=errors, warnings=warnings)


class AssemblyStrategy(ABC):
    """Common contract for all assembly chemistries."""

    method_id: AssemblyMethodId
    display_name: str
    minimum_fragments: int = 1
    maximum_fragments: int = 99

    def validate_parts(self, parts: tuple[AssemblyPart, ...]) -> AssemblyValidation:
        if len(parts) < self.minimum_fragments:
            return AssemblyValidation.fail(
                f"{self.display_name} requires at least {self.minimum_fragments} fragment(s)"
            )
        if len(parts) > self.maximum_fragments:
            return AssemblyValidation.fail(
                f"{self.display_name} supports at most {self.maximum_fragments} fragments"
            )
        duplicate_ids = _duplicate_part_ids(parts)
        if duplicate_ids:
            return AssemblyValidation.fail(
                f"duplicate assembly part ids: {', '.join(duplicate_ids)}"
            )
        return AssemblyValidation.ok()

    @abstractmethod
    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        """Return deterministic primer-design placeholders for T-704 to refine."""

    @abstractmethod
    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> AssemblyPlanSummary:
        """Compile a typed assembly plan summary."""

    def _require_valid_parts(self, parts: tuple[AssemblyPart, ...]) -> None:
        validation = self.validate_parts(parts)
        if not validation.valid:
            raise ValueError("; ".join(validation.errors))


class AssemblyEngine:
    """Registry-backed facade for downstream orchestration tasks."""

    def __init__(self, strategies: tuple[AssemblyStrategy, ...] | None = None) -> None:
        registered = default_strategies() if strategies is None else strategies
        if not registered:
            raise ValueError("AssemblyEngine requires at least one strategy")
        by_id: dict[AssemblyMethodId, AssemblyStrategy] = {}
        for strategy in registered:
            if strategy.method_id in by_id:
                raise ValueError(f"duplicate assembly strategy: {strategy.method_id}")
            by_id[strategy.method_id] = strategy
        self._strategies = by_id

    @property
    def strategies(self) -> tuple[AssemblyStrategy, ...]:
        return tuple(self._strategies.values())

    def strategy_for(self, method_id: AssemblyMethodId | str) -> AssemblyStrategy:
        key = AssemblyMethodId(str(method_id))
        if key not in self._strategies:
            raise KeyError(f"unknown assembly method: {method_id}")
        return self._strategies[key]

    def compile_plan(
        self,
        method_id: AssemblyMethodId | str,
        parts: tuple[AssemblyPart, ...],
    ) -> AssemblyPlanSummary:
        return self.strategy_for(method_id).compile_assembly_plan(parts)

    def design_primers(
        self,
        method_id: AssemblyMethodId | str,
        parts: tuple[AssemblyPart, ...],
    ) -> tuple[PrimerDesign, ...]:
        return self.strategy_for(method_id).design_primers(parts)


def default_strategies() -> tuple[AssemblyStrategy, ...]:
    from engine.assembly.gateway import GatewayStrategy
    from engine.assembly.gibson import GibsonLikeStrategy, InFusionStrategy, NEBuilderHiFiStrategy
    from engine.assembly.golden_gate import (
        GoldenBraidStrategy,
        GreenGateStrategy,
        JUMPStrategy,
        LoopStrategy,
        MIDASStrategy,
        MoCloStrategy,
        TypeIISGoldenGateStrategy,
        YTKStrategy,
    )
    from engine.assembly.iva import IVAStrategy
    from engine.assembly.lic import LICStrategy
    from engine.assembly.restriction_ligation import RestrictionLigationStrategy
    from engine.assembly.slic import SLICStrategy
    from engine.assembly.user import USERStrategy
    from engine.assembly.yeast_tar import YeastTARStrategy

    return (
        RestrictionLigationStrategy(),
        GibsonLikeStrategy(),
        NEBuilderHiFiStrategy(),
        InFusionStrategy(),
        TypeIISGoldenGateStrategy(),
        MoCloStrategy(),
        LoopStrategy(),
        YTKStrategy(),
        GreenGateStrategy(),
        GoldenBraidStrategy(),
        JUMPStrategy(),
        MIDASStrategy(),
        GatewayStrategy(),
        LICStrategy(),
        SLICStrategy(),
        USERStrategy(),
        IVAStrategy(),
        YeastTARStrategy(),
    )


def expected_product_record(
    record_id: str,
    sequence: str,
    *,
    topology: Literal["linear", "circular"] = "linear",
) -> SequenceRecord:
    return SequenceRecord(
        id=record_id,
        sequence=DnaSequence(sequence),
        topology=topology,
        molecule_type=MoleculeType.DS_DNA,
    )


def fragment_ids(parts: tuple[AssemblyPart, ...]) -> tuple[str, ...]:
    return tuple(part.id for part in parts)


def concatenate_parts(parts: tuple[AssemblyPart, ...]) -> str:
    return "".join(part.sequence for part in parts)


def overlap_assembled_sequence(parts: tuple[AssemblyPart, ...], overlaps: tuple[int, ...]) -> str:
    if len(overlaps) != max(0, len(parts) - 1):
        raise ValueError("overlap count must describe each junction")
    sequence = parts[0].sequence
    for index, overlap_length in enumerate(overlaps):
        next_part = parts[index + 1]
        sequence += next_part.sequence[overlap_length:]
    return sequence


def overlap_lengths_from_parts(
    parts: tuple[AssemblyPart, ...],
    default_length: int,
) -> tuple[int, ...]:
    overlaps: list[int] = []
    for left, right in pairwise(parts):
        if left.right_overlap or right.left_overlap:
            if left.right_overlap != right.left_overlap:
                raise ValueError(f"overlap mismatch between {left.id} and {right.id}")
            overlaps.append(len(left.right_overlap))
            continue
        inferred = _longest_suffix_prefix(left.sequence, right.sequence, default_length)
        if inferred < default_length:
            raise ValueError(
                f"missing {default_length} bp overlap between {left.id} and {right.id}"
            )
        overlaps.append(inferred)
    return tuple(overlaps)


def generic_primers(parts: tuple[AssemblyPart, ...], purpose: str) -> tuple[PrimerDesign, ...]:
    primers: list[PrimerDesign] = []
    for part in parts:
        forward = part.sequence[: min(18, len(part.sequence))]
        reverse = reverse_complement(part.sequence[-min(18, len(part.sequence)) :])
        primers.append(
            PrimerDesign(
                name=f"{part.id}_fwd",
                template_part_id=part.id,
                sequence=forward,
                purpose=purpose,
            )
        )
        primers.append(
            PrimerDesign(
                name=f"{part.id}_rev",
                template_part_id=part.id,
                sequence=reverse,
                purpose=purpose,
            )
        )
    return tuple(primers)


def reverse_complement(sequence: str) -> str:
    return sequence.upper().translate(str.maketrans("ACGT", "TGCA"))[::-1]


def _duplicate_part_ids(parts: tuple[AssemblyPart, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for part in parts:
        if part.id in seen:
            duplicates.add(part.id)
        seen.add(part.id)
    return tuple(sorted(duplicates))


def _longest_suffix_prefix(left: str, right: str, minimum: int) -> int:
    max_len = min(len(left), len(right))
    for length in range(max_len, minimum - 1, -1):
        if left[-length:] == right[:length]:
            return length
    return 0
