"""
module_id: domain.types.sop_protected.protocol_step
file: src/domain/types/sop_protected/protocol_step.py
task_id: T-306

Operational protocol step; intentionally isolated in sop_protected.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.security import OperationalRole
from domain.types.sop_protected.deviation import DeviationPolicy
from domain.types.sop_protected.hazard import HazardClass


class ProtocolEdgeKind(Enum):
    THEN = "then"
    BRANCH = "branch"
    CHECKPOINT = "checkpoint"
    PARALLEL = "parallel"


@dataclass(frozen=True)
class ProtocolEdge:
    target_step_id: str
    kind: ProtocolEdgeKind

    def __post_init__(self) -> None:
        if not self.target_step_id:
            raise ValueError("target_step_id cannot be empty")


@dataclass(frozen=True)
class ProtocolStep:
    step_id: str
    action: str
    reagents: tuple[str, ...]
    quantities: tuple[str, ...]
    temperature_c: float | None
    duration: str | None
    rationale: str
    safety_note: str | None
    successors: tuple[ProtocolEdge, ...]
    sop_ref: str
    approval_gate: str | None
    hazard_class: HazardClass
    allowed_roles: frozenset[OperationalRole]
    checkpoint_criteria: tuple[str, ...]
    measured_outputs: tuple[str, ...]
    deviation_policy: DeviationPolicy
    decision_rule: str | None

    def __post_init__(self) -> None:
        if not self.step_id:
            raise ValueError("step_id cannot be empty")
        if not self.action:
            raise ValueError("protocol action cannot be empty")
        if not self.rationale:
            raise ValueError("protocol rationale cannot be empty")
        if not self.sop_ref:
            raise ValueError("sop_ref cannot be empty")
        if not self.allowed_roles:
            raise ValueError("ProtocolStep requires allowed_roles")
