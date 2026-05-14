"""
module_id: domain.ports.decision_record_signing
file: src/domain/ports/decision_record_signing.py
task_id: T-314a

Decision-record signing Protocols.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from domain.security import KeyVersionId, Principal, PrincipalId
from domain.sequence import Sha256
from domain.types.governance import DecisionRecord
from domain.types.signing_errors import DecisionRecordVerificationResult


@dataclass(frozen=True)
class SignedDecisionRecord:
    decision: DecisionRecord
    signing_principal_id: PrincipalId
    signing_key_version: KeyVersionId
    signed_payload_hash: Sha256
    signature_bytes: bytes

    def __post_init__(self) -> None:
        if not str(self.signing_principal_id):
            raise ValueError("signing_principal_id cannot be empty")
        if not str(self.signing_key_version):
            raise ValueError("signing_key_version cannot be empty")
        if not str(self.signed_payload_hash):
            raise ValueError("signed_payload_hash cannot be empty")
        if not self.signature_bytes:
            raise ValueError("signature_bytes cannot be empty")


@runtime_checkable
class DecisionRecordSigner(Protocol):
    def sign(self, decision: DecisionRecord, principal: Principal) -> SignedDecisionRecord: ...


@runtime_checkable
class DecisionRecordVerifier(Protocol):
    def verify(self, signed: SignedDecisionRecord) -> DecisionRecordVerificationResult: ...
