"""
module_id: tests.security.audit_key.test_rotation_service
file: tests/security/audit_key/test_rotation_service.py
task_id: T-312b
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.persistence import JsonlEventLog
from adapter.security.audit_key import FileAuditKeyProvider
from app.audit_key_rotation_service import AuditKeyRotationService
from domain.events import AuditKeyRotated, EventStream
from domain.ports.audit_key import KeyVersionId
from domain.security import Principal
from domain.types.governance import DecisionRecord, RoleSnapshot
from tests.fakes.security.profile_signing.fixtures import admin_principal, decision_record
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner
from tests.security.audit_key.helpers import NOW, bootstrap_principal, deterministic_key_factory


def test_rotation_service_emits_signed_governance_event(tmp_path: Path) -> None:
    principal = admin_principal()
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    old_version, old_mac = provider.mac(b"historical-row")
    event_log = JsonlEventLog(tmp_path / "events", expected_stream=EventStream.GOVERNANCE)
    service = AuditKeyRotationService(
        key_provider=provider,
        governance_event_log=event_log,
        clock=lambda: NOW,
    )
    signed_decision = FakeDecisionRecordSigner().sign(
        _audit_key_rotation_decision(),
        principal,
    )

    result = service.rotate(
        principal,
        reason="scheduled quarterly audit-key rotation",
        signed_decision_record=signed_decision,
    )

    events = event_log.read_events("inst")
    assert result.key_version_before == old_version
    assert result.key_version_after == provider.current_key_version()
    assert provider.verify_with_archived(old_version, b"historical-row", old_mac)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, AuditKeyRotated)
    assert event.key_version_before == "1"
    assert event.key_version_after == "2"
    assert event.rotation_reason == "scheduled quarterly audit-key rotation"
    assert dict(event.decision_record_payload)["decision_type"] == "audit_key_rotation"
    assert dict(event.decision_record_payload)["signature_bytes_hex"]
    assert event.decision_record_hash == result.decision_record_hash


def test_rotation_service_rejects_non_admin_principal(tmp_path: Path) -> None:
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    service = AuditKeyRotationService(
        key_provider=provider,
        governance_event_log=JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE),
    )
    principal = Principal(
        id=admin_principal().id,
        role=admin_principal().role,
        institution=admin_principal().institution,
        credentials_verified_at=admin_principal().credentials_verified_at,
    )
    signed_decision = FakeDecisionRecordSigner().sign(
        _audit_key_rotation_decision(),
        admin_principal(),
    )

    with pytest.raises(PermissionError, match="administrator"):
        service.rotate(
            principal,
            reason="unauthorised",
            signed_decision_record=signed_decision,
        )


def test_rotation_service_allows_bootstrap_principal(tmp_path: Path) -> None:
    principal = bootstrap_principal()
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    service = AuditKeyRotationService(
        key_provider=provider,
        governance_event_log=JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE),
        clock=lambda: NOW,
    )
    signed_decision = FakeDecisionRecordSigner().sign(
        _audit_key_rotation_decision(),
        admin_principal(),
    )

    result = service.rotate(
        principal,
        reason="bootstrap audit-key rotation",
        signed_decision_record=signed_decision,
    )

    assert result.key_version_after == KeyVersionId(2)


def _audit_key_rotation_decision() -> DecisionRecord:
    principal = admin_principal()
    base = decision_record()
    return type(base)(
        decision_id="audit-key-rotation-1",
        decision_type="audit_key_rotation",
        role_snapshot=RoleSnapshot(
            principal_id=principal.id,
            role=principal.role,
            institution_id=str(principal.institution),
            captured_at_utc=NOW,
            credentials_verified_at_utc=principal.credentials_verified_at,
        ),
        profile_content_hash=base.profile_content_hash,
        policy_version=base.policy_version,
        signed_payload_hash=base.signed_payload_hash,
        signature_bytes=base.signature_bytes,
        signed_at_utc=NOW,
    )
