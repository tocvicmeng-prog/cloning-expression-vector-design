"""
module_id: tests.security.audit_key.helpers
file: tests/security/audit_key/helpers.py
task_id: T-312b
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from adapter.persistence import audit_row_message
from adapter.persistence.sqlite_audit_log import SCHEMA
from domain.ports.audit_key import AuditKeyProvider
from domain.security import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    InstitutionId,
    PrincipalId,
    SecurityRole,
)

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def deterministic_key_factory() -> Callable[[], bytes]:
    counter = 0

    def make_key() -> bytes:
        nonlocal counter
        counter += 1
        return hashlib.sha256(f"audit-key-{counter}".encode()).digest()

    return make_key


def admin_principal() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def bootstrap_principal() -> DeveloperBootstrapPrincipal:
    return DeveloperBootstrapPrincipal(
        id=PrincipalId("dev-bootstrap-1"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
        is_bootstrap=True,
        bootstrap_expires_at=datetime.now(UTC) + timedelta(days=1),
    )


def seed_audit_rows(
    path: Path,
    provider: AuditKeyProvider,
    *,
    rotate_between_rows: bool = False,
) -> None:
    previous_mac = b""
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)
        for sequence_number, payload in enumerate(({"a": "1"}, {"b": "2"}), start=1):
            if sequence_number == 2 and rotate_between_rows:
                provider.rotate("between-row rotation", admin_principal())
            payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            occurred_at_utc = f"2026-05-14T00:00:0{sequence_number}Z"
            message = audit_row_message(
                sequence_number=sequence_number,
                entry_type="test",
                payload_json=payload_json,
                occurred_at_utc=occurred_at_utc,
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
                    occurred_at_utc,
                    int(key_version),
                    previous_mac,
                    bytes(row_mac),
                ),
            )
            previous_mac = bytes(row_mac)
