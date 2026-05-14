"""
module_id: domain.graph.nodes
file: src/domain/graph/nodes.py
task_id: T-302

Immutable graph nodes for construct topology and feature-table derivation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, NewType, TypeAlias

from domain.sequence import FeatureV14

NodeId = NewType("NodeId", str)
GraphNodeKind = Literal["part", "feature", "module"]
NodePayload: TypeAlias = FeatureV14 | str | tuple[tuple[str, str], ...]

GRAPH_NODE_KINDS = frozenset({"part", "feature", "module"})


@dataclass(frozen=True)
class GraphNode:
    id: NodeId
    kind: GraphNodeKind
    payload: NodePayload

    def __post_init__(self) -> None:
        if not str(self.id):
            raise ValueError("graph node id cannot be empty")
        if self.kind not in GRAPH_NODE_KINDS:
            raise ValueError(f"unsupported graph node kind: {self.kind}")
        if self.kind == "feature" and not isinstance(self.payload, FeatureV14):
            raise TypeError("feature graph nodes require a FeatureV14 payload")
        if self.kind != "feature" and isinstance(self.payload, FeatureV14):
            raise TypeError("FeatureV14 payloads are only valid for feature graph nodes")
        if isinstance(self.payload, tuple):
            for key, _value in self.payload:
                if not key:
                    raise ValueError("graph node payload keys cannot be empty")
            object.__setattr__(self, "payload", tuple(sorted(self.payload)))
