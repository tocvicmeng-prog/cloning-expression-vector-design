"""
module_id: tests.platform.filewatch_debounce_harness
file: tests/platform/filewatch_debounce_harness.py
task_id: T-205
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DebouncedEvent:
    path: Path
    timestamp_ms: int


class FilewatchDebounceHarness:
    def __init__(self, debounce_ms: int) -> None:
        self._debounce_ms = debounce_ms
        self._latest_by_path: dict[Path, int] = {}

    def record_write(self, path: Path, timestamp_ms: int) -> None:
        self._latest_by_path[path] = timestamp_ms

    def flush_ready(self, now_ms: int) -> list[DebouncedEvent]:
        ready: list[DebouncedEvent] = []
        for path, timestamp_ms in list(self._latest_by_path.items()):
            if now_ms - timestamp_ms >= self._debounce_ms:
                ready.append(DebouncedEvent(path=path, timestamp_ms=timestamp_ms))
                del self._latest_by_path[path]
        return ready
