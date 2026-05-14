"""
module_id: tests.fakes.security.audit_append.test_fake_brokers
file: tests/fakes/security/audit_append/test_fake_brokers.py
task_id: T-313a
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import cast

import pytest

from domain.ports.audit_append import AdminAuditAppendPort, AuditAppendPort, AuditEntry
from domain.security import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    InstitutionId,
    PrincipalId,
    SecurityRole,
)
from tests.fakes.security.audit_append.brokers import (
    FakeAdminAuditBroker,
    FakeAuditBroker,
    FakeAuditChainStore,
    service_principal,
)
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.security.test_audit_append_chain_integrity_helpers import assert_linear_hmac_chain

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def _entry(entry_type: str = "decision") -> AuditEntry:
    return AuditEntry(
        entry_type=entry_type,
        payload={"decision_id": "decision-1"},
        occurred_at_utc=NOW,
    )


def _admin() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def _bootstrap_developer() -> DeveloperBootstrapPrincipal:
    return DeveloperBootstrapPrincipal(
        id=PrincipalId("dev-1"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
        is_bootstrap=True,
        bootstrap_expires_at=datetime.now(UTC) + timedelta(days=1),
    )


def test_fake_brokers_share_one_linear_chain() -> None:
    key_provider = TestAuditKeyProvider()
    store = FakeAuditChainStore()
    engine = FakeAuditBroker(key_provider, store)
    admin = FakeAdminAuditBroker(key_provider, store)

    assert isinstance(engine, AuditAppendPort)
    assert isinstance(admin, AdminAuditAppendPort)
    assert engine.append(_entry("engine"), service_principal()) == "audit-000001"
    assert admin.append(_entry("admin"), _admin()) == "audit-000002"

    assert [row.previous_mac_hex for row in store.rows] == ["", store.rows[0].mac_hex]
    assert_linear_hmac_chain(store.rows, key_provider)


def test_chain_survives_key_rotation_between_appends() -> None:
    key_provider = TestAuditKeyProvider()
    store = FakeAuditChainStore()
    engine = FakeAuditBroker(key_provider, store)
    admin = FakeAdminAuditBroker(key_provider, store)

    engine.append(_entry("engine"), service_principal())
    key_provider.rotate("scheduled rotation", _admin())
    admin.append(_entry("admin"), _admin())

    assert store.rows[0].key_version != store.rows[1].key_version
    assert_linear_hmac_chain(store.rows, key_provider)


def test_separation_of_duties_rejects_wrong_callers() -> None:
    key_provider = TestAuditKeyProvider()
    engine = FakeAuditBroker(key_provider)
    admin = FakeAdminAuditBroker(key_provider)

    with pytest.raises(TypeError, match="ServicePrincipal"):
        engine.append(_entry(), cast(object, _admin()))  # type: ignore[arg-type]
    with pytest.raises(PermissionError, match="administrator"):
        admin.append(_entry(), cast(object, service_principal()))  # type: ignore[arg-type]


def test_bootstrap_developer_can_use_admin_append_fake() -> None:
    key_provider = TestAuditKeyProvider()
    admin = FakeAdminAuditBroker(key_provider)

    assert admin.append(_entry(), _bootstrap_developer()) == "audit-000001"
