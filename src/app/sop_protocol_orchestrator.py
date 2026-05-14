"""
module_id: app.sop_protocol_orchestrator
file: src/app/sop_protocol_orchestrator.py
task_id: T-805b

Post-authorisation SOP protocol bundle orchestration.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Protocol

from domain.canonicalisation import canonical_json, canonical_sha256
from domain.events import (
    DesignEvent,
    DomainEvent,
    OperationalProtocolAuthorised,
    SopRendered,
)
from domain.sequence import Sha256
from domain.types.sop_protected import SopLinkedProtocol
from engine.sop_protocol import (
    SopProtocolAuthorisationMissingError,
    SopProtocolGenerationRequest,
    SopProtocolGenerator,
    render_json,
    render_markdown,
    render_pdf,
    sop_protocol_content_hash,
)

MODULE_ID = "app.sop_protocol_orchestrator"
OWNING_TASKS = ("T-805b",)

AuthorisationEvidencePayload = tuple[tuple[str, str], ...]


class DesignEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


class SopProtocolOrchestrationError(ValueError):
    """Raised when an SOP bundle request is internally inconsistent."""


@dataclass(frozen=True)
class SopProtocolBundleRequest:
    design_session_id: str
    actor_id: str
    occurred_at_utc: datetime
    generation_request: SopProtocolGenerationRequest
    event_id_prefix: str = "sop-protocol-bundle"

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise SopProtocolOrchestrationError("design_session_id cannot be empty")
        if not self.actor_id:
            raise SopProtocolOrchestrationError("actor_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise SopProtocolOrchestrationError("occurred_at_utc must be timezone-aware")
        if not self.event_id_prefix:
            raise SopProtocolOrchestrationError("event_id_prefix cannot be empty")


@dataclass(frozen=True)
class SopProtocolBundle:
    design_session_id: str
    construct_id: str
    sop_protocol: SopLinkedProtocol
    sop_protocol_json: str
    sop_protocol_markdown: str
    sop_protocol_pdf: bytes
    authorisation_evidence: AuthorisationEvidencePayload
    sop_rendered_event: SopRendered
    content_hash: Sha256 = field(init=False)

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise ValueError("design_session_id cannot be empty")
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        content_hash = _bundle_content_hash(
            design_session_id=self.design_session_id,
            construct_id=self.construct_id,
            sop_protocol=self.sop_protocol,
            sop_protocol_json=self.sop_protocol_json,
            sop_protocol_markdown=self.sop_protocol_markdown,
            sop_protocol_pdf=self.sop_protocol_pdf,
            authorisation_evidence=self.authorisation_evidence,
        )
        if self.sop_rendered_event.sop_bundle_hash != str(content_hash):
            raise ValueError("SopRendered event must reference the bundle content hash")
        object.__setattr__(self, "content_hash", content_hash)

    def to_payload(self) -> dict[str, object]:
        payload = self._content_payload()
        payload["content_hash"] = str(self.content_hash)
        payload["sop_rendered_event"] = self.sop_rendered_event.to_dict()
        return payload

    def canonical_json(self) -> str:
        return canonical_json(self.to_payload()).decode("utf-8")

    def _content_payload(self) -> dict[str, object]:
        return _bundle_content_payload(
            design_session_id=self.design_session_id,
            construct_id=self.construct_id,
            sop_protocol=self.sop_protocol,
            sop_protocol_json=self.sop_protocol_json,
            sop_protocol_markdown=self.sop_protocol_markdown,
            sop_protocol_pdf=self.sop_protocol_pdf,
            authorisation_evidence=self.authorisation_evidence,
        )


class SopProtocolOrchestrator:
    def __init__(
        self,
        sop_protocol_generator: SopProtocolGenerator,
        *,
        design_event_log: DesignEventLog | None = None,
    ) -> None:
        self._sop_protocol_generator = sop_protocol_generator
        self._design_event_log = design_event_log

    def render_sop_bundle(self, request: SopProtocolBundleRequest) -> SopProtocolBundle:
        authorisation = _required_session_authorisation(
            request.generation_request.observed_design_events,
            request.design_session_id,
        )
        generation_request = replace(
            request.generation_request,
            observed_design_events=(authorisation,),
        )
        protocol = self._sop_protocol_generator.generate(generation_request)
        protocol_json = render_json(protocol)
        protocol_markdown = render_markdown(protocol)
        protocol_pdf = render_pdf(protocol)
        evidence = _authorisation_evidence(authorisation)
        content_hash = _bundle_content_hash(
            design_session_id=request.design_session_id,
            construct_id=protocol.construct_id,
            sop_protocol=protocol,
            sop_protocol_json=protocol_json,
            sop_protocol_markdown=protocol_markdown,
            sop_protocol_pdf=protocol_pdf,
            authorisation_evidence=evidence,
        )
        event = SopRendered(
            event_id=f"{request.event_id_prefix}.sop-rendered",
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            session_id=request.design_session_id,
            sop_bundle_hash=str(content_hash),
        )
        bundle = SopProtocolBundle(
            design_session_id=request.design_session_id,
            construct_id=protocol.construct_id,
            sop_protocol=protocol,
            sop_protocol_json=protocol_json,
            sop_protocol_markdown=protocol_markdown,
            sop_protocol_pdf=protocol_pdf,
            authorisation_evidence=evidence,
            sop_rendered_event=event,
        )
        if self._design_event_log is not None:
            self._design_event_log.append_event(request.design_session_id, event)
        return bundle


def _required_session_authorisation(
    events: tuple[DesignEvent, ...],
    design_session_id: str,
) -> OperationalProtocolAuthorised:
    authorisations = tuple(
        event
        for event in events
        if isinstance(event, OperationalProtocolAuthorised)
        and event.session_id == design_session_id
    )
    if not authorisations:
        raise SopProtocolAuthorisationMissingError(
            "SopProtocolBundle requires an observed OperationalProtocolAuthorised "
            "event for the current design session"
        )
    return authorisations[-1]


def _authorisation_evidence(
    authorisation: OperationalProtocolAuthorised,
) -> AuthorisationEvidencePayload:
    payload = {
        "authorisation_event_hash": str(canonical_sha256(authorisation.to_dict())),
        "authorisation_event_id": authorisation.event_id,
        "decision_record_hash": authorisation.decision_record_hash,
        "profile_id": authorisation.profile_id,
    }
    return tuple(sorted(payload.items()))


def _bundle_content_hash(
    *,
    design_session_id: str,
    construct_id: str,
    sop_protocol: SopLinkedProtocol,
    sop_protocol_json: str,
    sop_protocol_markdown: str,
    sop_protocol_pdf: bytes,
    authorisation_evidence: AuthorisationEvidencePayload,
) -> Sha256:
    return canonical_sha256(
        _bundle_content_payload(
            design_session_id=design_session_id,
            construct_id=construct_id,
            sop_protocol=sop_protocol,
            sop_protocol_json=sop_protocol_json,
            sop_protocol_markdown=sop_protocol_markdown,
            sop_protocol_pdf=sop_protocol_pdf,
            authorisation_evidence=authorisation_evidence,
        )
    )


def _bundle_content_payload(
    *,
    design_session_id: str,
    construct_id: str,
    sop_protocol: SopLinkedProtocol,
    sop_protocol_json: str,
    sop_protocol_markdown: str,
    sop_protocol_pdf: bytes,
    authorisation_evidence: AuthorisationEvidencePayload,
) -> dict[str, object]:
    return {
        "authorisation_evidence": authorisation_evidence,
        "construct_id": construct_id,
        "design_session_id": design_session_id,
        "sop_protocol_content_hash": str(sop_protocol_content_hash(sop_protocol)),
        "sop_protocol_json_hash": str(canonical_sha256(sop_protocol_json)),
        "sop_protocol_markdown_hash": str(canonical_sha256(sop_protocol_markdown)),
        "sop_protocol_pdf_hash": str(_sha256_bytes(sop_protocol_pdf)),
        "sop_template_id": sop_protocol.sop_template_id,
    }


def _sha256_bytes(value: bytes) -> Sha256:
    return Sha256(hashlib.sha256(value).hexdigest())


__all__ = [
    "DesignEventLog",
    "SopProtocolBundle",
    "SopProtocolBundleRequest",
    "SopProtocolOrchestrationError",
    "SopProtocolOrchestrator",
]
