"""
module_id: adapter.security.audit_key
file: src/adapter/security/audit_key/__init__.py
task_id: T-312b

Audit-key provider adapters and backend selection.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from adapter.security.audit_key.file_keystore import (
    AuditKeyArchiveError,
    AuditKeyRotation,
    FileAuditKeyProvider,
    archive_contains_raw_key_accessor,
)
from adapter.security.audit_key.os_keystore_posix import PosixKeyringAuditKeyProvider
from adapter.security.audit_key.os_keystore_windows import WindowsDpapiAuditKeyProvider
from domain.ports.audit_key import AuditKeyProvider

AuditKeyBackendName = Literal["file", "windows_dpapi", "posix_keyring"]


@dataclass(frozen=True)
class AuditKeyProviderConfig:
    archive_path: Path
    audit_key_backend: AuditKeyBackendName | None = None
    production: bool = False


def build_audit_key_provider(config: AuditKeyProviderConfig) -> AuditKeyProvider:
    backend = config.audit_key_backend or _default_backend(config.production)
    if backend == "file":
        return FileAuditKeyProvider(config.archive_path)
    if backend == "windows_dpapi":
        return WindowsDpapiAuditKeyProvider(config.archive_path)
    if backend == "posix_keyring":
        return PosixKeyringAuditKeyProvider(config.archive_path)
    raise ValueError(f"unsupported audit-key backend: {backend}")


def _default_backend(production: bool) -> AuditKeyBackendName:
    if not production:
        return "file"
    if os.name == "nt":
        return "windows_dpapi"
    return "posix_keyring"


__all__ = [
    "AuditKeyArchiveError",
    "AuditKeyBackendName",
    "AuditKeyProviderConfig",
    "AuditKeyRotation",
    "FileAuditKeyProvider",
    "PosixKeyringAuditKeyProvider",
    "WindowsDpapiAuditKeyProvider",
    "archive_contains_raw_key_accessor",
    "build_audit_key_provider",
]
