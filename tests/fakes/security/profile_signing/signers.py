"""
module_id: tests.fakes.security.profile_signing.signers
file: tests/fakes/security/profile_signing/signers.py
task_id: T-314a
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import replace
from datetime import UTC, datetime

from domain.canonicalisation import canonical_sha256
from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security import (
    AdminPrincipal,
    AuthorisationProfile,
    DeveloperBootstrapPrincipal,
    KeyVersionId,
    Principal,
    ProfileSignature,
)
from domain.sequence import Sha256
from domain.types.governance import DecisionRecord
from domain.types.signing_errors import (
    DecisionRecordPrincipalMismatchError,
    DecisionRecordTamperDetectedError,
    DecisionRecordVerificationResult,
    ProfileTamperDetectedError,
    ProfileVerificationResult,
    Result,
    RevokedKeyError,
    UnknownKeyVersionError,
)

SIGNED_AT = datetime(2026, 5, 14, tzinfo=UTC)
PROFILE_TEST_KEY_VERSION = KeyVersionId("profile-test-key-v1")
DECISION_TEST_KEY_VERSION = KeyVersionId("decision-test-key-v1")


class FakeProfileSigner:
    __test__ = False

    def __init__(self, key_version: KeyVersionId = PROFILE_TEST_KEY_VERSION) -> None:
        self._key_version = key_version
        self._keys: dict[str, bytes] = {str(key_version): b"profile-signing-test-key"}

    def sign(
        self,
        profile: AuthorisationProfile,
        admin: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> ProfileSignature:
        _require_profile_admin(admin)
        return ProfileSignature(
            signed_payload_hash=profile.profile_content_hash,
            signature_bytes=_mac(
                self._keys[str(self._key_version)],
                str(profile.profile_content_hash),
            ),
            signing_key_version=self._key_version,
            signed_at_utc=SIGNED_AT,
        )


class FakeProfileVerifier:
    __test__ = False

    def __init__(self, keys: dict[str, bytes] | None = None) -> None:
        self._keys = keys or {"profile-test-key-v1": b"profile-signing-test-key"}
        self._revoked: set[str] = set()

    def revoke(self, key_version: KeyVersionId) -> None:
        self._revoked.add(str(key_version))

    def verify(self, profile: AuthorisationProfile) -> ProfileVerificationResult:
        key_version = str(profile.profile_signature.signing_key_version)
        key = self._keys.get(key_version)
        if key is None:
            return Result.fail(UnknownKeyVersionError(key_version))
        if key_version in self._revoked:
            return Result.fail(RevokedKeyError(key_version))
        if profile.profile_signature_key_version != profile.profile_signature.signing_key_version:
            return Result.fail(ProfileTamperDetectedError("profile key-version mismatch"))
        if profile.profile_signature.signed_payload_hash != profile.profile_content_hash:
            return Result.fail(ProfileTamperDetectedError("profile payload hash mismatch"))
        expected = _mac(key, str(profile.profile_content_hash))
        if not hmac.compare_digest(expected, profile.profile_signature.signature_bytes):
            return Result.fail(ProfileTamperDetectedError("profile signature mismatch"))
        return Result.ok(None)


class FakeDecisionRecordSigner:
    __test__ = False

    def __init__(self, key_version: KeyVersionId = DECISION_TEST_KEY_VERSION) -> None:
        self._key_version = key_version
        self._keys: dict[str, bytes] = {str(key_version): b"decision-record-signing-test-key"}

    def sign(self, decision: DecisionRecord, principal: Principal) -> SignedDecisionRecord:
        payload_hash = _decision_payload_hash(decision, principal.id, self._key_version)
        return SignedDecisionRecord(
            decision=decision,
            signing_principal_id=principal.id,
            signing_key_version=self._key_version,
            signed_payload_hash=payload_hash,
            signature_bytes=_mac(self._keys[str(self._key_version)], str(payload_hash)),
        )


class FakeDecisionRecordVerifier:
    __test__ = False

    def __init__(self, keys: dict[str, bytes] | None = None) -> None:
        self._keys = keys or {"decision-test-key-v1": b"decision-record-signing-test-key"}
        self._revoked: set[str] = set()

    def revoke(self, key_version: KeyVersionId) -> None:
        self._revoked.add(str(key_version))

    def verify(self, signed: SignedDecisionRecord) -> DecisionRecordVerificationResult:
        key_version = str(signed.signing_key_version)
        key = self._keys.get(key_version)
        if key is None:
            return Result.fail(UnknownKeyVersionError(key_version))
        if key_version in self._revoked:
            return Result.fail(RevokedKeyError(key_version))
        if signed.signing_principal_id != signed.decision.role_snapshot.principal_id:
            return Result.fail(DecisionRecordPrincipalMismatchError("principal mismatch"))
        expected_hash = _decision_payload_hash(
            signed.decision,
            signed.signing_principal_id,
            signed.signing_key_version,
        )
        if signed.signed_payload_hash != expected_hash:
            return Result.fail(DecisionRecordTamperDetectedError("decision payload hash mismatch"))
        expected_signature = _mac(key, str(expected_hash))
        if not hmac.compare_digest(expected_signature, signed.signature_bytes):
            return Result.fail(DecisionRecordTamperDetectedError("decision signature mismatch"))
        return Result.ok(None)


def tamper_profile_signature(profile: AuthorisationProfile) -> AuthorisationProfile:
    return replace(
        profile,
        profile_signature=replace(profile.profile_signature, signature_bytes=b"tampered"),
    )


def _decision_payload_hash(
    decision: DecisionRecord,
    principal_id: object,
    key_version: KeyVersionId,
) -> Sha256:
    return canonical_sha256(
        {
            "decision": decision,
            "key_version": str(key_version),
            "principal_id": str(principal_id),
        }
    )


def _mac(key: bytes, payload: str) -> bytes:
    return hmac.new(key, payload.encode(), hashlib.sha256).digest()


def _require_profile_admin(admin: AdminPrincipal | DeveloperBootstrapPrincipal) -> None:
    if isinstance(admin, AdminPrincipal):
        return
    if isinstance(admin, DeveloperBootstrapPrincipal) and admin.has_bootstrap_authority:
        return
    raise PermissionError("profile signing requires administrator or bootstrap authority")
