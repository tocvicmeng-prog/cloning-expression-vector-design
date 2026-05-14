"""
module_id: domain.sequence
file: src/domain/sequence/alphabets.py
task_id: T-301

Sequence alphabets and validated sequence value objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Alphabet(Enum):
    DNA = "DNA"
    RNA = "RNA"
    PROTEIN = "PROTEIN"
    OLIGO = "OLIGO"


class MoleculeType(Enum):
    DS_DNA = "ds-DNA"
    SS_DNA = "ss-DNA"
    MRNA = "mRNA"
    GRNA = "gRNA"
    OTHER_RNA = "RNA"
    PROTEIN = "protein"
    OLIGO_PRIMER = "primer"
    OLIGO_PROBE = "probe"


@dataclass(frozen=True)
class SequenceValidationFlags:
    allow_ambiguous: bool = True
    allow_gap: bool = False


DNA_BASES = frozenset("ACGT")
DNA_AMBIGUOUS = frozenset("RYSWKMBDHVN")
RNA_BASES = frozenset("ACGU")
RNA_AMBIGUOUS = frozenset("RYSWKMBDHVN")
PROTEIN_BASES = frozenset("ABCDEFGHIKLMNPQRSTVWXYZ*")
GAP = frozenset("-")


def _allowed_symbols(alphabet: Alphabet, flags: SequenceValidationFlags) -> frozenset[str]:
    if alphabet is Alphabet.DNA:
        allowed = DNA_BASES | (DNA_AMBIGUOUS if flags.allow_ambiguous else frozenset())
    elif alphabet is Alphabet.RNA:
        allowed = RNA_BASES | (RNA_AMBIGUOUS if flags.allow_ambiguous else frozenset())
    elif alphabet is Alphabet.PROTEIN:
        allowed = PROTEIN_BASES
    else:
        allowed = DNA_BASES | RNA_BASES | (DNA_AMBIGUOUS if flags.allow_ambiguous else frozenset())
    return allowed | (GAP if flags.allow_gap else frozenset())


@dataclass(frozen=True)
class Sequence:
    alphabet: Alphabet
    body: str
    validation: SequenceValidationFlags = field(default_factory=SequenceValidationFlags)

    def __post_init__(self) -> None:
        body = self.body.upper()
        if not body:
            raise ValueError("sequence body cannot be empty")
        invalid = sorted(set(body) - _allowed_symbols(self.alphabet, self.validation))
        if invalid:
            invalid_text = "".join(invalid)
            raise ValueError(f"invalid {self.alphabet.value} sequence symbols: {invalid_text}")
        object.__setattr__(self, "body", body)

    def __len__(self) -> int:
        return len(self.body)


@dataclass(frozen=True)
class DnaSequence(Sequence):
    alphabet: Alphabet = field(default=Alphabet.DNA, init=False)


@dataclass(frozen=True)
class RnaSequence(Sequence):
    alphabet: Alphabet = field(default=Alphabet.RNA, init=False)


@dataclass(frozen=True)
class ProteinSequence(Sequence):
    alphabet: Alphabet = field(default=Alphabet.PROTEIN, init=False)


@dataclass(frozen=True)
class OligoSequence(Sequence):
    alphabet: Alphabet = field(default=Alphabet.OLIGO, init=False)
