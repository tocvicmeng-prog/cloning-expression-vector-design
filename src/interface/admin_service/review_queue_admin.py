"""
module_id: interface.admin_service.review_queue_admin
file: src/interface/admin_service/review_queue_admin.py
task_id: T-1103b

Admin-service adapter for ReviewQueueAdminPort operations.
"""

from __future__ import annotations

from app.review_queue_service import ReviewQueueAdminResolutionService
from domain.ports.review_queue_admin import ReviewQueueStore
from domain.security import AdminPrincipal, Principal, PrincipalId, SecurityRole
from domain.types.review_queue import ReviewQueueStatus


class AdminServiceReviewQueueHandler:
    """Routes admin-service IPC payloads to the review-queue admin service."""

    def __init__(
        self,
        *,
        store: ReviewQueueStore | None = None,
        resolution_service: ReviewQueueAdminResolutionService | None = None,
    ) -> None:
        self._store = store
        self._resolution_service = resolution_service

    def dispatch(self, principal: Principal, payload: dict[str, object]) -> dict[str, object]:
        operation = _optional_str(payload.get("admin_operation")) or "triage_request"
        if operation == "list_review_queue":
            return self.list_pending(principal)
        if operation == "triage_request":
            return self.triage(principal, payload)
        raise ValueError(f"unsupported review-queue admin operation: {operation}")

    def list_pending(self, principal: Principal) -> dict[str, object]:
        admin = _require_admin(principal)
        if self._store is None:
            raise RuntimeError("review-queue store is not configured")
        return {"items": [item.to_payload() for item in self._store.list_pending(admin)]}

    def triage(self, principal: Principal, payload: dict[str, object]) -> dict[str, object]:
        admin = _require_admin(principal)
        if self._resolution_service is None:
            raise RuntimeError("review-queue resolution service is not configured")
        assigned_admin_id = _optional_str(payload.get("assigned_admin_id"))
        result = self._resolution_service.resolve_item(
            admin,
            _expect_str(payload, "item_id"),
            ReviewQueueStatus(_expect_str(payload, "decision_status")),
            justification=_expect_str(payload, "justification"),
            assigned_admin_id=None if assigned_admin_id is None else PrincipalId(assigned_admin_id),
        )
        return {
            "audit_entry_id": result.audit_entry_id,
            "governance_event_id": result.governance_event_id,
            "item": result.item.to_payload(),
        }


def _require_admin(principal: Principal) -> AdminPrincipal:
    if isinstance(principal, AdminPrincipal) and principal.can_act_as(SecurityRole.ADMINISTRATOR):
        return principal
    raise PermissionError("review queue admin operations require administrator")


def _expect_str(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    if not value.strip():
        raise ValueError(f"{key} cannot be empty")
    return value


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("optional review-queue payload field must be a string")
    return value


__all__ = ["AdminServiceReviewQueueHandler"]
