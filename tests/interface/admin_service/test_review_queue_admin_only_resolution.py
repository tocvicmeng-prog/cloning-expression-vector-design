"""
module_id: tests.interface.admin_service.test_review_queue_admin_only_resolution
file: tests/interface/admin_service/test_review_queue_admin_only_resolution.py
task_id: T-1103b
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

from domain.types.admin_ipc import AdminIpcStatus
from domain.types.review_queue import ReviewQueueStatus
from interface.admin_service import AdminServiceReviewQueueHandler
from tests.app.review_queue.helpers import (
    admin_resolution_stack,
    requested_scope,
    review_queue_stack,
    user_principal,
)
from tests.interface.admin_service.helpers import NOW, harness, token


def test_review_queue_admin_only_resolution(tmp_path: Path) -> None:
    submitter, store, governance_log, _audit = review_queue_stack(tmp_path)
    created = submitter.submit_extension_request(
        user_principal(),
        requested_scope(),
        "Need a scoped temporary authorisation extension.",
    )
    resolver, _admin_audit, _admin = admin_resolution_stack(store, governance_log)
    app = harness(
        review_queue_handler=AdminServiceReviewQueueHandler(
            store=store,
            resolution_service=resolver,
        )
    )

    denied = app.client.triage_review_queue_item(
        token("user"),
        {
            "decision_status": ReviewQueueStatus.APPROVED.value,
            "item_id": str(created.item.item_id),
            "justification": "self-approval attempt",
        },
        requested_at_utc=NOW,
    )
    response = app.client.triage_review_queue_item(
        token(),
        {
            "decision_status": ReviewQueueStatus.APPROVED.value,
            "item_id": str(created.item.item_id),
            "justification": "Approved by administrator after review.",
        },
        requested_at_utc=NOW,
    )

    assert denied.status is AdminIpcStatus.DENIED
    assert response.status is AdminIpcStatus.ACCEPTED
    item_payload = cast(dict[str, object], response.payload["item"])
    assert item_payload["status"] == ReviewQueueStatus.APPROVED.value
    assert store.get(str(created.item.item_id)).status is ReviewQueueStatus.APPROVED


def test_cli_api_cannot_import_review_queue_admin_port_or_handler() -> None:
    forbidden = (
        "AdminActionHandler",
        "ReviewQueueAdminPort",
        "ReviewQueueAdminResolutionService",
    )
    checked_files = tuple(Path("src/interface/cli").rglob("*.py")) + tuple(
        Path("src/interface/api").rglob("*.py")
    )

    offenders = [
        str(path)
        for path in checked_files
        if any(term in path.read_text(encoding="utf-8") for term in forbidden)
    ]

    assert offenders == []
