"""
module_id: adapter.catalogue
file: src/adapter/catalogue/__init__.py
task_id: T-401

Catalogue loader framework.
"""

from __future__ import annotations

from adapter.catalogue.yaml_loader import (
    CatalogueDocument,
    CatalogueSchemaError,
    CatalogueValidationError,
    MaintenanceMetadata,
    catalogue_yaml_paths,
    find_citations,
    load_catalogue,
    load_json_schema,
    load_yaml_document,
    parse_graded_citation,
    parse_maintenance_metadata,
    schema_for_catalogue,
    validate_json_schema,
)

__all__ = [
    "CatalogueDocument",
    "CatalogueSchemaError",
    "CatalogueValidationError",
    "MaintenanceMetadata",
    "catalogue_yaml_paths",
    "find_citations",
    "load_catalogue",
    "load_json_schema",
    "load_yaml_document",
    "parse_graded_citation",
    "parse_maintenance_metadata",
    "schema_for_catalogue",
    "validate_json_schema",
]
