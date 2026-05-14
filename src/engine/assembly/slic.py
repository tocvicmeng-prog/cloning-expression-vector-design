"""
module_id: engine.assembly.slic
file: src/engine/assembly/slic.py
task_id: T-703
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.assembly_plan import OverlapAssemblyPlan
from domain.types.ids import AssemblyMethodId
from engine.assembly.base import AssemblyPart, PrimerDesign
from engine.assembly.gibson import GibsonLikeStrategy


@dataclass(frozen=True)
class SLICPlan(OverlapAssemblyPlan):
    t4_pol_conditions: str = "T4 DNA polymerase chew-back without ligase"


class SLICStrategy(GibsonLikeStrategy):
    def __init__(self) -> None:
        super().__init__(
            method_id="slic",
            display_name="SLIC",
            polymerase="T4 DNA polymerase",
            default_overlap_length=20,
        )
        self._t4_pol_conditions = "T4 DNA polymerase chew-back, dCTP stop, anneal without ligase"

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        primers = super().design_primers(parts)
        return tuple(
            PrimerDesign(
                name=primer.name,
                template_part_id=primer.template_part_id,
                sequence=primer.sequence,
                purpose="SLIC chew-back tail addition",
            )
            for primer in primers
        )

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> SLICPlan:
        base_plan = super().compile_assembly_plan(parts)
        return SLICPlan(
            method=AssemblyMethodId("slic"),
            fragments=base_plan.fragments,
            expected_product=base_plan.expected_product,
            expected_byproducts=base_plan.expected_byproducts,
            verification_checkpoints=base_plan.verification_checkpoints,
            expected_failure_modes=base_plan.expected_failure_modes,
            overlap_lengths=base_plan.overlap_lengths,
            polymerase=base_plan.polymerase,
            molar_ratio_table=base_plan.molar_ratio_table,
            t4_pol_conditions=self._t4_pol_conditions,
        )
