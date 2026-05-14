"""
module_id: tests.app.review_queue.test_cli_api_cannot_resolve_without_admin_service
file: tests/app/review_queue/test_cli_api_cannot_resolve_without_admin_service.py
task_id: T-315
"""

from __future__ import annotations

from pathlib import Path

import pytest

from domain.types.review_queue import ReviewQueueStatus
from tests.app.review_queue.helpers import (
    admin_resolution_stack,
    requested_scope,
    review_queue_stack,
    reviewer_principal,
    user_principal,
)


def test_cli_api_paths_have_no_user_facing_resolution_surface(tmp_path: Path) -> None:
    service, store, governance_log, _audit = review_queue_stack(tmp_path)
    item = service.submit_extension_request(
        user_principal(),
        requested_scope(),
        "Request expanded operational scope for this design.",
    ).item
    resolver, _admin_audit, _admin = admin_resolution_stack(store, governance_log)

    assert not hasattr(service, "resolve")
    assert not hasattr(service, "triage_request")
    with pytest.raises(PermissionError, match="administrator"):
        resolver.resolve_item(
            reviewer_principal(),
            str(item.item_id),
            ReviewQueueStatus.DENIED,
            justification="Reviewer cannot perform administrator triage.",
        )
