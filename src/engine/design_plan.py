"""
module_id: engine.design_plan
file: src/engine/design_plan.py
task_id: T-203

Public API placeholder for engine.design_plan. The owning implementation task is T-802.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.design_plan"
OWNING_TASKS = ("T-802",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.design_plan's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
