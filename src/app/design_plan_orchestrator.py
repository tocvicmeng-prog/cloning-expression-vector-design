"""
module_id: app.design_plan_orchestrator
file: src/app/design_plan_orchestrator.py
task_id: T-203

Public API placeholder for app.design_plan_orchestrator. The owning implementation task is T-805a.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.design_plan_orchestrator"
OWNING_TASKS = ("T-805a",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.design_plan_orchestrator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
