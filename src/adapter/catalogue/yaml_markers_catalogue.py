"""
module_id:           adapter.catalogue.yaml_markers_catalogue
file:                src/adapter/catalogue/yaml_markers_catalogue.py
task_id:             T-409
architecture_refs:   § 9.1 v0.2 Enrichment Amendment; § 9.2 MarkersCataloguePort wiring
requirements_refs:   FR-MARK-01, FR-MARK-10; UR-13
citations:           v0.2 Enrichment Amendment (2026-05-23); architect § 3.1
purity:              adapter (file I/O + JSONSchema validation)

YAML-backed implementation of MarkersCataloguePort.

Wraps adapter.catalogue.load_catalogue against catalogues/markers.yaml +
schemas/markers.schema.json. Read-only at runtime; mutations are offline
curation only (T-410 populates content).

The architect's step-3 analysis § 3.1 sketched typed value objects
(Marker / MarkerId / MarkerClass / HostClass / WorkingConcentration); the
project convention for the existing catalogue ports (HostCatalogue,
PartCatalogue, EnzymeCatalogue) is to return raw `Payload = Mapping[str, object]`
dicts. This adapter follows the project convention — typed-value-object
shaping is left to downstream consumers (e.g., engine.compatibility).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from adapter.catalogue.yaml_loader import (
    CatalogueDocument,
    CatalogueValidationError,
    load_catalogue,
)

Payload = Mapping[str, object]
PayloadSequence = Sequence[Payload]


class YamlMarkersCatalogue:
    """File-backed `MarkersCataloguePort` implementation.

    The catalogue is loaded eagerly on construction and validated against
    `schemas/markers.schema.json` v1.0. Items are indexed by `id`; lookups are
    O(1). The catalogue is immutable post-construction; rebuilding requires a
    new instance.
    """

    def __init__(self, catalogue_path: Path, schema_path: Path) -> None:
        self._document: CatalogueDocument = load_catalogue(catalogue_path, schema_path)
        items = self._document.payload.get("items", ())
        if not isinstance(items, list):
            raise CatalogueValidationError(
                "markers catalogue payload missing 'items' array"
            )
        self._items: tuple[Payload, ...] = tuple(items)
        self._index: dict[str, Payload] = {
            str(item.get("id", "")): item for item in self._items if isinstance(item, dict)
        }

    def get_marker(self, marker_id: str) -> Payload:
        """Return the marker entry with the given id.

        Raises KeyError if not found — caller responsibility to handle.
        """
        if marker_id not in self._index:
            raise KeyError(f"marker not found: {marker_id!r}")
        return self._index[marker_id]

    def list_markers(self) -> PayloadSequence:
        """Return all markers in catalogue order."""
        return self._items

    def list_compatible_with_host_class(self, host_class: str) -> PayloadSequence:
        """Return markers whose `working_concentrations[].host_class` includes the given host class.

        Used by `engine.compatibility` (per architect § 3.2) to resolve a host's
        `recommended_selection_markers[]` and to enforce MR-MARKER-MISMATCH
        advisories (FR-MARK-12 / MR-59 / MR-60).
        """
        matching: list[Payload] = []
        for item in self._items:
            if not isinstance(item, dict):
                continue
            working_concentrations = item.get("working_concentrations", ())
            if not isinstance(working_concentrations, list):
                continue
            for wc in working_concentrations:
                if isinstance(wc, dict) and wc.get("host_class") == host_class:
                    matching.append(item)
                    break
        return tuple(matching)
