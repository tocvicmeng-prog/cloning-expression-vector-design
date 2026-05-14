"""
module_id: tests.fakes.sop_template.test_fake_signer
file: tests/fakes/sop_template/test_fake_signer.py
task_id: T-316a
"""

from __future__ import annotations

from dataclasses import replace

from domain.security import KeyVersionId
from domain.types.signing_errors import (
    RevokedKeyError,
    SopTemplateTamperDetectedError,
    UnknownKeyVersionError,
)
from tests.fakes.sop_template.fixtures import (
    admin_principal,
    signed_template,
    unsigned_template,
)
from tests.fakes.sop_template.signer import (
    FakeSopTemplateSigner,
    FakeSopTemplateVerifier,
    tamper_template_signature,
)


def test_fake_sop_template_signer_and_verifier_round_trip() -> None:
    signer = FakeSopTemplateSigner()
    verifier = FakeSopTemplateVerifier()
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))

    assert verifier.verify(template).success


def test_fake_sop_template_verifier_detects_failure_modes() -> None:
    signer = FakeSopTemplateSigner()
    verifier = FakeSopTemplateVerifier()
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))

    assert isinstance(
        verifier.verify(tamper_template_signature(template)).error,
        SopTemplateTamperDetectedError,
    )
    assert isinstance(verifier.verify(unsigned_template()).error, SopTemplateTamperDetectedError)

    assert template.signature is not None
    unknown_signature = replace(
        template.signature,
        signing_key_version=KeyVersionId("unknown-sop-template-key"),
    )
    unknown = replace(template, signature=unknown_signature)
    assert isinstance(verifier.verify(unknown).error, UnknownKeyVersionError)

    verifier.revoke(KeyVersionId("sop-template-test-key-v1"))
    assert isinstance(verifier.verify(template).error, RevokedKeyError)
