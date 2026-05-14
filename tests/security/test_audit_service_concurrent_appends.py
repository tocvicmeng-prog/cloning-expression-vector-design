"""
module_id: tests.security.test_audit_service_concurrent_appends
file: tests/security/test_audit_service_concurrent_appends.py
task_id: T-313b
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from adapter.ipc import AuditServiceClient, InProcessAuditServiceTransport
from adapter.persistence import SqliteAuditLog
from tests.fakes.security.profile_signing.fixtures import admin_principal
from tests.security.audit_service_helpers import (
    AuditServiceFixture,
    audit_entry,
    service_principal,
)


def test_concurrent_engine_and_admin_appends_produce_single_linear_chain(tmp_path: Path) -> None:
    fixture = AuditServiceFixture(tmp_path)
    client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server),
        token_provider=fixture.token_provider,
    )
    callers = [service_principal(), admin_principal()] * 10

    with ThreadPoolExecutor(max_workers=4) as pool:
        entry_ids = list(pool.map(lambda caller: client.append(audit_entry(), caller), callers))

    assert len(set(entry_ids)) == 20
    assert fixture.writer.verify_chain()
    assert len(SqliteAuditLog(fixture.audit_db, fixture.audit_key_provider).replay()) == 20
