"""
module_id: adapter.security.audit_key.file_keystore
file: src/adapter/security/audit_key/file_keystore.py
task_id: T-312b

File-backed AuditKeyProvider with indefinite escrow archive retention.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import tempfile
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Final, cast

from domain.ports.audit_key import KeyVersionId, MacBytes
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, Principal

AUDIT_KEY_ARCHIVE_VERSION: Final[int] = 1
AUDIT_KEY_BYTES: Final[int] = 32

KeyFactory = Callable[[], bytes]


class AuditKeyArchiveError(ValueError):
    """Raised when an audit-key archive is missing or malformed."""


@dataclass(frozen=True)
class AuditKeyRotation:
    old_key_version: KeyVersionId
    new_key_version: KeyVersionId
    reason: str
    principal_id: str
    rotated_at_utc: datetime


@dataclass(frozen=True)
class _Archive:
    backend: str
    current_version: int
    keys: dict[int, bytes]
    archived_versions: frozenset[int]
    rotation_log: tuple[AuditKeyRotation, ...]


class FileAuditKeyProvider:
    """Audit HMAC keystore backed by an escrow JSON file.

    The archive stores every historical key version indefinitely so old audit
    rows remain verifiable after rotation. The class never returns raw key bytes.
    """

    def __init__(
        self,
        archive_path: str | Path,
        *,
        key_factory: KeyFactory | None = None,
        create_if_missing: bool = True,
        emit_warning: bool = True,
        backend_label: str = "file",
    ) -> None:
        self._archive_path = Path(archive_path)
        self._key_factory = key_factory or _secure_key_factory
        self._backend_label = backend_label
        self._lock = RLock()
        if emit_warning:
            warnings.warn(
                "file audit-key backend stores the escrow archive on disk; "
                "use an OS keystore backend for production deployments",
                RuntimeWarning,
                stacklevel=2,
            )
        with self._lock:
            if self._archive_path.exists():
                self._load_archive()
            elif create_if_missing:
                self._write_archive(
                    _Archive(
                        backend=self._backend_label,
                        current_version=1,
                        keys={1: self._new_key()},
                        archived_versions=frozenset(),
                        rotation_log=(),
                    )
                )
            else:
                raise AuditKeyArchiveError(f"audit-key archive not found: {self._archive_path}")

    @property
    def archive_path(self) -> Path:
        return self._archive_path

    @property
    def rotation_log(self) -> tuple[AuditKeyRotation, ...]:
        with self._lock:
            return self._load_archive().rotation_log

    def mac(self, message: bytes) -> tuple[KeyVersionId, MacBytes]:
        with self._lock:
            archive = self._load_archive()
            key = _current_key(archive)
            return (
                KeyVersionId(archive.current_version),
                MacBytes(hmac.new(key, message, hashlib.sha256).digest()),
            )

    def verify(self, key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool:
        with self._lock:
            archive = self._load_archive()
            key = archive.keys.get(int(key_version))
            if key is None:
                return False
            expected = hmac.new(key, message, hashlib.sha256).digest()
            return hmac.compare_digest(expected, bytes(mac))

    def verify_with_archived(
        self,
        key_version: KeyVersionId,
        message: bytes,
        mac: MacBytes,
    ) -> bool:
        with self._lock:
            archive = self._load_archive()
            version = int(key_version)
            if version != archive.current_version and version not in archive.archived_versions:
                return False
        return self.verify(key_version, message, mac)

    def rotate(
        self,
        reason: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> KeyVersionId:
        clean_reason = reason.strip()
        if not clean_reason:
            raise ValueError("rotation reason cannot be empty")
        _require_rotation_authority(principal)

        with self._lock:
            archive = self._load_archive()
            old_version = archive.current_version
            new_version = max(archive.keys) + 1
            rotation = AuditKeyRotation(
                old_key_version=KeyVersionId(old_version),
                new_key_version=KeyVersionId(new_version),
                reason=clean_reason,
                principal_id=str(principal.id),
                rotated_at_utc=datetime.now(UTC),
            )
            self._write_archive(
                _Archive(
                    backend=archive.backend,
                    current_version=new_version,
                    keys={**archive.keys, new_version: self._new_key()},
                    archived_versions=frozenset((*archive.archived_versions, old_version)),
                    rotation_log=(*archive.rotation_log, rotation),
                )
            )
            return KeyVersionId(new_version)

    def current_key_version(self) -> KeyVersionId:
        with self._lock:
            return KeyVersionId(self._load_archive().current_version)

    def _new_key(self) -> bytes:
        key = self._key_factory()
        if len(key) < AUDIT_KEY_BYTES:
            raise AuditKeyArchiveError("audit keys must be at least 32 bytes")
        return key

    def _load_archive(self) -> _Archive:
        try:
            data = json.loads(self._archive_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise AuditKeyArchiveError(
                f"audit-key archive not found: {self._archive_path}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise AuditKeyArchiveError(f"invalid audit-key archive JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise AuditKeyArchiveError("audit-key archive must be a JSON object")
        return _archive_from_json(data)

    def _write_archive(self, archive: _Archive) -> None:
        self._archive_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            _archive_to_json(archive),
            sort_keys=True,
            indent=2,
        )
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self._archive_path.name}.",
            suffix=".tmp",
            dir=self._archive_path.parent,
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self._archive_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()


def _secure_key_factory() -> bytes:
    return secrets.token_bytes(AUDIT_KEY_BYTES)


def _current_key(archive: _Archive) -> bytes:
    try:
        return archive.keys[archive.current_version]
    except KeyError as exc:
        raise AuditKeyArchiveError("current audit-key version is absent from archive") from exc


def _require_rotation_authority(principal: Principal) -> None:
    if isinstance(principal, AdminPrincipal):
        return
    if isinstance(principal, DeveloperBootstrapPrincipal) and principal.has_bootstrap_authority:
        return
    raise PermissionError("audit-key rotation requires administrator or bootstrap authority")


def _archive_from_json(data: dict[str, object]) -> _Archive:
    archive_version = _expect_int(data.get("archive_version"), "archive_version")
    if archive_version != AUDIT_KEY_ARCHIVE_VERSION:
        raise AuditKeyArchiveError(f"unsupported audit-key archive version: {archive_version}")
    backend = _expect_str(data.get("backend"), "backend")
    current_version = _expect_positive_int(data.get("current_version"), "current_version")
    keys = _parse_keys(data.get("keys"))
    if current_version not in keys:
        raise AuditKeyArchiveError("current audit-key version is absent from keys")
    archived_versions = frozenset(
        _expect_positive_int(item, "archived_versions")
        for item in _expect_list(data.get("archived_versions"), "archived_versions")
    )
    missing_archived = archived_versions.difference(keys)
    if missing_archived:
        raise AuditKeyArchiveError(
            f"archived audit-key versions missing: {sorted(missing_archived)}"
        )
    return _Archive(
        backend=backend,
        current_version=current_version,
        keys=keys,
        archived_versions=archived_versions,
        rotation_log=_parse_rotation_log(data.get("rotation_log")),
    )


def _archive_to_json(archive: _Archive) -> dict[str, object]:
    return {
        "archive_version": AUDIT_KEY_ARCHIVE_VERSION,
        "archived_versions": sorted(archive.archived_versions),
        "backend": archive.backend,
        "current_version": archive.current_version,
        "keys": {
            str(version): base64.b64encode(key).decode("ascii")
            for version, key in sorted(archive.keys.items())
        },
        "rotation_log": [
            {
                "new_key_version": int(rotation.new_key_version),
                "old_key_version": int(rotation.old_key_version),
                "principal_id": rotation.principal_id,
                "reason": rotation.reason,
                "rotated_at_utc": _datetime_to_json(rotation.rotated_at_utc),
            }
            for rotation in archive.rotation_log
        ],
    }


def _parse_keys(raw: object) -> dict[int, bytes]:
    if not isinstance(raw, dict):
        raise AuditKeyArchiveError("keys must be a JSON object")
    parsed: dict[int, bytes] = {}
    for raw_version, raw_key in raw.items():
        version = _parse_version_key(raw_version)
        encoded = _expect_str(raw_key, f"keys.{version}")
        try:
            key = base64.b64decode(encoded.encode("ascii"), validate=True)
        except Exception as exc:
            raise AuditKeyArchiveError(f"invalid base64 key for version {version}") from exc
        if len(key) < AUDIT_KEY_BYTES:
            raise AuditKeyArchiveError(f"audit key version {version} is too short")
        parsed[version] = key
    if not parsed:
        raise AuditKeyArchiveError("keys cannot be empty")
    return parsed


def _parse_version_key(raw: object) -> int:
    if not isinstance(raw, str):
        raise AuditKeyArchiveError("key versions must be strings")
    try:
        version = int(raw)
    except ValueError as exc:
        raise AuditKeyArchiveError(f"invalid key version: {raw}") from exc
    if version < 1:
        raise AuditKeyArchiveError("key versions must be positive")
    return version


def _parse_rotation_log(raw: object) -> tuple[AuditKeyRotation, ...]:
    return tuple(_parse_rotation(item) for item in _expect_list(raw, "rotation_log"))


def _parse_rotation(raw: object) -> AuditKeyRotation:
    if not isinstance(raw, dict):
        raise AuditKeyArchiveError("rotation_log entries must be JSON objects")
    entry = cast(dict[str, object], raw)
    return AuditKeyRotation(
        old_key_version=KeyVersionId(
            _expect_positive_int(entry.get("old_key_version"), "old_key_version")
        ),
        new_key_version=KeyVersionId(
            _expect_positive_int(entry.get("new_key_version"), "new_key_version")
        ),
        reason=_expect_str(entry.get("reason"), "reason"),
        principal_id=_expect_str(entry.get("principal_id"), "principal_id"),
        rotated_at_utc=_parse_datetime(entry.get("rotated_at_utc")),
    )


def _expect_list(raw: object, field_name: str) -> list[object]:
    if not isinstance(raw, list):
        raise AuditKeyArchiveError(f"{field_name} must be a list")
    return raw


def _expect_str(raw: object, field_name: str) -> str:
    if not isinstance(raw, str):
        raise AuditKeyArchiveError(f"{field_name} must be a string")
    if not raw:
        raise AuditKeyArchiveError(f"{field_name} cannot be empty")
    return raw


def _expect_int(raw: object, field_name: str) -> int:
    if not isinstance(raw, int):
        raise AuditKeyArchiveError(f"{field_name} must be an integer")
    return raw


def _expect_positive_int(raw: object, field_name: str) -> int:
    value = _expect_int(raw, field_name)
    if value < 1:
        raise AuditKeyArchiveError(f"{field_name} must be positive")
    return value


def _datetime_to_json(value: datetime) -> str:
    if value.tzinfo is None:
        raise AuditKeyArchiveError("rotation timestamp must be timezone-aware")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(raw: object) -> datetime:
    text = _expect_str(raw, "rotated_at_utc")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise AuditKeyArchiveError("rotated_at_utc must be timezone-aware")
    return parsed.astimezone(UTC)


def archive_contains_raw_key_accessor(provider: object) -> bool:
    """Return True if a provider exposes a known raw-key accessor name."""

    raw_accessors: set[str] = {"current_key", "current_key_bytes", "export_key", "get_key"}
    return any(hasattr(provider, name) for name in raw_accessors)
