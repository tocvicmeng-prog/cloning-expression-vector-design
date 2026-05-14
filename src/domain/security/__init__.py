"""
module_id: domain.security
file: src/domain/security/__init__.py
task_id: T-304

Security roles, principals, authorisation profile drafts, and signed profiles.
"""

from __future__ import annotations

from domain.security.authorisation_profile import (
    AuthorisationDecision,
    AuthorisationProfile,
    CoveredBiologicalScope,
    InvalidProfileError,
    UnsignedAuthorisationProfileDraft,
    UserDeclaration,
)
from domain.security.dual_control import DualControlFlags
from domain.security.identifiers import (
    AdminId,
    AuthProfileId,
    BiosafetyApprovalId,
    ExportClass,
    InstitutionId,
    KeyVersionId,
    PrincipalId,
    SopLibraryId,
    UserId,
)
from domain.security.operational_role import OperationalRole
from domain.security.principals import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    DeveloperPrincipal,
    Principal,
    ReviewerPrincipal,
    UserPrincipal,
)
from domain.security.profile_signature import ProfileSignature
from domain.security.roles import ROLE_INHERITS, SecurityRole
from domain.security.service_principals import ServiceName, ServicePrincipal

__all__ = [
    "ROLE_INHERITS",
    "AdminId",
    "AdminPrincipal",
    "AuthProfileId",
    "AuthorisationDecision",
    "AuthorisationProfile",
    "BiosafetyApprovalId",
    "CoveredBiologicalScope",
    "DeveloperBootstrapPrincipal",
    "DeveloperPrincipal",
    "DualControlFlags",
    "ExportClass",
    "InstitutionId",
    "InvalidProfileError",
    "KeyVersionId",
    "OperationalRole",
    "Principal",
    "PrincipalId",
    "ProfileSignature",
    "ReviewerPrincipal",
    "SecurityRole",
    "ServiceName",
    "ServicePrincipal",
    "SopLibraryId",
    "UnsignedAuthorisationProfileDraft",
    "UserDeclaration",
    "UserId",
    "UserPrincipal",
]
