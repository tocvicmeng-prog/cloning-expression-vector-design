"""
module_id: domain.types.assembly_plan
file: src/domain/types/assembly_plan.py
task_id: T-303

Typed assembly plan summaries and chemistry-specific subclasses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from domain.sequence import SequenceRecord
from domain.types.ids import AssemblyMethodId, HostId, MarkerId, require_non_empty

FragmentSpec = str
Checkpoint = str
FailureMode = str
Enzyme = str
LigationConditions = str
Polymerase = str
FragmentRatio = tuple[str, float]
TypeIISEnzyme = str
OverhangSet = tuple[str, ...]
ThermocyclingProfile = str
AttScar = str
GatewayKitId = str
LicTail = str
T4PolConditions = str
Position = int
PrimerExtension = str
HomologyArm = str
TarFragment = str
EMPTY_HOST_ID = HostId("")
EMPTY_MARKER_ID = MarkerId("")


@dataclass(frozen=True)
class AssemblyPlanSummary:
    method: AssemblyMethodId
    fragments: tuple[FragmentSpec, ...]
    expected_product: SequenceRecord
    expected_byproducts: tuple[SequenceRecord, ...] = ()
    verification_checkpoints: tuple[Checkpoint, ...] = ()
    expected_failure_modes: tuple[FailureMode, ...] = ()

    def __post_init__(self) -> None:
        require_non_empty(str(self.method), "assembly method")
        if not self.fragments:
            raise ValueError("assembly plan requires at least one fragment")
        for fragment in self.fragments:
            require_non_empty(fragment, "fragment")


@dataclass(frozen=True)
class RestrictionLigationPlan(AssemblyPlanSummary):
    enzymes: frozenset[Enzyme] = frozenset()
    dephosphorylation: bool = False
    ligation_conditions: LigationConditions = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.enzymes:
            raise ValueError("restriction-ligation plan requires enzymes")
        require_non_empty(self.ligation_conditions, "ligation_conditions")


@dataclass(frozen=True)
class OverlapAssemblyPlan(AssemblyPlanSummary):
    overlap_lengths: tuple[int, ...] = ()
    polymerase: Polymerase = ""
    molar_ratio_table: tuple[FragmentRatio, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        if len(self.overlap_lengths) != max(0, len(self.fragments) - 1):
            raise ValueError("overlap_lengths must describe each fragment junction")
        if any(length < 1 for length in self.overlap_lengths):
            raise ValueError("overlap lengths must be positive")
        require_non_empty(self.polymerase, "polymerase")


@dataclass(frozen=True)
class TypeIISAssemblyPlan(AssemblyPlanSummary):
    enzyme: TypeIISEnzyme = ""
    overhang_set: OverhangSet = ()
    cycling_profile: ThermocyclingProfile = ""
    overhang_fidelity_score: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()
        require_non_empty(self.enzyme, "type IIS enzyme")
        if not self.overhang_set:
            raise ValueError("Type IIS plan requires an overhang_set")
        require_non_empty(self.cycling_profile, "cycling_profile")
        if not 0.0 <= self.overhang_fidelity_score <= 1.0:
            raise ValueError("overhang_fidelity_score must be between 0 and 1")


@dataclass(frozen=True)
class GatewayPlan(AssemblyPlanSummary):
    reaction: Literal["BP", "LR"] = "BP"
    attB_scars: tuple[AttScar, ...] = ()
    enzyme_kit: GatewayKitId = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        require_non_empty(self.enzyme_kit, "enzyme_kit")


@dataclass(frozen=True)
class LICPlan(AssemblyPlanSummary):
    tail_design: tuple[LicTail, ...] = ()
    t4_pol_conditions: T4PolConditions = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.tail_design:
            raise ValueError("LIC plan requires tail_design")
        require_non_empty(self.t4_pol_conditions, "t4_pol_conditions")


@dataclass(frozen=True)
class USERPlan(AssemblyPlanSummary):
    dU_positions: tuple[Position, ...] = ()
    primer_extensions: tuple[PrimerExtension, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.dU_positions:
            raise ValueError("USER plan requires dU_positions")
        if any(position < 0 for position in self.dU_positions):
            raise ValueError("dU_positions must be non-negative")
        if not self.primer_extensions:
            raise ValueError("USER plan requires primer_extensions")


@dataclass(frozen=True)
class InVivoAssemblyPlan(AssemblyPlanSummary):
    host_strain: HostId = EMPTY_HOST_ID
    recombination_arms: tuple[HomologyArm, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        require_non_empty(str(self.host_strain), "host_strain")
        if not self.recombination_arms:
            raise ValueError("in-vivo assembly plan requires recombination_arms")


@dataclass(frozen=True)
class YeastTARPlan(AssemblyPlanSummary):
    yeast_host: HostId = EMPTY_HOST_ID
    selection_marker: MarkerId = EMPTY_MARKER_ID
    tar_fragment_design: tuple[TarFragment, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        require_non_empty(str(self.yeast_host), "yeast_host")
        require_non_empty(str(self.selection_marker), "selection_marker")
        if not self.tar_fragment_design:
            raise ValueError("TAR plan requires tar_fragment_design")
