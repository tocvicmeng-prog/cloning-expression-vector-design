"""
module_id: domain.ports.audit_append
file: src/domain/ports/audit_append.py
task_id: T-313a

Append-only audit client Protocols for the dedicated audit-service writer.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Protocol, runtime_checkable

from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, ServicePrincipal

AuditEntryId = NewType("AuditEntryId", str)


@dataclass(frozen=True)
class AuditEntry:
    entry_type: str
    payload: Mapping[str, object]
    occurred_at_utc: datetime

    def __post_init__(self) -> None:
        if not self.entry_type:
            raise ValueError("entry_type cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise ValueError("occurred_at_utc must be timezone-aware")


@runtime_checkable
class AuditAppendPort(Protocol):
    def append(self, entry: AuditEntry, caller: ServicePrincipal) -> AuditEntryId: ...


@runtime_checkable
class AdminAuditAppendPort(Protocol):
    def append(
        self,
        entry: AuditEntry,
        caller: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> AuditEntryId: ...
