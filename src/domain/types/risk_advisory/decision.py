"""
module_id: domain.types.risk_advisory.decision
file: src/domain/types/risk_advisory/decision.py
task_id: T-306
"""

from __future__ import annotations

from enum import Enum


class AdvisoryAcknowledgementDecision(Enum):
    ACKNOWLEDGED = "acknowledged"
    DECLINED = "declined"
    ESCALATED = "escalated"
