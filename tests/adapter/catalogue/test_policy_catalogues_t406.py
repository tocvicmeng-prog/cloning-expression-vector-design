"""
module_id: tests.adapter.catalogue.test_policy_catalogues_t406
file: tests/adapter/catalogue/test_policy_catalogues_t406.py
task_id: T-406
"""

from __future__ import annotations

from pathlib import Path

from adapter.catalogue import find_citations, load_catalogue, schema_for_catalogue
from tools.ci_gates.source_grade_citation_check import check_citations
from tools.ci_gates.stale_catalogue_check import check_catalogues

ROOT = Path(__file__).resolve().parents[3]
VENDOR_FILES = ("twist.yaml", "idt.yaml", "genscript.yaml")


def _catalogue(relative_path: str) -> dict[str, object]:
    path = ROOT / "catalogues" / relative_path
    return load_catalogue(path, schema_for_catalogue(path, ROOT / "schemas")).payload


def _items_by_id(items: object) -> dict[str, dict[str, object]]:
    assert isinstance(items, list)
    indexed: dict[str, dict[str, object]] = {}
    for item in items:
        assert isinstance(item, dict)
        indexed[str(item["id"])] = item
    return indexed


def _int_value(value: object) -> int:
    assert isinstance(value, int)
    return value


def test_t406_vendor_profiles_cover_required_vendors_and_synthesis_limits() -> None:
    vendors = {
        str(_catalogue(f"vendor_profiles/{filename}")["vendor_id"]): _catalogue(
            f"vendor_profiles/{filename}"
        )
        for filename in VENDOR_FILES
    }

    assert set(vendors) == {"twist", "idt", "genscript"}
    for vendor in vendors.values():
        assert vendor["screening_protocol"] == "igsc_v3"
        submission_policy = vendor["submission_policy"]
        assert isinstance(submission_policy, dict)
        assert submission_policy["direct_order_supported_by_platform"] is False
        assert set(submission_policy["order_blocking_verdicts"]) == {
            "watchlist",
            "hit",
            "unavailable",
        }
        services = _items_by_id(vendor["services"])
        for service in services.values():
            assert _int_value(service["min_bp"]) < _int_value(service["max_bp"])
            constraints = service["sequence_constraints"]
            assert isinstance(constraints, dict)
            assert _int_value(constraints["direct_repeat_warn_bp"]) < _int_value(
                constraints["direct_repeat_block_bp"]
            )

    twist_services = _items_by_id(vendors["twist"]["services"])
    assert twist_services["twist.gene_fragment"]["min_bp"] == 300
    assert twist_services["twist.gene_fragment"]["max_bp"] == 5000

    idt_services = _items_by_id(vendors["idt"]["services"])
    assert idt_services["idt.gblocks"]["min_bp"] == 125
    assert idt_services["idt.gblocks"]["max_bp"] == 3000

    genscript_services = _items_by_id(vendors["genscript"]["services"])
    assert _int_value(genscript_services["genscript.premium_gene"]["max_bp"]) >= 200000


def test_t406_screening_trust_policy_encodes_provider_and_verdict_defaults() -> None:
    policy = _catalogue("screening_trust_policy.yaml")
    scope = policy["screening_scope"]
    verdict_policy = policy["verdict_policy"]
    providers = _items_by_id(policy["providers"])

    assert isinstance(scope, dict)
    assert scope["minimum_synthetic_na_nt"] == 200
    assert scope["screen_assembled_product"] is True
    assert scope["preserve_query_privacy_when_supported"] is True
    assert set(providers) == {
        "igsc_v3",
        "ibbis_common_mechanism",
        "securedna",
        "institutional_blacklist",
    }
    assert providers["securedna"]["query_privacy_mode"] == "cryptographically_blinded"

    assert isinstance(verdict_policy, dict)
    assert verdict_policy["clear"]["vendor_submission_allowed"] is True
    for verdict in ("watchlist", "hit", "unavailable"):
        action = verdict_policy[verdict]
        assert "BlockVendorSubmission" in action["blocks"]
        assert action["requires_reviewer"] is True
        assert action["vendor_submission_allowed"] is False


def test_t406_institutional_policy_blocks_self_elevation_and_unsupported_tiers() -> None:
    policy = _catalogue("institutional_policy.yaml")
    defaults = policy["defaults"]
    advisory = policy["advisory_acknowledgement"]

    assert isinstance(defaults, dict)
    assert defaults["administrator_controlled_authorisation"] is True
    assert defaults["user_self_authorisation_allowed"] is False
    assert defaults["reviewer_can_mutate_authorisation_profile"] is False
    assert defaults["administrator_can_act_as_reviewer"] is True
    assert defaults["unsupported_biosafety_tiers"] == ["BSL-4"]
    assert set(defaults["unsupported_tier_blocks"]) == {
        "BlockCompile",
        "BlockOperationalProtocol",
        "BlockVendorSubmission",
    }

    assert isinstance(advisory, dict)
    assert advisory["passive_dismissal_allowed"] is False
    assert set(advisory["severities_requiring_signed_acknowledgement"]) == {
        "caution",
        "strong_caution",
    }


def test_t406_export_profiles_preserve_required_redaction_boundaries() -> None:
    profiles = _items_by_id(_catalogue("export_profiles.yaml")["profiles"])

    assert set(profiles) == {
        "export.internal_audit",
        "export.vendor_submission",
        "export.public_share_redacted",
        "export.regulatory_review",
    }
    assert profiles["export.internal_audit"]["include_authorisation_trace"] is True
    assert profiles["export.internal_audit"]["include_screening_evidence"] is True
    assert profiles["export.vendor_submission"]["include_authorisation_trace"] is False
    assert profiles["export.vendor_submission"]["include_vendor_quote_payload"] is True
    assert profiles["export.public_share_redacted"]["redaction_level"] == "strong"


def test_t406_risk_advisories_require_active_acknowledgement() -> None:
    catalogue = _catalogue("risk_advisories.yaml")
    policy = catalogue["acknowledgement_policy"]
    advisories = _items_by_id(catalogue["advisories"])

    assert isinstance(policy, dict)
    assert policy["passive_dismissal_allowed"] is False
    assert set(policy["severities_requiring_signed_acknowledgement"]) == {
        "caution",
        "strong_caution",
    }
    assert len(advisories) >= 10
    assert {
        "risk.unsupported_bsl4",
        "risk.ms2_vlp_delivery",
        "risk.ai_screening_evasion_watch",
        "risk.select_agent_or_pathogen_homology",
    } <= set(advisories)

    for advisory in advisories.values():
        if advisory["severity"] in {"caution", "strong_caution"}:
            assert advisory["blocks"]
            assert advisory["recommended_action"]


def test_t406_policy_catalogues_validate_and_have_release_grade_citations() -> None:
    for relative_path in (
        "screening_trust_policy.yaml",
        "institutional_policy.yaml",
        "export_profiles.yaml",
        "risk_advisories.yaml",
        "vendor_profiles/twist.yaml",
        "vendor_profiles/idt.yaml",
        "vendor_profiles/genscript.yaml",
    ):
        document = _catalogue(relative_path)
        assert find_citations(document)

    assert check_catalogues(ROOT).passed
    assert check_citations(ROOT).passed
