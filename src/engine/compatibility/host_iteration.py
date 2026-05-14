"""
module_id: engine.compatibility.host_iteration
file: src/engine/compatibility/host_iteration.py
task_id: T-504

Host-context workflow helpers.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from domain.types.construct import Construct
from domain.types.enums import HostRole
from domain.types.host_context import HostContext


@dataclass(frozen=True)
class HostWorkflow:
    contexts: tuple[HostContext, ...]

    def __post_init__(self) -> None:
        if not self.contexts:
            raise ValueError("host workflow requires at least one host context")
        roles = tuple(context.role for context in self.contexts)
        if len(roles) != len(set(roles)):
            raise ValueError("host workflow roles must be unique")

    @property
    def roles(self) -> frozenset[HostRole]:
        return frozenset(context.role for context in self.contexts)

    def by_role(self, role: HostRole) -> HostContext | None:
        return next((context for context in self.contexts if context.role is role), None)


def iter_host_contexts(
    construct: Construct,
    hosts: Iterable[HostContext] | None = None,
) -> Iterator[HostContext]:
    workflow = HostWorkflow(tuple(hosts) if hosts is not None else construct.hosts)
    yield from workflow.contexts


__all__ = [
    "HostWorkflow",
    "iter_host_contexts",
]
