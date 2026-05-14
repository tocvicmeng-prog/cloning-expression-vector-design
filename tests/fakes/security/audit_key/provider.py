"""
module_id: tests.fakes.security.audit_key.provider
file: tests/fakes/security/audit_key/provider.py
task_id: T-312a
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

from domain.ports.audit_key import KeyVersionId, MacBytes
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, Principal


@dataclass(frozen=True)
class AuditKeyRotation:
    old_key_version: KeyVersionId
    new_key_version: KeyVersionId
    reason: str
    principal_id: str


class TestAuditKeyProvider:
    """Deterministic in-memory audit-key provider for contract and integration tests."""

    __test__ = False

    def __init__(self, initial_key: bytes = b"cev-test-audit-key-v1") -> None:
        if not initial_key:
            raise ValueError("initial_key cannot be empty")
        self._current_version = 1
        self._keys: dict[int, bytes] = {self._current_version: initial_key}
        self._archived_versions: set[int] = set()
        self._rotation_log: tuple[AuditKeyRotation, ...] = ()

    @property
    def rotation_log(self) -> tuple[AuditKeyRotation, ...]:
        return self._rotation_log

    def mac(self, message: bytes) -> tuple[KeyVersionId, MacBytes]:
        return (
            KeyVersionId(self._current_version),
            MacBytes(hmac.new(self._current_key(), message, hashlib.sha256).digest()),
        )

    def verify(self, key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool:
        key = self._keys.get(int(key_version))
        if key is None:
            return False
        return hmac.compare_digest(hmac.new(key, message, hashlib.sha256).digest(), bytes(mac))

    def verify_with_archived(
        self,
        key_version: KeyVersionId,
        message: bytes,
        mac: MacBytes,
    ) -> bool:
        version = int(key_version)
        if version == self._current_version or version in self._archived_versions:
            return self.verify(key_version, message, mac)
        return False

    def rotate(
        self,
        reason: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> KeyVersionId:
        if not reason:
            raise ValueError("rotation reason cannot be empty")
        _require_rotation_authority(principal)

        old_version = self._current_version
        new_version = old_version + 1
        self._archived_versions.add(old_version)
        self._keys[new_version] = _derive_next_key(self._keys[old_version], new_version, reason)
        self._current_version = new_version
        rotation = AuditKeyRotation(
            old_key_version=KeyVersionId(old_version),
            new_key_version=KeyVersionId(new_version),
            reason=reason,
            principal_id=str(principal.id),
        )
        self._rotation_log = (*self._rotation_log, rotation)
        return KeyVersionId(new_version)

    def current_key_version(self) -> KeyVersionId:
        return KeyVersionId(self._current_version)

    def _current_key(self) -> bytes:
        return self._keys[self._current_version]


def _derive_next_key(old_key: bytes, new_version: int, reason: str) -> bytes:
    payload = f"{new_version}:{reason}".encode()
    return hmac.new(old_key, payload, hashlib.sha256).digest()


def _require_rotation_authority(principal: Principal) -> None:
    if isinstance(principal, AdminPrincipal):
        return
    if isinstance(principal, DeveloperBootstrapPrincipal) and principal.has_bootstrap_authority:
        return
    raise PermissionError("audit-key rotation requires administrator or bootstrap authority")
