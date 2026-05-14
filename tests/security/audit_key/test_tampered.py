"""
module_id: tests.security.audit_key.test_tampered
file: tests/security/audit_key/test_tampered.py
task_id: T-312b
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from adapter.security.audit_key import AuditKeyArchiveError, FileAuditKeyProvider
from tests.security.audit_key.helpers import admin_principal, deterministic_key_factory


def test_tampered_archive_key_material_is_rejected(tmp_path: Path) -> None:
    archive_path = tmp_path / "audit-key.json"
    FileAuditKeyProvider(
        archive_path,
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    payload = json.loads(archive_path.read_text(encoding="utf-8"))
    payload["keys"]["1"] = base64.b64encode(b"short").decode("ascii")
    archive_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditKeyArchiveError, match="too short"):
        FileAuditKeyProvider(archive_path, emit_warning=False).current_key_version()


def test_malformed_archives_are_rejected(tmp_path: Path) -> None:
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{", encoding="utf-8")
    with pytest.raises(AuditKeyArchiveError, match="invalid audit-key archive JSON"):
        FileAuditKeyProvider(invalid_json, emit_warning=False)

    wrong_shape = tmp_path / "wrong-shape.json"
    wrong_shape.write_text("[]", encoding="utf-8")
    with pytest.raises(AuditKeyArchiveError, match="JSON object"):
        FileAuditKeyProvider(wrong_shape, emit_warning=False)


def test_archive_integrity_metadata_is_validated(tmp_path: Path) -> None:
    archive_path = tmp_path / "audit-key.json"
    provider = FileAuditKeyProvider(
        archive_path,
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    provider.rotate("scheduled", admin_principal())
    payload = json.loads(archive_path.read_text(encoding="utf-8"))
    payload["archived_versions"] = [99]
    archive_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditKeyArchiveError, match="archived audit-key versions missing"):
        FileAuditKeyProvider(archive_path, emit_warning=False)


def test_empty_rotation_reason_and_short_key_are_rejected(tmp_path: Path) -> None:
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    with pytest.raises(ValueError, match="reason"):
        provider.rotate(" ", admin_principal())

    with pytest.raises(AuditKeyArchiveError, match="at least 32 bytes"):
        FileAuditKeyProvider(
            tmp_path / "short-key.json",
            key_factory=lambda: b"short",
            emit_warning=False,
        )
