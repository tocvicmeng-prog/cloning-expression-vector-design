"""
module_id: engine.assembly.user
file: src/engine/assembly/user.py
task_id: T-703
"""

from __future__ import annotations

from domain.types.assembly_plan import USERPlan
from domain.types.ids import AssemblyMethodId
from engine.assembly.base import (
    AssemblyPart,
    AssemblyStrategy,
    PrimerDesign,
    concatenate_parts,
    expected_product_record,
    fragment_ids,
    generic_primers,
)


class USERStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("user")
    display_name = "USER cloning"
    minimum_fragments = 1
    maximum_fragments = 8

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, "uracil-containing primer extension")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> USERPlan:
        self._require_valid_parts(parts)
        positions = tuple(index * 10 for index, _part in enumerate(parts, start=1))
        return USERPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record("user_product", concatenate_parts(parts)),
            dU_positions=positions,
            primer_extensions=tuple(f"{part.id}:dU-tail" for part in parts),
            verification_checkpoints=("junction_sanger",),
            expected_failure_modes=("incomplete_uracil_excision",),
        )
