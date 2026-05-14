"""
module_id: tests.security.test_audit_service_crash_recovery
file: tests/security/test_audit_service_crash_recovery.py
task_id: T-313b
"""

from __future__ import annotations

from pathlib import Path

from adapter.ipc import AuditServiceClient, InProcessAuditServiceTransport
from adapter.persistence import SqliteAuditLogWriter
from interface.audit_service.handlers import AuditServiceHandlers
from interface.audit_service.server import AuditServiceServer
from tests.security.audit_service_helpers import (
    AuditServiceFixture,
    audit_entry,
    service_principal,
)


def test_audit_service_restart_verifies_existing_chain_before_new_append(tmp_path: Path) -> None:
    fixture = AuditServiceFixture(tmp_path)
    first_client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server),
        token_provider=fixture.token_provider,
    )
    first_client.append(audit_entry("before-crash"), service_principal())

    restarted_writer = SqliteAuditLogWriter(fixture.audit_db, fixture.audit_key_provider)
    restarted_server = AuditServiceServer(
        AuditServiceHandlers(
            writer=restarted_writer,
            verifier=fixture.verifier,
            governance_writer=fixture.governance_writer,
        )
    )
    restarted_client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(restarted_server),
        token_provider=fixture.token_provider,
    )
    restarted_client.append(audit_entry("after-crash"), service_principal())

    assert restarted_writer.verify_chain()
    last_row = restarted_writer.last_row()
    assert last_row is not None
    assert last_row.sequence_number == 2
