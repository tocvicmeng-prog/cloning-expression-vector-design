"""
module_id: tests.platform
file: tests/platform/test_spawn_context_available.py
task_id: T-205
"""

from __future__ import annotations

import multiprocessing


def _identity(value: int) -> int:
    return value


def test_spawn_context_available() -> None:
    context = multiprocessing.get_context("spawn")
    with context.Pool(processes=1) as pool:
        assert pool.apply(_identity, (42,)) == 42
