"""
module_id: tests.engine.test_vlp_policy_t807
file: tests/engine/test_vlp_policy_t807.py
task_id: T-807
"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

from adapter.catalogue import load_catalogue, schema_for_catalogue
from domain.sequence import sha256_text
from domain.types.controls import ControlKind
from engine.risk_classification import (
    RiskAdvisoryCatalogue,
    RiskClassificationEngine,
    RiskClassificationInput,
)
from engine.vlp_policy import (
    MS_RULE_IDS,
    VlpPolicyEngine,
    VlpPolicyRequest,
    VlpSystemClass,
    evaluate_vlp_policy,
)

ROOT = Path(__file__).resolve().parents[2]


def test_ms2_rna_display_policy_passes_and_triggers_risk_advisory_tags() -> None:
    request = VlpPolicyRequest(
        construct_id="ms2-display",
        system_class=VlpSystemClass.MS2_RNA_DISPLAY,
        cargo_size_nt=1200,
        vector_features=(
            "single-chain-dimer",
            "ab-loop-tolerated",
            "v75e-a81g-declared",
            "consensus-residues-preserved",
        ),
        packaging_signals=("ms2-pac",),
        capsid_components=("ms2 coat protein",),
        control_kinds=(
            ControlKind.POSITIVE,
            ControlKind.NEGATIVE,
            ControlKind.PROCESS,
            ControlKind.VEHICLE,
        ),
        validation_readouts=("SEC", "TEM"),
        coat_variant_declared=True,
        coat_reference_checksum="sha256:ms2-coat-reference",
        pac_hairpin_copy_number=1,
    )

    report = evaluate_vlp_policy(request)

    assert report.passed
    assert report.findings == ()
    assert {"MS2", "VLP", "delivery_vehicle"} <= set(report.risk_trigger_tags)
    assert str(report.content_hash())
    assert report.content_hash() == evaluate_vlp_policy(request).content_hash()

    risk_report = _risk_engine().classify(
        RiskClassificationInput(
            design_session_id="session-ms2",
            construct_id=request.construct_id,
            construct_checksum=sha256_text("ms2-display"),
            construct_version="1",
            trigger_tags=report.risk_trigger_tags,
        )
    )
    assert "risk.ms2_vlp_delivery" in {advisory.advisory_id for advisory in risk_report.advisories}


def test_ms2_missing_reference_and_pac_declarations_blocks_ms_rules() -> None:
    report = evaluate_vlp_policy(
        VlpPolicyRequest(
            construct_id="ms2-incomplete",
            system_class=VlpSystemClass.MS2_RNA_DISPLAY,
            cargo_size_nt=900,
            vector_features=("single-chain-dimer",),
            packaging_signals=(),
            control_kinds=(ControlKind.POSITIVE, ControlKind.NEGATIVE),
            validation_readouts=(),
        )
    )

    assert not report.passed
    assert {"MS-01", "MS-02", "MS-03"} <= report.blocked_rule_ids
    assert {"MS-07", "VLP-CONTROLS"} <= report.advisory_rule_ids
    assert "BlockOperationalProtocol" in report.blocked_gates


def test_phage_derived_vlp_family_mismatch_requires_override() -> None:
    base = VlpPolicyRequest(
        construct_id="qbeta-vlp",
        system_class=VlpSystemClass.PHAGE_DERIVED_VLP,
        cargo_size_nt=1600,
        phage_family="qbeta",
        packaging_signals=("ms2-pac", "qbeta-pac"),
        capsid_components=("qbeta coat",),
        control_kinds=(
            ControlKind.POSITIVE,
            ControlKind.NEGATIVE,
            ControlKind.PROCESS,
            ControlKind.VEHICLE,
        ),
        validation_readouts=("native PAGE metadata",),
    )

    assert "MS-04" in evaluate_vlp_policy(base).advisory_rule_ids
    overridden = replace(
        base,
        orthogonality_override="documented orthogonal pac/hairpin pairing",
    )
    assert "MS-04" not in evaluate_vlp_policy(overridden).triggered_rule_ids


def test_aav_policy_enforces_itr_capacity_and_helper_separation() -> None:
    report = evaluate_vlp_policy(
        VlpPolicyRequest(
            construct_id="aav-overfull",
            system_class=VlpSystemClass.AAV,
            cargo_size_nt=5100,
            packaging_signals=(),
            vector_features=("rep",),
            helper_components=(),
            control_kinds=(ControlKind.POSITIVE, ControlKind.NEGATIVE, ControlKind.PROCESS),
            validation_readouts=("transfer vector integrity",),
        )
    )

    assert not report.passed
    assert {
        "VLP-AAV-ITR",
        "VLP-CAPACITY",
        "VLP-HELPER-SEPARATION",
    } <= report.blocked_rule_ids
    assert "VLP-CONTROLS" in report.advisory_rule_ids
    assert {"AAV", "viral_vector", "packaging"} <= set(report.risk_trigger_tags)


def test_lentiviral_policy_blocks_replication_competence_and_triggers_risk() -> None:
    report = evaluate_vlp_policy(
        VlpPolicyRequest(
            construct_id="lenti-risk",
            system_class=VlpSystemClass.LENTIVIRAL,
            cargo_size_nt=8500,
            packaging_signals=("LTR", "psi"),
            helper_components=("gag-pol", "env"),
            control_kinds=(
                ControlKind.POSITIVE,
                ControlKind.NEGATIVE,
                ControlKind.PROCESS,
                ControlKind.VEHICLE,
            ),
            validation_readouts=("particle titer",),
            replication_competent=True,
        )
    )

    assert not report.passed
    assert report.blocked_rule_ids == frozenset({"MS-06"})
    assert {"lentiviral", "viral_vector", "replication_competent"} <= set(report.risk_trigger_tags)

    risk_report = _risk_engine().classify(
        RiskClassificationInput(
            design_session_id="session-lenti",
            construct_id="lenti-risk",
            construct_checksum=sha256_text("lenti-risk"),
            construct_version="1",
            trigger_tags=report.risk_trigger_tags,
            replication_competent=True,
        )
    )
    assert {
        "risk.lentiviral_or_aav_packaging",
        "risk.replication_competent_viral_vector",
    } <= {advisory.advisory_id for advisory in risk_report.advisories}


def test_vlp_policy_ms_rule_ids_are_backed_by_rule_catalogue() -> None:
    payload = _catalogue("rules/MS.yaml")
    rules = payload["rules"]
    assert isinstance(rules, list)
    catalogue_rule_ids = {str(rule["rule_id"]) for rule in rules if isinstance(rule, dict)}

    assert VlpPolicyEngine().supported_ms_rule_ids == MS_RULE_IDS
    assert catalogue_rule_ids == MS_RULE_IDS


def test_vlp_policy_package_does_not_import_gated_namespace() -> None:
    package_dir = ROOT / "src" / "engine" / "vlp_policy"
    offenders: list[str] = []
    for path in package_dir.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (
                node.module is not None and node.module.startswith("domain.types.sop_protected")
            ):
                offenders.append(str(path.relative_to(ROOT)))
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("domain.types.sop_protected"):
                        offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _catalogue(relative_path: str) -> dict[str, object]:
    path = ROOT / "catalogues" / relative_path
    return load_catalogue(path, schema_for_catalogue(path, ROOT / "schemas")).payload


def _risk_engine() -> RiskClassificationEngine:
    payload = _catalogue("risk_advisories.yaml")
    return RiskClassificationEngine(RiskAdvisoryCatalogue.from_payload(payload))
