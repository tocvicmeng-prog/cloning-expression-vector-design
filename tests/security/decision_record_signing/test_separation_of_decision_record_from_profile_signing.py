"""Decision-record/profile-signing separation tests for T-314b."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.persistence import JsonlEventLog
from adapter.security.decision_record_signing import PerPrincipalDecisionRecordSigner
from adapter.security.profile_signing import Ed25519InstitutionalProfileSigner
from adapter.security.signing_key_archive import SigningKeyArchiveError
from app.decision_record_key_management import DecisionRecordKeyManagementService
from domain.events import EventStream
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    decision_record,
    reviewer_principal,
    signed_profile,
    unsigned_profile,
)
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner


def test_decision_record_and_profile_keys_are_distinct_archives(tmp_path: Path) -> None:
    profile_archive = tmp_path / "profile-keys.json"
    decision_archive = tmp_path / "decision-keys.json"
    profile_signer = Ed25519InstitutionalProfileSigner(profile_archive)
    profile = signed_profile(profile_signer.sign(unsigned_profile(), admin_principal()))
    service = DecisionRecordKeyManagementService(
        archive_path=decision_archive,
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
    signed_decision = PerPrincipalDecisionRecordSigner(decision_archive).sign(
        decision_record(),
        reviewer_principal(),
    )

    assert str(profile.profile_signature_key_version).startswith("profile-ed25519")
    assert str(signed_decision.signing_key_version).startswith("decision-record")
    assert profile.profile_signature.signature_bytes != signed_decision.signature_bytes
    with pytest.raises(SigningKeyArchiveError, match="purpose"):
        PerPrincipalDecisionRecordSigner(profile_archive).sign(
            decision_record(), reviewer_principal()
        )
