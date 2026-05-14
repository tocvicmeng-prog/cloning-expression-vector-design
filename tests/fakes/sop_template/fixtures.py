"""
module_id: tests.fakes.sop_template.fixtures
file: tests/fakes/sop_template/fixtures.py
task_id: T-316a
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from domain.security import AdminPrincipal, InstitutionId, PrincipalId, SecurityRole
from domain.types.derivation import Semver, SopTemplateId
from domain.types.sop_template import SopTemplate, SopTemplateSignature

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def admin_principal() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def unsigned_template() -> SopTemplate:
    return SopTemplate(
        template_id=SopTemplateId("sop-template-1"),
        version=Semver("1.0.0"),
        name="Institutional assembly SOP",
        description="Fixture template for signing tests.",
        content_markdown="Follow the institution-controlled SOP.",
        hazard_notes=("Use institutional biosafety controls.",),
        required_approval_gate="OperationalProtocolAuthorised",
    )


def signed_template(signature: SopTemplateSignature) -> SopTemplate:
    return replace(unsigned_template(), signature=signature)
