"""
module_id: engine.codon.algorithms
file: src/engine/codon/algorithms.py
task_id: T-701

Pure deterministic codon optimisation algorithms and sequence metrics.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from itertools import pairwise

from engine.codon.types import CodonAlgorithmName, ProtectedInterval

CODON_TO_AA = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

AA_TO_CODONS: dict[str, tuple[str, ...]] = {}
for _codon, _aa in CODON_TO_AA.items():
    AA_TO_CODONS.setdefault(_aa, ())
    AA_TO_CODONS[_aa] = (*AA_TO_CODONS[_aa], _codon)

DEFAULT_CODON_USAGE_TABLE = {
    codon: 0.2 + ((codon.count("G") + codon.count("C")) / 3)
    for codon in CODON_TO_AA
}
for _aa, _synonyms in AA_TO_CODONS.items():
    _preferred = sorted(
        _synonyms,
        key=lambda codon: (-((codon.count("G") + codon.count("C")) / 3), codon),
    )[0]
    DEFAULT_CODON_USAGE_TABLE[_preferred] = 1.0


def normalise_dna(sequence: str) -> str:
    letters = "".join(sequence.upper().split()).replace("U", "T")
    invalid = sorted(set(letters) - set("ACGT"))
    if invalid:
        raise ValueError(f"invalid coding DNA symbols: {''.join(invalid)}")
    if len(letters) % 3:
        raise ValueError("coding sequence length must be divisible by three")
    for codon in _codons(letters):
        if codon not in CODON_TO_AA:
            raise ValueError(f"unsupported codon: {codon}")
    return letters


def translate(sequence: str) -> str:
    dna = normalise_dna(sequence)
    return "".join(CODON_TO_AA[dna[index : index + 3]] for index in range(0, len(dna), 3))


def gc_fraction(sequence: str) -> float:
    if not sequence:
        return 0.0
    dna = "".join(sequence.upper().split()).replace("U", "T")
    return (dna.count("G") + dna.count("C")) / len(dna)


def windowed_gc_fraction(sequence: str, *, window_size: int = 50) -> tuple[float, ...]:
    dna = "".join(sequence.upper().split()).replace("U", "T")
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    if len(dna) <= window_size:
        return (round(gc_fraction(dna), 4),)
    return tuple(
        round(gc_fraction(dna[index : index + window_size]), 4)
        for index in range(0, len(dna) - window_size + 1)
    )


def homopolymer_run_length(sequence: str) -> int:
    dna = "".join(sequence.upper().split()).replace("U", "T")
    if not dna:
        return 0
    best = 1
    current = 1
    for left, right in pairwise(dna):
        if left == right:
            current += 1
        else:
            best = max(best, current)
            current = 1
    return max(best, current)


def direct_repeat_count(sequence: str, *, repeat_size: int = 6) -> int:
    dna = "".join(sequence.upper().split()).replace("U", "T")
    if repeat_size <= 0:
        raise ValueError("repeat_size must be positive")
    seen: dict[str, int] = {}
    for index in range(0, max(0, len(dna) - repeat_size + 1)):
        repeat = dna[index : index + repeat_size]
        seen[repeat] = seen.get(repeat, 0) + 1
    return sum(count - 1 for count in seen.values() if count > 1)


def cai_score(sequence: str, usage_table: Mapping[str, float]) -> float:
    dna = normalise_dna(sequence)
    weights: list[float] = []
    for codon in _codons(dna):
        aa = CODON_TO_AA[codon]
        codon_weight = _usage_weight(codon, usage_table)
        max_weight = max(_usage_weight(item, usage_table) for item in AA_TO_CODONS[aa])
        weights.append(codon_weight / max_weight if max_weight > 0 else 0.0)
    if not weights:
        return 0.0
    product = math.prod(max(weight, 1e-9) for weight in weights)
    return round(product ** (1 / len(weights)), 4)


def optimise_algorithm_once(
    sequence: str,
    *,
    algorithm: CodonAlgorithmName,
    usage_table: Mapping[str, float],
    protected_intervals: tuple[ProtectedInterval, ...],
    target_gc_fraction: float | None,
) -> str:
    dna = normalise_dna(sequence)
    codons = list(_codons(dna))
    output: list[str] = []
    for index, codon in enumerate(codons):
        aa = CODON_TO_AA[codon]
        if _codon_is_protected(index, protected_intervals) or algorithm == "avoid_only":
            output.append(codon)
        elif algorithm == "cai":
            output.append(_best_usage_codon(aa, usage_table))
        elif algorithm == "minmax":
            output.append(_minmax_codon(codon, usage_table))
        else:
            output.append(
                _charming_codon(
                    aa,
                    usage_table,
                    target_gc_fraction=target_gc_fraction,
                    previous=output[-1] if output else "",
                )
            )
    return "".join(output)


def remove_avoided_motif_once(
    sequence: str,
    *,
    avoid_motifs: tuple[str, ...],
    protected_intervals: tuple[ProtectedInterval, ...],
    usage_table: Mapping[str, float],
) -> str:
    dna = normalise_dna(sequence)
    motifs = tuple(normalise_motif(motif) for motif in avoid_motifs if motif)
    codons = list(_codons(dna))
    for motif in motifs:
        start = dna.find(motif)
        if start < 0:
            continue
        for codon_index in _codon_indices_overlapping(start, start + len(motif)):
            if codon_index >= len(codons) or _codon_is_protected(codon_index, protected_intervals):
                continue
            aa = CODON_TO_AA[codons[codon_index]]
            alternatives = sorted(
                (item for item in AA_TO_CODONS[aa] if item != codons[codon_index]),
                key=lambda item: (-_usage_weight(item, usage_table), item),
            )
            for alternative in alternatives:
                trial = [*codons]
                trial[codon_index] = alternative
                trial_sequence = "".join(trial)
                if motif not in trial_sequence:
                    return trial_sequence
    return dna


def unresolved_motifs(sequence: str, avoid_motifs: tuple[str, ...]) -> tuple[str, ...]:
    dna = normalise_dna(sequence)
    return tuple(
        motif for motif in (normalise_motif(item) for item in avoid_motifs) if motif in dna
    )


def normalise_motif(motif: str) -> str:
    letters = "".join(motif.upper().split()).replace("U", "T")
    invalid = sorted(set(letters) - set("ACGT"))
    if invalid:
        raise ValueError(f"invalid DNA motif symbols: {''.join(invalid)}")
    return letters


def changed_codons(left: str, right: str) -> int:
    left_dna = normalise_dna(left)
    right_dna = normalise_dna(right)
    if len(left_dna) != len(right_dna):
        raise ValueError("cannot compare coding sequences with different lengths")
    return sum(
        1
        for index in range(0, len(left_dna), 3)
        if left_dna[index : index + 3] != right_dna[index : index + 3]
    )


def _best_usage_codon(aa: str, usage_table: Mapping[str, float]) -> str:
    return sorted(
        AA_TO_CODONS[aa],
        key=lambda codon: (-_usage_weight(codon, usage_table), codon),
    )[0]


def _minmax_codon(native_codon: str, usage_table: Mapping[str, float]) -> str:
    aa = CODON_TO_AA[native_codon]
    ranked = _ranked_codons(aa, usage_table)
    native_rank = ranked.index(native_codon) if native_codon in ranked else len(ranked) // 2
    target_rank = min(native_rank, len(ranked) - 1)
    return ranked[target_rank]


def _charming_codon(
    aa: str,
    usage_table: Mapping[str, float],
    *,
    target_gc_fraction: float | None,
    previous: str,
) -> str:
    target_gc = 0.5 if target_gc_fraction is None else target_gc_fraction
    ranked = sorted(
        AA_TO_CODONS[aa],
        key=lambda codon: (
            abs(gc_fraction(codon) - target_gc),
            -_usage_weight(codon, usage_table),
            codon[-1] == previous[-1:] if previous else False,
            codon,
        ),
    )
    return ranked[0]


def _ranked_codons(aa: str, usage_table: Mapping[str, float]) -> tuple[str, ...]:
    return tuple(
        sorted(
            AA_TO_CODONS[aa],
            key=lambda codon: (-_usage_weight(codon, usage_table), codon),
        )
    )


def _usage_weight(codon: str, usage_table: Mapping[str, float]) -> float:
    value = usage_table.get(codon, DEFAULT_CODON_USAGE_TABLE[codon])
    if value <= 0:
        return 1e-9
    return float(value)


def _codons(sequence: str) -> tuple[str, ...]:
    return tuple(sequence[index : index + 3] for index in range(0, len(sequence), 3))


def _codon_is_protected(
    codon_index: int,
    protected_intervals: tuple[ProtectedInterval, ...],
) -> bool:
    start = codon_index * 3
    end = start + 3
    return any(interval.overlaps(start, end) for interval in protected_intervals)


def _codon_indices_overlapping(start: int, end: int) -> Iterable[int]:
    first = start // 3
    last = (end - 1) // 3
    return range(first, last + 1)


__all__ = [
    "AA_TO_CODONS",
    "CODON_TO_AA",
    "DEFAULT_CODON_USAGE_TABLE",
    "cai_score",
    "changed_codons",
    "direct_repeat_count",
    "gc_fraction",
    "homopolymer_run_length",
    "normalise_dna",
    "normalise_motif",
    "optimise_algorithm_once",
    "remove_avoided_motif_once",
    "translate",
    "unresolved_motifs",
    "windowed_gc_fraction",
]
