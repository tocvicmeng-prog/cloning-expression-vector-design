"""
module_id: tests.security.profile_signing.test_separation_of_profile_signing_from_audit_hmac
file: tests/security/profile_signing/test_separation_of_profile_signing_from_audit_hmac.py
task_id: T-314b
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.audit_key import FileAuditKeyProvider
from adapter.security.profile_signing import Ed25519InstitutionalProfileSigner
from domain.ports.audit_key import KeyVersionId as AuditKeyVersionId
from domain.ports.audit_key import MacBytes
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    signed_profile,
    unsigned_profile,
)
from tests.security.audit_key.helpers import deterministic_key_factory


def test_profile_signature_is_not_valid_audit_hmac(tmp_path: Path) -> None:
    signer = Ed25519InstitutionalProfileSigner(tmp_path / "profile-keys.json")
    profile = signed_profile(signer.sign(unsigned_profile(), admin_principal()))
    audit_provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )

    assert not audit_provider.verify(
        AuditKeyVersionId(1),
        str(profile.profile_content_hash).encode(),
        MacBytes(profile.profile_signature.signature_bytes),
    )
