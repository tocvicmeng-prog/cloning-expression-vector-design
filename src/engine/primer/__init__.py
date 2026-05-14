"""
module_id: engine.primer
file: src/engine/primer/__init__.py
task_id: T-704

Primer design, off-target scanning, sequencing primers, and diagnostic helpers.
"""

from __future__ import annotations

from engine.primer.designer import (
    OffTargetHit,
    Primer,
    PrimerDesigner,
    PrimerPair,
    PrimerSet,
    reverse_complement,
    scan_off_targets,
)
from engine.primer.diagnostic import DiagnosticPrimerDesign, DiagnosticPrimerDesigner
from engine.primer.parameters import OligoModification, PrimerDesignParameters, TargetProduct
from engine.primer.sequencing import SequencingPrimerDesigner, SequencingPrimerRequest

__all__ = [
    "DiagnosticPrimerDesign",
    "DiagnosticPrimerDesigner",
    "OffTargetHit",
    "OligoModification",
    "Primer",
    "PrimerDesignParameters",
    "PrimerDesigner",
    "PrimerPair",
    "PrimerSet",
    "SequencingPrimerDesigner",
    "SequencingPrimerRequest",
    "TargetProduct",
    "reverse_complement",
    "scan_off_targets",
]
