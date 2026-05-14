"""
module_id: tests.fakes.admin_service.test_in_memory_client
file: tests/fakes/admin_service/test_in_memory_client.py
task_id: T-1103a
"""

from __future__ import annotations

from datetime import UTC, datetime

from domain.types.admin_ipc import (
    AdminIpcErrorCode,
    AdminIpcRequest,
    AdminIpcStatus,
    AdminRequestId,
    AdminServiceVerb,
)
from tests.fakes.admin_service.client import InMemoryAdminServiceClient, signed_admin_token

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def test_in_memory_client_routes_to_configured_handler_without_real_ipc() -> None:
    observed: list[AdminIpcRequest] = []

    def handler(request: AdminIpcRequest) -> dict[str, object]:
        observed.append(request)
        return {"resolved_item_id": str(request.payload["item_id"])}

    client = InMemoryAdminServiceClient(
        {AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM: handler},
        clock=lambda: NOW,
    )

    response = client.triage_review_queue_item(
        signed_admin_token(now=NOW),
        {"item_id": "review-item-1"},
        request_id="triage-1",
        requested_at_utc=NOW,
    )

    assert response.status is AdminIpcStatus.ACCEPTED
    assert response.payload == {"resolved_item_id": "review-item-1"}
    assert observed == list(client.requests)


def test_in_memory_client_denies_non_admin_tokens() -> None:
    client = InMemoryAdminServiceClient(clock=lambda: NOW)

    response = client.rotate_audit_key(
        signed_admin_token(principal_role="user", now=NOW),
        {"reason": "fixture"},
        request_id="rotate-1",
        requested_at_utc=NOW,
    )

    assert response.status is AdminIpcStatus.ERROR
    assert response.error_code is AdminIpcErrorCode.AUTHENTICATION_FAILED


def test_in_memory_client_reports_version_mismatch() -> None:
    client = InMemoryAdminServiceClient(clock=lambda: NOW)
    request = AdminIpcRequest(
        request_id=AdminRequestId("req-old-version"),
        verb=AdminServiceVerb.MINT_PROFILE,
        principal_token=signed_admin_token(now=NOW),
        payload={},
        requested_at_utc=NOW,
        protocol_version="admin-service-ipc.v0",
    )

    response = client.dispatch(request)

    assert response.status is AdminIpcStatus.ERROR
    assert response.error_code is AdminIpcErrorCode.VERSION_MISMATCH
