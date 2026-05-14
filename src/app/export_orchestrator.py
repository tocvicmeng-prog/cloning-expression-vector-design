"""
module_id: app.export_orchestrator
file: src/app/export_orchestrator.py
task_id: T-203

Public API placeholder for app.export_orchestrator. The owning implementation task is T-903.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.export_orchestrator"
OWNING_TASKS = ("T-903",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.export_orchestrator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
