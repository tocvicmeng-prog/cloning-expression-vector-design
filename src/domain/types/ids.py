"""
module_id: domain.types.ids
file: src/domain/types/ids.py
task_id: T-303

Typed identifiers shared by the T-303 domain type package.
"""

from __future__ import annotations

from typing import NewType

PartId = NewType("PartId", str)
ModuleId = NewType("ModuleId", str)
ConstructId = NewType("ConstructId", str)
HostId = NewType("HostId", str)
OriginId = NewType("OriginId", str)
MarkerId = NewType("MarkerId", str)
RuleId = NewType("RuleId", str)
MetricId = NewType("MetricId", str)
ReviewerId = NewType("ReviewerId", str)
AssemblyMethodId = NewType("AssemblyMethodId", str)
SequenceOntologyTerm = NewType("SequenceOntologyTerm", str)


def require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
