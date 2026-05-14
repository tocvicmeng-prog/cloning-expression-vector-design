"""
module_id: tests.domain.security
file: tests/domain/security/test_authorisation_profile.py
task_id: T-304
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from domain.security import (
    AdminId,
    AuthorisationDecision,
    AuthorisationProfile,
    AuthProfileId,
    CoveredBiologicalScope,
    ExportClass,
    InstitutionId,
    InvalidProfileError,
    KeyVersionId,
    OperationalRole,
    PrincipalId,
    ProfileSignature,
    SopLibraryId,
    UnsignedAuthorisationProfileDraft,
    UserDeclaration,
    UserId,
)
from domain.sequence import Sha256
from domain.types import AssemblyMethodId, BiosafetyTier, ChassisClass, DownstreamUse

NOW = datetime(2026, 5, 14, tzinfo=UTC)
LATER = datetime(2027, 5, 14, tzinfo=UTC)


def _scope() -> CoveredBiologicalScope:
    return CoveredBiologicalScope(
        covered_biosafety_tiers=frozenset({BiosafetyTier.BSL_1, BiosafetyTier.BSL_2}),
        covered_host_classes=frozenset({ChassisClass.BACTERIAL}),
        covered_assembly_chemistries=frozenset({AssemblyMethodId("golden-gate")}),
        covered_downstream_uses=frozenset({DownstreamUse.EXPRESSION}),
        covered_sop_libraries=frozenset({SopLibraryId("institutional-sop")}),
        covered_vendor_submission=False,
        covered_export_classes=frozenset({ExportClass("internal-review")}),
        role_of_operation_allowed=frozenset({OperationalRole.DESIGNER}),
        cargo_classes=frozenset({"enzyme"}),
        vector_system_classes=frozenset({"plasmid"}),
        insert_size_range_bp=(0, 5000),
        target_organisms=frozenset({"E. coli"}),
        jurisdictions=frozenset({"AU"}),
    )


def _draft() -> UnsignedAuthorisationProfileDraft:
    return UnsignedAuthorisationProfileDraft(
        profile_id=AuthProfileId("profile-1"),
        subject_user_id=UserId("user-1"),
        issued_by_admin_id=AdminId("admin-1"),
        issuer_principal_id=PrincipalId("principal-admin-1"),
        institution=InstitutionId("inst"),
        profile_version=1,
        valid_from=NOW,
        valid_until=LATER,
        covered_scope=_scope(),
        additional_constraints=("institutional review only",),
    )


def _signature(draft: UnsignedAuthorisationProfileDraft) -> ProfileSignature:
    return ProfileSignature(
        signed_payload_hash=draft.content_hash(),
        signature_bytes=b"signature",
        signing_key_version=KeyVersionId("profile-key-v1"),
        signed_at_utc=NOW,
    )


def test_signed_profile_round_trips_canonical_payload_from_unsigned_draft() -> None:
    draft = _draft()
    profile = AuthorisationProfile.from_draft(draft, _signature(draft))

    assert profile.profile_content_hash == draft.content_hash()
    assert profile.canonical_signed_payload() == draft.canonical_signed_payload()
    assert profile.canonical_signed_payload() == profile.canonical_signed_payload()


def test_signed_profile_rejects_mismatched_content_hash_and_signature_hash() -> None:
    draft = _draft()
    profile = AuthorisationProfile.from_draft(draft, _signature(draft))

    with pytest.raises(InvalidProfileError, match="profile_content_hash"):
        replace(
            profile,
            profile_content_hash=Sha256(profile.profile_signature.signed_payload_hash + "-bad"),
        )
    with pytest.raises(InvalidProfileError, match="signature hash"):
        AuthorisationProfile.from_draft(
            draft,
            replace(
                _signature(draft), signed_payload_hash=Sha256(profile.profile_content_hash + "-bad")
            ),
        )
    with pytest.raises(InvalidProfileError, match="key version"):
        replace(profile, profile_signature_key_version=KeyVersionId("other-key"))


def test_profile_signature_rejects_empty_signature_bytes() -> None:
    draft = _draft()

    with pytest.raises(ValueError, match="signature bytes"):
        ProfileSignature(
            signed_payload_hash=draft.content_hash(),
            signature_bytes=b"",
            signing_key_version=KeyVersionId("profile-key-v1"),
            signed_at_utc=NOW,
        )


def test_covered_scope_and_draft_validate_required_fields() -> None:
    with pytest.raises(ValueError, match="covered_biosafety_tiers"):
        replace(_scope(), covered_biosafety_tiers=frozenset())
    with pytest.raises(ValueError, match="insert_size_range"):
        replace(_scope(), insert_size_range_bp=(100, 10))
    with pytest.raises(ValueError, match="valid_until"):
        replace(_draft(), valid_until=NOW)
    with pytest.raises(ValueError, match="revocation_reason"):
        replace(_draft(), revoked_at=NOW)


def test_authorisation_decision_and_user_declaration_validate_invariants() -> None:
    assert AuthorisationDecision(
        allowed=True,
        blocked_by=(),
        profile_id=AuthProfileId("profile-1"),
        decision_at=NOW,
    )

    with pytest.raises(ValueError, match="block reasons"):
        AuthorisationDecision(
            allowed=False,
            blocked_by=(),
            profile_id=AuthProfileId("profile-1"),
            decision_at=NOW,
        )

    declaration = UserDeclaration(
        declared_at=NOW,
        declared_by=UserId("user-1"),
        sop_library_id=SopLibraryId("institutional-sop"),
        biosafety_approval_id=None,
        role_of_operation=OperationalRole.DESIGNER,
        intended_export_class=ExportClass("internal-review"),
        intended_vendor_submission=False,
    )

    assert declaration.role_of_operation is OperationalRole.DESIGNER
