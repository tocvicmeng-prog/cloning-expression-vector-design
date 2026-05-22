"""
module_id:           tests.schemas.test_corpus_record_schema
file:                tests/schemas/test_corpus_record_schema.py
task_id:             T-1402
architecture_refs:   § 9.3 ML Training Corpus Subsystem; § 9.3.2 split sequence/annotation license schema
requirements_refs:   FR-ML-01..15; BR-15..17; UR-14
citations:           v0.2 Enrichment Amendment (2026-05-23); architect § 2.3 + IP-auditor § 5.2 fold-in
purity:              adapter (file I/O + JSONSchema validation)
migration_notes:     - Schema lives OUTSIDE schemas/ at docs/ml_corpus/schemas/corpus_record.schema.json
                       per architect § 9.3 (training data, not runtime config; enforced by
                       the `ml-corpus-is-not-runtime` import-linter contract).
                     - License block is SPLIT into sequence_license + annotation_license per
                       IP-auditor § 5.2.
                     - snapgene_crosscheck supports `checked: false` per architect § 9.3.5
                       (process-only artefact, not a runtime gate).
                     - Schema is FLAT to match the project's hand-rolled validator; constraints
                       not enforceable by the validator (pattern, allOf/if conditional required,
                       maxLength) are enforced by separate CI gates at T-1403 / T-1409.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from adapter.catalogue import load_json_schema, validate_json_schema

ROOT = Path(__file__).resolve().parents[2]
CORPUS_RECORD_SCHEMA = ROOT / "docs" / "ml_corpus" / "schemas" / "corpus_record.schema.json"


def _full_license_block(spdx: str = "CC0-1.0", commercial_ok: bool = True, ml_ok: bool = True) -> dict[str, Any]:
    return {
        "spdx_id": spdx,
        "redistribution_allowed": True,
        "ml_training_allowed": ml_ok,
        "attribution_required": False,
        "commercial_use_allowed": commercial_ok,
        "source_text_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    }


_POSITIVE_PUC19_BACKBONE: dict[str, Any] = {
    "id": "corpus.backbone.ecoli.puc19",
    "category": "backbone",
    "sequence": {
        "bases": "ACGTACGTACGTACGTACGT",  # placeholder; real records carry full backbone sequence
        "topology": "circular",
        "length_bp": 20,
    },
    "annotation": [
        {
            "type": "rep_origin",
            "start": 0,
            "end": 10,
            "strand": "+",
            "qualifiers": {"label": "pMB1 origin (placeholder)"},
        }
    ],
    "provenance": {
        "source": "ncbi_genbank",
        "accession_or_url": "M77789.2",
        "retrieved_at": "2026-05-23T12:00:00Z",
        "retrieved_by": "researcher@gmexpression.example",
    },
    "license": {
        "sequence_license": _full_license_block(),
        "annotation_license": _full_license_block(),
    },
    "snapgene_crosscheck": {"checked": False},
    "host_topology": {"host_class": "ecoli", "replicon": "pMB1", "copy_number_class": "high"},
    "intended_use_category": ["cloning_propagation"],
    "checksum": {"algorithm": "sha256", "value": "0" * 64},
}


def test_corpus_record_schema_loads() -> None:
    """The new corpus_record.schema.json v1.0 file MUST be a valid JSON Schema document."""
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    assert schema["title"] == "CEV ML training corpus record"


def test_corpus_record_schema_validates_positive_backbone_fixture() -> None:
    """A minimal but complete pUC19-like backbone record validates."""
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    validate_json_schema(_POSITIVE_PUC19_BACKBONE, schema)


def test_corpus_record_schema_requires_split_license_blocks() -> None:
    """The license object MUST require both sequence_license and annotation_license (IP-auditor § 5.2 fold-in)."""
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    bad = dict(_POSITIVE_PUC19_BACKBONE)
    bad["license"] = {"sequence_license": _full_license_block()}  # missing annotation_license
    with pytest.raises(Exception):
        validate_json_schema(bad, schema)


def test_corpus_record_schema_rejects_explicitly_required_license_field_missing() -> None:
    """Each license block MUST require redistribution_allowed and ml_training_allowed explicitly."""
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    bad = dict(_POSITIVE_PUC19_BACKBONE)
    incomplete = {
        "spdx_id": "CC0-1.0",
        "redistribution_allowed": True,
        # ml_training_allowed deliberately omitted
        "attribution_required": False,
        "commercial_use_allowed": True,
        "source_text_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    }
    bad["license"] = {
        "sequence_license": incomplete,
        "annotation_license": _full_license_block(),
    }
    with pytest.raises(Exception):
        validate_json_schema(bad, schema)


def test_corpus_record_schema_rejects_addgene_metadata_only_in_provenance_enum() -> None:
    """The provenance.source enum MUST NOT include `addgene_metadata_only` as a default-allow option.

    Per FR-ML-04: Addgene-metadata sources require per-case clearance via exclusions.yaml, never
    as a default in-corpus provenance source.
    """
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    source_enum = set(schema["properties"]["provenance"]["properties"]["source"]["enum"])
    assert "addgene_metadata_only" not in source_enum, (
        "addgene_metadata_only must not appear in the default-allow provenance enum (FR-ML-04)."
    )


def test_corpus_record_schema_provenance_source_enum_is_complete() -> None:
    """The provenance.source enum MUST cover the Tier-1+Tier-2 allowlist per IP-auditor § 8.1."""
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    source_enum = set(schema["properties"]["provenance"]["properties"]["source"]["enum"])
    expected = {
        "ncbi_genbank",
        "ebi_ena",
        "ddbj",
        "igem_registry",
        "jbei_ice",
        "dnasu",
        "vendor_published_map",
        "primary_literature",
        "fpbase",
    }
    assert source_enum == expected, (
        f"provenance.source enum drift detected. Got: {source_enum}; expected: {expected}"
    )


def test_corpus_record_schema_snapgene_crosscheck_allows_unchecked() -> None:
    """`snapgene_crosscheck.checked: false` MUST be valid (process-only artefact, not a hard gate).

    Per ARCHITECTURE.md § 9.3.5: the cross-check is human judgement, tracked for release-time
    coverage reporting but does not block per-record ingestion.
    """
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    record = dict(_POSITIVE_PUC19_BACKBONE)
    record["snapgene_crosscheck"] = {"checked": False}
    validate_json_schema(record, schema)


def test_corpus_record_schema_rejects_unknown_category_enum_value() -> None:
    """The `category` enum is enforced — only the 15 declared categories are valid."""
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    bad = dict(_POSITIVE_PUC19_BACKBONE)
    bad["category"] = "vector_backbone"  # not in enum (should be 'backbone')
    with pytest.raises(Exception):
        validate_json_schema(bad, schema)


def test_corpus_record_schema_rejects_unknown_topology_enum_value() -> None:
    """The `sequence.topology` enum is enforced — only circular or linear."""
    schema = load_json_schema(CORPUS_RECORD_SCHEMA)
    bad = dict(_POSITIVE_PUC19_BACKBONE)
    bad_seq = dict(bad["sequence"])
    bad_seq["topology"] = "branched"
    bad["sequence"] = bad_seq
    with pytest.raises(Exception):
        validate_json_schema(bad, schema)
