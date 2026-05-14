"""
module_id: interface.api
file: src/interface/api.py
task_id: T-203

Public API placeholder for interface.api. The owning implementation task is T-1102.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "interface.api"
OWNING_TASKS = ("T-1102",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until interface.api's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
