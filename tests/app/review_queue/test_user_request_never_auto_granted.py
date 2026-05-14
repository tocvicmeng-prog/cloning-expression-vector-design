"""
module_id: tests.app.review_queue.test_user_request_never_auto_granted
file: tests/app/review_queue/test_user_request_never_auto_granted.py
task_id: T-315
"""

from __future__ import annotations

from pathlib import Path

from adapter.persistence import SqliteAuthorisationStoreWrite
from tests.app.review_queue.helpers import (
    requested_scope,
    review_queue_stack,
    user_principal,
)


def test_user_request_never_modifies_authorisation_profiles(tmp_path: Path) -> None:
    authorisation_store = SqliteAuthorisationStoreWrite(tmp_path / "authorisation.sqlite")
    service, _store, _governance_log, _audit = review_queue_stack(tmp_path)

    service.submit_extension_request(
        user_principal(),
        requested_scope(),
        "Request expanded operational scope for this design.",
    )

    assert authorisation_store.list_profiles() == ()
