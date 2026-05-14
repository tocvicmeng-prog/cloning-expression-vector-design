"""
module_id: engine.risk_classification
file: src/engine/risk_classification.py
task_id: T-203

Public API placeholder for engine.risk_classification. The owning implementation task is T-801.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.risk_classification"
OWNING_TASKS = ("T-801",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.risk_classification's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
