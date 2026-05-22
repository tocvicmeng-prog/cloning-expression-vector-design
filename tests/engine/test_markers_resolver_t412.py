"""
module_id:           tests.engine.test_markers_resolver_t412
file:                tests/engine/test_markers_resolver_t412.py
task_id:             T-412, T-413
architecture_refs:   ARCHITECTURE.md § 9.2 MarkersCataloguePort wiring
requirements_refs:   FR-MARK-10, FR-MARK-12

Coverage for MarkersResolver dual-read shim (T-412/T-413).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import cast

from engine.markers_resolver import MarkersResolver


class _StubMarkersPort:
    """Minimal in-memory MarkersCataloguePort for tests."""

    def __init__(self, items: Mapping[str, Mapping[str, object]]):
        self._items = dict(items)

    def get_marker(self, marker_id: str) -> Mapping[str, object]:
        if marker_id not in self._items:
            raise KeyError(marker_id)
        return self._items[marker_id]

    def list_markers(self) -> Sequence[Mapping[str, object]]:
        return tuple(self._items.values())

    def list_compatible_with_host_class(
        self, host_class: str
    ) -> Sequence[Mapping[str, object]]:
        return tuple(
            item
            for item in self._items.values()
            if any(
                isinstance(wc, dict) and wc.get("host_class") == host_class
                for wc in cast(list, item.get("working_concentrations", []))
            )
        )


def test_resolver_returns_none_when_no_sources_configured() -> None:
    resolver = MarkersResolver()
    assert resolver.resolve("marker.ampicillin") is None


def test_resolver_returns_payload_from_port_on_hit() -> None:
    events: list[Mapping[str, object]] = []
    port = _StubMarkersPort({"marker.ampicillin": {"id": "marker.ampicillin", "class": "antibiotic_bacterial"}})
    resolver = MarkersResolver(port=port, telemetry_sink=events.append)

    payload = resolver.resolve("marker.ampicillin")

    assert payload == {"id": "marker.ampicillin", "class": "antibiotic_bacterial"}
    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "markers_resolver.shim_hit"
    assert event["marker_id"] == "marker.ampicillin"
    assert event["outcome"] == "port_hit"


def test_resolver_falls_back_to_legacy_on_port_miss_and_emits_warn_event() -> None:
    events: list[Mapping[str, object]] = []
    port = _StubMarkersPort({})  # empty — every lookup misses

    def legacy_lookup(marker_id: str) -> Mapping[str, object] | None:
        if marker_id == "marker.legacy_only":
            return {"id": "marker.legacy_only", "source": "parts.yaml::markers"}
        return None

    resolver = MarkersResolver(port=port, legacy_lookup=legacy_lookup, telemetry_sink=events.append)

    payload = resolver.resolve("marker.legacy_only")

    assert payload == {"id": "marker.legacy_only", "source": "parts.yaml::markers"}
    assert len(events) == 1
    event = events[0]
    assert event["outcome"] == "legacy_hit"
    assert "dual-read window" in str(event["reason"])
    assert "T-MARKERS-SHIM" in str(event["reason"])


def test_resolver_emits_miss_event_when_neither_source_resolves() -> None:
    events: list[Mapping[str, object]] = []
    port = _StubMarkersPort({})
    resolver = MarkersResolver(
        port=port,
        legacy_lookup=lambda _id: None,
        telemetry_sink=events.append,
    )

    payload = resolver.resolve("marker.nonexistent")

    assert payload is None
    assert len(events) == 1
    assert events[0]["outcome"] == "miss"


def test_resolver_is_silent_when_no_telemetry_sink() -> None:
    port = _StubMarkersPort({"marker.kan": {"id": "marker.kan"}})
    resolver = MarkersResolver(port=port)  # no telemetry_sink

    assert resolver.resolve("marker.kan") == {"id": "marker.kan"}
    assert resolver.resolve("marker.absent") is None


def test_resolver_handles_empty_marker_id() -> None:
    events: list[Mapping[str, object]] = []
    port = _StubMarkersPort({})
    resolver = MarkersResolver(port=port, telemetry_sink=events.append)

    assert resolver.resolve("") is None
    # empty id is a guard, no telemetry hit
    assert events == []


def test_resolver_port_alone_without_legacy_lookup_returns_none_on_miss() -> None:
    """The fallback emits a single 'miss' event with no 'or legacy lookup' phrasing."""
    events: list[Mapping[str, object]] = []
    port = _StubMarkersPort({})
    resolver = MarkersResolver(port=port, telemetry_sink=events.append)

    payload = resolver.resolve("marker.missing")

    assert payload is None
    assert len(events) == 1
    assert events[0]["outcome"] == "miss"
    assert "or legacy lookup" not in str(events[0]["reason"])
