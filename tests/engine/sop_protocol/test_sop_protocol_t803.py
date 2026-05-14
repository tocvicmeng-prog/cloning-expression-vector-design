"""
module_id: tests.engine.sop_protocol.test_sop_protocol_t803
file: tests/engine/sop_protocol/test_sop_protocol_t803.py
task_id: T-803
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from domain.events import OperationalProtocolAuthorised
from domain.security import OperationalRole
from domain.types.derivation import SopTemplateId
from domain.types.signing_errors import SopTemplateTamperDetectedError
from domain.types.sop_protected import HazardClass, SopLinkedProtocol
from domain.types.sop_template import SopTemplate
from engine.sop_protocol import (
    SopProtocolAuthorisationMissingError,
    SopProtocolGenerationRequest,
    SopProtocolGenerator,
    render_json,
    render_markdown,
    render_pdf,
    sop_protocol_content_hash,
)
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template
from tests.fakes.sop_template.signer import FakeSopTemplateSigner

NOW = datetime(2026, 5, 14, 12, tzinfo=UTC)


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


def test_sop_protocol_requires_operational_authorisation_before_template_read() -> None:
    read_port = FakeTemplateReadPort(_signed_template(), [])
    generator = SopProtocolGenerator(read_port)

    with pytest.raises(SopProtocolAuthorisationMissingError, match="OperationalProtocolAuthorised"):
        generator.generate(_request(observed_design_events=()))

    assert read_port.requested == []


def test_sop_protocol_generation_uses_read_port_and_sop_protected_types() -> None:
    template = _signed_template()
    read_port = FakeTemplateReadPort(template, [])

    protocol = SopProtocolGenerator(read_port).generate(_request())

    assert isinstance(protocol, SopLinkedProtocol)
    assert read_port.requested == [template.template_id]
    assert protocol.construct_id == "construct-803"
    assert protocol.sop_template_id == str(template.template_id)
    assert protocol.authorisation_event_id == "authorised-1"
    assert protocol.protocol_dag.root == "step-01-authorisation-gate"
    assert protocol.protocol_dag.canonical_step_ids == (
        "step-01-authorisation-gate",
        "step-02-institutional-sop",
    )

    for step in protocol.protocol_dag.steps:
        assert step.sop_ref == "sop-template-1@1.0.0"
        assert step.approval_gate == "OperationalProtocolAuthorised"
        assert step.hazard_class is HazardClass.BSL1
        assert step.allowed_roles == frozenset({OperationalRole.CLONING_OPERATOR})
        assert step.checkpoint_criteria
        assert step.measured_outputs
        assert not step.deviation_policy.allowed
        assert step.deviation_policy.escalation_contact == "institutional-biosafety-office"
        assert step.decision_rule is not None


def test_sop_protocol_refuses_unsigned_template_from_read_port() -> None:
    generator = SopProtocolGenerator(FakeTemplateReadPort(unsigned_template(), []))

    with pytest.raises(SopTemplateTamperDetectedError, match="unsigned"):
        generator.generate(_request())


def test_sop_protocol_renderers_are_deterministic() -> None:
    protocol = SopProtocolGenerator(FakeTemplateReadPort(_signed_template(), [])).generate(
        _request()
    )

    json_text = render_json(protocol)
    markdown = render_markdown(protocol)
    pdf = render_pdf(protocol)

    assert render_json(protocol) == json_text
    assert render_markdown(protocol) == markdown
    assert render_pdf(protocol) == pdf
    assert sop_protocol_content_hash(protocol) == sop_protocol_content_hash(protocol)
    assert '"construct_id":"construct-803"' in json_text
    assert "SOP-Linked Protocol" in markdown
    assert "OperationalProtocolAuthorised" in markdown
    assert pdf.startswith(b"%PDF-1.4")
    assert b"/CreationDate" not in pdf


def _request(
    *,
    observed_design_events: tuple[OperationalProtocolAuthorised, ...] | None = None,
) -> SopProtocolGenerationRequest:
    events = (_authorisation_event(),) if observed_design_events is None else observed_design_events
    return SopProtocolGenerationRequest(
        construct_id="construct-803",
        template_id=SopTemplateId("sop-template-1"),
        observed_design_events=events,
        assembly_method="reference-only-assembly",
        host_id="ecoli-k12",
        biosafety_tier="BSL-1",
    )


def _authorisation_event() -> OperationalProtocolAuthorised:
    return OperationalProtocolAuthorised(
        event_id="authorised-1",
        occurred_at_utc=NOW,
        actor_id="app.authorisation_decision",
        session_id="session-803",
        profile_id="profile-1",
        decision_record_hash="decision-record-1",
    )


def _signed_template() -> SopTemplate:
    template = unsigned_template()
    signature = FakeSopTemplateSigner().sign(template, admin_principal())
    return signed_template(signature)
