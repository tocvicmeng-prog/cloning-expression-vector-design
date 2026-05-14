"""
module_id: tests.security.audit_key.test_absent
file: tests/security/audit_key/test_absent.py
task_id: T-312b
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.security.audit_key import AuditKeyArchiveError, FileAuditKeyProvider


def test_offline_load_refuses_absent_escrow_archive(tmp_path: Path) -> None:
    with pytest.raises(AuditKeyArchiveError, match="not found"):
        FileAuditKeyProvider(
            tmp_path / "missing-audit-key.json",
            create_if_missing=False,
            emit_warning=False,
        )
