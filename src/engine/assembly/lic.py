"""
module_id: engine.assembly.lic
file: src/engine/assembly/lic.py
task_id: T-703
"""

from __future__ import annotations

from domain.types.assembly_plan import LICPlan
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


class LICStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("lic")
    display_name = "Ligation-independent cloning"
    minimum_fragments = 1
    maximum_fragments = 4

    def __init__(self, *, t4_pol_conditions: str = "T4 DNA polymerase chew-back") -> None:
        self._t4_pol_conditions = t4_pol_conditions

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, "LIC tail addition")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> LICPlan:
        self._require_valid_parts(parts)
        return LICPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record("lic_product", concatenate_parts(parts)),
            tail_design=tuple(f"{part.id}:LIC-tail" for part in parts),
            t4_pol_conditions=self._t4_pol_conditions,
            verification_checkpoints=("junction_sanger",),
            expected_failure_modes=("insufficient_chewback",),
        )
