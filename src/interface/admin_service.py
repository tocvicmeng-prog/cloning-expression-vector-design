"""
module_id: interface.admin_service
file: src/interface/admin_service.py
task_id: T-203

Public API placeholder for interface.admin_service. The owning implementation task is T-1103b.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "interface.admin_service"
OWNING_TASKS = ("T-1103b",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until interface.admin_service's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
