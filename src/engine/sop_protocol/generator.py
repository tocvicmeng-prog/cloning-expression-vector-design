"""
module_id: engine.sop_protocol.generator
file: src/engine/sop_protocol/generator.py
task_id: T-803

SOP-linked protocol generator gated on OperationalProtocolAuthorised.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from domain.events import DesignEvent, OperationalProtocolAuthorised
from domain.ports.sop_template import SopTemplateReadPort
from domain.security import OperationalRole
from domain.types.derivation import SopTemplateId
from domain.types.signing_errors import SopTemplateTamperDetectedError
from domain.types.sop_protected import (
    DeviationPolicy,
    HazardClass,
    ProtocolDAG,
    ProtocolEdge,
    ProtocolEdgeKind,
    ProtocolStep,
    SopLinkedProtocol,
)
from domain.types.sop_template import SopTemplate


class SopProtocolAuthorisationMissingError(PermissionError):
    """Raised when SOP-linked protocol generation is attempted before authorisation."""


class SopProtocolTemplateError(ValueError):
    """Raised when a signed template cannot be used for SOP-linked protocol generation."""


@dataclass(frozen=True)
class SopProtocolGenerationRequest:
    construct_id: str
    template_id: SopTemplateId
    observed_design_events: tuple[DesignEvent, ...]
    assembly_method: str
    host_id: str
    biosafety_tier: str
    allowed_roles: frozenset[OperationalRole] = frozenset({OperationalRole.CLONING_OPERATOR})
    institutional_escalation_contact: str = "institutional-biosafety-office"

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.construct_id, "construct_id"),
            (str(self.template_id), "template_id"),
            (self.assembly_method, "assembly_method"),
            (self.host_id, "host_id"),
            (self.biosafety_tier, "biosafety_tier"),
            (self.institutional_escalation_contact, "institutional_escalation_contact"),
        ):
            if not value:
                raise ValueError(f"{field_name} cannot be empty")
        if not self.allowed_roles:
            raise ValueError("allowed_roles cannot be empty")


class SopProtocolGenerator:
    def __init__(self, template_read_port: SopTemplateReadPort) -> None:
        self._template_read_port = template_read_port

    def generate(self, request: SopProtocolGenerationRequest) -> SopLinkedProtocol:
        authorisation = _required_authorisation_event(request.observed_design_events)
        template = self._template_read_port.get_template(request.template_id)
        _require_signed_authorised_template(template)
        steps = _protocol_steps(request, template)
        return SopLinkedProtocol(
            construct_id=request.construct_id,
            protocol_dag=ProtocolDAG(root=steps[0].step_id, steps=steps),
            sop_template_id=str(template.template_id),
            authorisation_event_id=authorisation.event_id,
        )


def sop_protocol_payload(protocol: SopLinkedProtocol) -> dict[str, object]:
    return {
        "authorisation_event_id": protocol.authorisation_event_id,
        "construct_id": protocol.construct_id,
        "protocol_dag": {
            "root": protocol.protocol_dag.root,
            "steps": [_step_payload(step) for step in protocol.protocol_dag.steps],
        },
        "sop_template_id": protocol.sop_template_id,
    }


def _required_authorisation_event(
    events: Iterable[DesignEvent],
) -> OperationalProtocolAuthorised:
    authorisations = tuple(
        event for event in events if isinstance(event, OperationalProtocolAuthorised)
    )
    if not authorisations:
        raise SopProtocolAuthorisationMissingError(
            "SopLinkedProtocol requires an observed OperationalProtocolAuthorised event"
        )
    return authorisations[-1]


def _require_signed_authorised_template(template: SopTemplate) -> None:
    if template.required_approval_gate != OperationalProtocolAuthorised.event_type:
        raise SopProtocolTemplateError(
            f"SOP template requires unsupported gate {template.required_approval_gate!r}"
        )
    if template.signature is None:
        raise SopTemplateTamperDetectedError("SOP template read port returned an unsigned template")


def _protocol_steps(
    request: SopProtocolGenerationRequest,
    template: SopTemplate,
) -> tuple[ProtocolStep, ...]:
    gate_step = ProtocolStep(
        step_id="step-01-authorisation-gate",
        action="Confirm the recorded operational authorisation before accessing the signed SOP.",
        reagents=(),
        quantities=(),
        temperature_c=None,
        duration=None,
        rationale="Operational SOP rendering is allowed only after governance approval.",
        safety_note="Stop if the authorisation event, template signature, or scope is absent.",
        successors=(ProtocolEdge("step-02-institutional-sop", ProtocolEdgeKind.THEN),),
        sop_ref=f"{template.template_id}@{template.version}",
        approval_gate=template.required_approval_gate,
        hazard_class=_hazard_class(request.biosafety_tier),
        allowed_roles=request.allowed_roles,
        checkpoint_criteria=(
            f"authorisation_event:{OperationalProtocolAuthorised.event_type}",
            f"template_hash:{template.content_hash()}",
        ),
        measured_outputs=("authorisation evidence recorded", "template signature accepted"),
        deviation_policy=DeviationPolicy(
            allowed=False,
            escalation_contact=request.institutional_escalation_contact,
        ),
        decision_rule="Refuse SOP rendering unless all checkpoint criteria are satisfied.",
    )
    sop_step = ProtocolStep(
        step_id="step-02-institutional-sop",
        action="Use the institution-controlled signed SOP template by reference.",
        reagents=(),
        quantities=(),
        temperature_c=None,
        duration=None,
        rationale=(
            "Procedure-specific content is governed by the signed institutional template, "
            "not generated ad hoc."
        ),
        safety_note="Follow local SOP controls and stop on any scope mismatch.",
        successors=(),
        sop_ref=f"{template.template_id}@{template.version}",
        approval_gate=template.required_approval_gate,
        hazard_class=_hazard_class(request.biosafety_tier),
        allowed_roles=request.allowed_roles,
        checkpoint_criteria=(
            f"assembly_method:{request.assembly_method}",
            f"host:{request.host_id}",
            f"biosafety_tier:{request.biosafety_tier}",
        ),
        measured_outputs=("institutional SOP reference archived",),
        deviation_policy=DeviationPolicy(
            allowed=False,
            escalation_contact=request.institutional_escalation_contact,
        ),
        decision_rule="Escalate to the institutional reviewer if the template scope differs.",
    )
    return (gate_step, sop_step)


def _hazard_class(biosafety_tier: str) -> HazardClass:
    mapping = {
        "BSL-1": HazardClass.BSL1,
        "BSL-2": HazardClass.BSL2,
        "BSL-2+": HazardClass.BSL2_PLUS,
        "BSL-3": HazardClass.BSL3,
    }
    try:
        return mapping[biosafety_tier]
    except KeyError as exc:
        raise SopProtocolTemplateError(f"unsupported SOP hazard tier: {biosafety_tier}") from exc


def _step_payload(step: ProtocolStep) -> dict[str, object]:
    return {
        "action": step.action,
        "allowed_roles": sorted(role.value for role in step.allowed_roles),
        "approval_gate": step.approval_gate,
        "checkpoint_criteria": list(step.checkpoint_criteria),
        "decision_rule": step.decision_rule,
        "deviation_policy": {
            "allowed": step.deviation_policy.allowed,
            "escalation_contact": step.deviation_policy.escalation_contact,
        },
        "duration": step.duration,
        "hazard_class": step.hazard_class.value,
        "measured_outputs": list(step.measured_outputs),
        "quantities": list(step.quantities),
        "rationale": step.rationale,
        "reagents": list(step.reagents),
        "safety_note": step.safety_note,
        "sop_ref": step.sop_ref,
        "step_id": step.step_id,
        "successors": [_edge_payload(edge) for edge in step.successors],
        "temperature_c": step.temperature_c,
    }


def _edge_payload(edge: ProtocolEdge) -> Mapping[str, str]:
    return {
        "kind": edge.kind.value,
        "target_step_id": edge.target_step_id,
    }
