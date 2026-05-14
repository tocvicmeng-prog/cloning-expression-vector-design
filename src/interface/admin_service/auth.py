"""
module_id: interface.admin_service.auth
file: src/interface/admin_service/auth.py
task_id: T-1103b

Admin-service principal-token authentication.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from domain.security import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    DeveloperPrincipal,
    InstitutionId,
    Principal,
    PrincipalId,
    ReviewerPrincipal,
    SecurityRole,
    UserPrincipal,
)
from domain.types.admin_ipc import SignedAdminPrincipalToken


class AdminServiceAuthenticationError(PermissionError):
    """Raised when an admin-service credential cannot be authenticated."""


class AdminServiceAuthorisationError(PermissionError):
    """Raised when an authenticated principal lacks authority for an operation."""


class AdminServiceSecurityEventSink(Protocol):
    def authentication_failed(self, principal_id: str, reason: str) -> None: ...
    def permission_denied(self, principal_id: str, operation: str, reason: str) -> None: ...


class AdminPrincipalTokenVerifier(Protocol):
    def verify(self, token: SignedAdminPrincipalToken) -> bool: ...


@dataclass(frozen=True, slots=True)
class AdminSecurityEvent:
    event_type: str
    principal_id: str
    reason: str
    operation: str | None = None


class InMemoryAdminServiceSecurityLog:
    """Small test/development event sink for admin-service auth decisions."""

    def __init__(self) -> None:
        self._events: list[AdminSecurityEvent] = []

    @property
    def events(self) -> tuple[AdminSecurityEvent, ...]:
        return tuple(self._events)

    def authentication_failed(self, principal_id: str, reason: str) -> None:
        self._events.append(
            AdminSecurityEvent(
                event_type="authentication_failed",
                principal_id=principal_id,
                reason=reason,
            )
        )

    def permission_denied(self, principal_id: str, operation: str, reason: str) -> None:
        self._events.append(
            AdminSecurityEvent(
                event_type="permission_denied",
                principal_id=principal_id,
                operation=operation,
                reason=reason,
            )
        )


@dataclass(frozen=True, slots=True)
class AuthenticatedAdminCaller:
    token: SignedAdminPrincipalToken
    principal: Principal


class AdminServiceAuthenticator:
    """Validates the T-1103a signed-token envelope and binds a domain principal."""

    def __init__(
        self,
        *,
        trusted_signing_key_versions: frozenset[str] | None = None,
        token_verifier: AdminPrincipalTokenVerifier | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._trusted_signing_key_versions = trusted_signing_key_versions
        self._token_verifier = token_verifier
        self._clock = clock or (lambda: datetime.now(UTC))

    def authenticate(self, token: SignedAdminPrincipalToken) -> AuthenticatedAdminCaller:
        now = self._clock()
        if token.issued_at_utc > now:
            raise AdminServiceAuthenticationError("admin-service token is not yet valid")
        if token.expires_at_utc <= now:
            raise AdminServiceAuthenticationError("admin-service token has expired")
        if (
            self._trusted_signing_key_versions is not None
            and token.signing_key_version not in self._trusted_signing_key_versions
        ):
            raise AdminServiceAuthenticationError("admin-service token signing key is not trusted")
        if self._token_verifier is not None and not self._token_verifier.verify(token):
            raise AdminServiceAuthenticationError("admin-service token signature is invalid")
        return AuthenticatedAdminCaller(token=token, principal=_principal_from_token(token))


def _principal_from_token(token: SignedAdminPrincipalToken) -> Principal:
    principal_id = PrincipalId(token.principal_id)
    institution = InstitutionId(token.institution_id)
    if token.principal_role == SecurityRole.ADMINISTRATOR.value:
        return AdminPrincipal(
            id=principal_id,
            role=SecurityRole.ADMINISTRATOR,
            institution=institution,
            credentials_verified_at=token.issued_at_utc,
        )
    if token.principal_role == "developer_bootstrap":
        return DeveloperBootstrapPrincipal(
            id=principal_id,
            role=SecurityRole.DEVELOPER,
            institution=institution,
            credentials_verified_at=token.issued_at_utc,
            is_bootstrap=True,
            bootstrap_expires_at=token.expires_at_utc,
        )
    if token.principal_role == SecurityRole.DEVELOPER.value:
        return DeveloperPrincipal(
            id=principal_id,
            role=SecurityRole.DEVELOPER,
            institution=institution,
            credentials_verified_at=token.issued_at_utc,
        )
    if token.principal_role == SecurityRole.REVIEWER.value:
        return ReviewerPrincipal(
            id=principal_id,
            role=SecurityRole.REVIEWER,
            institution=institution,
            credentials_verified_at=token.issued_at_utc,
        )
    if token.principal_role == SecurityRole.USER.value:
        return UserPrincipal(
            id=principal_id,
            role=SecurityRole.USER,
            institution=institution,
            credentials_verified_at=token.issued_at_utc,
        )
    raise AdminServiceAuthenticationError("admin-service token principal role is unknown")


__all__ = [
    "AdminPrincipalTokenVerifier",
    "AdminSecurityEvent",
    "AdminServiceAuthenticationError",
    "AdminServiceAuthenticator",
    "AdminServiceAuthorisationError",
    "AdminServiceSecurityEventSink",
    "AuthenticatedAdminCaller",
    "InMemoryAdminServiceSecurityLog",
]
