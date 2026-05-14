"""
module_id: domain.types.library
file: src/domain/types/library.py
task_id: T-303

Library definition value object.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.construct import Construct
from domain.types.module import Module, OneOf, Override, Variable


@dataclass(frozen=True)
class ExpansionPolicy:
    max_realizations: int
    require_deterministic_order: bool = True

    def __post_init__(self) -> None:
        if self.max_realizations < 1:
            raise ValueError("max_realizations must be positive")


@dataclass(frozen=True)
class Library:
    definition: Construct
    expansion_policy: ExpansionPolicy

    def __post_init__(self) -> None:
        if not construct_has_variants(self.definition):
            raise ValueError("library definition requires at least one OneOf or Variable")


def module_has_variants(module: Module) -> bool:
    return any(isinstance(part, OneOf | Variable | Override) for part in module.parts)


def construct_has_variants(construct: Construct) -> bool:
    return any(module_has_variants(module) for module in construct.modules)
