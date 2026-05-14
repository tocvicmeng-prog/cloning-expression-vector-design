"""
module_id: tests.security.sop_template_signing.test_separation
file: tests/security/sop_template_signing/test_separation_of_identities.py
task_id: T-316c
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapter.security.decision_record_signing import PerPrincipalDecisionRecordSigner
from adapter.security.profile_signing import Ed25519InstitutionalProfileSigner
from adapter.security.signing_key_archive import SigningKeyArchiveError
from adapter.security.sop_template_signing import Ed25519InstitutionalSopTemplateSigner
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal as profile_admin_principal,
)
from tests.fakes.security.profile_signing.fixtures import (
    decision_record,
    reviewer_principal,
    signed_profile,
    unsigned_profile,
)
from tests.fakes.sop_template.fixtures import (
    admin_principal as sop_admin_principal,
)
from tests.fakes.sop_template.fixtures import signed_template, unsigned_template
from tests.security.sop_template_signing.helpers import provision_decision_record_key


def test_sop_template_profile_and_decision_record_keys_are_distinct_archives(
    tmp_path: Path,
) -> None:
    profile_archive = tmp_path / "profile-keys.json"
    decision_archive = tmp_path / "decision-keys.json"
    sop_archive = tmp_path / "sop-template-keys.json"

    profile_signer = Ed25519InstitutionalProfileSigner(profile_archive)
    profile = signed_profile(profile_signer.sign(unsigned_profile(), profile_admin_principal()))
    provision_decision_record_key(decision_archive, tmp_path)
    signed_decision = PerPrincipalDecisionRecordSigner(decision_archive).sign(
        decision_record(),
        reviewer_principal(),
    )
    sop_signer = Ed25519InstitutionalSopTemplateSigner(sop_archive)
    template = signed_template(sop_signer.sign(unsigned_template(), sop_admin_principal()))
    assert template.signature is not None

    assert str(profile.profile_signature_key_version).startswith("profile-ed25519")
    assert str(signed_decision.signing_key_version).startswith("decision-record")
    assert str(template.signature.signing_key_version).startswith("sop_template-ed25519")
    assert profile.profile_signature.signature_bytes != template.signature.signature_bytes
    assert signed_decision.signature_bytes != template.signature.signature_bytes
    assert _archive_purpose(profile_archive) == "profile"
    assert _archive_purpose(decision_archive) == "decision_record"
    assert _archive_purpose(sop_archive) == "sop_template"


def test_sop_template_signer_rejects_profile_or_decision_record_archives(
    tmp_path: Path,
) -> None:
    profile_archive = tmp_path / "profile-keys.json"
    decision_archive = tmp_path / "decision-keys.json"
    Ed25519InstitutionalProfileSigner(profile_archive)
    provision_decision_record_key(decision_archive, tmp_path)

    with pytest.raises(SigningKeyArchiveError, match="purpose"):
        Ed25519InstitutionalSopTemplateSigner(profile_archive)
    with pytest.raises(SigningKeyArchiveError, match="purpose"):
        Ed25519InstitutionalSopTemplateSigner(decision_archive)


def _archive_purpose(path: Path) -> str:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("archive must be a JSON object")
    purpose = raw["purpose"]
    if not isinstance(purpose, str):
        raise TypeError("purpose must be a string")
    return purpose
