"""
module_id: tests.app.review_queue.test_admin_triages_request_via_port_only
file: tests/app/review_queue/test_admin_triages_request_via_port_only.py
task_id: T-315
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from domain.events import ReviewQueueItemResolved
from domain.types.review_queue import ReviewQueueStatus
from tests.app.review_queue.helpers import (
    admin_resolution_stack,
    requested_scope,
    review_queue_stack,
    user_principal,
)


def test_admin_triages_request_via_port_only_and_request_row_is_immutable(
    tmp_path: Path,
) -> None:
    service, store, governance_log, _audit = review_queue_stack(tmp_path)
    item = service.submit_extension_request(
        user_principal(),
        requested_scope(),
        "Request expanded operational scope for this design.",
    ).item
    before_json = _stored_request_json(store.path, str(item.item_id))
    resolver, admin_audit, admin = admin_resolution_stack(store, governance_log)

    result = resolver.resolve_item(
        admin,
        str(item.item_id),
        ReviewQueueStatus.APPROVED,
        justification="Approved after institutional review.",
    )

    assert result.item.status is ReviewQueueStatus.APPROVED
    assert result.item.decision is not None
    assert admin_audit.rows[0].entry.entry_type == "ReviewQueueItemResolved"
    assert _stored_request_json(store.path, str(item.item_id)) == before_json
    event = governance_log.read_events("inst")[-1]
    assert isinstance(event, ReviewQueueItemResolved)
    assert dict(event.decision_payload)["decision_record_payload_json"]


def _stored_request_json(path: Path, item_id: str) -> str:
    with sqlite3.connect(path) as connection:
        row = connection.execute(
            "SELECT request_json FROM review_queue_requests WHERE item_id = ?",
            (item_id,),
        ).fetchone()
    assert row is not None
    return str(row[0])
