"""
module_id: domain.types.risk_advisory.advisory
file: src/domain/types/risk_advisory/advisory.py
task_id: T-306

Risk advisory value object.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.types.citation import GradedCitation


class RiskAdvisorySeverity(Enum):
    INFO = "info"
    CAUTION = "caution"
    STRONG_CAUTION = "strong_caution"


@dataclass(frozen=True)
class RiskAdvisory:
    advisory_id: str
    severity: RiskAdvisorySeverity
    category: str
    message: str
    citation: GradedCitation

    def __post_init__(self) -> None:
        if not self.advisory_id:
            raise ValueError("advisory_id cannot be empty")
        if not self.category:
            raise ValueError("risk advisory category cannot be empty")
        if not self.message:
            raise ValueError("risk advisory message cannot be empty")
