"""
module_id: tools.audit_key_verifier
file: tools/audit_key_verifier.py
task_id: T-312b

Standalone offline audit-key verifier.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from adapter.persistence import audit_row_message
from adapter.security.audit_key import AuditKeyArchiveError, FileAuditKeyProvider
from domain.ports.audit_key import KeyVersionId, MacBytes


@dataclass(frozen=True)
class AuditVerificationReport:
    total_rows: int
    failing_row_ids: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not self.failing_row_ids


def verify_audit_database(audit_db: str | Path, key_archive: str | Path) -> AuditVerificationReport:
    provider = FileAuditKeyProvider(
        key_archive,
        create_if_missing=False,
        emit_warning=False,
        backend_label="offline_verifier",
    )
    previous_mac = b""
    failing_row_ids: list[str] = []
    rows = _read_rows(Path(audit_db))
    for row in rows:
        entry_id = str(row["entry_id"])
        row_mac = bytes(row["row_mac"])
        prev_mac = bytes(row["prev_mac"])
        if prev_mac != previous_mac:
            failing_row_ids.append(entry_id)
        message = audit_row_message(
            sequence_number=int(row["sequence_number"]),
            entry_type=str(row["entry_type"]),
            payload_json=str(row["payload_json"]),
            occurred_at_utc=str(row["occurred_at_utc"]),
            prev_mac=prev_mac,
        )
        verified = provider.verify_with_archived(
            KeyVersionId(int(row["key_version"])),
            message,
            MacBytes(row_mac),
        )
        if not verified and entry_id not in failing_row_ids:
            failing_row_ids.append(entry_id)
        previous_mac = row_mac
    return AuditVerificationReport(
        total_rows=len(rows),
        failing_row_ids=tuple(failing_row_ids),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a CEV audit SQLite HMAC chain offline.")
    parser.add_argument("--audit-db", required=True, type=Path, help="Path to audit.sqlite")
    parser.add_argument(
        "--key-archive",
        required=True,
        type=Path,
        help="Path to the escrowed audit-key archive JSON",
    )
    args = parser.parse_args(argv)
    try:
        report = verify_audit_database(args.audit_db, args.key_archive)
    except (AuditKeyArchiveError, OSError, sqlite3.Error) as exc:
        print(f"audit verification failed before row verification: {exc}", file=sys.stderr)
        return 1
    if report.clean:
        print(f"audit verification clean: {report.total_rows} rows")
        return 0
    print("audit verification failed for row IDs: " + ", ".join(report.failing_row_ids))
    return 1


def _read_rows(audit_db: Path) -> tuple[sqlite3.Row, ...]:
    connection = sqlite3.connect(f"file:{audit_db}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT entry_id, sequence_number, entry_type, payload_json, occurred_at_utc,
                   key_version, prev_mac, row_mac
            FROM audit_entries
            ORDER BY sequence_number
            """
        ).fetchall()
    finally:
        connection.close()
    return tuple(rows)


if __name__ == "__main__":
    raise SystemExit(main())
