"""
module_id: domain.events.governance
file: src/domain/events/governance.py
task_id: T-305

Governance-stream event subclasses.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.events.base import CanonicalPayload, GovernanceEvent, register_event_type


@register_event_type
@dataclass(frozen=True)
class AdminBootstrapped(GovernanceEvent):
    event_type = "AdminBootstrapped"
    admin_principal_id: str


@register_event_type
@dataclass(frozen=True)
class AdminActionMinted(GovernanceEvent):
    event_type = "AdminActionMinted"
    target_user_id: str
    profile_payload: CanonicalPayload
    profile_content_hash: str
    justification: str


@register_event_type
@dataclass(frozen=True)
class AdminActionModified(GovernanceEvent):
    event_type = "AdminActionModified"
    target_user_id: str
    diff_payload: CanonicalPayload
    profile_content_hash: str
    justification: str


@register_event_type
@dataclass(frozen=True)
class AdminActionRevoked(GovernanceEvent):
    event_type = "AdminActionRevoked"
    target_user_id: str
    profile_id: str
    reason: str


@register_event_type
@dataclass(frozen=True)
class InstitutionalPolicyUpdated(GovernanceEvent):
    event_type = "InstitutionalPolicyUpdated"
    policy_version: str
    policy_hash: str


@register_event_type
@dataclass(frozen=True)
class ReviewerSignedOff(GovernanceEvent):
    event_type = "ReviewerSignedOff"
    decision_record_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class AuthorisationAttemptDenied(GovernanceEvent):
    event_type = "AuthorisationAttemptDenied"
    subject_user_id: str
    missing_or_failed_reasons: tuple[str, ...]


@register_event_type
@dataclass(frozen=True)
class AuthorisationExtensionRequested(GovernanceEvent):
    event_type = "AuthorisationExtensionRequested"
    item_id: str
    request_payload: CanonicalPayload
    request_content_hash: str


@register_event_type
@dataclass(frozen=True)
class ReviewQueueItemCreated(GovernanceEvent):
    event_type = "ReviewQueueItemCreated"
    item_id: str
    request_kind: str
    request_payload: CanonicalPayload
    request_content_hash: str


@register_event_type
@dataclass(frozen=True)
class ReviewQueueItemAssigned(GovernanceEvent):
    event_type = "ReviewQueueItemAssigned"
    item_id: str
    assigned_admin_id: str
    decision_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class ReviewQueueItemResolved(GovernanceEvent):
    event_type = "ReviewQueueItemResolved"
    item_id: str
    decision_status: str
    decision_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class PluginManifestApproved(GovernanceEvent):
    event_type = "PluginManifestApproved"
    plugin_id: str
    manifest_hash: str


@register_event_type
@dataclass(frozen=True)
class PluginManifestRejected(GovernanceEvent):
    event_type = "PluginManifestRejected"
    plugin_id: str
    reason: str


@register_event_type
@dataclass(frozen=True)
class AdvisoryWarningPresented(GovernanceEvent):
    event_type = "AdvisoryWarningPresented"
    design_session_id: str
    construct_id: str
    construct_version: str
    report_content_hash: str
    advisory_ids: tuple[str, ...]
    presenting_surface: str
    recipient_principal_id: str
    recipient_role: str


@register_event_type
@dataclass(frozen=True)
class RiskAdvisoryAcknowledged(GovernanceEvent):
    event_type = "RiskAdvisoryAcknowledged"
    acknowledgement_payload: CanonicalPayload
    acknowledgement_content_hash: str


@register_event_type
@dataclass(frozen=True)
class RiskAdvisoryDeclined(GovernanceEvent):
    event_type = "RiskAdvisoryDeclined"
    decline_payload: CanonicalPayload
    decline_content_hash: str


@register_event_type
@dataclass(frozen=True)
class RiskAdvisoryEscalated(GovernanceEvent):
    event_type = "RiskAdvisoryEscalated"
    escalation_payload: CanonicalPayload
    escalation_content_hash: str


@register_event_type
@dataclass(frozen=True)
class UnsupportedBiosafetyTierAttempted(GovernanceEvent):
    event_type = "UnsupportedBiosafetyTierAttempted"
    construct_id: str
    requested_tier: str


@register_event_type
@dataclass(frozen=True)
class AuditKeyRotated(GovernanceEvent):
    event_type = "AuditKeyRotated"
    key_version_before: str
    key_version_after: str
    rotation_reason: str
    decision_record_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class GatePredicateVersionBumped(GovernanceEvent):
    event_type = "GatePredicateVersionBumped"
    gate_name: str
    old_predicate_version: str
    new_predicate_version: str
    predicate_content_hash: str
    decision_record_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class DecisionRecordPublicKeyDistributed(GovernanceEvent):
    event_type = "DecisionRecordPublicKeyDistributed"
    principal_id: str
    signing_key_version: str
    public_key_fingerprint: str
    reason: str
    decision_record_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class DecisionRecordPrincipalKeyRevoked(GovernanceEvent):
    event_type = "DecisionRecordPrincipalKeyRevoked"
    principal_id: str
    signing_key_version: str
    reason: str
    decision_record_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class SopTemplateSigningKeyDistributed(GovernanceEvent):
    event_type = "SopTemplateSigningKeyDistributed"
    signing_key_version: str
    public_key_fingerprint: str
    reason: str
    decision_record_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class SopTemplateSigningKeyRevoked(GovernanceEvent):
    event_type = "SopTemplateSigningKeyRevoked"
    signing_key_version: str
    reason: str
    decision_record_payload: CanonicalPayload
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class SopTemplateMinted(GovernanceEvent):
    event_type = "SopTemplateMinted"
    template_id: str
    template_payload_hash: str
    signed_template_payload: CanonicalPayload


@register_event_type
@dataclass(frozen=True)
class SopTemplateModified(GovernanceEvent):
    event_type = "SopTemplateModified"
    template_id: str
    template_payload_hash: str
    signed_template_payload: CanonicalPayload


@register_event_type
@dataclass(frozen=True)
class SopTemplateRevoked(GovernanceEvent):
    event_type = "SopTemplateRevoked"
    template_id: str
    reason: str
    revocation_payload: CanonicalPayload


@register_event_type
@dataclass(frozen=True)
class AuditServiceAuthenticationFailed(GovernanceEvent):
    event_type = "AuditServiceAuthenticationFailed"
    principal_id: str
    reason: str
