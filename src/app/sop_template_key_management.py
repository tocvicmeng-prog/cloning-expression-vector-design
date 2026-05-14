"""
module_id: app.sop_template_key_management
file: src/app/sop_template_key_management.py
task_id: T-316c

Institutional SOP-template signing-key lifecycle service.
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
    SopTemplateSigningKeyDistributed,
    SopTemplateSigningKeyRevoked,
)
from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security.identifiers import KeyVersionId
from domain.security.principals import AdminPrincipal, DeveloperBootstrapPrincipal, Principal


@dataclass(frozen=True)
class SopTemplateKeyLifecycleResult:
    signing_key_version: KeyVersionId
    governance_event_id: str


class SopTemplateKeyManagementService:
    def __init__(
        self,
        *,
        archive_path: str | Path,
        governance_event_log: JsonlEventLog,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = SigningKeyArchiveStore(archive_path, purpose="sop_template")
        self._governance_event_log = governance_event_log
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_sequence = 0

    def distribute_current_key(
        self,
        admin: Principal,
        *,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> SopTemplateKeyLifecycleResult:
        actor = _require_admin(admin)
        clean_reason = _clean_reason(reason)
        key_version = self._store.ensure_institutional_key()
        event_id = self._emit_distribution(actor, key_version, clean_reason, signed_decision_record)
        return SopTemplateKeyLifecycleResult(key_version, event_id)

    def rotate_key(
        self,
        admin: Principal,
        *,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> SopTemplateKeyLifecycleResult:
        actor = _require_admin(admin)
        clean_reason = _clean_reason(reason)
        key_version = self._store.rotate_institutional_key()
        event_id = self._emit_distribution(actor, key_version, clean_reason, signed_decision_record)
        return SopTemplateKeyLifecycleResult(key_version, event_id)

    def revoke_key(
        self,
        admin: Principal,
        *,
        signing_key_version: KeyVersionId,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> SopTemplateKeyLifecycleResult:
        actor = _require_admin(admin)
        clean_reason = _clean_reason(reason)
        self._store.revoke_key(signing_key_version, clean_reason)
        event = SopTemplateSigningKeyRevoked(
            event_id=self._next_event_id("SopTemplateSigningKeyRevoked"),
            occurred_at_utc=self._clock(),
            actor_id=str(actor.id),
            institution_id=str(actor.institution),
            signing_key_version=str(signing_key_version),
            reason=clean_reason,
            decision_record_payload=_signed_decision_payload(signed_decision_record),
            decision_record_hash=str(canonical_sha256(signed_decision_record)),
        )
        event_id = self._governance_event_log.append_event(str(actor.institution), event)
        return SopTemplateKeyLifecycleResult(signing_key_version, event_id)

    def _emit_distribution(
        self,
        actor: AdminPrincipal | DeveloperBootstrapPrincipal,
        key_version: KeyVersionId,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> str:
        record = self._store.record(key_version)
        event = SopTemplateSigningKeyDistributed(
            event_id=self._next_event_id("SopTemplateSigningKeyDistributed"),
            occurred_at_utc=self._clock(),
            actor_id=str(actor.id),
            institution_id=str(actor.institution),
            signing_key_version=str(key_version),
            public_key_fingerprint=_fingerprint(record.public_key_bytes),
            reason=reason,
            decision_record_payload=_signed_decision_payload(signed_decision_record),
            decision_record_hash=str(canonical_sha256(signed_decision_record)),
        )
        return self._governance_event_log.append_event(str(actor.institution), event)

    def _next_event_id(self, prefix: str) -> str:
        self._event_sequence += 1
        return f"{prefix}-{self._event_sequence:06d}"


def _require_admin(principal: Principal) -> AdminPrincipal | DeveloperBootstrapPrincipal:
    if isinstance(principal, AdminPrincipal):
        return principal
    if isinstance(principal, DeveloperBootstrapPrincipal) and principal.has_bootstrap_authority:
        return principal
    raise PermissionError("SOP-template key management requires administrator")


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
