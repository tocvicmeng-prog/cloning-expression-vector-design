"""
module_id: tests.security.test_audit_service_key_rotation_during_appends
file: tests/security/test_audit_service_key_rotation_during_appends.py
task_id: T-313b
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from adapter.ipc import AuditServiceClient, InProcessAuditServiceTransport
from tests.fakes.security.profile_signing.fixtures import admin_principal
from tests.security.audit_service_helpers import (
    AuditServiceFixture,
    audit_entry,
    service_principal,
)


def test_audit_key_rotation_between_appends_preserves_clean_chain(tmp_path: Path) -> None:
    fixture = AuditServiceFixture(tmp_path)
    client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server),
        token_provider=fixture.token_provider,
    )

    client.append(audit_entry("before-rotation"), service_principal())
    fixture.audit_key_provider.rotate("scheduled audit-service rotation", admin_principal())
    client.append(audit_entry("after-rotation"), service_principal())

    with sqlite3.connect(fixture.audit_db) as connection:
        versions = [
            int(row[0])
            for row in connection.execute(
                "SELECT key_version FROM audit_entries ORDER BY sequence_number"
            )
        ]
    assert versions == [1, 2]
    assert fixture.writer.verify_chain()
