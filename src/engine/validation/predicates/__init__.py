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
    marker_host_compat,  # v0.2.1 audit fix H4
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
    # v0.2.1 audit fix H4 — MR-59 real predicate (marker-host auxotrophic compat).
    # Overrides the structural-metric stub for mr_59. MR-55 + MR-60 remain INFO
    # stubs at v0.2.1 (deferred to v0.3 — each needs additional supporting data).
    **marker_host_compat.MARKER_HOST_COMPAT_PREDICATES,
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
