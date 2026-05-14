"""
module_id: domain.security.authorisation_profile
file: src/domain/security/authorisation_profile.py
task_id: T-304

Unsigned drafts, signed authorisation profiles, and user declarations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import cast

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
    require_non_empty,
)
from domain.security.operational_role import OperationalRole
from domain.security.profile_signature import ProfileSignature
from domain.sequence import Sha256, sha256_text
from domain.types.enums import BiosafetyTier, ChassisClass, DownstreamUse
from domain.types.ids import AssemblyMethodId

CargoClass = str
VectorSystemClass = str
ReplicationCompetence = str
TargetOrganism = str
ScreeningExceptionClass = str
InstitutionalProtocolId = str
Jurisdiction = str
ComponentLineageTrust = str
AuthorisationConstraint = str
BlockReason = str


class InvalidProfileError(ValueError):
    """Raised when a signed profile does not match its canonical signed payload."""


@dataclass(frozen=True)
class CoveredBiologicalScope:
    covered_biosafety_tiers: frozenset[BiosafetyTier]
    covered_host_classes: frozenset[ChassisClass]
    covered_assembly_chemistries: frozenset[AssemblyMethodId]
    covered_downstream_uses: frozenset[DownstreamUse]
    covered_sop_libraries: frozenset[SopLibraryId]
    covered_vendor_submission: bool
    covered_export_classes: frozenset[ExportClass]
    role_of_operation_allowed: frozenset[OperationalRole]
    cargo_classes: frozenset[CargoClass] = frozenset()
    vector_system_classes: frozenset[VectorSystemClass] = frozenset()
    replication_competence: frozenset[ReplicationCompetence] = frozenset()
    insert_size_range_bp: tuple[int, int] | None = None
    target_organisms: frozenset[TargetOrganism] = frozenset()
    screening_exception_classes: frozenset[ScreeningExceptionClass] = frozenset()
    institutional_protocol_ids: frozenset[InstitutionalProtocolId] = frozenset()
    jurisdictions: frozenset[Jurisdiction] = frozenset()
    component_lineage_trust: frozenset[ComponentLineageTrust] = frozenset()

    def __post_init__(self) -> None:
        if not self.covered_biosafety_tiers:
            raise ValueError("covered_biosafety_tiers cannot be empty")
        if not self.covered_host_classes:
            raise ValueError("covered_host_classes cannot be empty")
        if not self.role_of_operation_allowed:
            raise ValueError("role_of_operation_allowed cannot be empty")
        if self.insert_size_range_bp is not None:
            lower, upper = self.insert_size_range_bp
            if lower < 0 or upper < lower:
                raise ValueError("insert_size_range_bp must be a non-negative inclusive range")

    def to_payload(self) -> dict[str, object]:
        return {
            "cargo_classes": sorted(self.cargo_classes),
            "component_lineage_trust": sorted(self.component_lineage_trust),
            "covered_assembly_chemistries": sorted(map(str, self.covered_assembly_chemistries)),
            "covered_biosafety_tiers": sorted(tier.value for tier in self.covered_biosafety_tiers),
            "covered_downstream_uses": sorted(use.value for use in self.covered_downstream_uses),
            "covered_export_classes": sorted(map(str, self.covered_export_classes)),
            "covered_host_classes": sorted(chassis.value for chassis in self.covered_host_classes),
            "covered_sop_libraries": sorted(map(str, self.covered_sop_libraries)),
            "covered_vendor_submission": self.covered_vendor_submission,
            "insert_size_range_bp": list(self.insert_size_range_bp)
            if self.insert_size_range_bp is not None
            else None,
            "institutional_protocol_ids": sorted(self.institutional_protocol_ids),
            "jurisdictions": sorted(self.jurisdictions),
            "replication_competence": sorted(self.replication_competence),
            "role_of_operation_allowed": sorted(
                role.value for role in self.role_of_operation_allowed
            ),
            "screening_exception_classes": sorted(self.screening_exception_classes),
            "target_organisms": sorted(self.target_organisms),
            "vector_system_classes": sorted(self.vector_system_classes),
        }


@dataclass(frozen=True)
class UnsignedAuthorisationProfileDraft:
    profile_id: AuthProfileId
    subject_user_id: UserId
    issued_by_admin_id: AdminId
    issuer_principal_id: PrincipalId
    institution: InstitutionId
    profile_version: int
    valid_from: datetime
    valid_until: datetime
    covered_scope: CoveredBiologicalScope
    additional_constraints: tuple[AuthorisationConstraint, ...] = ()
    revoked_at: datetime | None = None
    revocation_reason: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(str(self.profile_id), "profile_id")
        require_non_empty(str(self.subject_user_id), "subject_user_id")
        require_non_empty(str(self.issued_by_admin_id), "issued_by_admin_id")
        require_non_empty(str(self.issuer_principal_id), "issuer_principal_id")
        require_non_empty(str(self.institution), "institution")
        if self.profile_version < 1:
            raise ValueError("profile_version must be positive")
        _require_aware(self.valid_from, "valid_from")
        _require_aware(self.valid_until, "valid_until")
        if self.valid_until <= self.valid_from:
            raise ValueError("valid_until must be after valid_from")
        if self.revoked_at is not None:
            _require_aware(self.revoked_at, "revoked_at")
            require_non_empty(self.revocation_reason or "", "revocation_reason")
        for constraint in self.additional_constraints:
            require_non_empty(constraint, "authorisation constraint")

    def to_content_payload(self) -> dict[str, object]:
        return _content_payload(
            profile_id=self.profile_id,
            subject_user_id=self.subject_user_id,
            issued_by_admin_id=self.issued_by_admin_id,
            issuer_principal_id=self.issuer_principal_id,
            institution=self.institution,
            profile_version=self.profile_version,
            valid_from=self.valid_from,
            valid_until=self.valid_until,
            covered_scope=self.covered_scope,
            additional_constraints=self.additional_constraints,
            revoked_at=self.revoked_at,
            revocation_reason=self.revocation_reason,
        )

    def canonical_signed_payload(self) -> str:
        return _canonical_json(self.to_content_payload())

    def content_hash(self) -> Sha256:
        return sha256_text(self.canonical_signed_payload())


@dataclass(frozen=True)
class AuthorisationProfile:
    profile_id: AuthProfileId
    subject_user_id: UserId
    issued_by_admin_id: AdminId
    issuer_principal_id: PrincipalId
    institution: InstitutionId
    profile_version: int
    valid_from: datetime
    valid_until: datetime
    covered_scope: CoveredBiologicalScope
    profile_content_hash: Sha256
    profile_signature: ProfileSignature
    profile_signature_key_version: KeyVersionId
    additional_constraints: tuple[AuthorisationConstraint, ...] = ()
    revoked_at: datetime | None = None
    revocation_reason: str | None = None

    def __post_init__(self) -> None:
        expected_hash = sha256_text(self.canonical_signed_payload())
        if self.profile_content_hash != expected_hash:
            raise InvalidProfileError("profile_content_hash does not match canonical payload")
        if self.profile_signature.signed_payload_hash != expected_hash:
            raise InvalidProfileError("profile signature hash does not match canonical payload")
        if self.profile_signature.signing_key_version != self.profile_signature_key_version:
            raise InvalidProfileError("profile signature key version mismatch")

    @classmethod
    def from_draft(
        cls,
        draft: UnsignedAuthorisationProfileDraft,
        signature: ProfileSignature,
    ) -> AuthorisationProfile:
        return cls(
            profile_id=draft.profile_id,
            subject_user_id=draft.subject_user_id,
            issued_by_admin_id=draft.issued_by_admin_id,
            issuer_principal_id=draft.issuer_principal_id,
            institution=draft.institution,
            profile_version=draft.profile_version,
            valid_from=draft.valid_from,
            valid_until=draft.valid_until,
            covered_scope=draft.covered_scope,
            profile_content_hash=draft.content_hash(),
            profile_signature=signature,
            profile_signature_key_version=signature.signing_key_version,
            additional_constraints=draft.additional_constraints,
            revoked_at=draft.revoked_at,
            revocation_reason=draft.revocation_reason,
        )

    def to_content_payload(self) -> dict[str, object]:
        return _content_payload(
            profile_id=self.profile_id,
            subject_user_id=self.subject_user_id,
            issued_by_admin_id=self.issued_by_admin_id,
            issuer_principal_id=self.issuer_principal_id,
            institution=self.institution,
            profile_version=self.profile_version,
            valid_from=self.valid_from,
            valid_until=self.valid_until,
            covered_scope=self.covered_scope,
            additional_constraints=self.additional_constraints,
            revoked_at=self.revoked_at,
            revocation_reason=self.revocation_reason,
        )

    def canonical_signed_payload(self) -> str:
        return _canonical_json(self.to_content_payload())


@dataclass(frozen=True)
class AuthorisationDecision:
    allowed: bool
    blocked_by: tuple[BlockReason, ...]
    profile_id: AuthProfileId
    decision_at: datetime

    def __post_init__(self) -> None:
        require_non_empty(str(self.profile_id), "profile_id")
        _require_aware(self.decision_at, "decision_at")
        if self.allowed and self.blocked_by:
            raise ValueError("allowed authorisation decisions cannot include block reasons")
        if not self.allowed and not self.blocked_by:
            raise ValueError("blocked authorisation decisions require block reasons")


@dataclass(frozen=True)
class UserDeclaration:
    declared_at: datetime
    declared_by: UserId
    sop_library_id: SopLibraryId | None
    biosafety_approval_id: BiosafetyApprovalId | None
    role_of_operation: OperationalRole
    intended_export_class: ExportClass
    intended_vendor_submission: bool

    def __post_init__(self) -> None:
        _require_aware(self.declared_at, "declared_at")
        require_non_empty(str(self.declared_by), "declared_by")
        require_non_empty(str(self.intended_export_class), "intended_export_class")


def _content_payload(
    *,
    profile_id: AuthProfileId,
    subject_user_id: UserId,
    issued_by_admin_id: AdminId,
    issuer_principal_id: PrincipalId,
    institution: InstitutionId,
    profile_version: int,
    valid_from: datetime,
    valid_until: datetime,
    covered_scope: CoveredBiologicalScope,
    additional_constraints: tuple[AuthorisationConstraint, ...],
    revoked_at: datetime | None,
    revocation_reason: str | None,
) -> dict[str, object]:
    return {
        "additional_constraints": list(additional_constraints),
        "covered_scope": covered_scope.to_payload(),
        "institution": str(institution),
        "issued_by_admin_id": str(issued_by_admin_id),
        "issuer_principal_id": str(issuer_principal_id),
        "profile_id": str(profile_id),
        "profile_version": profile_version,
        "revocation_reason": revocation_reason,
        "revoked_at": None if revoked_at is None else _datetime_to_utc_iso(revoked_at),
        "subject_user_id": str(subject_user_id),
        "valid_from": _datetime_to_utc_iso(valid_from),
        "valid_until": _datetime_to_utc_iso(valid_until),
    }


def _canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(_json_ready(payload), sort_keys=True, separators=(",", ":"))


def _json_ready(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return _datetime_to_utc_iso(value)
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_json_ready(item) for item in value]
    if isinstance(value, frozenset | set):
        return sorted(cast(str, _json_ready(item)) for item in value)
    return value


def _datetime_to_utc_iso(value: datetime) -> str:
    _require_aware(value, "datetime")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")
