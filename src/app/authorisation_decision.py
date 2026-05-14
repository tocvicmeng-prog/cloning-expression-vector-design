"""
module_id: app.authorisation_decision
file: src/app/authorisation_decision.py
task_id: T-203

Public API placeholder for app.authorisation_decision. The owning implementation task is T-806b.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.authorisation_decision"
OWNING_TASKS = ("T-806b",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.authorisation_decision's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
