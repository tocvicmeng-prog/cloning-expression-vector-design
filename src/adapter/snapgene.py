"""
module_id: adapter.snapgene
file: src/adapter/snapgene.py
task_id: T-203

Public API placeholder for adapter.snapgene. The owning implementation task is T-902.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "adapter.snapgene"
OWNING_TASKS = ("T-902", "T-1203")


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until adapter.snapgene's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
