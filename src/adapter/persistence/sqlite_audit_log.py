"""
module_id: adapter.persistence.sqlite_audit_log
file: src/adapter/persistence/sqlite_audit_log.py
task_id: T-310

SQLite audit-log read interface with HMAC-chain verification.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from domain.ports.audit_key import AuditKeyProvider, KeyVersionId, MacBytes

Payload = tuple[tuple[str, str], ...]

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_entries (
    entry_id TEXT PRIMARY KEY,
    sequence_number INTEGER NOT NULL UNIQUE,
    entry_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    occurred_at_utc TEXT NOT NULL,
    key_version INTEGER NOT NULL,
    prev_mac BLOB NOT NULL,
    row_mac BLOB NOT NULL
);
"""


class AuditLogTamperDetectedError(ValueError):
    """Raised when the stored audit chain does not verify."""


class AuditLogTamperDetectionUnavailable(RuntimeError):
    """Raised when no AuditKeyProvider is available for chain verification."""


class AuditEntryNotFoundError(KeyError):
    """Raised when an audit entry ID is absent."""


@dataclass(frozen=True)
class SqliteAuditLog:
    path: Path
    key_provider: AuditKeyProvider | None

    def __init__(self, path: str | Path, key_provider: AuditKeyProvider | None) -> None:
        object.__setattr__(self, "path", Path(path))
        object.__setattr__(self, "key_provider", key_provider)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def read_entry(self, entry_id: str) -> Payload:
        self.verify_chain()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM audit_entries WHERE entry_id = ?",
                (entry_id,),
            ).fetchone()
        if row is None:
            raise AuditEntryNotFoundError(entry_id)
        return _payload_from_json(str(row[0]))

    def replay(self) -> tuple[Payload, ...]:
        self.verify_chain()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM audit_entries ORDER BY sequence_number"
            ).fetchall()
        return tuple(_payload_from_json(str(row[0])) for row in rows)

    def verify_chain(self) -> bool:
        if self.key_provider is None:
            raise AuditLogTamperDetectionUnavailable("AuditKeyProvider is required")
        previous_mac = b""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT entry_id, sequence_number, entry_type, payload_json, occurred_at_utc,
                       key_version, prev_mac, row_mac
                FROM audit_entries
                ORDER BY sequence_number
                """
            ).fetchall()
        for row in rows:
            (
                entry_id,
                sequence_number,
                entry_type,
                payload_json,
                occurred_at_utc,
                key_version,
                prev_mac,
                row_mac,
            ) = row
            if bytes(prev_mac) != previous_mac:
                raise AuditLogTamperDetectedError(f"broken previous HMAC at {entry_id}")
            message = audit_row_message(
                sequence_number=int(sequence_number),
                entry_type=str(entry_type),
                payload_json=str(payload_json),
                occurred_at_utc=str(occurred_at_utc),
                prev_mac=bytes(prev_mac),
            )
            verified = self.key_provider.verify_with_archived(
                KeyVersionId(int(key_version)),
                message,
                MacBytes(bytes(row_mac)),
            )
            if not verified:
                raise AuditLogTamperDetectedError(f"invalid audit HMAC at {entry_id}")
            previous_mac = bytes(row_mac)
        return True

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection


def audit_row_message(
    *,
    sequence_number: int,
    entry_type: str,
    payload_json: str,
    occurred_at_utc: str,
    prev_mac: bytes,
) -> bytes:
    return json.dumps(
        {
            "entry_type": entry_type,
            "occurred_at_utc": occurred_at_utc,
            "payload_json": payload_json,
            "prev_mac": prev_mac.hex(),
            "sequence_number": sequence_number,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def _payload_from_json(payload_json: str) -> Payload:
    loaded = json.loads(payload_json)
    if not isinstance(loaded, dict):
        raise TypeError("audit payload must be a JSON object")
    return tuple((key, str(value)) for key, value in sorted(loaded.items()))
