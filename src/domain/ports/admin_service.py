"""
module_id: domain.ports.admin_service
file: src/domain/ports/admin_service.py
task_id: T-1103a

Admin-service client Protocol used by CLI and API admin surfaces.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from domain.types.admin_ipc import (
    AdminIpcPayload,
    AdminIpcRequest,
    AdminIpcResponse,
    SignedAdminPrincipalToken,
)


@runtime_checkable
class AdminServiceClientPort(Protocol):
    def dispatch(self, request: AdminIpcRequest) -> AdminIpcResponse: ...

    def mint_profile(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def modify_profile(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def revoke_profile(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def list_profiles(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def view_audit_trail(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def mint_sop_template(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def modify_sop_template(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def revoke_sop_template(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def triage_review_queue_item(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...

    def rotate_audit_key(
        self,
        principal_token: SignedAdminPrincipalToken,
        payload: AdminIpcPayload,
        *,
        request_id: str | None = None,
        requested_at_utc: datetime | None = None,
    ) -> AdminIpcResponse: ...


__all__ = ["AdminServiceClientPort"]
