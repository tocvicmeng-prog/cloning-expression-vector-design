"""
module_id: engine.validation.predicates
file: src/engine/validation/predicates/__init__.py
task_id: T-405

Predicate registry for Phase-4 declarative rule manifests.
"""

from __future__ import annotations

from engine.validation.predicates import (
    br,
    cpg,
    frame,
    host,
    internal_sites,
    kozak,
    mr,
    ms,
    premature_polya,
    rbs,
    signal_peptide,
    splice,
    sr,
    structural,
    uorf,
    wr,
)
from engine.validation.predicates._stub import Predicate

PREDICATE_REGISTRY: dict[str, Predicate] = {
    **mr.PREDICATES,
    **wr.PREDICATES,
    **sr.PREDICATES,
    **br.PREDICATES,
    **ms.PREDICATES,
}

IMPLEMENTED_PREDICATE_REGISTRY: dict[str, Predicate] = {
    **structural.IMPLEMENTED_STRUCTURAL_PREDICATES,
    **frame.FRAME_PREDICATES,
    **internal_sites.INTERNAL_SITE_PREDICATES,
    **host.HOST_PREDICATES,
    **rbs.RBS_PREDICATES,
    **kozak.KOZAK_PREDICATES,
    **uorf.UORF_PREDICATES,
    **premature_polya.POLYA_PREDICATES,
    **splice.SPLICE_PREDICATES,
    **cpg.CPG_PREDICATES,
    **signal_peptide.SIGNAL_PEPTIDE_PREDICATES,
}


def resolve_predicate(name: str) -> Predicate:
    try:
        return PREDICATE_REGISTRY[name]
    except KeyError as exc:
        raise LookupError(f"unknown validation predicate: {name}") from exc


__all__ = [
    "IMPLEMENTED_PREDICATE_REGISTRY",
    "PREDICATE_REGISTRY",
    "Predicate",
    "resolve_predicate",
]
