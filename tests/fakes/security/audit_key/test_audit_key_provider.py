"""
module_id: tests.fakes.security.audit_key.test_audit_key_provider
file: tests/fakes/security/audit_key/test_audit_key_provider.py
task_id: T-312a
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from domain.ports.audit_key import AuditKeyProvider, KeyVersionId, MacBytes
from domain.security import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    InstitutionId,
    PrincipalId,
    SecurityRole,
)
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider

NOW = datetime(2026, 5, 14, tzinfo=UTC)


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


def test_fake_provider_conforms_to_protocol_and_returns_typed_values() -> None:
    provider = TestAuditKeyProvider()
    key_version, mac = provider.mac(b"entry")

    assert isinstance(provider, AuditKeyProvider)
    assert key_version == KeyVersionId(1)
    assert isinstance(mac, bytes)
    assert provider.verify(key_version, b"entry", mac)


def test_fake_provider_is_deterministic_without_exposing_raw_key() -> None:
    left = TestAuditKeyProvider()
    right = TestAuditKeyProvider()

    assert left.mac(b"entry") == right.mac(b"entry")
    assert "current_key" not in {
        name for name in dir(left) if not name.startswith("_") and callable(getattr(left, name))
    }


def test_rotation_changes_current_version_and_keeps_archived_verification() -> None:
    provider = TestAuditKeyProvider()
    old_version, old_mac = provider.mac(b"entry")

    new_version = provider.rotate("scheduled test rotation", _admin())

    assert new_version == KeyVersionId(2)
    assert provider.current_key_version() == KeyVersionId(2)
    assert provider.verify_with_archived(old_version, b"entry", old_mac)
    assert provider.verify(new_version, b"entry", old_mac) is False
    assert provider.rotation_log[0].principal_id == "admin-1"


def test_bootstrap_developer_can_rotate_but_empty_reason_is_rejected() -> None:
    provider = TestAuditKeyProvider()

    assert provider.rotate("bootstrap rotation", _bootstrap_developer()) == KeyVersionId(2)

    with pytest.raises(ValueError, match="reason"):
        provider.rotate("", _admin())


def test_tampered_message_mac_and_unknown_version_fail_verification() -> None:
    provider = TestAuditKeyProvider()
    version, mac = provider.mac(b"entry")

    assert not provider.verify(version, b"tampered", mac)
    assert not provider.verify_with_archived(version, b"tampered", mac)
    assert not provider.verify(version, b"entry", MacBytes(bytes(mac)[:-1] + b"0"))
    assert not provider.verify(KeyVersionId(999), b"entry", mac)
