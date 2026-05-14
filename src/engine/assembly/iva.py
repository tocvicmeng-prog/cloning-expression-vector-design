"""
module_id: engine.assembly.iva
file: src/engine/assembly/iva.py
task_id: T-703
"""

from __future__ import annotations

from domain.types.assembly_plan import InVivoAssemblyPlan
from domain.types.ids import AssemblyMethodId, HostId
from engine.assembly.base import (
    AssemblyPart,
    AssemblyStrategy,
    PrimerDesign,
    concatenate_parts,
    expected_product_record,
    fragment_ids,
    generic_primers,
)

DEFAULT_IVA_HOST = HostId("ecoli-recA-plus")


class IVAStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("iva")
    display_name = "In-vivo assembly"
    minimum_fragments = 2
    maximum_fragments = 10

    def __init__(self, *, host_strain: HostId = DEFAULT_IVA_HOST) -> None:
        self._host_strain = host_strain

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, "in-vivo recombination arm addition")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> InVivoAssemblyPlan:
        self._require_valid_parts(parts)
        return InVivoAssemblyPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record("iva_product", concatenate_parts(parts)),
            host_strain=self._host_strain,
            recombination_arms=tuple(f"{part.id}:40bp-arm" for part in parts),
            verification_checkpoints=("colony_pcr", "junction_sanger"),
            expected_failure_modes=("host_recombination_failure",),
        )
