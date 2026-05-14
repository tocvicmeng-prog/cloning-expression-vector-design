"""
module_id: tests.uat.example_b_mammalian
file: tests/uat/example_b_mammalian.py
task_id: T-1301

Example B: lentiviral HEK293T CRISPRi workflow with dual-control authorisation.
"""

from __future__ import annotations

from domain.types import AssemblyMethodId, BiosafetyTier, ChassisClass, DownstreamUse, HostRole
from domain.types.controls import ControlKind
from engine.assembly import AssemblyPart
from engine.vlp_policy import VlpPolicyRequest, VlpSystemClass, evaluate_vlp_policy
from tests.uat.helpers import (
    ExampleChecks,
    HostFixture,
    SelectionIds,
    WhitePaperExample,
    coding_sequence,
)

_CODING = coding_sequence("example-b-crispri", 150)
_VLP_REPORT = evaluate_vlp_policy(
    VlpPolicyRequest(
        construct_id="example-b-lentiviral-crispri",
        system_class=VlpSystemClass.LENTIVIRAL,
        cargo_size_nt=len(_CODING),
        cargo_classes=("crispri", "cargo-delivery"),
        packaging_signals=("LTR", "psi"),
        helper_components=("gag-pol", "env"),
        host_roles=("producer_host", "mammalian_target"),
        control_kinds=(
            ControlKind.POSITIVE,
            ControlKind.NEGATIVE,
            ControlKind.PROCESS,
            ControlKind.VEHICLE,
        ),
        validation_readouts=("transfer-vector-integrity",),
        replication_competent=True,
    )
)


def example() -> WhitePaperExample:
    return WhitePaperExample(
        key="example_b",
        title="Example B mammalian lentiviral CRISPRi",
        project_name="White paper Example B",
        selections=SelectionIds(
            objective="objective.mammalian_expression",
            host="host.hek293t_producer",
            cargo="cargo.crispri_krab_sgrna",
            expression="promoter.ef1a",
            tagging="tag.nls",
            cloning_chemistry="chemistry.golden_gate",
            biosafety_tier="biosafety.BSL-2",
        ),
        extra_hosts=(
            HostFixture("host.ecoli_k12", HostRole.CLONING_PROPAGATION),
            HostFixture("host.hek293t_target", HostRole.TARGET),
        ),
        host_contexts=(
            HostFixture("host.ecoli_k12", HostRole.CLONING_PROPAGATION),
            HostFixture("host.hek293t_producer", HostRole.PRODUCER),
            HostFixture("host.hek293t_target", HostRole.TARGET),
        ),
        assembly_method_id=AssemblyMethodId("golden-gate"),
        coding_part_id="orf",
        coding_sequence=_CODING,
        assembly_parts=(
            AssemblyPart(id="promoter", sequence="GCTGACGAATTCGGTACCGGATCCGCTGACGAATTCGGTACC"),
            AssemblyPart(id="nls", sequence="GGTACCGCTGACGAATTCGGTACCGGATCCGCTGACGAATTC"),
            AssemblyPart(id="orf", sequence=_CODING),
            AssemblyPart(id="terminator", sequence="GATCCGCTGACGAATTCGGTACCGCTGACGAATTCGGTACC"),
        ),
        biosafety_tier=BiosafetyTier.BSL_2,
        host_class=ChassisClass.MAMMALIAN,
        downstream_use=DownstreamUse.VLP_OR_PHAGE_DISPLAY,
        control_host_role="mammalian producer",
        control_cargo_classes=("crispri", "reporter"),
        vector_system_classes=("lentivirus", "viral_vector"),
        intended_readout="transfer-vector integrity",
        risk_trigger_tags=_VLP_REPORT.risk_trigger_tags,
        risk_cargo_classes=("crispri",),
        risk_vector_system_classes=("lentiviral", "viral_vector"),
        risk_host_roles=("producer_host", "mammalian_target"),
        replication_competent=True,
        vlp_report=_VLP_REPORT,
        institutional_protocol_id="IBC-2026-LENTI-DC",
        profile_constraints=("biosafety_approval_required", "institutional_protocol_id_required"),
        checks=ExampleChecks(
            required_risk_advisory_ids=frozenset(
                {
                    "risk.rg2_or_higher_component",
                    "risk.replication_competent_viral_vector",
                    "risk.lentiviral_or_aav_packaging",
                }
            ),
            expected_vlp_blocked_rule_ids=frozenset({"MS-06"}),
            expected_host_roles=frozenset(
                {HostRole.CLONING_PROPAGATION, HostRole.PRODUCER, HostRole.TARGET}
            ),
            dual_control_required=True,
        ),
    )
