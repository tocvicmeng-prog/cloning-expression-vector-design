"""
module_id: tests.adapter.catalogue.test_hosts_catalogue_t403
file: tests/adapter/catalogue/test_hosts_catalogue_t403.py
task_id: T-403
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from adapter.catalogue import find_citations, load_catalogue, schema_for_catalogue

ROOT = Path(__file__).resolve().parents[3]

ALLOWED_CHASSIS = {
    "bacterial",
    "yeast",
    "plant",
    "mammalian",
    "insect",
    "cell_free",
    "viral_or_phage",
}
ALLOWED_BIOSAFETY = {"BSL-1", "BSL-2", "BSL-2+", "BSL-3", "BSL-4"}
SENTINEL_IDS = {
    "host.ecoli_dh5alpha",
    "host.ecoli_pir_plus",
    "host.ecoli_bl21_de3",
    "host.ecoli_lemo21_de3",
    "host.cell_free_pure",
    "host.scerevisiae_by4741",
    "host.kphaffii_gs115",
    "host.mammalian_hek293t",
    "host.mammalian_cho_dg44",
    "host.mammalian_h1_hesc",
    "host.insect_sf9",
    "host.plant_n_benthamiana",
    "host.phage_vlp_ecoli_ms2",
}


def _host_items() -> list[dict[str, object]]:
    document = load_catalogue(
        ROOT / "catalogues" / "hosts.yaml",
        schema_for_catalogue(ROOT / "catalogues" / "hosts.yaml", ROOT / "schemas"),
    )
    items = document.payload["items"]
    assert isinstance(items, list)
    return items


def test_t403_hosts_catalogue_replaces_seed_and_covers_all_chassis_classes() -> None:
    items = _host_items()
    ids = {str(item["id"]) for item in items}
    chassis_counts = Counter(str(item["chassis_class"]) for item in items)

    assert "host.seed" not in ids
    assert len(items) >= 60
    assert ids >= SENTINEL_IDS
    assert set(chassis_counts) == ALLOWED_CHASSIS
    assert chassis_counts["bacterial"] >= 20
    assert chassis_counts["mammalian"] >= 15
    assert chassis_counts["yeast"] >= 10


def test_t403_every_host_has_required_metadata_and_citation_traceability() -> None:
    for item in _host_items():
        assert str(item["id"]).startswith("host.")
        assert str(item["name"]).strip()
        assert item["chassis_class"] in ALLOWED_CHASSIS
        assert item["biosafety_tier"] in ALLOWED_BIOSAFETY
        assert item["source_section"] == "6"
        for list_field in ("host_roles", "replicons_supported", "expression_features"):
            value = item[list_field]
            assert isinstance(value, list)
            assert value
        assert str(item["genotype"]).strip()
        assert str(item["supplier_reference"]).strip()
        assert str(item["codon_usage_table_id"]).strip()
        assert str(item["growth_conditions"]).strip()
        citation = item["citation"]
        assert isinstance(citation, dict)
        # v0.2 (T-411, T-408a): a host citation is acceptable if it carries EITHER a
        # KB-document URL anchor (the v0.1.0 form, shared via *cite_*_hosts presets) OR
        # a PMID anchor (the v0.2 form, used for primary-lit-cited new strain records
        # such as Origami(DE3) Bessette 1999, BL21(DE3) Studier 1986, AH109 James 1996).
        # KB-anchored citations must still surface source_registry_ids for traceability.
        url = str(citation.get("url", ""))
        pmid = str(citation.get("pmid", "")).strip()
        kb_anchored = "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#18" in url
        primary_lit_anchored = bool(pmid)
        assert kb_anchored or primary_lit_anchored, (
            f"host {item['id']}: citation must carry either KB-URL anchor or PMID anchor"
        )
        if kb_anchored:
            assert citation.get("source_registry_ids"), (
                f"host {item['id']}: KB-anchored citation must list source_registry_ids"
            )
        maintenance = item["maintenance"]
        assert isinstance(maintenance, dict)
        assert maintenance["review_required_after"] == "2026-11-14"


def test_t403_every_host_has_a_discoverable_release_grade_citation() -> None:
    document = load_catalogue(
        ROOT / "catalogues" / "hosts.yaml",
        ROOT / "schemas" / "hosts.schema.json",
    )
    items = document.payload["items"]
    assert isinstance(items, list)
    citations = find_citations(document.payload)

    assert len(citations) >= len(items)
    assert {citation["grade"] for citation in citations} <= {"A1", "A2", "A3", "B1", "B2"}
