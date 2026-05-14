"""
module_id: tests.app.review_queue.test_user_submits_request
file: tests/app/review_queue/test_user_submits_request.py
task_id: T-315
"""

from __future__ import annotations

from pathlib import Path

from app.review_queue import ReviewQueueService as FacadeReviewQueueService
from domain.events import AuthorisationExtensionRequested, ReviewQueueItemCreated
from domain.types.review_queue import ReviewQueueStatus
from tests.app.review_queue.helpers import (
    requested_scope,
    review_queue_stack,
    user_principal,
)
from tests.fakes.security.profile_signing.fixtures import admin_principal


def test_user_submits_extension_request_to_pending_queue(tmp_path: Path) -> None:
    service, store, governance_log, audit = review_queue_stack(tmp_path)

    result = service.submit_extension_request(
        user_principal(),
        requested_scope(),
        "Request expanded operational scope for this design.",
        supporting_evidence=(("design_session_id", "session-1"),),
    )

    assert result.created
    assert isinstance(service, FacadeReviewQueueService)
    assert result.item.status is ReviewQueueStatus.PENDING
    assert store.list_pending(admin_principal()) == (result.item,)
    assert audit.rows[0].entry.entry_type == "AuthorisationExtensionRequested"

    events = governance_log.read_events("inst")
    assert isinstance(events[0], AuthorisationExtensionRequested)
    assert isinstance(events[1], ReviewQueueItemCreated)
    assert dict(events[0].request_payload)["requested_scope_json"]
