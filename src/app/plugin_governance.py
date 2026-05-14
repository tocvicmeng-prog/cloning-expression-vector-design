"""
module_id: app.plugin_governance
file: src/app/plugin_governance.py
task_id: T-203

Public API placeholder for app.plugin_governance. The owning implementation task is T-808.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.plugin_governance"
OWNING_TASKS = ("T-808",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.plugin_governance's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
