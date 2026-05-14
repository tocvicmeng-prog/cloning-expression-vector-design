"""
module_id: adapter.io.fasta
file: src/adapter/io/fasta.py
task_id: T-308
"""

from __future__ import annotations

from io import StringIO
from typing import Any, cast

from Bio import SeqIO

from adapter.io.imported_construct import ImportedConstruct, LossWarning
from adapter.io.write_result import WriteResult
from domain.sequence import DnaSequence, MoleculeType, SequenceRecord


class FastaAdapter:
    format_name = "fasta"

    def read(self, source: bytes) -> ImportedConstruct:
        records = list(cast(Any, SeqIO).parse(StringIO(source.decode("utf-8")), "fasta"))
        if len(records) != 1:
            raise ValueError("FASTA import requires exactly one sequence record")
        record = records[0]
        sequence_record = SequenceRecord(
            id=record.id,
            sequence=DnaSequence(str(record.seq).upper()),
            topology="linear",
            molecule_type=MoleculeType.DS_DNA,
        )
        return ImportedConstruct(
            construct_id=record.id,
            sequence_record=sequence_record,
            features=(),
            source_format=self.format_name,
            source_metadata={"description": record.description},
            loss_warnings=(
                LossWarning("fasta-drops-annotations", "FASTA preserves sequence only."),
            ),
        )

    def write(self, construct: ImportedConstruct) -> WriteResult:
        body = construct.sequence_record.canonical_sequence
        wrapped = "\n".join(body[index : index + 80] for index in range(0, len(body), 80))
        data = f">{construct.sequence_record.id}\n{wrapped}\n".encode()
        return WriteResult(
            format_name=self.format_name,
            data=data,
            semantic_fingerprint=construct.semantic_fingerprint(),
            loss_warnings=(
                LossWarning("fasta-drops-annotations", "FASTA preserves sequence only."),
            )
            if construct.features
            else (),
        )
