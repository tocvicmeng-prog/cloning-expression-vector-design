"""
module_id: interface.audit_service.__main__
file: src/interface/audit_service/__main__.py
task_id: T-313b

Audit-service process entry point placeholder.
"""

from __future__ import annotations

from interface.audit_service.server import audit_service_endpoint_for_platform


def main() -> int:
    print(f"audit-service endpoint: {audit_service_endpoint_for_platform()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
