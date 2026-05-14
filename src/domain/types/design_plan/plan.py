"""
module_id: domain.types.design_plan.plan
file: src/domain/types/design_plan/plan.py
task_id: T-306

Always-renderable, non-operational design realisation plan.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.assembly_plan import AssemblyPlanSummary
from domain.types.design_plan.guard import reject_sop_protected_values
from domain.types.design_plan.reviewer_packet import ReviewerPacket
from domain.types.design_plan.verification_artefacts import VerificationArtefact

PrimerSet = tuple[str, ...]
Checkpoint = str
ApprovalRequirement = str


@dataclass(frozen=True)
class DesignRealisationPlan:
    construct_id: str
    assembly_plan: AssemblyPlanSummary
    primer_set: PrimerSet
    qc_checkpoints: tuple[Checkpoint, ...]
    expected_verification_artefacts: tuple[VerificationArtefact, ...]
    institutional_approvals_required: tuple[ApprovalRequirement, ...]
    reviewer_packet: ReviewerPacket

    def __post_init__(self) -> None:
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not self.primer_set:
            raise ValueError("DesignRealisationPlan requires a primer_set")
        reject_sop_protected_values(self)
