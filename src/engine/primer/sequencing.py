"""
module_id: engine.primer.sequencing
file: src/engine/primer/sequencing.py
task_id: T-704

Sanger sequencing primer placement.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.sequence import SequenceRecord
from engine.primer.designer import Primer, _primer
from engine.primer.parameters import PrimerDesignParameters


@dataclass(frozen=True)
class SequencingPrimerRequest:
    target_id: str
    template: str | SequenceRecord
    junction_positions: tuple[int, ...]
    upstream_distance_range: tuple[int, int] = (50, 100)

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("target_id cannot be empty")
        low, high = self.upstream_distance_range
        if low < 0 or high < low:
            raise ValueError("upstream_distance_range must be increasing and non-negative")
        if not self.junction_positions:
            raise ValueError("at least one junction position is required")


class SequencingPrimerDesigner:
    def __init__(self, parameters: PrimerDesignParameters | None = None) -> None:
        self._parameters = PrimerDesignParameters(
            target_product="sequencing"
        ) if parameters is None else parameters

    def design(self, request: SequencingPrimerRequest) -> tuple[Primer, ...]:
        sequence = _sequence_body(request.template)
        min_len, max_len = self._parameters.length_range
        low_distance, high_distance = request.upstream_distance_range
        primers: list[Primer] = []
        for junction in request.junction_positions:
            if not 0 < junction < len(sequence):
                raise ValueError("junction positions must lie within the template")
            primer_end = max(min_len, junction - low_distance)
            primer_start = max(0, primer_end - max_len)
            window = sequence[primer_start:primer_end]
            if len(window) < min_len:
                primer_start = max(0, junction - high_distance)
                window = sequence[primer_start : primer_start + max_len]
            primer_sequence = _choose_from_window(window, self._parameters)
            primers.append(
                _primer(
                    "sequencing",
                    f"{request.target_id}_junction_{junction}",
                    primer_sequence,
                )
            )
        return tuple(primers)


def _choose_from_window(window: str, parameters: PrimerDesignParameters) -> str:
    from engine.primer.designer import _choose_primer_from_window

    return _choose_primer_from_window(window, parameters)


def _sequence_body(sequence: str | SequenceRecord) -> str:
    from engine.primer.designer import _sequence_body as body

    return body(sequence)
