"""
module_id: tests.adapter.catalogue.test_parts_catalogue_t402
file: tests/adapter/catalogue/test_parts_catalogue_t402.py
task_id: T-402
"""

from __future__ import annotations

from pathlib import Path

from adapter.catalogue import find_citations, load_catalogue, schema_for_catalogue

ROOT = Path(__file__).resolve().parents[3]

EXPECTED_SECTIONS = {f"5.{index}" for index in range(1, 14)}
ALLOWED_CHASSIS = {
    "bacterial",
    "yeast",
    "plant",
    "mammalian",
    "insect",
    "cell_free",
    "viral_or_phage",
}
SENTINEL_IDS = {
    "origin.cole1_pbr322",
    "origin.hiv_sin_ltr",
    "marker.ampicillin_bla",
    "marker.negative_selection_sacb",
    "promoter.t7",
    "promoter.cmv_hcmv_ie",
    "promoter.polyhedrin",
    "rbs.shine_dalgarno_consensus",
    "kozak.consensus",
    "terminator.rrnb_t1t2",
    "polya.bgh",
    "tag.his6",
    "cleavage.tev",
    "signal.pelb",
    "reporter.egfp",
    "reporter.nanoluc",
    "recombinase.cre_lox",
    "crispr.grna_spcas9_standard_scaffold",
    "inducible.tet_on_3g_tre3g",
}


def _parts_items() -> list[dict[str, object]]:
    document = load_catalogue(
        ROOT / "catalogues" / "parts.yaml",
        schema_for_catalogue(ROOT / "catalogues" / "parts.yaml", ROOT / "schemas"),
    )
    items = document.payload["items"]
    assert isinstance(items, list)
    return items


def test_t402_parts_catalogue_covers_kb_sections_5_1_to_5_13() -> None:
    items = _parts_items()
    ids = {str(item["id"]) for item in items}

    assert "part.seed" not in ids
    assert len(items) >= 160
    assert {str(item["source_section"]) for item in items} == EXPECTED_SECTIONS
    assert ids >= SENTINEL_IDS


def test_t402_every_part_has_required_traceability_and_host_metadata() -> None:
    for item in _parts_items():
        assert str(item["id"]).strip()
        assert str(item["name"]).strip()
        assert str(item["role"]).startswith("SO:")
        assert str(item["role_label"]).strip()
        assert str(item["licence"]).strip()
        assert str(item["provenance"]).startswith("KB v2.0 section 5.")
        host_compatibility = item["host_compatibility"]
        assert isinstance(host_compatibility, list)
        assert set(host_compatibility) <= ALLOWED_CHASSIS
        citation = item["citation"]
        assert isinstance(citation, dict)
        assert "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#18" in str(
            citation["url"]
        )
        assert citation.get("source_registry_ids")
        maintenance = item["maintenance"]
        assert isinstance(maintenance, dict)
        assert maintenance["review_required_after"] == "2026-11-14"


def test_t402_every_part_has_a_discoverable_release_grade_citation() -> None:
    document = load_catalogue(
        ROOT / "catalogues" / "parts.yaml",
        ROOT / "schemas" / "parts.schema.json",
    )
    citations = find_citations(document.payload)
    items = document.payload["items"]
    assert isinstance(items, list)

    assert len(citations) >= len(items)
    assert {citation["grade"] for citation in citations} <= {"A1", "A2", "A3", "B1", "B2"}
