"""
module_id: tests.security.audit_key.test_wrong
file: tests/security/audit_key/test_wrong.py
task_id: T-312b
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.audit_key import FileAuditKeyProvider
from domain.ports.audit_key import KeyVersionId, MacBytes
from tests.security.audit_key.helpers import deterministic_key_factory


def test_wrong_key_version_and_wrong_mac_fail_verification(tmp_path: Path) -> None:
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    version, mac = provider.mac(b"entry")

    assert not provider.verify(KeyVersionId(404), b"entry", mac)
    assert not provider.verify(version, b"entry", MacBytes(b"0" * 32))
    assert not provider.verify_with_archived(version, b"tampered", mac)
