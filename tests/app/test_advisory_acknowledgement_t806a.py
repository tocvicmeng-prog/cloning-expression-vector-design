"""
module_id: tests.app.test_advisory_acknowledgement_t806a
file: tests/app/test_advisory_acknowledgement_t806a.py
task_id: T-806a
"""

from __future__ import annotations

import ast
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from app.advisory_acknowledgement import (
    AdvisoryAcknowledgementService,
    AdvisoryActionRequest,
    AdvisoryPresentationRequest,
    all_required_advisories_acknowledged,
)
from domain.events import DomainEvent, GovernanceEvent, RiskAdvisoryAcknowledged
from domain.security import AdminPrincipal, InstitutionId, PrincipalId, SecurityRole, UserPrincipal
from domain.sequence import sha256_text
from domain.types.citation import GradedCitation
from domain.types.governance import DecisionRecord, RoleSnapshot
from domain.types.risk_advisory import RiskAdvisory, RiskAdvisoryReport, RiskAdvisorySeverity

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 5, 14, 13, 0, tzinfo=UTC)


def test_present_and_acknowledge_required_advisory_satisfies_predicate() -> None:
    report = _report()
    event_log = MemoryGovernanceEventLog()
    service = AdvisoryAcknowledgementService(event_log)
    presentation = service.present(_presentation_request(report, _admin()))
    acknowledged = service.acknowledge(
        _action_request(
            report,
            presentation,
            event_id="ack-1",
            justification="Reviewed by administrator with institutional context.",
        )
    )

    satisfied, missing = all_required_advisories_acknowledged(
        report,
        event_log.events["inst"],
    )

    assert isinstance(acknowledged, RiskAdvisoryAcknowledged)
    assert satisfied
    assert missing == frozenset()
    assert tuple(event.event_type for event in event_log.events["inst"]) == (
        "AdvisoryWarningPresented",
        "RiskAdvisoryAcknowledged",
    )
    assert dict(acknowledged.acknowledgement_payload)["presentation_event_id"] == (
        presentation.event_id
    )


def test_presentation_only_decline_and_escalation_do_not_satisfy_acknowledgement_gate() -> None:
    report = _report()
    service = AdvisoryAcknowledgementService()
    presentation = service.present(_presentation_request(report, _admin()))
    decline = service.decline(
        _action_request(
            report,
            presentation,
            event_id="decline-1",
            justification="Route this construct to an alternate institutional reviewer.",
        )
    )
    escalation = service.escalate(
        _action_request(
            report,
            presentation,
            event_id="escalate-1",
            justification="Escalate for institutional approval before authorisation.",
            institutional_approval_id="IBC-2026-001",
        )
    )

    for events in ((presentation,), (presentation, decline), (presentation, escalation)):
        satisfied, missing = all_required_advisories_acknowledged(report, events)
        assert not satisfied
        assert missing == frozenset({"risk.caution"})


def test_user_notification_and_user_action_cannot_satisfy_required_acknowledgement() -> None:
    report = _report()
    service = AdvisoryAcknowledgementService()
    user_presentation = service.present(_presentation_request(report, _user()))

    with pytest.raises(PermissionError, match="reviewer or administrator"):
        service.acknowledge(
            _action_request(
                report,
                user_presentation,
                actor=_user(),
                event_id="ack-user",
                justification="User attempted to acknowledge advisory warning.",
            )
        )

    admin_ack = service.acknowledge(
        _action_request(
            report,
            user_presentation,
            event_id="ack-admin-after-user-presentation",
            justification="Administrator reviewed after a user-only notification.",
        )
    )

    satisfied, missing = all_required_advisories_acknowledged(
        report,
        (user_presentation, admin_ack),
    )

    assert not satisfied
    assert missing == frozenset({"risk.caution"})


def test_hash_mismatch_and_short_justification_are_rejected() -> None:
    report = _report()
    service = AdvisoryAcknowledgementService()
    presentation = service.present(_presentation_request(report, _admin()))
    other_report = _report(seed="changed")

    with pytest.raises(ValueError, match="report_content_hash"):
        service.acknowledge(
            _action_request(
                other_report,
                presentation,
                event_id="ack-mismatch",
                justification="Reviewed by administrator with institutional context.",
            )
        )
    with pytest.raises(ValueError, match="20 characters"):
        service.acknowledge(
            _action_request(
                report,
                presentation,
                event_id="ack-short",
                justification="too short",
            )
        )
    with pytest.raises(ValueError, match="institutional_approval_id"):
        service.escalate(
            _action_request(
                report,
                presentation,
                event_id="escalate-missing",
                justification="Escalation requested with missing institutional approval.",
            )
        )


def test_advisory_acknowledgement_module_does_not_import_authorisation_event() -> None:
    path = ROOT / "src" / "app" / "advisory_acknowledgement.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            offenders.extend(
                alias.name
                for alias in node.names
                if alias.name == "OperationalProtocolAuthorised"
            )
        if isinstance(node, ast.Import):
            offenders.extend(
                alias.name for alias in node.names if "OperationalProtocolAuthorised" in alias.name
            )

    assert offenders == []


class MemoryGovernanceEventLog:
    def __init__(self) -> None:
        self.events: dict[str, list[GovernanceEvent]] = {}

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        assert isinstance(event, GovernanceEvent)
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


def _presentation_request(
    report: RiskAdvisoryReport,
    recipient: AdminPrincipal | UserPrincipal,
) -> AdvisoryPresentationRequest:
    return AdvisoryPresentationRequest(
        report=report,
        recipient=recipient,
        presenting_surface="cli==0.3.2",
        occurred_at_utc=NOW,
        event_id=f"present-{recipient.role.value}",
    )


def _action_request(
    report: RiskAdvisoryReport,
    presentation_event: GovernanceEvent,
    *,
    event_id: str,
    justification: str,
    actor: AdminPrincipal | UserPrincipal | None = None,
    institutional_approval_id: str | None = None,
) -> AdvisoryActionRequest:
    assert hasattr(presentation_event, "report_content_hash")
    return AdvisoryActionRequest(
        report=report,
        advisory_id="risk.caution",
        actor=actor or _admin(),
        presentation_event=presentation_event,  # type: ignore[arg-type]
        justification=justification,
        decision_record=_decision_record(event_id),
        occurred_at_utc=NOW,
        event_id=event_id,
        institutional_approval_id=institutional_approval_id,
    )


def _report(seed: str = "construct") -> RiskAdvisoryReport:
    checksum = sha256_text(seed)
    report_hash = sha256_text(f"report:{seed}")
    citation = GradedCitation(
        text="Institutional biosafety guidance",
        grade="A1",
        accessed=date(2026, 5, 14),
        url="https://example.org/biosafety",
    )
    return RiskAdvisoryReport(
        design_session_id="session-806a",
        construct_id="construct-806a",
        construct_checksum=checksum,
        construct_version="1",
        report_content_hash=report_hash,
        advisory_catalogue_version="risk-v1",
        advisory_catalogue_content_hash=sha256_text("catalogue"),
        advisories=(
            RiskAdvisory(
                advisory_id="risk.info",
                severity=RiskAdvisorySeverity.INFO,
                category="info",
                message="Informational advisory",
                citation=citation,
            ),
            RiskAdvisory(
                advisory_id="risk.caution",
                severity=RiskAdvisorySeverity.CAUTION,
                category="biosafety",
                message="Caution advisory",
                citation=citation,
            ),
        ),
    )


def _decision_record(seed: str) -> DecisionRecord:
    snapshot = RoleSnapshot(
        principal_id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution_id="inst",
        captured_at_utc=NOW,
        credentials_verified_at_utc=NOW,
    )
    return DecisionRecord(
        decision_id=f"decision-{seed}",
        decision_type="risk_advisory_acknowledgement",
        role_snapshot=snapshot,
        profile_content_hash=sha256_text("profile"),
        policy_version="policy-v1",
        signed_payload_hash=sha256_text(f"payload:{seed}"),
        signature_bytes=b"signature",
        signed_at_utc=NOW,
    )


def _admin() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def _user() -> UserPrincipal:
    return UserPrincipal(
        id=PrincipalId("user-1"),
        role=SecurityRole.USER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )
