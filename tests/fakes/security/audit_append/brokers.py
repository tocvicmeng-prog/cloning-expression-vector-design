"""
module_id: tests.fakes.security.audit_append.brokers
file: tests/fakes/security/audit_append/brokers.py
task_id: T-313a
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.canonicalisation import canonical_json
from domain.ports.audit_append import AuditEntry, AuditEntryId
from domain.ports.audit_key import AuditKeyProvider, KeyVersionId, MacBytes
from domain.security import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    ServiceName,
    ServicePrincipal,
)


@dataclass(frozen=True)
class AuditChainRow:
    entry_id: AuditEntryId
    sequence: int
    entry: AuditEntry
    caller_kind: str
    caller_id: str
    previous_mac_hex: str
    key_version: KeyVersionId
    message: bytes
    mac: MacBytes

    @property
    def mac_hex(self) -> str:
        return bytes(self.mac).hex()


class FakeAuditChainStore:
    def __init__(self) -> None:
        self._rows: tuple[AuditChainRow, ...] = ()

    @property
    def rows(self) -> tuple[AuditChainRow, ...]:
        return self._rows

    def append(
        self,
        entry: AuditEntry,
        caller_kind: str,
        caller_id: str,
        key_provider: AuditKeyProvider,
    ) -> AuditEntryId:
        sequence = len(self._rows) + 1
        entry_id = AuditEntryId(f"audit-{sequence:06d}")
        previous_mac_hex = self._rows[-1].mac_hex if self._rows else ""
        message = _canonical_chain_message(
            entry=entry,
            entry_id=entry_id,
            sequence=sequence,
            caller_kind=caller_kind,
            caller_id=caller_id,
            previous_mac_hex=previous_mac_hex,
        )
        key_version, mac = key_provider.mac(message)
        self._rows = (
            *self._rows,
            AuditChainRow(
                entry_id=entry_id,
                sequence=sequence,
                entry=entry,
                caller_kind=caller_kind,
                caller_id=caller_id,
                previous_mac_hex=previous_mac_hex,
                key_version=key_version,
                message=message,
                mac=mac,
            ),
        )
        return entry_id


class FakeAuditBroker:
    """Engine-process audit append fake."""

    def __init__(
        self,
        key_provider: AuditKeyProvider,
        store: FakeAuditChainStore | None = None,
    ) -> None:
        self._key_provider = key_provider
        self._store = store or FakeAuditChainStore()

    @property
    def rows(self) -> tuple[AuditChainRow, ...]:
        return self._store.rows

    def append(self, entry: AuditEntry, caller: ServicePrincipal) -> AuditEntryId:
        _require_service_principal(caller)
        return self._store.append(
            entry=entry,
            caller_kind="service",
            caller_id=caller.service_name.value,
            key_provider=self._key_provider,
        )


class FakeAdminAuditBroker:
    """Admin-service audit append fake."""

    def __init__(
        self,
        key_provider: AuditKeyProvider,
        store: FakeAuditChainStore | None = None,
    ) -> None:
        self._key_provider = key_provider
        self._store = store or FakeAuditChainStore()

    @property
    def rows(self) -> tuple[AuditChainRow, ...]:
        return self._store.rows

    def append(
        self,
        entry: AuditEntry,
        caller: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> AuditEntryId:
        _require_admin_principal(caller)
        return self._store.append(
            entry=entry,
            caller_kind="admin",
            caller_id=str(caller.id),
            key_provider=self._key_provider,
        )


def _canonical_chain_message(
    *,
    entry: AuditEntry,
    entry_id: AuditEntryId,
    sequence: int,
    caller_kind: str,
    caller_id: str,
    previous_mac_hex: str,
) -> bytes:
    return canonical_json(
        {
            "caller_id": caller_id,
            "caller_kind": caller_kind,
            "entry": entry,
            "entry_id": str(entry_id),
            "previous_mac_hex": previous_mac_hex,
            "sequence": sequence,
        }
    )


def _require_service_principal(caller: object) -> None:
    if not isinstance(caller, ServicePrincipal):
        raise TypeError("engine audit appends require ServicePrincipal")


def _require_admin_principal(caller: object) -> None:
    if isinstance(caller, AdminPrincipal):
        return
    if isinstance(caller, DeveloperBootstrapPrincipal) and caller.has_bootstrap_authority:
        return
    raise PermissionError("admin audit appends require administrator or bootstrap authority")


def service_principal(
    service_name: ServiceName = ServiceName.AUTHORISATION_DECISION,
) -> ServicePrincipal:
    return ServicePrincipal(service_name=service_name, token=f"token:{service_name.value}".encode())
