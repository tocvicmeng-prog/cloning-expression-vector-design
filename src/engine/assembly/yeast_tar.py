"""
module_id: engine.assembly.yeast_tar
file: src/engine/assembly/yeast_tar.py
task_id: T-703
"""

from __future__ import annotations

from domain.types.assembly_plan import YeastTARPlan
from domain.types.ids import AssemblyMethodId, HostId, MarkerId
from engine.assembly.base import (
    AssemblyPart,
    AssemblyStrategy,
    PrimerDesign,
    concatenate_parts,
    expected_product_record,
    fragment_ids,
    generic_primers,
)

DEFAULT_YEAST_HOST = HostId("s-cerevisiae")
DEFAULT_YEAST_MARKER = MarkerId("ura3")


class YeastTARStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("yeast-tar")
    display_name = "Yeast TAR"
    minimum_fragments = 2
    maximum_fragments = 20

    def __init__(
        self,
        *,
        yeast_host: HostId = DEFAULT_YEAST_HOST,
        selection_marker: MarkerId = DEFAULT_YEAST_MARKER,
    ) -> None:
        self._yeast_host = yeast_host
        self._selection_marker = selection_marker

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, "yeast TAR homology-arm addition")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> YeastTARPlan:
        self._require_valid_parts(parts)
        return YeastTARPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record("yeast_tar_product", concatenate_parts(parts)),
            yeast_host=self._yeast_host,
            selection_marker=self._selection_marker,
            tar_fragment_design=tuple(f"{part.id}:TAR-arm" for part in parts),
            verification_checkpoints=("yeast_colony_pcr", "junction_sanger"),
            expected_failure_modes=("low_recombination_efficiency",),
        )
