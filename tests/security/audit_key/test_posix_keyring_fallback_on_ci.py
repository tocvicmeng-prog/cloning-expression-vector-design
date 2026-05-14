"""
module_id: tests.security.audit_key.test_posix_keyring_fallback_on_ci
file: tests/security/audit_key/test_posix_keyring_fallback_on_ci.py
task_id: T-312b
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.security.audit_key import PosixKeyringAuditKeyProvider
from tests.security.audit_key.helpers import admin_principal, deterministic_key_factory


def test_posix_keyring_backend_falls_back_to_file_keystore_on_ci(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "1")

    with pytest.warns(RuntimeWarning, match="CI environment"):
        provider = PosixKeyringAuditKeyProvider(
            tmp_path / "audit-key.json",
            key_factory=deterministic_key_factory(),
        )

    version, mac = provider.mac(b"entry")
    assert provider.fallback_reason == "CI environment"
    assert provider.verify(version, b"entry", mac)

    new_version = provider.rotate("ci fallback rotation", admin_principal())
    assert provider.current_key_version() == new_version
    assert provider.verify_with_archived(version, b"entry", mac)
