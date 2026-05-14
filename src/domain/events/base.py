"""
module_id: domain.events.base
file: src/domain/events/base.py
task_id: T-305

Typed event base, stream discriminator, and deterministic serialisation helpers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from datetime import UTC, datetime
from enum import Enum
from typing import Any, ClassVar, Self, cast, get_args, get_origin, get_type_hints

EventId = str
ActorId = str
SessionId = str
InstitutionId = str
CanonicalPayload = tuple[tuple[str, str], ...]


class EventStream(Enum):
    DESIGN = "design"
    GOVERNANCE = "governance"
    EXPORT = "export"


EVENT_REGISTRY: dict[str, type[DomainEvent]] = {}


def register_event_type(cls: type[DomainEvent]) -> type[DomainEvent]:
    if cls.event_type in EVENT_REGISTRY:
        raise ValueError(f"duplicate event_type registered: {cls.event_type}")
    EVENT_REGISTRY[cls.event_type] = cls
    return cls


@dataclass(frozen=True)
class DomainEvent:
    event_id: EventId
    occurred_at_utc: datetime
    actor_id: ActorId

    event_type: ClassVar[str] = "domain_event"
    stream: ClassVar[EventStream]

    def __post_init__(self) -> None:
        _require_non_empty(self.event_id, "event_id")
        _require_non_empty(self.actor_id, "actor_id")
        if self.occurred_at_utc.tzinfo is None:
            raise ValueError("occurred_at_utc must be timezone-aware")

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "event_type": self.event_type,
            "stream": self.stream.value,
        }
        for field in fields(self):
            payload[field.name] = _json_ready(getattr(self, field.name))
        return payload

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> DomainEvent:
        event_type = _expect_str(data.get("event_type"), "event_type")
        event_cls = EVENT_REGISTRY[event_type]
        return event_cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, object]) -> Self:
        kwargs: dict[str, object] = {}
        hints = get_type_hints(cls)
        for field in fields(cls):
            kwargs[field.name] = _parse_value(
                data.get(field.name),
                hints[field.name],
                field.name,
            )
        return cls(**cast(dict[str, Any], kwargs))


@dataclass(frozen=True)
class DesignEvent(DomainEvent):
    session_id: SessionId
    stream: ClassVar[EventStream] = EventStream.DESIGN

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_non_empty(self.session_id, "session_id")


@dataclass(frozen=True)
class GovernanceEvent(DomainEvent):
    institution_id: InstitutionId
    stream: ClassVar[EventStream] = EventStream.GOVERNANCE

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_non_empty(self.institution_id, "institution_id")


@dataclass(frozen=True)
class ExportEvent(DomainEvent):
    institution_id: InstitutionId
    stream: ClassVar[EventStream] = EventStream.EXPORT

    def __post_init__(self) -> None:
        super().__post_init__()
        _require_non_empty(self.institution_id, "institution_id")


def _parse_value(raw: object, hint: object, field_name: str) -> object:
    if hint is datetime:
        return _parse_datetime(raw, field_name)
    if hint is str:
        return _expect_str(raw, field_name)
    if hint is bool:
        if not isinstance(raw, bool):
            raise TypeError(f"{field_name} must be a boolean")
        return raw
    origin = get_origin(hint)
    args = get_args(hint)
    if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
        if args[0] is str:
            return tuple(_expect_str(item, field_name) for item in _expect_list(raw, field_name))
        if get_origin(args[0]) is tuple:
            return _parse_payload_items(raw, field_name)
    raise TypeError(f"unsupported event field type for {field_name}: {hint}")


def _parse_payload_items(raw: object, field_name: str) -> CanonicalPayload:
    items = _expect_list(raw, field_name)
    parsed: list[tuple[str, str]] = []
    for item in items:
        pair = _expect_list(item, field_name)
        if len(pair) != 2:
            raise TypeError(f"{field_name} items must be key/value pairs")
        parsed.append((_expect_str(pair[0], field_name), _expect_str(pair[1], field_name)))
    return tuple(parsed)


def _json_ready(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    return value


def _parse_datetime(raw: object, field_name: str) -> datetime:
    text = _expect_str(raw, field_name)
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def _expect_list(raw: object, field_name: str) -> list[object]:
    if not isinstance(raw, list):
        raise TypeError(f"{field_name} must be a list")
    return raw


def _expect_str(raw: object, field_name: str) -> str:
    if not isinstance(raw, str):
        raise TypeError(f"{field_name} must be a string")
    return raw


def _require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
