"""
module_id: engine.session.snapshots
file: src/engine/session/snapshots.py
task_id: T-309

Snapshot selection keyed by derivation-environment hash.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.events import SessionId
from domain.sequence import Sha256
from engine.session.state_machine import DesignSession


@dataclass(frozen=True)
class SessionSnapshot:
    session_id: SessionId
    event_sequence: int
    derivation_environment_hash: Sha256
    session: DesignSession

    def __post_init__(self) -> None:
        if not self.session_id:
            raise ValueError("snapshot session_id cannot be empty")
        if self.event_sequence < 0:
            raise ValueError("snapshot event_sequence cannot be negative")
        if self.session.session_id != self.session_id:
            raise ValueError("snapshot session must match session_id")


@dataclass
class InMemorySnapshotStore:
    retain_per_session: int = 10
    _snapshots: dict[SessionId, tuple[SessionSnapshot, ...]] | None = None

    def __post_init__(self) -> None:
        if self.retain_per_session <= 0:
            raise ValueError("retain_per_session must be positive")
        if self._snapshots is None:
            self._snapshots = {}

    def save(self, snapshot: SessionSnapshot) -> None:
        snapshots = (*self._items(snapshot.session_id), snapshot)
        snapshots = tuple(sorted(snapshots, key=lambda item: item.event_sequence))
        assert self._snapshots is not None
        self._snapshots[snapshot.session_id] = self._pruned(snapshots)

    def latest_matching(
        self,
        session_id: SessionId,
        derivation_environment_hash: Sha256,
    ) -> SessionSnapshot | None:
        for snapshot in reversed(self._items(session_id)):
            if snapshot.derivation_environment_hash == derivation_environment_hash:
                return snapshot
        return None

    def list_session(self, session_id: SessionId) -> tuple[SessionSnapshot, ...]:
        return self._items(session_id)

    def _items(self, session_id: SessionId) -> tuple[SessionSnapshot, ...]:
        assert self._snapshots is not None
        return self._snapshots.get(session_id, ())

    def _pruned(self, snapshots: tuple[SessionSnapshot, ...]) -> tuple[SessionSnapshot, ...]:
        keep_by_hash: dict[Sha256, SessionSnapshot] = {}
        for snapshot in snapshots:
            keep_by_hash[snapshot.derivation_environment_hash] = snapshot
        retained = set(keep_by_hash.values())
        retained.update(snapshots[-self.retain_per_session :])
        return tuple(sorted(retained, key=lambda item: item.event_sequence))
