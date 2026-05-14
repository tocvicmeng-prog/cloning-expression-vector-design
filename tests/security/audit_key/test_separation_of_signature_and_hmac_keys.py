"""
module_id: tests.security.audit_key.test_separation_of_signature_and_hmac_keys
file: tests/security/audit_key/test_separation_of_signature_and_hmac_keys.py
task_id: T-312b
"""

from __future__ import annotations

from pathlib import Path

from adapter.security.audit_key import FileAuditKeyProvider, archive_contains_raw_key_accessor
from domain.ports.audit_key import KeyVersionId, MacBytes
from tests.fakes.security.profile_signing.fixtures import decision_record, reviewer_principal
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner
from tests.security.audit_key.helpers import deterministic_key_factory


def test_decision_record_signature_is_not_an_audit_hmac(tmp_path: Path) -> None:
    provider = FileAuditKeyProvider(
        tmp_path / "audit-key.json",
        key_factory=deterministic_key_factory(),
        emit_warning=False,
    )
    signed = FakeDecisionRecordSigner().sign(decision_record(), reviewer_principal())

    assert not archive_contains_raw_key_accessor(provider)
    assert not provider.verify(
        KeyVersionId(1),
        str(signed.signed_payload_hash).encode(),
        MacBytes(signed.signature_bytes),
    )
    assert provider.mac(b"decision-record")[1] != signed.signature_bytes
