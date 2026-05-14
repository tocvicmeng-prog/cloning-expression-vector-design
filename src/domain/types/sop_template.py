"""
module_id: domain.types.sop_template
file: src/domain/types/sop_template.py
task_id: T-316a

Signed SOP-template value objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.canonicalisation import canonical_sha256
from domain.security.identifiers import KeyVersionId, PrincipalId
from domain.sequence import Sha256
from domain.types.derivation import Semver, SopTemplateId


@dataclass(frozen=True)
class SopTemplateSignature:
    template_content_hash: Sha256
    signature_bytes: bytes
    signing_key_version: KeyVersionId
    signed_at_utc: datetime

    def __post_init__(self) -> None:
        _require_non_empty(str(self.template_content_hash), "template_content_hash")
        if not self.signature_bytes:
            raise ValueError("signature_bytes cannot be empty")
        _require_non_empty(str(self.signing_key_version), "signing_key_version")
        _require_aware(self.signed_at_utc, "signed_at_utc")


@dataclass(frozen=True)
class SopTemplate:
    template_id: SopTemplateId
    version: Semver
    name: str
    description: str
    content_markdown: str
    hazard_notes: tuple[str, ...]
    required_approval_gate: str
    signature: SopTemplateSignature | None = None

    def __post_init__(self) -> None:
        _require_non_empty(str(self.template_id), "template_id")
        _require_non_empty(str(self.version), "version")
        _require_non_empty(self.name, "name")
        _require_non_empty(self.content_markdown, "content_markdown")
        _require_non_empty(self.required_approval_gate, "required_approval_gate")
        for note in self.hazard_notes:
            _require_non_empty(note, "hazard_note")
        if (
            self.signature is not None
            and self.signature.template_content_hash != self.content_hash()
        ):
            raise ValueError("SOP-template signature content hash does not match template payload")

    def content_payload(self) -> dict[str, object]:
        return {
            "content_markdown": self.content_markdown,
            "description": self.description,
            "hazard_notes": list(self.hazard_notes),
            "name": self.name,
            "required_approval_gate": self.required_approval_gate,
            "template_id": str(self.template_id),
            "version": str(self.version),
        }

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.content_payload())


@dataclass(frozen=True)
class SopTemplateVersion:
    template_id: SopTemplateId
    version: Semver
    content_hash: Sha256
    created_at_utc: datetime

    def __post_init__(self) -> None:
        _require_non_empty(str(self.template_id), "template_id")
        _require_non_empty(str(self.version), "version")
        _require_non_empty(str(self.content_hash), "content_hash")
        _require_aware(self.created_at_utc, "created_at_utc")


@dataclass(frozen=True)
class SopTemplateRevocation:
    template_id: SopTemplateId
    version: Semver
    revoked_by_principal_id: PrincipalId
    revoked_at_utc: datetime
    reason: str

    def __post_init__(self) -> None:
        _require_non_empty(str(self.template_id), "template_id")
        _require_non_empty(str(self.version), "version")
        _require_non_empty(str(self.revoked_by_principal_id), "revoked_by_principal_id")
        _require_aware(self.revoked_at_utc, "revoked_at_utc")
        _require_non_empty(self.reason, "reason")


def _require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} cannot be empty")


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")
