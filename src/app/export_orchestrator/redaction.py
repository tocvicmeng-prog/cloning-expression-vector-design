"""
module_id: app.export_orchestrator.redaction
file: src/app/export_orchestrator/redaction.py
task_id: T-903

Export-profile redaction helpers for final bundle rendering.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any

from domain.canonicalisation import canonical_json
from domain.sequence import Sha256
from domain.types.derivation import ExportProfile

MODULE_ID = "app.export_orchestrator.redaction"
OWNING_TASKS = ("T-903",)

REDACTED_VALUE = "REDACTED"


@dataclass(frozen=True, slots=True)
class ExportRedactionPolicy:
    """Resolved export-profile policy used at serialisation time."""

    profile: ExportProfile
    profile_id: str
    include_authorisation_trace: bool
    include_screening_evidence: bool
    include_project_event_log: bool
    redact_user_identity: bool
    redact_institutional_ids: bool
    redact_vendor_account_ids: bool

    def policy_hash(self) -> Sha256:
        payload = {
            "profile": self.profile.value,
            "profile_id": self.profile_id,
            "include_authorisation_trace": self.include_authorisation_trace,
            "include_screening_evidence": self.include_screening_evidence,
            "include_project_event_log": self.include_project_event_log,
            "redact_user_identity": self.redact_user_identity,
            "redact_institutional_ids": self.redact_institutional_ids,
            "redact_vendor_account_ids": self.redact_vendor_account_ids,
        }
        return Sha256(hashlib.sha256(canonical_json(payload)).hexdigest())


_PROFILE_POLICIES: dict[ExportProfile, ExportRedactionPolicy] = {
    ExportProfile.INTERNAL_AUDIT: ExportRedactionPolicy(
        profile=ExportProfile.INTERNAL_AUDIT,
        profile_id="export.internal_audit",
        include_authorisation_trace=True,
        include_screening_evidence=True,
        include_project_event_log=True,
        redact_user_identity=False,
        redact_institutional_ids=False,
        redact_vendor_account_ids=True,
    ),
    ExportProfile.COLLABORATOR: ExportRedactionPolicy(
        profile=ExportProfile.COLLABORATOR,
        profile_id="export.public_share_redacted",
        include_authorisation_trace=False,
        include_screening_evidence=False,
        include_project_event_log=False,
        redact_user_identity=True,
        redact_institutional_ids=True,
        redact_vendor_account_ids=True,
    ),
    ExportProfile.VENDOR: ExportRedactionPolicy(
        profile=ExportProfile.VENDOR,
        profile_id="export.vendor_submission",
        include_authorisation_trace=False,
        include_screening_evidence=False,
        include_project_event_log=False,
        redact_user_identity=True,
        redact_institutional_ids=True,
        redact_vendor_account_ids=True,
    ),
    ExportProfile.PUBLICATION_SUPPLEMENT: ExportRedactionPolicy(
        profile=ExportProfile.PUBLICATION_SUPPLEMENT,
        profile_id="export.public_share_redacted",
        include_authorisation_trace=False,
        include_screening_evidence=False,
        include_project_event_log=False,
        redact_user_identity=True,
        redact_institutional_ids=True,
        redact_vendor_account_ids=True,
    ),
}


def redaction_policy_for_profile(profile: ExportProfile) -> ExportRedactionPolicy:
    """Return the canonical export policy for a derivation export profile."""

    return _PROFILE_POLICIES[profile]


def redact_payload(payload: Any, policy: ExportRedactionPolicy) -> Any:
    """Apply profile redaction recursively to JSON-like payloads."""

    if isinstance(payload, dict):
        return {
            str(key): _redact_value_for_key(str(key), value, policy)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if is_dataclass(payload) and not isinstance(payload, type):
        return redact_payload(asdict(payload), policy)
    if isinstance(payload, tuple | list):
        return [redact_payload(value, policy) for value in payload]
    if isinstance(payload, Enum):
        return payload.value
    return payload


def _redact_value_for_key(key: str, value: Any, policy: ExportRedactionPolicy) -> Any:
    normalised_key = key.lower()
    if policy.redact_user_identity and _is_user_identity_key(normalised_key):
        return REDACTED_VALUE
    if policy.redact_institutional_ids and _is_institutional_key(normalised_key):
        return REDACTED_VALUE
    if policy.redact_vendor_account_ids and _is_vendor_key(normalised_key):
        return REDACTED_VALUE
    return redact_payload(value, policy)


def _is_user_identity_key(key: str) -> bool:
    return (
        key in {"actor_id", "declared_by", "subject_user_id", "user_id"}
        or key.endswith("_user_id")
        or "principal_id" in key
    )


def _is_institutional_key(key: str) -> bool:
    return (
        key == "institution_id"
        or key.endswith("_institution_id")
        or key.endswith("_approval_id")
        or "institutional" in key
        or "biosafety_approval" in key
    )


def _is_vendor_key(key: str) -> bool:
    return "vendor_account" in key or key in {"account_id", "quote_id", "vendor_quote_id"}
