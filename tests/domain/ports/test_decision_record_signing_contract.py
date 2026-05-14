"""
module_id: tests.domain.ports.test_decision_record_signing_contract
file: tests/domain/ports/test_decision_record_signing_contract.py
task_id: T-314a
"""

from __future__ import annotations

from dataclasses import replace

from domain.ports.decision_record_signing import DecisionRecordSigner, DecisionRecordVerifier
from domain.types.signing_errors import DecisionRecordTamperDetectedError
from tests.fakes.security.profile_signing.fixtures import decision_record, reviewer_principal
from tests.fakes.security.profile_signing.signers import (
    FakeDecisionRecordSigner,
    FakeDecisionRecordVerifier,
)


def assert_decision_record_signing_contract(
    signer: DecisionRecordSigner,
    verifier: DecisionRecordVerifier,
) -> None:
    signed = signer.sign(decision_record(), reviewer_principal())

    assert verifier.verify(signed).success
    tampered = replace(signed, decision=replace(signed.decision, policy_version="other-policy"))
    assert isinstance(verifier.verify(tampered).error, DecisionRecordTamperDetectedError)


def test_fake_decision_record_signer_and_verifier_satisfy_contract() -> None:
    assert_decision_record_signing_contract(
        FakeDecisionRecordSigner(),
        FakeDecisionRecordVerifier(),
    )
