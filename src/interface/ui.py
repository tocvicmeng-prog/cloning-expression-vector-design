"""
module_id: interface.ui
file: src/interface/ui.py
task_id: T-203

Public API placeholder for interface.ui. The owning implementation task is T-1202.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "interface.ui"
OWNING_TASKS = ("T-1202",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until interface.ui's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
