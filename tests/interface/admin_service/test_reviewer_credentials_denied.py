"""
module_id: tests.interface.admin_service.test_reviewer_credentials_denied
file: tests/interface/admin_service/test_reviewer_credentials_denied.py
task_id: T-1103b
"""

from __future__ import annotations

from domain.types.admin_ipc import AdminIpcErrorCode, AdminIpcStatus
from tests.interface.admin_service.helpers import NOW, harness, token


def test_reviewer_credentials_denied() -> None:
    app = harness()
    response = app.client.list_profiles(token("reviewer"), {}, requested_at_utc=NOW)

    assert response.status is AdminIpcStatus.DENIED
    assert response.error_code is AdminIpcErrorCode.PERMISSION_DENIED
    assert app.security_log.events[-1].operation == "list_profiles"
