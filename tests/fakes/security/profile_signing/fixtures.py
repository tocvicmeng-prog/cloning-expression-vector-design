"""
module_id: tests.fakes.security.profile_signing.fixtures
file: tests/fakes/security/profile_signing/fixtures.py
task_id: T-314a
"""

from __future__ import annotations

from datetime import UTC, datetime

from domain.security import (
    AdminId,
    AdminPrincipal,
    AuthorisationProfile,
    AuthProfileId,
    CoveredBiologicalScope,
    ExportClass,
    InstitutionId,
    KeyVersionId,
    OperationalRole,
    Principal,
    PrincipalId,
    ProfileSignature,
    SecurityRole,
    SopLibraryId,
    UnsignedAuthorisationProfileDraft,
    UserId,
)
from domain.sequence import Sha256
from domain.types import AssemblyMethodId, BiosafetyTier, ChassisClass, DownstreamUse
from domain.types.governance import DecisionRecord, RoleSnapshot

NOW = datetime(2026, 5, 14, tzinfo=UTC)
LATER = datetime(2027, 5, 14, tzinfo=UTC)


def admin_principal() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("principal-admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def reviewer_principal() -> Principal:
    return Principal(
        id=PrincipalId("reviewer-1"),
        role=SecurityRole.REVIEWER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def unsigned_profile_draft() -> UnsignedAuthorisationProfileDraft:
    return UnsignedAuthorisationProfileDraft(
        profile_id=AuthProfileId("profile-1"),
        subject_user_id=UserId("user-1"),
        issued_by_admin_id=AdminId("admin-1"),
        issuer_principal_id=PrincipalId("principal-admin-1"),
        institution=InstitutionId("inst"),
        profile_version=1,
        valid_from=NOW,
        valid_until=LATER,
        covered_scope=CoveredBiologicalScope(
            covered_biosafety_tiers=frozenset({BiosafetyTier.BSL_1}),
            covered_host_classes=frozenset({ChassisClass.BACTERIAL}),
            covered_assembly_chemistries=frozenset({AssemblyMethodId("golden-gate")}),
            covered_downstream_uses=frozenset({DownstreamUse.EXPRESSION}),
            covered_sop_libraries=frozenset({SopLibraryId("institutional-sop")}),
            covered_vendor_submission=False,
            covered_export_classes=frozenset({ExportClass("internal-review")}),
            role_of_operation_allowed=frozenset({OperationalRole.DESIGNER}),
        ),
    )


def unsigned_profile() -> AuthorisationProfile:
    draft = unsigned_profile_draft()
    return AuthorisationProfile.from_draft(
        draft,
        ProfileSignature(
            signed_payload_hash=draft.content_hash(),
            signature_bytes=b"placeholder-signature",
            signing_key_version=KeyVersionId("profile-test-key-v1"),
            signed_at_utc=NOW,
        ),
    )


def signed_profile(signature: ProfileSignature) -> AuthorisationProfile:
    return AuthorisationProfile.from_draft(unsigned_profile_draft(), signature)


def decision_record() -> DecisionRecord:
    principal = reviewer_principal()
    snapshot = RoleSnapshot(
        principal_id=principal.id,
        role=principal.role,
        institution_id=str(principal.institution),
        captured_at_utc=NOW,
        credentials_verified_at_utc=principal.credentials_verified_at,
    )
    return DecisionRecord(
        decision_id="decision-1",
        decision_type="reviewer_signoff",
        role_snapshot=snapshot,
        profile_content_hash=unsigned_profile_draft().content_hash(),
        policy_version="policy-v1",
        signed_payload_hash=Sha256("sha256:payload-placeholder"),
        signature_bytes=b"placeholder",
        signed_at_utc=NOW,
    )
