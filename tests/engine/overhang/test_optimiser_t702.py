"""
module_id: tests.engine.overhang
file: tests/engine/overhang/test_optimiser_t702.py
task_id: T-702
"""

from __future__ import annotations

import time

import pytest

from engine.overhang import (
    POTAPOV_2018_HIGH_FIDELITY_SETS,
    PRYOR_2020_24_FRAGMENT_BENCHMARK,
    PRYOR_2020_GOLDEN_GATE,
    OverhangDesignRequest,
    OverhangSetOptimiser,
    all_overhang_candidates,
    canonical_overhang,
    is_palindromic,
    normalise_overhang,
    reverse_complement,
    score_overhang_set,
)


def test_overhang_normalisation_and_reverse_complement_helpers() -> None:
    assert normalise_overhang(" aatg ") == "AATG"
    assert reverse_complement("AATG") == "CATT"
    assert canonical_overhang("CATT") == "AATG"
    assert is_palindromic("ATAT")

    with pytest.raises(ValueError, match="non-DNA"):
        normalise_overhang("AARG")


def test_candidate_enumerator_returns_non_palindromic_canonical_fourmers() -> None:
    candidates = all_overhang_candidates()

    assert len(candidates) == 120
    assert "ATAT" not in candidates
    assert all(not is_palindromic(candidate) for candidate in candidates)
    assert all(candidate <= reverse_complement(candidate) for candidate in candidates)


def test_score_uses_product_of_per_overhang_fidelity() -> None:
    high_fidelity = POTAPOV_2018_HIGH_FIDELITY_SETS[15]
    score = score_overhang_set(high_fidelity, PRYOR_2020_GOLDEN_GATE)

    product = 1.0
    for per_overhang in score.per_overhang:
        product *= per_overhang.fidelity

    assert score.fidelity == pytest.approx(product)
    assert score.palindrome_count == 0
    assert score.reverse_complement_conflict_count == 0
    assert score.fidelity > 0.95


def test_score_penalises_palindromes_and_reverse_complement_conflicts() -> None:
    clean_score = score_overhang_set(("AATG", "GCTT", "CGAA"), PRYOR_2020_GOLDEN_GATE)
    conflicted_score = score_overhang_set(("AATG", "CATT", "ATAT"), PRYOR_2020_GOLDEN_GATE)

    assert conflicted_score.reverse_complement_conflict_count == 1
    assert conflicted_score.palindrome_count == 1
    assert conflicted_score.fidelity < clean_score.fidelity


def test_branch_and_bound_selects_best_small_set_and_respects_filters() -> None:
    optimiser = OverhangSetOptimiser()
    result = optimiser.optimise(
        OverhangDesignRequest(
            set_size=4,
            candidate_overhangs=(
                "AATG",
                "GCTT",
                "CGAA",
                "ATAT",
                "CATT",
                "GGCT",
                "AGCC",
                "CTAA",
            ),
            required_overhangs=("AATG",),
            excluded_overhangs=("GGCT",),
            max_pair_crosstalk=0.02,
        )
    )

    assert "AATG" in result.overhangs
    assert "GGCT" not in result.overhangs
    assert "ATAT" not in result.overhangs
    assert "CATT" not in result.overhangs
    assert result.exhaustive
    assert result.nodes_visited > 0
    assert result.score.worst_pair_crosstalk <= 0.02


def test_optimiser_reproduces_pryor_2020_24_fragment_benchmark() -> None:
    optimiser = OverhangSetOptimiser()
    result = optimiser.optimise(
        OverhangDesignRequest(
            set_size=len(PRYOR_2020_24_FRAGMENT_BENCHMARK.overhangs),
            candidate_overhangs=PRYOR_2020_24_FRAGMENT_BENCHMARK.overhangs,
            minimum_fidelity=PRYOR_2020_24_FRAGMENT_BENCHMARK.expected_fidelity_floor,
            minimum_per_overhang_fidelity=0.99,
            max_pair_crosstalk=0.02,
        )
    )

    assert result.overhangs == PRYOR_2020_24_FRAGMENT_BENCHMARK.overhangs
    assert result.fidelity >= PRYOR_2020_24_FRAGMENT_BENCHMARK.expected_fidelity_floor
    assert not result.warnings


def test_twenty_fragment_request_stays_inside_performance_budget() -> None:
    optimiser = OverhangSetOptimiser()
    started = time.perf_counter()

    result = optimiser.optimise(
        OverhangDesignRequest(
            set_size=20,
            candidate_overhangs=POTAPOV_2018_HIGH_FIDELITY_SETS[30],
            minimum_fidelity=0.90,
            minimum_per_overhang_fidelity=0.99,
            max_pair_crosstalk=0.02,
            node_budget=80_000,
        )
    )

    elapsed = time.perf_counter() - started
    assert len(result.overhangs) == 20
    assert result.fidelity >= 0.90
    assert elapsed < 5.0


def test_threshold_failures_are_reported_when_directly_scoring() -> None:
    optimiser = OverhangSetOptimiser()
    result = optimiser.optimise(
        OverhangDesignRequest(
            set_size=3,
            candidate_overhangs=("GGCT", "CTTG", "AAAA"),
            minimum_fidelity=0.9995,
            max_pair_crosstalk=0.02,
        )
    )

    assert result.fidelity < 0.9995
    assert result.warnings == ("set fidelity is below the requested threshold",)
