"""
module_id: tests.platform
file: tests/platform/test_filewatch_debounce_harness.py
task_id: T-205
"""

from __future__ import annotations

from tests.platform.filewatch_debounce_harness import FilewatchDebounceHarness


def test_debounce_harness_coalesces_burst_writes(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "watched.dna"
    harness = FilewatchDebounceHarness(debounce_ms=50)

    harness.record_write(path, timestamp_ms=0)
    harness.record_write(path, timestamp_ms=10)
    harness.record_write(path, timestamp_ms=20)

    assert harness.flush_ready(now_ms=40) == []
    ready = harness.flush_ready(now_ms=75)

    assert len(ready) == 1
    assert ready[0].path == path
    assert ready[0].timestamp_ms == 20
