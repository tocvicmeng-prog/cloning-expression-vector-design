"""
module_id: tests.engine.test_risk_classification_t801
file: tests/engine/test_risk_classification_t801.py
task_id: T-801
"""

from __future__ import annotations

from pathlib import Path

from adapter.catalogue import load_catalogue, schema_for_catalogue
from domain.sequence import sha256_text
from domain.types.risk_advisory import RiskAdvisorySeverity
from engine.risk_classification import (
    RiskAdvisoryCatalogue,
    RiskClassificationEngine,
    RiskClassificationInput,
)

ROOT = Path(__file__).resolve().parents[2]


def test_risk_classification_generates_active_report_from_catalogue() -> None:
    report = _engine().classify(
        RiskClassificationInput(
            design_session_id="session-1",
            construct_id="construct-1",
            construct_checksum=sha256_text("construct-sequence"),
            construct_version="1.0.0",
            biosafety_tier="BSL-4",
            cargo_classes=("MS2",),
            external_export=True,
            antibiotic_resistance_marker=True,
        )
    )

    advisory_ids = tuple(advisory.advisory_id for advisory in report.advisories)
    assert {
        "risk.rg2_or_higher_component",
        "risk.ms2_vlp_delivery",
        "risk.unsupported_bsl4",
    } <= set(advisory_ids)
    assert advisory_ids.index("risk.unsupported_bsl4") < advisory_ids.index(
        "risk.ms2_vlp_delivery"
    )
    assert "risk.antibiotic_resistance_marker_export" in advisory_ids
    assert report.required_acknowledgements() >= {
        "risk.ms2_vlp_delivery",
        "risk.unsupported_bsl4",
    }
    assert str(report.report_content_hash)
    assert str(report.advisory_catalogue_content_hash)


def test_inferred_screening_and_provenance_tags_trigger_expected_advisories() -> None:
    report = _engine().classify(
        RiskClassificationInput(
            design_session_id="session-2",
            construct_id="construct-2",
            construct_checksum=sha256_text("watchlist"),
            construct_version="2",
            screening_verdict="watchlist",
            missing_provenance=True,
            ai_evasion_watch=True,
        )
    )

    by_id = {advisory.advisory_id: advisory for advisory in report.advisories}
    assert by_id["risk.select_agent_or_pathogen_homology"].severity is (
        RiskAdvisorySeverity.STRONG_CAUTION
    )
    assert by_id["risk.component_lineage_untrusted"].severity is RiskAdvisorySeverity.CAUTION
    assert by_id["risk.ai_screening_evasion_watch"].severity is RiskAdvisorySeverity.CAUTION


def test_report_hash_is_deterministic_and_bound_to_construct_version() -> None:
    engine = _engine()
    base_request = RiskClassificationInput(
        design_session_id="session-3",
        construct_id="construct-3",
        construct_checksum=sha256_text("same"),
        construct_version="1",
        trigger_tags=("VLP", "MS2"),
    )
    reordered_request = RiskClassificationInput(
        design_session_id="session-3",
        construct_id="construct-3",
        construct_checksum=sha256_text("same"),
        construct_version="1",
        trigger_tags=("MS2", "VLP"),
    )
    changed_request = RiskClassificationInput(
        design_session_id="session-3",
        construct_id="construct-3",
        construct_checksum=sha256_text("changed"),
        construct_version="1",
        trigger_tags=("MS2", "VLP"),
    )

    assert engine.classify(base_request).report_content_hash == (
        engine.classify(reordered_request).report_content_hash
    )
    assert engine.classify(base_request).report_content_hash != (
        engine.classify(changed_request).report_content_hash
    )


def test_clean_construct_produces_empty_report_with_stable_hash() -> None:
    request = RiskClassificationInput(
        design_session_id="session-clean",
        construct_id="construct-clean",
        construct_checksum=sha256_text("clean"),
        construct_version="1",
    )
    report = _engine().classify(request)

    assert report.advisories == ()
    assert report.required_acknowledgements() == frozenset()
    assert str(report.report_content_hash)


def _engine() -> RiskClassificationEngine:
    path = ROOT / "catalogues" / "risk_advisories.yaml"
    payload = load_catalogue(path, schema_for_catalogue(path, ROOT / "schemas")).payload
    return RiskClassificationEngine(RiskAdvisoryCatalogue.from_payload(payload))
