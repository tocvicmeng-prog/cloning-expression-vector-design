"""Decision-record key rotation tests for T-314b."""

from __future__ import annotations

from pathlib import Path

from adapter.persistence import JsonlEventLog
from adapter.security.decision_record_signing import (
    PerPrincipalDecisionRecordSigner,
    PerPrincipalDecisionRecordVerifier,
)
from app.decision_record_key_management import DecisionRecordKeyManagementService
from domain.events import EventStream
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    decision_record,
    reviewer_principal,
)
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner


def test_rotated_principal_key_verifies_historical_records(tmp_path: Path) -> None:
    archive = tmp_path / "decision-keys.json"
    service = DecisionRecordKeyManagementService(
        archive_path=archive,
        governance_event_log=JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE),
    )
    lifecycle_decision = FakeDecisionRecordSigner().sign(decision_record(), reviewer_principal())
    service.provision_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        reason="initial provisioning",
        signed_decision_record=lifecycle_decision,
    )
    signer = PerPrincipalDecisionRecordSigner(archive)
    verifier = PerPrincipalDecisionRecordVerifier(archive)
    historical = signer.sign(decision_record(), reviewer_principal())

    service.rotate_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        reason="scheduled user key rotation",
        signed_decision_record=lifecycle_decision,
    )
    current = signer.sign(decision_record(), reviewer_principal())

    assert historical.signing_key_version != current.signing_key_version
    assert verifier.verify(historical).success
    assert verifier.verify(current).success
