"""
module_id: domain.ports.profile_signing
file: src/domain/ports/profile_signing.py
task_id: T-314a

Authorisation-profile signing Protocols.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from domain.security import (
    AdminPrincipal,
    AuthorisationProfile,
    DeveloperBootstrapPrincipal,
    ProfileSignature,
)
from domain.types.signing_errors import ProfileVerificationResult


@runtime_checkable
class AuthorisationProfileSigner(Protocol):
    def sign(
        self,
        profile: AuthorisationProfile,
        admin: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> ProfileSignature: ...


@runtime_checkable
class AuthorisationProfileVerifier(Protocol):
    def verify(self, profile: AuthorisationProfile) -> ProfileVerificationResult: ...
