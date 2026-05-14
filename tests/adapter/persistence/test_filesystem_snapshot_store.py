"""
module_id: tests.adapter.persistence.test_filesystem_snapshot_store
file: tests/adapter/persistence/test_filesystem_snapshot_store.py
task_id: T-310
"""

from __future__ import annotations

from pathlib import Path

from adapter.persistence import FilesystemSnapshotStore
from domain.sequence import sha256_text


def test_filesystem_snapshot_store_keeps_latest_per_hash_and_recent_window(tmp_path: Path) -> None:
    store = FilesystemSnapshotStore(tmp_path / "snapshots", retain_per_session=2)
    first_hash = str(sha256_text("env-a"))
    second_hash = str(sha256_text("env-b"))

    for event_seq, derivation_hash in (
        (1, first_hash),
        (2, second_hash),
        (3, first_hash),
    ):
        store.write_snapshot(
            "session-1",
            event_seq,
            {
                "session_id": "session-1",
                "event_seq": event_seq,
                "derivation_environment_hash": derivation_hash,
            },
        )

    latest = store.read_latest_snapshot("session-1")
    matching = store.latest_matching("session-1", sha256_text("env-a"))

    assert latest is not None
    assert latest["event_seq"] == 3
    assert matching is not None
    assert matching["event_seq"] == 3
    assert len(tuple((tmp_path / "snapshots" / "session-1").glob("*.json"))) == 2
