"""
module_id: adapter.security.profile_signing.institutional_signer
file: src/adapter/security/profile_signing/institutional_signer.py
task_id: T-314b

Ed25519 institutional authorisation-profile signer.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from adapter.security.signing_key_archive import SigningKeyArchiveStore
from domain.security import (
    AdminPrincipal,
    AuthorisationProfile,
    DeveloperBootstrapPrincipal,
    KeyVersionId,
    Principal,
    ProfileSignature,
)


class Ed25519InstitutionalProfileSigner:
    def __init__(
        self,
        archive_path: str | Path,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = SigningKeyArchiveStore(archive_path, purpose="profile")
        self._store.ensure_institutional_key()
        self._clock = clock or (lambda: datetime.now(UTC))

    def sign(
        self,
        profile: AuthorisationProfile,
        admin: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> ProfileSignature:
        _require_profile_admin(admin)
        record = self._store.current_institutional_record()
        payload = _profile_signature_payload(profile)
        return ProfileSignature(
            signed_payload_hash=profile.profile_content_hash,
            signature_bytes=record.private_key().sign(payload),
            signing_key_version=record.key_version,
            signed_at_utc=self._clock(),
        )

    def rotate(
        self, reason: str, principal: AdminPrincipal | DeveloperBootstrapPrincipal
    ) -> KeyVersionId:
        if not reason.strip():
            raise ValueError("rotation reason cannot be empty")
        _require_profile_admin(principal)
        return self._store.rotate_institutional_key()

    def revoke(self, key_version: KeyVersionId, reason: str) -> None:
        self._store.revoke_key(key_version, reason)


def _profile_signature_payload(profile: AuthorisationProfile) -> bytes:
    return str(profile.profile_content_hash).encode("utf-8")


def _require_profile_admin(admin: Principal) -> None:
    if isinstance(admin, AdminPrincipal):
        return
    if isinstance(admin, DeveloperBootstrapPrincipal) and admin.has_bootstrap_authority:
        return
    raise PermissionError("profile signing requires administrator or bootstrap authority")
