"""
module_id: adapter.persistence.sqlite_review_queue_store
file: src/adapter/persistence/sqlite_review_queue_store.py
task_id: T-315

Append-only SQLite review-queue store.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from domain.security import AdminPrincipal, Principal, SecurityRole
from domain.types.review_queue import (
    AuthorisationRequest,
    ReviewQueueItem,
    ReviewQueueItemDecision,
    ReviewQueueItemId,
    ReviewQueueStatus,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS review_queue_requests (
    item_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    subject_user_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    related_session_id TEXT,
    request_json TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_queue_decisions (
    decision_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL REFERENCES review_queue_requests(item_id),
    decision_id TEXT NOT NULL UNIQUE,
    decision_status TEXT NOT NULL,
    decided_by_admin_id TEXT NOT NULL,
    assigned_admin_id TEXT,
    decision_json TEXT NOT NULL,
    decided_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_review_queue_requests_subject
ON review_queue_requests(subject_user_id);

CREATE INDEX IF NOT EXISTS idx_review_queue_decisions_item
ON review_queue_decisions(item_id, decision_sequence DESC);
"""


class ReviewQueueItemNotFoundError(KeyError):
    """Raised when a review queue item does not exist."""


class ReviewQueueRequestConflictError(ValueError):
    """Raised when the same request id is reused for a different payload."""


@dataclass(frozen=True)
class SqliteReviewQueueStore:
    path: Path

    def __init__(self, path: str | Path) -> None:
        db_path = Path(path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        object.__setattr__(self, "path", db_path)
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def add(self, request: AuthorisationRequest) -> str:
        request_json = _json_dumps(request.to_payload())
        item_id = str(request.item_id)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT request_json FROM review_queue_requests WHERE item_id = ?",
                (item_id,),
            ).fetchone()
            if existing is not None:
                if str(existing[0]) != request_json:
                    raise ReviewQueueRequestConflictError(item_id)
                connection.commit()
                return item_id
            connection.execute(
                """
                INSERT INTO review_queue_requests(
                    item_id,
                    request_id,
                    subject_user_id,
                    institution_id,
                    related_session_id,
                    request_json,
                    created_at_utc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    str(request.request_id),
                    str(request.subject_user_id),
                    str(request.institution_id),
                    request.related_session_id,
                    request_json,
                    _datetime_to_json(request.created_at_utc),
                ),
            )
            connection.commit()
        return item_id

    def resolve(
        self,
        item_id: str,
        decision: ReviewQueueItemDecision,
        admin_principal: AdminPrincipal,
    ) -> str:
        _require_admin(admin_principal)
        if str(decision.item_id) != item_id:
            raise ValueError("decision item_id does not match resolved item_id")
        decision_json = _json_dumps(decision.to_payload())
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if not self._exists(item_id, connection):
                raise ReviewQueueItemNotFoundError(item_id)
            connection.execute(
                """
                INSERT INTO review_queue_decisions(
                    item_id,
                    decision_id,
                    decision_status,
                    decided_by_admin_id,
                    assigned_admin_id,
                    decision_json,
                    decided_at_utc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    str(decision.decision_id),
                    decision.decision_status.value,
                    str(decision.decided_by_admin_id),
                    None if decision.assigned_admin_id is None else str(decision.assigned_admin_id),
                    decision_json,
                    _datetime_to_json(decision.decided_at_utc),
                ),
            )
            connection.commit()
        return str(decision.decision_id)

    def get(self, item_id: str) -> ReviewQueueItem:
        with self._connect() as connection:
            row = self._request_row(item_id, connection)
            decision = self._latest_decision(item_id, connection)
        return _item_from_rows(row, decision)

    def list_pending(self, admin_principal: AdminPrincipal) -> tuple[ReviewQueueItem, ...]:
        _require_admin(admin_principal)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT item_id FROM review_queue_requests ORDER BY created_at_utc, item_id"
            ).fetchall()
        items = tuple(self.get(str(row[0])) for row in rows)
        return tuple(item for item in items if item.is_open)

    def _request_row(self, item_id: str, connection: sqlite3.Connection) -> sqlite3.Row:
        row = connection.execute(
            """
            SELECT item_id, request_json, created_at_utc
            FROM review_queue_requests
            WHERE item_id = ?
            """,
            (item_id,),
        ).fetchone()
        if row is None:
            raise ReviewQueueItemNotFoundError(item_id)
        return cast(sqlite3.Row, row)

    def _latest_decision(
        self,
        item_id: str,
        connection: sqlite3.Connection,
    ) -> sqlite3.Row | None:
        row = connection.execute(
            """
            SELECT decision_json, decision_status, assigned_admin_id, decided_at_utc
            FROM review_queue_decisions
            WHERE item_id = ?
            ORDER BY decision_sequence DESC
            LIMIT 1
            """,
            (item_id,),
        ).fetchone()
        return None if row is None else cast(sqlite3.Row, row)

    def _exists(self, item_id: str, connection: sqlite3.Connection) -> bool:
        return (
            connection.execute(
                "SELECT 1 FROM review_queue_requests WHERE item_id = ?",
                (item_id,),
            ).fetchone()
            is not None
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection


def _item_from_rows(
    request_row: sqlite3.Row,
    decision_row: sqlite3.Row | None,
) -> ReviewQueueItem:
    request = AuthorisationRequest.from_payload(_json_loads(str(request_row["request_json"])))
    if decision_row is None:
        return ReviewQueueItem(
            item_id=ReviewQueueItemId(str(request_row["item_id"])),
            request=request,
            status=ReviewQueueStatus.PENDING,
            created_at_utc=_parse_datetime(str(request_row["created_at_utc"])),
            updated_at_utc=_parse_datetime(str(request_row["created_at_utc"])),
        )
    decision = ReviewQueueItemDecision.from_payload(_json_loads(str(decision_row["decision_json"])))
    return ReviewQueueItem(
        item_id=ReviewQueueItemId(str(request_row["item_id"])),
        request=request,
        status=decision.decision_status,
        created_at_utc=_parse_datetime(str(request_row["created_at_utc"])),
        updated_at_utc=decision.decided_at_utc,
        assigned_admin_id=decision.assigned_admin_id,
        decision=decision,
    )


def _require_admin(principal: Principal) -> AdminPrincipal:
    if isinstance(principal, AdminPrincipal) and principal.can_act_as(SecurityRole.ADMINISTRATOR):
        return principal
    raise PermissionError("review queue resolution requires administrator")


def _json_dumps(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _json_loads(payload: str) -> dict[str, object]:
    loaded = json.loads(payload)
    if not isinstance(loaded, dict):
        raise TypeError("review queue payload must be a JSON object")
    return dict(loaded)


def _datetime_to_json(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
