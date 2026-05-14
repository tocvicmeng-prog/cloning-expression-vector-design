"""
module_id: engine.assembly.restriction_ligation
file: src/engine/assembly/restriction_ligation.py
task_id: T-703
"""

from __future__ import annotations

from domain.types.assembly_plan import RestrictionLigationPlan
from domain.types.ids import AssemblyMethodId
from engine.assembly.base import (
    AssemblyPart,
    AssemblyStrategy,
    AssemblyValidation,
    PrimerDesign,
    concatenate_parts,
    expected_product_record,
    fragment_ids,
    generic_primers,
)


class RestrictionLigationStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("restriction-ligation")
    display_name = "Restriction ligation"
    minimum_fragments = 2
    maximum_fragments = 2

    def __init__(
        self,
        *,
        enzymes: frozenset[str] = frozenset({"EcoRI", "XhoI"}),
        ligation_conditions: str = "T4 DNA ligase, compatible cohesive ends",
        dephosphorylation: bool = False,
    ) -> None:
        self._enzymes = enzymes
        self._ligation_conditions = ligation_conditions
        self._dephosphorylation = dephosphorylation

    def validate_parts(self, parts: tuple[AssemblyPart, ...]) -> AssemblyValidation:
        base = super().validate_parts(parts)
        if not base.valid:
            return base
        if not self._enzymes:
            return AssemblyValidation.fail("restriction ligation requires at least one enzyme")
        return AssemblyValidation.ok()

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, "restriction-site addition")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> RestrictionLigationPlan:
        self._require_valid_parts(parts)
        return RestrictionLigationPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record(
                "restriction_ligation_product",
                concatenate_parts(parts),
            ),
            enzymes=self._enzymes,
            dephosphorylation=self._dephosphorylation,
            ligation_conditions=self._ligation_conditions,
            verification_checkpoints=("diagnostic_digest", "junction_sanger"),
            expected_failure_modes=("vector_religation", "wrong_insert_orientation"),
        )
