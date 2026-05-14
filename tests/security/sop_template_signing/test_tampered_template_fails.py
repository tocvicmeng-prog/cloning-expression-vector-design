"""
module_id: tests.security.sop_template_signing.test_tampered_template_fails
file: tests/security/sop_template_signing/test_tampered_template_fails.py
task_id: T-316c
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateSigner,
    Ed25519InstitutionalSopTemplateVerifier,
)
from domain.types.signing_errors import SopTemplateTamperDetectedError
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template
from tests.fakes.sop_template.signer import tamper_template_signature


def test_tampered_sop_template_signature_fails(tmp_path: Path) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    verifier = Ed25519InstitutionalSopTemplateVerifier(archive)
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))

    assert isinstance(
        verifier.verify(tamper_template_signature(template)).error,
        SopTemplateTamperDetectedError,
    )
