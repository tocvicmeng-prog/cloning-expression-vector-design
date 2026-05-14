"""
module_id: adapter.io.embl
file: src/adapter/io/embl.py
task_id: T-901
"""

from __future__ import annotations

from io import StringIO
from typing import Any, cast

from Bio import SeqIO

from adapter.io._biopython import imported_from_seqrecord, seqrecord_from_imported
from adapter.io.imported_construct import ImportedConstruct
from adapter.io.write_result import WriteResult


class EmblAdapter:
    format_name = "embl"

    def read(self, source: bytes) -> ImportedConstruct:
        record = cast(Any, SeqIO).read(StringIO(source.decode("utf-8")), "embl")
        return imported_from_seqrecord(record, self.format_name, qualifier_namespace="embl")

    def write(self, construct: ImportedConstruct) -> WriteResult:
        output = StringIO()
        cast(Any, SeqIO).write(seqrecord_from_imported(construct), output, "embl")
        return WriteResult(
            format_name=self.format_name,
            data=output.getvalue().encode("utf-8"),
            semantic_fingerprint=construct.semantic_fingerprint(),
        )
