"""
module_id: tests.platform
file: tests/platform/test_sqlite_wal_locking.py
task_id: T-205
"""

from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tests.conftest_platform import make_sync_like_path


def _initialise_database(path: Path) -> None:
    with sqlite3.connect(path, timeout=5) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, value TEXT)")
        connection.commit()


def _write_rows(path: Path, prefix: str) -> None:
    with sqlite3.connect(path, timeout=5) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        for index in range(10):
            connection.execute("INSERT INTO events(value) VALUES (?)", (f"{prefix}-{index}",))
        connection.commit()


def test_sqlite_wal_two_writers_no_database_locked(tmp_path) -> None:  # type: ignore[no-untyped-def]
    database = make_sync_like_path(tmp_path).path / "platform.sqlite"
    _initialise_database(database)

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda prefix: _write_rows(database, prefix), ("a", "b")))

    with sqlite3.connect(database, timeout=5) as connection:
        count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    assert count == 20
