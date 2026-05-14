"""
module_id: domain.types.design_plan.reviewer_packet
file: src/domain/types/design_plan/reviewer_packet.py
task_id: T-306

Reviewer-facing non-operational packet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewerPacket:
    summary: str
    evidence_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.summary:
            raise ValueError("reviewer packet summary cannot be empty")
        for evidence_hash in self.evidence_hashes:
            if not evidence_hash:
                raise ValueError("reviewer packet evidence hashes cannot be empty")
