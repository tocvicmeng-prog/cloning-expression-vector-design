"""
module_id: adapter.vendor
file: src/adapter/vendor.py
task_id: T-203

Public API placeholder for adapter.vendor. The owning implementation task is T-1001.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "adapter.vendor"
OWNING_TASKS = ("T-1001",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until adapter.vendor's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
