"""
module_id: engine.primer
file: src/engine/primer.py
task_id: T-203

Public API placeholder for engine.primer. The owning implementation task is T-704.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.primer"
OWNING_TASKS = ("T-704",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.primer's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
