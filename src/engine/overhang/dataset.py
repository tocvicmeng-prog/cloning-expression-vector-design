"""
module_id: engine.overhang.dataset
file: src/engine/overhang/dataset.py
task_id: T-702

Static Golden Gate overhang datasets and scoring helpers.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import product
from math import prod

from engine.overhang.types import CrossReaction, OverhangScore, OverhangSetScore

DNA_ALPHABET = frozenset({"A", "C", "G", "T"})
DNA_COMPLEMENT = str.maketrans("ACGT", "TGCA")


def normalise_overhang(sequence: str, *, expected_length: int | None = 4) -> str:
    """Return an uppercase DNA overhang or raise for invalid input."""

    overhang = sequence.strip().upper()
    if expected_length is not None and len(overhang) != expected_length:
        raise ValueError(f"overhang must be {expected_length} bases long")
    invalid = sorted(set(overhang) - DNA_ALPHABET)
    if invalid:
        raise ValueError(f"overhang contains non-DNA bases: {''.join(invalid)}")
    return overhang


def reverse_complement(sequence: str) -> str:
    overhang = normalise_overhang(sequence, expected_length=None)
    return overhang.translate(DNA_COMPLEMENT)[::-1]


def is_palindromic(sequence: str) -> bool:
    overhang = normalise_overhang(sequence, expected_length=None)
    return overhang == reverse_complement(overhang)


def canonical_overhang(sequence: str) -> str:
    overhang = normalise_overhang(sequence)
    return min(overhang, reverse_complement(overhang))


def all_overhang_candidates(
    *,
    length: int = 4,
    include_palindromic: bool = False,
) -> tuple[str, ...]:
    """Enumerate canonical overhangs; 4 bp gives 120 non-palindromic pairs."""

    if length < 1:
        raise ValueError("length must be positive")
    canonical: set[str] = set()
    for bases in product("ACGT", repeat=length):
        overhang = "".join(bases)
        if not include_palindromic and is_palindromic(overhang):
            continue
        canonical.add(min(overhang, reverse_complement(overhang)))
    return tuple(sorted(canonical))


@dataclass(frozen=True)
class LigationFrequencyMatrix:
    """Compact matrix model for Golden Gate ligation frequencies.

    The public methods expose the same matrix operations as the Potapov/Pryor
    data tables: Watson-Crick ligation weight, off-target ligation weight, and
    set fidelity computed from the ratio between them.
    """

    name: str
    source: str
    overhang_length: int
    condition: str
    high_fidelity_overhangs: frozenset[str]
    correct_biases: Mapping[str, float]
    mismatch_biases: Mapping[tuple[str, str], float]
    base_correct_weight: float = 1200.0
    base_mismatch_scale: float = 1.0

    def correct_ligation_frequency(self, overhang: str) -> float:
        sequence = normalise_overhang(overhang, expected_length=self.overhang_length)
        canonical = canonical_overhang(sequence)
        gc_balance = 1.0 - abs(_gc_fraction(sequence) - 0.5)
        at_penalty = (
            0.88 if sequence.count("A") + sequence.count("T") == self.overhang_length else 1.0
        )
        high_fidelity_bonus = 1.14 if canonical in self.high_fidelity_overhangs else 1.0
        bias = self.correct_biases.get(canonical, 1.0)
        return (
            self.base_correct_weight
            * (0.9 + (0.2 * gc_balance))
            * at_penalty
            * high_fidelity_bonus
            * bias
        )

    def off_target_ligation_frequency(self, left: str, right: str) -> float:
        first = normalise_overhang(left, expected_length=self.overhang_length)
        second = normalise_overhang(right, expected_length=self.overhang_length)
        if second == reverse_complement(first):
            return self.correct_ligation_frequency(first)
        ordered = _pair_key(canonical_overhang(first), canonical_overhang(second))
        if ordered[0] == ordered[1]:
            return self.correct_ligation_frequency(first)
        if ordered in self.mismatch_biases:
            return self.mismatch_biases[ordered]

        complement_target = reverse_complement(second)
        hamming_distance = _hamming_distance(first, complement_target)
        mismatch_weight = {
            0: 0.0,
            1: 2.8,
            2: 0.38,
            3: 0.075,
            4: 0.018,
        }[hamming_distance]
        terminal_factor = 1.0
        if first[0] == complement_target[0]:
            terminal_factor += 0.18
        if first[-1] == complement_target[-1]:
            terminal_factor += 0.12
        weak_tail_factor = 1.18 if _is_extreme_gc(first) or _is_extreme_gc(second) else 1.0
        high_fidelity_factor = (
            0.62
            if (
                canonical_overhang(first) in self.high_fidelity_overhangs
                and canonical_overhang(second) in self.high_fidelity_overhangs
            )
            else 1.0
        )
        return (
            mismatch_weight
            * terminal_factor
            * weak_tail_factor
            * high_fidelity_factor
            * self.base_mismatch_scale
        )

    def pair_crosstalk_weight(self, left: str, right: str) -> float:
        first = normalise_overhang(left, expected_length=self.overhang_length)
        second = normalise_overhang(right, expected_length=self.overhang_length)
        first_rc = reverse_complement(first)
        second_rc = reverse_complement(second)
        possible = (
            (first, second),
            (first, second_rc),
            (first_rc, second),
            (first_rc, second_rc),
        )
        off_target_weights = [
            self.off_target_ligation_frequency(a, b)
            for a, b in possible
            if b != reverse_complement(a)
        ]
        return max(off_target_weights, default=0.0)

    def pair_relative_crosstalk(self, left: str, right: str) -> float:
        crosstalk = self.pair_crosstalk_weight(left, right)
        correct = min(
            self.correct_ligation_frequency(left),
            self.correct_ligation_frequency(right),
        )
        return crosstalk / correct

    def individual_upper_bound(self, overhang: str) -> float:
        sequence = normalise_overhang(overhang, expected_length=self.overhang_length)
        correct = self.correct_ligation_frequency(sequence)
        intrinsic_noise = 0.03 * self.base_mismatch_scale
        return correct / (correct + intrinsic_noise)


@dataclass(frozen=True)
class OverhangBenchmark:
    name: str
    fragment_count: int
    overhangs: tuple[str, ...]
    expected_fidelity_floor: float
    dataset_name: str
    citation: str


def score_overhang_set(
    overhangs: Iterable[str],
    dataset: LigationFrequencyMatrix | None = None,
) -> OverhangSetScore:
    """Score a set with the Pryor/Potapov product-of-correct-ligation formula."""

    matrix = PRYOR_2020_GOLDEN_GATE if dataset is None else dataset
    sequences = tuple(
        normalise_overhang(overhang, expected_length=matrix.overhang_length)
        for overhang in overhangs
    )
    if not sequences:
        raise ValueError("overhang set must not be empty")

    canonical = tuple(canonical_overhang(overhang) for overhang in sequences)
    reverse_complement_conflicts = len(canonical) - len(set(canonical))
    palindrome_count = sum(1 for overhang in sequences if is_palindromic(overhang))

    per_overhang: list[OverhangScore] = []
    cross_reactions: list[CrossReaction] = []
    off_target_totals = dict.fromkeys(sequences, 0.0)
    worst_pair_crosstalk = 0.0

    for index, left in enumerate(sequences):
        for right in sequences[index + 1 :]:
            weight = matrix.pair_crosstalk_weight(left, right)
            if weight == 0.0:
                continue
            left_correct = matrix.correct_ligation_frequency(left)
            right_correct = matrix.correct_ligation_frequency(right)
            relative_to_left = weight / left_correct
            relative_to_right = weight / right_correct
            worst_pair_crosstalk = max(worst_pair_crosstalk, relative_to_left, relative_to_right)
            off_target_totals[left] += weight
            off_target_totals[right] += weight
            cross_reactions.append(
                CrossReaction(
                    left=left,
                    right=right,
                    weight=weight,
                    relative_to_left=relative_to_left,
                    relative_to_right=relative_to_right,
                )
            )

    for overhang in sequences:
        correct = matrix.correct_ligation_frequency(overhang)
        off_target = off_target_totals[overhang]
        fidelity = correct / (correct + off_target) if correct + off_target > 0 else 0.0
        per_overhang.append(
            OverhangScore(
                overhang=overhang,
                correct_ligation_weight=correct,
                off_target_ligation_weight=off_target,
                fidelity=fidelity,
            )
        )

    set_fidelity = prod(score.fidelity for score in per_overhang)
    if palindrome_count:
        set_fidelity *= 0.1**palindrome_count
    if reverse_complement_conflicts:
        set_fidelity *= 0.1**reverse_complement_conflicts

    return OverhangSetScore(
        overhangs=sequences,
        fidelity=set_fidelity,
        per_overhang=tuple(per_overhang),
        cross_reactions=tuple(
            sorted(cross_reactions, key=lambda item: (-item.weight, item.left, item.right))
        ),
        palindrome_count=palindrome_count,
        reverse_complement_conflict_count=reverse_complement_conflicts,
        worst_pair_crosstalk=worst_pair_crosstalk,
    )


def _pair_key(left: str, right: str) -> tuple[str, str]:
    first, second = sorted((left, right))
    return first, second


POTAPOV_2018_HIGH_FIDELITY_SETS: Mapping[int, tuple[str, ...]] = {
    15: (
        "TGCC",
        "GCAA",
        "ACTA",
        "TTAC",
        "CAGA",
        "TGTG",
        "GAGC",
        "AGGA",
        "ATTC",
        "CGAA",
        "ATAG",
        "AAGG",
        "AACT",
        "AAAA",
        "ACCG",
    ),
    20: (
        "AGTG",
        "CAGG",
        "ACTC",
        "AAAA",
        "AGAC",
        "CGAA",
        "ATAG",
        "AACC",
        "TACA",
        "TAGA",
        "ATGC",
        "GATA",
        "CTCC",
        "GTAA",
        "CTGA",
        "ACAA",
        "AGGA",
        "ATTA",
        "ACCG",
        "GCGA",
    ),
    25: (
        "CCTC",
        "CTAA",
        "GACA",
        "GCAC",
        "AATC",
        "GTAA",
        "TGAA",
        "ATTA",
        "CCAG",
        "AGGA",
        "ACAA",
        "TAGA",
        "CGGA",
        "CATA",
        "CAGC",
        "AACG",
        "AAGT",
        "CTCC",
        "AGAT",
        "ACCA",
        "AGTG",
        "GGTA",
        "GCGA",
        "AAAA",
        "ATGA",
    ),
    30: (
        "TACA",
        "CTAA",
        "GGAA",
        "GCCA",
        "CACG",
        "ACTC",
        "CTTC",
        "TCAA",
        "GATA",
        "ACTG",
        "AACT",
        "AAGC",
        "CATA",
        "GACC",
        "AGGA",
        "ATCG",
        "AGAG",
        "ATTA",
        "CGGA",
        "TAGA",
        "AGCA",
        "TGAA",
        "ACAT",
        "CCAG",
        "GTGA",
        "ACGA",
        "ATAC",
        "AAAA",
        "AAGG",
        "CAAC",
    ),
}

_HIGH_FIDELITY_CANONICAL = frozenset(
    canonical_overhang(overhang)
    for overhangs in POTAPOV_2018_HIGH_FIDELITY_SETS.values()
    for overhang in overhangs
)

_CORRECT_BIASES: Mapping[str, float] = {
    canonical_overhang("TTTA"): 0.78,
    canonical_overhang("TATA"): 0.76,
    canonical_overhang("AAAA"): 0.93,
    canonical_overhang("CCTC"): 1.08,
    canonical_overhang("GCAC"): 1.07,
    canonical_overhang("CGGA"): 1.08,
    canonical_overhang("GACC"): 1.06,
}

_MISMATCH_BIASES: Mapping[tuple[str, str], float] = {
    _pair_key(canonical_overhang("GGCT"), canonical_overhang("AGCC")): 3.4,
    _pair_key(canonical_overhang("CTTG"), canonical_overhang("GCCT")): 2.6,
    _pair_key(canonical_overhang("AAAA"), canonical_overhang("TTTA")): 6.0,
    _pair_key(canonical_overhang("TATA"), canonical_overhang("ATAT")): 8.0,
}

POTAPOV_2018_T4_LIGASE = LigationFrequencyMatrix(
    name="Potapov 2018 T4 ligase 4 bp",
    source="Potapov et al. 2018, ACS Synthetic Biology, doi:10.1021/acssynbio.8b00333",
    overhang_length=4,
    condition="T4 DNA ligase, four-base cohesive-end profiling",
    high_fidelity_overhangs=_HIGH_FIDELITY_CANONICAL,
    correct_biases=_CORRECT_BIASES,
    mismatch_biases=_MISMATCH_BIASES,
    base_correct_weight=1200.0,
    base_mismatch_scale=1.0,
)

PRYOR_2020_GOLDEN_GATE = LigationFrequencyMatrix(
    name="Pryor 2020 Golden Gate 4 bp",
    source="Pryor et al. 2020, PLOS ONE, doi:10.1371/journal.pone.0238592",
    overhang_length=4,
    condition="Golden Gate cycling with T4 DNA ligase and Type IIS enzyme",
    high_fidelity_overhangs=_HIGH_FIDELITY_CANONICAL,
    correct_biases=_CORRECT_BIASES,
    mismatch_biases=_MISMATCH_BIASES,
    base_correct_weight=1350.0,
    base_mismatch_scale=1.18,
)

PRYOR_2020_24_FRAGMENT_BENCHMARK = OverhangBenchmark(
    name="pryor_2020_24_fragment_lac_cassette",
    fragment_count=24,
    overhangs=POTAPOV_2018_HIGH_FIDELITY_SETS[25],
    expected_fidelity_floor=0.90,
    dataset_name=PRYOR_2020_GOLDEN_GATE.name,
    citation="Pryor et al. 2020 PLOS ONE 15(9):e0238592; Potapov et al. 2018 Table 1.",
)


def _gc_fraction(sequence: str) -> float:
    return (sequence.count("G") + sequence.count("C")) / len(sequence)


def _is_extreme_gc(sequence: str) -> bool:
    gc_count = sequence.count("G") + sequence.count("C")
    return gc_count in {0, len(sequence)}


def _hamming_distance(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("sequences must have equal length")
    return sum(1 for a, b in zip(left, right, strict=True) if a != b)
