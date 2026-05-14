"""
module_id: domain.security.identifiers
file: src/domain/security/identifiers.py
task_id: T-304

Security identifier newtypes.
"""

from __future__ import annotations

from typing import NewType

PrincipalId = NewType("PrincipalId", str)
InstitutionId = NewType("InstitutionId", str)
UserId = NewType("UserId", str)
AdminId = NewType("AdminId", str)
AuthProfileId = NewType("AuthProfileId", str)
KeyVersionId = NewType("KeyVersionId", str)
ExportClass = NewType("ExportClass", str)
SopLibraryId = NewType("SopLibraryId", str)
BiosafetyApprovalId = NewType("BiosafetyApprovalId", str)


def require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
