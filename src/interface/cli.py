"""
module_id: interface.cli
file: src/interface/cli.py
task_id: T-203

Public API placeholder for interface.cli. The owning implementation task is T-1101.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "interface.cli"
OWNING_TASKS = ("T-1101",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until interface.cli's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
