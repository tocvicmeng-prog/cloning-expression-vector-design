"""
module_id: tests.security.audit_key.test_backend_selection
file: tests/security/audit_key/test_backend_selection.py
task_id: T-312b
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from adapter.security.audit_key import (
    AuditKeyBackendName,
    AuditKeyProviderConfig,
    FileAuditKeyProvider,
    PosixKeyringAuditKeyProvider,
    WindowsDpapiAuditKeyProvider,
    build_audit_key_provider,
)


def test_backend_selection_builds_file_provider_with_warning(tmp_path: Path) -> None:
    with pytest.warns(RuntimeWarning, match="file audit-key backend"):
        provider = build_audit_key_provider(
            AuditKeyProviderConfig(tmp_path / "audit-key.json", audit_key_backend="file")
        )

    assert isinstance(provider, FileAuditKeyProvider)


def test_backend_selection_builds_explicit_os_fallbacks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "1")

    with pytest.warns(RuntimeWarning, match="windows_dpapi"):
        windows = build_audit_key_provider(
            AuditKeyProviderConfig(tmp_path / "windows.json", audit_key_backend="windows_dpapi")
        )
    with pytest.warns(RuntimeWarning, match="posix_keyring"):
        posix = build_audit_key_provider(
            AuditKeyProviderConfig(tmp_path / "posix.json", audit_key_backend="posix_keyring")
        )

    assert isinstance(windows, WindowsDpapiAuditKeyProvider)
    assert isinstance(posix, PosixKeyringAuditKeyProvider)


def test_backend_selection_rejects_unknown_backend(tmp_path: Path) -> None:
    config = AuditKeyProviderConfig(
        tmp_path / "audit-key.json",
        audit_key_backend=cast(AuditKeyBackendName, "unknown"),
    )

    with pytest.raises(ValueError, match="unsupported"):
        build_audit_key_provider(config)
