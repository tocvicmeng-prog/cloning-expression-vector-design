"""
module_id: app.controls_orchestrator
file: src/app/controls_orchestrator.py
task_id: T-203

Public API placeholder for app.controls_orchestrator. The owning implementation task is T-804.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.controls_orchestrator"
OWNING_TASKS = ("T-804", "T-805a")


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.controls_orchestrator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
