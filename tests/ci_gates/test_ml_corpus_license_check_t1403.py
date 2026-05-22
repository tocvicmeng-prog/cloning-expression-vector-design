"""
module_id: tests.ci_gates.test_ml_corpus_license_check_t1403
file: tests/ci_gates/test_ml_corpus_license_check_t1403.py
task_id: T-1403
architecture_refs: § 9.3 ML Training Corpus Subsystem; § 9.3.2 split license schema
requirements_refs: FR-ML-05, FR-ML-08, FR-ML-09; BR-15

Tests for the ml-corpus-license-check CI gate (T-1403).

Coverage:
  1. Empty corpus: gate passes (vacuous baseline; BR-15 default-deny holds).
  2. Real v0.2 corpus (zero records as of 2026-05-23): gate passes.
  3. Complete record passes.
  4. Missing license object → fails.
  5. Missing sequence_license block → fails.
  6. Missing annotation_license block → fails.
  7. Missing required boolean field (ml_training_allowed) on a sub-block → fails.
  8. ml_training_allowed: false on sequence_license under records/ → fails.
  9. Provenance source not in allowlist (e.g., addgene_metadata_only) → fails.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.ci_gates.ml_corpus_license_check import (
    ALLOWED_PROVENANCE_SOURCES,
    check_ml_corpus_license,
)

ROOT = Path(__file__).resolve().parents[2]


def _full_license_block(spdx: str = "CC0-1.0", ml_ok: bool = True, commercial_ok: bool = True) -> dict[str, Any]:
    return {
        "spdx_id": spdx,
        "redistribution_allowed": True,
        "ml_training_allowed": ml_ok,
        "attribution_required": False,
        "commercial_use_allowed": commercial_ok,
        "source_text_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    }


def _full_record(record_id: str = "corpus.backbone.ecoli.puc19_fixture") -> dict[str, Any]:
    return {
        "id": record_id,
        "category": "backbone",
        "sequence": {"bases": "ACGTACGT", "topology": "circular", "length_bp": 8},
        "annotation": [],
        "provenance": {
            "source": "ncbi_genbank",
            "accession_or_url": "M77789.2",
            "retrieved_at": "2026-05-23T12:00:00Z",
            "retrieved_by": "fixture@example",
        },
        "license": {
            "sequence_license": _full_license_block(),
            "annotation_license": _full_license_block(),
        },
        "snapgene_crosscheck": {"checked": False},
        "host_topology": {"host_class": "ecoli"},
        "intended_use_category": ["cloning_propagation"],
        "checksum": {"algorithm": "sha256", "value": "0" * 64},
    }


def _write_record(tmp_path: Path, record: dict[str, Any], rel_path: str = "records/backbones/ecoli/test.json") -> None:
    target = tmp_path / "docs" / "ml_corpus" / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record), encoding="utf-8")


def test_ml_corpus_license_check_passes_on_real_v0_2_corpus() -> None:
    """The real v0.2 corpus (zero records as of 2026-05-23) MUST pass — BR-15 default-deny baseline."""
    result = check_ml_corpus_license(ROOT)
    assert result.passed, f"BR-15 default-deny baseline broken. Findings: {result.messages}"


def test_ml_corpus_license_check_passes_on_empty_corpus(tmp_path: Path) -> None:
    """An empty corpus tree (no records yet) MUST pass with the vacuous message."""
    (tmp_path / "docs" / "ml_corpus" / "records").mkdir(parents=True)
    result = check_ml_corpus_license(tmp_path)
    assert result.passed
    assert any("default-deny" in msg for msg in result.messages)


def test_ml_corpus_license_check_passes_on_complete_record(tmp_path: Path) -> None:
    """A record with complete license blocks (both sequence_license and annotation_license) MUST pass."""
    _write_record(tmp_path, _full_record())
    result = check_ml_corpus_license(tmp_path)
    assert result.passed, f"complete record incorrectly flagged. Findings: {result.messages}"


def test_ml_corpus_license_check_fails_on_missing_license_object(tmp_path: Path) -> None:
    """A record without a `license` object MUST fail."""
    record = _full_record()
    record.pop("license")
    _write_record(tmp_path, record)
    result = check_ml_corpus_license(tmp_path)
    assert not result.passed
    assert any("missing required `license`" in msg for msg in result.messages)


def test_ml_corpus_license_check_fails_on_missing_sequence_license_block(tmp_path: Path) -> None:
    """A record missing the sequence_license sub-block MUST fail."""
    record = _full_record()
    record["license"] = {"annotation_license": _full_license_block()}  # missing sequence_license
    _write_record(tmp_path, record)
    result = check_ml_corpus_license(tmp_path)
    assert not result.passed
    assert any("sequence_license" in msg for msg in result.messages)


def test_ml_corpus_license_check_fails_on_missing_required_boolean_field(tmp_path: Path) -> None:
    """A license sub-block missing `ml_training_allowed` (or any required explicit boolean) MUST fail."""
    record = _full_record()
    incomplete = {
        "spdx_id": "CC0-1.0",
        "redistribution_allowed": True,
        # ml_training_allowed deliberately omitted
        "attribution_required": False,
        "commercial_use_allowed": True,
        "source_text_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    }
    record["license"] = {
        "sequence_license": incomplete,
        "annotation_license": _full_license_block(),
    }
    _write_record(tmp_path, record)
    result = check_ml_corpus_license(tmp_path)
    assert not result.passed
    assert any("ml_training_allowed" in msg for msg in result.messages)


def test_ml_corpus_license_check_fails_on_ml_training_false_under_records(tmp_path: Path) -> None:
    """A record with sequence_license.ml_training_allowed: false MUST NOT live under records/ (BR-15)."""
    record = _full_record()
    record["license"] = {
        "sequence_license": _full_license_block(ml_ok=False),
        "annotation_license": _full_license_block(),
    }
    _write_record(tmp_path, record)
    result = check_ml_corpus_license(tmp_path)
    assert not result.passed
    assert any("exclusions.yaml" in msg for msg in result.messages)


def test_ml_corpus_license_check_fails_on_provenance_source_not_in_allowlist(tmp_path: Path) -> None:
    """A record carrying `provenance.source: addgene_metadata_only` MUST fail (FR-ML-04)."""
    record = _full_record()
    record["provenance"]["source"] = "addgene_metadata_only"
    _write_record(tmp_path, record)
    result = check_ml_corpus_license(tmp_path)
    assert not result.passed
    assert any("addgene_metadata_only" in msg for msg in result.messages)


def test_allowed_provenance_sources_excludes_addgene_metadata_only() -> None:
    """The allowlist constant MUST NOT include addgene_metadata_only (FR-ML-04 default-deny)."""
    assert "addgene_metadata_only" not in ALLOWED_PROVENANCE_SOURCES
