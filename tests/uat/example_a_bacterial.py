"""
module_id: tests.uat.example_a_bacterial
file: tests/uat/example_a_bacterial.py
task_id: T-1301

Example A: pET-28a-style BL21(DE3) over-expression of an EGFP-tagged target.
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

_OVERLAP = "ATGGCCGCTGACGAACTGTTC"
_CODING = _OVERLAP + coding_sequence("example-a-enzyme-egfp", 96)


def example() -> WhitePaperExample:
    return WhitePaperExample(
        key="example_a",
        title="Example A bacterial EGFP-tagged enzyme expression",
        project_name="White paper Example A",
        selections=SelectionIds(
            objective="objective.bacterial_expression",
            host="host.ecoli_bl21_de3",
            cargo="cargo.enzyme_a.egfp",
            expression="promoter.t7",
            tagging="tag.his6_tev",
            cloning_chemistry="chemistry.gibson",
            biosafety_tier="biosafety.BSL-1",
        ),
        extra_hosts=(),
        host_contexts=(HostFixture("host.ecoli_bl21_de3", HostRole.EXPRESSION),),
        assembly_method_id=AssemblyMethodId("gibson"),
        coding_part_id="orf",
        coding_sequence=_CODING,
        assembly_parts=(
            AssemblyPart(
                id="pet28a-backbone",
                sequence=(
                    "GCTGACGAATTCGGTACCGGATCCGCTGACGAATTCGGTACCGGATCCGCTGACGAATTC" + _OVERLAP
                ),
                right_overlap=_OVERLAP,
                annotations=("pET-28a-compatible backbone",),
            ),
            AssemblyPart(
                id="orf",
                sequence=_CODING,
                left_overlap=_OVERLAP,
                annotations=("His6-TEV-EGFP-EnzymeA coding cassette",),
            ),
        ),
        biosafety_tier=BiosafetyTier.BSL_1,
        host_class=ChassisClass.BACTERIAL,
        downstream_use=DownstreamUse.EXPRESSION,
        control_host_role="bacterial expression",
        control_cargo_classes=("enzyme", "gfp", "protein_expression"),
        vector_system_classes=("plasmid",),
        intended_readout="reporter fluorescence and protein-expression signal",
        risk_trigger_tags=("antibiotic_resistance_marker", "external_export"),
        risk_cargo_classes=("enzyme", "gfp"),
        risk_vector_system_classes=("plasmid",),
        risk_host_roles=("bacterial expression",),
        antibiotic_resistance_marker=True,
        external_export=True,
        checks=ExampleChecks(
            required_risk_advisory_ids=frozenset({"risk.antibiotic_resistance_marker_export"}),
            expected_host_roles=frozenset({HostRole.EXPRESSION}),
        ),
    )
