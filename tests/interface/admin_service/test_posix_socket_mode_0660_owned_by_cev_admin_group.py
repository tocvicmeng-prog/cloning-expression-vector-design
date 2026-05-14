"""
module_id: tests.interface.admin_service.test_posix_socket_mode_0660_owned_by_cev_admin_group
file: tests/interface/admin_service/test_posix_socket_mode_0660_owned_by_cev_admin_group.py
task_id: T-1103b
"""

from __future__ import annotations

from interface.admin_service.ipc import (
    DEFAULT_POSIX_GROUP,
    DEFAULT_POSIX_MODE,
    AdminServiceAccessPolicy,
    validate_admin_service_access_policy,
)


def test_posix_socket_mode_0660_owned_by_cev_admin_group() -> None:
    policy = AdminServiceAccessPolicy(
        endpoint="/var/run/cev-admin/socket",
        service_account="cev-admin-svc",
        engine_account="cev-engine-svc",
        allowed_windows_sids=("S-1-5-32-544", "S-1-5-80-12345"),
        posix_mode=DEFAULT_POSIX_MODE,
        posix_group=DEFAULT_POSIX_GROUP,
    )

    validate_admin_service_access_policy(policy)

    assert policy.posix_mode == 0o660
    assert policy.posix_group == "cev-admin"
