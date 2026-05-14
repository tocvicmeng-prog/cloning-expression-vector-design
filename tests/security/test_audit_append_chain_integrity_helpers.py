"""
module_id: tests.security.test_audit_append_chain_integrity_helpers
file: tests/security/test_audit_append_chain_integrity_helpers.py
task_id: T-313a
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from domain.ports.audit_append import AuditEntry
from domain.ports.audit_key import AuditKeyProvider
from domain.security import AdminPrincipal, InstitutionId, PrincipalId, SecurityRole
from tests.fakes.security.audit_append.brokers import (
    AuditChainRow,
    FakeAdminAuditBroker,
    FakeAuditBroker,
    FakeAuditChainStore,
    service_principal,
)
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def assert_linear_hmac_chain(
    rows: tuple[AuditChainRow, ...],
    key_provider: AuditKeyProvider,
) -> None:
    previous_mac_hex = ""
    for expected_sequence, row in enumerate(rows, start=1):
        assert row.sequence == expected_sequence
        assert row.previous_mac_hex == previous_mac_hex
        assert key_provider.verify_with_archived(row.key_version, row.message, row.mac)
        previous_mac_hex = row.mac_hex


def _entry(entry_type: str) -> AuditEntry:
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


def test_chain_integrity_helper_detects_tampered_message() -> None:
    key_provider = TestAuditKeyProvider()
    store = FakeAuditChainStore()
    engine = FakeAuditBroker(key_provider, store)
    admin = FakeAdminAuditBroker(key_provider, store)
    engine.append(_entry("engine"), service_principal())
    admin.append(_entry("admin"), _admin())

    assert_linear_hmac_chain(store.rows, key_provider)

    tampered = (replace(store.rows[0], message=b"tampered"), store.rows[1])
    with pytest.raises(AssertionError):
        assert_linear_hmac_chain(tampered, key_provider)


def test_chain_integrity_helper_detects_broken_link() -> None:
    key_provider = TestAuditKeyProvider()
    store = FakeAuditChainStore()
    engine = FakeAuditBroker(key_provider, store)
    admin = FakeAdminAuditBroker(key_provider, store)
    engine.append(_entry("engine"), service_principal())
    admin.append(_entry("admin"), _admin())

    broken = (store.rows[0], replace(store.rows[1], previous_mac_hex="bad"))
    with pytest.raises(AssertionError):
        assert_linear_hmac_chain(broken, key_provider)
