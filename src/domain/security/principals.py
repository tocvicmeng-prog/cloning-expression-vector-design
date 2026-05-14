"""
module_id: domain.security.principals
file: src/domain/security/principals.py
task_id: T-304

Principal hierarchy and bootstrap authority predicate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from domain.security.identifiers import InstitutionId, PrincipalId, require_non_empty
from domain.security.roles import ROLE_INHERITS, SecurityRole


@dataclass(frozen=True)
class Principal:
    id: PrincipalId
    role: SecurityRole
    institution: InstitutionId
    credentials_verified_at: datetime

    def __post_init__(self) -> None:
        require_non_empty(str(self.id), "principal id")
        require_non_empty(str(self.institution), "institution")
        if self.credentials_verified_at.tzinfo is None:
            raise ValueError("credentials_verified_at must be timezone-aware")

    def can_act_as(self, required_role: SecurityRole) -> bool:
        return self.role == required_role or required_role in ROLE_INHERITS[self.role]

    @property
    def has_bootstrap_authority(self) -> bool:
        return False


@dataclass(frozen=True)
class UserPrincipal(Principal):
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.role is not SecurityRole.USER:
            raise ValueError("UserPrincipal must carry SecurityRole.USER")


@dataclass(frozen=True)
class ReviewerPrincipal(Principal):
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.role is not SecurityRole.REVIEWER:
            raise ValueError("ReviewerPrincipal must carry SecurityRole.REVIEWER")


@dataclass(frozen=True)
class AdminPrincipal(Principal):
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.role is not SecurityRole.ADMINISTRATOR:
            raise ValueError("AdminPrincipal must carry SecurityRole.ADMINISTRATOR")


@dataclass(frozen=True)
class DeveloperPrincipal(Principal):
    def __post_init__(self) -> None:
        super().__post_init__()
        if self.role is not SecurityRole.DEVELOPER:
            raise ValueError("DeveloperPrincipal must carry SecurityRole.DEVELOPER")


@dataclass(frozen=True)
class DeveloperBootstrapPrincipal(DeveloperPrincipal):
    is_bootstrap: bool
    bootstrap_expires_at: datetime

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.bootstrap_expires_at.tzinfo is None:
            raise ValueError("bootstrap_expires_at must be timezone-aware")

    @property
    def has_bootstrap_authority(self) -> bool:
        return self.is_bootstrap and self.bootstrap_expires_at > datetime.now(UTC)
