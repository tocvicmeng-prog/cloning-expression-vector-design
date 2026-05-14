"""
module_id: tests.app.review_queue.test_user_cannot_self_approve
file: tests/app/review_queue/test_user_cannot_self_approve.py
task_id: T-315
"""

from __future__ import annotations

from pathlib import Path

import pytest

from domain.events import AuthorisationAttemptDenied
from domain.types.review_queue import ReviewQueueStatus
from tests.app.review_queue.helpers import (
    admin_resolution_stack,
    requested_scope,
    review_queue_stack,
    user_principal,
)


def test_user_cannot_self_approve_review_queue_item(tmp_path: Path) -> None:
    service, store, governance_log, _audit = review_queue_stack(tmp_path)
    item = service.submit_extension_request(
        user_principal(),
        requested_scope(),
        "Request expanded operational scope for this design.",
    ).item
    resolver, _admin_audit, _admin = admin_resolution_stack(store, governance_log)

    with pytest.raises(PermissionError, match="administrator"):
        resolver.resolve_item(
            user_principal(),
            str(item.item_id),
            ReviewQueueStatus.APPROVED,
            justification="Self approval must be rejected.",
        )

    events = governance_log.read_events("inst")
    assert isinstance(events[-1], AuthorisationAttemptDenied)
    assert store.get(str(item.item_id)).status is ReviewQueueStatus.PENDING
    assert not hasattr(service, "resolve_item")
