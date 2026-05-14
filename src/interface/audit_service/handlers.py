"""
module_id: interface.audit_service.handlers
file: src/interface/audit_service/handlers.py
task_id: T-313b

Audit-service IPC verb handlers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from adapter.persistence import SqliteAuditLogWriter
from adapter.security.decision_record_signing import signed_decision_from_json
from domain.ports.audit_append import AuditEntry, AuditEntryId
from domain.ports.decision_record_signing import DecisionRecordVerifier, SignedDecisionRecord
from interface.audit_service.governance_event_writer import AuditServiceGovernanceEventWriter


class AuditServiceAuthenticationError(PermissionError):
    """Raised when an audit-service append token fails authentication."""


@dataclass(frozen=True)
class AuthenticatedCaller:
    principal_id: str
    institution_id: str


class AuditServiceHandlers:
    def __init__(
        self,
        *,
        writer: SqliteAuditLogWriter,
        verifier: DecisionRecordVerifier,
        governance_writer: AuditServiceGovernanceEventWriter,
    ) -> None:
        self._writer = writer
        self._verifier = verifier
        self._governance_writer = governance_writer

    def engine_append(self, entry: AuditEntry, service_name: str, token: bytes) -> AuditEntryId:
        caller = self._authenticate(token, expected_principal_id=f"service:{service_name}")
        return self._writer.append(
            AuditEntry(
                entry_type=entry.entry_type,
                payload={
                    **dict(entry.payload),
                    "caller_id": caller.principal_id,
                    "caller_kind": "service",
                },
                occurred_at_utc=entry.occurred_at_utc,
            )
        )

    def admin_append(self, entry: AuditEntry, principal_id: str, token: bytes) -> AuditEntryId:
        caller = self._authenticate(token, expected_principal_id=principal_id)
        return self._writer.append(
            AuditEntry(
                entry_type=entry.entry_type,
                payload={
                    **dict(entry.payload),
                    "caller_id": caller.principal_id,
                    "caller_kind": "admin",
                },
                occurred_at_utc=entry.occurred_at_utc,
            )
        )

    def _authenticate(self, token: bytes, *, expected_principal_id: str) -> AuthenticatedCaller:
        try:
            signed = signed_decision_from_json(token.decode("utf-8"))
            result = self._verifier.verify(signed)
        except Exception as exc:
            self._record_auth_failure(expected_principal_id, str(exc))
            raise AuditServiceAuthenticationError("invalid audit-service token") from exc
        if not result.success:
            self._record_auth_failure(expected_principal_id, str(result.error))
            raise AuditServiceAuthenticationError("invalid audit-service token")
        _require_expected_principal(signed, expected_principal_id)
        return AuthenticatedCaller(
            principal_id=str(signed.signing_principal_id),
            institution_id=signed.decision.role_snapshot.institution_id,
        )

    def _record_auth_failure(self, principal_id: str, reason: str) -> None:
        self._governance_writer.authentication_failed(principal_id, reason)


def entry_from_payload(data: dict[str, object]) -> AuditEntry:
    occurred_at = data.get("occurred_at_utc")
    payload = data.get("payload")
    if not isinstance(occurred_at, str):
        raise TypeError("occurred_at_utc must be a string")
    if not isinstance(payload, dict):
        raise TypeError("payload must be a JSON object")
    return AuditEntry(
        entry_type=_expect_str(data.get("entry_type"), "entry_type"),
        payload=dict(payload),
        occurred_at_utc=datetime.fromisoformat(occurred_at.replace("Z", "+00:00")),
    )


def entry_to_payload(entry: AuditEntry) -> dict[str, object]:
    return {
        "entry_type": entry.entry_type,
        "occurred_at_utc": entry.occurred_at_utc.isoformat(),
        "payload": dict(entry.payload),
    }


def _require_expected_principal(signed: SignedDecisionRecord, expected_principal_id: str) -> None:
    if str(signed.signing_principal_id) != expected_principal_id:
        raise AuditServiceAuthenticationError("token principal does not match caller")


def _expect_str(raw: object, field_name: str) -> str:
    if not isinstance(raw, str):
        raise TypeError(f"{field_name} must be a string")
    return raw
