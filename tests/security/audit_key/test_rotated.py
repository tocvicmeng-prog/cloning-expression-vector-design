"""
module_id: tests.security.audit_key.test_rotated
file: tests/security/audit_key/test_rotated.py
task_id: T-312b
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.audit_key import FileAuditKeyProvider
from domain.ports.audit_key import AuditKeyProvider, KeyVersionId
from tests.domain.ports.test_audit_key_provider_contract import assert_audit_key_provider_contract
from tests.security.audit_key.helpers import (
    admin_principal,
    bootstrap_principal,
    deterministic_key_factory,
)


def test_file_provider_satisfies_audit_key_contract(tmp_path: Path) -> None:
    assert_audit_key_provider_contract(
        lambda: FileAuditKeyProvider(
            tmp_path / "contract-audit-key.json",
            key_factory=deterministic_key_factory(),
            emit_warning=False,
        )
    )


def test_rotation_changes_current_version_and_retains_archive(tmp_path: Path) -> None:
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    old_version, old_mac = provider.mac(b"row-1")

    new_version = provider.rotate("scheduled rotation", admin_principal())

    assert isinstance(provider, AuditKeyProvider)
    assert old_version == KeyVersionId(1)
    assert new_version == KeyVersionId(2)
    assert provider.current_key_version() == KeyVersionId(2)
    assert provider.verify_with_archived(old_version, b"row-1", old_mac)
    assert not provider.verify(new_version, b"row-1", old_mac)
    assert provider.rotation_log[0].reason == "scheduled rotation"
    assert provider.rotation_log[0].principal_id == "admin-1"


def test_bootstrap_principal_can_rotate_file_provider(tmp_path: Path) -> None:
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )

    assert provider.rotate("bootstrap rotation", bootstrap_principal()) == KeyVersionId(2)
