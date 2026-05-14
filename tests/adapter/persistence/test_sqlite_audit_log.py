"""
module_id: tests.adapter.persistence.test_sqlite_audit_log
file: tests/adapter/persistence/test_sqlite_audit_log.py
task_id: T-310
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from adapter.persistence import (
    AuditLogTamperDetectedError,
    AuditLogTamperDetectionUnavailable,
    SqliteAuditLog,
    audit_row_message,
)
from adapter.persistence.sqlite_audit_log import SCHEMA
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider


def _seed_audit_rows(path: Path, provider: TestAuditKeyProvider) -> None:
    previous_mac = b""
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)
        for sequence_number, payload in enumerate(({"a": "1"}, {"b": "2"}), start=1):
            payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            message = audit_row_message(
                sequence_number=sequence_number,
                entry_type="test",
                payload_json=payload_json,
                occurred_at_utc=f"2026-05-14T00:00:0{sequence_number}Z",
                prev_mac=previous_mac,
            )
            key_version, row_mac = provider.mac(message)
            connection.execute(
                """
                INSERT INTO audit_entries(
                    entry_id, sequence_number, entry_type, payload_json, occurred_at_utc,
                    key_version, prev_mac, row_mac
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"audit-{sequence_number}",
                    sequence_number,
                    "test",
                    payload_json,
                    f"2026-05-14T00:00:0{sequence_number}Z",
                    int(key_version),
                    previous_mac,
                    bytes(row_mac),
                ),
            )
            previous_mac = bytes(row_mac)


def test_sqlite_audit_log_verifies_chain_and_replays_payloads(tmp_path: Path) -> None:
    provider = TestAuditKeyProvider()
    path = tmp_path / "audit.sqlite"
    _seed_audit_rows(path, provider)
    log = SqliteAuditLog(path, provider)

    assert log.verify_chain() is True
    assert dict(log.read_entry("audit-1")) == {"a": "1"}
    assert [dict(item) for item in log.replay()] == [{"a": "1"}, {"b": "2"}]


def test_sqlite_audit_log_detects_tampered_payload(tmp_path: Path) -> None:
    provider = TestAuditKeyProvider()
    path = tmp_path / "audit.sqlite"
    _seed_audit_rows(path, provider)
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE audit_entries SET payload_json = ? WHERE entry_id = ?",
            (json.dumps({"a": "tampered"}), "audit-1"),
        )

    with pytest.raises(AuditLogTamperDetectedError, match="invalid audit HMAC"):
        SqliteAuditLog(path, provider).verify_chain()


def test_sqlite_audit_log_refuses_to_verify_without_key_provider(tmp_path: Path) -> None:
    path = tmp_path / "audit.sqlite"
    _seed_audit_rows(path, TestAuditKeyProvider())

    with pytest.raises(AuditLogTamperDetectionUnavailable):
        SqliteAuditLog(path, None).verify_chain()
