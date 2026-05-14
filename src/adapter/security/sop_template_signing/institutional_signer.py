"""
module_id: adapter.security.sop_template_signing.institutional_signer
file: src/adapter/security/sop_template_signing/institutional_signer.py
task_id: T-316c

Ed25519 institutional SOP-template signer.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from adapter.security.signing_key_archive import SigningKeyArchiveError, SigningKeyArchiveStore
from domain.security.identifiers import KeyVersionId
from domain.security.principals import AdminPrincipal, DeveloperBootstrapPrincipal, Principal
from domain.types.sop_template import SopTemplate, SopTemplateSignature


class Ed25519InstitutionalSopTemplateSigner:
    def __init__(
        self,
        archive_path: str | Path,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = SigningKeyArchiveStore(archive_path, purpose="sop_template")
        self._store.ensure_institutional_key()
        self._clock = clock or (lambda: datetime.now(UTC))

    def sign(
        self,
        template: SopTemplate,
        admin: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateSignature:
        _require_sop_template_admin(admin)
        record = self._store.current_institutional_record()
        if record.revoked:
            raise SigningKeyArchiveError(
                f"current SOP-template signing key is revoked: {record.key_version}"
            )
        payload = _sop_template_signature_payload(template)
        return SopTemplateSignature(
            template_content_hash=template.content_hash(),
            signature_bytes=record.private_key().sign(payload),
            signing_key_version=record.key_version,
            signed_at_utc=self._clock(),
        )

    def rotate(
        self,
        reason: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> KeyVersionId:
        if not reason.strip():
            raise ValueError("rotation reason cannot be empty")
        _require_sop_template_admin(principal)
        return self._store.rotate_institutional_key()

    def revoke(self, key_version: KeyVersionId, reason: str) -> None:
        self._store.revoke_key(key_version, reason)


def _sop_template_signature_payload(template: SopTemplate) -> bytes:
    return str(template.content_hash()).encode("utf-8")


def _require_sop_template_admin(admin: Principal) -> None:
    if isinstance(admin, AdminPrincipal):
        return
    if isinstance(admin, DeveloperBootstrapPrincipal) and admin.has_bootstrap_authority:
        return
    raise PermissionError("SOP-template signing requires administrator or bootstrap authority")
