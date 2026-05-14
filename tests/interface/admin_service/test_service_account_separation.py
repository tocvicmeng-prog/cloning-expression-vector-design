"""
module_id: tests.interface.admin_service.test_service_account_separation
file: tests/interface/admin_service/test_service_account_separation.py
task_id: T-1103b
"""

from __future__ import annotations

import pytest

from interface.admin_service.ipc import (
    AdminServiceAccessPolicy,
    validate_admin_service_access_policy,
)


def test_service_account_separation() -> None:
    policy = AdminServiceAccessPolicy(
        endpoint="/var/run/cev-admin/socket",
        service_account="cev-admin-svc",
        engine_account="cev-engine-svc",
        allowed_windows_sids=("S-1-5-32-544", "S-1-5-80-12345"),
        posix_mode=0o660,
        posix_group="cev-admin",
    )

    validate_admin_service_access_policy(policy)

    assert policy.service_account_separated


def test_service_account_separation_rejects_shared_account() -> None:
    policy = AdminServiceAccessPolicy(
        endpoint="/var/run/cev-admin/socket",
        service_account="cev-admin-svc",
        engine_account="cev-admin-svc",
        allowed_windows_sids=("S-1-5-32-544", "S-1-5-80-12345"),
        posix_mode=0o660,
        posix_group="cev-admin",
    )

    with pytest.raises(ValueError, match="separate from engine account"):
        validate_admin_service_access_policy(policy)
