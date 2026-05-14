"""
module_id: interface.admin_service.__main__
file: src/interface/admin_service/__main__.py
task_id: T-1103b

Admin-service process entry point.
"""

from __future__ import annotations

from interface.admin_service.ipc import (
    admin_service_access_policy_for_platform,
    validate_admin_service_access_policy,
)


def main() -> int:
    policy = admin_service_access_policy_for_platform()
    validate_admin_service_access_policy(policy)
    print(f"admin-service endpoint: {policy.endpoint}")
    print(f"admin-service account: {policy.service_account}")
    print(f"engine account: {policy.engine_account}")
    return 0


if __name__ == "__main__":  # pragma: no cover - module execution shim
    raise SystemExit(main())
