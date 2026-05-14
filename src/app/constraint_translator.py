"""
module_id: app.constraint_translator
file: src/app/constraint_translator.py
task_id: T-203

Public API placeholder for app.constraint_translator. The owning implementation task is T-1201.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.constraint_translator"
OWNING_TASKS = ("T-1201",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.constraint_translator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
