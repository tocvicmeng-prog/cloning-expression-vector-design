"""
module_id:           engine.markers_resolver
file:                src/engine/markers_resolver.py
task_id:             T-412, T-413
architecture_refs:   ARCHITECTURE.md § 9.2 MarkersCataloguePort wiring; § 9.1 v0.2 Enrichment Amendment
requirements_refs:   FR-MARK-10, FR-MARK-12; MR-55..60 future predicate consumers
citations:           v0.2 Enrichment Amendment (2026-05-23); joint plan § 4 T-412/T-413
purity:              pure (resolver dispatch + telemetry-sink callback only)

Marker-metadata resolver with dual-read shim.

This resolver is the single in-engine entry point for looking up marker metadata
(working concentration, host_genotype_requirement, citations, etc.) by marker
id. It is consumed by `engine.compatibility` (T-412) and `engine.validation`
(T-413, future MR-55..60 predicates in Phase 5/6).

Resolution order
----------------
1. **Primary**: `MarkersCataloguePort.get_marker(id)` — the v0.2 canonical
   source (catalogues/markers.yaml + schemas/markers.schema.json v1.0).
2. **Fallback** (dual-read window only): a caller-supplied
   `legacy_lookup` callable, which historically used to read from the
   `parts.yaml::markers` block. In the v0.1.0 baseline there was no such block
   — engine code held marker ids as opaque strings — so the fallback is
   forward-compatible scaffolding; if absent, a port miss simply returns
   `None`. Phase 5/6 predicates can wire a real legacy lookup if a transitional
   `parts.yaml::markers` block is reintroduced.

Telemetry
---------
Every fallback hit (port miss → legacy lookup, or port miss + no legacy →
`None`) emits a structured event to the optional `telemetry_sink` callback.
The sink protocol is intentionally minimal — `Callable[[Mapping[str, object]],
None]` — so callers can route to whatever event bus they prefer (governance
events at the composition root, plain `print()` in tests, in-memory list in
unit tests, etc.). When `telemetry_sink is None`, fallback events are silent.

Event schema:
    {
      "event_type": "markers_resolver.shim_hit",
      "marker_id":   <str>,
      "outcome":     "port_hit" | "legacy_hit" | "miss",
      "reason":      <str — short human-readable explanation>,
    }

The architecture-spec § 9.2 paragraph "runtime reads go through this port
exclusively after the dual-read migration window closes" implies that, once
Phase 5/6 lands, this resolver should be reduced to a thin pass-through over
the port. Future task T-MARKERS-SHIM removes the fallback path entirely and
elevates port misses to a hard `KeyError`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from domain.ports import MarkersCataloguePort

Payload = Mapping[str, object]
TelemetrySink = Callable[[Mapping[str, object]], None]
LegacyLookup = Callable[[str], Payload | None]


@dataclass(frozen=True)
class MarkersResolver:
    """Dual-read resolver over MarkersCataloguePort + optional legacy lookup."""

    port: MarkersCataloguePort | None = None
    legacy_lookup: LegacyLookup | None = None
    telemetry_sink: TelemetrySink | None = None

    def resolve(self, marker_id: str) -> Payload | None:
        """Return the marker payload, or `None` if not found in any source.

        Resolution order: port → legacy_lookup → `None`. Each fallback hit
        emits a structured telemetry event when `telemetry_sink` is provided.
        """
        if not marker_id:
            return None

        if self.port is not None:
            try:
                payload = self.port.get_marker(marker_id)
            except KeyError:
                payload = None
            else:
                self._emit(marker_id, outcome="port_hit", reason="resolved via MarkersCataloguePort")
                return payload

        if self.legacy_lookup is not None:
            legacy = self.legacy_lookup(marker_id)
            if legacy is not None:
                self._emit(
                    marker_id,
                    outcome="legacy_hit",
                    reason=(
                        "MarkersCataloguePort miss — falling back to legacy lookup "
                        "(parts.yaml::markers dual-read window; will be removed at T-MARKERS-SHIM)"
                    ),
                )
                return legacy

        self._emit(
            marker_id,
            outcome="miss",
            reason=(
                "marker id not found in MarkersCataloguePort"
                + (" or legacy lookup" if self.legacy_lookup is not None else "")
            ),
        )
        return None

    def _emit(self, marker_id: str, *, outcome: str, reason: str) -> None:
        sink = self.telemetry_sink
        if sink is None:
            return
        sink(
            {
                "event_type": "markers_resolver.shim_hit",
                "marker_id": marker_id,
                "outcome": outcome,
                "reason": reason,
            }
        )


__all__ = ["MarkersResolver", "LegacyLookup", "TelemetrySink"]
