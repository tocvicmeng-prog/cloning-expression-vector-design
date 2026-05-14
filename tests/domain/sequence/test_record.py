"""
module_id: tests.domain.sequence
file: tests/domain/sequence/test_record.py
task_id: T-301
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from domain.sequence import (
    DnaSequence,
    MoleculeType,
    RnaSequence,
    SequenceRecord,
    canonical_rotation,
    sha256_text,
)

DNA_TEXT = st.text(alphabet="ACGT", min_size=1, max_size=64)


def _rotate(body: str, offset: int) -> str:
    offset %= len(body)
    return body[offset:] + body[:offset]


@settings(max_examples=1000, suppress_health_check=(HealthCheck.too_slow,))
@given(DNA_TEXT, st.integers(min_value=0, max_value=128))
def test_circular_sequence_checksum_is_rotation_invariant(body: str, offset: int) -> None:
    original = SequenceRecord(
        id="plasmid",
        sequence=DnaSequence(body),
        topology="circular",
        molecule_type=MoleculeType.DS_DNA,
    )
    rotated = SequenceRecord(
        id="plasmid-rotated",
        sequence=DnaSequence(_rotate(body, offset)),
        topology="circular",
        molecule_type=MoleculeType.DS_DNA,
    )

    assert original.checksum == rotated.checksum
    assert original.canonical_sequence == rotated.canonical_sequence


@settings(max_examples=1000, suppress_health_check=(HealthCheck.too_slow,))
@given(DNA_TEXT)
def test_circular_canonical_sequence_is_lexicographic_minimum_rotation(body: str) -> None:
    assert canonical_rotation(body) == min(_rotate(body, offset) for offset in range(len(body)))


def test_linear_sequence_checksum_uses_supplied_orientation() -> None:
    record = SequenceRecord(
        id="linear",
        sequence=DnaSequence("GTAC"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )

    assert record.canonical_sequence == "GTAC"
    assert record.checksum == sha256_text("GTAC")


def test_sequence_record_round_trips_through_dict() -> None:
    record = SequenceRecord(
        id="record-1",
        sequence=DnaSequence("CGTA"),
        topology="circular",
        molecule_type=MoleculeType.DS_DNA,
    )

    assert SequenceRecord.from_dict(record.to_dict()).to_dict() == record.to_dict()


def test_rna_sequence_record_round_trips_through_dict() -> None:
    record = SequenceRecord(
        id="rna-record",
        sequence=RnaSequence("ACGU"),
        topology="linear",
        molecule_type=MoleculeType.MRNA,
    )

    assert SequenceRecord.from_dict(record.to_dict()).to_dict() == record.to_dict()


def test_canonical_rotation_rejects_empty_body() -> None:
    with pytest.raises(ValueError, match="empty"):
        canonical_rotation("")


def test_sequence_record_rejects_empty_id() -> None:
    with pytest.raises(ValueError, match="id"):
        SequenceRecord(
            id="",
            sequence=DnaSequence("ACGT"),
            topology="linear",
            molecule_type=MoleculeType.DS_DNA,
        )
