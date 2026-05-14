"""
module_id: tests.domain.ports.test_audit_append_contract
file: tests/domain/ports/test_audit_append_contract.py
task_id: T-313a
"""

from __future__ import annotations

from datetime import UTC, datetime

from domain.ports.audit_append import AdminAuditAppendPort, AuditAppendPort, AuditEntry
from domain.security import AdminPrincipal, InstitutionId, PrincipalId, SecurityRole
from tests.fakes.security.audit_append.brokers import (
    FakeAdminAuditBroker,
    FakeAuditBroker,
    FakeAuditChainStore,
    service_principal,
)
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.security.test_audit_append_chain_integrity_helpers import assert_linear_hmac_chain

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def _entry() -> AuditEntry:
    return AuditEntry(
        entry_type="contract",
        payload={"payload_hash": "sha256:payload"},
        occurred_at_utc=NOW,
    )


def _admin() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def test_fake_brokers_satisfy_append_contracts() -> None:
    key_provider = TestAuditKeyProvider()
    store = FakeAuditChainStore()
    engine: AuditAppendPort = FakeAuditBroker(key_provider, store)
    admin: AdminAuditAppendPort = FakeAdminAuditBroker(key_provider, store)

    first_id = engine.append(_entry(), service_principal())
    second_id = admin.append(_entry(), _admin())

    assert first_id == "audit-000001"
    assert second_id == "audit-000002"
    assert_linear_hmac_chain(store.rows, key_provider)
