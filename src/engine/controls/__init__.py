"""
module_id: engine.controls
file: src/engine/controls/__init__.py
task_id: T-804

First-class non-operational control-set generation.
"""

from __future__ import annotations

from engine.controls.generator import ControlGenerationInput, ControlSetGenerator, generate_controls
from engine.controls.validation import (
    ControlValidationFinding,
    ControlValidationReport,
    ControlValidationSeverity,
    validate_control_set,
)

MODULE_ID = "engine.controls"
OWNING_TASKS = ("T-804",)

__all__ = [
    "ControlGenerationInput",
    "ControlSetGenerator",
    "ControlValidationFinding",
    "ControlValidationReport",
    "ControlValidationSeverity",
    "generate_controls",
    "validate_control_set",
]
