"""
module_id: engine.sequence_analysis
file: src/engine/sequence_analysis/__init__.py
task_id: T-503

Topology-aware sequence analysis primitives.
"""

from __future__ import annotations

from typing import NoReturn

from engine.sequence_analysis.compatible_ends import (
    EndCompatibility,
    FragmentEnd,
    compatible_ends,
    reverse_complement,
)
from engine.sequence_analysis.design_diagnostic import (
    DiagnosticDigestDesign,
    WrongCloneModel,
    design_diagnostic_digest,
)
from engine.sequence_analysis.digest import (
    RestrictionDigest,
    RestrictionFragment,
    digest,
)
from engine.sequence_analysis.find_sites import (
    RestrictionEnzyme,
    RestrictionSite,
    find_sites,
)
from engine.sequence_analysis.fragment_sim import FragmentSimulation, simulate_fragments
from engine.sequence_analysis.rank_directional import (
    DirectionalCloningCandidate,
    rank_directional_cloning_sites,
)

MODULE_ID = "engine.sequence_analysis"
OWNING_TASKS = ("T-503",)


class PublicApiStub:
    """Historical marker retained for T-203 scaffold compatibility."""


def module_not_implemented() -> NoReturn:
    """Raise for callers that still use the pre-T-503 placeholder sentinel."""
    raise NotImplementedError(f"{MODULE_ID} public API has been replaced by T-503")


__all__ = [
    "DiagnosticDigestDesign",
    "DirectionalCloningCandidate",
    "EndCompatibility",
    "FragmentEnd",
    "FragmentSimulation",
    "PublicApiStub",
    "RestrictionDigest",
    "RestrictionEnzyme",
    "RestrictionFragment",
    "RestrictionSite",
    "WrongCloneModel",
    "compatible_ends",
    "design_diagnostic_digest",
    "digest",
    "find_sites",
    "module_not_implemented",
    "rank_directional_cloning_sites",
    "reverse_complement",
    "simulate_fragments",
]
