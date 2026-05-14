"""
module_id: tests.app.review_queue.test_gate_recovery_path
file: tests/app/review_queue/test_gate_recovery_path.py
task_id: T-315
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.persistence import (
    AuthorisationProfileNotFoundError,
    JsonlEventLog,
    SqliteAuthorisationStoreRead,
    SqliteAuthorisationStoreWrite,
)
from app.admin_action_handler import AdminActionHandler
from domain.events import EventStream
from domain.security import InstitutionId, ServiceName, UserId
from domain.types.review_queue import ReviewQueueStatus
from tests.app.review_queue.helpers import (
    admin_resolution_stack,
    requested_scope,
    review_queue_stack,
    service_principal,
)
from tests.fakes.security.audit_append.brokers import FakeAdminAuditBroker
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    unsigned_profile_draft,
)
from tests.fakes.security.profile_signing.signers import FakeProfileSigner, FakeProfileVerifier


def test_gate_recovery_requires_queue_approval_then_profile_grant(tmp_path: Path) -> None:
    authorisation_writer = SqliteAuthorisationStoreWrite(tmp_path / "authorisation.sqlite")
    authorisation_reader = SqliteAuthorisationStoreRead(
        authorisation_writer.path,
        FakeProfileVerifier(),
    )
    service, store, governance_log, _audit = review_queue_stack(tmp_path)
    item = service.route_blocked_authorisation(
        "session-1",
        "missing profile coverage",
        service_principal(ServiceName.AUTHORISATION_DECISION),
        subject_user_id=UserId("user-1"),
        institution_id=InstitutionId("inst"),
        requested_scope=requested_scope(),
    ).item

    with pytest.raises(AuthorisationProfileNotFoundError):
        authorisation_reader.read_own_profile("user-1")

    resolver, _admin_audit, admin = admin_resolution_stack(store, governance_log)
    resolver.resolve_item(
        admin,
        str(item.item_id),
        ReviewQueueStatus.APPROVED,
        justification="Approved after institutional review.",
    )

    with pytest.raises(AuthorisationProfileNotFoundError):
        authorisation_reader.read_own_profile("user-1")

    handler = AdminActionHandler(
        authorisation_store=authorisation_writer,
        profile_signer=FakeProfileSigner(),
        audit_append=FakeAdminAuditBroker(TestAuditKeyProvider()),
        governance_event_log=JsonlEventLog(
            tmp_path / "admin-events",
            expected_stream=EventStream.GOVERNANCE,
        ),
        clock=lambda: item.created_at_utc,
    )
    handler.mint_profile(
        admin_principal(),
        unsigned_profile_draft(),
        justification="Grant scope after approved review-queue item.",
    )

    assert authorisation_reader.read_own_profile("user-1").subject_user_id == UserId("user-1")
