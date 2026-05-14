"""
module_id: domain.types.admin_ipc
file: src/domain/types/admin_ipc.py
task_id: T-1103a

Canonical request and response envelopes for admin-service IPC.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, NewType, Self

from domain.canonicalisation import canonical_json, canonical_sha256
from domain.sequence import Sha256

ADMIN_IPC_PROTOCOL_VERSION = "admin-service-ipc.v1"

AdminRequestId = NewType("AdminRequestId", str)
AdminPrincipalTokenId = NewType("AdminPrincipalTokenId", str)
AdminIpcPayload = Mapping[str, object]


class AdminServiceVerb(Enum):
    MINT_PROFILE = "mint_profile"
    MODIFY_PROFILE = "modify_profile"
    REVOKE_PROFILE = "revoke_profile"
    LIST_PROFILES = "list_profiles"
    VIEW_AUDIT_TRAIL = "view_audit_trail"
    MINT_SOP_TEMPLATE = "mint_sop_template"
    MODIFY_SOP_TEMPLATE = "modify_sop_template"
    REVOKE_SOP_TEMPLATE = "revoke_sop_template"
    TRIAGE_REVIEW_QUEUE_ITEM = "triage_review_queue_item"
    ROTATE_AUDIT_KEY = "rotate_audit_key"


class AdminIpcStatus(Enum):
    ACCEPTED = "accepted"
    DENIED = "denied"
    ERROR = "error"


class AdminIpcErrorCode(Enum):
    AUTHENTICATION_FAILED = "authentication_failed"
    HANDLER_ERROR = "handler_error"
    PERMISSION_DENIED = "permission_denied"
    UNKNOWN_VERB = "unknown_verb"
    VALIDATION_ERROR = "validation_error"
    VERSION_MISMATCH = "version_mismatch"


@dataclass(frozen=True, slots=True)
class SignedAdminPrincipalToken:
    token_id: AdminPrincipalTokenId
    principal_id: str
    principal_role: str
    institution_id: str
    issued_at_utc: datetime
    expires_at_utc: datetime
    signing_key_version: str
    signature_bytes_hex: str

    def __post_init__(self) -> None:
        _require_non_empty(str(self.token_id), "token_id")
        _require_non_empty(self.principal_id, "principal_id")
        _require_non_empty(self.principal_role, "principal_role")
        _require_non_empty(self.institution_id, "institution_id")
        _require_aware(self.issued_at_utc, "issued_at_utc")
        _require_aware(self.expires_at_utc, "expires_at_utc")
        if self.expires_at_utc <= self.issued_at_utc:
            raise ValueError("expires_at_utc must be after issued_at_utc")
        _require_non_empty(self.signing_key_version, "signing_key_version")
        _require_hex(self.signature_bytes_hex, "signature_bytes_hex")

    @property
    def is_admin_authority(self) -> bool:
        return self.principal_role in {"administrator", "developer_bootstrap"}

    def to_payload(self) -> dict[str, object]:
        return {
            "token_id": str(self.token_id),
            "principal_id": self.principal_id,
            "principal_role": self.principal_role,
            "institution_id": self.institution_id,
            "issued_at_utc": _datetime_to_wire(self.issued_at_utc),
            "expires_at_utc": _datetime_to_wire(self.expires_at_utc),
            "signing_key_version": self.signing_key_version,
            "signature_bytes_hex": self.signature_bytes_hex,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        return cls(
            token_id=AdminPrincipalTokenId(_expect_str(payload, "token_id")),
            principal_id=_expect_str(payload, "principal_id"),
            principal_role=_expect_str(payload, "principal_role"),
            institution_id=_expect_str(payload, "institution_id"),
            issued_at_utc=_parse_datetime(_expect_str(payload, "issued_at_utc")),
            expires_at_utc=_parse_datetime(_expect_str(payload, "expires_at_utc")),
            signing_key_version=_expect_str(payload, "signing_key_version"),
            signature_bytes_hex=_expect_str(payload, "signature_bytes_hex"),
        )

    def canonical_json(self) -> bytes:
        return canonical_json(self.to_payload())

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())


@dataclass(frozen=True, slots=True)
class SignedDecisionRecordPayload:
    decision_id: str
    decision_type: str
    policy_version: str
    signing_principal_id: str
    signing_key_version: str
    signed_payload_hash: str
    signature_bytes_hex: str

    def __post_init__(self) -> None:
        _require_non_empty(self.decision_id, "decision_id")
        _require_non_empty(self.decision_type, "decision_type")
        _require_non_empty(self.policy_version, "policy_version")
        _require_non_empty(self.signing_principal_id, "signing_principal_id")
        _require_non_empty(self.signing_key_version, "signing_key_version")
        _require_non_empty(self.signed_payload_hash, "signed_payload_hash")
        _require_hex(self.signature_bytes_hex, "signature_bytes_hex")

    @classmethod
    def from_signed_decision_record(cls, signed: Any) -> Self:
        return cls(
            decision_id=signed.decision.decision_id,
            decision_type=signed.decision.decision_type,
            policy_version=signed.decision.policy_version,
            signing_principal_id=str(signed.signing_principal_id),
            signing_key_version=str(signed.signing_key_version),
            signed_payload_hash=str(signed.signed_payload_hash),
            signature_bytes_hex=signed.signature_bytes.hex(),
        )

    def to_payload(self) -> dict[str, str]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "policy_version": self.policy_version,
            "signing_principal_id": self.signing_principal_id,
            "signing_key_version": self.signing_key_version,
            "signed_payload_hash": self.signed_payload_hash,
            "signature_bytes_hex": self.signature_bytes_hex,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        return cls(
            decision_id=_expect_str(payload, "decision_id"),
            decision_type=_expect_str(payload, "decision_type"),
            policy_version=_expect_str(payload, "policy_version"),
            signing_principal_id=_expect_str(payload, "signing_principal_id"),
            signing_key_version=_expect_str(payload, "signing_key_version"),
            signed_payload_hash=_expect_str(payload, "signed_payload_hash"),
            signature_bytes_hex=_expect_str(payload, "signature_bytes_hex"),
        )


@dataclass(frozen=True, slots=True)
class AdminIpcRequest:
    request_id: AdminRequestId
    verb: AdminServiceVerb
    principal_token: SignedAdminPrincipalToken
    payload: AdminIpcPayload
    requested_at_utc: datetime
    protocol_version: str = ADMIN_IPC_PROTOCOL_VERSION

    def __post_init__(self) -> None:
        _require_non_empty(str(self.request_id), "request_id")
        _require_non_empty(self.protocol_version, "protocol_version")
        _require_aware(self.requested_at_utc, "requested_at_utc")
        _validate_payload(self.payload, "payload")

    def to_payload(self) -> dict[str, object]:
        return {
            "protocol_version": self.protocol_version,
            "request_id": str(self.request_id),
            "verb": self.verb.value,
            "principal_token": self.principal_token.to_payload(),
            "payload": dict(self.payload),
            "requested_at_utc": _datetime_to_wire(self.requested_at_utc),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        return cls(
            protocol_version=_expect_str(payload, "protocol_version"),
            request_id=AdminRequestId(_expect_str(payload, "request_id")),
            verb=AdminServiceVerb(_expect_str(payload, "verb")),
            principal_token=SignedAdminPrincipalToken.from_payload(
                _expect_mapping(payload, "principal_token")
            ),
            payload=_expect_mapping(payload, "payload"),
            requested_at_utc=_parse_datetime(_expect_str(payload, "requested_at_utc")),
        )

    def canonical_json(self) -> bytes:
        return canonical_json(self.to_payload())

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())


@dataclass(frozen=True, slots=True)
class AdminIpcResponse:
    request_id: AdminRequestId
    verb: AdminServiceVerb
    status: AdminIpcStatus
    payload: AdminIpcPayload
    responded_at_utc: datetime
    decision_record: SignedDecisionRecordPayload | None = None
    error_code: AdminIpcErrorCode | None = None
    error_message: str | None = None
    protocol_version: str = ADMIN_IPC_PROTOCOL_VERSION

    def __post_init__(self) -> None:
        _require_non_empty(str(self.request_id), "request_id")
        _require_non_empty(self.protocol_version, "protocol_version")
        _require_aware(self.responded_at_utc, "responded_at_utc")
        _validate_payload(self.payload, "payload")
        if self.status is AdminIpcStatus.ACCEPTED and self.decision_record is None:
            raise ValueError("accepted admin IPC responses require a signed decision record")
        if self.status is not AdminIpcStatus.ACCEPTED:
            if self.error_code is None:
                raise ValueError("non-accepted admin IPC responses require an error_code")
            _require_non_empty(self.error_message or "", "error_message")

    @classmethod
    def accepted(
        cls,
        *,
        request: AdminIpcRequest,
        payload: AdminIpcPayload,
        decision_record: SignedDecisionRecordPayload,
        responded_at_utc: datetime,
    ) -> Self:
        return cls(
            request_id=request.request_id,
            verb=request.verb,
            status=AdminIpcStatus.ACCEPTED,
            payload=payload,
            decision_record=decision_record,
            responded_at_utc=responded_at_utc,
            protocol_version=request.protocol_version,
        )

    @classmethod
    def denied(
        cls,
        *,
        request: AdminIpcRequest,
        error_message: str,
        responded_at_utc: datetime,
        payload: AdminIpcPayload | None = None,
    ) -> Self:
        return cls(
            request_id=request.request_id,
            verb=request.verb,
            status=AdminIpcStatus.DENIED,
            payload={} if payload is None else payload,
            error_code=AdminIpcErrorCode.PERMISSION_DENIED,
            error_message=error_message,
            responded_at_utc=responded_at_utc,
            protocol_version=request.protocol_version,
        )

    @classmethod
    def error(
        cls,
        *,
        request: AdminIpcRequest,
        error_code: AdminIpcErrorCode,
        error_message: str,
        responded_at_utc: datetime,
        payload: AdminIpcPayload | None = None,
    ) -> Self:
        return cls(
            request_id=request.request_id,
            verb=request.verb,
            status=AdminIpcStatus.ERROR,
            payload={} if payload is None else payload,
            error_code=error_code,
            error_message=error_message,
            responded_at_utc=responded_at_utc,
            protocol_version=request.protocol_version,
        )

    @property
    def accepted_ok(self) -> bool:
        return self.status is AdminIpcStatus.ACCEPTED

    def to_payload(self) -> dict[str, object]:
        return {
            "protocol_version": self.protocol_version,
            "request_id": str(self.request_id),
            "verb": self.verb.value,
            "status": self.status.value,
            "payload": dict(self.payload),
            "responded_at_utc": _datetime_to_wire(self.responded_at_utc),
            "decision_record": None
            if self.decision_record is None
            else self.decision_record.to_payload(),
            "error_code": None if self.error_code is None else self.error_code.value,
            "error_message": self.error_message,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> Self:
        raw_decision = payload.get("decision_record")
        raw_error_code = payload.get("error_code")
        return cls(
            protocol_version=_expect_str(payload, "protocol_version"),
            request_id=AdminRequestId(_expect_str(payload, "request_id")),
            verb=AdminServiceVerb(_expect_str(payload, "verb")),
            status=AdminIpcStatus(_expect_str(payload, "status")),
            payload=_expect_mapping(payload, "payload"),
            responded_at_utc=_parse_datetime(_expect_str(payload, "responded_at_utc")),
            decision_record=None
            if raw_decision is None
            else SignedDecisionRecordPayload.from_payload(
                _expect_mapping(payload, "decision_record")
            ),
            error_code=None
            if raw_error_code is None
            else AdminIpcErrorCode(_expect_str(payload, "error_code")),
            error_message=_optional_str(payload.get("error_message")),
        )

    def canonical_json(self) -> bytes:
        return canonical_json(self.to_payload())

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())


def _validate_payload(payload: Mapping[str, object], field_name: str) -> None:
    for key in payload:
        if not isinstance(key, str):
            raise TypeError(f"{field_name} keys must be strings")
        _require_non_empty(key, f"{field_name} key")
    canonical_json(payload)


def _expect_mapping(payload: Mapping[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise TypeError(f"{key} must be an object")
    return dict(value)


def _expect_str(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    return value


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("optional string field must be a string")
    return value


def _require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} cannot be empty")


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_hex(value: str, field_name: str) -> None:
    _require_non_empty(value, field_name)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be lowercase hex") from exc
    if value.lower() != value:
        raise ValueError(f"{field_name} must be lowercase hex")


def _datetime_to_wire(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


__all__ = [
    "ADMIN_IPC_PROTOCOL_VERSION",
    "AdminIpcErrorCode",
    "AdminIpcPayload",
    "AdminIpcRequest",
    "AdminIpcResponse",
    "AdminIpcStatus",
    "AdminPrincipalTokenId",
    "AdminRequestId",
    "AdminServiceVerb",
    "SignedAdminPrincipalToken",
    "SignedDecisionRecordPayload",
]
