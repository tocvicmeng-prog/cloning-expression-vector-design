"""
module_id: adapter.persistence.filesystem_snapshot_store
file: src/adapter/persistence/filesystem_snapshot_store.py
task_id: T-310

Filesystem snapshot store for replay acceleration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from domain.sequence import Sha256
from engine.session import DesignSession

JsonObject = dict[str, object]


@dataclass(frozen=True)
class FilesystemSnapshotStore:
    root_dir: Path
    retain_per_session: int = 10

    def __init__(self, root_dir: str | Path, retain_per_session: int = 10) -> None:
        if retain_per_session <= 0:
            raise ValueError("retain_per_session must be positive")
        root = Path(root_dir)
        root.mkdir(parents=True, exist_ok=True)
        object.__setattr__(self, "root_dir", root)
        object.__setattr__(self, "retain_per_session", retain_per_session)

    def write_snapshot(self, session_id: str, event_seq: int, snapshot: JsonObject) -> str:
        derivation_hash = _required_hash(snapshot)
        path = self._path(session_id, event_seq, derivation_hash)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(snapshot, sort_keys=True, separators=(",", ":")), encoding="utf-8"
        )
        self._cleanup(session_id)
        return str(path)

    def write_session_snapshot(self, session: DesignSession, event_seq: int) -> str:
        return self.write_snapshot(session.session_id, event_seq, session.to_canonical_dict())

    def read_latest_snapshot(self, session_id: str) -> JsonObject | None:
        snapshots = self._snapshot_paths(session_id)
        if not snapshots:
            return None
        return _read_json(snapshots[-1])

    def latest_matching(
        self, session_id: str, derivation_environment_hash: Sha256
    ) -> JsonObject | None:
        for path in reversed(self._snapshot_paths(session_id)):
            if path.stem.endswith(f"_{derivation_environment_hash}"):
                return _read_json(path)
        return None

    def _path(self, session_id: str, event_seq: int, derivation_hash: str) -> Path:
        if not session_id:
            raise ValueError("session_id cannot be empty")
        if event_seq < 0:
            raise ValueError("event_seq cannot be negative")
        return self.root_dir / session_id / f"{event_seq:012d}_{derivation_hash}.json"

    def _snapshot_paths(self, session_id: str) -> tuple[Path, ...]:
        session_dir = self.root_dir / session_id
        if not session_dir.exists():
            return ()
        return tuple(sorted(session_dir.glob("*.json")))

    def _cleanup(self, session_id: str) -> None:
        snapshots = self._snapshot_paths(session_id)
        keep = set(snapshots[-self.retain_per_session :])
        latest_by_hash: dict[str, Path] = {}
        for path in snapshots:
            latest_by_hash[path.stem.split("_", maxsplit=1)[1]] = path
        keep.update(latest_by_hash.values())
        for path in snapshots:
            if path not in keep:
                path.unlink(missing_ok=True)


def _required_hash(snapshot: JsonObject) -> str:
    value = snapshot.get("derivation_environment_hash")
    if not isinstance(value, str) or not value:
        raise ValueError("snapshot requires derivation_environment_hash")
    return value


def _read_json(path: Path) -> JsonObject:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError("snapshot must contain a JSON object")
    return dict(loaded)
