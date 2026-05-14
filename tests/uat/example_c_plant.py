"""
module_id: tests.uat.example_c_plant
file: tests/uat/example_c_plant.py
task_id: T-1301

Example C: Agrobacterium-mediated transient expression in N. benthamiana.
"""

from __future__ import annotations

from domain.types import AssemblyMethodId, BiosafetyTier, ChassisClass, DownstreamUse, HostRole
from engine.assembly import AssemblyPart
from tests.uat.helpers import (
    ExampleChecks,
    HostFixture,
    SelectionIds,
    WhitePaperExample,
    coding_sequence,
)

_CODING = coding_sequence("example-c-plant-egfp", 120)


def example() -> WhitePaperExample:
    return WhitePaperExample(
        key="example_c",
        title="Example C plant transient expression",
        project_name="White paper Example C",
        selections=SelectionIds(
            objective="objective.plant_transient",
            host="host.n_benthamiana",
            cargo="cargo.plant_egfp",
            expression="promoter.35s",
            tagging="tag.ha",
            cloning_chemistry="chemistry.golden_gate",
            biosafety_tier="biosafety.BSL-1",
        ),
        extra_hosts=(
            HostFixture("host.ecoli_k12", HostRole.CLONING_PROPAGATION),
            HostFixture("host.agrobacterium_gv3101", HostRole.DELIVERY),
        ),
        host_contexts=(
            HostFixture("host.ecoli_k12", HostRole.CLONING_PROPAGATION),
            HostFixture("host.agrobacterium_gv3101", HostRole.DELIVERY),
            HostFixture("host.n_benthamiana", HostRole.TARGET),
        ),
        assembly_method_id=AssemblyMethodId("moclo"),
        coding_part_id="orf",
        coding_sequence=_CODING,
        assembly_parts=(
            AssemblyPart(
                id="promoter",
                sequence="GCTGACGAATTCGGTACCGGATCCGCTGACGAATTCGGTACC",
            ),
            AssemblyPart(
                id="tag",
                sequence="TTCGGTACCGGATCCGCTGACGAATTCGGTACCGCTGAC",
            ),
            AssemblyPart(id="orf", sequence=_CODING),
            AssemblyPart(
                id="terminator",
                sequence="GGATCCGCTGACGAATTCGGTACCGCTGACGAATTCGGT",
            ),
        ),
        biosafety_tier=BiosafetyTier.BSL_1,
        host_class=ChassisClass.PLANT,
        downstream_use=DownstreamUse.EXPRESSION,
        control_host_role="plant agrobacterium transient expression",
        control_cargo_classes=("gfp", "reporter"),
        vector_system_classes=("binary_vector", "agrobacterium"),
        intended_readout="reporter fluorescence",
        risk_trigger_tags=("environmental_release",),
        risk_cargo_classes=("gfp", "reporter"),
        risk_vector_system_classes=("agrobacterium_binary_vector",),
        risk_host_roles=("cloning_propagation", "delivery", "plant_target"),
        risk_intended_uses=("environmental_release",),
        compatibility_origin_id="origin.binary",
        checks=ExampleChecks(
            required_risk_advisory_ids=frozenset({"risk.in_vivo_or_environmental_release"}),
            expected_host_roles=frozenset(
                {HostRole.CLONING_PROPAGATION, HostRole.DELIVERY, HostRole.TARGET}
            ),
        ),
    )
