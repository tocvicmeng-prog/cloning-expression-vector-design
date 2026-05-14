"""
module_id: domain.types.governance.decision_record
file: src/domain/types/governance/decision_record.py
task_id: T-306

Signed decision record value object.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.sequence import Sha256
from domain.types.governance.role_snapshot import RoleSnapshot


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    decision_type: str
    role_snapshot: RoleSnapshot
    profile_content_hash: Sha256
    policy_version: str
    signed_payload_hash: Sha256
    signature_bytes: bytes
    signed_at_utc: datetime

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id cannot be empty")
        if not self.decision_type:
            raise ValueError("decision_type cannot be empty")
        if not str(self.profile_content_hash):
            raise ValueError("profile_content_hash cannot be empty")
        if not self.policy_version:
            raise ValueError("policy_version cannot be empty")
        if not str(self.signed_payload_hash):
            raise ValueError("signed_payload_hash cannot be empty")
        if not self.signature_bytes:
            raise ValueError("decision record signature_bytes cannot be empty")
        if self.signed_at_utc.tzinfo is None:
            raise ValueError("signed_at_utc must be timezone-aware")
