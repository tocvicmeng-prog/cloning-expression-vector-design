"""
module_id: domain.types.host_compat
file: src/domain/types/host_compat.py
task_id: T-303

Contextual host-compatibility constraints.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.enums import ChassisClass, HostRole
from domain.types.ids import MarkerId, OriginId


@dataclass(frozen=True)
class HostCompatibilityConstraints:
    role: HostRole
    allowed_chassis: frozenset[ChassisClass]
    required_origins: frozenset[OriginId] = frozenset()
    forbidden_markers: frozenset[MarkerId] = frozenset()
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.allowed_chassis:
            raise ValueError("host compatibility constraints require allowed_chassis")
        for note in self.notes:
            if not note:
                raise ValueError("host compatibility notes cannot be empty")
