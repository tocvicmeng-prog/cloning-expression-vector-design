"""
module_id: tests.app.sop_template.test_admin_handler_sop_templates
file: tests/app/sop_template/test_admin_handler_sop_templates.py
task_id: T-316b
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from adapter.persistence import JsonlEventLog, SqliteAuthorisationStoreWrite, SqliteSopTemplateStore
from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateSigner,
    Ed25519InstitutionalSopTemplateVerifier,
)
from app.admin_action_handler import AdminActionHandler
from domain.events import (
    AuthorisationAttemptDenied,
    EventStream,
    SopTemplateMinted,
    SopTemplateModified,
    SopTemplateRevoked,
)
from domain.security import (
    InstitutionId,
    PrincipalId,
    ReviewerPrincipal,
    SecurityRole,
    UserPrincipal,
)
from domain.types.derivation import Semver
from tests.fakes.security.audit_append.brokers import FakeAdminAuditBroker
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.fakes.security.profile_signing.signers import FakeProfileSigner
from tests.fakes.sop_template.fixtures import admin_principal, unsigned_template

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def _user_principal() -> UserPrincipal:
    return UserPrincipal(
        id=PrincipalId("user-1"),
        role=SecurityRole.USER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def _reviewer_principal() -> ReviewerPrincipal:
    return ReviewerPrincipal(
        id=PrincipalId("reviewer-1"),
        role=SecurityRole.REVIEWER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def test_admin_handler_mints_modifies_and_revokes_signed_sop_template(
    tmp_path: Path,
) -> None:
    handler, store, governance_log, audit = _handler(tmp_path)
    minted = handler.mint_sop_template(
        admin_principal(),
        unsigned_template(),
        justification="Initial institutional SOP template.",
    )
    modified_template = replace(
        unsigned_template(),
        version=Semver("1.0.1"),
        content_markdown="Updated controlled SOP template.",
    )
    modified = handler.modify_sop_template(
        admin_principal(),
        modified_template,
        justification="Template clarified after review.",
    )
    revoked = handler.revoke_sop_template(
        admin_principal(),
        unsigned_template().template_id,
        reason="Template retired.",
    )

    events = governance_log.read_events("inst")
    assert minted.template.signature is not None
    assert modified.template.signature is not None
    assert str(modified.template_version.version) == "1.0.1"
    assert revoked.revocation.reason == "Template retired."
    assert len(audit.rows) == 3
    assert isinstance(events[0], SopTemplateMinted)
    assert isinstance(events[1], SopTemplateModified)
    assert isinstance(events[2], SopTemplateRevoked)
    assert dict(events[0].signed_template_payload)["template_id"] == "sop-template-1"
    assert store.list_templates() == ()


@pytest.mark.parametrize("principal", [_user_principal(), _reviewer_principal()])
def test_user_and_reviewer_cannot_write_sop_templates(
    tmp_path: Path,
    principal: UserPrincipal | ReviewerPrincipal,
) -> None:
    handler, _store, governance_log, _audit = _handler(tmp_path)

    with pytest.raises(PermissionError, match="administrator"):
        handler.mint_sop_template(
            principal,
            unsigned_template(),
            justification="Attempted SOP-template write.",
        )

    events = governance_log.read_events("inst")
    assert isinstance(events[0], AuthorisationAttemptDenied)
    assert events[0].missing_or_failed_reasons[0].startswith("mint_sop_template")


def test_sop_template_methods_require_configured_store_and_signer(tmp_path: Path) -> None:
    handler = AdminActionHandler(
        authorisation_store=SqliteAuthorisationStoreWrite(tmp_path / "authorisation.sqlite"),
        profile_signer=FakeProfileSigner(),
        audit_append=FakeAdminAuditBroker(TestAuditKeyProvider()),
        governance_event_log=JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE),
        clock=lambda: NOW,
    )

    with pytest.raises(RuntimeError, match="signer"):
        handler.mint_sop_template(
            admin_principal(),
            unsigned_template(),
            justification="Missing signer.",
        )


def _handler(
    tmp_path: Path,
) -> tuple[AdminActionHandler, SqliteSopTemplateStore, JsonlEventLog, FakeAdminAuditBroker]:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive, clock=lambda: NOW)
    verifier = Ed25519InstitutionalSopTemplateVerifier(archive)
    store = SqliteSopTemplateStore(
        tmp_path / "sop_templates.sqlite",
        verifier,
        clock=lambda: NOW,
    )
    governance_log = JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE)
    audit = FakeAdminAuditBroker(TestAuditKeyProvider())
    handler = AdminActionHandler(
        authorisation_store=SqliteAuthorisationStoreWrite(tmp_path / "authorisation.sqlite"),
        profile_signer=FakeProfileSigner(),
        audit_append=audit,
        governance_event_log=governance_log,
        sop_template_store=store,
        sop_template_signer=signer,
        clock=lambda: NOW,
    )
    return handler, store, governance_log, audit
