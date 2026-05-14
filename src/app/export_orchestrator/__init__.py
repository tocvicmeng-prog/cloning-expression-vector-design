"""
module_id: app.export_orchestrator
file: src/app/export_orchestrator/__init__.py
task_id: T-903

Final export-bundle orchestration.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from domain.canonicalisation import canonical_json
from domain.events import (
    ExportBundleCreated,
    ExportEvent,
    ExportProfileRedactionApplied,
    OperationalProtocolAuthorised,
    ScreeningCompleted,
    SopRendered,
)
from domain.sequence import Sha256
from domain.types.derivation import DerivationEnvironment, ExportProfile

from .redaction import ExportRedactionPolicy, redact_payload, redaction_policy_for_profile
from .renderers.bundle_zip import bundle_zip_hash, render_bundle_zip
from .renderers.manifest import ExportArtefact, manifest_event_payload, render_manifest

MODULE_ID = "app.export_orchestrator"
OWNING_TASKS = ("T-903",)

_OPEN_SCREENING_VERDICTS = frozenset({"CLEAR", "NOT_APPLICABLE"})


class ExportOrchestrationError(ValueError):
    """Raised when a final export bundle cannot be produced."""


class ExportEventLogPort(Protocol):
    def append_event(self, stream_id: str, event: ExportEvent) -> str: ...


class DesignBundlePort(Protocol):
    @property
    def design_session_id(self) -> str: ...

    @property
    def construct_id(self) -> str: ...

    @property
    def design_plan_json(self) -> str: ...

    @property
    def design_plan_markdown(self) -> str: ...

    @property
    def design_plan_pdf(self) -> bytes: ...

    @property
    def control_set(self) -> Any: ...

    @property
    def control_validation(self) -> Any: ...

    @property
    def content_hash(self) -> Sha256: ...

    def canonical_json(self) -> str: ...


class SopBundlePort(Protocol):
    @property
    def design_session_id(self) -> str: ...

    @property
    def construct_id(self) -> str: ...

    @property
    def sop_protocol_json(self) -> str: ...

    @property
    def sop_protocol_markdown(self) -> str: ...

    @property
    def sop_protocol_pdf(self) -> bytes: ...

    @property
    def authorisation_evidence(self) -> tuple[Any, ...]: ...

    @property
    def content_hash(self) -> Sha256: ...

    def canonical_json(self) -> str: ...


@dataclass(frozen=True, slots=True)
class ExportSequenceArtefacts:
    genbank: bytes
    fasta: bytes
    sbol3: bytes
    primer_csv: bytes
    primer_fasta: bytes


@dataclass(frozen=True, slots=True)
class ExportBundleRequest:
    bundle_id: str
    design_session_id: str
    institution_id: str
    actor_id: str
    occurred_at_utc: datetime
    export_profile: ExportProfile
    derivation_environment: DerivationEnvironment
    draft_design_bundle: DesignBundlePort
    sop_protocol_bundle: SopBundlePort
    screening_event: ScreeningCompleted
    authorisation_event: OperationalProtocolAuthorised
    sop_rendered_event: SopRendered
    sequence_artefacts: ExportSequenceArtefacts
    advisory_governance_events: tuple[Any, ...] = ()
    design_events: tuple[Any, ...] = ()
    event_id_prefix: str = "export-bundle"


@dataclass(frozen=True, slots=True)
class ExportBundle:
    bundle_id: str
    design_session_id: str
    institution_id: str
    export_profile: ExportProfile
    artefacts: tuple[ExportArtefact, ...]
    manifest_json: str
    zip_bytes: bytes
    content_hash: Sha256
    events: tuple[ExportEvent, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "design_session_id": self.design_session_id,
            "institution_id": self.institution_id,
            "export_profile": self.export_profile.value,
            "bundle_hash": str(self.content_hash),
            "manifest_hash": str(
                Sha256(hashlib.sha256(self.manifest_json.encode("utf-8")).hexdigest())
            ),
            "artefacts": [
                {
                    "path": artefact.path,
                    "media_type": artefact.media_type,
                    "size_bytes": len(artefact.content),
                    "sha256": str(artefact.content_hash),
                }
                for artefact in sorted(self.artefacts, key=lambda item: item.path)
            ],
            "event_ids": [event.event_id for event in self.events],
        }

    def canonical_json(self) -> str:
        return canonical_json(self.to_payload()).decode("utf-8")


class ExportOrchestrator:
    """Build complete, redacted, deterministic final export bundles."""

    def __init__(self, export_event_log: ExportEventLogPort | None = None) -> None:
        self._export_event_log = export_event_log

    def create_bundle(self, request: ExportBundleRequest) -> ExportBundle:
        _validate_request(request)
        policy = redaction_policy_for_profile(request.export_profile)
        timestamp_utc = _normalise_timestamp(request.occurred_at_utc)

        redaction_event = ExportProfileRedactionApplied(
            event_id=f"{request.event_id_prefix}.redaction-applied",
            actor_id=request.actor_id,
            occurred_at_utc=timestamp_utc,
            institution_id=request.institution_id,
            export_profile_id=policy.profile_id,
            redaction_policy_hash=str(policy.policy_hash()),
        )

        artefacts = _build_artefacts(
            request=request, policy=policy, redaction_event=redaction_event
        )
        manifest_metadata = _redacted_json_payload(
            _metadata_payload(request=request, policy=policy, redaction_event=redaction_event),
            policy,
        )
        manifest_json = render_manifest(
            bundle_id=request.bundle_id,
            export_profile_id=policy.profile_id,
            derivation_environment_hash=request.derivation_environment.hash(),
            artefacts=artefacts,
            metadata=manifest_metadata,
        )
        manifest_artefact = ExportArtefact(
            path="manifest.json",
            media_type="application/json",
            content=manifest_json.encode("utf-8"),
        )
        zip_bytes = render_bundle_zip(
            (*artefacts, manifest_artefact),
            timestamp_utc=timestamp_utc,
        )
        bundle_hash = bundle_zip_hash(zip_bytes)
        bundle_event = ExportBundleCreated(
            event_id=f"{request.event_id_prefix}.bundle-created",
            actor_id=request.actor_id,
            occurred_at_utc=timestamp_utc,
            institution_id=request.institution_id,
            bundle_id=request.bundle_id,
            bundle_hash=str(bundle_hash),
            artefact_manifest=manifest_event_payload(
                bundle_id=request.bundle_id,
                manifest_json=manifest_json,
                artefacts=artefacts,
            ),
        )
        events: tuple[ExportEvent, ...] = (redaction_event, bundle_event)
        for event in events:
            if self._export_event_log is not None:
                self._export_event_log.append_event(request.institution_id, event)
        return ExportBundle(
            bundle_id=request.bundle_id,
            design_session_id=request.design_session_id,
            institution_id=request.institution_id,
            export_profile=request.export_profile,
            artefacts=(*artefacts, manifest_artefact),
            manifest_json=manifest_json,
            zip_bytes=zip_bytes,
            content_hash=bundle_hash,
            events=events,
        )


def create_export_bundle(
    request: ExportBundleRequest,
    *,
    export_event_log: ExportEventLogPort | None = None,
) -> ExportBundle:
    return ExportOrchestrator(export_event_log=export_event_log).create_bundle(request)


def _validate_request(request: ExportBundleRequest) -> None:
    if not request.bundle_id:
        raise ExportOrchestrationError("bundle_id is required")
    if not request.design_session_id:
        raise ExportOrchestrationError("design_session_id is required")
    if request.derivation_environment.export_profile != request.export_profile:
        raise ExportOrchestrationError(
            "derivation environment export profile does not match request profile"
        )
    _assert_matches(
        request.draft_design_bundle.design_session_id,
        request.design_session_id,
        "design bundle session",
    )
    _assert_matches(
        request.sop_protocol_bundle.design_session_id,
        request.design_session_id,
        "SOP bundle session",
    )
    _assert_matches(
        request.screening_event.session_id, request.design_session_id, "screening event session"
    )
    _assert_matches(
        request.authorisation_event.session_id,
        request.design_session_id,
        "authorisation event session",
    )
    _assert_matches(
        request.sop_rendered_event.session_id,
        request.design_session_id,
        "SOP rendered event session",
    )
    _assert_matches(
        request.draft_design_bundle.construct_id,
        request.sop_protocol_bundle.construct_id,
        "construct",
    )
    if str(request.sop_protocol_bundle.content_hash) != request.sop_rendered_event.sop_bundle_hash:
        raise ExportOrchestrationError(
            "SOP rendered event does not reference the supplied SOP bundle"
        )
    if _screening_verdict(request.screening_event) not in _OPEN_SCREENING_VERDICTS:
        raise ExportOrchestrationError(
            "screening must be completed with a non-blocking verdict before export"
        )
    if not request.authorisation_event.decision_record_hash:
        raise ExportOrchestrationError(
            "operational protocol authorisation evidence is required before export"
        )
    if not request.sop_rendered_event.sop_bundle_hash:
        raise ExportOrchestrationError("SOP rendering evidence is required before export")


def _assert_matches(actual: str, expected: str, label: str) -> None:
    if actual != expected:
        raise ExportOrchestrationError(f"{label} does not match export request")


def _build_artefacts(
    *,
    request: ExportBundleRequest,
    policy: ExportRedactionPolicy,
    redaction_event: ExportProfileRedactionApplied,
) -> tuple[ExportArtefact, ...]:
    artefacts = [
        _binary_artefact(
            "sequences/construct.gb", "chemical/x-genbank", request.sequence_artefacts.genbank
        ),
        _binary_artefact(
            "sequences/construct.fasta", "text/x-fasta", request.sequence_artefacts.fasta
        ),
        _binary_artefact(
            "sequences/construct.sbol3.ttl", "text/turtle", request.sequence_artefacts.sbol3
        ),
        _binary_artefact("primers/primers.csv", "text/csv", request.sequence_artefacts.primer_csv),
        _binary_artefact(
            "primers/primers.fasta", "text/x-fasta", request.sequence_artefacts.primer_fasta
        ),
        _text_artefact(
            "design/design_plan.json",
            "application/json",
            _json_text(request.draft_design_bundle.design_plan_json, policy),
        ),
        _text_artefact(
            "design/design_plan.md",
            "text/markdown",
            request.draft_design_bundle.design_plan_markdown,
        ),
        _binary_artefact(
            "design/design_plan.pdf", "application/pdf", request.draft_design_bundle.design_plan_pdf
        ),
        _json_artefact(
            "controls/control_set.json", request.draft_design_bundle.control_set, policy
        ),
        _json_artefact(
            "controls/control_validation.json",
            request.draft_design_bundle.control_validation,
            policy,
        ),
        _text_artefact(
            "sop/sop_linked_protocol.json",
            "application/json",
            _json_text(request.sop_protocol_bundle.sop_protocol_json, policy),
        ),
        _text_artefact(
            "sop/sop_linked_protocol.md",
            "text/markdown",
            request.sop_protocol_bundle.sop_protocol_markdown,
        ),
        _binary_artefact(
            "sop/sop_linked_protocol.pdf",
            "application/pdf",
            request.sop_protocol_bundle.sop_protocol_pdf,
        ),
        _binary_artefact(
            "environment/derivation_environment.json",
            "application/json",
            request.derivation_environment.canonical_json(),
        ),
        _json_artefact(
            "metadata/export_metadata.json",
            _metadata_payload(request=request, policy=policy, redaction_event=redaction_event),
            policy,
        ),
    ]
    if policy.include_screening_evidence:
        artefacts.append(
            _json_artefact(
                "screening/screening_verdict.json", request.screening_event.to_dict(), policy
            )
        )
    if policy.include_authorisation_trace:
        artefacts.append(
            _json_artefact(
                "authorisation/authorisation_evidence.json",
                {
                    "authorisation_event": request.authorisation_event.to_dict(),
                    "sop_rendered_event": request.sop_rendered_event.to_dict(),
                    "sop_authorisation_evidence": (
                        request.sop_protocol_bundle.authorisation_evidence
                    ),
                },
                policy,
            )
        )
        artefacts.append(
            _json_artefact(
                "authorisation/advisory_approval_trace.json",
                {
                    "redaction_event": redaction_event.to_dict(),
                    "advisory_governance_events": [
                        _event_to_payload(event) for event in request.advisory_governance_events
                    ],
                    "authorisation_event": request.authorisation_event.to_dict(),
                },
                policy,
            )
        )
    if policy.include_project_event_log:
        artefacts.append(
            _json_artefact(
                "events/design_events.json",
                [_event_to_payload(event) for event in request.design_events],
                policy,
            )
        )
    return tuple(artefacts)


def _metadata_payload(
    *,
    request: ExportBundleRequest,
    policy: ExportRedactionPolicy,
    redaction_event: ExportProfileRedactionApplied,
) -> dict[str, Any]:
    return {
        "schema": "cloning-expression-vector.export-metadata.v1",
        "bundle_id": request.bundle_id,
        "design_session_id": request.design_session_id,
        "construct_id": request.draft_design_bundle.construct_id,
        "institution_id": request.institution_id,
        "actor_id": request.actor_id,
        "export_profile": request.export_profile.value,
        "export_profile_id": policy.profile_id,
        "redaction_policy_hash": str(policy.policy_hash()),
        "redaction_event_id": redaction_event.event_id,
        "derivation_environment_hash": str(request.derivation_environment.hash()),
        "draft_design_bundle_hash": str(request.draft_design_bundle.content_hash),
        "sop_protocol_bundle_hash": str(request.sop_protocol_bundle.content_hash),
        "screening_event_id": request.screening_event.event_id,
        "authorisation_event_id": request.authorisation_event.event_id,
        "sop_rendered_event_id": request.sop_rendered_event.event_id,
    }


def _json_artefact(path: str, payload: Any, policy: ExportRedactionPolicy) -> ExportArtefact:
    return _text_artefact(path, "application/json", _json_payload(payload, policy))


def _text_artefact(path: str, media_type: str, text: str) -> ExportArtefact:
    return ExportArtefact(path=path, media_type=media_type, content=text.encode("utf-8"))


def _binary_artefact(path: str, media_type: str, content: bytes) -> ExportArtefact:
    return ExportArtefact(path=path, media_type=media_type, content=bytes(content))


def _json_text(raw_json_text: str, policy: ExportRedactionPolicy) -> str:
    try:
        import json

        payload = json.loads(raw_json_text)
    except ValueError:
        payload = {"raw": raw_json_text}
    return _json_payload(payload, policy)


def _json_payload(payload: Any, policy: ExportRedactionPolicy) -> str:
    return canonical_json(_redacted_json_payload(payload, policy)).decode("utf-8")


def _redacted_json_payload(payload: Any, policy: ExportRedactionPolicy) -> Any:
    return redact_payload(payload, policy)


def _event_to_payload(event: Any) -> Any:
    if hasattr(event, "to_dict"):
        return event.to_dict()
    return event


def _screening_verdict(event: ScreeningCompleted) -> str:
    verdict = getattr(event, "verdict", None)
    if verdict is not None:
        return str(verdict)
    return str(dict(event.verdict_payload).get("verdict", ""))


def _normalise_timestamp(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC).replace(microsecond=0)


__all__ = [
    "ExportArtefact",
    "ExportBundle",
    "ExportBundleRequest",
    "ExportEventLogPort",
    "ExportOrchestrationError",
    "ExportOrchestrator",
    "ExportRedactionPolicy",
    "ExportSequenceArtefacts",
    "create_export_bundle",
    "redaction_policy_for_profile",
]
