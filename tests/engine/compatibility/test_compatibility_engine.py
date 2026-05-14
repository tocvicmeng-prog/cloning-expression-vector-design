"""
module_id: tests.engine.compatibility.test_compatibility_engine
file: tests/engine/compatibility/test_compatibility_engine.py
task_id: T-504
"""

from __future__ import annotations

from datetime import date

from domain.graph import ConstructGraph, GraphNode, NodeId
from domain.sequence import DnaSequence, MoleculeType, SequenceRecord, sha256_text
from domain.types import (
    BiosafetyTier,
    ChassisClass,
    Construct,
    ConstructId,
    DownstreamUse,
    GradedCitation,
    Host,
    HostCompatibilityConstraints,
    HostContext,
    HostId,
    HostRole,
    MarkerId,
    Module,
    ModuleId,
    ModuleLayer,
    OriginId,
    Part,
    PartId,
    SafetyGate,
    SequenceOntologyTerm,
    Severity,
    SlotKind,
)
from engine.compatibility import (
    CompatibilityChecker,
    HostThresholdProfile,
)


def test_checker_accepts_plant_transient_three_host_workflow() -> None:
    construct = _construct(
        hosts=(
            _context(HostRole.CLONING_PROPAGATION, "ecoli"),
            _context(HostRole.DELIVERY, "agrobacterium"),
            _context(HostRole.TARGET, "plant"),
        )
    )

    report = _checker().check(construct)

    assert report.passed
    assert report.issues == ()
    assert {result.host_role for result in report.host_results} == {
        HostRole.CLONING_PROPAGATION,
        HostRole.DELIVERY,
        HostRole.TARGET,
    }


def test_checker_accepts_lentivirus_and_aav_three_host_workflows() -> None:
    checker = _checker()

    for producer_host in ("hek293t", "aav_producer"):
        construct = _construct(
            hosts=(
                _context(HostRole.CLONING_PROPAGATION, "ecoli"),
                _context(HostRole.PRODUCER, producer_host),
                _context(HostRole.TARGET, "mammalian_target"),
            )
        )

        report = checker.check(construct)

        assert report.passed
        assert report.issues == ()


def test_checker_accepts_vlp_four_host_workflow() -> None:
    construct = _construct(
        hosts=(
            _context(HostRole.CLONING_PROPAGATION, "ecoli"),
            _context(HostRole.EXPRESSION, "yeast"),
            _context(HostRole.PRODUCER, "hek293t"),
            _context(HostRole.TARGET, "mammalian_target"),
        ),
        origin_id="origin.shuttle",
        marker_id="marker.ura3",
    )

    report = _checker().check(construct)

    assert report.passed
    assert len(report.host_results) == 4


def test_checker_accepts_cell_free_workflow_without_propagation_host() -> None:
    construct = _construct(
        hosts=(_context(HostRole.EXPRESSION, "cell_free"),),
        marker_id="marker.none",
    )

    report = _checker().check(construct)

    assert report.passed
    assert HostRole.CLONING_PROPAGATION not in {result.host_role for result in report.host_results}


def test_checker_accepts_shuttle_vector_with_two_maintenance_hosts() -> None:
    construct = _construct(
        hosts=(
            _context(HostRole.CLONING_PROPAGATION, "ecoli"),
            _context(HostRole.STORAGE, "yeast"),
        ),
        origin_id="origin.shuttle",
        marker_id="marker.ura3",
    )

    report = _checker().check(construct)

    assert report.passed
    assert tuple(result.host_role for result in report.host_results) == (
        HostRole.CLONING_PROPAGATION,
        HostRole.STORAGE,
    )


def test_marker_conflict_is_checked_per_host_role() -> None:
    construct = _construct(
        hosts=(
            _context(HostRole.CLONING_PROPAGATION, "ecoli"),
            _context(HostRole.EXPRESSION, "yeast"),
        ),
        origin_id="origin.shuttle",
        marker_id="marker.kan",
    )

    report = _checker().check(construct)

    assert not report.passed
    assert report.blocked_gates == frozenset({SafetyGate.COMPILE})
    assert [(issue.host_role, issue.check_id) for issue in report.issues] == [
        (HostRole.EXPRESSION, "marker_compatibility")
    ]


def test_threshold_profile_can_downgrade_role_specific_issue() -> None:
    construct = _construct(
        hosts=(
            _context(HostRole.CLONING_PROPAGATION, "ecoli"),
            _context(HostRole.EXPRESSION, "yeast"),
        ),
        origin_id="origin.shuttle",
        marker_id="marker.kan",
    )
    checker = _checker(
        threshold_profiles={
            "thresholds.default:expression": HostThresholdProfile(
                profile_id="thresholds.default:expression",
                default_severity=Severity.SOFT,
            )
        }
    )

    report = checker.check(construct)

    assert report.passed
    assert report.blocked_gates == frozenset()
    assert report.issues[0].severity is Severity.SOFT
    assert report.issues[0].threshold_profile == "thresholds.default:expression"


def test_missing_host_is_reported_as_typed_issue() -> None:
    construct = _construct(hosts=(_context(HostRole.EXPRESSION, "missing"),))

    report = _checker().check(construct)

    assert not report.passed
    assert report.host_results[0].host_chassis is None
    assert report.issues[0].check_id == "host_catalogue"


def test_report_payload_is_deterministic() -> None:
    construct = _construct(
        hosts=(
            _context(HostRole.CLONING_PROPAGATION, "ecoli"),
            _context(HostRole.EXPRESSION, "yeast"),
        ),
        origin_id="origin.shuttle",
        marker_id="marker.kan",
    )
    checker = _checker()

    payloads = {checker.check(construct).canonical_json() for _ in range(50)}

    assert len(payloads) == 1


def _checker(
    *,
    threshold_profiles: dict[str, HostThresholdProfile] | None = None,
) -> CompatibilityChecker:
    return CompatibilityChecker(
        host_catalogue={
            host.id: host
            for host in (
                _host(
                    "ecoli",
                    ChassisClass.BACTERIAL,
                    origins=("origin.col_e1", "origin.shuttle"),
                    markers=("marker.kan", "marker.ura3", "marker.none"),
                ),
                _host(
                    "agrobacterium",
                    ChassisClass.BACTERIAL,
                    origins=("origin.col_e1",),
                    markers=("marker.kan", "marker.none"),
                ),
                _host("plant", ChassisClass.PLANT),
                _host("hek293t", ChassisClass.MAMMALIAN),
                _host("aav_producer", ChassisClass.MAMMALIAN),
                _host("mammalian_target", ChassisClass.MAMMALIAN),
                _host(
                    "yeast",
                    ChassisClass.YEAST,
                    origins=("origin.shuttle",),
                    markers=("marker.ura3", "marker.none"),
                ),
                _host("cell_free", ChassisClass.CELL_FREE, markers=("marker.none",)),
            )
        },
        constraints={
            HostRole.CLONING_PROPAGATION: _constraint(
                HostRole.CLONING_PROPAGATION,
                ChassisClass.BACTERIAL,
            ),
            HostRole.DELIVERY: _constraint(HostRole.DELIVERY, ChassisClass.BACTERIAL),
            HostRole.TARGET: _constraint(
                HostRole.TARGET,
                ChassisClass.PLANT,
                ChassisClass.MAMMALIAN,
            ),
            HostRole.PRODUCER: _constraint(HostRole.PRODUCER, ChassisClass.MAMMALIAN),
            HostRole.EXPRESSION: _constraint(
                HostRole.EXPRESSION,
                ChassisClass.YEAST,
                ChassisClass.CELL_FREE,
            ),
            HostRole.STORAGE: _constraint(HostRole.STORAGE, ChassisClass.YEAST),
        },
        threshold_profiles=threshold_profiles or {},
    )


def _constraint(
    role: HostRole,
    *allowed_chassis: ChassisClass,
    required_origins: tuple[str, ...] = (),
) -> HostCompatibilityConstraints:
    return HostCompatibilityConstraints(
        role=role,
        allowed_chassis=frozenset(allowed_chassis),
        required_origins=frozenset(OriginId(origin) for origin in required_origins),
    )


def _host(
    host_id: str,
    chassis: ChassisClass,
    *,
    origins: tuple[str, ...] = (),
    markers: tuple[str, ...] = (),
) -> Host:
    return Host(
        id=HostId(host_id),
        name=host_id.replace("_", " "),
        chassis=chassis,
        genotype="fixture genotype",
        compatible_origins=frozenset(OriginId(origin) for origin in origins),
        compatible_markers=frozenset(MarkerId(marker) for marker in markers),
        expression_features=frozenset(),
        codon_usage_table=f"{host_id}-codon-table",
        growth_conditions="fixture conditions",
        biosafety_tier=BiosafetyTier.BSL_1,
        references=(_citation(),),
    )


def _construct(
    *,
    hosts: tuple[HostContext, ...],
    origin_id: str = "origin.col_e1",
    marker_id: str = "marker.kan",
) -> Construct:
    graph = _graph()
    return Construct(
        id=ConstructId("construct.fixture"),
        version="1.0.0",
        modules=(
            _module("module.origin", ModuleLayer.PROPAGATION, _part(origin_id, "origin")),
            _module("module.marker", ModuleLayer.PROPAGATION, _part(marker_id, "selection_marker")),
            _module("module.cargo", ModuleLayer.CARGO, _part("cargo.gfp", "cargo")),
        ),
        graph=graph,
        hosts=hosts,
        biosafety_tier=BiosafetyTier.BSL_1,
        downstream_use=DownstreamUse.EXPRESSION,
        feature_table=graph.feature_table,
        sbol_record=None,
        checksum=graph.sequence_record.checksum,
        provenance="fixture",
    )


def _module(module_id: str, layer: ModuleLayer, part: Part) -> Module:
    return Module(
        id=ModuleId(module_id),
        layer=layer,
        slot_kind=SlotKind.REQUIRED,
        parts=(part,),
    )


def _part(part_id: str, role: str) -> Part:
    sequence = DnaSequence("ACGT")
    return Part(
        id=PartId(part_id),
        name=part_id,
        role=SequenceOntologyTerm(role),
        sequence=sequence,
        annotations=(),
        parent=None,
        licence="Apache-2.0",
        provenance="fixture",
        checksum=sha256_text(sequence.body),
    )


def _context(role: HostRole, host_id: str) -> HostContext:
    return HostContext(role=role, host_id=HostId(host_id))


def _graph() -> ConstructGraph:
    record = SequenceRecord(
        id="construct-seq",
        sequence=DnaSequence("ACGT"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )
    return ConstructGraph(
        nodes=(GraphNode(id=NodeId("construct-root"), kind="part", payload="construct"),),
        edges=(),
        topology="linear",
        sequence_record=record,
    )


def _citation() -> GradedCitation:
    return GradedCitation(
        text="compatibility fixture",
        grade="B2",
        accessed=date(2026, 5, 14),
        url="REQUIREMENTS.md",
    )
