"""
module_id: tests.domain.ports.test_audit_key_provider_contract
file: tests/domain/ports/test_audit_key_provider_contract.py
task_id: T-312a
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from domain.ports.audit_key import AuditKeyProvider, KeyVersionId
from domain.security import AdminPrincipal, InstitutionId, PrincipalId, SecurityRole
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def _admin() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def assert_audit_key_provider_contract(
    provider_factory: Callable[[], AuditKeyProvider],
) -> None:
    provider = provider_factory()
    message = b"audit-entry-canonical-bytes"
    version, mac = provider.mac(message)

    assert provider.current_key_version() == version
    assert provider.verify(version, message, mac)
    assert not provider.verify(version, b"other-message", mac)
    assert not provider.verify(KeyVersionId(404), message, mac)
    assert "current_key" not in {
        name
        for name in dir(provider)
        if not name.startswith("_") and callable(getattr(provider, name))
    }

    new_version = provider.rotate("contract rotation", _admin())

    assert new_version != version
    assert provider.current_key_version() == new_version
    assert provider.verify_with_archived(version, message, mac)
    assert not provider.verify(new_version, message, mac)


def test_test_audit_key_provider_satisfies_contract() -> None:
    assert_audit_key_provider_contract(TestAuditKeyProvider)
