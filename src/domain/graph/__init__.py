"""
module_id: domain.graph
file: src/domain/graph/__init__.py
task_id: T-302

Canonical construct graph primitives and derived feature-table helpers.
"""

from __future__ import annotations

from domain.graph.construct_graph import (
    ConstructGraph,
    derive_feature_table,
)
from domain.graph.edges import AnnotationItems, Edge, EdgeKind
from domain.graph.nodes import GraphNode, GraphNodeKind, NodeId, NodePayload

__all__ = [
    "AnnotationItems",
    "ConstructGraph",
    "Edge",
    "EdgeKind",
    "GraphNode",
    "GraphNodeKind",
    "NodeId",
    "NodePayload",
    "derive_feature_table",
]
