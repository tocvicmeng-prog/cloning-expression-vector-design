"""
module_id: domain.ports.review_queue_admin
file: src/domain/ports/review_queue_admin.py
task_id: T-315

Review-queue request and admin-resolution Protocols.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from domain.security import AdminPrincipal
from domain.types.review_queue import (
    AuthorisationRequest,
    ReviewQueueItem,
    ReviewQueueItemDecision,
)


@runtime_checkable
class ReviewQueueStore(Protocol):
    def add(self, request: AuthorisationRequest) -> str: ...
    def list_pending(self, admin_principal: AdminPrincipal) -> tuple[ReviewQueueItem, ...]: ...
    def get(self, item_id: str) -> ReviewQueueItem: ...


@runtime_checkable
class ReviewQueueAdminPort(Protocol):
    def resolve(
        self,
        item_id: str,
        decision: ReviewQueueItemDecision,
        admin_principal: AdminPrincipal,
    ) -> str: ...
