"""
module_id: tests.app.review_queue.helpers
file: tests/app/review_queue/helpers.py
task_id: T-315
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from adapter.persistence import JsonlEventLog, SqliteReviewQueueStore
from app.review_queue_service import ReviewQueueAdminResolutionService, ReviewQueueService
from domain.events import EventStream
from domain.security import (
    AdminPrincipal,
    CoveredBiologicalScope,
    InstitutionId,
    PrincipalId,
    ReviewerPrincipal,
    SecurityRole,
    ServiceName,
    ServicePrincipal,
    UserPrincipal,
)
from tests.fakes.security.audit_append.brokers import FakeAdminAuditBroker, FakeAuditBroker
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.fakes.security.profile_signing.fixtures import admin_principal, unsigned_profile_draft
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner

NOW = datetime(2026, 5, 14, tzinfo=UTC)


def user_principal() -> UserPrincipal:
    return UserPrincipal(
        id=PrincipalId("user-1"),
        role=SecurityRole.USER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def reviewer_principal() -> ReviewerPrincipal:
    return ReviewerPrincipal(
        id=PrincipalId("reviewer-1"),
        role=SecurityRole.REVIEWER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def service_principal(
    service_name: ServiceName = ServiceName.REVIEW_QUEUE,
) -> ServicePrincipal:
    return ServicePrincipal(
        service_name=service_name,
        token=f"token:{service_name.value}".encode(),
    )


def requested_scope() -> CoveredBiologicalScope:
    return unsigned_profile_draft().covered_scope


def review_queue_stack(
    tmp_path: Path,
) -> tuple[ReviewQueueService, SqliteReviewQueueStore, JsonlEventLog, FakeAuditBroker]:
    store = SqliteReviewQueueStore(tmp_path / "review_queue.sqlite")
    governance_log = JsonlEventLog(
        tmp_path / "events" / "governance",
        expected_stream=EventStream.GOVERNANCE,
    )
    audit = FakeAuditBroker(TestAuditKeyProvider())
    service = ReviewQueueService(
        review_queue_store=store,
        audit_append=audit,
        governance_event_log=governance_log,
        service_principal=service_principal(),
        clock=lambda: NOW,
    )
    return service, store, governance_log, audit


def admin_resolution_stack(
    store: SqliteReviewQueueStore,
    governance_log: JsonlEventLog,
) -> tuple[ReviewQueueAdminResolutionService, FakeAdminAuditBroker, AdminPrincipal]:
    audit = FakeAdminAuditBroker(TestAuditKeyProvider())
    resolver = ReviewQueueAdminResolutionService(
        review_queue_store=store,
        review_queue_admin_port=store,
        decision_record_signer=FakeDecisionRecordSigner(),
        audit_append=audit,
        governance_event_log=governance_log,
        clock=lambda: NOW,
    )
    return resolver, audit, admin_principal()
