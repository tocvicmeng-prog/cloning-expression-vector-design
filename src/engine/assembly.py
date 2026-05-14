"""
module_id: engine.assembly
file: src/engine/assembly.py
task_id: T-203

Public API placeholder for engine.assembly. The owning implementation task is T-703.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.assembly"
OWNING_TASKS = ("T-703",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.assembly's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
