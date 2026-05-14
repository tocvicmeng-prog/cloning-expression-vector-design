"""
module_id: tests.security.profile_signing.test_wrong_key_version_fails
file: tests/security/profile_signing/test_wrong_key_version_fails.py
task_id: T-314b
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from adapter.security.profile_signing import (
    Ed25519InstitutionalProfileSigner,
    Ed25519InstitutionalProfileVerifier,
)
from domain.security import KeyVersionId
from domain.types.signing_errors import UnknownKeyVersionError
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    signed_profile,
    unsigned_profile,
)


def test_unknown_profile_key_version_fails(tmp_path: Path) -> None:
    archive = tmp_path / "profile-keys.json"
    signer = Ed25519InstitutionalProfileSigner(archive)
    verifier = Ed25519InstitutionalProfileVerifier(archive)
    profile = signed_profile(signer.sign(unsigned_profile(), admin_principal()))
    signature = replace(
        profile.profile_signature,
        signing_key_version=KeyVersionId("unknown-profile-key"),
    )
    unknown = replace(
        profile,
        profile_signature=signature,
        profile_signature_key_version=KeyVersionId("unknown-profile-key"),
    )

    assert isinstance(verifier.verify(unknown).error, UnknownKeyVersionError)
