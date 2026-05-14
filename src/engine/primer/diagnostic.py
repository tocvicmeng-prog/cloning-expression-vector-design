"""
module_id: engine.primer.diagnostic
file: src/engine/primer/diagnostic.py
task_id: T-704

Diagnostic digest primer support.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from domain.sequence import SequenceRecord
from engine.primer.designer import PrimerDesigner, PrimerPair
from engine.primer.parameters import PrimerDesignParameters
from engine.sequence_analysis import (
    DiagnosticDigestDesign,
    RestrictionEnzyme,
    WrongCloneModel,
    design_diagnostic_digest,
)


@dataclass(frozen=True)
class DiagnosticPrimerDesign:
    digest: DiagnosticDigestDesign
    primer_pair: PrimerPair


class DiagnosticPrimerDesigner:
    def __init__(self, parameters: PrimerDesignParameters | None = None) -> None:
        self._parameters = PrimerDesignParameters(
            target_product="diagnostic"
        ) if parameters is None else parameters
        self._primer_designer = PrimerDesigner(self._parameters)

    def design(
        self,
        correct_clone: str | SequenceRecord,
        wrong_clones: Iterable[WrongCloneModel],
        enzymes: Iterable[RestrictionEnzyme],
        *,
        topology: str = "circular",
        max_enzymes: int = 2,
    ) -> DiagnosticPrimerDesign | None:
        digest_design = design_diagnostic_digest(
            correct_clone,
            wrong_clones,
            enzymes,
            topology=topology,
            max_enzymes=max_enzymes,
        )
        if digest_design is None:
            return None
        primer_pair = self._primer_designer.design_pair(
            correct_clone,
            target_id="diagnostic",
            full_plasmid=correct_clone,
            parameters=self._parameters,
        )
        return DiagnosticPrimerDesign(digest=digest_design, primer_pair=primer_pair)
