"""
module_id: adapter.io.sbol3
file: src/adapter/io/sbol3.py
task_id: T-308
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any

import sbol3 as py_sbol3  # type: ignore[import-untyped]

from adapter.io.imported_construct import ImportedConstruct, LossWarning
from adapter.io.write_result import WriteResult
from domain.sequence import DnaSequence, MoleculeType, SequenceRecord

NAMESPACE = "https://cev.local/sbol"
_DISPLAY_ID_PATTERN = re.compile(r"[^A-Za-z0-9_]")


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
            sequence_id = sequence.identity.rsplit("/", maxsplit=1)[-1]
            sequence_record = SequenceRecord(
                id=sequence_id,
                sequence=DnaSequence(str(sequence.elements).upper()),
                topology="linear",
                molecule_type=MoleculeType.DS_DNA,
            )
            return ImportedConstruct(
                construct_id=sequence_id,
                sequence_record=sequence_record,
                features=(),
                source_format=self.format_name,
                source_metadata={"sbol_identity": sequence.identity},
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
                loss_warnings=(
                    LossWarning(
                        "sbol-lite-drops-features",
                        "T-308 SBOL writer preserves sequence.",
                    ),
                )
                if construct.features
                else (),
            )
        finally:
            path.unlink(missing_ok=True)


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
