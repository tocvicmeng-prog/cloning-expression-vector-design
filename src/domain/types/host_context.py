"""
module_id: domain.types.host_context
file: src/domain/types/host_context.py
task_id: T-303

Role-keyed host context value object.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.enums import HostRole
from domain.types.ids import HostId, require_non_empty

HostConstraint = str
ApprovalContext = str


@dataclass(frozen=True)
class HostContext:
    role: HostRole
    host_id: HostId
    constraints: tuple[HostConstraint, ...] = ()
    approval_context: ApprovalContext | None = None

    def __post_init__(self) -> None:
        require_non_empty(str(self.host_id), "host_id")
        for constraint in self.constraints:
            require_non_empty(constraint, "host constraint")
