"""
module_id: engine.assembly.gateway
file: src/engine/assembly/gateway.py
task_id: T-703
"""

from __future__ import annotations

from typing import Literal

from domain.types.assembly_plan import GatewayPlan
from domain.types.ids import AssemblyMethodId
from engine.assembly.base import (
    AssemblyPart,
    AssemblyStrategy,
    PrimerDesign,
    expected_product_record,
    fragment_ids,
    generic_primers,
)


class GatewayStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("gateway")
    display_name = "Gateway"
    minimum_fragments = 1
    maximum_fragments = 5

    def __init__(
        self,
        *,
        reaction: Literal["BP", "LR"] = "LR",
        enzyme_kit: str = "Gateway LR Clonase II",
    ) -> None:
        self._reaction = reaction
        self._enzyme_kit = enzyme_kit

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, "att-site addition")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> GatewayPlan:
        self._require_valid_parts(parts)
        scars = tuple(f"attB{index + 1}" for index in range(max(1, len(parts))))
        product_sequence = "G".join(part.sequence for part in parts)
        return GatewayPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record("gateway_product", product_sequence),
            reaction=self._reaction,
            attB_scars=scars,
            enzyme_kit=self._enzyme_kit,
            verification_checkpoints=("junction_sanger",),
            expected_failure_modes=("wrong_entry_clone",),
        )
