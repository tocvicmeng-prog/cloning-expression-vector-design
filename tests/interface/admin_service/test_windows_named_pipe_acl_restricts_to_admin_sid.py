"""
module_id: tests.interface.admin_service.test_windows_named_pipe_acl_restricts_to_admin_sid
file: tests/interface/admin_service/test_windows_named_pipe_acl_restricts_to_admin_sid.py
task_id: T-1103b
"""

from __future__ import annotations

from interface.admin_service.ipc import (
    WINDOWS_ADMINISTRATORS_SID,
    admin_service_access_policy_for_platform,
    validate_admin_service_access_policy,
)


def test_windows_named_pipe_acl_restricts_to_admin_sid() -> None:
    service_sid = "S-1-5-80-12345"
    policy = admin_service_access_policy_for_platform(
        endpoint=r"\\.\pipe\cev-admin-service",
        service_sid=service_sid,
    )

    validate_admin_service_access_policy(policy)

    assert WINDOWS_ADMINISTRATORS_SID in policy.allowed_windows_sids
    assert service_sid in policy.allowed_windows_sids
    assert "S-1-5-11" not in policy.allowed_windows_sids
