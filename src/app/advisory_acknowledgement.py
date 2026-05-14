"""
module_id: app.advisory_acknowledgement
file: src/app/advisory_acknowledgement.py
task_id: T-203

Public API placeholder for app.advisory_acknowledgement. The owning implementation task is T-806a.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.advisory_acknowledgement"
OWNING_TASKS = ("T-806a",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.advisory_acknowledgement's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
