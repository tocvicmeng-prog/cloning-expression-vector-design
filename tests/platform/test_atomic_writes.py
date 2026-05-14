"""
module_id: tests.platform
file: tests/platform/test_atomic_writes.py
task_id: T-205
"""

from __future__ import annotations

import os
from pathlib import Path


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def test_atomic_write_replaces_complete_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    target = tmp_path / "result.json"
    target.write_bytes(b"old")
    atomic_write_bytes(target, b"new")

    assert target.read_bytes() == b"new"
    assert not target.with_suffix(".json.tmp").exists()


def test_partial_temp_file_does_not_replace_target(tmp_path) -> None:  # type: ignore[no-untyped-def]
    target = tmp_path / "result.json"
    target.write_bytes(b"committed")
    target.with_suffix(".json.tmp").write_bytes(b"partial")

    assert target.read_bytes() == b"committed"
