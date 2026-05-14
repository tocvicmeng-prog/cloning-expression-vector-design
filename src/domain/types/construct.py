"""
module_id: domain.types.construct
file: src/domain/types/construct.py
task_id: T-303

Construct entity binding user-facing modules to the canonical graph.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.graph import ConstructGraph, derive_feature_table
from domain.sequence import FeatureV14, Sha256
from domain.types.enums import BiosafetyTier, DownstreamUse
from domain.types.host_context import HostContext
from domain.types.ids import ConstructId, require_non_empty
from domain.types.module import Module
from domain.types.part import Provenance

Semver = str
SbolRef = str


@dataclass(frozen=True)
class Construct:
    id: ConstructId
    version: Semver
    modules: tuple[Module, ...]
    graph: ConstructGraph
    hosts: tuple[HostContext, ...]
    biosafety_tier: BiosafetyTier
    downstream_use: DownstreamUse
    feature_table: tuple[FeatureV14, ...]
    sbol_record: SbolRef | None
    checksum: Sha256
    provenance: Provenance

    def __post_init__(self) -> None:
        require_non_empty(str(self.id), "construct id")
        require_non_empty(self.version, "construct version")
        require_non_empty(self.provenance, "provenance")
        if not self.modules:
            raise ValueError("construct requires at least one module")
        if not self.hosts:
            raise ValueError("construct requires at least one host context")
        host_roles = [host.role for host in self.hosts]
        if len(host_roles) != len(set(host_roles)):
            raise ValueError("construct host roles must be unique")
        if self.feature_table != derive_feature_table(self.graph):
            raise ValueError("construct feature_table must equal derive_feature_table(graph)")
        if self.checksum != self.graph.sequence_record.checksum:
            raise ValueError("construct checksum must match graph sequence_record checksum")
