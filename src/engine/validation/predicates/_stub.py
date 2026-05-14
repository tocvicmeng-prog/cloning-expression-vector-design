"""
module_id: engine.validation.predicates._stub
file: src/engine/validation/predicates/_stub.py
task_id: T-502

Shared predicate-stub factory for declarative rule manifests.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from domain.types.enums import Severity

Predicate = Callable[..., Severity]


@dataclass(frozen=True)
class StubPredicate:
    name: str

    def __call__(self, *_args: object, **_kwargs: object) -> Severity:
        return Severity.INFO

    @property
    def __name__(self) -> str:
        return self.name


def make_stub(name: str) -> Predicate:
    return StubPredicate(name)


def numbered_predicates(prefix: str, count: int) -> dict[str, Predicate]:
    return {
        f"{prefix.lower()}_{index:02d}": make_stub(f"{prefix.lower()}_{index:02d}")
        for index in range(1, count + 1)
    }
