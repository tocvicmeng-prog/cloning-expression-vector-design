"""
module_id: tests.domain.ports.test_profile_signing_contract
file: tests/domain/ports/test_profile_signing_contract.py
task_id: T-314a
"""

from __future__ import annotations

from domain.ports.profile_signing import AuthorisationProfileSigner, AuthorisationProfileVerifier
from domain.types.signing_errors import ProfileTamperDetectedError
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    signed_profile,
    unsigned_profile,
)
from tests.fakes.security.profile_signing.signers import (
    FakeProfileSigner,
    FakeProfileVerifier,
    tamper_profile_signature,
)


def assert_profile_signing_contract(
    signer: AuthorisationProfileSigner,
    verifier: AuthorisationProfileVerifier,
) -> None:
    signature = signer.sign(unsigned_profile(), admin_principal())
    profile = signed_profile(signature)

    assert verifier.verify(profile).success
    assert isinstance(
        verifier.verify(tamper_profile_signature(profile)).error,
        ProfileTamperDetectedError,
    )


def test_fake_profile_signer_and_verifier_satisfy_contract() -> None:
    assert_profile_signing_contract(FakeProfileSigner(), FakeProfileVerifier())
