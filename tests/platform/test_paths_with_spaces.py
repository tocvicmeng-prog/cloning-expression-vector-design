"""
module_id: tests.platform
file: tests/platform/test_paths_with_spaces.py
task_id: T-205
"""

from __future__ import annotations

import os

from tests.conftest_platform import make_sync_like_path


def test_paths_with_spaces_and_long_segments(tmp_path) -> None:  # type: ignore[no-untyped-def]
    sync_path = make_sync_like_path(tmp_path).path
    long_segment = "a" * 80
    target = sync_path / "folder with spaces" / long_segment / "payload.txt"
    target.parent.mkdir(parents=True)
    target.write_text("payload", encoding="utf-8")

    assert target.read_text(encoding="utf-8") == "payload"
    assert " " in str(target)


def test_case_sensitivity_baseline(tmp_path) -> None:  # type: ignore[no-untyped-def]
    upper = tmp_path / "Foo.txt"
    lower = tmp_path / "foo.txt"
    upper.write_text("upper", encoding="utf-8")
    lower.write_text("lower", encoding="utf-8")

    if os.name == "nt":
        assert upper.read_text(encoding="utf-8") == "lower"
    else:
        assert upper.read_text(encoding="utf-8") == "upper"
        assert lower.read_text(encoding="utf-8") == "lower"
