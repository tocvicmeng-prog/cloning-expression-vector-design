"""
module_id: domain.security.operational_role
file: src/domain/security/operational_role.py
task_id: T-304

Operational roles declared for a specific workflow, separate from security identity.
"""

from __future__ import annotations

from enum import Enum


class OperationalRole(Enum):
    DESIGNER = "designer"
    CLONING_OPERATOR = "cloning_operator"
    EXPRESSION_OPERATOR = "expression_operator"
    BIOSAFETY_REVIEWER = "biosafety_reviewer"
    VIEW_ONLY = "view_only"
