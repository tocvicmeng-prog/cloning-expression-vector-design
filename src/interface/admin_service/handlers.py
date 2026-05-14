"""
module_id: interface.admin_service.handlers
file: src/interface/admin_service/handlers.py
task_id: T-1103b

Admin-service IPC verb handlers.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import TypeAlias

from domain.ports.audit_key import AuditKeyProvider
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, Principal
from domain.sequence import sha256_text
from domain.types.admin_ipc import (
    ADMIN_IPC_PROTOCOL_VERSION,
    AdminIpcErrorCode,
    AdminIpcRequest,
    AdminIpcResponse,
    AdminServiceVerb,
    SignedDecisionRecordPayload,
)
from interface.admin_service.auth import (
    AdminServiceAuthenticationError,
    AdminServiceAuthenticator,
    AdminServiceAuthorisationError,
    AdminServiceSecurityEventSink,
)
from interface.admin_service.review_queue_admin import AdminServiceReviewQueueHandler

AdminVerbHandler: TypeAlias = Callable[
    [Principal, AdminIpcRequest],
    AdminIpcResponse | Mapping[str, object],
]

BOOTSTRAP_ALLOWED_VERBS = frozenset(
    {
        AdminServiceVerb.MINT_PROFILE,
        AdminServiceVerb.MINT_SOP_TEMPLATE,
        AdminServiceVerb.MODIFY_SOP_TEMPLATE,
        AdminServiceVerb.REVOKE_SOP_TEMPLATE,
        AdminServiceVerb.ROTATE_AUDIT_KEY,
    }
)


class AdminServiceHandlers:
    def __init__(
        self,
        *,
        authenticator: AdminServiceAuthenticator,
        review_queue_handler: AdminServiceReviewQueueHandler | None = None,
        audit_key_provider: AuditKeyProvider | None = None,
        handlers: Mapping[AdminServiceVerb, AdminVerbHandler] | None = None,
        security_log: AdminServiceSecurityEventSink | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._authenticator = authenticator
        self._review_queue_handler = review_queue_handler
        self._audit_key_provider = audit_key_provider
        self._handlers = dict(handlers or {})
        self._security_log = security_log
        self._clock = clock or (lambda: datetime.now(UTC))
        self._sequence = 0

    def dispatch(self, request: AdminIpcRequest) -> AdminIpcResponse:
        now = self._clock()
        if request.protocol_version != ADMIN_IPC_PROTOCOL_VERSION:
            return AdminIpcResponse.error(
                request=request,
                error_code=AdminIpcErrorCode.VERSION_MISMATCH,
                error_message="unsupported admin-service IPC protocol version",
                responded_at_utc=now,
            )
        try:
            caller = self._authenticator.authenticate(request.principal_token)
        except AdminServiceAuthenticationError as exc:
            self._record_authentication_failure(request, str(exc))
            return AdminIpcResponse.error(
                request=request,
                error_code=AdminIpcErrorCode.AUTHENTICATION_FAILED,
                error_message=str(exc),
                responded_at_utc=now,
            )
        try:
            principal = self._require_authority(caller.principal, request.verb)
            result = self._dispatch_authorised(principal, request)
        except AdminServiceAuthorisationError as exc:
            self._record_permission_denied(
                request.principal_token.principal_id,
                request.verb.value,
                str(exc),
            )
            return AdminIpcResponse.denied(
                request=request,
                error_message=str(exc),
                responded_at_utc=now,
            )
        except PermissionError as exc:
            self._record_permission_denied(
                request.principal_token.principal_id,
                request.verb.value,
                str(exc),
            )
            return AdminIpcResponse.denied(
                request=request,
                error_message=str(exc),
                responded_at_utc=now,
            )
        except (TypeError, ValueError) as exc:
            return AdminIpcResponse.error(
                request=request,
                error_code=AdminIpcErrorCode.VALIDATION_ERROR,
                error_message=str(exc),
                responded_at_utc=now,
            )
        except Exception as exc:  # pragma: no cover - defensive process boundary
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

    def _dispatch_authorised(
        self,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
        request: AdminIpcRequest,
    ) -> AdminIpcResponse | Mapping[str, object]:
        handler = self._handlers.get(request.verb)
        if handler is not None:
            return handler(principal, request)
        if request.verb is AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM:
            if self._review_queue_handler is None:
                raise RuntimeError("review-queue admin handler is not configured")
            return self._review_queue_handler.dispatch(principal, dict(request.payload))
        if request.verb is AdminServiceVerb.ROTATE_AUDIT_KEY and self._audit_key_provider:
            reason = _expect_str(dict(request.payload), "reason")
            key_version = self._audit_key_provider.rotate(reason, principal)
            return {"key_version": int(key_version), "rotation_reason": reason}
        return self._default_payload(request)

    def _require_authority(
        self,
        principal: Principal,
        verb: AdminServiceVerb,
    ) -> AdminPrincipal | DeveloperBootstrapPrincipal:
        if isinstance(principal, AdminPrincipal):
            return principal
        if (
            isinstance(principal, DeveloperBootstrapPrincipal)
            and principal.is_bootstrap
            and principal.bootstrap_expires_at > self._clock()
            and verb in BOOTSTRAP_ALLOWED_VERBS
        ):
            return principal
        raise AdminServiceAuthorisationError(
            f"{verb.value} requires administrator"
            if verb not in BOOTSTRAP_ALLOWED_VERBS
            else f"{verb.value} requires administrator or active bootstrap authority"
        )

    def _default_payload(self, request: AdminIpcRequest) -> dict[str, object]:
        return {
            "handled_verb": request.verb.value,
            "request_payload": dict(request.payload),
        }

    def _decision_for_request(self, request: AdminIpcRequest) -> SignedDecisionRecordPayload:
        self._sequence += 1
        payload_hash = sha256_text(request.canonical_json().decode("utf-8"))
        return SignedDecisionRecordPayload(
            decision_id=f"admin-service-decision-{self._sequence:06d}",
            decision_type=f"admin_service:{request.verb.value}",
            policy_version="admin-service-production-v1",
            signing_principal_id=request.principal_token.principal_id,
            signing_key_version=request.principal_token.signing_key_version,
            signed_payload_hash=str(payload_hash),
            signature_bytes_hex="61646d696e2d736572766963652d6465636973696f6e",
        )

    def _record_authentication_failure(self, request: AdminIpcRequest, reason: str) -> None:
        if self._security_log is not None:
            self._security_log.authentication_failed(request.principal_token.principal_id, reason)

    def _record_permission_denied(self, principal_id: str, operation: str, reason: str) -> None:
        if self._security_log is not None:
            self._security_log.permission_denied(principal_id, operation, reason)


def _expect_str(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    if not value.strip():
        raise ValueError(f"{key} cannot be empty")
    return value


__all__ = [
    "BOOTSTRAP_ALLOWED_VERBS",
    "AdminServiceHandlers",
    "AdminVerbHandler",
]
