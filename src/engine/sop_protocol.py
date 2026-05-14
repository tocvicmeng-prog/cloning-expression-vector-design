"""
module_id: engine.sop_protocol
file: src/engine/sop_protocol.py
task_id: T-203

Public API placeholder for engine.sop_protocol. The owning implementation task is T-803.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.sop_protocol"
OWNING_TASKS = ("T-803",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.sop_protocol's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
