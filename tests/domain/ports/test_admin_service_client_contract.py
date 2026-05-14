"""
module_id: tests.domain.ports.test_admin_service_client_contract
file: tests/domain/ports/test_admin_service_client_contract.py
task_id: T-1103a
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from domain.ports import AdminServiceClientPort
from domain.types.admin_ipc import AdminIpcResponse, AdminIpcStatus, AdminServiceVerb
from tests.fakes.admin_service.client import InMemoryAdminServiceClient, signed_admin_token

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def assert_admin_service_client_contract(client: AdminServiceClientPort) -> None:
    token = signed_admin_token(now=NOW)
    verb_methods: tuple[
        tuple[AdminServiceVerb, Callable[..., AdminIpcResponse]],
        ...,
    ] = (
        (AdminServiceVerb.MINT_PROFILE, client.mint_profile),
        (AdminServiceVerb.MODIFY_PROFILE, client.modify_profile),
        (AdminServiceVerb.REVOKE_PROFILE, client.revoke_profile),
        (AdminServiceVerb.LIST_PROFILES, client.list_profiles),
        (AdminServiceVerb.VIEW_AUDIT_TRAIL, client.view_audit_trail),
        (AdminServiceVerb.MINT_SOP_TEMPLATE, client.mint_sop_template),
        (AdminServiceVerb.MODIFY_SOP_TEMPLATE, client.modify_sop_template),
        (AdminServiceVerb.REVOKE_SOP_TEMPLATE, client.revoke_sop_template),
        (AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM, client.triage_review_queue_item),
        (AdminServiceVerb.ROTATE_AUDIT_KEY, client.rotate_audit_key),
    )

    for verb, method in verb_methods:
        response = method(
            token,
            {"fixture": verb.value},
            request_id=f"request-{verb.value}",
            requested_at_utc=NOW,
        )
        assert response.status is AdminIpcStatus.ACCEPTED
        assert response.verb is verb
        assert response.request_id == f"request-{verb.value}"
        assert response.decision_record is not None
        assert response.decision_record.decision_type == f"admin_service:{verb.value}"


def test_in_memory_admin_service_client_satisfies_contract() -> None:
    assert_admin_service_client_contract(
        InMemoryAdminServiceClient(clock=lambda: NOW),
    )
