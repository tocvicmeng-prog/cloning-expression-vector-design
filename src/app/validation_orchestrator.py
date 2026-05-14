"""
module_id: app.validation_orchestrator
file: src/app/validation_orchestrator.py
task_id: T-203

Public API placeholder for app.validation_orchestrator. The owning implementation task is T-603.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.validation_orchestrator"
OWNING_TASKS = ("T-603",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.validation_orchestrator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
