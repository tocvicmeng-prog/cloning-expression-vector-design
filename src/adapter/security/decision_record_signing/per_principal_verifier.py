"""
module_id: adapter.security.decision_record_signing.per_principal_verifier
file: src/adapter/security/decision_record_signing/per_principal_verifier.py
task_id: T-314b

Ed25519 per-principal decision-record verifier.
"""

from __future__ import annotations

from pathlib import Path

from cryptography.exceptions import InvalidSignature

from adapter.security.decision_record_signing.per_principal_signer import (
    decision_record_payload_hash,
)
from adapter.security.signing_key_archive import SigningKeyArchiveError, SigningKeyArchiveStore
from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security import KeyVersionId
from domain.types.signing_errors import (
    DecisionRecordPrincipalMismatchError,
    DecisionRecordTamperDetectedError,
    DecisionRecordVerificationResult,
    Result,
    RevokedKeyError,
    UnknownKeyVersionError,
)


class PerPrincipalDecisionRecordVerifier:
    def __init__(self, archive_path: str | Path) -> None:
        self._store = SigningKeyArchiveStore(
            archive_path,
            purpose="decision_record",
            create_if_missing=False,
        )

    def verify(self, signed: SignedDecisionRecord) -> DecisionRecordVerificationResult:
        try:
            record = self._store.record(signed.signing_key_version)
        except SigningKeyArchiveError:
            return Result.fail(UnknownKeyVersionError(str(signed.signing_key_version)))
        if record.revoked:
            return Result.fail(RevokedKeyError(str(signed.signing_key_version)))
        if record.principal_id != str(signed.signing_principal_id):
            return Result.fail(DecisionRecordPrincipalMismatchError("principal/key mismatch"))
        if signed.signing_principal_id != signed.decision.role_snapshot.principal_id:
            return Result.fail(DecisionRecordPrincipalMismatchError("principal mismatch"))
        expected_hash = decision_record_payload_hash(
            signed.decision,
            signed.signing_principal_id,
            signed.signing_key_version,
        )
        if signed.signed_payload_hash != expected_hash:
            return Result.fail(DecisionRecordTamperDetectedError("decision payload hash mismatch"))
        try:
            record.public_key().verify(
                signed.signature_bytes,
                str(expected_hash).encode("utf-8"),
            )
        except InvalidSignature:
            return Result.fail(DecisionRecordTamperDetectedError("decision signature mismatch"))
        return Result.ok(None)

    def revoke(self, key_version: KeyVersionId, reason: str = "revoked by verifier") -> None:
        self._store.revoke_key(key_version, reason)
