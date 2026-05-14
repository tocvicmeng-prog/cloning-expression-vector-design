"""
module_id: engine.codon
file: src/engine/codon.py
task_id: T-203

Public API placeholder for engine.codon. The owning implementation task is T-701.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "engine.codon"
OWNING_TASKS = ("T-701",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.codon's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
