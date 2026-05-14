"""
module_id: tests.adapter.catalogue.test_enzymes_catalogue_t404
file: tests/adapter/catalogue/test_enzymes_catalogue_t404.py
task_id: T-404
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from adapter.catalogue import find_citations, load_catalogue, schema_for_catalogue

ROOT = Path(__file__).resolve().parents[3]

SENTINEL_ENZYMES = {
    "enzyme.re.ecori",
    "enzyme.re.noti",
    "enzyme.type_iis.bsai",
    "enzyme.type_iis.paqci",
    "enzyme.toolkit.t4_dna_ligase",
    "enzyme.toolkit.q5",
    "enzyme.toolkit.t5_exonuclease",
    "enzyme.toolkit.dpni",
    "enzyme.protease.tev",
    "enzyme.protease.sumo_ulp1",
}


def _enzyme_document() -> dict[str, object]:
    return load_catalogue(
        ROOT / "catalogues" / "enzymes.yaml",
        schema_for_catalogue(ROOT / "catalogues" / "enzymes.yaml", ROOT / "schemas"),
    ).payload


def _buffer_document() -> dict[str, object]:
    return load_catalogue(
        ROOT / "catalogues" / "enzyme_buffer_compat.yaml",
        schema_for_catalogue(ROOT / "catalogues" / "enzyme_buffer_compat.yaml", ROOT / "schemas"),
    ).payload


def test_t404_enzyme_catalogue_replaces_seed_and_covers_required_classes() -> None:
    items = _enzyme_document()["items"]
    assert isinstance(items, list)
    ids = {str(item["id"]) for item in items}
    class_counts = Counter(str(item["enzyme_class"]) for item in items)

    assert "enzyme.seed" not in ids
    assert len(items) >= 65
    assert ids >= SENTINEL_ENZYMES
    assert class_counts["type_ii_restriction"] >= 40
    assert class_counts["type_iis_restriction"] >= 6
    toolkit_classes = (
        "ligase",
        "kinase",
        "polymerase",
        "exonuclease",
        "restriction",
        "phosphatase",
        "glycosylase_mix",
    )
    assert sum(class_counts[name] for name in toolkit_classes) >= 12
    assert class_counts["protease"] >= 7


def test_t404_every_enzyme_has_required_metadata_and_release_grade_citation() -> None:
    items = _enzyme_document()["items"]
    assert isinstance(items, list)
    for item in items:
        assert str(item["id"]).startswith("enzyme.")
        assert str(item["name"]).strip()
        assert str(item["recognition_site"]).strip()
        assert str(item["cut_offset"]).strip()
        assert str(item["overhang"]).strip()
        assert str(item["methylation_sensitivity"]).strip()
        assert isinstance(item["use_cases"], list)
        assert item["use_cases"]
        citation = item["citation"]
        assert isinstance(citation, dict)
        assert citation["grade"] in {"A1", "A2", "A3", "B1", "B2"}
        assert citation.get("source_registry_ids")
        maintenance = item["maintenance"]
        assert isinstance(maintenance, dict)
        assert maintenance["review_required_after"] == "2026-11-14"


def test_t404_buffer_matrix_covers_every_enzyme_id() -> None:
    enzyme_items = _enzyme_document()["items"]
    assert isinstance(enzyme_items, list)
    enzyme_ids = {str(item["id"]) for item in enzyme_items}
    buffer_document = _buffer_document()
    buffers = buffer_document["buffers"]
    compatibility = buffer_document["compatibility"]
    assert isinstance(buffers, list)
    assert isinstance(compatibility, list)
    buffer_ids = {str(buffer["id"]) for buffer in buffers}
    covered_ids = {
        str(enzyme_id)
        for row in compatibility
        if isinstance(row, dict)
        for enzyme_id in row["enzyme_ids"]
    }

    assert len(buffers) >= 10
    assert enzyme_ids <= covered_ids
    assert all(
        str(row["buffer_id"]) in buffer_ids for row in compatibility if isinstance(row, dict)
    )
    assert find_citations(buffer_document)
