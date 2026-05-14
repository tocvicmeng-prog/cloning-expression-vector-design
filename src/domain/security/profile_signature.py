"""
module_id: domain.security.profile_signature
file: src/domain/security/profile_signature.py
task_id: T-304

Profile signature value object.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.security.identifiers import KeyVersionId, require_non_empty
from domain.sequence import Sha256


@dataclass(frozen=True)
class ProfileSignature:
    signed_payload_hash: Sha256
    signature_bytes: bytes
    signing_key_version: KeyVersionId
    signed_at_utc: datetime

    def __post_init__(self) -> None:
        require_non_empty(str(self.signed_payload_hash), "signed_payload_hash")
        if not self.signature_bytes:
            raise ValueError("profile signature bytes cannot be empty")
        require_non_empty(str(self.signing_key_version), "signing_key_version")
        if self.signed_at_utc.tzinfo is None:
            raise ValueError("signed_at_utc must be timezone-aware")
