"""
module_id:           tests.schemas.test_markers_schema
file:                tests/schemas/test_markers_schema.py
task_id:             T-408
architecture_refs:   § 9.1 v0.2 Enrichment Amendment delta summary; § 9.2 MarkersCataloguePort
requirements_refs:   FR-MARK-01..12; UR-13
citations:           v0.2 Enrichment Amendment (2026-05-23); architect analysis § 2.2
purity:              adapter (file I/O + JSONSchema validation via adapter.catalogue helpers)
migration_notes:     - Schema is FLAT (no $ref / $defs) to match the project's hand-rolled validator
                       in adapter.catalogue.yaml_loader._validate, which handles type / enum /
                       required / additionalProperties / minLength / minItems / format=date.
                       Constraints not enforced by the validator (pattern, oneOf, maxLength,
                       allOf/if) are intentionally absent from the schema; the editorial
                       discipline they would have expressed is enforced by separate CI scripts
                       (e.g., markers_auxotrophic_sanity.py, T-415 link-integrity-check).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from adapter.catalogue import load_json_schema, validate_json_schema

ROOT = Path(__file__).resolve().parents[2]
MARKERS_SCHEMA = ROOT / "schemas" / "markers.schema.json"


_POSITIVE_AMP_MARKER: dict[str, Any] = {
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
                "text": "Sambrook & Russell, Molecular Cloning 4th ed., Appendix A1",
                "grade": "B2",
                "accessed": "2026-05-23",
            },
        }
    ],
    "incompatibilities": ["satellite_colonies_at_low_conc"],
    "use_cases": ["pUC", "pBR322", "pET"],
    "citation": {
        "text": "Sambrook & Russell 2001 Molecular Cloning: A Laboratory Manual 4th ed.",
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


def _wrap_in_catalogue(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "catalogue_id": "cev.markers",
        "schema_version": "1.0.0",
        "maintenance": {
            "retrieved_at": "2026-05-23",
            "valid_until": "2027-05-23",
            "source_url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#5.2",
            "review_required_after": "2026-11-23",
        },
        "items": items,
    }


def test_markers_schema_loads() -> None:
    """The new schemas/markers.schema.json file MUST be a valid JSON Schema document."""
    schema = load_json_schema(MARKERS_SCHEMA)
    assert schema["title"] == "CEV selection-markers catalogue"
    assert "catalogue_id" in schema["properties"]


def test_markers_schema_validates_positive_amp_fixture() -> None:
    """A minimal but complete bacterial-antibiotic marker (Amp) validates."""
    schema = load_json_schema(MARKERS_SCHEMA)
    catalogue = _wrap_in_catalogue([_POSITIVE_AMP_MARKER])
    validate_json_schema(catalogue, schema)


def test_markers_schema_rejects_missing_required_field() -> None:
    """Removing a required marker field (e.g. `gene`) MUST cause validation to raise."""
    schema = load_json_schema(MARKERS_SCHEMA)
    bad = dict(_POSITIVE_AMP_MARKER)
    bad.pop("gene")
    catalogue = _wrap_in_catalogue([bad])
    with pytest.raises(Exception):  # CatalogueValidationError
        validate_json_schema(catalogue, schema)


def test_markers_schema_rejects_unknown_class_enum_value() -> None:
    """The `class` field is restricted to a five-value enum (enforced by validator)."""
    schema = load_json_schema(MARKERS_SCHEMA)
    bad = dict(_POSITIVE_AMP_MARKER)
    bad["class"] = "bacterial_phage_selection"  # not in enum
    catalogue = _wrap_in_catalogue([bad])
    with pytest.raises(Exception):
        validate_json_schema(catalogue, schema)


def test_markers_schema_rejects_unknown_host_class_enum_value() -> None:
    """The `working_concentrations[].host_class` enum is enforced."""
    schema = load_json_schema(MARKERS_SCHEMA)
    bad = dict(_POSITIVE_AMP_MARKER)
    bad_wc = dict(bad["working_concentrations"][0])
    bad_wc["host_class"] = "archaea"  # not in enum
    bad["working_concentrations"] = [bad_wc]
    catalogue = _wrap_in_catalogue([bad])
    with pytest.raises(Exception):
        validate_json_schema(catalogue, schema)


def test_markers_schema_rejects_invalid_citation_grade() -> None:
    """Citation grade enum is enforced — only A1/A2/A3/B1/B2/C are valid."""
    schema = load_json_schema(MARKERS_SCHEMA)
    bad = dict(_POSITIVE_AMP_MARKER)
    bad["citation"] = {
        "text": "Lab tradition",
        "grade": "D",  # not in enum
        "accessed": "2026-05-23",
    }
    catalogue = _wrap_in_catalogue([bad])
    with pytest.raises(Exception):
        validate_json_schema(catalogue, schema)


def test_markers_schema_accepts_auxotrophic_sentinel_zero_concentration() -> None:
    """Auxotrophic markers use sentinel {min:0, typical:0, max:0} per FR-MARK-04.

    The schema validator accepts non-zero auxotrophic concentrations too; the editorial
    discipline (sentinel zeros) is enforced by tools/ci/markers_auxotrophic_sanity.py.
    """
    schema = load_json_schema(MARKERS_SCHEMA)
    aux: dict[str, Any] = {
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
                "medium": "SD -Ura (CSM-Ura)",
                "notes": "auxotrophic — selection on dropout medium, not concentration-based",
                "citation": {
                    "text": "Sikorski & Hieter 1989",
                    "grade": "A1",
                    "accessed": "2026-05-23",
                    "pmid": "2659436",
                },
            }
        ],
        "counter_selection": {
            "agent": "5-FOA",
            "selection_medium": "SD +5-FOA",
            "citation": {
                "text": "Boeke 1984",
                "grade": "A1",
                "accessed": "2026-05-23",
                "pmid": "6394957",
            },
        },
        "host_genotype_requirement": "ura3-Δ",
        "incompatibilities": [],
        "use_cases": ["pYES2", "p426GPD", "pRS416"],
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
    catalogue = _wrap_in_catalogue([aux])
    validate_json_schema(catalogue, schema)
