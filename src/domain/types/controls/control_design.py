"""
module_id: domain.types.controls.control_design
file: src/domain/types/controls/control_design.py
task_id: T-306

Non-operational control design descriptors.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ControlKind(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    PROCESS = "process"
    VEHICLE = "vehicle"
    LIBRARY_SPECIFIC = "library_specific"


@dataclass(frozen=True)
class ControlDesign:
    control_id: str
    kind: ControlKind
    purpose: str
    expected_observation: str

    def __post_init__(self) -> None:
        if not self.control_id:
            raise ValueError("control_id cannot be empty")
        if not self.purpose:
            raise ValueError("control purpose cannot be empty")
        if not self.expected_observation:
            raise ValueError("expected_observation cannot be empty")
