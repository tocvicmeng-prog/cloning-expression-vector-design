"""
module_id: tests.interface.admin_service.test_unauthenticated_denied
file: tests/interface/admin_service/test_unauthenticated_denied.py
task_id: T-1103b
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from domain.types.admin_ipc import AdminIpcErrorCode, AdminIpcStatus
from tests.interface.admin_service.helpers import NOW, harness, token


def test_unauthenticated_denied() -> None:
    issued_at = datetime(2026, 1, 1, tzinfo=UTC)
    response = harness().client.list_profiles(
        token(
            issued_at=issued_at,
            expires_at=issued_at + timedelta(days=1),
        ),
        {},
        requested_at_utc=NOW,
    )

    assert response.status is AdminIpcStatus.ERROR
    assert response.error_code is AdminIpcErrorCode.AUTHENTICATION_FAILED


def test_unauthenticated_denial_records_security_event() -> None:
    app = harness()
    issued_at = datetime(2026, 1, 1, tzinfo=UTC)
    app.client.list_profiles(
        token(issued_at=issued_at, expires_at=issued_at + timedelta(days=1)),
        {},
        requested_at_utc=NOW,
    )

    assert app.security_log.events[-1].event_type == "authentication_failed"
