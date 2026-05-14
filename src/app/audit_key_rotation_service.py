"""
module_id: app.audit_key_rotation_service
file: src/app/audit_key_rotation_service.py
task_id: T-312b

Administrator audit-key rotation workflow.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from adapter.persistence import JsonlEventLog
from domain.canonicalisation import canonical_sha256
from domain.events import AuditKeyRotated, CanonicalPayload
from domain.ports.audit_key import AuditKeyProvider, KeyVersionId
from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, Principal


@dataclass(frozen=True)
class AuditKeyRotationResult:
    key_version_before: KeyVersionId
    key_version_after: KeyVersionId
    governance_event_id: str
    decision_record_hash: str


class AuditKeyRotationService:
    def __init__(
        self,
        *,
        key_provider: AuditKeyProvider,
        governance_event_log: JsonlEventLog,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._key_provider = key_provider
        self._governance_event_log = governance_event_log
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_sequence = 0

    def rotate(
        self,
        principal: Principal,
        *,
        reason: str,
        signed_decision_record: SignedDecisionRecord,
    ) -> AuditKeyRotationResult:
        rotating_principal = _require_rotation_authority(principal)
        clean_reason = reason.strip()
        if not clean_reason:
            raise ValueError("rotation reason cannot be empty")

        key_version_before = self._key_provider.current_key_version()
        key_version_after = self._key_provider.rotate(clean_reason, rotating_principal)
        decision_payload = _signed_decision_payload(signed_decision_record)
        decision_hash = str(canonical_sha256(signed_decision_record))
        event = AuditKeyRotated(
            event_id=self._next_event_id(),
            occurred_at_utc=self._clock(),
            actor_id=str(principal.id),
            institution_id=str(principal.institution),
            key_version_before=str(int(key_version_before)),
            key_version_after=str(int(key_version_after)),
            rotation_reason=clean_reason,
            decision_record_payload=decision_payload,
            decision_record_hash=decision_hash,
        )
        governance_event_id = self._governance_event_log.append_event(
            str(principal.institution),
            event,
        )
        return AuditKeyRotationResult(
            key_version_before=key_version_before,
            key_version_after=key_version_after,
            governance_event_id=governance_event_id,
            decision_record_hash=decision_hash,
        )

    def _next_event_id(self) -> str:
        self._event_sequence += 1
        return f"AuditKeyRotated-{self._event_sequence:06d}"


def _require_rotation_authority(
    principal: Principal,
) -> AdminPrincipal | DeveloperBootstrapPrincipal:
    if isinstance(principal, AdminPrincipal):
        return principal
    if isinstance(principal, DeveloperBootstrapPrincipal) and principal.has_bootstrap_authority:
        return principal
    raise PermissionError("audit-key rotation requires administrator or bootstrap authority")


def _signed_decision_payload(signed: SignedDecisionRecord) -> CanonicalPayload:
    decision = signed.decision
    snapshot = decision.role_snapshot
    return (
        ("decision_id", decision.decision_id),
        ("decision_type", decision.decision_type),
        ("policy_version", decision.policy_version),
        ("profile_content_hash", str(decision.profile_content_hash)),
        ("role_principal_id", str(snapshot.principal_id)),
        ("role", snapshot.role.value),
        ("institution_id", snapshot.institution_id),
        ("credentials_verified_at_utc", snapshot.credentials_verified_at_utc.isoformat()),
        ("signing_principal_id", str(signed.signing_principal_id)),
        ("signing_key_version", str(signed.signing_key_version)),
        ("signed_payload_hash", str(signed.signed_payload_hash)),
        ("signature_bytes_hex", signed.signature_bytes.hex()),
    )
