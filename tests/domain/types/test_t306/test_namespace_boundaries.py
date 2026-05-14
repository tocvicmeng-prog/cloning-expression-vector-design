"""
module_id: tests.domain.types.t306
file: tests/domain/types/test_t306/test_namespace_boundaries.py
task_id: T-306
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import cast

import pytest

from domain.security import OperationalRole, PrincipalId, SecurityRole
from domain.sequence import DnaSequence, MoleculeType, SequenceRecord, Sha256, sha256_text
from domain.types import AssemblyMethodId
from domain.types.assembly_plan import AssemblyPlanSummary
from domain.types.citation import GradedCitation
from domain.types.controls import ControlDesign, ControlKind, ControlSet
from domain.types.design_plan import DesignRealisationPlan, ReviewerPacket, VerificationArtefact
from domain.types.governance import DecisionRecord, RoleSnapshot
from domain.types.risk_advisory import (
    AdvisoryAcknowledgementDecision,
    RiskAdvisory,
    RiskAdvisoryAcknowledgement,
    RiskAdvisoryReport,
    RiskAdvisorySeverity,
)
from domain.types.sop_protected import (
    DeviationPolicy,
    HazardClass,
    ProtocolDAG,
    ProtocolEdge,
    ProtocolEdgeKind,
    ProtocolStep,
    SopLinkedProtocol,
)

ROOT = Path(__file__).resolve().parents[4]
NOW = datetime(2026, 5, 14, tzinfo=UTC)


def _sequence_record() -> SequenceRecord:
    return SequenceRecord(
        id="product",
        sequence=DnaSequence("ACGT"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )


def _assembly_plan() -> AssemblyPlanSummary:
    return AssemblyPlanSummary(
        method=AssemblyMethodId("summary"),
        fragments=("backbone", "insert"),
        expected_product=_sequence_record(),
    )


def _protocol_step(
    step_id: str = "step-1", successors: tuple[ProtocolEdge, ...] = ()
) -> ProtocolStep:
    return ProtocolStep(
        step_id=step_id,
        action="Follow institutional SOP",
        reagents=("fixture reagent",),
        quantities=("institutional SOP governed",),
        temperature_c=None,
        duration=None,
        rationale="Operational detail is institution-controlled.",
        safety_note=None,
        successors=successors,
        sop_ref="SOP-001",
        approval_gate="OperationalProtocolAuthorised",
        hazard_class=HazardClass.BSL1,
        allowed_roles=frozenset({OperationalRole.CLONING_OPERATOR}),
        checkpoint_criteria=("checkpoint",),
        measured_outputs=("output",),
        deviation_policy=DeviationPolicy(allowed=False, escalation_contact="admin@example.org"),
        decision_rule=None,
    )


def _decision_record() -> DecisionRecord:
    snapshot = RoleSnapshot(
        principal_id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution_id="inst",
        captured_at_utc=NOW,
        credentials_verified_at_utc=NOW,
    )
    return DecisionRecord(
        decision_id="decision-1",
        decision_type="advisory_acknowledgement",
        role_snapshot=snapshot,
        profile_content_hash=Sha256("sha256:profile"),
        policy_version="policy-v1",
        signed_payload_hash=Sha256("sha256:payload"),
        signature_bytes=b"signature",
        signed_at_utc=NOW,
    )


def test_design_plan_is_valid_without_sop_protected_values() -> None:
    plan = DesignRealisationPlan(
        construct_id="construct-1",
        assembly_plan=_assembly_plan(),
        primer_set=("primer-a", "primer-b"),
        qc_checkpoints=("sequence junctions",),
        expected_verification_artefacts=(
            VerificationArtefact(name="GenBank", description="Annotated map"),
        ),
        institutional_approvals_required=("IBC review may be required",),
        reviewer_packet=ReviewerPacket(
            summary="Review packet", evidence_hashes=("sha256:evidence",)
        ),
    )

    assert plan.construct_id == "construct-1"


def test_design_plan_runtime_guard_rejects_sop_protected_value() -> None:
    step = _protocol_step()

    with pytest.raises(TypeError, match="sop_protected"):
        DesignRealisationPlan(
            construct_id="construct-1",
            assembly_plan=_assembly_plan(),
            primer_set=("primer-a",),
            qc_checkpoints=("qc",),
            expected_verification_artefacts=cast(tuple[VerificationArtefact, ...], (step,)),
            institutional_approvals_required=(),
            reviewer_packet=ReviewerPacket(summary="Review packet", evidence_hashes=()),
        )


def test_design_plan_package_does_not_import_sop_protected_namespace() -> None:
    design_plan_dir = ROOT / "src" / "domain" / "types" / "design_plan"
    offenders = [
        path.name
        for path in design_plan_dir.glob("*.py")
        if path.name != "guard.py"
        and "domain.types.sop_protected" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_control_set_requires_positive_and_negative_controls() -> None:
    positive = ControlDesign(
        control_id="positive",
        kind=ControlKind.POSITIVE,
        purpose="Assay sensitivity",
        expected_observation="signal",
    )
    negative = ControlDesign(
        control_id="negative",
        kind=ControlKind.NEGATIVE,
        purpose="Background",
        expected_observation="no signal",
    )

    assert ControlSet(construct_id="construct-1", controls=(positive, negative))

    with pytest.raises(ValueError, match="negative"):
        ControlSet(construct_id="construct-1", controls=(positive,))


def test_protocol_dag_orders_steps_and_rejects_cycles() -> None:
    first = _protocol_step("step-1", successors=(ProtocolEdge("step-2", ProtocolEdgeKind.THEN),))
    second = _protocol_step("step-2")
    dag = ProtocolDAG(root="step-1", steps=(second, first))

    assert dag.canonical_step_ids == ("step-1", "step-2")
    assert SopLinkedProtocol(
        construct_id="construct-1",
        protocol_dag=dag,
        sop_template_id="template-1",
        authorisation_event_id="event-1",
    )

    cycle_a = _protocol_step("a", successors=(ProtocolEdge("b", ProtocolEdgeKind.THEN),))
    cycle_b = _protocol_step("b", successors=(ProtocolEdge("a", ProtocolEdgeKind.THEN),))
    with pytest.raises(ValueError, match="cycles"):
        ProtocolDAG(root="a", steps=(cycle_a, cycle_b))


def test_risk_advisory_report_identifies_required_acknowledgements() -> None:
    citation = GradedCitation(
        text="Fixture source",
        grade="A1",
        accessed=date(2026, 5, 14),
        doi="10.0000/example",
    )
    info = RiskAdvisory(
        advisory_id="ADV-INFO",
        severity=RiskAdvisorySeverity.INFO,
        category="context",
        message="Informational advisory",
        citation=citation,
    )
    caution = RiskAdvisory(
        advisory_id="ADV-CAUTION",
        severity=RiskAdvisorySeverity.CAUTION,
        category="biosafety",
        message="Requires acknowledgement",
        citation=citation,
    )
    report = RiskAdvisoryReport(
        design_session_id="session-1",
        construct_id="construct-1",
        construct_checksum=sha256_text("ACGT"),
        construct_version="1.0.0",
        report_content_hash=Sha256("sha256:report"),
        advisory_catalogue_version="v1",
        advisory_catalogue_content_hash=Sha256("sha256:catalogue"),
        advisories=(info, caution),
    )

    assert report.required_acknowledgements() == frozenset({"ADV-CAUTION"})


def test_advisory_acknowledgement_requires_substantive_justification() -> None:
    with pytest.raises(ValueError, match="20 characters"):
        RiskAdvisoryAcknowledgement(
            advisory_id="ADV-1",
            report_content_hash=Sha256("sha256:report"),
            construct_checksum=Sha256("sha256:construct"),
            decision=AdvisoryAcknowledgementDecision.ACKNOWLEDGED,
            justification="too short",
            decision_record=_decision_record(),
            acknowledged_at_utc=NOW,
        )

    acknowledgement = RiskAdvisoryAcknowledgement(
        advisory_id="ADV-1",
        report_content_hash=Sha256("sha256:report"),
        construct_checksum=Sha256("sha256:construct"),
        decision=AdvisoryAcknowledgementDecision.ACKNOWLEDGED,
        justification="Reviewed by administrator with institutional context.",
        decision_record=_decision_record(),
        acknowledged_at_utc=NOW,
    )

    assert acknowledgement.decision_record.decision_id == "decision-1"


def test_governance_decision_record_requires_signature() -> None:
    with pytest.raises(ValueError, match="signature"):
        DecisionRecord(
            decision_id="decision-1",
            decision_type="advisory_acknowledgement",
            role_snapshot=_decision_record().role_snapshot,
            profile_content_hash=Sha256("sha256:profile"),
            policy_version="policy-v1",
            signed_payload_hash=Sha256("sha256:payload"),
            signature_bytes=b"",
            signed_at_utc=NOW,
        )
