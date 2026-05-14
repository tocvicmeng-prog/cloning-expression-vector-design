"""
module_id: app.decision_tree
file: src/app/decision_tree.py
task_id: T-203

Public API placeholder for app.decision_tree. The owning implementation task is T-607.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.decision_tree"
OWNING_TASKS = ("T-607",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.decision_tree's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
