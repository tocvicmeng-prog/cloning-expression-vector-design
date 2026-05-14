"""
module_id: app.design_plan_orchestrator
file: src/app/design_plan_orchestrator.py
task_id: T-805a

Pre-screening draft design bundle orchestration.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Protocol

from domain.canonicalisation import canonical_json, canonical_sha256
from domain.events import (
    ControlSetRendered,
    DesignEvent,
    DesignRealisationPlanRendered,
    DomainEvent,
    RiskAdvisoryReportRendered,
)
from domain.sequence import Sha256
from domain.types.controls import ControlSet
from domain.types.design_plan import DesignRealisationPlan
from domain.types.risk_advisory import RiskAdvisoryReport
from engine.controls import (
    ControlGenerationInput,
    ControlSetGenerator,
    ControlValidationReport,
    validate_control_set,
)
from engine.design_plan import (
    DesignPlanGenerator,
    DesignPlanInput,
    design_plan_content_hash,
    render_json,
    render_markdown,
    render_pdf,
)
from engine.risk_classification import (
    RiskClassificationEngine,
    RiskClassificationInput,
)

MODULE_ID = "app.design_plan_orchestrator"
OWNING_TASKS = ("T-805a",)


class DesignEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


@dataclass(frozen=True)
class DraftDesignBundleRequest:
    design_session_id: str
    actor_id: str
    occurred_at_utc: datetime
    design_plan_input: DesignPlanInput
    control_input: ControlGenerationInput
    risk_classification_input: RiskClassificationInput
    event_id_prefix: str = "draft-design-bundle"

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise ValueError("design_session_id cannot be empty")
        if not self.actor_id:
            raise ValueError("actor_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise ValueError("occurred_at_utc must be timezone-aware")
        if not self.event_id_prefix:
            raise ValueError("event_id_prefix cannot be empty")
        construct_ids = {
            self.design_plan_input.construct_id,
            self.control_input.construct_id,
            self.risk_classification_input.construct_id,
        }
        if len(construct_ids) != 1:
            raise ValueError("draft bundle inputs must target the same construct_id")
        if self.risk_classification_input.design_session_id != self.design_session_id:
            raise ValueError("risk classification input must target the request design_session_id")
        if (
            self.risk_classification_input.construct_version
            != self.design_plan_input.construct_version
        ):
            raise ValueError("risk and design-plan inputs must use the same construct_version")


@dataclass(frozen=True)
class DraftDesignBundle:
    design_session_id: str
    construct_id: str
    construct_version: str
    design_plan: DesignRealisationPlan
    control_set: ControlSet
    risk_advisory_report: RiskAdvisoryReport
    control_validation: ControlValidationReport
    design_plan_json: str
    design_plan_markdown: str
    design_plan_pdf: bytes
    events: tuple[DesignEvent, ...]
    content_hash: Sha256 = field(init=False)

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise ValueError("design_session_id cannot be empty")
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not self.construct_version:
            raise ValueError("construct_version cannot be empty")
        object.__setattr__(self, "content_hash", canonical_sha256(self._content_payload()))

    def to_payload(self) -> dict[str, object]:
        payload = self._content_payload()
        payload["content_hash"] = str(self.content_hash)
        return payload

    def canonical_json(self) -> str:
        return canonical_json(self.to_payload()).decode("utf-8")

    def _content_payload(self) -> dict[str, object]:
        return {
            "construct_id": self.construct_id,
            "construct_version": self.construct_version,
            "control_set_content_hash": str(canonical_sha256(self.control_set)),
            "control_validation": self.control_validation,
            "design_plan_content_hash": str(design_plan_content_hash(self.design_plan)),
            "design_plan_json_hash": str(canonical_sha256(self.design_plan_json)),
            "design_plan_markdown_hash": str(canonical_sha256(self.design_plan_markdown)),
            "design_plan_pdf_hash": str(_sha256_bytes(self.design_plan_pdf)),
            "design_session_id": self.design_session_id,
            "event_fingerprints": tuple(
                (event.event_type, event.event_id, event.canonical_json()) for event in self.events
            ),
            "risk_advisory_report_content_hash": str(self.risk_advisory_report.report_content_hash),
        }


class DesignPlanOrchestrator:
    def __init__(
        self,
        risk_engine: RiskClassificationEngine,
        *,
        design_plan_generator: DesignPlanGenerator | None = None,
        control_generator: ControlSetGenerator | None = None,
        event_log: DesignEventLog | None = None,
    ) -> None:
        self._risk_engine = risk_engine
        self._design_plan_generator = design_plan_generator or DesignPlanGenerator()
        self._control_generator = control_generator or ControlSetGenerator()
        self._event_log = event_log

    def render_draft_bundle(self, request: DraftDesignBundleRequest) -> DraftDesignBundle:
        report = self._risk_engine.classify(request.risk_classification_input)
        design_plan_input = replace(
            request.design_plan_input,
            risk_advisory_report=report,
        )
        design_plan = self._design_plan_generator.generate(design_plan_input)
        control_set = self._control_generator.generate(request.control_input)
        control_validation = validate_control_set(request.control_input, control_set)
        design_plan_json = render_json(design_plan)
        design_plan_markdown = render_markdown(design_plan)
        design_plan_pdf = render_pdf(design_plan)
        events = _render_events(
            request=request,
            design_plan=design_plan,
            design_plan_json=design_plan_json,
            design_plan_markdown=design_plan_markdown,
            design_plan_pdf=design_plan_pdf,
            control_set=control_set,
            report=report,
        )
        bundle = DraftDesignBundle(
            design_session_id=request.design_session_id,
            construct_id=design_plan.construct_id,
            construct_version=design_plan_input.construct_version,
            design_plan=design_plan,
            control_set=control_set,
            risk_advisory_report=report,
            control_validation=control_validation,
            design_plan_json=design_plan_json,
            design_plan_markdown=design_plan_markdown,
            design_plan_pdf=design_plan_pdf,
            events=events,
        )
        if self._event_log is not None:
            for event in events:
                self._event_log.append_event(request.design_session_id, event)
        return bundle


def _render_events(
    *,
    request: DraftDesignBundleRequest,
    design_plan: DesignRealisationPlan,
    design_plan_json: str,
    design_plan_markdown: str,
    design_plan_pdf: bytes,
    control_set: ControlSet,
    report: RiskAdvisoryReport,
) -> tuple[DesignEvent, ...]:
    return (
        DesignRealisationPlanRendered(
            event_id=f"{request.event_id_prefix}.design-plan",
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            session_id=request.design_session_id,
            construct_id=design_plan.construct_id,
            construct_version=request.design_plan_input.construct_version,
            plan_content_hash=str(design_plan_content_hash(design_plan)),
            renderer_payload_hashes=(
                ("json", str(canonical_sha256(design_plan_json))),
                ("markdown", str(canonical_sha256(design_plan_markdown))),
                ("pdf", str(_sha256_bytes(design_plan_pdf))),
            ),
        ),
        ControlSetRendered(
            event_id=f"{request.event_id_prefix}.controls",
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            session_id=request.design_session_id,
            construct_id=control_set.construct_id,
            control_set_content_hash=str(canonical_sha256(control_set)),
            control_ids=tuple(control.control_id for control in control_set.controls),
        ),
        RiskAdvisoryReportRendered(
            event_id=f"{request.event_id_prefix}.risk-advisory",
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            session_id=request.design_session_id,
            construct_id=report.construct_id,
            construct_version=report.construct_version,
            report_content_hash=str(report.report_content_hash),
            advisory_ids=tuple(advisory.advisory_id for advisory in report.advisories),
        ),
    )


def _sha256_bytes(value: bytes) -> Sha256:
    return Sha256(hashlib.sha256(value).hexdigest())


__all__ = [
    "DesignEventLog",
    "DesignPlanOrchestrator",
    "DraftDesignBundle",
    "DraftDesignBundleRequest",
]
