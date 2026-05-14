"""
module_id: domain.ports.sop_template
file: src/domain/ports/sop_template.py
task_id: T-316a

SOP-template read/write/bootstrap and signing Protocols.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal
from domain.types.derivation import SopTemplateId
from domain.types.signing_errors import SopTemplateVerificationResult
from domain.types.sop_template import (
    SopTemplate,
    SopTemplateRevocation,
    SopTemplateSignature,
    SopTemplateVersion,
)


@runtime_checkable
class SopTemplateReadPort(Protocol):
    def get_template(self, template_id: SopTemplateId) -> SopTemplate: ...
    def list_templates(self) -> tuple[SopTemplate, ...]: ...


@runtime_checkable
class SopTemplateAdminWritePort(Protocol):
    def write_mint(
        self,
        template: SopTemplate,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateVersion: ...
    def write_modify(
        self,
        template: SopTemplate,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateVersion: ...
    def write_revoke(
        self,
        template_id: SopTemplateId,
        reason: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateRevocation: ...


@runtime_checkable
class SopTemplateBootstrapPort(Protocol):
    def bootstrap_initial_templates(
        self,
        developer: DeveloperBootstrapPrincipal,
    ) -> tuple[SopTemplateVersion, ...]: ...


@runtime_checkable
class SopTemplateSigner(Protocol):
    def sign(
        self,
        template: SopTemplate,
        admin: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateSignature: ...


@runtime_checkable
class SopTemplateVerifier(Protocol):
    def verify(self, template: SopTemplate) -> SopTemplateVerificationResult: ...
