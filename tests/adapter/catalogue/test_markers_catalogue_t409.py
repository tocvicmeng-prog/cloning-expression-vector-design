"""
module_id: tests.adapter.catalogue.test_markers_catalogue_t409
file: tests/adapter/catalogue/test_markers_catalogue_t409.py
task_id: T-409
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from adapter.catalogue.yaml_markers_catalogue import YamlMarkersCatalogue

ROOT = Path(__file__).resolve().parents[3]
MARKERS_SCHEMA = ROOT / "schemas" / "markers.schema.json"


def _amp_marker() -> dict[str, Any]:
    return {
        "id": "marker.ampicillin",
        "name": "Ampicillin / Carbenicillin (bla, TEM-1)",
        "class": "bacterial_antibiotic",
        "gene": "bla",
        "mechanism": "Class A β-lactamase (TEM-1) hydrolyses β-lactam ring",
        "plasmid_borne": True,
        "chromosomal": False,
        "working_concentrations": [
            {
                "host_class": "ecoli",
                "agent": "ampicillin",
                "concentration_ugml": {"min": 50, "typical": 100, "max": 200},
                "medium": "LB",
                "citation": {
                    "text": "Sambrook 4th ed. Appendix A1",
                    "grade": "B2",
                    "accessed": "2026-05-23",
                },
            }
        ],
        "incompatibilities": [],
        "use_cases": ["pUC", "pBR322", "pET"],
        "citation": {
            "text": "Sambrook 4th ed.",
            "grade": "B2",
            "accessed": "2026-05-23",
        },
        "maintenance": {
            "retrieved_at": "2026-05-23",
            "valid_until": "2027-05-23",
            "source_url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#5.2",
            "review_required_after": "2026-11-23",
        },
    }


def _ura3_marker() -> dict[str, Any]:
    return {
        "id": "marker.ura3",
        "name": "URA3 auxotrophic marker",
        "class": "yeast_auxotrophic",
        "gene": "URA3",
        "mechanism": "Restores uracil biosynthesis in ura3-Δ host",
        "plasmid_borne": True,
        "chromosomal": True,
        "working_concentrations": [
            {
                "host_class": "scerevisiae",
                "agent": "uracil_dropout",
                "concentration_ugml": {"min": 0, "typical": 0, "max": 0},
                "medium": "SD -Ura",
                "notes": "auxotrophic — dropout selection",
                "citation": {
                    "text": "Sikorski & Hieter 1989",
                    "grade": "A1",
                    "accessed": "2026-05-23",
                    "pmid": "2659436",
                },
            }
        ],
        "host_genotype_requirement": "ura3-Δ",
        "incompatibilities": [],
        "use_cases": ["pYES2", "pRS416"],
        "citation": {
            "text": "Sikorski & Hieter 1989",
            "grade": "A1",
            "accessed": "2026-05-23",
            "pmid": "2659436",
        },
        "maintenance": {
            "retrieved_at": "2026-05-23",
            "valid_until": "2027-05-23",
            "source_url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#5.2",
            "review_required_after": "2026-11-23",
        },
    }


def _write_fixture_catalogue(tmp_path: Path, items: list[dict[str, Any]]) -> Path:
    catalogue_path = tmp_path / "markers.yaml"
    catalogue_path.write_text(
        yaml.safe_dump({
            "catalogue_id": "cev.markers",
            "schema_version": "1.0.0",
            "maintenance": {
                "retrieved_at": "2026-05-23",
                "valid_until": "2027-05-23",
                "source_url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#5.2",
                "review_required_after": "2026-11-23",
            },
            "items": items,
        }, sort_keys=False),
        encoding="utf-8",
    )
    return catalogue_path


def test_yaml_markers_catalogue_loads_two_markers(tmp_path: Path) -> None:
    """An adapter constructed against a 2-marker fixture exposes both via list_markers()."""
    catalogue_path = _write_fixture_catalogue(tmp_path, [_amp_marker(), _ura3_marker()])
    catalogue = YamlMarkersCatalogue(catalogue_path, MARKERS_SCHEMA)
    markers = catalogue.list_markers()
    assert len(markers) == 2
    assert {m["id"] for m in markers} == {"marker.ampicillin", "marker.ura3"}


def test_yaml_markers_catalogue_get_marker_returns_indexed_payload(tmp_path: Path) -> None:
    catalogue_path = _write_fixture_catalogue(tmp_path, [_amp_marker(), _ura3_marker()])
    catalogue = YamlMarkersCatalogue(catalogue_path, MARKERS_SCHEMA)
    amp = catalogue.get_marker("marker.ampicillin")
    assert amp["class"] == "bacterial_antibiotic"
    assert amp["gene"] == "bla"


def test_yaml_markers_catalogue_get_marker_raises_on_missing(tmp_path: Path) -> None:
    catalogue_path = _write_fixture_catalogue(tmp_path, [_amp_marker()])
    catalogue = YamlMarkersCatalogue(catalogue_path, MARKERS_SCHEMA)
    with pytest.raises(KeyError):
        catalogue.get_marker("marker.does_not_exist")


def test_yaml_markers_catalogue_list_compatible_with_host_class(tmp_path: Path) -> None:
    """ecoli host returns Amp; scerevisiae host returns URA3."""
    catalogue_path = _write_fixture_catalogue(tmp_path, [_amp_marker(), _ura3_marker()])
    catalogue = YamlMarkersCatalogue(catalogue_path, MARKERS_SCHEMA)
    ecoli_compat = catalogue.list_compatible_with_host_class("ecoli")
    assert [m["id"] for m in ecoli_compat] == ["marker.ampicillin"]
    yeast_compat = catalogue.list_compatible_with_host_class("scerevisiae")
    assert [m["id"] for m in yeast_compat] == ["marker.ura3"]
    none_compat = catalogue.list_compatible_with_host_class("kphaffii")
    assert list(none_compat) == []


def test_yaml_markers_catalogue_satisfies_port_protocol() -> None:
    """The concrete YamlMarkersCatalogue must structurally satisfy the MarkersCataloguePort Protocol."""
    from domain.ports import MarkersCataloguePort

    methods = {"get_marker", "list_markers", "list_compatible_with_host_class"}
    for name in methods:
        assert hasattr(YamlMarkersCatalogue, name), f"YamlMarkersCatalogue missing {name!r}"
        assert hasattr(MarkersCataloguePort, name), f"MarkersCataloguePort missing {name!r}"
