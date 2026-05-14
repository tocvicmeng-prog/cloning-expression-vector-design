"""
module_id: tests.engine.codon.test_optimiser_t701
file: tests/engine/codon/test_optimiser_t701.py
task_id: T-701
"""

from __future__ import annotations

import pytest

from engine.codon import (
    DEFAULT_CODON_USAGE_TABLE,
    CodingSequenceDesign,
    CodonAlgorithmName,
    CodonOptimiser,
    FunctionalRnaFeature,
    ProtectedInterval,
    direct_repeat_count,
    homopolymer_run_length,
    translate,
    windowed_gc_fraction,
)


def test_cai_optimisation_preserves_protein_and_protected_intervals() -> None:
    original = "ATGGCTGATGAACTT"
    usage = _usage_table({"GCC": 1.0, "GAC": 1.0, "GAG": 1.0, "CTG": 1.0})

    result = CodonOptimiser().optimise(
        CodingSequenceDesign(
            sequence=original,
            algorithm="cai",
            host_codon_usage=usage,
            protected_intervals=(ProtectedInterval(0, 3, "start codon"),),
        )
    )

    assert result.sequence.startswith("ATG")
    assert result.sequence != original
    assert result.protein_preserved
    assert translate(result.sequence) == "MADEL"
    assert result.metrics_after.cai >= result.metrics_before.cai
    assert result.protected_intervals_preserved


def test_avoid_only_removes_forbidden_motif_without_changing_unneeded_codons() -> None:
    original = "ATGGCTGATGAA"

    result = CodonOptimiser().optimise(
        CodingSequenceDesign(
            sequence=original,
            algorithm="avoid_only",
            host_codon_usage=DEFAULT_CODON_USAGE_TABLE,
            avoid_motifs=("GCTGAT",),
        )
    )

    assert "GCTGAT" not in result.sequence
    assert result.sequence[:3] == original[:3]
    assert result.protein_preserved
    assert result.unresolved_motifs == ()
    assert 1 <= result.iterations <= 5


def test_functional_rna_features_are_treated_as_protected_intervals() -> None:
    original = "ATGGCTGATGAA"

    result = CodonOptimiser().optimise(
        CodingSequenceDesign(
            sequence=original,
            algorithm="cai",
            host_codon_usage=_usage_table({"GCC": 1.0, "GAC": 1.0, "GAG": 1.0}),
            functional_rna_features=(FunctionalRnaFeature(3, 9, "ribozyme-hairpin"),),
            avoid_motifs=("GCTGAT",),
        )
    )

    assert result.sequence[3:9] == "GCTGAT"
    assert result.protected_intervals_preserved
    assert result.unresolved_motifs == ("GCTGAT",)
    assert result.protein_preserved


@pytest.mark.parametrize("algorithm", ["cai", "minmax", "charming", "avoid_only"])
def test_all_declared_algorithms_are_deterministic(algorithm: CodonAlgorithmName) -> None:
    design = CodingSequenceDesign(
        sequence="ATGGCTGATGAACTT",
        algorithm=algorithm,
        host_codon_usage=_usage_table({"GCC": 1.0, "GAC": 1.0, "GAG": 1.0, "CTG": 1.0}),
        avoid_motifs=("AAAAAA",),
        target_gc_fraction=0.5,
    )

    first = CodonOptimiser().optimise(design)
    second = CodonOptimiser().optimise(design)

    assert first == second
    assert first.protein_preserved
    assert first.iterations <= 5


def test_sequence_metrics_cover_gc_windows_homopolymers_and_repeats() -> None:
    sequence = "ATGCCCATGCCC"

    assert max(windowed_gc_fraction(sequence, window_size=6)) == 0.6667
    assert homopolymer_run_length(sequence) == 3
    assert direct_repeat_count(sequence, repeat_size=6) == 1


def test_invalid_sequences_and_out_of_range_protection_are_rejected() -> None:
    with pytest.raises(ValueError, match="divisible by three"):
        CodonOptimiser().optimise(
            CodingSequenceDesign(
                sequence="ATGG",
                algorithm="cai",
                host_codon_usage=DEFAULT_CODON_USAGE_TABLE,
            )
        )

    with pytest.raises(ValueError, match="exceeds sequence length"):
        CodonOptimiser().optimise(
            CodingSequenceDesign(
                sequence="ATGGCT",
                algorithm="cai",
                host_codon_usage=DEFAULT_CODON_USAGE_TABLE,
                protected_intervals=(ProtectedInterval(0, 99),),
            )
        )


def _usage_table(overrides: dict[str, float]) -> dict[str, float]:
    table = dict(DEFAULT_CODON_USAGE_TABLE)
    table.update(overrides)
    return table
