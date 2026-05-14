"""
module_id: tests.engine.validation.test_worker_pool_factory
file: tests/engine/validation/test_worker_pool_factory.py
task_id: T-502
"""

from __future__ import annotations

import inspect
import multiprocessing
from typing import cast

import pytest

from engine.validation.worker_pool_factory import (
    ProcessWorkerPool,
    WorkerPoolFactory,
    WorkerPoolMode,
)


def double(value: int) -> int:
    return value * 2


def test_sequential_and_thread_pools_preserve_input_order() -> None:
    for factory in (
        WorkerPoolFactory("sequential"),
        WorkerPoolFactory("thread", max_workers=2),
    ):
        with factory.create() as pool:
            assert pool.map(double, (3, 1, 2)) == (6, 2, 4)


def test_process_pool_uses_local_spawn_context_without_global_mutation() -> None:
    before = multiprocessing.get_start_method(allow_none=True)

    with WorkerPoolFactory("process", max_workers=1).create() as pool:
        assert pool.map(double, (2, 5)) == (4, 10)

    after = multiprocessing.get_start_method(allow_none=True)
    assert before is None or after == before
    assert "set_start_method" not in inspect.getsource(ProcessWorkerPool)


def test_worker_pool_factory_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError, match="unsupported worker-pool mode"):
        WorkerPoolFactory(cast(WorkerPoolMode, "invalid"))
    with pytest.raises(ValueError, match="max_workers"):
        WorkerPoolFactory("thread", max_workers=0)
