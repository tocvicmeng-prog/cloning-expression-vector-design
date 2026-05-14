"""
module_id: tests.fakes.admin_service.client
file: tests/fakes/admin_service/client.py
task_id: T-1103a

Deterministic in-memory AdminServiceClientPort implementation for CLI/API tests.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import TypeAlias

from domain.sequence import sha256_text
from domain.types.admin_ipc import (
    ADMIN_IPC_PROTOCOL_VERSION,
    AdminIpcErrorCode,
    AdminIpcPayload,
    AdminIpcRequest,
    AdminIpcResponse,
    AdminPrincipalTokenId,
    AdminRequestId,
    AdminServiceVerb,
    SignedAdminPrincipalToken,
    SignedDecisionRecordPayload,
)

AdminRequestHandler: TypeAlias = Callable[
    [AdminIpcRequest],
    AdminIpcResponse | Mapping[str, object],
]


class InMemoryAdminServiceClient:
    def __init__(
        self,
        handlers: Mapping[AdminServiceVerb, AdminRequestHandler] | None = None,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._handlers = dict(handlers or {})
        self._clock = clock or (lambda: datetime.now(UTC))
        self._requests: list[AdminIpcRequest] = []
        self._sequence = 0

    @property
    def requests(self) -> tuple[AdminIpcRequest, ...]:
        return tuple(self._requests)

    def dispatch(self, request: AdminIpcRequest) -> AdminIpcResponse:
        self._requests.append(request)
        now = self._clock()
        if request.protocol_version != ADMIN_IPC_PROTOCOL_VERSION:
            return AdminIpcResponse.error(
                request=request,
                error_code=AdminIpcErrorCode.VERSION_MISMATCH,
                error_message="unsupported admin-service IPC protocol version",
                responded_at_utc=now,
            )
        if not request.principal_token.is_admin_authority:
            return AdminIpcResponse.error(
                request=request,
                error_code=AdminIpcErrorCode.AUTHENTICATION_FAILED,
                error_message="admin-service command token does not carry admin authority",
                responded_at_utc=now,
            )
        handler = self._handlers.get(request.verb, self._default_handler)
        try:
            result = handler(request)
        except PermissionError as exc:
            return AdminIpcResponse.denied(
                request=request,
                error_message=str(exc),
                responded_at_utc=now,
            )
        except Exception as exc:  # pragma: no cover - defensive contract boundary
            return AdminIpcResponse.error(
                request=request,
                error_code=AdminIpcErrorCode.HANDLER_ERROR,
                error_message=str(exc),
                responded_at_utc=now,
            )
        if isinstance(result, AdminIpcResponse):
            return result
        return AdminIpcResponse.accepted(
            request=request,
            payload=dict(result),
            decision_record=self._decision_for_request(request),
            responded_at_utc=now,
        )

    def mint_profile(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.MINT_PROFILE,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def modify_profile(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.MODIFY_PROFILE,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def revoke_profile(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.REVOKE_PROFILE,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def list_profiles(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.LIST_PROFILES,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def view_audit_trail(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.VIEW_AUDIT_TRAIL,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def mint_sop_template(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.MINT_SOP_TEMPLATE,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def modify_sop_template(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.MODIFY_SOP_TEMPLATE,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def revoke_sop_template(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.REVOKE_SOP_TEMPLATE,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def triage_review_queue_item(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def rotate_audit_key(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse:
        return self._invoke(
            AdminServiceVerb.ROTATE_AUDIT_KEY,
            principal_token,
            payload,
            request_id=request_id,
            requested_at_utc=requested_at_utc,
        )

    def _invoke(
        self,
        verb: AdminServiceVerb,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None,
        requested_at_utc: datetime | None,
    ) -> AdminIpcResponse:
        request = AdminIpcRequest(
            request_id=AdminRequestId(request_id or self._next_request_id(verb)),
            verb=verb,
            principal_token=principal_token,
            payload=payload,
            requested_at_utc=requested_at_utc or self._clock(),
        )
        return self.dispatch(request)

    def _default_handler(self, request: AdminIpcRequest) -> Mapping[str, object]:
        return {
            "handled_verb": request.verb.value,
            "request_payload": dict(request.payload),
        }

    def _next_request_id(self, verb: AdminServiceVerb) -> str:
        self._sequence += 1
        return f"{verb.value}-{self._sequence:06d}"

    def _decision_for_request(self, request: AdminIpcRequest) -> SignedDecisionRecordPayload:
        payload_hash = sha256_text(request.canonical_json().decode("utf-8"))
        return SignedDecisionRecordPayload(
            decision_id=f"decision-{request.request_id}",
            decision_type=f"admin_service:{request.verb.value}",
            policy_version="admin-service-contract-v1",
            signing_principal_id=request.principal_token.principal_id,
            signing_key_version=request.principal_token.signing_key_version,
            signed_payload_hash=str(payload_hash),
            signature_bytes_hex="66616b652d61646d696e2d6465636973696f6e",
        )


def signed_admin_token(
    *,
    principal_role: str = "administrator",
    now: datetime | None = None,
) -> SignedAdminPrincipalToken:
    issued_at = now or datetime(2026, 5, 14, tzinfo=UTC)
    return SignedAdminPrincipalToken(
        token_id=AdminPrincipalTokenId("token-admin-1"),
        principal_id="principal-admin-1",
        principal_role=principal_role,
        institution_id="inst",
        issued_at_utc=issued_at,
        expires_at_utc=issued_at.replace(year=issued_at.year + 1),
        signing_key_version="admin-token-key-v1",
        signature_bytes_hex="66616b652d61646d696e2d746f6b656e",
    )


__all__ = ["InMemoryAdminServiceClient", "signed_admin_token"]
