"""
module_id: engine.vlp_policy
file: src/engine/vlp_policy.py
task_id: T-203

Public API placeholder for engine.vlp_policy. The owning implementation task is T-807.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.vlp_policy"
OWNING_TASKS = ("T-807",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.vlp_policy's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
