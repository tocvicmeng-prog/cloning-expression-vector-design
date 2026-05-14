"""
module_id: engine.assembly.gibson
file: src/engine/assembly/gibson.py
task_id: T-703
"""

from __future__ import annotations

from domain.types.assembly_plan import OverlapAssemblyPlan
from domain.types.ids import AssemblyMethodId
from engine.assembly.base import (
    AssemblyPart,
    AssemblyStrategy,
    AssemblyValidation,
    PrimerDesign,
    expected_product_record,
    fragment_ids,
    generic_primers,
    overlap_assembled_sequence,
    overlap_lengths_from_parts,
)


class GibsonLikeStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("gibson")
    display_name = "Gibson-like overlap assembly"
    minimum_fragments = 2
    maximum_fragments = 10

    def __init__(
        self,
        *,
        method_id: str = "gibson",
        display_name: str = "Gibson-like overlap assembly",
        polymerase: str = "Gibson exonuclease/polymerase/ligase mix",
        default_overlap_length: int = 20,
    ) -> None:
        self.method_id = AssemblyMethodId(method_id)
        self.display_name = display_name
        self._polymerase = polymerase
        self._default_overlap_length = default_overlap_length

    def validate_parts(self, parts: tuple[AssemblyPart, ...]) -> AssemblyValidation:
        base = super().validate_parts(parts)
        if not base.valid:
            return base
        try:
            overlap_lengths_from_parts(parts, self._default_overlap_length)
        except ValueError as error:
            return AssemblyValidation.fail(str(error))
        return AssemblyValidation.ok()

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, "overlap-tail addition")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> OverlapAssemblyPlan:
        self._require_valid_parts(parts)
        overlaps = overlap_lengths_from_parts(parts, self._default_overlap_length)
        return OverlapAssemblyPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record(
                f"{self.method_id}_product",
                overlap_assembled_sequence(parts, overlaps),
            ),
            overlap_lengths=overlaps,
            polymerase=self._polymerase,
            molar_ratio_table=tuple((part.id, 1.0) for part in parts),
            verification_checkpoints=("junction_sanger",),
            expected_failure_modes=("insufficient_overlap", "template_carryover"),
        )


class NEBuilderHiFiStrategy(GibsonLikeStrategy):
    def __init__(self) -> None:
        super().__init__(
            method_id="nebuilder-hifi",
            display_name="NEBuilder HiFi",
            polymerase="NEBuilder HiFi DNA Assembly Master Mix",
            default_overlap_length=20,
        )


class InFusionStrategy(GibsonLikeStrategy):
    def __init__(self) -> None:
        super().__init__(
            method_id="in-fusion",
            display_name="In-Fusion",
            polymerase="In-Fusion recombinase/polymerase mix",
            default_overlap_length=15,
        )
