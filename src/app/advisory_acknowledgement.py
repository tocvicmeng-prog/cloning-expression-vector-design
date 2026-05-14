"""
module_id: app.advisory_acknowledgement
file: src/app/advisory_acknowledgement.py
task_id: T-806a

Active advisory presentation and acknowledgement workflow.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from domain.canonicalisation import canonical_json, canonical_sha256
from domain.events import (
    AdvisoryWarningPresented,
    DomainEvent,
    GovernanceEvent,
    RiskAdvisoryAcknowledged,
    RiskAdvisoryDeclined,
    RiskAdvisoryEscalated,
)
from domain.security import Principal, SecurityRole
from domain.types.governance import DecisionRecord
from domain.types.risk_advisory import (
    AdvisoryAcknowledgementDecision,
    RiskAdvisoryAcknowledgement,
    RiskAdvisoryReport,
)

MODULE_ID = "app.advisory_acknowledgement"
OWNING_TASKS = ("T-806a",)
MIN_ACK_JUSTIFICATION_CHARS = 20
BINDING_PRESENTATION_ROLES = frozenset({SecurityRole.ADMINISTRATOR, SecurityRole.REVIEWER})


class GovernanceEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


@dataclass(frozen=True)
class AdvisoryPresentationRequest:
    report: RiskAdvisoryReport
    recipient: Principal
    presenting_surface: str
    occurred_at_utc: datetime
    event_id: str
    actor_id: str = "app.advisory_acknowledgement"

    def __post_init__(self) -> None:
        if not self.presenting_surface:
            raise ValueError("presenting_surface cannot be empty")
        if not self.event_id:
            raise ValueError("event_id cannot be empty")
        if not self.actor_id:
            raise ValueError("actor_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise ValueError("occurred_at_utc must be timezone-aware")


@dataclass(frozen=True)
class AdvisoryActionRequest:
    report: RiskAdvisoryReport
    advisory_id: str
    actor: Principal
    presentation_event: AdvisoryWarningPresented
    justification: str
    decision_record: DecisionRecord
    occurred_at_utc: datetime
    event_id: str
    institutional_approval_id: str | None = None

    def __post_init__(self) -> None:
        if not self.advisory_id:
            raise ValueError("advisory_id cannot be empty")
        if not self.justification:
            raise ValueError("justification cannot be empty")
        if not self.event_id:
            raise ValueError("event_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise ValueError("occurred_at_utc must be timezone-aware")


class AdvisoryAcknowledgementService:
    def __init__(self, event_log: GovernanceEventLog | None = None) -> None:
        self._event_log = event_log

    def present(self, request: AdvisoryPresentationRequest) -> AdvisoryWarningPresented:
        event = AdvisoryWarningPresented(
            event_id=request.event_id,
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            institution_id=str(request.recipient.institution),
            design_session_id=request.report.design_session_id,
            construct_id=request.report.construct_id,
            construct_version=request.report.construct_version,
            report_content_hash=str(request.report.report_content_hash),
            advisory_ids=tuple(advisory.advisory_id for advisory in request.report.advisories),
            presenting_surface=request.presenting_surface,
            recipient_principal_id=str(request.recipient.id),
            recipient_role=request.recipient.role.value,
        )
        self._append(event)
        return event

    def acknowledge(self, request: AdvisoryActionRequest) -> RiskAdvisoryAcknowledged:
        acknowledgement = _acknowledgement(
            request,
            decision=AdvisoryAcknowledgementDecision.ACKNOWLEDGED,
        )
        payload = _action_payload(request, acknowledgement)
        event = RiskAdvisoryAcknowledged(
            event_id=request.event_id,
            occurred_at_utc=request.occurred_at_utc,
            actor_id=str(request.actor.id),
            institution_id=str(request.actor.institution),
            acknowledgement_payload=payload,
            acknowledgement_content_hash=str(canonical_sha256(acknowledgement)),
        )
        self._append(event)
        return event

    def decline(self, request: AdvisoryActionRequest) -> RiskAdvisoryDeclined:
        acknowledgement = _acknowledgement(
            request,
            decision=AdvisoryAcknowledgementDecision.DECLINED,
        )
        payload = _action_payload(request, acknowledgement)
        event = RiskAdvisoryDeclined(
            event_id=request.event_id,
            occurred_at_utc=request.occurred_at_utc,
            actor_id=str(request.actor.id),
            institution_id=str(request.actor.institution),
            decline_payload=payload,
            decline_content_hash=str(canonical_sha256(acknowledgement)),
        )
        self._append(event)
        return event

    def escalate(self, request: AdvisoryActionRequest) -> RiskAdvisoryEscalated:
        if not request.institutional_approval_id:
            raise ValueError("institutional_approval_id is required for escalation")
        acknowledgement = _acknowledgement(
            request,
            decision=AdvisoryAcknowledgementDecision.ESCALATED,
        )
        payload = _action_payload(request, acknowledgement)
        event = RiskAdvisoryEscalated(
            event_id=request.event_id,
            occurred_at_utc=request.occurred_at_utc,
            actor_id=str(request.actor.id),
            institution_id=str(request.actor.institution),
            escalation_payload=payload,
            escalation_content_hash=str(canonical_sha256(acknowledgement)),
        )
        self._append(event)
        return event

    def _append(self, event: GovernanceEvent) -> None:
        if self._event_log is not None:
            self._event_log.append_event(event.institution_id, event)


def all_required_advisories_acknowledged(
    report: RiskAdvisoryReport,
    events: Iterable[GovernanceEvent],
) -> tuple[bool, frozenset[str]]:
    required = report.required_acknowledgements()
    if not required:
        return True, frozenset()
    event_tuple = tuple(events)
    binding_presentations = _binding_presentations(report, event_tuple)
    acknowledged = _acknowledged_advisories(report, event_tuple, binding_presentations)
    missing = required - acknowledged
    return not missing, frozenset(sorted(missing))


def _acknowledgement(
    request: AdvisoryActionRequest,
    *,
    decision: AdvisoryAcknowledgementDecision,
) -> RiskAdvisoryAcknowledgement:
    _require_binding_actor(request.actor)
    _require_report_advisory(request.report, request.advisory_id)
    _require_presentation_matches_report(request.presentation_event, request.report)
    return RiskAdvisoryAcknowledgement(
        advisory_id=request.advisory_id,
        report_content_hash=request.report.report_content_hash,
        construct_checksum=request.report.construct_checksum,
        decision=decision,
        justification=request.justification,
        decision_record=request.decision_record,
        acknowledged_at_utc=request.occurred_at_utc,
    )


def _action_payload(
    request: AdvisoryActionRequest,
    acknowledgement: RiskAdvisoryAcknowledgement,
) -> tuple[tuple[str, str], ...]:
    payload = {
        "acknowledgement_json": canonical_json(acknowledgement).decode("utf-8"),
        "advisory_id": acknowledgement.advisory_id,
        "construct_checksum": str(acknowledgement.construct_checksum),
        "decision": acknowledgement.decision.value,
        "decision_record_id": acknowledgement.decision_record.decision_id,
        "justification": acknowledgement.justification,
        "presentation_event_id": request.presentation_event.event_id,
        "report_content_hash": str(acknowledgement.report_content_hash),
        "signature_valid": str(_phase_local_signature_valid(acknowledgement)).lower(),
    }
    if request.institutional_approval_id is not None:
        payload["institutional_approval_id"] = request.institutional_approval_id
    return tuple(sorted(payload.items()))


def _binding_presentations(
    report: RiskAdvisoryReport,
    events: tuple[GovernanceEvent, ...],
) -> dict[str, AdvisoryWarningPresented]:
    presentations: dict[str, AdvisoryWarningPresented] = {}
    for event in events:
        if not isinstance(event, AdvisoryWarningPresented):
            continue
        if event.report_content_hash != str(report.report_content_hash):
            continue
        if event.construct_id != report.construct_id:
            continue
        if event.construct_version != report.construct_version:
            continue
        if event.recipient_role not in {role.value for role in BINDING_PRESENTATION_ROLES}:
            continue
        presentations[event.event_id] = event
    return presentations


def _acknowledged_advisories(
    report: RiskAdvisoryReport,
    events: tuple[GovernanceEvent, ...],
    binding_presentations: dict[str, AdvisoryWarningPresented],
) -> frozenset[str]:
    acknowledged: set[str] = set()
    for event in events:
        if not isinstance(event, RiskAdvisoryAcknowledged):
            continue
        payload = dict(event.acknowledgement_payload)
        advisory_id = payload.get("advisory_id", "")
        presentation_id = payload.get("presentation_event_id", "")
        if advisory_id not in report.required_acknowledgements():
            continue
        if presentation_id not in binding_presentations:
            continue
        if payload.get("decision") != AdvisoryAcknowledgementDecision.ACKNOWLEDGED.value:
            continue
        if payload.get("report_content_hash") != str(report.report_content_hash):
            continue
        if payload.get("construct_checksum") != str(report.construct_checksum):
            continue
        if payload.get("signature_valid") != "true":
            continue
        if len(payload.get("justification", "").strip()) < MIN_ACK_JUSTIFICATION_CHARS:
            continue
        acknowledged.add(advisory_id)
    return frozenset(acknowledged)


def _require_binding_actor(actor: Principal) -> None:
    if not actor.can_act_as(SecurityRole.REVIEWER):
        raise PermissionError("advisory actions require reviewer or administrator authority")


def _require_report_advisory(report: RiskAdvisoryReport, advisory_id: str) -> None:
    if advisory_id not in {advisory.advisory_id for advisory in report.advisories}:
        raise ValueError(f"advisory_id is not present in report: {advisory_id}")


def _require_presentation_matches_report(
    presentation: AdvisoryWarningPresented,
    report: RiskAdvisoryReport,
) -> None:
    if presentation.report_content_hash != str(report.report_content_hash):
        raise ValueError("presentation report_content_hash does not match report")
    if presentation.construct_id != report.construct_id:
        raise ValueError("presentation construct_id does not match report")
    if presentation.construct_version != report.construct_version:
        raise ValueError("presentation construct_version does not match report")


def _phase_local_signature_valid(acknowledgement: RiskAdvisoryAcknowledgement) -> bool:
    return bool(acknowledgement.decision_record.signature_bytes)


__all__ = [
    "BINDING_PRESENTATION_ROLES",
    "MIN_ACK_JUSTIFICATION_CHARS",
    "AdvisoryAcknowledgementService",
    "AdvisoryActionRequest",
    "AdvisoryPresentationRequest",
    "all_required_advisories_acknowledged",
]
