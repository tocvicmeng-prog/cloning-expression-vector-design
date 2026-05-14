"""
module_id: tests.domain.types
file: tests/domain/types/test_core_entities.py
task_id: T-303
"""

from __future__ import annotations

from datetime import date

import pytest

from domain.graph import ConstructGraph, GraphNode, NodeId
from domain.sequence import (
    DnaSequence,
    FeatureV14,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
    sha256_text,
)
from domain.types import (
    BiosafetyTier,
    ChassisClass,
    Construct,
    ConstructId,
    DownstreamUse,
    GradedCitation,
    Host,
    HostContext,
    HostId,
    HostRole,
    Module,
    ModuleId,
    ModuleLayer,
    Part,
    PartId,
    SequenceOntologyTerm,
    SlotKind,
)


def _record() -> SequenceRecord:
    return SequenceRecord(
        id="seq-1",
        sequence=DnaSequence("ACGT"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )


def _feature(name: str = "gene") -> FeatureV14:
    return FeatureV14(
        role="SO:0000316",
        qualifiers=(
            Qualifier(
                namespace="GenBank",
                key="gene",
                value=name,
                value_type="string",
                order=0,
            ),
        ),
        locations=(LocationV14(start=0, end=3, strand="+", phase=0),),
        parent_sequence_id="seq-1",
    )


def _graph() -> ConstructGraph:
    return ConstructGraph(
        nodes=(GraphNode(id=NodeId("feature-a"), kind="feature", payload=_feature()),),
        edges=(),
        topology="linear",
        sequence_record=_record(),
    )


def _part(part_id: str = "part-1") -> Part:
    sequence = DnaSequence("ACGT")
    return Part(
        id=PartId(part_id),
        name="promoter",
        role=SequenceOntologyTerm("SO:0000167"),
        sequence=sequence,
        annotations=(),
        parent=None,
        licence="Apache-2.0",
        provenance="fixture",
        checksum=sha256_text(sequence.body),
        host_compatibility=frozenset({ChassisClass.BACTERIAL}),
    )


def _module(part: Part | None = None) -> Module:
    return Module(
        id=ModuleId("module-1"),
        layer=ModuleLayer.EXPRESSION,
        slot_kind=SlotKind.REQUIRED,
        parts=(part or _part(),),
    )


def _host_context(role: HostRole = HostRole.EXPRESSION) -> HostContext:
    return HostContext(role=role, host_id=HostId("ecoli"), constraints=("BSL-1 only",))


def _construct(module: Module | None = None) -> Construct:
    graph = _graph()
    return Construct(
        id=ConstructId("construct-1"),
        version="1.0.0",
        modules=(module or _module(),),
        graph=graph,
        hosts=(_host_context(),),
        biosafety_tier=BiosafetyTier.BSL_1,
        downstream_use=DownstreamUse.EXPRESSION,
        feature_table=graph.feature_table,
        sbol_record=None,
        checksum=graph.sequence_record.checksum,
        provenance="fixture",
    )


def test_part_checksum_is_bound_to_sequence_body() -> None:
    sequence = DnaSequence("ACGT")

    with pytest.raises(ValueError, match="checksum"):
        Part(
            id=PartId("part-1"),
            name="bad",
            role=SequenceOntologyTerm("SO:0000167"),
            sequence=sequence,
            annotations=(),
            parent=None,
            licence="Apache-2.0",
            provenance="fixture",
            checksum=sha256_text("TGCA"),
        )


def test_part_annotations_must_reference_part_id() -> None:
    annotation = FeatureV14(
        role="SO:0000316",
        qualifiers=(),
        locations=(LocationV14(start=0, end=1, strand="+", phase="."),),
        parent_sequence_id="other",
    )
    sequence = DnaSequence("ACGT")

    with pytest.raises(ValueError, match="annotations"):
        Part(
            id=PartId("part-1"),
            name="bad",
            role=SequenceOntologyTerm("SO:0000167"),
            sequence=sequence,
            annotations=(annotation,),
            parent=None,
            licence="Apache-2.0",
            provenance="fixture",
            checksum=sha256_text(sequence.body),
        )


def test_construct_requires_derived_feature_table_and_matching_checksum() -> None:
    graph = _graph()

    with pytest.raises(ValueError, match="feature_table"):
        Construct(
            id=ConstructId("construct-1"),
            version="1.0.0",
            modules=(_module(),),
            graph=graph,
            hosts=(_host_context(),),
            biosafety_tier=BiosafetyTier.BSL_1,
            downstream_use=DownstreamUse.EXPRESSION,
            feature_table=(),
            sbol_record=None,
            checksum=graph.sequence_record.checksum,
            provenance="fixture",
        )

    with pytest.raises(ValueError, match="checksum"):
        Construct(
            id=ConstructId("construct-1"),
            version="1.0.0",
            modules=(_module(),),
            graph=graph,
            hosts=(_host_context(),),
            biosafety_tier=BiosafetyTier.BSL_1,
            downstream_use=DownstreamUse.EXPRESSION,
            feature_table=graph.feature_table,
            sbol_record=None,
            checksum=sha256_text("TGCA"),
            provenance="fixture",
        )


def test_construct_requires_unique_host_roles() -> None:
    graph = _graph()

    with pytest.raises(ValueError, match="host roles"):
        Construct(
            id=ConstructId("construct-1"),
            version="1.0.0",
            modules=(_module(),),
            graph=graph,
            hosts=(_host_context(), _host_context()),
            biosafety_tier=BiosafetyTier.BSL_1,
            downstream_use=DownstreamUse.EXPRESSION,
            feature_table=graph.feature_table,
            sbol_record=None,
            checksum=graph.sequence_record.checksum,
            provenance="fixture",
        )


def test_host_requires_citation_and_core_fields() -> None:
    citation = GradedCitation(
        text="Fixture source",
        grade="A1",
        accessed=date(2026, 5, 14),
        doi="10.0000/example",
    )
    host = Host(
        id=HostId("ecoli"),
        name="E. coli",
        chassis=ChassisClass.BACTERIAL,
        genotype="K-12",
        compatible_origins=frozenset(),
        compatible_markers=frozenset(),
        expression_features=frozenset({"lac"}),
        codon_usage_table="ecoli-table",
        growth_conditions="37C",
        biosafety_tier=BiosafetyTier.BSL_1,
        references=(citation,),
    )

    assert host.name == "E. coli"

    with pytest.raises(ValueError, match="citation"):
        GradedCitation(text="No source", grade="A1", accessed=date(2026, 5, 14))


def test_module_and_host_context_validate_required_values() -> None:
    with pytest.raises(ValueError, match="module"):
        Module(
            id=ModuleId("module-1"),
            layer=ModuleLayer.CARGO,
            slot_kind=SlotKind.REQUIRED,
            parts=(),
        )

    with pytest.raises(ValueError, match="host_id"):
        HostContext(role=HostRole.EXPRESSION, host_id=HostId(""))


def test_construct_fixture_is_valid() -> None:
    assert _construct().feature_table == _graph().feature_table
