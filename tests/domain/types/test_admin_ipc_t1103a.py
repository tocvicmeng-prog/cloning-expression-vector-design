"""
module_id: tests.domain.types.test_admin_ipc_t1103a
file: tests/domain/types/test_admin_ipc_t1103a.py
task_id: T-1103a
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from domain.types.admin_ipc import (
    AdminIpcErrorCode,
    AdminIpcRequest,
    AdminIpcResponse,
    AdminIpcStatus,
    AdminRequestId,
    AdminServiceVerb,
    SignedDecisionRecordPayload,
)
from tests.fakes.admin_service.client import signed_admin_token

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def test_admin_ipc_request_and_response_round_trip_canonical_payloads() -> None:
    token = signed_admin_token(now=NOW)
    request = AdminIpcRequest(
        request_id=AdminRequestId("req-1"),
        verb=AdminServiceVerb.MINT_PROFILE,
        principal_token=token,
        payload={"profile_id": "profile-1", "justification": "fixture"},
        requested_at_utc=NOW,
    )
    decision = SignedDecisionRecordPayload(
        decision_id="decision-1",
        decision_type="admin_service:mint_profile",
        policy_version="admin-service-contract-v1",
        signing_principal_id="principal-admin-1",
        signing_key_version="admin-token-key-v1",
        signed_payload_hash="0" * 64,
        signature_bytes_hex="66616b65",
    )
    response = AdminIpcResponse.accepted(
        request=request,
        payload={"profile_id": "profile-1"},
        decision_record=decision,
        responded_at_utc=NOW,
    )

    assert AdminIpcRequest.from_payload(request.to_payload()) == request
    assert AdminIpcResponse.from_payload(response.to_payload()) == response
    assert response.accepted_ok
    assert (
        request.canonical_json()
        == AdminIpcRequest.from_payload(request.to_payload()).canonical_json()
    )


def test_admin_ipc_response_rejects_success_without_decision_record() -> None:
    request = AdminIpcRequest(
        request_id=AdminRequestId("req-1"),
        verb=AdminServiceVerb.MINT_PROFILE,
        principal_token=signed_admin_token(now=NOW),
        payload={},
        requested_at_utc=NOW,
    )

    with pytest.raises(ValueError, match="signed decision record"):
        AdminIpcResponse(
            request_id=request.request_id,
            verb=request.verb,
            status=AdminIpcStatus.ACCEPTED,
            payload={},
            responded_at_utc=NOW,
        )


def test_admin_ipc_error_response_requires_error_message() -> None:
    request = AdminIpcRequest(
        request_id=AdminRequestId("req-1"),
        verb=AdminServiceVerb.MINT_PROFILE,
        principal_token=signed_admin_token(now=NOW),
        payload={},
        requested_at_utc=NOW,
    )

    with pytest.raises(ValueError, match="error_message"):
        AdminIpcResponse.error(
            request=request,
            error_code=AdminIpcErrorCode.VALIDATION_ERROR,
            error_message="",
            responded_at_utc=NOW,
        )
