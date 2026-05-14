"""
module_id: domain.sequence
file: src/domain/sequence/qualifier.py
task_id: T-301

Structured feature qualifiers preserving namespace, type, order, and provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

StructuredValue = str | bool | int | float | tuple[tuple[str, object], ...]
QualifierValueType = Literal[
    "string",
    "boolean",
    "integer",
    "float",
    "url",
    "ontology_term",
    "structured",
]


@dataclass(frozen=True)
class Qualifier:
    namespace: str
    key: str
    value: StructuredValue
    value_type: QualifierValueType
    order: int
    provenance: str | None = None

    def __post_init__(self) -> None:
        if not self.namespace:
            raise ValueError("qualifier namespace cannot be empty")
        if not self.key:
            raise ValueError("qualifier key cannot be empty")
        if self.order < 0:
            raise ValueError("qualifier order must be non-negative")
        if not self._value_matches_type():
            raise TypeError(f"qualifier value {self.value!r} does not match {self.value_type}")

    def _value_matches_type(self) -> bool:
        if self.value_type in {"string", "url", "ontology_term"}:
            return isinstance(self.value, str)
        if self.value_type == "boolean":
            return isinstance(self.value, bool)
        if self.value_type == "integer":
            return isinstance(self.value, int) and not isinstance(self.value, bool)
        if self.value_type == "float":
            return isinstance(self.value, float)
        return isinstance(self.value, tuple)
