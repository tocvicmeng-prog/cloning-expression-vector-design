"""
module_id: tests.security.test_audit_service_endpoints
file: tests/security/test_audit_service_endpoints.py
task_id: T-313b
"""

from __future__ import annotations

import os

from interface.audit_service import audit_service_endpoint_for_platform


def test_endpoint_shape_matches_current_platform() -> None:
    endpoint = audit_service_endpoint_for_platform("cev-audit-service")
    if os.name == "nt":
        assert endpoint == r"\\.\pipe\cev-audit-service"
    else:
        assert endpoint == "/var/run/cev-audit/socket"
