"""
module_id: tests.security.sop_template_signing.test_wrong_key_version_fails
file: tests/security/sop_template_signing/test_wrong_key_version_fails.py
task_id: T-316c
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateSigner,
    Ed25519InstitutionalSopTemplateVerifier,
)
from domain.security import KeyVersionId
from domain.types.signing_errors import UnknownKeyVersionError
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template


def test_unknown_sop_template_key_version_fails(tmp_path: Path) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    verifier = Ed25519InstitutionalSopTemplateVerifier(archive)
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))
    assert template.signature is not None
    unknown = replace(
        template,
        signature=replace(
            template.signature,
            signing_key_version=KeyVersionId("unknown-sop-template-key"),
        ),
    )

    assert isinstance(verifier.verify(unknown).error, UnknownKeyVersionError)
