"""
module_id: tests.interface.admin_service.test_admin_credentials_routed
file: tests/interface/admin_service/test_admin_credentials_routed.py
task_id: T-1103b
"""

from __future__ import annotations

from domain.types.admin_ipc import AdminIpcStatus, AdminServiceVerb
from tests.interface.admin_service.helpers import NOW, accepted_handler, harness, token


def test_admin_credentials_routed() -> None:
    principals_seen: list[str] = []
    app = harness(handlers={AdminServiceVerb.LIST_PROFILES: accepted_handler(principals_seen)})

    response = app.client.list_profiles(token(), {"scope": "all"}, requested_at_utc=NOW)

    assert response.status is AdminIpcStatus.ACCEPTED
    assert response.decision_record is not None
    assert response.payload["principal_type"] == "AdminPrincipal"
    assert principals_seen == ["AdminPrincipal"]
