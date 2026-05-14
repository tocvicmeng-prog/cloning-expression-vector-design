"""
module_id: tests.security.decision_record_signing.test_decision_record_signature_verifier
file: tests/security/decision_record_signing/test_decision_record_signature_verifier.py
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
from domain.events import DecisionRecordPublicKeyDistributed, EventStream
from tests.domain.ports.test_decision_record_signing_contract import (
    assert_decision_record_signing_contract,
)
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    decision_record,
    reviewer_principal,
)
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner


def test_per_principal_signer_and_verifier_satisfy_contract(tmp_path: Path) -> None:
    archive = tmp_path / "decision-keys.json"
    _provision_reviewer_key(archive, tmp_path)
    assert_decision_record_signing_contract(
        PerPrincipalDecisionRecordSigner(archive),
        PerPrincipalDecisionRecordVerifier(archive),
    )


def test_key_management_emits_public_key_distribution_event(tmp_path: Path) -> None:
    archive = tmp_path / "decision-keys.json"
    event_log = JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE)
    service = DecisionRecordKeyManagementService(
        archive_path=archive,
        governance_event_log=event_log,
    )
    signed_decision = FakeDecisionRecordSigner().sign(decision_record(), reviewer_principal())

    result = service.provision_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        reason="initial user provisioning",
        signed_decision_record=signed_decision,
    )

    events = event_log.read_events("inst")
    assert result.principal_id == str(reviewer_principal().id)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, DecisionRecordPublicKeyDistributed)
    assert event.principal_id == str(reviewer_principal().id)
    assert event.public_key_fingerprint


def _provision_reviewer_key(archive: Path, tmp_path: Path) -> None:
    service = DecisionRecordKeyManagementService(
        archive_path=archive,
        governance_event_log=JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE),
    )
    service.provision_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        reason="initial provisioning",
        signed_decision_record=FakeDecisionRecordSigner().sign(
            decision_record(), reviewer_principal()
        ),
    )
