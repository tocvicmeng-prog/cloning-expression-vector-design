"""
module_id: app.library_realisation
file: src/app/library_realisation.py
task_id: T-203

Public API placeholder for app.library_realisation. The owning implementation task is T-606.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.library_realisation"
OWNING_TASKS = ("T-606",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.library_realisation's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
