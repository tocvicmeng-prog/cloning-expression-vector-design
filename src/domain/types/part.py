"""
module_id: domain.types.part
file: src/domain/types/part.py
task_id: T-303

Part entity with sequence checksum validation.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.sequence import FeatureV14, Sequence, Sha256, sha256_text
from domain.types.enums import ChassisClass
from domain.types.ids import PartId, SequenceOntologyTerm, require_non_empty

Licence = str
Provenance = str


@dataclass(frozen=True)
class Part:
    id: PartId
    name: str
    role: SequenceOntologyTerm
    sequence: Sequence
    annotations: tuple[FeatureV14, ...]
    parent: PartId | None
    licence: Licence
    provenance: Provenance
    checksum: Sha256
    host_compatibility: frozenset[ChassisClass] = frozenset()

    def __post_init__(self) -> None:
        require_non_empty(str(self.id), "part id")
        require_non_empty(self.name, "part name")
        require_non_empty(str(self.role), "part role")
        require_non_empty(self.licence, "licence")
        require_non_empty(self.provenance, "provenance")
        expected_checksum = sha256_text(self.sequence.body)
        if self.checksum != expected_checksum:
            raise ValueError("part checksum must match the part sequence")
        for annotation in self.annotations:
            if annotation.parent_sequence_id != str(self.id):
                raise ValueError("part annotations must reference the part id")
