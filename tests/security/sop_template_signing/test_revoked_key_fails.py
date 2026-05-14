"""
module_id: tests.security.sop_template_signing.test_revoked_key_fails
file: tests/security/sop_template_signing/test_revoked_key_fails.py
task_id: T-316c
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateSigner,
    Ed25519InstitutionalSopTemplateVerifier,
)
from domain.types.signing_errors import RevokedKeyError
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template


def test_revoked_sop_template_key_fails(tmp_path: Path) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    verifier = Ed25519InstitutionalSopTemplateVerifier(archive)
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))
    assert template.signature is not None

    verifier.revoke(template.signature.signing_key_version, "compromised")

    assert isinstance(verifier.verify(template).error, RevokedKeyError)
