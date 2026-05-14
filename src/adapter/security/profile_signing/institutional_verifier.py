"""
module_id: adapter.security.profile_signing.institutional_verifier
file: src/adapter/security/profile_signing/institutional_verifier.py
task_id: T-314b

Ed25519 institutional authorisation-profile verifier.
"""

from __future__ import annotations

from pathlib import Path

from cryptography.exceptions import InvalidSignature

from adapter.security.profile_signing.institutional_signer import _profile_signature_payload
from adapter.security.signing_key_archive import SigningKeyArchiveError, SigningKeyArchiveStore
from domain.security import AuthorisationProfile, KeyVersionId
from domain.types.signing_errors import (
    ProfileTamperDetectedError,
    ProfileVerificationResult,
    Result,
    RevokedKeyError,
    UnknownKeyVersionError,
)


class Ed25519InstitutionalProfileVerifier:
    def __init__(self, archive_path: str | Path) -> None:
        self._store = SigningKeyArchiveStore(
            archive_path, purpose="profile", create_if_missing=False
        )

    def verify(self, profile: AuthorisationProfile) -> ProfileVerificationResult:
        key_version = profile.profile_signature.signing_key_version
        try:
            record = self._store.record(key_version)
        except SigningKeyArchiveError:
            return Result.fail(UnknownKeyVersionError(str(key_version)))
        if record.revoked:
            return Result.fail(RevokedKeyError(str(key_version)))
        if profile.profile_signature_key_version != key_version:
            return Result.fail(ProfileTamperDetectedError("profile key-version mismatch"))
        if profile.profile_signature.signed_payload_hash != profile.profile_content_hash:
            return Result.fail(ProfileTamperDetectedError("profile payload hash mismatch"))
        try:
            record.public_key().verify(
                profile.profile_signature.signature_bytes,
                _profile_signature_payload(profile),
            )
        except InvalidSignature:
            return Result.fail(ProfileTamperDetectedError("profile signature mismatch"))
        return Result.ok(None)

    def revoke(self, key_version: KeyVersionId, reason: str = "revoked by verifier") -> None:
        self._store.revoke_key(key_version, reason)
