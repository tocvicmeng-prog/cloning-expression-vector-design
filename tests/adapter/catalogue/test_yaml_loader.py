"""
module_id: tests.adapter.catalogue.test_yaml_loader
file: tests/adapter/catalogue/test_yaml_loader.py
task_id: T-401
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from adapter.catalogue import (
    CatalogueSchemaError,
    CatalogueValidationError,
    MaintenanceMetadata,
    catalogue_yaml_paths,
    find_citations,
    load_catalogue,
    load_json_schema,
    load_yaml_document,
    parse_graded_citation,
    schema_for_catalogue,
    validate_json_schema,
)
from tools.ci_gates.source_grade_citation_check import check_citations
from tools.ci_gates.stale_catalogue_check import check_catalogues

ROOT = Path(__file__).resolve().parents[3]


def test_all_seed_catalogues_validate_against_registered_json_schemas() -> None:
    paths = catalogue_yaml_paths(ROOT / "catalogues")

    assert {path.name for path in paths} >= {
        "parts.yaml",
        "hosts.yaml",
        "enzymes.yaml",
        "MR.yaml",
        "WR.yaml",
        "SR.yaml",
        "BR.yaml",
        "MS.yaml",
    }
    for path in paths:
        document = load_catalogue(path, schema_for_catalogue(path, ROOT / "schemas"))
        assert document.maintenance.valid_until >= date(2027, 5, 14)
        assert find_citations(document.payload)


def test_maintenance_and_citation_parsing() -> None:
    document = load_catalogue(
        ROOT / "catalogues" / "parts.yaml",
        ROOT / "schemas" / "parts.schema.json",
    )
    citation = parse_graded_citation(find_citations(document.payload)[0])

    assert document.maintenance.review_required_after == date(2026, 11, 14)
    assert citation.grade == "B2"
    assert citation.url is not None


def test_json_schema_validation_reports_missing_required_field() -> None:
    schema = {
        "type": "object",
        "required": ["id"],
        "properties": {"id": {"type": "string", "minLength": 1}},
    }

    with pytest.raises(CatalogueValidationError, match="missing required key"):
        validate_json_schema({}, schema)


def test_schema_subset_validation_edge_cases(tmp_path: Path) -> None:
    validate_json_schema(
        {"id": "x", "choice": "a", "items": [1], "maybe": None},
        {
            "type": "object",
            "required": ["id"],
            "additionalProperties": False,
            "properties": {
                "choice": {"type": "string", "enum": ["a", "b"]},
                "id": {"type": ["string", "null"], "minLength": 1},
                "items": {"type": "array", "minItems": 1, "items": {"type": "integer"}},
                "maybe": {"type": "null"},
            },
        },
    )

    with pytest.raises(CatalogueValidationError, match="expected"):
        validate_json_schema(
            {"id": 1}, {"type": "object", "properties": {"id": {"type": "string"}}}
        )
    with pytest.raises(CatalogueValidationError, match="not in enum"):
        validate_json_schema("z", {"type": "string", "enum": ["a"]})
    with pytest.raises(CatalogueValidationError, match="shorter"):
        validate_json_schema("", {"type": "string", "minLength": 1})
    with pytest.raises(CatalogueValidationError, match="invalid ISO date"):
        validate_json_schema("bad-date", {"type": "string", "format": "date"})
    with pytest.raises(CatalogueValidationError, match="unexpected keys"):
        validate_json_schema({"extra": True}, {"type": "object", "additionalProperties": False})
    with pytest.raises(CatalogueValidationError, match="at least"):
        validate_json_schema([], {"type": "array", "minItems": 1})
    with pytest.raises(CatalogueSchemaError, match="unsupported"):
        validate_json_schema("x", {"type": "unsupported"})

    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("- not-a-mapping\n", encoding="utf-8")
    with pytest.raises(CatalogueValidationError, match="root must be a mapping"):
        load_yaml_document(invalid_yaml)

    invalid_schema = tmp_path / "invalid.schema.json"
    invalid_schema.write_text("[]", encoding="utf-8")
    with pytest.raises(CatalogueSchemaError, match="schema root"):
        load_json_schema(invalid_schema)

    with pytest.raises(CatalogueSchemaError, match="no schema registered"):
        schema_for_catalogue("unknown.yaml", ROOT / "schemas")


def test_metadata_and_citation_error_paths() -> None:
    assert MaintenanceMetadata(
        retrieved_at=date(2026, 5, 14),
        valid_until=date(2026, 5, 15),
        source_url="source",
        review_required_after=date(2026, 5, 15),
    ).is_stale(date(2026, 5, 16))

    with pytest.raises(ValueError, match="valid_until"):
        MaintenanceMetadata(date(2026, 5, 14), date(2026, 5, 13), "source", date(2026, 5, 14))
    with pytest.raises(ValueError, match="review_required_after"):
        MaintenanceMetadata(date(2026, 5, 14), date(2026, 5, 14), "source", date(2026, 5, 13))
    with pytest.raises(ValueError, match="source_url"):
        MaintenanceMetadata(date(2026, 5, 14), date(2026, 5, 14), "", date(2026, 5, 14))
    with pytest.raises(CatalogueValidationError, match="unsupported citation grade"):
        parse_graded_citation(
            {"text": "bad", "grade": "D", "accessed": "2026-05-14", "url": "source"}
        )
    with pytest.raises(CatalogueValidationError, match="optional string"):
        parse_graded_citation({"text": "bad", "grade": "B2", "accessed": "2026-05-14", "url": 1})


def test_catalogue_gate_check_functions_pass_directly() -> None:
    assert check_catalogues(ROOT).passed
    assert check_citations(ROOT).passed
