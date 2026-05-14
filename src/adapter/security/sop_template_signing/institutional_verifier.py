"""
module_id: adapter.security.sop_template_signing.institutional_verifier
file: src/adapter/security/sop_template_signing/institutional_verifier.py
task_id: T-316c

Ed25519 institutional SOP-template verifier.
"""

from __future__ import annotations

from pathlib import Path

from cryptography.exceptions import InvalidSignature

from adapter.security.signing_key_archive import SigningKeyArchiveError, SigningKeyArchiveStore
from adapter.security.sop_template_signing.institutional_signer import (
    _sop_template_signature_payload,
)
from domain.security.identifiers import KeyVersionId
from domain.types.signing_errors import (
    Result,
    RevokedKeyError,
    SopTemplateTamperDetectedError,
    SopTemplateVerificationResult,
    UnknownKeyVersionError,
)
from domain.types.sop_template import SopTemplate


class Ed25519InstitutionalSopTemplateVerifier:
    def __init__(self, archive_path: str | Path) -> None:
        self._store = SigningKeyArchiveStore(
            archive_path,
            purpose="sop_template",
            create_if_missing=False,
        )

    def verify(self, template: SopTemplate) -> SopTemplateVerificationResult:
        if template.signature is None:
            return Result.fail(SopTemplateTamperDetectedError("template is unsigned"))
        key_version = template.signature.signing_key_version
        try:
            record = self._store.record(key_version)
        except SigningKeyArchiveError:
            return Result.fail(UnknownKeyVersionError(str(key_version)))
        if record.revoked:
            return Result.fail(RevokedKeyError(str(key_version)))
        if record.principal_id is not None:
            return Result.fail(SopTemplateTamperDetectedError("template key is not institutional"))
        content_hash = template.content_hash()
        if template.signature.template_content_hash != content_hash:
            return Result.fail(SopTemplateTamperDetectedError("template content hash mismatch"))
        try:
            record.public_key().verify(
                template.signature.signature_bytes,
                _sop_template_signature_payload(template),
            )
        except InvalidSignature:
            return Result.fail(SopTemplateTamperDetectedError("template signature mismatch"))
        return Result.ok(None)

    def revoke(self, key_version: KeyVersionId, reason: str = "revoked by verifier") -> None:
        self._store.revoke_key(key_version, reason)
