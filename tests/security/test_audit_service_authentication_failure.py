"""
module_id: tests.security.test_audit_service_authentication_failure
file: tests/security/test_audit_service_authentication_failure.py
task_id: T-313b
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.ipc import AuditServiceClient, InProcessAuditServiceTransport
from tests.security.audit_service_helpers import (
    AuditServiceFixture,
    audit_entry,
    bad_token_provider,
    service_principal,
)


def test_authentication_failure_writes_governance_event_without_audit_row(
    tmp_path: Path,
) -> None:
    fixture = AuditServiceFixture(tmp_path)
    client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server),
        token_provider=bad_token_provider,
    )

    with pytest.raises(PermissionError, match="token"):
        client.append(audit_entry(), service_principal())

    assert fixture.writer.last_row() is None
    events = fixture.governance_writer.read_events()
    assert len(events) == 1
    assert events[0].principal_id == "service:AuthorisationDecisionService"
