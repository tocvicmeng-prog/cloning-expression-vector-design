"""
module_id: domain.sequence
file: src/domain/sequence/record.py
task_id: T-301

Topology-aware sequence records and typed hashes.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, NewType

from domain.sequence.alphabets import Alphabet, DnaSequence, MoleculeType, Sequence

Sha256 = NewType("Sha256", str)
Topology = Literal["linear", "circular"]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_text(text: str) -> Sha256:
    return Sha256(hashlib.sha256(text.encode("utf-8")).hexdigest())


def _validate_sha256(value: Sha256, field_name: str) -> None:
    if SHA256_RE.fullmatch(str(value)) is None:
        raise ValueError(f"{field_name} must be a lowercase SHA-256 hex digest")


def canonical_rotation(body: str) -> str:
    if not body:
        raise ValueError("cannot canonicalise an empty circular sequence")
    doubled = body + body
    return min(doubled[index : index + len(body)] for index in range(len(body)))


@dataclass(frozen=True)
class SequenceRecord:
    id: str
    sequence: Sequence
    topology: Topology
    molecule_type: MoleculeType
    canonical_sequence: str = field(init=False)
    length: int = field(init=False)
    checksum: Sha256 = field(init=False)
    canonical_strand: Literal["+", "-"] = field(default="+", init=False)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("sequence record id cannot be empty")
        canonical = (
            canonical_rotation(self.sequence.body)
            if self.topology == "circular"
            else self.sequence.body
        )
        object.__setattr__(self, "canonical_sequence", canonical)
        object.__setattr__(self, "length", len(self.sequence))
        object.__setattr__(self, "checksum", sha256_text(canonical))

    @property
    def alphabet(self) -> Alphabet:
        return self.sequence.alphabet

    def to_dict(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "alphabet": self.alphabet.value,
            "topology": self.topology,
            "molecule_type": self.molecule_type.value,
            "sequence": self.canonical_sequence,
            "length": self.length,
            "checksum": str(self.checksum),
            "canonical_strand": self.canonical_strand,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, str | int]) -> SequenceRecord:
        alphabet = Alphabet(str(payload["alphabet"]))
        if alphabet is not Alphabet.DNA:
            sequence = Sequence(alphabet=alphabet, body=str(payload["sequence"]))
        else:
            sequence = DnaSequence(str(payload["sequence"]))
        return cls(
            id=str(payload["id"]),
            sequence=sequence,
            topology=str(payload["topology"]),  # type: ignore[arg-type]
            molecule_type=MoleculeType(str(payload["molecule_type"])),
        )


class ReverseComplementEquivalence(Enum):
    EQUIVALENT = "equivalent"
    DISTINCT = "distinct"


@dataclass(frozen=True)
class ConstructHashes:
    sequence_hash: Sha256
    topology_hash: Sha256
    annotation_hash: Sha256
    construct_graph_hash: Sha256
    export_bundle_hash: Sha256

    def __post_init__(self) -> None:
        _validate_sha256(self.sequence_hash, "sequence_hash")
        _validate_sha256(self.topology_hash, "topology_hash")
        _validate_sha256(self.annotation_hash, "annotation_hash")
        _validate_sha256(self.construct_graph_hash, "construct_graph_hash")
        _validate_sha256(self.export_bundle_hash, "export_bundle_hash")
