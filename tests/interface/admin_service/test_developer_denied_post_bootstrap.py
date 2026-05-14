"""
module_id: tests.interface.admin_service.test_developer_denied_post_bootstrap
file: tests/interface/admin_service/test_developer_denied_post_bootstrap.py
task_id: T-1103b
"""

from __future__ import annotations

from domain.types.admin_ipc import AdminIpcErrorCode, AdminIpcStatus
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.interface.admin_service.helpers import NOW, harness, token


def test_developer_denied_post_bootstrap() -> None:
    app = harness(audit_key_provider=TestAuditKeyProvider())

    response = app.client.rotate_audit_key(
        token("developer"),
        {"reason": "ordinary developer cannot rotate"},
        requested_at_utc=NOW,
    )

    assert response.status is AdminIpcStatus.DENIED
    assert response.error_code is AdminIpcErrorCode.PERMISSION_DENIED
    assert "bootstrap authority" in (response.error_message or "")
