"""
module_id: tests.app.test_sop_protocol_orchestrator_t805b
file: tests/app/test_sop_protocol_orchestrator_t805b.py
task_id: T-805b
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from app.sop_protocol_orchestrator import (
    SopProtocolBundle,
    SopProtocolBundleRequest,
    SopProtocolOrchestrator,
)
from domain.events import DomainEvent, EventStream, OperationalProtocolAuthorised, SopRendered
from domain.types.derivation import SopTemplateId
from domain.types.sop_template import SopTemplate
from engine.sop_protocol import (
    SopProtocolAuthorisationMissingError,
    SopProtocolGenerationRequest,
    SopProtocolGenerator,
    render_json,
    render_markdown,
    render_pdf,
)
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template
from tests.fakes.sop_template.signer import FakeSopTemplateSigner

NOW = datetime(2026, 5, 14, 13, tzinfo=UTC)


@dataclass
class FakeTemplateReadPort:
    template: SopTemplate
    requested: list[SopTemplateId]

    def get_template(self, template_id: SopTemplateId) -> SopTemplate:
        self.requested.append(template_id)
        if template_id != self.template.template_id:
            raise KeyError(str(template_id))
        return self.template

    def list_templates(self) -> tuple[SopTemplate, ...]:
        return (self.template,)


class MemoryDesignEventLog:
    def __init__(self) -> None:
        self.events: dict[str, list[DomainEvent]] = {}

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


def test_sop_protocol_orchestrator_renders_bundle_and_appends_sop_event() -> None:
    template = _signed_template()
    read_port = FakeTemplateReadPort(template, [])
    event_log = MemoryDesignEventLog()

    bundle = SopProtocolOrchestrator(
        SopProtocolGenerator(read_port),
        design_event_log=event_log,
    ).render_sop_bundle(_request())

    assert isinstance(bundle, SopProtocolBundle)
    assert read_port.requested == [template.template_id]
    assert bundle.design_session_id == "session-805b"
    assert bundle.construct_id == "construct-805b"
    assert bundle.sop_protocol_json == render_json(bundle.sop_protocol)
    assert bundle.sop_protocol_markdown == render_markdown(bundle.sop_protocol)
    assert bundle.sop_protocol_pdf == render_pdf(bundle.sop_protocol)
    assert dict(bundle.authorisation_evidence)["authorisation_event_id"] == "authorised-805b"
    assert isinstance(bundle.sop_rendered_event, SopRendered)
    assert bundle.sop_rendered_event.stream is EventStream.DESIGN
    assert bundle.sop_rendered_event.sop_bundle_hash == str(bundle.content_hash)
    assert event_log.events["session-805b"] == [bundle.sop_rendered_event]


def test_sop_protocol_orchestrator_refuses_without_authorisation_before_template_read() -> None:
    read_port = FakeTemplateReadPort(_signed_template(), [])
    event_log = MemoryDesignEventLog()
    orchestrator = SopProtocolOrchestrator(
        SopProtocolGenerator(read_port),
        design_event_log=event_log,
    )

    with pytest.raises(SopProtocolAuthorisationMissingError, match="current design session"):
        orchestrator.render_sop_bundle(_request(observed_design_events=()))

    assert read_port.requested == []
    assert event_log.events == {}


def test_sop_protocol_orchestrator_ignores_authorisation_for_another_session() -> None:
    read_port = FakeTemplateReadPort(_signed_template(), [])
    orchestrator = SopProtocolOrchestrator(SopProtocolGenerator(read_port))

    with pytest.raises(SopProtocolAuthorisationMissingError):
        orchestrator.render_sop_bundle(
            _request(
                observed_design_events=(
                    _authorisation_event(
                        event_id="authorised-other",
                        session_id="other-session",
                    ),
                )
            )
        )

    assert read_port.requested == []


def test_sop_protocol_bundle_canonical_json_is_deterministic() -> None:
    first = SopProtocolOrchestrator(
        SopProtocolGenerator(FakeTemplateReadPort(_signed_template(), []))
    ).render_sop_bundle(_request())
    second = SopProtocolOrchestrator(
        SopProtocolGenerator(FakeTemplateReadPort(_signed_template(), []))
    ).render_sop_bundle(_request())

    assert first.content_hash == second.content_hash
    assert first.canonical_json() == second.canonical_json()
    assert '"sop_rendered_event"' in first.canonical_json()


def _request(
    *,
    observed_design_events: tuple[OperationalProtocolAuthorised, ...] | None = None,
) -> SopProtocolBundleRequest:
    events = (_authorisation_event(),) if observed_design_events is None else observed_design_events
    return SopProtocolBundleRequest(
        design_session_id="session-805b",
        actor_id="app.sop_protocol_orchestrator",
        occurred_at_utc=NOW,
        event_id_prefix="session-805b.sop",
        generation_request=SopProtocolGenerationRequest(
            construct_id="construct-805b",
            template_id=SopTemplateId("sop-template-1"),
            observed_design_events=events,
            assembly_method="reference-only-assembly",
            host_id="ecoli-k12",
            biosafety_tier="BSL-1",
        ),
    )


def _authorisation_event(
    *,
    event_id: str = "authorised-805b",
    session_id: str = "session-805b",
) -> OperationalProtocolAuthorised:
    return OperationalProtocolAuthorised(
        event_id=event_id,
        occurred_at_utc=NOW,
        actor_id="app.authorisation_decision",
        session_id=session_id,
        profile_id="profile-805b",
        decision_record_hash="decision-record-805b",
    )


def _signed_template() -> SopTemplate:
    template = unsigned_template()
    signature = FakeSopTemplateSigner().sign(template, admin_principal())
    return signed_template(signature)
