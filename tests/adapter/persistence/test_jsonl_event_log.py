"""
module_id: tests.adapter.persistence.test_jsonl_event_log
file: tests/adapter/persistence/test_jsonl_event_log.py
task_id: T-310
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from adapter.persistence import EventStreamOwnershipError, JsonlEventLog
from domain.events import DesignEvent, EventStream, ReviewerSignedOff, SessionStarted
from engine.session import replay_canonical_json
from tests.engine.session.test_replay_determinism import _reviewer_event, _session_events

BASE_TIME = datetime(2026, 5, 14, tzinfo=UTC)


def _started(index: int) -> SessionStarted:
    return SessionStarted(
        event_id=f"event-{index}",
        occurred_at_utc=BASE_TIME + timedelta(seconds=index),
        actor_id="actor-1",
        session_id="session-1",
        project_name=f"demo-{index}",
    )


def test_jsonl_event_log_appends_fsyncs_and_reads_events(tmp_path: Path) -> None:
    log = JsonlEventLog(tmp_path / "events" / "design", expected_stream=EventStream.DESIGN)
    event = _started(1)

    event_id = log.append_event("session-1", event)

    assert event_id == "event-1"
    assert log.read_events("session-1") == (event,)
    assert dict(log.read_stream("session-1")[0])["event_id"] == "event-1"


def test_jsonl_event_log_drops_trailing_partial_crash_line(tmp_path: Path) -> None:
    log = JsonlEventLog(tmp_path / "events" / "design", expected_stream=EventStream.DESIGN)
    log.append_event("session-1", _started(1))
    path = tmp_path / "events" / "design" / "session-1.jsonl"
    with path.open("ab") as handle:
        handle.write(b'{"event_type":"SessionStarted"')

    assert log.read_events("session-1") == (_started(1),)


def test_jsonl_event_log_enforces_stream_ownership(tmp_path: Path) -> None:
    log = JsonlEventLog(tmp_path / "events" / "design", expected_stream=EventStream.DESIGN)
    governance = ReviewerSignedOff(
        event_id="governance-1",
        occurred_at_utc=BASE_TIME,
        actor_id="reviewer-1",
        institution_id="inst",
        decision_record_payload=(("decision", "approved"),),
        decision_record_hash="decision-1",
    )

    with pytest.raises(EventStreamOwnershipError, match="governance"):
        log.append_event("session-1", governance)


def test_jsonl_event_log_replays_100_synthetic_sessions(tmp_path: Path) -> None:
    log = JsonlEventLog(tmp_path / "events" / "design", expected_stream=EventStream.DESIGN)
    for index in range(100):
        session_id = f"session-{index}"
        events = _session_events(session_id, index)
        for event in events:
            log.append_event(session_id, event)

        stored = tuple(
            event for event in log.read_events(session_id) if isinstance(event, DesignEvent)
        )
        assert replay_canonical_json(
            stored, governance_events=(_reviewer_event(index),)
        ) == replay_canonical_json(
            events,
            governance_events=(_reviewer_event(index),),
        )
