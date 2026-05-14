"""
module_id: engine.validation.worker_pool_factory
file: src/engine/validation/worker_pool_factory.py
task_id: T-502

Local worker-pool factory for deterministic validation execution.
"""

from __future__ import annotations

import multiprocessing
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from multiprocessing.pool import Pool as MultiprocessingPool
from types import TracebackType
from typing import Final, Literal, Protocol, TypeVar

WorkerPoolMode = Literal["sequential", "thread", "process"]
SUPPORTED_WORKER_POOL_MODES: Final[tuple[WorkerPoolMode, ...]] = (
    "sequential",
    "thread",
    "process",
)

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class WorkerPool(Protocol):
    def __enter__(self) -> WorkerPool:
        """Open worker resources and return the pool."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close worker resources."""

    def map(
        self,
        func: Callable[[InputT], OutputT],
        items: Iterable[InputT],
    ) -> tuple[OutputT, ...]:
        """Map in input order and return a tuple in the same order."""


@dataclass(frozen=True)
class SequentialWorkerPool:
    def __enter__(self) -> SequentialWorkerPool:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def map(
        self,
        func: Callable[[InputT], OutputT],
        items: Iterable[InputT],
    ) -> tuple[OutputT, ...]:
        return tuple(func(item) for item in items)


@dataclass(frozen=True)
class ThreadWorkerPool:
    max_workers: int | None = None
    _executor: ThreadPoolExecutor | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    def __enter__(self) -> ThreadWorkerPool:
        object.__setattr__(self, "_executor", ThreadPoolExecutor(max_workers=self.max_workers))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=False)
        object.__setattr__(self, "_executor", None)

    def map(
        self,
        func: Callable[[InputT], OutputT],
        items: Iterable[InputT],
    ) -> tuple[OutputT, ...]:
        item_tuple = tuple(items)
        if not item_tuple:
            return ()
        if self._executor is None:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                return tuple(executor.map(func, item_tuple))
        return tuple(self._executor.map(func, item_tuple))


@dataclass(frozen=True)
class ProcessWorkerPool:
    max_workers: int | None = None
    _pool: MultiprocessingPool | None = field(default=None, init=False, repr=False, compare=False)

    def __enter__(self) -> ProcessWorkerPool:
        context = multiprocessing.get_context("spawn")
        object.__setattr__(self, "_pool", context.Pool(processes=self.max_workers))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._pool is None:
            return None
        if exc_type is None:
            self._pool.close()
        else:
            self._pool.terminate()
        self._pool.join()
        object.__setattr__(self, "_pool", None)

    def map(
        self,
        func: Callable[[InputT], OutputT],
        items: Iterable[InputT],
    ) -> tuple[OutputT, ...]:
        item_tuple = tuple(items)
        if not item_tuple:
            return ()
        if self._pool is None:
            context = multiprocessing.get_context("spawn")
            with context.Pool(processes=self.max_workers) as pool:
                raw_result = pool.map(func, item_tuple)
            return tuple(raw_result)
        raw_result = self._pool.map(func, item_tuple)
        return tuple(raw_result)


@dataclass(frozen=True)
class WorkerPoolFactory:
    mode: WorkerPoolMode = "sequential"
    max_workers: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in SUPPORTED_WORKER_POOL_MODES:
            modes = ", ".join(SUPPORTED_WORKER_POOL_MODES)
            raise ValueError(f"unsupported worker-pool mode {self.mode!r}; expected one of {modes}")
        if self.max_workers is not None and self.max_workers < 1:
            raise ValueError("max_workers must be >= 1 when provided")

    def create(self) -> WorkerPool:
        if self.mode == "sequential":
            return SequentialWorkerPool()
        if self.mode == "thread":
            return ThreadWorkerPool(max_workers=self.max_workers)
        return ProcessWorkerPool(max_workers=self.max_workers)


def default_worker_pool_factory() -> WorkerPoolFactory:
    return WorkerPoolFactory("sequential")


__all__ = [
    "SUPPORTED_WORKER_POOL_MODES",
    "ProcessWorkerPool",
    "SequentialWorkerPool",
    "ThreadWorkerPool",
    "WorkerPool",
    "WorkerPoolFactory",
    "WorkerPoolMode",
    "default_worker_pool_factory",
]
