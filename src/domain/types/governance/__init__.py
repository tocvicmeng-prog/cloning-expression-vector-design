"""
module_id: domain.types.governance
file: src/domain/types/governance/__init__.py
task_id: T-306
"""

from __future__ import annotations

from domain.types.governance.decision_record import DecisionRecord
from domain.types.governance.role_snapshot import RoleSnapshot

__all__ = ["DecisionRecord", "RoleSnapshot"]
