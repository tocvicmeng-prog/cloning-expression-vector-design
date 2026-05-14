"""
module_id: domain.ports.authorisation
file: src/domain/ports/authorisation.py
task_id: T-311

Split authorisation read/admin/bootstrap ports.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from domain.security import (
    AdminPrincipal,
    AuthorisationProfile,
    DeveloperBootstrapPrincipal,
    Principal,
    UnsignedAuthorisationProfileDraft,
)


@runtime_checkable
class AuthorisationReadPort(Protocol):
    def get(self, profile_id: str) -> AuthorisationProfile: ...
    def read_own_profile(self, principal_id: str) -> AuthorisationProfile: ...
    def list_for_admin(self, admin_principal: Principal) -> tuple[AuthorisationProfile, ...]: ...


@runtime_checkable
class AuthorisationAdminWritePort(Protocol):
    def write_mint(self, profile: AuthorisationProfile, principal: AdminPrincipal) -> str: ...
    def write_modify(self, profile: AuthorisationProfile, principal: AdminPrincipal) -> str: ...
    def write_revoke(self, profile: AuthorisationProfile, principal: AdminPrincipal) -> str: ...


@runtime_checkable
class AuthorisationBootstrapPort(Protocol):
    def bootstrap_initial_admin(
        self,
        developer: DeveloperBootstrapPrincipal,
        draft: UnsignedAuthorisationProfileDraft,
    ) -> str: ...
