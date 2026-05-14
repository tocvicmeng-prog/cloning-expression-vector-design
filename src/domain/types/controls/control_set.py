"""
module_id: domain.types.controls.control_set
file: src/domain/types/controls/control_set.py
task_id: T-306

Control set emitted with draft design bundles.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.controls.control_design import ControlDesign, ControlKind


@dataclass(frozen=True)
class ControlSet:
    construct_id: str
    controls: tuple[ControlDesign, ...]

    def __post_init__(self) -> None:
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        kinds = {control.kind for control in self.controls}
        if ControlKind.POSITIVE not in kinds:
            raise ValueError("ControlSet requires a positive control")
        if ControlKind.NEGATIVE not in kinds:
            raise ValueError("ControlSet requires a negative control")
