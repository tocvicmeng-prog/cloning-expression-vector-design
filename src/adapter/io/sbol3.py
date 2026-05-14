"""
module_id: adapter.io.sbol3
file: src/adapter/io/sbol3.py
task_id: T-308
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any, Literal

import sbol3 as py_sbol3  # type: ignore[import-untyped]

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

NAMESPACE = "https://cev.local/sbol"
_DISPLAY_ID_PATTERN = re.compile(r"[^A-Za-z0-9_]")
_ROLE_TO_SBOL = {
    "CDS": py_sbol3.SO_CDS,
    "gene": py_sbol3.SO_GENE,
    "promoter": py_sbol3.SO_PROMOTER,
    "RBS": py_sbol3.SO_RBS,
    "terminator": py_sbol3.SO_TERMINATOR,
}
_SBOL_TO_ROLE = {value: key for key, value in _ROLE_TO_SBOL.items()}


class Sbol3Adapter:
    format_name = "sbol3"

    def read(self, source: bytes) -> ImportedConstruct:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nt") as handle:
            path = Path(handle.name)
            handle.write(source)
        try:
            document = py_sbol3.Document()
            document.read(path, py_sbol3.SORTED_NTRIPLES)
            sequence = _first_sequence(document)
            component = _first_component(document)
            sequence_id = sequence.identity.rsplit("/", maxsplit=1)[-1]
            sequence_record = SequenceRecord(
                id=sequence_id,
                sequence=DnaSequence(str(sequence.elements).upper()),
                topology="linear",
                molecule_type=MoleculeType.DS_DNA,
            )
            features = _features_from_component(component, sequence_record.id) if component else ()
            return ImportedConstruct(
                construct_id=sequence_id,
                sequence_record=sequence_record,
                features=features,
                source_format=self.format_name,
                source_metadata={
                    "sbol_component_identity": component.identity if component else None,
                    "sbol_identity": sequence.identity,
                },
            )
        finally:
            path.unlink(missing_ok=True)

    def write(self, construct: ImportedConstruct) -> WriteResult:
        py_sbol3.set_namespace(NAMESPACE)
        document = py_sbol3.Document()
        sequence_display_id = _display_id(construct.sequence_record.id)
        sequence = py_sbol3.Sequence(
            sequence_display_id,
            elements=construct.sequence_record.canonical_sequence,
            encoding=py_sbol3.IUPAC_DNA_ENCODING,
        )
        component = py_sbol3.Component(
            f"{sequence_display_id}_component",
            types=[py_sbol3.SBO_DNA],
            sequences=[sequence],
            features=_features_to_sbol(sequence, construct.features),
        )
        document.add(sequence)
        document.add(component)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nt") as handle:
            path = Path(handle.name)
        try:
            document.write(path, py_sbol3.SORTED_NTRIPLES)
            return WriteResult(
                format_name=self.format_name,
                data=path.read_bytes(),
                semantic_fingerprint=construct.semantic_fingerprint(),
                loss_warnings=_feature_loss_warnings(construct.features),
            )
        finally:
            path.unlink(missing_ok=True)


def _first_component(document: Any) -> Any | None:
    for item in document.objects:
        if isinstance(item, py_sbol3.Component):
            return item
    return None


def _first_sequence(document: Any) -> Any:
    for item in document.objects:
        if isinstance(item, py_sbol3.Sequence):
            return item
    raise ValueError("SBOL document does not contain a Sequence")


def _display_id(value: str) -> str:
    display_id = _DISPLAY_ID_PATTERN.sub("_", value)
    if not display_id:
        return "sequence"
    if display_id[0].isdigit():
        return f"s_{display_id}"
    return display_id


def _features_to_sbol(
    sequence: Any,
    features: tuple[FeatureV14, ...],
) -> list[Any]:
    converted: list[Any] = []
    for feature in features:
        locations = [_location_to_sbol(sequence, location) for location in feature.locations]
        locations = [location for location in locations if location is not None]
        if not locations:
            continue
        converted.append(
            py_sbol3.SequenceFeature(
                locations,
                roles=[_ROLE_TO_SBOL.get(feature.role, py_sbol3.SO_ENGINEERED_REGION)],
                name=_feature_name(feature),
            )
        )
    return converted


def _location_to_sbol(sequence: Any, location: LocationV14) -> Any | None:
    if not _sbol_round_trippable_location(location):
        return None
    return py_sbol3.Range(
        sequence,
        location.start + 1,
        location.end,
        orientation=_orientation_to_sbol(location.strand),
    )


def _features_from_component(component: Any, parent_sequence_id: str) -> tuple[FeatureV14, ...]:
    converted: list[FeatureV14] = []
    for index, feature in enumerate(component.features):
        locations = tuple(
            _location_from_sbol(location)
            for location in feature.locations
            if isinstance(location, py_sbol3.Range)
        )
        if not locations:
            continue
        name = getattr(feature, "name", None)
        qualifiers = (
            (
                Qualifier(
                    namespace="sbol",
                    key="name",
                    value=str(name),
                    value_type="string",
                    order=index * 1000,
                ),
            )
            if name
            else ()
        )
        converted.append(
            FeatureV14(
                role=_role_from_sbol(feature),
                qualifiers=qualifiers,
                locations=locations,
                parent_sequence_id=parent_sequence_id,
            )
        )
    return tuple(converted)


def _location_from_sbol(location: Any) -> LocationV14:
    return LocationV14(
        start=int(location.start) - 1,
        end=int(location.end),
        strand=_orientation_from_sbol(str(location.orientation)),
        phase=".",
    )


def _feature_name(feature: FeatureV14) -> str | None:
    for qualifier in feature.ordered_qualifiers:
        if qualifier.key in {"label", "name"}:
            return str(qualifier.value)
    return None


def _feature_loss_warnings(features: tuple[FeatureV14, ...]) -> tuple[LossWarning, ...]:
    unsupported = [
        feature
        for feature in features
        if not feature.locations
        or any(not _sbol_round_trippable_location(location) for location in feature.locations)
    ]
    if not unsupported:
        return ()
    return (
        LossWarning(
            "sbol-feature-location-not-supported",
            "SBOL writer preserved exact range features and skipped unsupported location shapes.",
        ),
    )


def _orientation_to_sbol(strand: str) -> str | None:
    if strand == "+":
        return str(py_sbol3.SO_FORWARD)
    if strand == "-":
        return str(py_sbol3.SO_REVERSE)
    return None


def _orientation_from_sbol(orientation: str) -> Literal["+", "-", "."]:
    if orientation == py_sbol3.SO_FORWARD:
        return "+"
    if orientation == py_sbol3.SO_REVERSE:
        return "-"
    return "."


def _role_from_sbol(feature: Any) -> str:
    roles = getattr(feature, "roles", ())
    if roles:
        return _SBOL_TO_ROLE.get(str(roles[0]), "engineered_region")
    return "engineered_region"


def _sbol_round_trippable_location(location: LocationV14) -> bool:
    return (
        not location.sub_locations
        and not location.circular_wrap
        and not location.between_base
        and location.start_fuzziness is LocationFuzziness.EXACT
        and location.end_fuzziness is LocationFuzziness.EXACT
        and location.remote_accession is None
        and not location.partial_at_5p
        and not location.partial_at_3p
    )
