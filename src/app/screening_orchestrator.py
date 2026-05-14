"""
module_id: app.screening_orchestrator
file: src/app/screening_orchestrator.py
task_id: T-203

Public API placeholder for app.screening_orchestrator. The owning implementation task is T-1002.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.screening_orchestrator"
OWNING_TASKS = ("T-1002",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.screening_orchestrator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
