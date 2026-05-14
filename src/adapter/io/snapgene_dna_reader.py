"""
module_id: adapter.io.snapgene_dna_reader
file: src/adapter/io/snapgene_dna_reader.py
task_id: T-308
"""

from __future__ import annotations

from io import BytesIO

from snapgene_reader import (  # type: ignore[import-untyped]
    snapgene_file_to_dict,
    snapgene_file_to_seqrecord,
)

from adapter.io._biopython import imported_from_seqrecord
from adapter.io.imported_construct import ImportedConstruct, LossWarning


class SnapGeneDnaReadError(ValueError):
    """Raised when a SnapGene .dna file cannot be parsed."""


class SnapGeneDnaReader:
    format_name = "snapgene-dna"

    def read_dna(self, source: bytes) -> ImportedConstruct:
        try:
            record = snapgene_file_to_seqrecord(fileobject=BytesIO(source))
            metadata = snapgene_file_to_dict(fileobject=BytesIO(source))
            visual_metadata = {
                "features": metadata.get("features", []),
                "primers": metadata.get("primers", []),
            }
            imported = imported_from_seqrecord(record, self.format_name)
            return ImportedConstruct(
                construct_id=imported.construct_id,
                sequence_record=imported.sequence_record,
                features=imported.features,
                source_format=self.format_name,
                source_metadata=imported.source_metadata,
                snapgene_visual_metadata=visual_metadata,
            )
        except Exception as exc:
            warning = LossWarning(
                "snapgene-proprietary-format-unparseable",
                "Export the construct to GenBank from SnapGene and import that file instead.",
            )
            raise SnapGeneDnaReadError(warning.message) from exc
