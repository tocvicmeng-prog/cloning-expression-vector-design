"""
module_id: tests.security.test_audit_service_ipc_timeout
file: tests/security/test_audit_service_ipc_timeout.py
task_id: T-313b
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.ipc import (
    AuditServiceClient,
    AuditServiceUnreachableError,
    InProcessAuditServiceTransport,
)
from tests.security.audit_service_helpers import (
    AuditServiceFixture,
    audit_entry,
    service_principal,
)


def test_audit_service_client_retries_timeout_then_succeeds(tmp_path: Path) -> None:
    fixture = AuditServiceFixture(tmp_path)
    client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server, fail_first_attempts=2),
        token_provider=fixture.token_provider,
        retries=3,
    )

    assert str(client.append(audit_entry(), service_principal())) == "audit-000001"


def test_audit_service_client_raises_after_retry_budget(tmp_path: Path) -> None:
    fixture = AuditServiceFixture(tmp_path)
    client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server, fail_first_attempts=4),
        token_provider=fixture.token_provider,
        retries=3,
    )

    with pytest.raises(AuditServiceUnreachableError, match="timed out"):
        client.append(audit_entry(), service_principal())
