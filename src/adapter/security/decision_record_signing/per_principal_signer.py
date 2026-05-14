"""
module_id: adapter.security.decision_record_signing.per_principal_signer
file: src/adapter/security/decision_record_signing/per_principal_signer.py
task_id: T-314b

Ed25519 per-principal decision-record signer.
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.signing_key_archive import SigningKeyArchiveStore
from domain.canonicalisation import canonical_sha256
from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security import Principal
from domain.sequence import Sha256
from domain.types.governance import DecisionRecord


class PerPrincipalDecisionRecordSigner:
    def __init__(self, archive_path: str | Path, *, auto_provision: bool = False) -> None:
        self._store = SigningKeyArchiveStore(archive_path, purpose="decision_record")
        self._auto_provision = auto_provision

    def sign(self, decision: DecisionRecord, principal: Principal) -> SignedDecisionRecord:
        principal_id = str(principal.id)
        if self._auto_provision:
            self._store.ensure_principal_key(principal_id)
        record = self._store.current_principal_record(principal_id)
        payload_hash = decision_record_payload_hash(decision, principal.id, record.key_version)
        return SignedDecisionRecord(
            decision=decision,
            signing_principal_id=principal.id,
            signing_key_version=record.key_version,
            signed_payload_hash=payload_hash,
            signature_bytes=record.private_key().sign(str(payload_hash).encode("utf-8")),
        )


def decision_record_payload_hash(
    decision: DecisionRecord,
    principal_id: object,
    key_version: object,
) -> Sha256:
    return canonical_sha256(
        {
            "decision": decision,
            "key_version": str(key_version),
            "principal_id": str(principal_id),
        }
    )
