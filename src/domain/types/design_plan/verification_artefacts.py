"""
module_id: domain.types.design_plan.verification_artefacts
file: src/domain/types/design_plan/verification_artefacts.py
task_id: T-306

Non-operational verification artefact descriptors.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VerificationArtefact:
    name: str
    description: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("verification artefact name cannot be empty")
        if not self.description:
            raise ValueError("verification artefact description cannot be empty")
