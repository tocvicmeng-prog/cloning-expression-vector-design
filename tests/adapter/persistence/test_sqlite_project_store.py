"""
module_id: tests.adapter.persistence.test_sqlite_project_store
file: tests/adapter/persistence/test_sqlite_project_store.py
task_id: T-310
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from adapter.persistence import ProjectNotFoundError, SqliteProjectStore
from domain.events import SessionStarted
from engine.session import empty_session


def test_sqlite_project_store_saves_sessions_with_wal_settings(tmp_path: Path) -> None:
    store = SqliteProjectStore(tmp_path / "project.sqlite")
    session = empty_session("session-1").apply(
        SessionStarted(
            event_id="event-1",
            occurred_at_utc=datetime(2026, 5, 14, tzinfo=UTC),
            actor_id="actor-1",
            session_id="session-1",
            project_name="demo",
        )
    )

    store.save_session(session)

    assert store.load_session_payload("session-1")["state"] == "COLLECTING"
    assert store.list_sessions() == ("session-1",)

    with store._connect() as connection:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert int(connection.execute("PRAGMA synchronous").fetchone()[0]) == 2


def test_sqlite_project_store_port_payload_round_trip(tmp_path: Path) -> None:
    store = SqliteProjectStore(tmp_path / "project.sqlite")
    project_id = store.save_project((("project_id", "project-a"), ("name", "demo")))

    assert project_id == "project-a"
    assert dict(store.load_project("project-a"))["name"] == "demo"

    try:
        store.load_project("missing")
    except ProjectNotFoundError as exc:
        assert exc.args == ("missing",)
    else:  # pragma: no cover
        raise AssertionError("expected ProjectNotFoundError")
