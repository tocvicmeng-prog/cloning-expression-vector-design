"""
module_id: tests.security.sop_template_signing.test_sign_then_verify
file: tests/security/sop_template_signing/test_sign_then_verify.py
task_id: T-316c
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapter.persistence import JsonlEventLog
from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateSigner,
    Ed25519InstitutionalSopTemplateVerifier,
)
from app.sop_template_key_management import SopTemplateKeyManagementService
from domain.events import (
    EventStream,
    SopTemplateSigningKeyDistributed,
    SopTemplateSigningKeyRevoked,
)
from tests.domain.ports.test_sop_template_contract import assert_sop_template_signing_contract
from tests.fakes.security.profile_signing.fixtures import reviewer_principal
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template
from tests.security.sop_template_signing.helpers import signed_decision_record


def test_ed25519_sop_template_signer_and_verifier_satisfy_contract(tmp_path: Path) -> None:
    archive = tmp_path / "sop-template-keys.json"
    assert_sop_template_signing_contract(
        Ed25519InstitutionalSopTemplateSigner(archive),
        Ed25519InstitutionalSopTemplateVerifier(archive),
    )


def test_sop_template_signer_rotates_and_verifies_historical_signatures(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    verifier = Ed25519InstitutionalSopTemplateVerifier(archive)
    first = signed_template(signer.sign(unsigned_template(), admin_principal()))

    second_version = signer.rotate("scheduled SOP-template key rotation", admin_principal())
    second = signed_template(signer.sign(unsigned_template(), admin_principal()))

    assert first.signature is not None
    assert second.signature is not None
    assert str(first.signature.signing_key_version) != str(second_version)
    assert second.signature.signing_key_version == second_version
    assert verifier.verify(first).success
    assert verifier.verify(second).success


def test_sop_template_key_management_emits_distribution_and_revocation_events(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "sop-template-keys.json"
    event_log = JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE)
    service = SopTemplateKeyManagementService(
        archive_path=archive,
        governance_event_log=event_log,
    )

    distributed = service.distribute_current_key(
        admin_principal(),
        reason="initial SOP-template signing-key distribution",
        signed_decision_record=signed_decision_record(),
    )
    revoked = service.revoke_key(
        admin_principal(),
        signing_key_version=distributed.signing_key_version,
        reason="retired by controlled rotation",
        signed_decision_record=signed_decision_record(),
    )

    events = event_log.read_events("inst")
    assert len(events) == 2
    assert isinstance(events[0], SopTemplateSigningKeyDistributed)
    assert isinstance(events[1], SopTemplateSigningKeyRevoked)
    assert events[0].signing_key_version == str(distributed.signing_key_version)
    assert events[0].public_key_fingerprint
    assert events[1].signing_key_version == str(revoked.signing_key_version)


def test_sop_template_key_management_requires_admin_and_reason(tmp_path: Path) -> None:
    service = SopTemplateKeyManagementService(
        archive_path=tmp_path / "sop-template-keys.json",
        governance_event_log=JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE),
    )

    with pytest.raises(ValueError, match="reason"):
        service.distribute_current_key(
            admin_principal(),
            reason=" ",
            signed_decision_record=signed_decision_record(),
        )
    with pytest.raises(PermissionError, match="administrator"):
        service.distribute_current_key(
            reviewer_principal(),
            reason="initial distribution",
            signed_decision_record=signed_decision_record(),
        )
