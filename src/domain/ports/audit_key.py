"""
module_id: domain.ports.audit_key
file: src/domain/ports/audit_key.py
task_id: T-312a

Audit-key provider Protocol with no raw-key exposure.
"""

from __future__ import annotations

from typing import NewType, Protocol, runtime_checkable

from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal

KeyVersionId = NewType("KeyVersionId", int)
MacBytes = NewType("MacBytes", bytes)


@runtime_checkable
class AuditKeyProvider(Protocol):
    def mac(self, message: bytes) -> tuple[KeyVersionId, MacBytes]: ...
    def verify(self, key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool: ...
    def verify_with_archived(
        self,
        key_version: KeyVersionId,
        message: bytes,
        mac: MacBytes,
    ) -> bool: ...
    def rotate(
        self,
        reason: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> KeyVersionId: ...
    def current_key_version(self) -> KeyVersionId: ...
