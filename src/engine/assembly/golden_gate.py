"""
module_id: engine.assembly.golden_gate
file: src/engine/assembly/golden_gate.py
task_id: T-703
"""

from __future__ import annotations

from domain.types.assembly_plan import TypeIISAssemblyPlan
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
from engine.overhang import (
    POTAPOV_2018_HIGH_FIDELITY_SETS,
    OverhangDesignRequest,
    OverhangSetOptimiser,
)


class TypeIISGoldenGateStrategy(AssemblyStrategy):
    method_id = AssemblyMethodId("golden-gate")
    display_name = "Golden Gate"
    minimum_fragments = 2
    maximum_fragments = 35

    def __init__(
        self,
        *,
        method_id: str = "golden-gate",
        display_name: str = "Golden Gate",
        enzyme: str = "BsaI-HFv2",
        cycling_profile: str = "30 cycles 37C/16C, final heat inactivation",
        overhang_optimiser: OverhangSetOptimiser | None = None,
        candidate_overhangs: tuple[str, ...] = (),
    ) -> None:
        self.method_id = AssemblyMethodId(method_id)
        self.display_name = display_name
        self._enzyme = enzyme
        self._cycling_profile = cycling_profile
        self._overhang_optimiser = (
            OverhangSetOptimiser() if overhang_optimiser is None else overhang_optimiser
        )
        self._candidate_overhangs = candidate_overhangs or POTAPOV_2018_HIGH_FIDELITY_SETS[15]

    def validate_parts(self, parts: tuple[AssemblyPart, ...]) -> AssemblyValidation:
        base = super().validate_parts(parts)
        if not base.valid:
            return base
        overhangs = _provided_overhangs(parts)
        if overhangs and len(set(overhangs)) != len(overhangs):
            return AssemblyValidation.fail("Golden Gate overhangs must be unique")
        return AssemblyValidation.ok()

    def design_primers(self, parts: tuple[AssemblyPart, ...]) -> tuple[PrimerDesign, ...]:
        self._require_valid_parts(parts)
        return generic_primers(parts, f"{self._enzyme} site and overhang addition")

    def compile_assembly_plan(self, parts: tuple[AssemblyPart, ...]) -> TypeIISAssemblyPlan:
        self._require_valid_parts(parts)
        provided_overhangs = _provided_overhangs(parts)
        if provided_overhangs:
            score = self._overhang_optimiser.score(provided_overhangs)
        else:
            request = OverhangDesignRequest(
                set_size=len(parts) + 1,
                candidate_overhangs=self._candidate_overhangs,
                minimum_fidelity=0.90,
                minimum_per_overhang_fidelity=0.99,
                max_pair_crosstalk=0.02,
                node_budget=80_000,
            )
            score = self._overhang_optimiser.optimise(request).score
        return TypeIISAssemblyPlan(
            method=self.method_id,
            fragments=fragment_ids(parts),
            expected_product=expected_product_record(
                f"{self.method_id}_product",
                concatenate_parts(parts),
                topology="circular",
            ),
            enzyme=self._enzyme,
            overhang_set=score.overhangs,
            cycling_profile=self._cycling_profile,
            overhang_fidelity_score=score.fidelity,
            verification_checkpoints=("junction_sanger", "colony_pcr"),
            expected_failure_modes=("overhang_misligation", "internal_type_iis_site"),
        )


class MoCloStrategy(TypeIISGoldenGateStrategy):
    def __init__(self) -> None:
        super().__init__(method_id="moclo", display_name="MoClo", enzyme="BsaI-HFv2")


class LoopStrategy(TypeIISGoldenGateStrategy):
    def __init__(self) -> None:
        super().__init__(method_id="loop", display_name="Loop assembly", enzyme="BsaI-HFv2")


class YTKStrategy(TypeIISGoldenGateStrategy):
    def __init__(self) -> None:
        super().__init__(method_id="ytk", display_name="Yeast Toolkit", enzyme="BsmBI-v2")


class GreenGateStrategy(TypeIISGoldenGateStrategy):
    def __init__(self) -> None:
        super().__init__(method_id="greengate", display_name="GreenGate", enzyme="BsaI-HFv2")


class GoldenBraidStrategy(TypeIISGoldenGateStrategy):
    def __init__(self) -> None:
        super().__init__(method_id="goldenbraid", display_name="GoldenBraid", enzyme="BsaI-HFv2")


class JUMPStrategy(TypeIISGoldenGateStrategy):
    def __init__(self) -> None:
        super().__init__(method_id="jump", display_name="JUMP", enzyme="BsaI-HFv2")


class MIDASStrategy(TypeIISGoldenGateStrategy):
    def __init__(self) -> None:
        super().__init__(method_id="midas", display_name="MIDAS", enzyme="BbsI-HF")


def _provided_overhangs(parts: tuple[AssemblyPart, ...]) -> tuple[str, ...]:
    overhangs: list[str] = []
    for part in parts:
        if part.left_overhang:
            overhangs.append(part.left_overhang)
        if part.right_overhang:
            overhangs.append(part.right_overhang)
    return tuple(dict.fromkeys(overhangs))
