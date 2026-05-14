"""
module_id: tests.platform
file: tests/platform/test_onedrive_sqlite_wal_smoke.py
task_id: T-205
"""

from __future__ import annotations

import sqlite3

import pytest

from tests.conftest_platform import active_sync_path_from_env

pytestmark = pytest.mark.requires_active_onedrive_sync


def test_active_onedrive_sqlite_wal_smoke_is_local_only() -> None:
    active_path = active_sync_path_from_env()
    if active_path is None:
        pytest.skip("set CEV_ACTIVE_ONEDRIVE_PATH to run active OneDrive smoke test")

    database = active_path.path / "cev_onedrive_smoke.sqlite"
    with sqlite3.connect(database, timeout=5) as connection:
        mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
        connection.execute("CREATE TABLE IF NOT EXISTS smoke (value TEXT)")
        connection.execute("INSERT INTO smoke(value) VALUES ('ok')")
        connection.commit()

    assert mode.lower() == "wal"
