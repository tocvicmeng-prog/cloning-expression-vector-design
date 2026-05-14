"""
module_id: tests.app.admin_action_handler.test_admin_action_handler
file: tests/app/admin_action_handler/test_admin_action_handler.py
task_id: T-311
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from adapter.persistence import (
    AlreadyBootstrappedError,
    JsonlEventLog,
    SqliteAuthorisationStoreRead,
    SqliteAuthorisationStoreWrite,
)
from app.admin_action_handler import AdminActionHandler
from domain.events import AdminActionMinted, AuthorisationAttemptDenied, EventStream
from domain.security import (
    DeveloperBootstrapPrincipal,
    DeveloperPrincipal,
    InstitutionId,
    PrincipalId,
    ReviewerPrincipal,
    SecurityRole,
    UserPrincipal,
)
from tests.fakes.security.audit_append.brokers import FakeAdminAuditBroker
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.fakes.security.profile_signing.fixtures import admin_principal, unsigned_profile_draft
from tests.fakes.security.profile_signing.signers import FakeProfileSigner, FakeProfileVerifier

NOW = datetime(2026, 5, 14, tzinfo=UTC)
LATER = datetime(2030, 1, 1, tzinfo=UTC)


def _handler(
    tmp_path: Path,
) -> tuple[
    AdminActionHandler,
    SqliteAuthorisationStoreWrite,
    JsonlEventLog,
    FakeAdminAuditBroker,
]:
    writer = SqliteAuthorisationStoreWrite(tmp_path / "authorisation.sqlite")
    governance_log = JsonlEventLog(
        tmp_path / "events" / "governance",
        expected_stream=EventStream.GOVERNANCE,
    )
    audit = FakeAdminAuditBroker(TestAuditKeyProvider())
    handler = AdminActionHandler(
        authorisation_store=writer,
        profile_signer=FakeProfileSigner(),
        audit_append=audit,
        governance_event_log=governance_log,
        clock=lambda: NOW,
    )
    return handler, writer, governance_log, audit


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


def _developer_principal() -> DeveloperPrincipal:
    return DeveloperPrincipal(
        id=PrincipalId("developer-1"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def _bootstrap_principal() -> DeveloperBootstrapPrincipal:
    return DeveloperBootstrapPrincipal(
        id=PrincipalId("developer-bootstrap-1"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
        is_bootstrap=True,
        bootstrap_expires_at=LATER,
    )


def test_mint_profile_signs_writes_audits_and_emits_governance_event(tmp_path: Path) -> None:
    handler, writer, governance_log, audit = _handler(tmp_path)
    result = handler.mint_profile(
        admin_principal(),
        unsigned_profile_draft(),
        justification="Initial institutional authorisation.",
    )
    reader = SqliteAuthorisationStoreRead(writer.path, FakeProfileVerifier())

    assert str(result.profile.profile_id) == "profile-1"
    assert reader.get("profile-1") == result.profile
    assert len(audit.rows) == 1
    events = governance_log.read_events("inst")
    assert isinstance(events[0], AdminActionMinted)
    assert dict(events[0].profile_payload)["profile_id"] == "profile-1"


def test_modify_and_revoke_profile_round_trip(tmp_path: Path) -> None:
    handler, writer, _governance_log, _audit = _handler(tmp_path)
    handler.mint_profile(
        admin_principal(),
        unsigned_profile_draft(),
        justification="Initial institutional authorisation.",
    )
    modified_draft = replace(
        unsigned_profile_draft(),
        profile_version=2,
        additional_constraints=("institutional-review-required",),
    )
    modified = handler.modify_profile(
        admin_principal(),
        modified_draft,
        justification="Scope clarified after review.",
    )
    revoked = handler.revoke_profile(
        admin_principal(),
        "profile-1",
        reason="User left institution.",
    )

    stored = writer.get_profile("profile-1")
    assert modified.profile.profile_version == 2
    assert revoked.profile.revoked_at == NOW
    assert stored.revocation_reason == "User left institution."


@pytest.mark.parametrize("principal", [_user_principal(), _reviewer_principal()])
def test_user_and_reviewer_are_denied_with_governance_event(
    tmp_path: Path,
    principal: UserPrincipal | ReviewerPrincipal,
) -> None:
    handler, _writer, governance_log, _audit = _handler(tmp_path)

    with pytest.raises(PermissionError, match="administrator"):
        handler.mint_profile(
            principal,
            unsigned_profile_draft(),
            justification="Attempted self elevation.",
        )

    events = governance_log.read_events("inst")
    assert isinstance(events[0], AuthorisationAttemptDenied)
    assert events[0].missing_or_failed_reasons[0].startswith("mint_profile")


def test_developer_bootstrap_is_one_shot_and_ordinary_developer_is_rejected(
    tmp_path: Path,
) -> None:
    handler, _writer, _governance_log, _audit = _handler(tmp_path)
    handler.mint_profile(
        _bootstrap_principal(),
        unsigned_profile_draft(),
        justification="Bootstrap first administrator.",
    )

    with pytest.raises(AlreadyBootstrappedError):
        handler.bootstrap_initial_admin(
            _bootstrap_principal(),
            unsigned_profile_draft(),
            justification="Second bootstrap attempt.",
        )

    with pytest.raises(PermissionError, match="administrator"):
        handler.mint_profile(
            _developer_principal(),
            replace(unsigned_profile_draft(), profile_id=unsigned_profile_draft().profile_id),
            justification="Developer after bootstrap.",
        )


def test_list_profiles_and_view_audit_are_admin_only(tmp_path: Path) -> None:
    handler, _writer, _governance_log, _audit = _handler(tmp_path)
    handler.mint_profile(
        admin_principal(),
        unsigned_profile_draft(),
        justification="Initial institutional authorisation.",
    )

    assert len(handler.list_profiles(admin_principal())) == 1
    assert handler.view_audit_trail(admin_principal())[0]["profile_id"] == "profile-1"
    with pytest.raises(PermissionError):
        handler.list_profiles(_user_principal())
