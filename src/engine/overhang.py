"""
module_id: engine.overhang
file: src/engine/overhang.py
task_id: T-203

Public API placeholder for engine.overhang. The owning implementation task is T-702.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.overhang"
OWNING_TASKS = ("T-702",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.overhang's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
