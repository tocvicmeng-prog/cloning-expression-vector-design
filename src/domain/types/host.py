"""
module_id: domain.types.host
file: src/domain/types/host.py
task_id: T-303

Host catalogue entity.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.citation import GradedCitation
from domain.types.enums import BiosafetyTier, ChassisClass
from domain.types.ids import HostId, MarkerId, OriginId, require_non_empty

Genotype = str
HostFeatureSet = frozenset[str]
CodonUsageTable = str
GrowthConditions = str


@dataclass(frozen=True)
class Host:
    id: HostId
    name: str
    chassis: ChassisClass
    genotype: Genotype
    compatible_origins: frozenset[OriginId]
    compatible_markers: frozenset[MarkerId]
    expression_features: HostFeatureSet
    codon_usage_table: CodonUsageTable
    growth_conditions: GrowthConditions
    biosafety_tier: BiosafetyTier
    references: tuple[GradedCitation, ...]

    def __post_init__(self) -> None:
        require_non_empty(str(self.id), "host id")
        require_non_empty(self.name, "host name")
        require_non_empty(self.genotype, "genotype")
        require_non_empty(self.codon_usage_table, "codon_usage_table")
        require_non_empty(self.growth_conditions, "growth_conditions")
        if not self.references:
            raise ValueError("host requires at least one graded citation")
