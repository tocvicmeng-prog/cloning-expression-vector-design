"""
module_id: tests.fakes.sop_template.signer
file: tests/fakes/sop_template/signer.py
task_id: T-316a
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import replace
from datetime import UTC, datetime

from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, KeyVersionId
from domain.types.signing_errors import (
    Result,
    RevokedKeyError,
    SopTemplateTamperDetectedError,
    SopTemplateVerificationResult,
    UnknownKeyVersionError,
)
from domain.types.sop_template import SopTemplate, SopTemplateSignature

SIGNED_AT = datetime(2026, 5, 14, tzinfo=UTC)
SOP_TEMPLATE_TEST_KEY_VERSION = KeyVersionId("sop-template-test-key-v1")


class FakeSopTemplateSigner:
    __test__ = False

    def __init__(self, key_version: KeyVersionId = SOP_TEMPLATE_TEST_KEY_VERSION) -> None:
        self._key_version = key_version
        self._keys: dict[str, bytes] = {str(key_version): b"sop-template-signing-test-key"}

    def sign(
        self,
        template: SopTemplate,
        admin: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateSignature:
        _require_template_admin(admin)
        content_hash = template.content_hash()
        return SopTemplateSignature(
            template_content_hash=content_hash,
            signature_bytes=_mac(self._keys[str(self._key_version)], str(content_hash)),
            signing_key_version=self._key_version,
            signed_at_utc=SIGNED_AT,
        )


class FakeSopTemplateVerifier:
    __test__ = False

    def __init__(self, keys: dict[str, bytes] | None = None) -> None:
        self._keys = keys or {"sop-template-test-key-v1": b"sop-template-signing-test-key"}
        self._revoked: set[str] = set()

    def revoke(self, key_version: KeyVersionId) -> None:
        self._revoked.add(str(key_version))

    def verify(self, template: SopTemplate) -> SopTemplateVerificationResult:
        if template.signature is None:
            return Result.fail(SopTemplateTamperDetectedError("template is unsigned"))
        key_version = str(template.signature.signing_key_version)
        key = self._keys.get(key_version)
        if key is None:
            return Result.fail(UnknownKeyVersionError(key_version))
        if key_version in self._revoked:
            return Result.fail(RevokedKeyError(key_version))
        content_hash = template.content_hash()
        if template.signature.template_content_hash != content_hash:
            return Result.fail(SopTemplateTamperDetectedError("template content hash mismatch"))
        expected = _mac(key, str(content_hash))
        if not hmac.compare_digest(expected, template.signature.signature_bytes):
            return Result.fail(SopTemplateTamperDetectedError("template signature mismatch"))
        return Result.ok(None)


def tamper_template_signature(template: SopTemplate) -> SopTemplate:
    if template.signature is None:
        raise ValueError("cannot tamper unsigned template signature")
    return replace(
        template,
        signature=replace(template.signature, signature_bytes=b"tampered"),
    )


def _mac(key: bytes, payload: str) -> bytes:
    return hmac.new(key, payload.encode(), hashlib.sha256).digest()


def _require_template_admin(admin: AdminPrincipal | DeveloperBootstrapPrincipal) -> None:
    if isinstance(admin, AdminPrincipal):
        return
    if isinstance(admin, DeveloperBootstrapPrincipal) and admin.has_bootstrap_authority:
        return
    raise PermissionError("SOP-template signing requires administrator or bootstrap authority")
