"""
module_id: domain.types.sop_protected.protocol_dag
file: src/domain/types/sop_protected/protocol_dag.py
task_id: T-306

Operational protocol DAG with canonical step ordering and cycle detection.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.sop_protected.protocol_step import ProtocolStep


@dataclass(frozen=True)
class ProtocolDAG:
    root: str
    steps: tuple[ProtocolStep, ...]

    def __post_init__(self) -> None:
        if not self.root:
            raise ValueError("ProtocolDAG root cannot be empty")
        if not self.steps:
            raise ValueError("ProtocolDAG requires at least one step")
        step_ids = [step.step_id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("ProtocolDAG step ids must be unique")
        if self.root not in step_ids:
            raise ValueError("ProtocolDAG root must reference an existing step")
        step_id_set = set(step_ids)
        for step in self.steps:
            for edge in step.successors:
                if edge.target_step_id not in step_id_set:
                    raise ValueError("ProtocolDAG edge target must reference an existing step")
        edges = {
            step.step_id: tuple(edge.target_step_id for edge in step.successors)
            for step in self.steps
        }
        if _has_cycle(edges):
            raise ValueError("ProtocolDAG cannot contain cycles")
        object.__setattr__(
            self,
            "steps",
            tuple(sorted(self.steps, key=lambda step: step.step_id)),
        )

    @property
    def canonical_step_ids(self) -> tuple[str, ...]:
        return tuple(step.step_id for step in self.steps)


def _has_cycle(edges: dict[str, tuple[str, ...]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for target in edges[node]:
            if visit(target):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in edges)
