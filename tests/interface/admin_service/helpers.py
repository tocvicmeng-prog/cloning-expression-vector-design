"""
module_id: tests.interface.admin_service.helpers
file: tests/interface/admin_service/helpers.py
task_id: T-1103b
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from adapter.ipc.admin_service_client_production import (
    AdminServiceClient,
    InProcessAdminServiceTransport,
)
from domain.ports.audit_key import AuditKeyProvider
from domain.types.admin_ipc import (
    AdminIpcRequest,
    AdminPrincipalTokenId,
    AdminServiceVerb,
    SignedAdminPrincipalToken,
)
from interface.admin_service import (
    AdminServiceAuthenticator,
    AdminServiceHandlers,
    AdminServiceReviewQueueHandler,
    AdminServiceServer,
    InMemoryAdminServiceSecurityLog,
)
from interface.admin_service.handlers import AdminVerbHandler

NOW = datetime(2026, 5, 14, tzinfo=UTC)


@dataclass(frozen=True)
class AdminServiceHarness:
    client: AdminServiceClient
    security_log: InMemoryAdminServiceSecurityLog


def token(
    principal_role: str = "administrator",
    *,
    principal_id: str | None = None,
    issued_at: datetime = NOW,
    expires_at: datetime | None = None,
) -> SignedAdminPrincipalToken:
    resolved_principal_id = principal_id or f"principal-{principal_role.replace('_', '-')}"
    return SignedAdminPrincipalToken(
        token_id=AdminPrincipalTokenId(f"token-{resolved_principal_id}"),
        principal_id=resolved_principal_id,
        principal_role=principal_role,
        institution_id="inst",
        issued_at_utc=issued_at,
        expires_at_utc=expires_at or issued_at + timedelta(days=365),
        signing_key_version="admin-token-key-v1",
        signature_bytes_hex="66616b652d61646d696e2d746f6b656e",
    )


def harness(
    *,
    handlers: Mapping[AdminServiceVerb, AdminVerbHandler] | None = None,
    review_queue_handler: AdminServiceReviewQueueHandler | None = None,
    audit_key_provider: AuditKeyProvider | None = None,
) -> AdminServiceHarness:
    security_log = InMemoryAdminServiceSecurityLog()
    service_handlers = AdminServiceHandlers(
        authenticator=AdminServiceAuthenticator(clock=lambda: NOW),
        review_queue_handler=review_queue_handler,
        audit_key_provider=audit_key_provider,
        handlers=handlers,
        security_log=security_log,
        clock=lambda: NOW,
    )
    server = AdminServiceServer(service_handlers)
    client = AdminServiceClient(
        transport=InProcessAdminServiceTransport(server),
        clock=lambda: NOW,
    )
    return AdminServiceHarness(client=client, security_log=security_log)


def accepted_handler(principal_seen: list[str]) -> AdminVerbHandler:
    def _handler(principal: object, request: AdminIpcRequest) -> dict[str, object]:
        principal_seen.append(type(principal).__name__)
        return {"handled_verb": request.verb.value, "principal_type": type(principal).__name__}

    return _handler
