"""
module_id: adapter.security.audit_key.os_keystore_posix
file: src/adapter/security/audit_key/os_keystore_posix.py
task_id: T-312b

POSIX audit-key adapter facade with explicit file-keystore fallback.
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

from adapter.security.audit_key.file_keystore import FileAuditKeyProvider, KeyFactory
from domain.ports.audit_key import KeyVersionId, MacBytes
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal


class PosixKeyringAuditKeyProvider:
    """POSIX keyring facade that falls back to file escrow when unavailable."""

    def __init__(
        self,
        archive_path: str | Path,
        *,
        key_factory: KeyFactory | None = None,
        emit_warning: bool = True,
        force_fallback: bool | None = None,
    ) -> None:
        self.fallback_reason = _fallback_reason(force_fallback)
        if self.fallback_reason is not None and emit_warning:
            warnings.warn(
                f"posix_keyring audit-key backend unavailable ({self.fallback_reason}); "
                "using explicit file-keystore fallback",
                RuntimeWarning,
                stacklevel=2,
            )
        self._delegate = FileAuditKeyProvider(
            archive_path,
            key_factory=key_factory,
            emit_warning=False,
            backend_label="posix_keyring_file_fallback",
        )

    def mac(self, message: bytes) -> tuple[KeyVersionId, MacBytes]:
        return self._delegate.mac(message)

    def verify(self, key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool:
        return self._delegate.verify(key_version, message, mac)

    def verify_with_archived(
        self,
        key_version: KeyVersionId,
        message: bytes,
        mac: MacBytes,
    ) -> bool:
        return self._delegate.verify_with_archived(key_version, message, mac)

    def rotate(
        self,
        reason: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> KeyVersionId:
        return self._delegate.rotate(reason, principal)

    def current_key_version(self) -> KeyVersionId:
        return self._delegate.current_key_version()


def _fallback_reason(force_fallback: bool | None) -> str | None:
    if force_fallback is True:
        return "forced fallback requested"
    if os.environ.get("CI"):
        return "CI environment"
    if sys.platform.startswith(("linux", "darwin", "freebsd", "openbsd", "netbsd")):
        return "system keyring binding is not available in this runtime"
    return f"platform is {sys.platform}"
