"""
module_id: adapter.io.imported_construct
file: src/adapter/io/imported_construct.py
task_id: T-308

Imported and annotated construct contracts.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from domain.graph import ConstructGraph
from domain.sequence import FeatureV14, SequenceRecord, Sha256, sha256_text


@dataclass(frozen=True)
class LossWarning:
    code: str
    message: str

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("loss warning code cannot be empty")
        if not self.message:
            raise ValueError("loss warning message cannot be empty")


@dataclass(frozen=True)
class ImportedConstruct:
    construct_id: str
    sequence_record: SequenceRecord
    features: tuple[FeatureV14, ...]
    source_format: str
    source_metadata: Mapping[str, object]
    loss_warnings: tuple[LossWarning, ...] = ()
    snapgene_visual_metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not self.source_format:
            raise ValueError("source_format cannot be empty")
        if any(feature.parent_sequence_id != self.sequence_record.id for feature in self.features):
            raise ValueError("all imported features must belong to the sequence record")

    @property
    def sequence_hash(self) -> Sha256:
        return self.sequence_record.checksum

    def semantic_fingerprint(self) -> Sha256:
        feature_fingerprint = "|".join(
            (
                f"{feature.role}:"
                f"{','.join(q.key + '=' + str(q.value) for q in feature.ordered_qualifiers)}"
            )
            for feature in self.features
        )
        return sha256_text(f"{self.sequence_record.checksum}:{feature_fingerprint}")


@dataclass(frozen=True)
class AnnotatedConstruct:
    imported: ImportedConstruct
    graph: ConstructGraph

    def __post_init__(self) -> None:
        if self.graph.sequence_record != self.imported.sequence_record:
            raise ValueError("annotated graph sequence must match imported sequence")
