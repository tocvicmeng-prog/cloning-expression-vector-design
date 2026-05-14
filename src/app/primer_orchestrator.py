"""
module_id: app.primer_orchestrator
file: src/app/primer_orchestrator.py
task_id: T-203

Public API placeholder for app.primer_orchestrator. The owning implementation task is T-704.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.primer_orchestrator"
OWNING_TASKS = ("T-704", "T-705")


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.primer_orchestrator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
