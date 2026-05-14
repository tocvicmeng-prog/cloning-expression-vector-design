"""
module_id: engine.controls
file: src/engine/controls.py
task_id: T-203

Public API placeholder for engine.controls. The owning implementation task is T-804.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.controls"
OWNING_TASKS = ("T-804",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.controls's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
