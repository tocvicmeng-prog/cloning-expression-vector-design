"""
module_id: adapter.security.signing_key_archive
file: src/adapter/security/signing_key_archive.py
task_id: T-316c

Shared Ed25519 signing-key archive for production security adapters.
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Final, Literal, cast

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from domain.security.identifiers import KeyVersionId

ArchivePurpose = Literal["profile", "decision_record", "sop_template"]
ARCHIVE_VERSION: Final[int] = 1


class SigningKeyArchiveError(ValueError):
    """Raised when a signing-key archive is missing or malformed."""


@dataclass(frozen=True)
class SigningKeyRecord:
    key_version: KeyVersionId
    public_key_bytes: bytes
    private_key_bytes: bytes | None
    principal_id: str | None
    created_at_utc: datetime
    revoked_at_utc: datetime | None = None
    revocation_reason: str | None = None

    @property
    def revoked(self) -> bool:
        return self.revoked_at_utc is not None

    def private_key(self) -> Ed25519PrivateKey:
        if self.private_key_bytes is None:
            raise SigningKeyArchiveError(f"private key not available: {self.key_version}")
        return Ed25519PrivateKey.from_private_bytes(self.private_key_bytes)

    def public_key(self) -> Ed25519PublicKey:
        return Ed25519PublicKey.from_public_bytes(self.public_key_bytes)


@dataclass(frozen=True)
class SigningKeyArchive:
    purpose: ArchivePurpose
    current_key_version: KeyVersionId | None
    current_principal_versions: dict[str, KeyVersionId]
    keys: dict[str, SigningKeyRecord]


class SigningKeyArchiveStore:
    def __init__(
        self,
        path: str | Path,
        *,
        purpose: ArchivePurpose,
        create_if_missing: bool = True,
    ) -> None:
        self._path = Path(path)
        self._purpose = purpose
        self._lock = RLock()
        with self._lock:
            if self._path.exists():
                self.load()
            elif create_if_missing:
                self._write(
                    SigningKeyArchive(
                        purpose=purpose,
                        current_key_version=None,
                        current_principal_versions={},
                        keys={},
                    )
                )
            else:
                raise SigningKeyArchiveError(f"signing-key archive not found: {self._path}")

    @property
    def path(self) -> Path:
        return self._path

    def ensure_institutional_key(self) -> KeyVersionId:
        with self._lock:
            archive = self.load()
            if archive.current_key_version is not None:
                return archive.current_key_version
            key_version = KeyVersionId(f"{archive.purpose}-ed25519-v1")
            record = _new_record(key_version=key_version, principal_id=None)
            self._write(
                SigningKeyArchive(
                    purpose=archive.purpose,
                    current_key_version=key_version,
                    current_principal_versions=archive.current_principal_versions,
                    keys={**archive.keys, str(key_version): record},
                )
            )
            return key_version

    def rotate_institutional_key(self) -> KeyVersionId:
        with self._lock:
            archive = self.load()
            key_version = KeyVersionId(
                f"{archive.purpose}-ed25519-v{_next_global_version(archive)}"
            )
            record = _new_record(key_version=key_version, principal_id=None)
            self._write(
                SigningKeyArchive(
                    purpose=archive.purpose,
                    current_key_version=key_version,
                    current_principal_versions=archive.current_principal_versions,
                    keys={**archive.keys, str(key_version): record},
                )
            )
            return key_version

    def ensure_principal_key(self, principal_id: str) -> KeyVersionId:
        with self._lock:
            archive = self.load()
            existing = archive.current_principal_versions.get(principal_id)
            if existing is not None:
                return existing
            key_version = KeyVersionId(f"decision-record-{principal_id}-v1")
            record = _new_record(key_version=key_version, principal_id=principal_id)
            self._write(
                SigningKeyArchive(
                    purpose=archive.purpose,
                    current_key_version=archive.current_key_version,
                    current_principal_versions={
                        **archive.current_principal_versions,
                        principal_id: key_version,
                    },
                    keys={**archive.keys, str(key_version): record},
                )
            )
            return key_version

    def rotate_principal_key(self, principal_id: str) -> KeyVersionId:
        with self._lock:
            archive = self.load()
            key_version = KeyVersionId(
                f"decision-record-{principal_id}-v{_next_principal_version(archive, principal_id)}"
            )
            record = _new_record(key_version=key_version, principal_id=principal_id)
            self._write(
                SigningKeyArchive(
                    purpose=archive.purpose,
                    current_key_version=archive.current_key_version,
                    current_principal_versions={
                        **archive.current_principal_versions,
                        principal_id: key_version,
                    },
                    keys={**archive.keys, str(key_version): record},
                )
            )
            return key_version

    def revoke_key(self, key_version: KeyVersionId, reason: str) -> None:
        clean_reason = reason.strip()
        if not clean_reason:
            raise ValueError("revocation reason cannot be empty")
        with self._lock:
            archive = self.load()
            record = self.record(key_version)
            updated = SigningKeyRecord(
                key_version=record.key_version,
                public_key_bytes=record.public_key_bytes,
                private_key_bytes=record.private_key_bytes,
                principal_id=record.principal_id,
                created_at_utc=record.created_at_utc,
                revoked_at_utc=datetime.now(UTC),
                revocation_reason=clean_reason,
            )
            self._write(
                SigningKeyArchive(
                    purpose=archive.purpose,
                    current_key_version=archive.current_key_version,
                    current_principal_versions=archive.current_principal_versions,
                    keys={**archive.keys, str(key_version): updated},
                )
            )

    def current_institutional_record(self) -> SigningKeyRecord:
        key_version = self.ensure_institutional_key()
        return self.record(key_version)

    def current_principal_record(self, principal_id: str) -> SigningKeyRecord:
        archive = self.load()
        key_version = archive.current_principal_versions.get(principal_id)
        if key_version is None:
            raise SigningKeyArchiveError(f"no decision-record key provisioned for {principal_id}")
        return self.record(key_version)

    def record(self, key_version: KeyVersionId) -> SigningKeyRecord:
        archive = self.load()
        try:
            return archive.keys[str(key_version)]
        except KeyError as exc:
            raise SigningKeyArchiveError(f"unknown signing key version: {key_version}") from exc

    def load(self) -> SigningKeyArchive:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise SigningKeyArchiveError(f"signing-key archive not found: {self._path}") from exc
        except json.JSONDecodeError as exc:
            raise SigningKeyArchiveError(f"invalid signing-key archive JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise SigningKeyArchiveError("signing-key archive must be a JSON object")
        archive = _archive_from_json(dict(data))
        if archive.purpose != self._purpose:
            raise SigningKeyArchiveError(
                f"archive purpose {archive.purpose!r} does not match {self._purpose!r}"
            )
        return archive

    def _write(self, archive: SigningKeyArchive) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(_archive_to_json(archive), sort_keys=True, indent=2)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self._path.name}.",
            suffix=".tmp",
            dir=self._path.parent,
            text=True,
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self._path)
        finally:
            if temp_path.exists():
                temp_path.unlink()


def _new_record(key_version: KeyVersionId, principal_id: str | None) -> SigningKeyRecord:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return SigningKeyRecord(
        key_version=key_version,
        public_key_bytes=public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        ),
        private_key_bytes=private_key.private_bytes(
            encoding=Encoding.Raw,
            format=PrivateFormat.Raw,
            encryption_algorithm=NoEncryption(),
        ),
        principal_id=principal_id,
        created_at_utc=datetime.now(UTC),
    )


def _next_global_version(archive: SigningKeyArchive) -> int:
    prefix = f"{archive.purpose}-ed25519-v"
    versions = [
        int(version.removeprefix(prefix))
        for version in archive.keys
        if version.startswith(prefix) and version.removeprefix(prefix).isdigit()
    ]
    return max(versions, default=0) + 1


def _next_principal_version(archive: SigningKeyArchive, principal_id: str) -> int:
    prefix = f"decision-record-{principal_id}-v"
    versions = [
        int(version.removeprefix(prefix))
        for version in archive.keys
        if version.startswith(prefix) and version.removeprefix(prefix).isdigit()
    ]
    return max(versions, default=0) + 1


def _archive_from_json(data: dict[str, object]) -> SigningKeyArchive:
    if _expect_int(data.get("archive_version"), "archive_version") != ARCHIVE_VERSION:
        raise SigningKeyArchiveError("unsupported signing-key archive version")
    purpose = _expect_purpose(data.get("purpose"))
    current_raw = data.get("current_key_version")
    current_key_version = None if current_raw is None else KeyVersionId(_expect_str(current_raw))
    current_principal_versions = {
        _expect_str(key): KeyVersionId(_expect_str(value))
        for key, value in _expect_dict(
            data.get("current_principal_versions"),
            "current_principal_versions",
        ).items()
    }
    keys = {
        _expect_str(key): _record_from_json(value)
        for key, value in _expect_dict(data.get("keys"), "keys").items()
    }
    return SigningKeyArchive(
        purpose=purpose,
        current_key_version=current_key_version,
        current_principal_versions=current_principal_versions,
        keys=keys,
    )


def _archive_to_json(archive: SigningKeyArchive) -> dict[str, object]:
    return {
        "archive_version": ARCHIVE_VERSION,
        "current_key_version": None
        if archive.current_key_version is None
        else str(archive.current_key_version),
        "current_principal_versions": {
            principal_id: str(key_version)
            for principal_id, key_version in sorted(archive.current_principal_versions.items())
        },
        "keys": {
            key_version: _record_to_json(record)
            for key_version, record in sorted(archive.keys.items())
        },
        "purpose": archive.purpose,
    }


def _record_from_json(raw: object) -> SigningKeyRecord:
    data = _expect_dict(raw, "key record")
    private_raw = data.get("private_key")
    revoked_raw = data.get("revoked_at_utc")
    return SigningKeyRecord(
        key_version=KeyVersionId(_expect_str(data.get("key_version"))),
        public_key_bytes=_decode_b64(_expect_str(data.get("public_key")), "public_key"),
        private_key_bytes=None
        if private_raw is None
        else _decode_b64(_expect_str(private_raw), "private_key"),
        principal_id=None
        if data.get("principal_id") is None
        else _expect_str(data.get("principal_id")),
        created_at_utc=_parse_datetime(_expect_str(data.get("created_at_utc"))),
        revoked_at_utc=None if revoked_raw is None else _parse_datetime(_expect_str(revoked_raw)),
        revocation_reason=None
        if data.get("revocation_reason") is None
        else _expect_str(data.get("revocation_reason")),
    )


def _record_to_json(record: SigningKeyRecord) -> dict[str, object]:
    return {
        "created_at_utc": _datetime_to_json(record.created_at_utc),
        "key_version": str(record.key_version),
        "principal_id": record.principal_id,
        "private_key": None
        if record.private_key_bytes is None
        else base64.b64encode(record.private_key_bytes).decode("ascii"),
        "public_key": base64.b64encode(record.public_key_bytes).decode("ascii"),
        "revocation_reason": record.revocation_reason,
        "revoked_at_utc": None
        if record.revoked_at_utc is None
        else _datetime_to_json(record.revoked_at_utc),
    }


def _decode_b64(value: str, field_name: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except Exception as exc:
        raise SigningKeyArchiveError(f"{field_name} must be base64") from exc


def _expect_purpose(raw: object) -> ArchivePurpose:
    purpose = _expect_str(raw)
    if purpose not in ("profile", "decision_record", "sop_template"):
        raise SigningKeyArchiveError(f"unsupported archive purpose: {purpose}")
    return cast(ArchivePurpose, purpose)


def _expect_dict(raw: object, field_name: str) -> dict[object, object]:
    if not isinstance(raw, dict):
        raise SigningKeyArchiveError(f"{field_name} must be a JSON object")
    return dict(raw)


def _expect_str(raw: object) -> str:
    if not isinstance(raw, str) or not raw:
        raise SigningKeyArchiveError("expected non-empty string")
    return raw


def _expect_int(raw: object, field_name: str) -> int:
    if not isinstance(raw, int):
        raise SigningKeyArchiveError(f"{field_name} must be an integer")
    return raw


def _datetime_to_json(value: datetime) -> str:
    if value.tzinfo is None:
        raise SigningKeyArchiveError("datetime must be timezone-aware")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise SigningKeyArchiveError("datetime must be timezone-aware")
    return parsed.astimezone(UTC)
