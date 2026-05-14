"""
module_id: tests.security.profile_signing.test_tampered_payload_fails
file: tests/security/profile_signing/test_tampered_payload_fails.py
task_id: T-314b
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.profile_signing import (
    Ed25519InstitutionalProfileSigner,
    Ed25519InstitutionalProfileVerifier,
)
from domain.types.signing_errors import ProfileTamperDetectedError
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    signed_profile,
    unsigned_profile,
)
from tests.fakes.security.profile_signing.signers import tamper_profile_signature


def test_tampered_profile_signature_fails(tmp_path: Path) -> None:
    archive = tmp_path / "profile-keys.json"
    signer = Ed25519InstitutionalProfileSigner(archive)
    verifier = Ed25519InstitutionalProfileVerifier(archive)
    profile = signed_profile(signer.sign(unsigned_profile(), admin_principal()))

    result = verifier.verify(tamper_profile_signature(profile))

    assert isinstance(result.error, ProfileTamperDetectedError)
