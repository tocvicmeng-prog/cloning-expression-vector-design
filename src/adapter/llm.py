"""
module_id: adapter.llm
file: src/adapter/llm.py
task_id: T-203

Public API placeholder for adapter.llm. The owning implementation task is T-1201.
"""

from __future__ import annotations

from typing import NoReturn

MODULE_ID = "adapter.llm"
OWNING_TASKS = ("T-1201",)


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until adapter.llm's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")
