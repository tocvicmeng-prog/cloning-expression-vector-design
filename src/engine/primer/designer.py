"""
module_id: engine.primer.designer
file: src/engine/primer/designer.py
task_id: T-704

Deterministic Primer3-compatible primer design core.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Literal

from domain.sequence import SequenceRecord
from engine.assembly import AssemblyPart
from engine.primer.parameters import PrimerDesignParameters

DNA_COMPLEMENT = str.maketrans("ACGT", "TGCA")


@dataclass(frozen=True)
class OffTargetHit:
    start: int
    strand: Literal["+", "-"]
    matched_sequence: str


@dataclass(frozen=True)
class Primer:
    name: str
    sequence: str
    direction: Literal["forward", "reverse", "sequencing"]
    tm_C: float
    gc_fraction: float
    off_target_hits: tuple[OffTargetHit, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("primer name cannot be empty")
        _normalise_dna(self.sequence)


@dataclass(frozen=True)
class PrimerPair:
    target_id: str
    forward: Primer
    reverse: Primer
    product_size: int
    tm_difference_C: float
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class PrimerSet:
    pairs: tuple[PrimerPair, ...]
    backend: Literal["primer3", "deterministic-fallback"]
    warnings: tuple[str, ...] = ()


class PrimerDesigner:
    """Primer pair designer with deterministic fallback when Primer3 is unavailable."""

    def __init__(self, parameters: PrimerDesignParameters | None = None) -> None:
        self._parameters = PrimerDesignParameters() if parameters is None else parameters
        self._backend: Literal["primer3", "deterministic-fallback"] = (
            "primer3"
            if importlib.util.find_spec("primer3") is not None
            else "deterministic-fallback"
        )

    @property
    def backend(self) -> Literal["primer3", "deterministic-fallback"]:
        return self._backend

    def design_pair(
        self,
        template: str | SequenceRecord,
        *,
        target_id: str = "target",
        full_plasmid: str | SequenceRecord | None = None,
        parameters: PrimerDesignParameters | None = None,
    ) -> PrimerPair:
        resolved = self._parameters if parameters is None else parameters
        sequence = _sequence_body(template)
        if len(sequence) < resolved.length_range[0] * 2:
            raise ValueError("template is too short for primer-pair design")

        forward_sequence = _choose_forward_primer(sequence, resolved)
        reverse_sequence = _choose_reverse_primer(sequence, resolved)
        search_space = sequence if full_plasmid is None else _sequence_body(full_plasmid)
        forward_hits = scan_off_targets(forward_sequence, search_space)
        reverse_hits = scan_off_targets(reverse_sequence, search_space)
        forward = _primer("forward", f"{target_id}_fwd", forward_sequence, forward_hits)
        reverse = _primer("reverse", f"{target_id}_rev", reverse_sequence, reverse_hits)
        tm_difference = abs(forward.tm_C - reverse.tm_C)
        warnings = _pair_warnings(forward, reverse, resolved)
        return PrimerPair(
            target_id=target_id,
            forward=forward,
            reverse=reverse,
            product_size=len(sequence),
            tm_difference_C=tm_difference,
            warnings=warnings,
        )

    def design_for_parts(
        self,
        parts: tuple[AssemblyPart, ...],
        *,
        full_plasmid: str | SequenceRecord | None = None,
        parameters: PrimerDesignParameters | None = None,
    ) -> PrimerSet:
        if not parts:
            raise ValueError("at least one assembly part is required")
        pairs = tuple(
            self.design_pair(
                part.sequence,
                target_id=part.id,
                full_plasmid=full_plasmid,
                parameters=parameters,
            )
            for part in parts
        )
        warnings = tuple(warning for pair in pairs for warning in pair.warnings)
        return PrimerSet(pairs=pairs, backend=self.backend, warnings=warnings)


def scan_off_targets(
    primer_sequence: str,
    template: str | SequenceRecord,
    *,
    seed_length: int = 12,
) -> tuple[OffTargetHit, ...]:
    primer = _normalise_dna(primer_sequence)
    if seed_length < 4:
        raise ValueError("seed_length must be at least 4")
    seed = primer[-min(seed_length, len(primer)) :]
    reverse_seed = reverse_complement(seed)
    body = _sequence_body(template)
    hits: list[OffTargetHit] = []
    for start in _find_all(body, seed):
        hits.append(OffTargetHit(start=start, strand="+", matched_sequence=seed))
    for start in _find_all(body, reverse_seed):
        hits.append(OffTargetHit(start=start, strand="-", matched_sequence=reverse_seed))
    return tuple(sorted(hits, key=lambda hit: (hit.start, hit.strand)))


def reverse_complement(sequence: str) -> str:
    return _normalise_dna(sequence).translate(DNA_COMPLEMENT)[::-1]


def melting_temperature_C(sequence: str) -> float:
    primer = _normalise_dna(sequence)
    at_count = primer.count("A") + primer.count("T")
    gc_count = primer.count("G") + primer.count("C")
    return float((2 * at_count) + (4 * gc_count))


def gc_fraction(sequence: str) -> float:
    primer = _normalise_dna(sequence)
    return (primer.count("G") + primer.count("C")) / len(primer)


def _primer(
    direction: Literal["forward", "reverse", "sequencing"],
    name: str,
    sequence: str,
    hits: tuple[OffTargetHit, ...] = (),
) -> Primer:
    return Primer(
        name=name,
        sequence=sequence,
        direction=direction,
        tm_C=melting_temperature_C(sequence),
        gc_fraction=gc_fraction(sequence),
        off_target_hits=hits,
    )


def _choose_forward_primer(sequence: str, parameters: PrimerDesignParameters) -> str:
    return _choose_primer_from_window(sequence, parameters)


def _choose_reverse_primer(sequence: str, parameters: PrimerDesignParameters) -> str:
    reverse_template = reverse_complement(sequence)
    return _choose_primer_from_window(reverse_template, parameters)


def _choose_primer_from_window(sequence: str, parameters: PrimerDesignParameters) -> str:
    min_len, max_len = parameters.length_range
    max_allowed = min(max_len, len(sequence))
    candidates = tuple(sequence[:length] for length in range(min_len, max_allowed + 1))
    if not candidates:
        raise ValueError("template window is shorter than the minimum primer length")
    low_tm, high_tm = parameters.target_tm_C
    in_range = [
        primer for primer in candidates if low_tm <= melting_temperature_C(primer) <= high_tm
    ]
    pool = in_range or list(candidates)
    return min(
        pool,
        key=lambda primer: (
            abs(melting_temperature_C(primer) - parameters.target_tm_midpoint_C),
            abs(gc_fraction(primer) - 0.5),
            len(primer),
            primer,
        ),
    )


def _pair_warnings(
    forward: Primer,
    reverse: Primer,
    parameters: PrimerDesignParameters,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if abs(forward.tm_C - reverse.tm_C) > parameters.max_tm_difference_C:
        warnings.append("primer pair Tm difference exceeds limit")
    if len(forward.off_target_hits) > parameters.max_off_target_seed_hits:
        warnings.append("forward primer seed has multiple plasmid hits")
    if len(reverse.off_target_hits) > parameters.max_off_target_seed_hits:
        warnings.append("reverse primer seed has multiple plasmid hits")
    return tuple(warnings)


def _normalise_dna(sequence: str) -> str:
    body = sequence.strip().upper()
    if not body:
        raise ValueError("DNA sequence cannot be empty")
    invalid = sorted(set(body) - set("ACGT"))
    if invalid:
        raise ValueError(f"DNA sequence contains non-DNA bases: {''.join(invalid)}")
    return body


def _sequence_body(sequence: str | SequenceRecord) -> str:
    if isinstance(sequence, SequenceRecord):
        return sequence.sequence.body
    return _normalise_dna(sequence)


def _find_all(body: str, needle: str) -> tuple[int, ...]:
    starts: list[int] = []
    start = body.find(needle)
    while start != -1:
        starts.append(start)
        start = body.find(needle, start + 1)
    return tuple(starts)
