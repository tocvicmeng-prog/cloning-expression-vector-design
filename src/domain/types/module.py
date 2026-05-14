"""
module_id: domain.types.module
file: src/domain/types/module.py
task_id: T-303

Six-layer module and variant value objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypeAlias

from domain.types.enums import ModuleLayer, SlotKind
from domain.types.ids import ModuleId, require_non_empty
from domain.types.part import Part

VariableDomain = str
VariableConstraint = str
StructuredConstraint = tuple[str, str]
UserId = str


@dataclass(frozen=True)
class OneOf:
    candidates: tuple[Part, ...]

    def __post_init__(self) -> None:
        if not self.candidates:
            raise ValueError("OneOf requires at least one candidate part")


@dataclass(frozen=True)
class Variable:
    domain: VariableDomain
    constraints: tuple[VariableConstraint, ...] = ()

    def __post_init__(self) -> None:
        require_non_empty(self.domain, "variable domain")
        for constraint in self.constraints:
            require_non_empty(constraint, "variable constraint")


@dataclass(frozen=True)
class Override:
    free_text: str
    structured: tuple[StructuredConstraint, ...]
    origin: Literal["user", "llm_translation"]
    confirmed_by: UserId
    confirmed_at: datetime

    def __post_init__(self) -> None:
        if not self.free_text and not self.structured:
            raise ValueError("override requires free_text or structured constraints")
        require_non_empty(self.confirmed_by, "confirmed_by")
        for key, _value in self.structured:
            require_non_empty(key, "structured constraint key")


PartOrVariant: TypeAlias = Part | OneOf | Variable | Override


@dataclass(frozen=True)
class Module:
    id: ModuleId
    layer: ModuleLayer
    slot_kind: SlotKind
    parts: tuple[PartOrVariant, ...]

    def __post_init__(self) -> None:
        require_non_empty(str(self.id), "module id")
        if not self.parts:
            raise ValueError("module must contain at least one part or variant")
