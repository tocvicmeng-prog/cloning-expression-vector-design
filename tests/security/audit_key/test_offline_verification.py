"""
module_id: tests.security.audit_key.test_offline_verification
file: tests/security/audit_key/test_offline_verification.py
task_id: T-312b
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from adapter.security.audit_key import FileAuditKeyProvider
from tests.security.audit_key.helpers import deterministic_key_factory, seed_audit_rows
from tools.audit_key_verifier import main, verify_audit_database


def test_offline_verifier_exits_zero_for_clean_rotated_chain(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    audit_db = tmp_path / "audit.sqlite"
    key_archive = tmp_path / "keys" / "audit-key.json"
    provider = FileAuditKeyProvider(
        key_archive,
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    seed_audit_rows(audit_db, provider, rotate_between_rows=True)

    report = verify_audit_database(audit_db, key_archive)

    assert report.clean
    assert report.total_rows == 2
    assert main(["--audit-db", str(audit_db), "--key-archive", str(key_archive)]) == 0
    assert "2 rows" in capsys.readouterr().out


def test_offline_verifier_exits_one_and_lists_tampered_row(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    audit_db = tmp_path / "audit.sqlite"
    key_archive = tmp_path / "keys" / "audit-key.json"
    provider = FileAuditKeyProvider(
        key_archive,
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    seed_audit_rows(audit_db, provider)
    with sqlite3.connect(audit_db) as connection:
        connection.execute(
            "UPDATE audit_entries SET payload_json = ? WHERE entry_id = ?",
            (json.dumps({"a": "tampered"}), "audit-1"),
        )

    exit_code = main(["--audit-db", str(audit_db), "--key-archive", str(key_archive)])

    assert exit_code == 1
    assert "audit-1" in capsys.readouterr().out


def test_offline_verifier_exits_one_for_missing_archive(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    audit_db = tmp_path / "audit.sqlite"
    key_archive = tmp_path / "missing-audit-key.json"
    provider = FileAuditKeyProvider(
        tmp_path / "keys" / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    seed_audit_rows(audit_db, provider)

    exit_code = main(["--audit-db", str(audit_db), "--key-archive", str(key_archive)])

    assert exit_code == 1
    assert "not found" in capsys.readouterr().err
