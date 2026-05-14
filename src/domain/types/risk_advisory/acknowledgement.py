"""
module_id: domain.types.risk_advisory.acknowledgement
file: src/domain/types/risk_advisory/acknowledgement.py
task_id: T-306

Signed advisory acknowledgement value object.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.sequence import Sha256
from domain.types.governance import DecisionRecord
from domain.types.risk_advisory.decision import AdvisoryAcknowledgementDecision


@dataclass(frozen=True)
class RiskAdvisoryAcknowledgement:
    advisory_id: str
    report_content_hash: Sha256
    construct_checksum: Sha256
    decision: AdvisoryAcknowledgementDecision
    justification: str
    decision_record: DecisionRecord
    acknowledged_at_utc: datetime

    def __post_init__(self) -> None:
        if not self.advisory_id:
            raise ValueError("advisory_id cannot be empty")
        if not str(self.report_content_hash):
            raise ValueError("report_content_hash cannot be empty")
        if not str(self.construct_checksum):
            raise ValueError("construct_checksum cannot be empty")
        if (
            self.decision is AdvisoryAcknowledgementDecision.ACKNOWLEDGED
            and len(self.justification.strip()) < 20
        ):
            raise ValueError("acknowledgement justification must be at least 20 characters")
        if self.acknowledged_at_utc.tzinfo is None:
            raise ValueError("acknowledged_at_utc must be timezone-aware")
