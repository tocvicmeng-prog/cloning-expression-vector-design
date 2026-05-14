"""
module_id: adapter.persistence.sqlite_audit_log_writer
file: src/adapter/persistence/sqlite_audit_log_writer.py
task_id: T-313b

Single-writer SQLite audit-log append adapter.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from adapter.persistence.sqlite_audit_log import SCHEMA, SqliteAuditLog, audit_row_message
from domain.ports.audit_append import AuditEntry, AuditEntryId
from domain.ports.audit_key import AuditKeyProvider


@dataclass(frozen=True)
class AuditLogWriterRow:
    entry_id: str
    sequence_number: int
    key_version: int
    row_mac_hex: str


class SqliteAuditLogWriter:
    """The only production write surface for `audit.sqlite`."""

    def __init__(self, path: str | Path, key_provider: AuditKeyProvider) -> None:
        self.path = Path(path)
        self.key_provider = key_provider
        self._lock = RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA)
        SqliteAuditLog(self.path, key_provider).verify_chain()

    def append(self, entry: AuditEntry) -> AuditEntryId:
        with self._lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            sequence_number = _next_sequence(connection)
            entry_id = AuditEntryId(f"audit-{sequence_number:06d}")
            previous_mac = _previous_mac(connection)
            payload_json = _payload_json(entry.payload)
            occurred_at = entry.occurred_at_utc.astimezone().isoformat()
            message = audit_row_message(
                sequence_number=sequence_number,
                entry_type=entry.entry_type,
                payload_json=payload_json,
                occurred_at_utc=occurred_at,
                prev_mac=previous_mac,
            )
            key_version, row_mac = self.key_provider.mac(message)
            connection.execute(
                """
                INSERT INTO audit_entries(
                    entry_id, sequence_number, entry_type, payload_json, occurred_at_utc,
                    key_version, prev_mac, row_mac
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(entry_id),
                    sequence_number,
                    entry.entry_type,
                    payload_json,
                    occurred_at,
                    int(key_version),
                    previous_mac,
                    bytes(row_mac),
                ),
            )
            return entry_id

    def last_row(self) -> AuditLogWriterRow | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT entry_id, sequence_number, key_version, row_mac
                FROM audit_entries
                ORDER BY sequence_number DESC
                LIMIT 1
                """
            ).fetchone()
        if row is None:
            return None
        return AuditLogWriterRow(
            entry_id=str(row[0]),
            sequence_number=int(row[1]),
            key_version=int(row[2]),
            row_mac_hex=bytes(row[3]).hex(),
        )

    def verify_chain(self) -> bool:
        return SqliteAuditLog(self.path, self.key_provider).verify_chain()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection


def _next_sequence(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        "SELECT COALESCE(MAX(sequence_number), 0) FROM audit_entries"
    ).fetchone()
    return int(row[0]) + 1


def _previous_mac(connection: sqlite3.Connection) -> bytes:
    row = connection.execute(
        "SELECT row_mac FROM audit_entries ORDER BY sequence_number DESC LIMIT 1"
    ).fetchone()
    return b"" if row is None else bytes(row[0])


def _payload_json(payload: Mapping[str, object]) -> str:
    return json.dumps(dict(payload), sort_keys=True, separators=(",", ":"))
