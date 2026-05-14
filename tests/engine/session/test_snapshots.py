"""
module_id: tests.engine.session.test_snapshots
file: tests/engine/session/test_snapshots.py
task_id: T-309
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from domain.events import SessionStarted
from domain.sequence import sha256_text
from engine.session import DesignSession, InMemorySnapshotStore, SessionSnapshot, empty_session


def _session() -> DesignSession:
    return empty_session("session-1").apply(
        SessionStarted(
            event_id="event-1",
            occurred_at_utc=datetime(2026, 5, 14, tzinfo=UTC),
            actor_id="actor-1",
            session_id="session-1",
            project_name="demo",
        )
    )


def test_snapshot_store_returns_latest_matching_derivation_hash() -> None:
    store = InMemorySnapshotStore(retain_per_session=2)
    session = _session()
    first_hash = sha256_text("env-a")
    second_hash = sha256_text("env-b")
    store.save(
        SessionSnapshot(
            session_id="session-1",
            event_sequence=1,
            derivation_environment_hash=first_hash,
            session=session,
        )
    )
    store.save(
        SessionSnapshot(
            session_id="session-1",
            event_sequence=2,
            derivation_environment_hash=second_hash,
            session=session,
        )
    )
    store.save(
        SessionSnapshot(
            session_id="session-1",
            event_sequence=3,
            derivation_environment_hash=first_hash,
            session=session,
        )
    )

    latest = store.latest_matching("session-1", first_hash)

    assert latest is not None
    assert latest.event_sequence == 3
    assert [item.event_sequence for item in store.list_session("session-1")] == [2, 3]


def test_snapshot_rejects_mismatched_session_id() -> None:
    with pytest.raises(ValueError, match="match session_id"):
        SessionSnapshot(
            session_id="other-session",
            event_sequence=1,
            derivation_environment_hash=sha256_text("env"),
            session=_session(),
        )
