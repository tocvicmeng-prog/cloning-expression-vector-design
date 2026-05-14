"""
module_id: tests.security.profile_signing.test_sign_then_verify
file: tests/security/profile_signing/test_sign_then_verify.py
task_id: T-314b
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.profile_signing import (
    Ed25519InstitutionalProfileSigner,
    Ed25519InstitutionalProfileVerifier,
)
from tests.domain.ports.test_profile_signing_contract import assert_profile_signing_contract
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    signed_profile,
    unsigned_profile,
)


def test_ed25519_profile_signer_and_verifier_satisfy_contract(tmp_path: Path) -> None:
    archive = tmp_path / "profile-keys.json"
    assert_profile_signing_contract(
        Ed25519InstitutionalProfileSigner(archive),
        Ed25519InstitutionalProfileVerifier(archive),
    )


def test_profile_signer_rotates_and_verifies_historical_signatures(tmp_path: Path) -> None:
    archive = tmp_path / "profile-keys.json"
    signer = Ed25519InstitutionalProfileSigner(archive)
    verifier = Ed25519InstitutionalProfileVerifier(archive)
    first = signed_profile(signer.sign(unsigned_profile(), admin_principal()))

    second_version = signer.rotate("scheduled profile-key rotation", admin_principal())
    second = signed_profile(signer.sign(unsigned_profile(), admin_principal()))

    assert str(first.profile_signature_key_version) != str(second_version)
    assert second.profile_signature_key_version == second_version
    assert verifier.verify(first).success
    assert verifier.verify(second).success
