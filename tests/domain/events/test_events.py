"""
module_id: tests.domain.events
file: tests/domain/events/test_events.py
task_id: T-305
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from domain.events import (
    AdminActionMinted,
    AdvisoryWarningPresented,
    DomainEvent,
    EventStream,
    ExportBundleCreated,
    OperationalProtocolAuthorised,
    RiskAdvisoryAcknowledged,
    ScreeningCompleted,
    SessionForked,
    SessionStarted,
    SopRendered,
)
from domain.events.base import EVENT_REGISTRY

NOW = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)


def test_design_event_round_trips_with_canonical_json() -> None:
    event = ScreeningCompleted(
        event_id="event-1",
        occurred_at_utc=NOW,
        actor_id="screening-orchestrator",
        session_id="session-1",
        batch_id="batch-1",
        verdict_payload=(("realisation-1", "CLEAR"), ("realisation-2", "WATCHLIST")),
    )

    restored = DomainEvent.from_dict(event.to_dict())

    assert restored == event
    assert restored.canonical_json() == event.canonical_json()
    assert event.stream is EventStream.DESIGN


def test_governance_events_embed_full_signed_payloads_not_only_references() -> None:
    event = RiskAdvisoryAcknowledged(
        event_id="event-2",
        occurred_at_utc=NOW,
        actor_id="admin-1",
        institution_id="inst",
        acknowledgement_payload=(
            ("advisory_id", "ADV-1"),
            ("justification", "Reviewed and accepted with institutional context."),
            ("decision_record_hash", "sha256:decision"),
        ),
        acknowledgement_content_hash="sha256:ack",
    )

    restored = DomainEvent.from_dict(event.to_dict())

    assert restored == event
    assert dict(event.acknowledgement_payload)["decision_record_hash"] == "sha256:decision"
    assert event.stream is EventStream.GOVERNANCE


def test_export_event_round_trips_manifest_payload() -> None:
    event = ExportBundleCreated(
        event_id="event-3",
        occurred_at_utc=NOW,
        actor_id="export-orchestrator",
        institution_id="inst",
        bundle_id="bundle-1",
        bundle_hash="sha256:bundle",
        artefact_manifest=(("genbank", "construct.gb"), ("sbol", "construct.nt")),
    )

    assert DomainEvent.from_dict(event.to_dict()) == event
    assert event.stream is EventStream.EXPORT


def test_v12_screening_authorisation_and_sop_events_are_design_stream() -> None:
    for event_cls in (ScreeningCompleted, OperationalProtocolAuthorised, SopRendered):
        assert event_cls.stream is EventStream.DESIGN


def test_v15_advisory_presentation_schema_records_active_warning_fields() -> None:
    event = AdvisoryWarningPresented(
        event_id="event-4",
        occurred_at_utc=NOW,
        actor_id="advisory-service",
        institution_id="inst",
        design_session_id="session-1",
        construct_id="construct-1",
        construct_version="1.0.0",
        report_content_hash="sha256:report",
        advisory_ids=("ADV-1", "ADV-2"),
        presenting_surface="cli",
        recipient_principal_id="admin-1",
        recipient_role="administrator",
    )

    assert DomainEvent.from_dict(event.to_dict()) == event
    assert event.stream is EventStream.GOVERNANCE


def test_admin_action_events_are_governance_stream_and_self_contained() -> None:
    event = AdminActionMinted(
        event_id="event-5",
        occurred_at_utc=NOW,
        actor_id="admin-1",
        institution_id="inst",
        target_user_id="user-1",
        profile_payload=(("profile_id", "profile-1"), ("subject_user_id", "user-1")),
        profile_content_hash="sha256:profile",
        justification="Initial authorised institutional profile.",
    )

    assert DomainEvent.from_dict(event.to_dict()) == event
    assert event.stream is EventStream.GOVERNANCE
    assert dict(event.profile_payload)["profile_id"] == "profile-1"


def test_event_registry_contains_expected_active_event_types() -> None:
    expected = {
        "SessionStarted",
        "PartAdded",
        "HostSelected",
        "FreeTextEntered",
        "LLMTranslationProposed",
        "LLMTranslationConfirmed",
        "RuleAcknowledged",
        "OverrideJustified",
        "DesignCompiled",
        "ScreeningCompleted",
        "OperationalProtocolAuthorised",
        "SopRendered",
        "SessionForked",
        "AdminBootstrapped",
        "AdminActionMinted",
        "AdminActionModified",
        "AdminActionRevoked",
        "InstitutionalPolicyUpdated",
        "ReviewerSignedOff",
        "AuthorisationAttemptDenied",
        "PluginManifestApproved",
        "PluginManifestRejected",
        "AdvisoryWarningPresented",
        "RiskAdvisoryAcknowledged",
        "RiskAdvisoryDeclined",
        "RiskAdvisoryEscalated",
        "UnsupportedBiosafetyTierAttempted",
        "AuditKeyRotated",
        "DecisionRecordPrincipalKeyRevoked",
        "DecisionRecordPublicKeyDistributed",
        "SopTemplateMinted",
        "SopTemplateModified",
        "SopTemplateRevoked",
        "SopTemplateSigningKeyDistributed",
        "SopTemplateSigningKeyRevoked",
        "AuditServiceAuthenticationFailed",
        "ExportProfileRedactionApplied",
        "ExportBundleCreated",
    }

    assert expected <= set(EVENT_REGISTRY)


def test_session_started_and_forked_validate_session_fields() -> None:
    started = SessionStarted(
        event_id="event-6",
        occurred_at_utc=NOW,
        actor_id="user-1",
        session_id="session-1",
        project_name="Example",
    )
    forked = SessionForked(
        event_id="event-7",
        occurred_at_utc=NOW,
        actor_id="user-1",
        session_id="session-1",
        new_session_id="session-2",
        lineage=("session-1",),
    )

    assert DomainEvent.from_dict(started.to_dict()) == started
    assert DomainEvent.from_dict(forked.to_dict()) == forked


def test_event_deserialisation_rejects_bad_shapes() -> None:
    with pytest.raises(TypeError, match="occurred_at_utc"):
        DomainEvent.from_dict(
            {
                "event_type": "SessionStarted",
                "stream": "design",
                "event_id": "event-1",
                "occurred_at_utc": 123,
                "actor_id": "user-1",
                "session_id": "session-1",
                "project_name": "Example",
            },
        )

    with pytest.raises(TypeError, match="verdict_payload"):
        DomainEvent.from_dict(
            {
                "event_type": "ScreeningCompleted",
                "stream": "design",
                "event_id": "event-1",
                "occurred_at_utc": "2026-05-14T12:00:00Z",
                "actor_id": "screening-orchestrator",
                "session_id": "session-1",
                "batch_id": "batch-1",
                "verdict_payload": [["realisation-1"]],
            },
        )


def test_base_event_validation_rejects_empty_actor_and_naive_time() -> None:
    with pytest.raises(ValueError, match="actor_id"):
        SessionStarted(
            event_id="event-8",
            occurred_at_utc=NOW,
            actor_id="",
            session_id="session-1",
            project_name="Example",
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        SessionStarted(
            event_id="event-9",
            occurred_at_utc=datetime(2026, 5, 14, 12, 0),
            actor_id="user-1",
            session_id="session-1",
            project_name="Example",
        )
