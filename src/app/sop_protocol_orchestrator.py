"""
module_id: app.sop_protocol_orchestrator
file: src/app/sop_protocol_orchestrator.py
task_id: T-203

Public API placeholder for app.sop_protocol_orchestrator. The owning implementation task is T-805b.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "app.sop_protocol_orchestrator"
OWNING_TASKS = ("T-805b",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until app.sop_protocol_orchestrator's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
