"""
module_id: tests.fakes.security.profile_signing.test_fake_signers
file: tests/fakes/security/profile_signing/test_fake_signers.py
task_id: T-314a
"""

from __future__ import annotations

from dataclasses import replace

from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.ports.profile_signing import AuthorisationProfileSigner, AuthorisationProfileVerifier
from domain.security import KeyVersionId, PrincipalId
from domain.types.signing_errors import (
    DecisionRecordPrincipalMismatchError,
    DecisionRecordTamperDetectedError,
    ProfileTamperDetectedError,
    RevokedKeyError,
    UnknownKeyVersionError,
)
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    decision_record,
    reviewer_principal,
    signed_profile,
    unsigned_profile,
)
from tests.fakes.security.profile_signing.signers import (
    FakeDecisionRecordSigner,
    FakeDecisionRecordVerifier,
    FakeProfileSigner,
    FakeProfileVerifier,
    tamper_profile_signature,
)


def test_fake_profile_signer_and_verifier_round_trip() -> None:
    signer = FakeProfileSigner()
    verifier = FakeProfileVerifier()
    profile = unsigned_profile()
    signature = signer.sign(profile, admin_principal())
    signed = signed_profile(signature)

    assert isinstance(signer, AuthorisationProfileSigner)
    assert isinstance(verifier, AuthorisationProfileVerifier)
    assert verifier.verify(signed).success


def test_fake_profile_verifier_detects_tamper_unknown_key_and_revocation() -> None:
    signer = FakeProfileSigner()
    signed = signed_profile(signer.sign(unsigned_profile(), admin_principal()))
    verifier = FakeProfileVerifier()

    tampered = tamper_profile_signature(signed)
    assert isinstance(verifier.verify(tampered).error, ProfileTamperDetectedError)

    unknown_signature = replace(
        signed.profile_signature,
        signing_key_version=KeyVersionId("unknown-profile-key"),
    )
    unknown = replace(
        signed,
        profile_signature=unknown_signature,
        profile_signature_key_version=KeyVersionId("unknown-profile-key"),
    )
    assert isinstance(verifier.verify(unknown).error, UnknownKeyVersionError)

    verifier.revoke(KeyVersionId("profile-test-key-v1"))
    assert isinstance(verifier.verify(signed).error, RevokedKeyError)


def test_fake_decision_record_signer_and_verifier_round_trip() -> None:
    signer = FakeDecisionRecordSigner()
    verifier = FakeDecisionRecordVerifier()
    signed = signer.sign(decision_record(), reviewer_principal())

    assert verifier.verify(signed).success


def test_fake_decision_record_verifier_detects_failure_modes() -> None:
    signer = FakeDecisionRecordSigner()
    verifier = FakeDecisionRecordVerifier()
    signed = signer.sign(decision_record(), reviewer_principal())

    tampered_decision = replace(signed.decision, decision_type="tampered")
    tampered = replace(signed, decision=tampered_decision)
    assert isinstance(verifier.verify(tampered).error, DecisionRecordTamperDetectedError)

    mismatch = replace(signed, signing_principal_id=PrincipalId("other-principal"))
    assert isinstance(verifier.verify(mismatch).error, DecisionRecordPrincipalMismatchError)

    unknown = SignedDecisionRecord(
        decision=signed.decision,
        signing_principal_id=signed.signing_principal_id,
        signing_key_version=KeyVersionId("unknown-decision-key"),
        signed_payload_hash=signed.signed_payload_hash,
        signature_bytes=signed.signature_bytes,
    )
    assert isinstance(verifier.verify(unknown).error, UnknownKeyVersionError)

    verifier.revoke(KeyVersionId("decision-test-key-v1"))
    assert isinstance(verifier.verify(signed).error, RevokedKeyError)
