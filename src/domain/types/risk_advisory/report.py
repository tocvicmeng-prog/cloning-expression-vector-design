"""
module_id: domain.types.risk_advisory.report
file: src/domain/types/risk_advisory/report.py
task_id: T-306

Risk advisory report bound to a design session and construct checksum.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.sequence import Sha256
from domain.types.risk_advisory.advisory import RiskAdvisory, RiskAdvisorySeverity


@dataclass(frozen=True)
class RiskAdvisoryReport:
    design_session_id: str
    construct_id: str
    construct_checksum: Sha256
    construct_version: str
    report_content_hash: Sha256
    advisory_catalogue_version: str
    advisory_catalogue_content_hash: Sha256
    advisories: tuple[RiskAdvisory, ...]

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise ValueError("design_session_id cannot be empty")
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not str(self.construct_checksum):
            raise ValueError("construct_checksum cannot be empty")
        if not self.construct_version:
            raise ValueError("construct_version cannot be empty")
        if not str(self.report_content_hash):
            raise ValueError("report_content_hash cannot be empty")

    def required_acknowledgements(self) -> frozenset[str]:
        return frozenset(
            advisory.advisory_id
            for advisory in self.advisories
            if advisory.severity
            in {RiskAdvisorySeverity.CAUTION, RiskAdvisorySeverity.STRONG_CAUTION}
        )
