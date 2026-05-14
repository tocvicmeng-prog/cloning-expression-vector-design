"""
module_id: tests.app.review_queue.test_blocked_sop_creates_single_request
file: tests/app/review_queue/test_blocked_sop_creates_single_request.py
task_id: T-315
"""

from __future__ import annotations

from pathlib import Path

from domain.security import InstitutionId, ServiceName, UserId
from domain.types.review_queue import ReviewQueueStatus
from tests.app.review_queue.helpers import (
    requested_scope,
    review_queue_stack,
    service_principal,
)
from tests.fakes.security.profile_signing.fixtures import admin_principal


def test_blocked_sop_creates_single_pending_request_on_retry(tmp_path: Path) -> None:
    service, store, governance_log, audit = review_queue_stack(tmp_path)
    caller = service_principal(ServiceName.AUTHORISATION_DECISION)

    first = service.route_blocked_authorisation(
        "session-1",
        "missing profile coverage",
        caller,
        subject_user_id=UserId("user-1"),
        institution_id=InstitutionId("inst"),
        requested_scope=requested_scope(),
    )
    second = service.route_blocked_authorisation(
        "session-1",
        "missing profile coverage",
        caller,
        subject_user_id=UserId("user-1"),
        institution_id=InstitutionId("inst"),
        requested_scope=requested_scope(),
    )

    assert first.item.item_id == second.item.item_id
    assert first.created
    assert not second.created
    assert store.list_pending(admin_principal())[0].status is ReviewQueueStatus.PENDING
    assert len(store.list_pending(admin_principal())) == 1
    assert len(audit.rows) == 1
    assert len(governance_log.read_events("inst")) == 1
