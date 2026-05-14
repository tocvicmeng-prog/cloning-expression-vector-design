"""
module_id: adapter.io.gff3
file: src/adapter/io/gff3.py
task_id: T-901
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from io import StringIO
from typing import Any, Literal, cast
from urllib.parse import quote, unquote

from Bio import SeqIO

from adapter.io.imported_construct import ImportedConstruct, LossWarning
from adapter.io.write_result import WriteResult
from domain.sequence import (
    DnaSequence,
    FeatureV14,
    LocationFuzziness,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
)

GFF3_SOURCE_KEY = "source"
GFF3_SCORE_KEY = "score"
GFF3_NAMESPACE = "gff3"


@dataclass(frozen=True)
class _Gff3Line:
    seqid: str
    source: str
    feature_type: str
    start: int
    end: int
    score: str
    strand: Literal["+", "-", "."]
    phase: Literal[0, 1, 2, "."]
    attributes: tuple[Qualifier, ...]
    line_number: int


class Gff3Adapter:
    format_name = "gff3"

    def read(self, source: bytes) -> ImportedConstruct:
        text = source.decode("utf-8")
        feature_text, fasta_text = _split_embedded_fasta(text)
        sequence_record = _sequence_record_from_fasta(fasta_text)
        feature_lines, directives = _parse_feature_lines(feature_text)
        features = tuple(
            _feature_from_line(line, sequence_record.id)
            for line in feature_lines
            if line.seqid == sequence_record.id
        )
        mismatched = tuple(line.seqid for line in feature_lines if line.seqid != sequence_record.id)
        if mismatched:
            mismatch = ", ".join(sorted(set(mismatched)))
            raise ValueError(
                f"GFF3 features reference sequence IDs not present in FASTA: {mismatch}"
            )
        return ImportedConstruct(
            construct_id=sequence_record.id,
            sequence_record=sequence_record,
            features=features,
            source_format=self.format_name,
            source_metadata={"directives": directives},
        )

    def write(self, construct: ImportedConstruct) -> WriteResult:
        lines = ["##gff-version 3"]
        lines.append(
            f"##sequence-region {construct.sequence_record.id} 1 {construct.sequence_record.length}"
        )
        warnings: list[LossWarning] = []
        for feature_index, feature in enumerate(construct.features):
            source, score, attributes = _columns_from_qualifiers(feature.ordered_qualifiers)
            for location_index, location in enumerate(_iter_gff3_locations(feature)):
                warnings.extend(_location_loss_warnings(location, feature_index, location_index))
                start, end = _gff3_coordinates(location)
                phase = "." if location.phase == "." else str(location.phase)
                lines.append(
                    "\t".join(
                        (
                            construct.sequence_record.id,
                            source,
                            feature.role,
                            str(start),
                            str(end),
                            score,
                            location.strand,
                            phase,
                            attributes,
                        )
                    )
                )
        lines.append("##FASTA")
        lines.append(f">{construct.sequence_record.id}")
        lines.extend(_wrap_sequence(construct.sequence_record.canonical_sequence))
        data = ("\n".join(lines) + "\n").encode("utf-8")
        return WriteResult(
            format_name=self.format_name,
            data=data,
            semantic_fingerprint=construct.semantic_fingerprint(),
            loss_warnings=tuple(dict.fromkeys(warnings)),
        )


def _split_embedded_fasta(text: str) -> tuple[str, str]:
    marker = "\n##FASTA"
    if text.startswith("##FASTA"):
        return "", text.removeprefix("##FASTA").lstrip("\r\n")
    if marker not in text:
        raise ValueError("GFF3 import requires an embedded FASTA section")
    feature_text, fasta_text = text.split(marker, maxsplit=1)
    return feature_text, fasta_text.lstrip("\r\n")


def _sequence_record_from_fasta(fasta_text: str) -> SequenceRecord:
    records = list(cast(Any, SeqIO).parse(StringIO(fasta_text), "fasta"))
    if len(records) != 1:
        raise ValueError("GFF3 import requires exactly one embedded FASTA record")
    record = records[0]
    return SequenceRecord(
        id=record.id,
        sequence=DnaSequence(str(record.seq).upper()),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )


def _parse_feature_lines(feature_text: str) -> tuple[tuple[_Gff3Line, ...], tuple[str, ...]]:
    feature_lines: list[_Gff3Line] = []
    directives: list[str] = []
    for line_number, raw_line in enumerate(feature_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            directives.append(line)
            continue
        columns = raw_line.split("\t")
        if len(columns) != 9:
            raise ValueError(f"GFF3 line {line_number} must have 9 tab-delimited columns")
        feature_lines.append(_parse_feature_line(columns, line_number))
    return tuple(feature_lines), tuple(directives)


def _parse_feature_line(columns: list[str], line_number: int) -> _Gff3Line:
    (
        seqid,
        source,
        feature_type,
        start_text,
        end_text,
        score,
        strand_text,
        phase_text,
        attrs,
    ) = columns
    if strand_text not in {"+", "-", "."}:
        raise ValueError(f"GFF3 line {line_number} has unsupported strand {strand_text!r}")
    if phase_text not in {".", "0", "1", "2"}:
        raise ValueError(f"GFF3 line {line_number} has unsupported phase {phase_text!r}")
    start = int(start_text)
    end = int(end_text)
    if start < 1 or end < start:
        raise ValueError(f"GFF3 line {line_number} has invalid coordinates")
    phase: Literal[0, 1, 2, "."] = "." if phase_text == "." else cast(Any, int(phase_text))
    return _Gff3Line(
        seqid=seqid,
        source=source,
        feature_type=feature_type,
        start=start,
        end=end,
        score=score,
        strand=cast(Literal["+", "-", "."], strand_text),
        phase=phase,
        attributes=_parse_attributes(attrs, line_number),
        line_number=line_number,
    )


def _parse_attributes(attributes: str, line_number: int) -> tuple[Qualifier, ...]:
    if attributes in {"", "."}:
        return ()
    parsed: list[Qualifier] = []
    order = line_number * 1000
    for item in attributes.split(";"):
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"GFF3 line {line_number} has malformed attribute {item!r}")
        key, value_text = item.split("=", maxsplit=1)
        key = unquote(key)
        if not key:
            raise ValueError(f"GFF3 line {line_number} has empty attribute key")
        for value in value_text.split(","):
            parsed.append(
                Qualifier(
                    namespace=GFF3_NAMESPACE,
                    key=key,
                    value=unquote(value),
                    value_type="string",
                    order=order,
                )
            )
            order += 1
    return tuple(parsed)


def _feature_from_line(line: _Gff3Line, parent_sequence_id: str) -> FeatureV14:
    qualifiers: list[Qualifier] = []
    order = line.line_number * 1000
    if line.source != ".":
        qualifiers.append(
            Qualifier(
                namespace=GFF3_NAMESPACE,
                key=GFF3_SOURCE_KEY,
                value=line.source,
                value_type="string",
                order=order,
            )
        )
        order += 1
    if line.score != ".":
        qualifiers.append(
            Qualifier(
                namespace=GFF3_NAMESPACE,
                key=GFF3_SCORE_KEY,
                value=line.score,
                value_type="string",
                order=order,
            )
        )
        order += 1
    qualifiers.extend(line.attributes)
    return FeatureV14(
        role=line.feature_type,
        qualifiers=tuple(qualifiers),
        locations=(
            LocationV14(
                start=line.start - 1,
                end=line.end,
                strand=line.strand,
                phase=line.phase,
            ),
        ),
        parent_sequence_id=parent_sequence_id,
    )


def _columns_from_qualifiers(qualifiers: Iterable[Qualifier]) -> tuple[str, str, str]:
    source = "."
    score = "."
    attributes: dict[str, list[str]] = {}
    for qualifier in qualifiers:
        if qualifier.namespace == GFF3_NAMESPACE and qualifier.key == GFF3_SOURCE_KEY:
            source = str(qualifier.value)
            continue
        if qualifier.namespace == GFF3_NAMESPACE and qualifier.key == GFF3_SCORE_KEY:
            score = str(qualifier.value)
            continue
        attributes.setdefault(qualifier.key, []).append(str(qualifier.value))
    return source, score, _format_attributes(attributes)


def _format_attributes(attributes: dict[str, list[str]]) -> str:
    if not attributes:
        return "."
    return ";".join(
        f"{quote(key, safe='')}={','.join(quote(value, safe='') for value in values)}"
        for key, values in attributes.items()
    )


def _iter_gff3_locations(feature: FeatureV14) -> Iterable[LocationV14]:
    for location in feature.locations:
        if location.sub_locations:
            yield from location.sub_locations
        else:
            yield location


def _gff3_coordinates(location: LocationV14) -> tuple[int, int]:
    if location.circular_wrap:
        raise ValueError("GFF3 writer cannot serialise circular-wrap locations")
    if location.between_base:
        raise ValueError("GFF3 writer cannot serialise between-base locations")
    if location.remote_accession is not None:
        raise ValueError("GFF3 writer cannot serialise remote locations")
    if location.start >= location.end:
        raise ValueError("GFF3 writer requires non-empty feature spans")
    return location.start + 1, location.end


def _location_loss_warnings(
    location: LocationV14,
    feature_index: int,
    location_index: int,
) -> tuple[LossWarning, ...]:
    warnings: list[LossWarning] = []
    if (
        location.start_fuzziness is not LocationFuzziness.EXACT
        or location.end_fuzziness is not LocationFuzziness.EXACT
        or location.partial_at_5p
        or location.partial_at_3p
    ):
        warnings.append(
            LossWarning(
                "gff3-drops-location-fuzziness",
                (
                    "GFF3 coordinate columns cannot preserve all LocationV14 "
                    f"fuzziness fields at feature {feature_index}, location {location_index}."
                ),
            )
        )
    if location.sub_locations:
        warnings.append(
            LossWarning(
                "gff3-flattens-compound-locations",
                (
                    "GFF3 serialises compound feature parts as separate rows at "
                    f"feature {feature_index}, location {location_index}."
                ),
            )
        )
    return tuple(warnings)


def _wrap_sequence(sequence: str) -> tuple[str, ...]:
    return tuple(sequence[index : index + 80] for index in range(0, len(sequence), 80))
