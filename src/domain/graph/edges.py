"""
module_id: domain.graph.edges
file: src/domain/graph/edges.py
task_id: T-302

Typed construct graph edges.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.graph.nodes import NodeId

AnnotationItems = tuple[tuple[str, str], ...]


class EdgeKind(Enum):
    ADJACENCY = "adjacency"
    REGULATORY = "regulatory"
    DERIVATION = "derivation"
    ASSEMBLY = "assembly"


@dataclass(frozen=True)
class Edge:
    source: NodeId
    target: NodeId
    kind: EdgeKind
    annotations: AnnotationItems = ()

    def __post_init__(self) -> None:
        if not str(self.source):
            raise ValueError("edge source cannot be empty")
        if not str(self.target):
            raise ValueError("edge target cannot be empty")
        for key, _value in self.annotations:
            if not key:
                raise ValueError("edge annotation keys cannot be empty")
        object.__setattr__(self, "annotations", tuple(sorted(self.annotations)))
