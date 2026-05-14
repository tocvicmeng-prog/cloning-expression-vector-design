"""
module_id: domain.types.governance.role_snapshot
file: src/domain/types/governance/role_snapshot.py
task_id: T-306

Role snapshot value object for replay-safe decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.security import PrincipalId, SecurityRole


@dataclass(frozen=True)
class RoleSnapshot:
    principal_id: PrincipalId
    role: SecurityRole
    institution_id: str
    captured_at_utc: datetime
    credentials_verified_at_utc: datetime

    def __post_init__(self) -> None:
        if not str(self.principal_id):
            raise ValueError("principal_id cannot be empty")
        if not self.institution_id:
            raise ValueError("institution_id cannot be empty")
        if self.captured_at_utc.tzinfo is None:
            raise ValueError("captured_at_utc must be timezone-aware")
        if self.credentials_verified_at_utc.tzinfo is None:
            raise ValueError("credentials_verified_at_utc must be timezone-aware")
