"""
module_id: tests.engine.test_design_plan_t802
file: tests/engine/test_design_plan_t802.py
task_id: T-802
"""

from __future__ import annotations

import ast
from pathlib import Path

from domain.sequence import DnaSequence, MoleculeType, SequenceRecord, sha256_text
from domain.types.assembly_plan import AssemblyPlanSummary
from domain.types.ids import AssemblyMethodId
from domain.types.risk_advisory import RiskAdvisoryReport
from engine.design_plan import (
    DesignPlanGenerator,
    DesignPlanInput,
    design_plan_content_hash,
    render_json,
    render_markdown,
    render_pdf,
)

ROOT = Path(__file__).resolve().parents[2]


def test_generator_builds_non_operational_design_realisation_plan() -> None:
    report = _risk_report()
    request = DesignPlanInput(
        design_session_id="session-802",
        construct_id="construct-802",
        construct_version="1",
        assembly_plan=_assembly_plan(),
        primer_set=("vector_fwd", "vector_rev", "insert_fwd", "insert_rev"),
        biosafety_classification="BSL-2",
        extra_qc_checkpoints=("Confirm reviewer packet hash is archived",),
        institutional_approvals_required=("IBC notification before ordering",),
        validation_report_hashes=(str(sha256_text("validation-report")),),
        risk_advisory_report=report,
    )

    plan = DesignPlanGenerator().generate(request)

    assert plan.construct_id == "construct-802"
    assert plan.assembly_plan is request.assembly_plan
    assert plan.primer_set == request.primer_set
    assert "Confirm reviewer packet hash is archived" in plan.qc_checkpoints
    assert any(
        artefact.name == "Risk advisory report"
        for artefact in plan.expected_verification_artefacts
    )
    assert any("BSL-2" in approval for approval in plan.institutional_approvals_required)
    assert str(report.report_content_hash) in plan.reviewer_packet.evidence_hashes
    assert "Biosafety classification: BSL-2" in plan.reviewer_packet.summary


def test_renderers_are_deterministic_and_do_not_emit_operational_fields() -> None:
    plan = DesignPlanGenerator().generate(
        DesignPlanInput(
            design_session_id="session-802",
            construct_id="construct-802",
            construct_version="1",
            assembly_plan=_assembly_plan(),
            primer_set=("vector_fwd", "vector_rev"),
            biosafety_classification="BSL-1",
        )
    )

    json_text = render_json(plan)
    markdown = render_markdown(plan)
    pdf = render_pdf(plan)

    assert render_json(plan) == json_text
    assert design_plan_content_hash(plan) == design_plan_content_hash(plan)
    assert '"construct_id":"construct-802"' in json_text
    assert "Design Realisation Plan" in markdown
    assert "Assembly Route" in markdown
    assert "QC Checkpoints" in markdown
    assert pdf == render_pdf(plan)
    assert pdf.startswith(b"%PDF-1.4")
    assert b"/CreationDate" not in pdf
    assert "ProtocolStep" not in json_text
    assert "ProtocolStep" not in markdown
    assert b"ProtocolStep" not in pdf


def test_design_plan_engine_package_does_not_import_gated_namespace() -> None:
    design_plan_dir = ROOT / "src" / "engine" / "design_plan"
    offenders: list[str] = []
    for path in design_plan_dir.rglob("*.py"):
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
            if isinstance(node, ast.Name) and node.id == "ProtocolStep":
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _assembly_plan() -> AssemblyPlanSummary:
    return AssemblyPlanSummary(
        method=AssemblyMethodId("gibson"),
        fragments=("vector", "insert"),
        expected_product=SequenceRecord(
            id="construct-802-product",
            sequence=DnaSequence("ATGCGTACGTAG"),
            topology="linear",
            molecule_type=MoleculeType.DS_DNA,
        ),
        verification_checkpoints=("Review vector-insert junction",),
    )


def _risk_report() -> RiskAdvisoryReport:
    return RiskAdvisoryReport(
        design_session_id="session-802",
        construct_id="construct-802",
        construct_checksum=sha256_text("construct-802"),
        construct_version="1",
        report_content_hash=sha256_text("risk-report"),
        advisory_catalogue_version="risk-advisories-v1",
        advisory_catalogue_content_hash=sha256_text("risk-catalogue"),
        advisories=(),
    )
