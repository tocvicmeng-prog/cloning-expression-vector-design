"""
module_id: adapter.biology.codon_support
file: src/adapter/biology/codon_support.py
task_id: T-601f..k

Shared deterministic codon-optimisation helpers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from adapter.biology.common import Payload, gc_fraction, normalise_dna

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

PREFERRED_CODON = {
    aa: sorted(codons, key=lambda codon: (-gc_fraction(codon), codon))[0]
    for aa, codons in AA_TO_CODONS.items()
}
RARE_CODON = {
    aa: sorted(codons, key=lambda codon: (gc_fraction(codon), codon))[0]
    for aa, codons in AA_TO_CODONS.items()
}


def translate(sequence: str) -> str:
    dna = normalise_dna(sequence)
    if len(dna) % 3:
        raise ValueError("coding sequence length must be divisible by three")
    return "".join(CODON_TO_AA.get(dna[index : index + 3], "X") for index in range(0, len(dna), 3))


def optimise_payload(design: Mapping[str, object], *, strategy: str) -> Payload:
    sequence_value = design.get("sequence", "")
    if not isinstance(sequence_value, str):
        raise TypeError("coding_sequence_design['sequence'] must be a string")
    original = normalise_dna(sequence_value)
    protected = _protected_intervals(design.get("protected_intervals", ()))
    avoid = _avoid_motifs(design.get("avoid_motifs", ()))
    optimised = _optimise_sequence(
        original,
        strategy=strategy,
        protected=protected,
        avoid_motifs=avoid,
    )
    return {
        "algorithm": strategy,
        "input_sequence": original,
        "sequence": optimised,
        "protein": translate(optimised),
        "protein_preserved": translate(original) == translate(optimised),
        "changed_codons": _changed_codons(original, optimised),
        "gc_fraction": round(gc_fraction(optimised), 4),
    }


def _optimise_sequence(
    sequence: str,
    *,
    strategy: str,
    protected: tuple[tuple[int, int], ...],
    avoid_motifs: tuple[str, ...],
) -> str:
    codons = [sequence[index : index + 3] for index in range(0, len(sequence), 3)]
    new_codons: list[str] = []
    for index, codon in enumerate(codons):
        aa = CODON_TO_AA[codon]
        if _codon_is_protected(index, protected):
            new_codons.append(codon)
        elif strategy == "minmax" and index % 2:
            new_codons.append(RARE_CODON[aa])
        elif strategy == "charming":
            new_codons.append(_balanced_codon(aa, previous=new_codons[-1] if new_codons else ""))
        else:
            new_codons.append(PREFERRED_CODON[aa])
    optimised = "".join(new_codons)
    if strategy == "avoid_only":
        optimised = sequence
    if avoid_motifs:
        optimised = _remove_avoided_motifs(
            optimised,
            protected=protected,
            avoid_motifs=avoid_motifs,
        )
    return optimised


def _remove_avoided_motifs(
    sequence: str,
    *,
    protected: tuple[tuple[int, int], ...],
    avoid_motifs: tuple[str, ...],
) -> str:
    codons = [sequence[index : index + 3] for index in range(0, len(sequence), 3)]
    for _ in range(4):
        current = "".join(codons)
        hit = next((motif for motif in avoid_motifs if motif in current), "")
        if not hit:
            break
        start = current.find(hit)
        codon_index = start // 3
        if _codon_is_protected(codon_index, protected):
            break
        aa = CODON_TO_AA[codons[codon_index]]
        alternatives = [codon for codon in AA_TO_CODONS[aa] if codon != codons[codon_index]]
        for alternative in alternatives:
            trial = [*codons]
            trial[codon_index] = alternative
            if hit not in "".join(trial):
                codons = trial
                break
        else:
            break
    return "".join(codons)


def _balanced_codon(aa: str, *, previous: str) -> str:
    codons = sorted(AA_TO_CODONS[aa], key=lambda codon: (abs(gc_fraction(codon) - 0.5), codon))
    if previous and codons[0][-1:] == previous[-1:]:
        return codons[min(1, len(codons) - 1)]
    return codons[0]


def _codon_is_protected(codon_index: int, protected: tuple[tuple[int, int], ...]) -> bool:
    codon_start = codon_index * 3
    codon_end = codon_start + 3
    return any(codon_start < end and start < codon_end for start, end in protected)


def _protected_intervals(value: object) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ()
    intervals: list[tuple[int, int]] = []
    for item in value:
        if isinstance(item, Mapping):
            start = item.get("start")
            end = item.get("end")
            if isinstance(start, int) and isinstance(end, int) and 0 <= start < end:
                intervals.append((start, end))
        elif isinstance(item, Sequence) and not isinstance(item, str) and len(item) == 2:
            start, end = item
            if isinstance(start, int) and isinstance(end, int) and 0 <= start < end:
                intervals.append((start, end))
    return tuple(intervals)


def _avoid_motifs(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ()
    return tuple(normalise_dna(item) for item in value if isinstance(item, str) and item)


def _changed_codons(left: str, right: str) -> int:
    return sum(
        1 for index in range(0, len(left), 3) if left[index : index + 3] != right[index : index + 3]
    )
