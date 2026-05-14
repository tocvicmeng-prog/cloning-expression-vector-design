"""
module_id: domain.types.sop_protected.deviation
file: src/domain/types/sop_protected/deviation.py
task_id: T-306
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviationPolicy:
    allowed: bool
    escalation_contact: str | None = None

    def __post_init__(self) -> None:
        if not self.allowed and not self.escalation_contact:
            raise ValueError("disallowed deviations require escalation_contact")
