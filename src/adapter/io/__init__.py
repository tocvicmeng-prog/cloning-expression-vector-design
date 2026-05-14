"""
module_id: adapter.io
file: src/adapter/io/__init__.py
task_id: T-308

Sequence I/O adapters and imported construct contracts.
"""

from __future__ import annotations

from adapter.io.fasta import FastaAdapter
from adapter.io.genbank import GenBankAdapter
from adapter.io.imported_construct import (
    AnnotatedConstruct,
    ImportedConstruct,
    LossWarning,
)
from adapter.io.sbol3 import Sbol3Adapter
from adapter.io.snapgene_dna_reader import SnapGeneDnaReader, SnapGeneDnaReadError
from adapter.io.write_result import WriteResult

__all__ = [
    "AnnotatedConstruct",
    "FastaAdapter",
    "GenBankAdapter",
    "ImportedConstruct",
    "LossWarning",
    "Sbol3Adapter",
    "SnapGeneDnaReadError",
    "SnapGeneDnaReader",
    "WriteResult",
]
