"""
module_id:           tests.schemas.test_hosts_v1_1_migration
file:                tests/schemas/test_hosts_v1_1_migration.py
task_id:             T-407
architecture_refs:   § 9.1 v0.2 Enrichment Amendment delta summary; § 9.2 MarkersCataloguePort
requirements_refs:   FR-HOST-13..20; UR-12
citations:           v0.2 Enrichment Amendment (2026-05-23) — additive backward-compatible host phenotype model
purity:              adapter (file I/O + JSONSchema validation via adapter.catalogue helpers)
migration_notes:     - Backward-compatibility contract: every existing host record (schema_version 1.0.0)
                       MUST validate cleanly under hosts.schema.json v1.1.
                     - All v1.1 fields are OPTIONAL; the `required` array MUST NOT have been extended.
                     - When T-411 adds new strain records with v1.1 phenotype fields populated,
                       those records will also be validated by this same schema.
"""

from __future__ import annotations

import json
from pathlib import Path

from adapter.catalogue import load_catalogue, load_json_schema

ROOT = Path(__file__).resolve().parents[2]
HOSTS_YAML = ROOT / "catalogues" / "hosts.yaml"
HOSTS_SCHEMA = ROOT / "schemas" / "hosts.schema.json"


def test_hosts_schema_v1_1_validates_current_v1_0_yaml() -> None:
    """The v1.1 schema MUST validate the unmodified v1.0 hosts.yaml.

    Backward-compatibility contract from the v0.2 Enrichment Amendment:
    all v1.1 phenotype fields are additive and OPTIONAL. Existing host
    records that lack the new fields remain valid under v1.1.

    `load_catalogue` raises on schema-validation failure, so this test
    passes iff the existing v1.0 catalogue parses cleanly under v1.1.
    """
    catalogue = load_catalogue(HOSTS_YAML, HOSTS_SCHEMA)
    assert catalogue.payload["catalogue_id"] == "cev.hosts"
    assert len(catalogue.payload["items"]) > 0


def test_hosts_schema_v1_1_does_not_extend_required_fields() -> None:
    """The v1.1 schema MUST NOT have extended the `required` array on items.

    Adding fields to `required` would break backward-compatibility because
    existing v1.0 host records lack those fields.
    """
    schema = load_json_schema(HOSTS_SCHEMA)
    item_required = set(schema["properties"]["items"]["items"]["required"])
    v1_0_required = {
        "id",
        "name",
        "chassis_class",
        "source_section",
        "host_roles",
        "genotype",
        "supplier_reference",
        "replicons_supported",
        "expression_features",
        "codon_usage_table_id",
        "growth_conditions",
        "biosafety_tier",
        "citation",
        "maintenance",
    }
    assert item_required == v1_0_required, (
        f"v1.1 schema must not extend the v1.0 required field set. "
        f"Got: {item_required}; expected: {v1_0_required}"
    )


def test_hosts_schema_v1_1_advertises_new_phenotype_fields_as_optional() -> None:
    """The v1.1 schema MUST declare the new phenotype fields under properties.

    Per ARCHITECTURE.md § 9.1 + REQUIREMENTS FR-HOST-13..20.
    """
    schema = load_json_schema(HOSTS_SCHEMA)
    item_props = schema["properties"]["items"]["items"]["properties"]
    expected_new_fields = {
        "aliases",
        "t7_lysogen",
        "protease_status",
        "disulfide_environment",
        "rare_codon_supplementation",
        "plasmid_addons",
        "t7_lysozyme_load",
        "recombination_phenotype",
        "methylation_phenotype",
        "recommended_selection_markers",
        "vendor_strain_refs",
    }
    missing = expected_new_fields - set(item_props.keys())
    assert not missing, (
        f"v1.1 schema is missing expected new fields: {missing}"
    )


def test_recommended_selection_markers_pattern_matches_marker_ids() -> None:
    """The `recommended_selection_markers[]` field MUST constrain entries to marker_id pattern.

    Pattern `^marker\\.[a-z0-9_]+$` is enforced by host-marker-link-integrity-check at T-415.
    """
    schema = load_json_schema(HOSTS_SCHEMA)
    item_props = schema["properties"]["items"]["items"]["properties"]
    field = item_props["recommended_selection_markers"]
    item_schema = field["items"]
    assert item_schema["pattern"] == "^marker\\.[a-z0-9_]+$", (
        "recommended_selection_markers[] items must constrain to ^marker\\.[a-z0-9_]+$"
    )
