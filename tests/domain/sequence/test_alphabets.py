"""
module_id: tests.domain.sequence
file: tests/domain/sequence/test_alphabets.py
task_id: T-301
"""

from __future__ import annotations

import pytest

from domain.sequence import (
    DnaSequence,
    OligoSequence,
    ProteinSequence,
    RnaSequence,
    SequenceValidationFlags,
)


def test_dna_sequence_uppercases_and_counts_length() -> None:
    sequence = DnaSequence("acgtn")

    assert sequence.body == "ACGTN"
    assert len(sequence) == 5


def test_dna_sequence_rejects_rna_symbol() -> None:
    with pytest.raises(ValueError, match="invalid DNA"):
        DnaSequence("ACGU")


def test_ambiguous_symbols_can_be_disallowed() -> None:
    with pytest.raises(ValueError, match="invalid DNA"):
        DnaSequence("ACGN", validation=SequenceValidationFlags(allow_ambiguous=False))


def test_rna_sequence_accepts_u_and_rejects_t() -> None:
    assert RnaSequence("acgu").body == "ACGU"
    with pytest.raises(ValueError, match="invalid RNA"):
        RnaSequence("ACGT")


def test_protein_sequence_accepts_stop_symbol() -> None:
    assert ProteinSequence("Mst*").body == "MST*"


def test_oligo_sequence_accepts_mixed_dna_rna_symbols_and_gap() -> None:
    sequence = OligoSequence("acgu-", validation=SequenceValidationFlags(allow_gap=True))

    assert sequence.body == "ACGU-"


def test_empty_sequence_is_rejected() -> None:
    with pytest.raises(ValueError, match="empty"):
        DnaSequence("")
