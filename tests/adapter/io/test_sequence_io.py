"""
module_id: tests.adapter.io.test_sequence_io
file: tests/adapter/io/test_sequence_io.py
task_id: T-308
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from adapter.io import (
    AnnotatedConstruct,
    EmblAdapter,
    FastaAdapter,
    GenBankAdapter,
    Gff3Adapter,
    ImportedConstruct,
    Sbol3Adapter,
    SnapGeneDnaReader,
    SnapGeneDnaReadError,
)
from domain.graph import ConstructGraph, GraphNode, NodeId
from domain.sequence import (
    DnaSequence,
    FeatureV14,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
)


def _imported_construct(features: tuple[FeatureV14, ...] | None = None) -> ImportedConstruct:
    record = SequenceRecord(
        id="construct-1",
        sequence=DnaSequence("ACGTACGTACGT"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )
    feature = FeatureV14(
        role="CDS",
        qualifiers=(
            Qualifier(
                namespace="genbank",
                key="label",
                value="insert",
                value_type="string",
                order=0,
            ),
        ),
        locations=(LocationV14(start=2, end=8, strand="+", phase="."),),
        parent_sequence_id=record.id,
    )
    return ImportedConstruct(
        construct_id="construct-1",
        sequence_record=record,
        features=(feature,) if features is None else features,
        source_format="fixture",
        source_metadata={"fixture": True},
    )


def test_fasta_adapter_round_trips_sequence_and_reports_annotation_loss() -> None:
    adapter = FastaAdapter()
    result = adapter.write(_imported_construct())
    imported = adapter.read(result.data)

    assert imported.sequence_record.canonical_sequence == "ACGTACGTACGT"
    assert imported.features == ()
    assert result.loss_warnings[0].code == "fasta-drops-annotations"
    assert imported.loss_warnings[0].code == "fasta-drops-annotations"


def test_genbank_adapter_round_trips_simple_feature() -> None:
    adapter = GenBankAdapter()
    result = adapter.write(_imported_construct())
    imported = adapter.read(result.data)

    assert imported.sequence_record.canonical_sequence == "ACGTACGTACGT"
    assert imported.features[0].role == "CDS"
    assert imported.features[0].locations[0].start == 2
    assert imported.features[0].ordered_qualifiers[0].value == "insert"


def test_embl_adapter_round_trips_simple_feature() -> None:
    adapter = EmblAdapter()
    result = adapter.write(_imported_construct())
    imported = adapter.read(result.data)

    assert imported.sequence_record.canonical_sequence == "ACGTACGTACGT"
    assert imported.features[0].role == "CDS"
    assert imported.features[0].locations[0].start == 2
    assert imported.features[0].ordered_qualifiers[0].namespace == "embl"
    assert imported.features[0].ordered_qualifiers[0].value == "insert"


def test_gff3_adapter_round_trips_simple_feature_with_embedded_fasta() -> None:
    adapter = Gff3Adapter()
    result = adapter.write(_imported_construct())
    imported = adapter.read(result.data)

    assert imported.sequence_record.canonical_sequence == "ACGTACGTACGT"
    assert imported.features[0].role == "CDS"
    assert imported.features[0].locations[0].start == 2
    assert imported.features[0].locations[0].end == 8
    assert imported.features[0].ordered_qualifiers[0].key == "label"
    assert imported.features[0].ordered_qualifiers[0].value == "insert"
    assert result.data.decode("utf-8").startswith("##gff-version 3\n")


def test_gff3_adapter_requires_embedded_fasta_sequence() -> None:
    payload = b"##gff-version 3\nconstruct-1\t.\tCDS\t1\t3\t.\t+\t0\tID=cds1\n"

    with pytest.raises(ValueError, match="embedded FASTA"):
        Gff3Adapter().read(payload)


def test_sbol3_adapter_round_trips_sequence_and_exact_range_feature() -> None:
    adapter = Sbol3Adapter()
    result = adapter.write(_imported_construct())
    imported = adapter.read(result.data)

    assert imported.sequence_record.canonical_sequence == "ACGTACGTACGT"
    assert result.loss_warnings == ()
    assert imported.features[0].role == "CDS"
    assert imported.features[0].locations[0].start == 2
    assert imported.features[0].locations[0].end == 8
    assert imported.features[0].locations[0].strand == "+"
    assert imported.features[0].ordered_qualifiers[0].namespace == "sbol"
    assert imported.features[0].ordered_qualifiers[0].key == "name"
    assert imported.features[0].ordered_qualifiers[0].value == "insert"


def test_sbol3_adapter_warns_when_feature_location_cannot_round_trip() -> None:
    feature = replace(
        _imported_construct().features[0],
        locations=(LocationV14(start=10, end=2, strand="+", phase=".", circular_wrap=True),),
    )
    adapter = Sbol3Adapter()
    result = adapter.write(_imported_construct(features=(feature,)))
    imported = adapter.read(result.data)

    assert imported.features == ()
    assert result.loss_warnings[0].code == "sbol-feature-location-not-supported"


def test_snapgene_reader_reports_actionable_failure_for_corrupted_bytes() -> None:
    with pytest.raises(SnapGeneDnaReadError, match="Export the construct to GenBank"):
        SnapGeneDnaReader().read_dna(b"not-a-snapgene-file")


def test_imported_and_annotated_construct_invariants() -> None:
    imported = _imported_construct()
    graph = ConstructGraph(
        sequence_record=imported.sequence_record,
        topology=imported.sequence_record.topology,
        nodes=(
            GraphNode(
                id=NodeId("node-1"),
                kind="feature",
                payload=imported.features[0],
            ),
        ),
        edges=(),
    )

    assert AnnotatedConstruct(imported=imported, graph=graph)

    other_record = SequenceRecord(
        id="other",
        sequence=DnaSequence("ACGT"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )
    with pytest.raises(ValueError, match="graph sequence"):
        AnnotatedConstruct(imported=imported, graph=replace(graph, sequence_record=other_record))
