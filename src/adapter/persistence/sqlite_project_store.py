"""
module_id: adapter.persistence.sqlite_project_store
file: src/adapter/persistence/sqlite_project_store.py
task_id: T-310

SQLite project/session store with WAL durability settings.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from domain.sequence import sha256_text
from engine.session import DesignSession

JsonObject = dict[str, object]
Payload = tuple[tuple[str, str], ...]

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""


class ProjectNotFoundError(KeyError):
    """Raised when a project/session row cannot be found."""


@dataclass(frozen=True)
class SqliteProjectStore:
    path: Path

    def __init__(self, path: str | Path) -> None:
        object.__setattr__(self, "path", Path(path))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def save_project(self, project: Payload) -> str:
        payload = dict(project)
        project_id = payload.get("project_id") or str(
            sha256_text(json.dumps(payload, sort_keys=True))
        )
        self._upsert(str(project_id), payload)
        return str(project_id)

    def load_project(self, project_id: str) -> Payload:
        return tuple((key, str(value)) for key, value in self._load_json(project_id).items())

    def save_session(self, session: DesignSession) -> str:
        self._upsert(session.session_id, session.to_canonical_dict())
        return session.session_id

    def load_session_payload(self, session_id: str) -> JsonObject:
        return self._load_json(session_id)

    def list_sessions(self) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT project_id FROM projects ORDER BY project_id"
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _upsert(self, project_id: str, payload: Mapping[str, object]) -> None:
        payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                INSERT INTO projects(project_id, payload_json)
                VALUES (?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    updated_at_utc = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                """,
                (project_id, payload_json),
            )
            connection.commit()

    def _load_json(self, project_id: str) -> JsonObject:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        if row is None:
            raise ProjectNotFoundError(project_id)
        loaded = json.loads(str(row[0]))
        if not isinstance(loaded, dict):
            raise TypeError("project payload must be a JSON object")
        return dict(loaded)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection
