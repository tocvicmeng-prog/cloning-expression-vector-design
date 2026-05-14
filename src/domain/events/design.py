"""
module_id: domain.events.design
file: src/domain/events/design.py
task_id: T-305

Design-stream event subclasses.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.events.base import CanonicalPayload, DesignEvent, SessionId, register_event_type


@register_event_type
@dataclass(frozen=True)
class SessionStarted(DesignEvent):
    event_type = "SessionStarted"
    project_name: str


@register_event_type
@dataclass(frozen=True)
class PartAdded(DesignEvent):
    event_type = "PartAdded"
    part_id: str
    part_payload_hash: str


@register_event_type
@dataclass(frozen=True)
class HostSelected(DesignEvent):
    event_type = "HostSelected"
    host_id: str
    host_role: str


@register_event_type
@dataclass(frozen=True)
class FreeTextEntered(DesignEvent):
    event_type = "FreeTextEntered"
    text: str


@register_event_type
@dataclass(frozen=True)
class LLMTranslationProposed(DesignEvent):
    event_type = "LLMTranslationProposed"
    structured: CanonicalPayload


@register_event_type
@dataclass(frozen=True)
class LLMTranslationConfirmed(DesignEvent):
    event_type = "LLMTranslationConfirmed"
    structured: CanonicalPayload


@register_event_type
@dataclass(frozen=True)
class RuleAcknowledged(DesignEvent):
    event_type = "RuleAcknowledged"
    rule_id: str
    justification: str


@register_event_type
@dataclass(frozen=True)
class OverrideJustified(DesignEvent):
    event_type = "OverrideJustified"
    override_id: str
    justification: str


@register_event_type
@dataclass(frozen=True)
class DesignCompiled(DesignEvent):
    event_type = "DesignCompiled"
    construct_id: str
    construct_checksum: str
    design_plan_hash: str


@register_event_type
@dataclass(frozen=True)
class ScreeningCompleted(DesignEvent):
    event_type = "ScreeningCompleted"
    batch_id: str
    verdict_payload: CanonicalPayload


@register_event_type
@dataclass(frozen=True)
class OperationalProtocolAuthorised(DesignEvent):
    event_type = "OperationalProtocolAuthorised"
    profile_id: str
    decision_record_hash: str


@register_event_type
@dataclass(frozen=True)
class SopRendered(DesignEvent):
    event_type = "SopRendered"
    sop_bundle_hash: str


@register_event_type
@dataclass(frozen=True)
class SessionForked(DesignEvent):
    event_type = "SessionForked"
    new_session_id: SessionId
    lineage: tuple[SessionId, ...]
