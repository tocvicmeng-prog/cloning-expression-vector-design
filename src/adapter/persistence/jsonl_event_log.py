"""
module_id: adapter.persistence.jsonl_event_log
file: src/adapter/persistence/jsonl_event_log.py
task_id: T-310

Append-only JSONL event log.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from domain.events import DomainEvent, EventStream

Payload = tuple[tuple[str, str], ...]


class EventStreamOwnershipError(ValueError):
    """Raised when an event is appended to the wrong stream log."""


class EventLogDecodeError(ValueError):
    """Raised when a committed JSONL line cannot be decoded."""


@dataclass(frozen=True)
class JsonlEventLog:
    root_dir: Path
    expected_stream: EventStream | None = None

    def __init__(self, root_dir: str | Path, expected_stream: EventStream | None = None) -> None:
        root = Path(root_dir)
        root.mkdir(parents=True, exist_ok=True)
        object.__setattr__(self, "root_dir", root)
        object.__setattr__(self, "expected_stream", expected_stream)

    def append(self, stream_id: str, event: DomainEvent | Payload) -> str:
        path = self._path(stream_id)
        payload = self._event_payload(event)
        line = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        with path.open("ab") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return str(payload["event_id"]) if "event_id" in payload else str(path)

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        return self.append(stream_id, event)

    def read_stream(self, stream_id: str) -> tuple[Payload, ...]:
        return tuple(_payload_from_dict(event.to_dict()) for event in self.read_events(stream_id))

    def read_events(self, stream_id: str) -> tuple[DomainEvent, ...]:
        path = self._path(stream_id)
        if not path.exists():
            return ()
        content = path.read_bytes()
        if not content:
            return ()
        lines = content.splitlines()
        if not content.endswith(b"\n"):
            lines = lines[:-1]
        events: list[DomainEvent] = []
        for index, line in enumerate(lines, start=1):
            try:
                raw = json.loads(line.decode())
                if not isinstance(raw, dict):
                    raise TypeError("event line must decode to a JSON object")
                event = DomainEvent.from_dict(raw)
                self._require_stream(event)
                events.append(event)
            except Exception as exc:
                raise EventLogDecodeError(f"{path}:{index}: {exc}") from exc
        return tuple(events)

    def _event_payload(self, event: DomainEvent | Payload) -> dict[str, object]:
        if isinstance(event, DomainEvent):
            self._require_stream(event)
            return event.to_dict()
        return {key: value for key, value in event}

    def _require_stream(self, event: DomainEvent) -> None:
        if self.expected_stream is not None and event.stream is not self.expected_stream:
            raise EventStreamOwnershipError(
                f"{event.event_type} belongs to {event.stream.value}, "
                f"not {self.expected_stream.value}"
            )

    def _path(self, stream_id: str) -> Path:
        if not stream_id:
            raise ValueError("stream_id cannot be empty")
        safe_name = stream_id if stream_id.endswith(".jsonl") else f"{stream_id}.jsonl"
        return self.root_dir / safe_name


def _payload_from_dict(data: dict[str, object]) -> Payload:
    return tuple((key, str(value)) for key, value in sorted(data.items()))
