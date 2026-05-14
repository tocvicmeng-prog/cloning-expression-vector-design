"""
module_id: adapter.catalogue.yaml_loader
file: src/adapter/catalogue/yaml_loader.py
task_id: T-401

YAML catalogue loading with a small JSON-Schema validation subset.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TypeAlias, cast

import yaml  # type: ignore[import-untyped]

from domain.types import GradedCitation
from domain.types.citation import CitationGrade

JsonObject: TypeAlias = dict[str, object]

_SCHEMA_BY_FILE: dict[str, str] = {
    "parts.yaml": "parts.schema.json",
    "hosts.yaml": "hosts.schema.json",
    "enzymes.yaml": "enzymes.schema.json",
    "enzyme_buffer_compat.yaml": "enzyme_buffer_compat.schema.json",
    "export_profiles.yaml": "export_profiles.schema.json",
    "institutional_policy.yaml": "institutional_policy.schema.json",
    "risk_advisories.yaml": "risk_advisories.schema.json",
    "screening_trust_policy.yaml": "screening_trust_policy.schema.json",
    "genscript.yaml": "vendor_profile.schema.json",
    "idt.yaml": "vendor_profile.schema.json",
    "twist.yaml": "vendor_profile.schema.json",
    "BR.yaml": "rules_BR.schema.json",
    "MR.yaml": "rules_MR.schema.json",
    "MS.yaml": "rules_MS.schema.json",
    "SR.yaml": "rules_SR.schema.json",
    "WR.yaml": "rules_WR.schema.json",
    "plugin_manifest_seed.yaml": "plugin_manifests.schema.json",
    "sop_template_seed.yaml": "sop_templates.schema.json",
}

_ALLOWED_GRADES = {"A1", "A2", "A3", "B1", "B2", "C"}


class CatalogueValidationError(ValueError):
    """Raised when a catalogue document does not match its schema."""


class CatalogueSchemaError(ValueError):
    """Raised when a schema file cannot be applied."""


@dataclass(frozen=True)
class MaintenanceMetadata:
    retrieved_at: date
    valid_until: date
    source_url: str
    review_required_after: date

    def __post_init__(self) -> None:
        if self.valid_until < self.retrieved_at:
            raise ValueError("valid_until cannot be before retrieved_at")
        if self.review_required_after < self.retrieved_at:
            raise ValueError("review_required_after cannot be before retrieved_at")
        if not self.source_url:
            raise ValueError("source_url cannot be empty")

    def is_stale(self, today: date) -> bool:
        return today > self.valid_until or today > self.review_required_after


@dataclass(frozen=True)
class CatalogueDocument:
    path: Path
    payload: JsonObject
    maintenance: MaintenanceMetadata


def load_catalogue(path: str | Path, schema_path: str | Path) -> CatalogueDocument:
    catalogue_path = Path(path)
    payload = load_yaml_document(catalogue_path)
    schema = load_json_schema(schema_path)
    validate_json_schema(payload, schema)
    return CatalogueDocument(
        path=catalogue_path,
        payload=payload,
        maintenance=parse_maintenance_metadata(payload.get("maintenance")),
    )


def load_yaml_document(path: str | Path) -> JsonObject:
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise CatalogueValidationError(f"{path}: catalogue root must be a mapping")
    return dict(loaded)


def load_json_schema(path: str | Path) -> JsonObject:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise CatalogueSchemaError(f"{path}: schema root must be a JSON object")
    return dict(loaded)


def schema_for_catalogue(path: str | Path, schema_root: str | Path) -> Path:
    catalogue_path = Path(path)
    schema_name = _SCHEMA_BY_FILE.get(catalogue_path.name)
    if schema_name is None:
        raise CatalogueSchemaError(f"no schema registered for {catalogue_path}")
    return Path(schema_root) / schema_name


def catalogue_yaml_paths(root: str | Path) -> tuple[Path, ...]:
    catalogue_root = Path(root)
    return tuple(
        sorted(
            path
            for path in catalogue_root.rglob("*.yaml")
            if path.is_file() and not path.name.startswith(".")
        )
    )


def parse_maintenance_metadata(raw: object) -> MaintenanceMetadata:
    data = _expect_object(raw, "maintenance")
    return MaintenanceMetadata(
        retrieved_at=_parse_date(_expect_str(data, "retrieved_at")),
        valid_until=_parse_date(_expect_str(data, "valid_until")),
        source_url=_expect_str(data, "source_url"),
        review_required_after=_parse_date(_expect_str(data, "review_required_after")),
    )


def parse_graded_citation(raw: object) -> GradedCitation:
    data = _expect_object(raw, "citation")
    grade = _expect_str(data, "grade")
    if grade not in _ALLOWED_GRADES:
        raise CatalogueValidationError(f"unsupported citation grade: {grade}")
    return GradedCitation(
        text=_expect_str(data, "text"),
        grade=cast(CitationGrade, grade),
        accessed=_parse_date(_expect_str(data, "accessed")),
        pmid=_optional_str(data.get("pmid")),
        doi=_optional_str(data.get("doi")),
        pmc=_optional_str(data.get("pmc")),
        url=_optional_str(data.get("url")),
    )


def find_citations(value: object) -> tuple[JsonObject, ...]:
    found: list[JsonObject] = []
    _collect_citations(value, found)
    return tuple(found)


def validate_json_schema(instance: object, schema: Mapping[str, object]) -> None:
    _validate(instance, schema, "$")


def _validate(instance: object, schema: Mapping[str, object], path: str) -> None:
    expected_type = schema.get("type")
    if expected_type is not None and not _matches_type(instance, expected_type):
        raise CatalogueValidationError(
            f"{path}: expected {expected_type}, got {type(instance).__name__}"
        )
    enum = schema.get("enum")
    if enum is not None and instance not in _expect_array(enum, f"{path}.enum"):
        raise CatalogueValidationError(f"{path}: value {instance!r} not in enum")
    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            raise CatalogueValidationError(f"{path}: string shorter than {min_length}")
        if schema.get("format") == "date":
            _parse_date(instance)
    if isinstance(instance, dict):
        _validate_object(instance, schema, path)
    if isinstance(instance, list):
        _validate_array(instance, schema, path)


def _validate_object(
    instance: dict[object, object],
    schema: Mapping[str, object],
    path: str,
) -> None:
    properties = _optional_object(schema.get("properties"), f"{path}.properties")
    required = tuple(str(item) for item in _optional_array(schema.get("required")))
    for key in required:
        if key not in instance:
            raise CatalogueValidationError(f"{path}: missing required key {key}")
    for key, subschema in properties.items():
        if key in instance:
            _validate(instance[key], _expect_schema(subschema, f"{path}.{key}"), f"{path}.{key}")
    if schema.get("additionalProperties") is False:
        extra = set(instance) - set(properties)
        if extra:
            raise CatalogueValidationError(f"{path}: unexpected keys {sorted(map(str, extra))}")


def _validate_array(instance: list[object], schema: Mapping[str, object], path: str) -> None:
    min_items = schema.get("minItems")
    if isinstance(min_items, int) and len(instance) < min_items:
        raise CatalogueValidationError(f"{path}: expected at least {min_items} items")
    item_schema = schema.get("items")
    if item_schema is not None:
        schema_obj = _expect_schema(item_schema, f"{path}.items")
        for index, item in enumerate(instance):
            _validate(item, schema_obj, f"{path}[{index}]")


def _matches_type(instance: object, expected_type: object) -> bool:
    if isinstance(expected_type, list):
        return any(_matches_type(instance, item) for item in expected_type)
    match expected_type:
        case "object":
            return isinstance(instance, dict)
        case "array":
            return isinstance(instance, list)
        case "string":
            return isinstance(instance, str)
        case "boolean":
            return isinstance(instance, bool)
        case "integer":
            return isinstance(instance, int) and not isinstance(instance, bool)
        case "number":
            return isinstance(instance, int | float) and not isinstance(instance, bool)
        case "null":
            return instance is None
        case _:
            raise CatalogueSchemaError(f"unsupported JSON Schema type: {expected_type}")


def _collect_citations(value: object, found: list[JsonObject]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "citation":
                found.append(_expect_object(item, "citation"))
            elif key == "citations":
                for citation in _expect_array(item, "citations"):
                    found.append(_expect_object(citation, "citation"))
            else:
                _collect_citations(item, found)
    elif isinstance(value, list):
        for item in value:
            _collect_citations(item, found)


def _expect_schema(raw: object, name: str) -> Mapping[str, object]:
    return _expect_object(raw, name)


def _expect_object(raw: object, name: str) -> JsonObject:
    if not isinstance(raw, dict):
        raise CatalogueValidationError(f"{name} must be an object")
    return dict(raw)


def _optional_object(raw: object, name: str) -> JsonObject:
    if raw is None:
        return {}
    return _expect_object(raw, name)


def _expect_array(raw: object, name: str) -> list[object]:
    if not isinstance(raw, list):
        raise CatalogueValidationError(f"{name} must be an array")
    return raw


def _optional_array(raw: object) -> list[object]:
    return [] if raw is None else _expect_array(raw, "array")


def _expect_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise CatalogueValidationError(f"{key} must be a string")
    if not value:
        raise CatalogueValidationError(f"{key} cannot be empty")
    return value


def _optional_str(raw: object) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise CatalogueValidationError("optional string field must be a string")
    return raw


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CatalogueValidationError(f"invalid ISO date: {value}") from exc
