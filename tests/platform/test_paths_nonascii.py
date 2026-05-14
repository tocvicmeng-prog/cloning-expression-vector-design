"""
module_id: tests.platform
file: tests/platform/test_paths_nonascii.py
task_id: T-205
"""

from __future__ import annotations

from tests.conftest_platform import make_sync_like_path


def test_nonascii_sync_like_path_round_trips(tmp_path) -> None:  # type: ignore[no-untyped-def]
    sync_path = make_sync_like_path(tmp_path).path
    target = sync_path / "设计" / "construct.json"
    target.parent.mkdir(parents=True)
    target.write_text('{"ok": true}', encoding="utf-8")

    assert target.read_text(encoding="utf-8") == '{"ok": true}'
    assert "文档" in str(target)
