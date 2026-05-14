"""
module_id: app.decision_record_key_management
file: src/app/decision_record_key_management.py
task_id: T-314b

Per-principal decision-record key lifecycle service.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from adapter.persistence import JsonlEventLog
from adapter.security.signing_key_archive import SigningKeyArchiveStore
from domain.canonicalisation import canonical_sha256
from domain.events import (
    CanonicalPayload,
    DecisionRecordPrincipalKeyRevoked,
    DecisionRecordPublicKeyDistributed,
)
from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, KeyVersionId, Principal


@dataclass(frozen=True)
class DecisionRecordKeyLifecycleResult:
    principal_id: str
    signing_key_version: KeyVersionId
    governance_event_id: str


class DecisionRecordKeyManagementService:
    def __init__(
        self,
        *,
        archive_path: str | Path,
        governance_event_log: JsonlEventLog,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = SigningKeyArchiveStore(archive_path, purpose="decision_record")
        self._governance_event_log = governance_event_log
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_sequence = 0

    def provision_principal_key(
        self,
        admin: Principal,
        *,
        principal_id: str,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> DecisionRecordKeyLifecycleResult:
        rotating_admin = _require_admin(admin)
        clean_reason = _clean_reason(reason)
        key_version = self._store.ensure_principal_key(principal_id)
        record = self._store.record(key_version)
        event = DecisionRecordPublicKeyDistributed(
            event_id=self._next_event_id("DecisionRecordPublicKeyDistributed"),
            occurred_at_utc=self._clock(),
            actor_id=str(rotating_admin.id),
            institution_id=str(rotating_admin.institution),
            principal_id=principal_id,
            signing_key_version=str(key_version),
            public_key_fingerprint=_fingerprint(record.public_key_bytes),
            reason=clean_reason,
            decision_record_payload=_signed_decision_payload(signed_decision_record),
            decision_record_hash=str(canonical_sha256(signed_decision_record)),
        )
        event_id = self._governance_event_log.append_event(str(rotating_admin.institution), event)
        return DecisionRecordKeyLifecycleResult(principal_id, key_version, event_id)

    def rotate_principal_key(
        self,
        admin: Principal,
        *,
        principal_id: str,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> DecisionRecordKeyLifecycleResult:
        rotating_admin = _require_admin(admin)
        clean_reason = _clean_reason(reason)
        key_version = self._store.rotate_principal_key(principal_id)
        record = self._store.record(key_version)
        event = DecisionRecordPublicKeyDistributed(
            event_id=self._next_event_id("DecisionRecordPublicKeyDistributed"),
            occurred_at_utc=self._clock(),
            actor_id=str(rotating_admin.id),
            institution_id=str(rotating_admin.institution),
            principal_id=principal_id,
            signing_key_version=str(key_version),
            public_key_fingerprint=_fingerprint(record.public_key_bytes),
            reason=clean_reason,
            decision_record_payload=_signed_decision_payload(signed_decision_record),
            decision_record_hash=str(canonical_sha256(signed_decision_record)),
        )
        event_id = self._governance_event_log.append_event(str(rotating_admin.institution), event)
        return DecisionRecordKeyLifecycleResult(principal_id, key_version, event_id)

    def revoke_principal_key(
        self,
        admin: Principal,
        *,
        principal_id: str,
        signing_key_version: KeyVersionId,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> DecisionRecordKeyLifecycleResult:
        rotating_admin = _require_admin(admin)
        clean_reason = _clean_reason(reason)
        self._store.revoke_key(signing_key_version, clean_reason)
        event = DecisionRecordPrincipalKeyRevoked(
            event_id=self._next_event_id("DecisionRecordPrincipalKeyRevoked"),
            occurred_at_utc=self._clock(),
            actor_id=str(rotating_admin.id),
            institution_id=str(rotating_admin.institution),
            principal_id=principal_id,
            signing_key_version=str(signing_key_version),
            reason=clean_reason,
            decision_record_payload=_signed_decision_payload(signed_decision_record),
            decision_record_hash=str(canonical_sha256(signed_decision_record)),
        )
        event_id = self._governance_event_log.append_event(str(rotating_admin.institution), event)
        return DecisionRecordKeyLifecycleResult(principal_id, signing_key_version, event_id)

    def _next_event_id(self, prefix: str) -> str:
        self._event_sequence += 1
        return f"{prefix}-{self._event_sequence:06d}"


def _require_admin(principal: Principal) -> AdminPrincipal | DeveloperBootstrapPrincipal:
    if isinstance(principal, AdminPrincipal):
        return principal
    if isinstance(principal, DeveloperBootstrapPrincipal) and principal.has_bootstrap_authority:
        return principal
    raise PermissionError("decision-record key management requires administrator")


def _clean_reason(reason: str) -> str:
    clean = reason.strip()
    if not clean:
        raise ValueError("key lifecycle reason cannot be empty")
    return clean


def _fingerprint(public_key_bytes: bytes) -> str:
    return hashlib.sha256(public_key_bytes).hexdigest()


def _signed_decision_payload(signed: SignedDecisionRecord) -> CanonicalPayload:
    decision = signed.decision
    snapshot = decision.role_snapshot
    return (
        ("decision_id", decision.decision_id),
        ("decision_type", decision.decision_type),
        ("policy_version", decision.policy_version),
        ("role_principal_id", str(snapshot.principal_id)),
        ("role", snapshot.role.value),
        ("signing_principal_id", str(signed.signing_principal_id)),
        ("signing_key_version", str(signed.signing_key_version)),
        ("signed_payload_hash", str(signed.signed_payload_hash)),
        ("signature_bytes_hex", signed.signature_bytes.hex()),
    )
