"""
module_id: adapter.ipc.audit_service_client
file: src/adapter/ipc/audit_service_client.py
task_id: T-313b

Audit-service IPC client implementing audit append ports.
"""

from __future__ import annotations

import base64
import json
from collections.abc import Callable
from typing import Protocol

from domain.ports.audit_append import AuditEntry, AuditEntryId
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, ServicePrincipal
from interface.audit_service.handlers import entry_to_payload
from interface.audit_service.server import AuditServiceServer


class AuditServiceUnreachableError(ConnectionError):
    """Raised when the audit-service IPC endpoint cannot be reached."""


class AuditServiceTransport(Protocol):
    def send(self, frame: bytes, *, timeout_seconds: float) -> bytes: ...


class InProcessAuditServiceTransport:
    def __init__(self, server: AuditServiceServer, *, fail_first_attempts: int = 0) -> None:
        self._server = server
        self._remaining_failures = fail_first_attempts

    def send(self, frame: bytes, *, timeout_seconds: float) -> bytes:
        if self._remaining_failures > 0:
            self._remaining_failures -= 1
            raise TimeoutError(f"simulated audit-service timeout after {timeout_seconds}s")
        return self._server.handle_frame(frame)


TokenProvider = Callable[[ServicePrincipal | AdminPrincipal | DeveloperBootstrapPrincipal], bytes]


class AuditServiceClient:
    def __init__(
        self,
        *,
        transport: AuditServiceTransport,
        token_provider: TokenProvider,
        timeout_seconds: float = 5.0,
        retries: int = 3,
    ) -> None:
        self._transport = transport
        self._token_provider = token_provider
        self._timeout_seconds = timeout_seconds
        self._retries = retries

    def append(
        self,
        entry: AuditEntry,
        caller: ServicePrincipal | AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> AuditEntryId:
        token = self._token_provider(caller)
        if isinstance(caller, ServicePrincipal):
            request = {
                "entry": entry_to_payload(entry),
                "service_name": caller.service_name.value,
                "token": base64.b64encode(token).decode("ascii"),
                "verb": "engine_append",
            }
        else:
            request = {
                "entry": entry_to_payload(entry),
                "principal_id": str(caller.id),
                "token": base64.b64encode(token).decode("ascii"),
                "verb": "admin_append",
            }
        response = self._send_with_retries(
            json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        if not response.get("ok"):
            raise PermissionError(str(response.get("error", "audit-service append rejected")))
        return AuditEntryId(str(response["entry_id"]))

    def _send_with_retries(self, frame: bytes) -> dict[str, object]:
        attempts = self._retries + 1
        last_error: TimeoutError | None = None
        for _attempt in range(attempts):
            try:
                raw = self._transport.send(frame, timeout_seconds=self._timeout_seconds)
                decoded = json.loads(raw.decode("utf-8"))
                if not isinstance(decoded, dict):
                    raise AuditServiceUnreachableError("audit-service response was not an object")
                return dict(decoded)
            except TimeoutError as exc:
                last_error = exc
        raise AuditServiceUnreachableError("audit-service IPC timed out") from last_error
