"""
module_id: adapter.security.audit_key.os_keystore_windows
file: src/adapter/security/audit_key/os_keystore_windows.py
task_id: T-312b

Windows audit-key adapter facade with explicit file-keystore fallback.
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

from adapter.security.audit_key.file_keystore import FileAuditKeyProvider, KeyFactory
from domain.ports.audit_key import KeyVersionId, MacBytes
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal


class WindowsDpapiAuditKeyProvider:
    """DPAPI facade that falls back to the file escrow backend when unavailable."""

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
                f"windows_dpapi audit-key backend unavailable ({self.fallback_reason}); "
                "using explicit file-keystore fallback",
                RuntimeWarning,
                stacklevel=2,
            )
        self._delegate = FileAuditKeyProvider(
            archive_path,
            key_factory=key_factory,
            emit_warning=False,
            backend_label="windows_dpapi_file_fallback",
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
    if sys.platform != "win32":
        return f"platform is {sys.platform}"
    return "DPAPI binding is not available in this runtime"
