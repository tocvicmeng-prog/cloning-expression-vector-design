"""
module_id: tests.security.decision_record_signing.test_revoked_principal_signature_fails
file: tests/security/decision_record_signing/test_revoked_principal_signature_fails.py
task_id: T-314b
"""

from __future__ import annotations

from pathlib import Path

from adapter.persistence import JsonlEventLog
from adapter.security.decision_record_signing import (
    PerPrincipalDecisionRecordSigner,
    PerPrincipalDecisionRecordVerifier,
)
from app.decision_record_key_management import DecisionRecordKeyManagementService
from domain.events import DecisionRecordPrincipalKeyRevoked, EventStream
from domain.types.signing_errors import RevokedKeyError
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    decision_record,
    reviewer_principal,
)
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner


def test_revoked_principal_key_fails_and_emits_event(tmp_path: Path) -> None:
    archive = tmp_path / "decision-keys.json"
    event_log = JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE)
    service = DecisionRecordKeyManagementService(
        archive_path=archive,
        governance_event_log=event_log,
    )
    lifecycle_decision = FakeDecisionRecordSigner().sign(decision_record(), reviewer_principal())
    provisioned = service.provision_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        reason="initial provisioning",
        signed_decision_record=lifecycle_decision,
    )
    signed = PerPrincipalDecisionRecordSigner(archive).sign(decision_record(), reviewer_principal())

    service.revoke_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        signing_key_version=provisioned.signing_key_version,
        reason="compromised user credential",
        signed_decision_record=lifecycle_decision,
    )

    assert isinstance(
        PerPrincipalDecisionRecordVerifier(archive).verify(signed).error, RevokedKeyError
    )
    event = event_log.read_events("inst")[-1]
    assert isinstance(event, DecisionRecordPrincipalKeyRevoked)
    assert event.reason == "compromised user credential"
