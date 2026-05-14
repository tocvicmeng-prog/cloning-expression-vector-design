"""
module_id: tests.domain.ports.test_sop_template_contract
file: tests/domain/ports/test_sop_template_contract.py
task_id: T-316a
"""

from __future__ import annotations

from domain.ports.sop_template import SopTemplateSigner, SopTemplateVerifier
from domain.types.signing_errors import SopTemplateTamperDetectedError
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template
from tests.fakes.sop_template.signer import (
    FakeSopTemplateSigner,
    FakeSopTemplateVerifier,
    tamper_template_signature,
)


def assert_sop_template_signing_contract(
    signer: SopTemplateSigner,
    verifier: SopTemplateVerifier,
) -> None:
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))

    assert verifier.verify(template).success
    assert isinstance(
        verifier.verify(tamper_template_signature(template)).error,
        SopTemplateTamperDetectedError,
    )


def test_fake_sop_template_signer_and_verifier_satisfy_contract() -> None:
    assert_sop_template_signing_contract(FakeSopTemplateSigner(), FakeSopTemplateVerifier())
