"""
module_id: adapter.ipc.admin_service_client_production
file: src/adapter/ipc/admin_service_client_production.py
task_id: T-1103b

Production AdminServiceClientPort implementation over local IPC.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from domain.types.admin_ipc import (
    AdminIpcPayload,
    AdminIpcRequest,
    AdminIpcResponse,
    AdminRequestId,
    AdminServiceVerb,
    SignedAdminPrincipalToken,
)
from interface.admin_service.ipc import (
    AdminServiceProtocolError,
    AdminServiceServer,
    decode_admin_frame,
    encode_admin_frame,
)


class AdminServiceUnreachableError(ConnectionError):
    """Raised when the admin-service IPC endpoint cannot be reached."""


class AdminServiceTransport(Protocol):
    def send(self, frame: bytes, *, timeout_seconds: float) -> bytes: ...


class InProcessAdminServiceTransport:
    def __init__(self, server: AdminServiceServer, *, fail_first_attempts: int = 0) -> None:
        self._server = server
        self._remaining_failures = fail_first_attempts

    def send(self, frame: bytes, *, timeout_seconds: float) -> bytes:
        if self._remaining_failures > 0:
            self._remaining_failures -= 1
            raise TimeoutError(f"simulated admin-service timeout after {timeout_seconds}s")
        return self._server.handle_frame(frame)


class AdminServiceClient:
    def __init__(
        self,
        *,
        transport: AdminServiceTransport,
        timeout_seconds: float = 5.0,
        retries: int = 3,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._transport = transport
        self._timeout_seconds = timeout_seconds
        self._retries = retries
        self._clock = clock or (lambda: datetime.now(UTC))
        self._sequence = 0

    def dispatch(self, request: AdminIpcRequest) -> AdminIpcResponse:
        raw = self._send_with_retries(encode_admin_frame(request.to_payload()))
        payload = decode_admin_frame(raw)
        if payload.get("ok") is False:
            raise AdminServiceProtocolError(str(payload.get("error_message", "IPC rejected")))
        return AdminIpcResponse.from_payload(payload)

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

    def _send_with_retries(self, frame: bytes) -> bytes:
        attempts = self._retries + 1
        last_timeout: TimeoutError | None = None
        for _attempt in range(attempts):
            try:
                return self._transport.send(frame, timeout_seconds=self._timeout_seconds)
            except TimeoutError as exc:
                last_timeout = exc
        raise AdminServiceUnreachableError("admin-service IPC timed out") from last_timeout

    def _next_request_id(self, verb: AdminServiceVerb) -> str:
        self._sequence += 1
        return f"{verb.value}-{self._sequence:06d}"


def admin_response_to_json(response: AdminIpcResponse) -> str:
    return json.dumps(response.to_payload(), sort_keys=True, separators=(",", ":"))


__all__ = [
    "AdminServiceClient",
    "AdminServiceTransport",
    "AdminServiceUnreachableError",
    "InProcessAdminServiceTransport",
    "admin_response_to_json",
]
