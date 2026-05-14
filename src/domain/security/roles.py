"""
module_id: domain.security.roles
file: src/domain/security/roles.py
task_id: T-304

Security roles and v1.3 one-way inheritance semantics.
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class SecurityRole(Enum):
    DEVELOPER = "developer"
    ADMINISTRATOR = "administrator"
    REVIEWER = "reviewer"
    USER = "user"


ROLE_INHERITS: Final[dict[SecurityRole, frozenset[SecurityRole]]] = {
    SecurityRole.DEVELOPER: frozenset(),
    SecurityRole.ADMINISTRATOR: frozenset({SecurityRole.REVIEWER}),
    SecurityRole.REVIEWER: frozenset(),
    SecurityRole.USER: frozenset(),
}
