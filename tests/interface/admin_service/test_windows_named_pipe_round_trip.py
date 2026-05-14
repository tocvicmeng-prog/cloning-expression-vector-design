"""
module_id: tests.interface.admin_service.test_windows_named_pipe_round_trip
file: tests/interface/admin_service/test_windows_named_pipe_round_trip.py
task_id: T-1103b
"""

from __future__ import annotations

from domain.types.admin_ipc import AdminIpcStatus
from interface.admin_service import admin_service_access_policy_for_platform
from tests.interface.admin_service.helpers import NOW, harness, token


def test_windows_named_pipe_round_trip() -> None:
    policy = admin_service_access_policy_for_platform(endpoint=r"\\.\pipe\cev-admin-service")
    app = harness()

    response = app.client.list_profiles(
        token(),
        {"endpoint": policy.endpoint},
        requested_at_utc=NOW,
    )

    assert policy.endpoint == r"\\.\pipe\cev-admin-service"
    assert response.status is AdminIpcStatus.ACCEPTED
    assert response.payload["request_payload"] == {"endpoint": policy.endpoint}
