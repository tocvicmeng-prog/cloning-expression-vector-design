"""
module_id: tests.interface.admin_service.test_developer_bootstrap_pre_bootstrap
file: tests/interface/admin_service/test_developer_bootstrap_pre_bootstrap.py
task_id: T-1103b
"""

from __future__ import annotations

from domain.types.admin_ipc import AdminIpcStatus
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.interface.admin_service.helpers import NOW, harness, token


def test_developer_bootstrap_pre_bootstrap() -> None:
    audit_key_provider = TestAuditKeyProvider()
    app = harness(audit_key_provider=audit_key_provider)

    response = app.client.rotate_audit_key(
        token("developer_bootstrap"),
        {"reason": "bootstrap key rotation"},
        requested_at_utc=NOW,
    )

    assert response.status is AdminIpcStatus.ACCEPTED
    assert response.payload["key_version"] == 2
    assert audit_key_provider.rotation_log[-1].principal_id == "principal-developer-bootstrap"
