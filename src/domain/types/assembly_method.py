"""
module_id: domain.types.assembly_method
file: src/domain/types/assembly_method.py
task_id: T-303

Assembly method strategy hierarchy.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.citation import GradedCitation
from domain.types.enums import AssemblyCapability
from domain.types.ids import AssemblyMethodId, require_non_empty


@dataclass(frozen=True)
class AssemblyMethod:
    id: AssemblyMethodId
    name: str
    scarless: bool
    typical_max_fragments: int
    capabilities: frozenset[AssemblyCapability]
    references: tuple[GradedCitation, ...]

    def __post_init__(self) -> None:
        require_non_empty(str(self.id), "assembly method id")
        require_non_empty(self.name, "assembly method name")
        if self.typical_max_fragments < 1:
            raise ValueError("typical_max_fragments must be positive")
        if not self.capabilities:
            raise ValueError("assembly method requires at least one capability")
        if not self.references:
            raise ValueError("assembly method requires at least one graded citation")


@dataclass(frozen=True)
class RestrictionLigation(AssemblyMethod):
    pass


@dataclass(frozen=True)
class GibsonLike(AssemblyMethod):
    pass


@dataclass(frozen=True)
class TypeIISGoldenGate(AssemblyMethod):
    pass


@dataclass(frozen=True)
class GatewayMethod(AssemblyMethod):
    pass


@dataclass(frozen=True)
class LICMethod(AssemblyMethod):
    pass


@dataclass(frozen=True)
class USERMethod(AssemblyMethod):
    pass


@dataclass(frozen=True)
class IVAMethod(AssemblyMethod):
    pass


@dataclass(frozen=True)
class YeastTAR(AssemblyMethod):
    pass
