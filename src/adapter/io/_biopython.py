"""
module_id: adapter.io._biopython
file: src/adapter/io/_biopython.py
task_id: T-308

Biopython conversion helpers.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal, cast

from Bio.Seq import Seq
from Bio.SeqFeature import CompoundLocation, SeqFeature, SimpleLocation
from Bio.SeqRecord import SeqRecord

from adapter.io.imported_construct import ImportedConstruct
from domain.sequence import (
    CompoundLocationKind,
    DnaSequence,
    FeatureV14,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
    Topology,
)


def imported_from_seqrecord(record: SeqRecord, source_format: str) -> ImportedConstruct:
    topology: Topology = (
        "circular" if record.annotations.get("topology") == "circular" else "linear"
    )
    sequence_record = SequenceRecord(
        id=record.id or "imported-sequence",
        sequence=DnaSequence(str(record.seq).upper()),
        topology=topology,
        molecule_type=MoleculeType.DS_DNA,
    )
    features = tuple(
        _feature_from_seqfeature(feature, sequence_record.id, order)
        for order, feature in enumerate(record.features)
        if feature.type != "source"
    )
    return ImportedConstruct(
        construct_id=record.id or sequence_record.id,
        sequence_record=sequence_record,
        features=features,
        source_format=source_format,
        source_metadata={"name": record.name, "description": record.description},
    )


def seqrecord_from_imported(imported: ImportedConstruct) -> SeqRecord:
    record = SeqRecord(
        Seq(imported.sequence_record.canonical_sequence),
        id=imported.sequence_record.id,
        name=imported.construct_id[:16] or imported.sequence_record.id[:16],
        description=imported.construct_id,
    )
    record.annotations["molecule_type"] = "DNA"
    record.annotations["topology"] = imported.sequence_record.topology
    record.features = [_seqfeature_from_feature(feature) for feature in imported.features]
    return record


def _feature_from_seqfeature(
    feature: SeqFeature,
    parent_sequence_id: str,
    feature_order: int,
) -> FeatureV14:
    qualifiers: list[Qualifier] = []
    order = feature_order * 1000
    for key, values in sorted(feature.qualifiers.items()):
        value_items = values if isinstance(values, list) else [values]
        for value in value_items:
            qualifiers.append(
                Qualifier(
                    namespace="genbank",
                    key=str(key),
                    value=str(value),
                    value_type="string",
                    order=order,
                )
            )
            order += 1
    return FeatureV14(
        role=str(feature.type),
        qualifiers=tuple(qualifiers),
        locations=(_location_from_biopython(feature.location),),
        parent_sequence_id=parent_sequence_id,
    )


def _location_from_biopython(location: object) -> LocationV14:
    if isinstance(location, CompoundLocation):
        parts = tuple(_location_from_biopython(part) for part in location.parts)
        kind = (
            CompoundLocationKind.JOIN if location.operator == "join" else CompoundLocationKind.ORDER
        )
        start = min(part.start for part in parts)
        end = max(part.end for part in parts)
        return LocationV14(
            start=start,
            end=end,
            strand=".",
            phase=".",
            sub_locations=parts,
            sub_kind=kind,
        )
    if isinstance(location, SimpleLocation):
        return LocationV14(
            start=int(location.start),
            end=int(location.end),
            strand=_strand_from_biopython(location.strand),
            phase=".",
        )
    raise TypeError(f"unsupported Biopython location: {type(location).__name__}")


def _seqfeature_from_feature(feature: FeatureV14) -> SeqFeature:
    location = feature.locations[0]
    qualifiers = _qualifiers_to_biopython(feature.ordered_qualifiers)
    bio_location = cast(Any, SimpleLocation)(
        location.start,
        location.end,
        strand=_strand_to_biopython(location.strand),
    )
    return cast(
        SeqFeature,
        cast(Any, SeqFeature)(bio_location, type=feature.role, qualifiers=qualifiers),
    )


def _strand_from_biopython(strand: int | None) -> Literal["+", "-", "."]:
    if strand == 1:
        return "+"
    if strand == -1:
        return "-"
    return "."


def _qualifiers_to_biopython(qualifiers: Iterable[Qualifier]) -> dict[str, list[str]]:
    converted: dict[str, list[str]] = {}
    for qualifier in qualifiers:
        converted.setdefault(qualifier.key, []).append(str(qualifier.value))
    return converted


def _strand_to_biopython(strand: Literal["+", "-", "."]) -> int | None:
    if strand == "+":
        return 1
    if strand == "-":
        return -1
    return None
