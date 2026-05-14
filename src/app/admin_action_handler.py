"""
module_id: app.admin_action_handler
file: src/app/admin_action_handler.py
task_id: T-311

Administrator-only authorisation profile write service.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import TypedDict

from adapter.persistence import JsonlEventLog, SqliteAuthorisationStoreWrite
from domain.events import (
    AdminActionMinted,
    AdminActionModified,
    AdminActionRevoked,
    AdminBootstrapped,
    AuthorisationAttemptDenied,
    CanonicalPayload,
    SopTemplateMinted,
    SopTemplateModified,
    SopTemplateRevoked,
)
from domain.ports.audit_append import AdminAuditAppendPort, AuditEntry
from domain.ports.profile_signing import AuthorisationProfileSigner
from domain.ports.sop_template import SopTemplateAdminWritePort, SopTemplateSigner
from domain.security import (
    AdminPrincipal,
    AuthorisationProfile,
    DeveloperBootstrapPrincipal,
    DualControlFlags,
    KeyVersionId,
    Principal,
    ProfileSignature,
    SecurityRole,
    UnsignedAuthorisationProfileDraft,
)
from domain.types.derivation import SopTemplateId
from domain.types.sop_template import SopTemplate, SopTemplateRevocation, SopTemplateVersion


class _GovernanceEventBase(TypedDict):
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    institution_id: str


@dataclass(frozen=True)
class AdminActionResult:
    profile: AuthorisationProfile
    audit_entry_id: str
    governance_event_id: str


@dataclass(frozen=True)
class SopTemplateWriteResult:
    template: SopTemplate
    template_version: SopTemplateVersion
    audit_entry_id: str
    governance_event_id: str


@dataclass(frozen=True)
class SopTemplateRevokeResult:
    revocation: SopTemplateRevocation
    audit_entry_id: str
    governance_event_id: str


class AdminActionHandler:
    def __init__(
        self,
        *,
        authorisation_store: SqliteAuthorisationStoreWrite,
        profile_signer: AuthorisationProfileSigner,
        audit_append: AdminAuditAppendPort,
        governance_event_log: JsonlEventLog,
        sop_template_store: SopTemplateAdminWritePort | None = None,
        sop_template_signer: SopTemplateSigner | None = None,
        dual_control_flags: DualControlFlags | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._authorisation_store = authorisation_store
        self._profile_signer = profile_signer
        self._audit_append = audit_append
        self._governance_event_log = governance_event_log
        self._sop_template_store = sop_template_store
        self._sop_template_signer = sop_template_signer
        self._dual_control_flags = dual_control_flags or DualControlFlags()
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_sequence = 0

    def mint_profile(
        self,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal | Principal,
        draft: UnsignedAuthorisationProfileDraft,
        *,
        justification: str,
    ) -> AdminActionResult:
        if isinstance(principal, DeveloperBootstrapPrincipal):
            return self.bootstrap_initial_admin(principal, draft, justification=justification)
        admin = self._require_admin(principal, "mint_profile")
        profile = self._sign_profile(draft, admin)
        profile_id = self._authorisation_store.write_mint(profile, admin)
        return self._record_profile_event(
            event_type="AdminActionMinted",
            principal=admin,
            profile=profile,
            target_user_id=str(draft.subject_user_id),
            justification=justification,
            store_id=profile_id,
        )

    def modify_profile(
        self,
        principal: Principal,
        draft: UnsignedAuthorisationProfileDraft,
        *,
        justification: str,
    ) -> AdminActionResult:
        admin = self._require_admin(principal, "modify_profile")
        profile = self._sign_profile(draft, admin)
        profile_id = self._authorisation_store.write_modify(profile, admin)
        return self._record_profile_event(
            event_type="AdminActionModified",
            principal=admin,
            profile=profile,
            target_user_id=str(draft.subject_user_id),
            justification=justification,
            store_id=profile_id,
        )

    def revoke_profile(
        self,
        principal: Principal,
        profile_id: str,
        *,
        reason: str,
    ) -> AdminActionResult:
        admin = self._require_admin(principal, "revoke_profile")
        current = self._authorisation_store.get_profile(profile_id)
        if (
            self._dual_control_flags.require_two_admins_for_profile_revocation
            and admin.id == current.issuer_principal_id
        ):
            self._record_denial(admin, "revoke_profile", "dual-control-violation")
            raise PermissionError(
                "DualControlViolation: profile revocation requires a distinct administrator"
            )
        draft = UnsignedAuthorisationProfileDraft(
            profile_id=current.profile_id,
            subject_user_id=current.subject_user_id,
            issued_by_admin_id=current.issued_by_admin_id,
            issuer_principal_id=current.issuer_principal_id,
            institution=current.institution,
            profile_version=current.profile_version + 1,
            valid_from=current.valid_from,
            valid_until=current.valid_until,
            covered_scope=current.covered_scope,
            additional_constraints=current.additional_constraints,
            revoked_at=self._clock(),
            revocation_reason=reason,
        )
        profile = self._sign_profile(draft, admin)
        stored_id = self._authorisation_store.write_revoke(profile, admin)
        return self._record_profile_event(
            event_type="AdminActionRevoked",
            principal=admin,
            profile=profile,
            target_user_id=str(profile.subject_user_id),
            justification=reason,
            store_id=stored_id,
        )

    def bootstrap_initial_admin(
        self,
        developer: DeveloperBootstrapPrincipal,
        draft: UnsignedAuthorisationProfileDraft,
        *,
        justification: str,
    ) -> AdminActionResult:
        if not developer.has_bootstrap_authority:
            raise PermissionError("bootstrap requires active DeveloperBootstrapPrincipal")
        profile = self._sign_profile(draft, developer)
        profile_id = self._authorisation_store.bootstrap_initial_admin(developer, profile)
        return self._record_profile_event(
            event_type="AdminBootstrapped",
            principal=developer,
            profile=profile,
            target_user_id=str(draft.subject_user_id),
            justification=justification,
            store_id=profile_id,
        )

    def list_profiles(self, principal: Principal) -> tuple[AuthorisationProfile, ...]:
        self._require_admin(principal, "list_profiles")
        return self._authorisation_store.list_profiles()

    def view_audit_trail(self, principal: Principal) -> tuple[Mapping[str, object], ...]:
        self._require_admin(principal, "view_audit_trail")
        rows = getattr(self._audit_append, "rows", ())
        return tuple(row.entry.payload for row in rows)

    def mint_sop_template(
        self,
        principal: Principal,
        template: SopTemplate,
        *,
        justification: str,
    ) -> SopTemplateWriteResult:
        admin = self._require_sop_template_admin(principal, "mint_sop_template")
        signed = self._sign_sop_template(template, admin)
        version = self._require_sop_template_store().write_mint(signed, admin)
        return self._record_sop_template_write_event(
            event_type="SopTemplateMinted",
            principal=admin,
            template=signed,
            version=version,
            justification=justification,
        )

    def modify_sop_template(
        self,
        principal: Principal,
        template: SopTemplate,
        *,
        justification: str,
    ) -> SopTemplateWriteResult:
        admin = self._require_sop_template_admin(principal, "modify_sop_template")
        signed = self._sign_sop_template(template, admin)
        version = self._require_sop_template_store().write_modify(signed, admin)
        return self._record_sop_template_write_event(
            event_type="SopTemplateModified",
            principal=admin,
            template=signed,
            version=version,
            justification=justification,
        )

    def revoke_sop_template(
        self,
        principal: Principal,
        template_id: SopTemplateId,
        *,
        reason: str,
    ) -> SopTemplateRevokeResult:
        admin = self._require_sop_template_admin(principal, "revoke_sop_template")
        revocation = self._require_sop_template_store().write_revoke(
            template_id,
            reason,
            admin,
        )
        return self._record_sop_template_revocation_event(
            principal=admin,
            revocation=revocation,
        )

    def _record_profile_event(
        self,
        *,
        event_type: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
        profile: AuthorisationProfile,
        target_user_id: str,
        justification: str,
        store_id: str,
    ) -> AdminActionResult:
        occurred_at = self._clock()
        audit_entry_id = self._audit_append.append(
            AuditEntry(
                entry_type=event_type,
                payload={
                    "profile_id": str(profile.profile_id),
                    "profile_content_hash": str(profile.profile_content_hash),
                    "store_id": store_id,
                    "target_user_id": target_user_id,
                },
                occurred_at_utc=occurred_at,
            ),
            principal,
        )
        governance_event_id = self._append_governance_event(
            event_type=event_type,
            principal=principal,
            profile=profile,
            target_user_id=target_user_id,
            justification=justification,
            occurred_at=occurred_at,
        )
        return AdminActionResult(
            profile=profile,
            audit_entry_id=str(audit_entry_id),
            governance_event_id=governance_event_id,
        )

    def _append_governance_event(
        self,
        *,
        event_type: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
        profile: AuthorisationProfile,
        target_user_id: str,
        justification: str,
        occurred_at: datetime,
    ) -> str:
        event_id = self._next_event_id(event_type)
        common: _GovernanceEventBase = {
            "event_id": event_id,
            "occurred_at_utc": occurred_at,
            "actor_id": str(principal.id),
            "institution_id": str(principal.institution),
        }
        event: AdminActionMinted | AdminActionModified | AdminActionRevoked | AdminBootstrapped
        if event_type == "AdminActionMinted":
            event = AdminActionMinted(
                **common,
                target_user_id=target_user_id,
                profile_payload=_profile_payload(profile),
                profile_content_hash=str(profile.profile_content_hash),
                justification=justification,
            )
        elif event_type == "AdminActionModified":
            event = AdminActionModified(
                **common,
                target_user_id=target_user_id,
                diff_payload=_profile_payload(profile),
                profile_content_hash=str(profile.profile_content_hash),
                justification=justification,
            )
        elif event_type == "AdminActionRevoked":
            event = AdminActionRevoked(
                **common,
                target_user_id=target_user_id,
                profile_id=str(profile.profile_id),
                reason=justification,
            )
        else:
            event = AdminBootstrapped(
                **common,
                admin_principal_id=str(profile.issuer_principal_id),
            )
        return self._governance_event_log.append_event(str(principal.institution), event)

    def _record_sop_template_write_event(
        self,
        *,
        event_type: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
        template: SopTemplate,
        version: SopTemplateVersion,
        justification: str,
    ) -> SopTemplateWriteResult:
        occurred_at = self._clock()
        audit_entry_id = self._audit_append.append(
            AuditEntry(
                entry_type=event_type,
                payload={
                    "template_id": str(template.template_id),
                    "template_payload_hash": str(version.content_hash),
                    "template_version": str(template.version),
                },
                occurred_at_utc=occurred_at,
            ),
            principal,
        )
        event_id = self._next_event_id(event_type)
        common: _GovernanceEventBase = {
            "event_id": event_id,
            "occurred_at_utc": occurred_at,
            "actor_id": str(principal.id),
            "institution_id": str(principal.institution),
        }
        event: SopTemplateMinted | SopTemplateModified
        if event_type == "SopTemplateMinted":
            event = SopTemplateMinted(
                **common,
                template_id=str(template.template_id),
                template_payload_hash=str(version.content_hash),
                signed_template_payload=_sop_template_payload(template),
            )
        else:
            event = SopTemplateModified(
                **common,
                template_id=str(template.template_id),
                template_payload_hash=str(version.content_hash),
                signed_template_payload=_sop_template_payload(template),
            )
        governance_event_id = self._governance_event_log.append_event(
            str(principal.institution),
            event,
        )
        return SopTemplateWriteResult(
            template=template,
            template_version=version,
            audit_entry_id=str(audit_entry_id),
            governance_event_id=governance_event_id,
        )

    def _record_sop_template_revocation_event(
        self,
        *,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
        revocation: SopTemplateRevocation,
    ) -> SopTemplateRevokeResult:
        occurred_at = self._clock()
        audit_entry_id = self._audit_append.append(
            AuditEntry(
                entry_type="SopTemplateRevoked",
                payload={
                    "reason": revocation.reason,
                    "template_id": str(revocation.template_id),
                    "template_version": str(revocation.version),
                },
                occurred_at_utc=occurred_at,
            ),
            principal,
        )
        event = SopTemplateRevoked(
            event_id=self._next_event_id("SopTemplateRevoked"),
            occurred_at_utc=occurred_at,
            actor_id=str(principal.id),
            institution_id=str(principal.institution),
            template_id=str(revocation.template_id),
            reason=revocation.reason,
            revocation_payload=_sop_template_revocation_payload(revocation),
        )
        governance_event_id = self._governance_event_log.append_event(
            str(principal.institution),
            event,
        )
        return SopTemplateRevokeResult(
            revocation=revocation,
            audit_entry_id=str(audit_entry_id),
            governance_event_id=governance_event_id,
        )

    def _sign_profile(
        self,
        draft: UnsignedAuthorisationProfileDraft,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> AuthorisationProfile:
        placeholder = AuthorisationProfile.from_draft(
            draft,
            ProfileSignature(
                signed_payload_hash=draft.content_hash(),
                signature_bytes=b"unsigned-profile-draft",
                signing_key_version=KeyVersionId("unsigned-draft"),
                signed_at_utc=draft.valid_from,
            ),
        )
        signature = self._profile_signer.sign(placeholder, principal)
        return AuthorisationProfile.from_draft(draft, signature)

    def _sign_sop_template(
        self,
        template: SopTemplate,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplate:
        unsigned = replace(template, signature=None)
        signature = self._require_sop_template_signer().sign(unsigned, principal)
        return replace(unsigned, signature=signature)

    def _require_sop_template_store(self) -> SopTemplateAdminWritePort:
        if self._sop_template_store is None:
            raise RuntimeError("SOP-template store is not configured")
        return self._sop_template_store

    def _require_sop_template_signer(self) -> SopTemplateSigner:
        if self._sop_template_signer is None:
            raise RuntimeError("SOP-template signer is not configured")
        return self._sop_template_signer

    def _require_admin(self, principal: Principal, operation: str) -> AdminPrincipal:
        if isinstance(principal, AdminPrincipal) and principal.can_act_as(
            SecurityRole.ADMINISTRATOR
        ):
            return principal
        self._record_denial(principal, operation)
        raise PermissionError(f"{operation} requires administrator")

    def _require_sop_template_admin(
        self,
        principal: Principal,
        operation: str,
    ) -> AdminPrincipal | DeveloperBootstrapPrincipal:
        if isinstance(principal, AdminPrincipal) and principal.can_act_as(
            SecurityRole.ADMINISTRATOR
        ):
            return principal
        if isinstance(principal, DeveloperBootstrapPrincipal) and principal.has_bootstrap_authority:
            return principal
        self._record_denial(principal, operation)
        raise PermissionError(f"{operation} requires administrator or bootstrap authority")

    def _record_denial(
        self,
        principal: Principal,
        operation: str,
        reason: str = "administrator-required",
    ) -> None:
        event = AuthorisationAttemptDenied(
            event_id=self._next_event_id("AuthorisationAttemptDenied"),
            occurred_at_utc=self._clock(),
            actor_id=str(principal.id),
            institution_id=str(principal.institution),
            subject_user_id=str(principal.id),
            missing_or_failed_reasons=(f"{operation}:{reason}",),
        )
        self._governance_event_log.append_event(str(principal.institution), event)

    def _next_event_id(self, prefix: str) -> str:
        self._event_sequence += 1
        return f"{prefix}-{self._event_sequence:06d}"


def _profile_payload(profile: AuthorisationProfile) -> CanonicalPayload:
    return (
        ("profile_id", str(profile.profile_id)),
        ("subject_user_id", str(profile.subject_user_id)),
        ("profile_content_hash", str(profile.profile_content_hash)),
        ("profile_signature_key_version", str(profile.profile_signature_key_version)),
    )


def _sop_template_payload(template: SopTemplate) -> CanonicalPayload:
    if template.signature is None:
        raise ValueError("signed SOP template payload requires a signature")
    return (
        ("template_id", str(template.template_id)),
        ("version", str(template.version)),
        ("template_content_hash", str(template.signature.template_content_hash)),
        ("signing_key_version", str(template.signature.signing_key_version)),
        ("signed_at_utc", template.signature.signed_at_utc.astimezone(UTC).isoformat()),
        ("signature_bytes_hex", template.signature.signature_bytes.hex()),
    )


def _sop_template_revocation_payload(revocation: SopTemplateRevocation) -> CanonicalPayload:
    return (
        ("template_id", str(revocation.template_id)),
        ("version", str(revocation.version)),
        ("revoked_by_principal_id", str(revocation.revoked_by_principal_id)),
        ("revoked_at_utc", revocation.revoked_at_utc.astimezone(UTC).isoformat()),
        ("reason", revocation.reason),
    )
