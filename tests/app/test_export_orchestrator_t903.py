"""
module_id: tests.app.test_export_orchestrator_t903
file: tests/app/test_export_orchestrator_t903.py
task_id: T-903
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
from zipfile import ZipFile

import pytest

from app.export_orchestrator import (
    ExportBundleRequest,
    ExportOrchestrationError,
    ExportOrchestrator,
    ExportSequenceArtefacts,
)
from domain.canonicalisation import canonical_json
from domain.events import (
    ExportEvent,
    OperationalProtocolAuthorised,
    RiskAdvisoryAcknowledged,
    ScreeningCompleted,
    SopRendered,
)
from domain.sequence import Sha256, sha256_text
from domain.types.derivation import (
    AuthProfileId,
    CatalogueId,
    ContainerDigest,
    DatabaseId,
    DerivationEnvironment,
    ExportProfile,
    GateName,
    LLMModelIdentifier,
    LLMUseSite,
    OptimisationSettings,
    PluginId,
    PredicateVersion,
    PrivacyClassification,
    PromptTemplateId,
    RandomSeedId,
    ReviewerDecision,
    RoundingPolicy,
    ScreeningScope,
    Semver,
    SopTemplateId,
    UnitsProfile,
    UserOverride,
)

FIXED_TIME = datetime(2026, 5, 14, 9, 30, 0, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class _DraftDesignBundle:
    design_session_id: str
    construct_id: str
    design_plan_json: str
    design_plan_markdown: str
    design_plan_pdf: bytes
    control_set: dict[str, object]
    control_validation: dict[str, object]
    content_hash: Sha256

    def canonical_json(self) -> str:
        return canonical_json(
            {
                "design_session_id": self.design_session_id,
                "construct_id": self.construct_id,
                "design_plan_json": self.design_plan_json,
                "control_set": self.control_set,
                "control_validation": self.control_validation,
            }
        ).decode("utf-8")


@dataclass(frozen=True, slots=True)
class _SopProtocolBundle:
    design_session_id: str
    construct_id: str
    sop_protocol_json: str
    sop_protocol_markdown: str
    sop_protocol_pdf: bytes
    authorisation_evidence: tuple[dict[str, object], ...]
    content_hash: Sha256

    def canonical_json(self) -> str:
        return canonical_json(
            {
                "design_session_id": self.design_session_id,
                "construct_id": self.construct_id,
                "sop_protocol_json": self.sop_protocol_json,
                "authorisation_evidence": self.authorisation_evidence,
            }
        ).decode("utf-8")


class _CapturingExportLog:
    def __init__(self) -> None:
        self.events: list[ExportEvent] = []

    def append_event(self, stream_id: str, event: ExportEvent) -> str:
        assert stream_id == "institution-1"
        self.events.append(event)
        return event.event_id


def test_export_orchestrator_creates_complete_deterministic_bundle_for_examples() -> None:
    for construct_id in ("white-paper-alpha", "white-paper-beta", "white-paper-gamma"):
        request = _request(bundle_id=f"bundle-{construct_id}", construct_id=construct_id)
        log = _CapturingExportLog()

        first = ExportOrchestrator(export_event_log=log).create_bundle(request)
        second = ExportOrchestrator().create_bundle(request)

        assert first.content_hash == second.content_hash
        assert first.zip_bytes == second.zip_bytes
        assert [event.event_type for event in log.events] == [
            "ExportProfileRedactionApplied",
            "ExportBundleCreated",
        ]

        with ZipFile(BytesIO(first.zip_bytes)) as archive:
            names = set(archive.namelist())
            assert names == _complete_internal_bundle_paths()
            for name in names:
                assert archive.read(name)
            manifest = json.loads(archive.read("manifest.json"))
            assert manifest["bundle_id"] == f"bundle-{construct_id}"
            assert manifest["artefact_count"] == len(names) - 1
            assert {artefact["path"]: artefact["sha256"] for artefact in manifest["artefacts"]}[
                "sop/sop_linked_protocol.json"
            ] == str(
                sha256_text(
                    json.dumps(
                        {"protocol": "linked", "actor_id": "author-1"},
                        separators=(",", ":"),
                        sort_keys=True,
                    )
                )
            )


def test_vendor_profile_redacts_and_omits_internal_evidence() -> None:
    request = _request(export_profile=ExportProfile.VENDOR)

    bundle = ExportOrchestrator().create_bundle(request)

    with ZipFile(BytesIO(bundle.zip_bytes)) as archive:
        names = set(archive.namelist())
        assert not any(name.startswith("authorisation/") for name in names)
        assert not any(name.startswith("screening/") for name in names)
        assert not any(name.startswith("events/") for name in names)
        metadata = json.loads(archive.read("metadata/export_metadata.json"))
        design_plan = json.loads(archive.read("design/design_plan.json"))

    assert metadata["actor_id"] == "REDACTED"
    assert metadata["institution_id"] == "REDACTED"
    assert design_plan["actor_id"] == "REDACTED"


def test_export_orchestrator_rejects_blocked_or_incomplete_evidence() -> None:
    blocked = replace(
        _request(),
        screening_event=ScreeningCompleted(
            event_id="screening-hit",
            occurred_at_utc=FIXED_TIME,
            actor_id="screening-service",
            session_id="session-1",
            batch_id="batch-1",
            verdict_payload=(("verdict", "HIT"),),
        ),
    )
    with pytest.raises(ExportOrchestrationError, match="screening must be completed"):
        ExportOrchestrator().create_bundle(blocked)

    incomplete_authorisation = replace(
        _request(),
        authorisation_event=OperationalProtocolAuthorised(
            event_id="auth-empty",
            occurred_at_utc=FIXED_TIME,
            actor_id="auth-service",
            session_id="session-1",
            profile_id="auth-profile-1",
            decision_record_hash="",
        ),
    )
    with pytest.raises(ExportOrchestrationError, match="authorisation evidence is required"):
        ExportOrchestrator().create_bundle(incomplete_authorisation)


def _request(
    *,
    bundle_id: str = "bundle-1",
    construct_id: str = "construct-1",
    export_profile: ExportProfile = ExportProfile.INTERNAL_AUDIT,
) -> ExportBundleRequest:
    draft_bundle = _draft_bundle(construct_id=construct_id)
    sop_bundle = _sop_bundle(construct_id=construct_id)
    authorisation_event = OperationalProtocolAuthorised(
        event_id="auth-1",
        occurred_at_utc=FIXED_TIME,
        actor_id="auth-service",
        session_id="session-1",
        profile_id="auth-profile-1",
        decision_record_hash=str(sha256_text("decision-record")),
    )
    screening_event = ScreeningCompleted(
        event_id="screening-clear",
        occurred_at_utc=FIXED_TIME,
        actor_id="screening-service",
        session_id="session-1",
        batch_id="batch-1",
        verdict_payload=(("verdict", "CLEAR"), ("provider", "fixture")),
    )
    sop_rendered_event = SopRendered(
        event_id="sop-rendered",
        occurred_at_utc=FIXED_TIME,
        actor_id="sop-service",
        session_id="session-1",
        sop_bundle_hash=str(sop_bundle.content_hash),
    )
    advisory_event = RiskAdvisoryAcknowledged(
        event_id="advisory-ack",
        occurred_at_utc=FIXED_TIME,
        actor_id="author-1",
        institution_id="institution-1",
        acknowledgement_payload=(("advisory_id", "adv-1"), ("subject_user_id", "author-1")),
        acknowledgement_content_hash=str(sha256_text("advisory-ack")),
    )
    return ExportBundleRequest(
        bundle_id=bundle_id,
        design_session_id="session-1",
        institution_id="institution-1",
        actor_id="author-1",
        occurred_at_utc=FIXED_TIME,
        export_profile=export_profile,
        derivation_environment=_environment(export_profile=export_profile),
        draft_design_bundle=draft_bundle,
        sop_protocol_bundle=sop_bundle,
        screening_event=screening_event,
        authorisation_event=authorisation_event,
        sop_rendered_event=sop_rendered_event,
        sequence_artefacts=ExportSequenceArtefacts(
            genbank=(
                b"LOCUS       CONSTRUCT     12 bp    DNA     circular 14-MAY-2026\n"
                b"ORIGIN\n        1 atgcgtaaaccg\n//\n"
            ),
            fasta=b">construct\nATGCGTAAACCG\n",
            sbol3=b"@prefix sbol: <http://sbols.org/v3#> .\n",
            primer_csv=b"name,sequence\nFWD,ATGCGT\nREV,CGGTTT\n",
            primer_fasta=b">FWD\nATGCGT\n>REV\nCGGTTT\n",
        ),
        advisory_governance_events=(advisory_event,),
        design_events=(screening_event, authorisation_event, sop_rendered_event),
        event_id_prefix=f"{bundle_id}.export",
    )


def _draft_bundle(*, construct_id: str) -> _DraftDesignBundle:
    design_json = json.dumps(
        {
            "plan": "DesignRealisationPlan",
            "construct_id": construct_id,
            "actor_id": "author-1",
            "institution_id": "institution-1",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return _DraftDesignBundle(
        design_session_id="session-1",
        construct_id=construct_id,
        design_plan_json=design_json,
        design_plan_markdown=f"# DesignRealisationPlan\n\nConstruct: {construct_id}\n",
        design_plan_pdf=b"%PDF-1.4\n% design plan fixture\n",
        control_set={"control_set_id": "controls-1", "institution_id": "institution-1"},
        control_validation={"verdict": "PASS", "checked_by_user_id": "qa-1"},
        content_hash=sha256_text(f"draft-{construct_id}"),
    )


def _sop_bundle(*, construct_id: str) -> _SopProtocolBundle:
    sop_json = json.dumps(
        {"protocol": "linked", "actor_id": "author-1"},
        sort_keys=True,
        separators=(",", ":"),
    )
    return _SopProtocolBundle(
        design_session_id="session-1",
        construct_id=construct_id,
        sop_protocol_json=sop_json,
        sop_protocol_markdown=f"# SopLinkedProtocol\n\nConstruct: {construct_id}\n",
        sop_protocol_pdf=b"%PDF-1.4\n% SOP fixture\n",
        authorisation_evidence=(
            {
                "event_id": "auth-1",
                "decision_record_hash": str(sha256_text("decision-record")),
                "subject_user_id": "author-1",
            },
        ),
        content_hash=sha256_text(f"sop-{construct_id}"),
    )


def _environment(*, export_profile: ExportProfile) -> DerivationEnvironment:
    return DerivationEnvironment(
        rule_registry_version=Semver("1.0.0"),
        rule_manifest_hashes={"MR": sha256_text("mr")},
        catalogue_versions={CatalogueId("parts"): Semver("2026.5.14")},
        catalogue_content_hashes={CatalogueId("parts"): sha256_text("parts")},
        plugin_versions={PluginId("codon"): Semver("1.2.3")},
        plugin_configurations={PluginId("codon"): sha256_text("plugin-config")},
        external_database_versions={DatabaseId("rebase"): "2026-05"},
        sop_template_versions={SopTemplateId("sop-assembly"): Semver("2.0.0")},
        container_image_digest=ContainerDigest("sha256:container"),
        cpu_arch="x86_64",
        locale="C.UTF-8",
        units_profile=UnitsProfile("si-v1"),
        rounding_policy=RoundingPolicy("half-even-6dp"),
        random_seeds={RandomSeedId("optimiser"): 7},
        optimisation_settings=OptimisationSettings(
            strategy="deterministic",
            objective_weights=(("gc_balance", Decimal("0.50")),),
            max_iterations=10,
        ),
        user_overrides=(
            UserOverride(
                override_id="override-1",
                path="/assembly/max_fragments",
                value=6,
                reason="Institutional fixture for deterministic test",
            ),
        ),
        reviewer_decisions=(
            ReviewerDecision(
                decision_id="decision-1",
                reviewer_id="reviewer-1",
                decision_type="approve",
                decision_content_hash=sha256_text("decision"),
            ),
        ),
        construct_checksum=sha256_text("construct"),
        authorisation_profile_id=AuthProfileId("auth-profile-1"),
        authorisation_profile_content_hash=sha256_text("auth-profile"),
        sop_template_content_hashes={SopTemplateId("sop-assembly"): sha256_text("sop")},
        screening_provider_trust_policy_version=Semver("1.0.0"),
        screening_query_scope=ScreeningScope.ASSEMBLED_PRODUCT,
        screening_threshold_policy_version=Semver("1.0.0"),
        screening_submitted_sequence_hash=sha256_text("submitted"),
        plugin_package_hashes={PluginId("codon"): sha256_text("plugin-package")},
        llm_prompt_template_versions={PromptTemplateId("advisory"): Semver("1.0.0")},
        llm_model_identifiers={LLMUseSite("advisory_text"): LLMModelIdentifier("none")},
        institutional_policy_version=Semver("2026.05"),
        user_declaration_hash=sha256_text("declaration"),
        export_profile=export_profile,
        redaction_policy_version=Semver("1.0.0"),
        risk_advisory_catalogue_version=Semver("2026.05"),
        risk_advisory_catalogue_content_hash=sha256_text("risk-catalogue"),
        privacy_classification=PrivacyClassification.SENSITIVE,
        advisory_approval_trace_hash=sha256_text("trace"),
        advisory_acknowledgement_event_ids=("advisory-ack",),
        gate_predicate_versions={
            GateName("BlockExport"): PredicateVersion("1.0.0-t903-final-export-readiness")
        },
        gate_predicate_content_hashes={
            GateName("BlockExport"): sha256_text("T-903:final-export-readiness")
        },
    )


def _complete_internal_bundle_paths() -> set[str]:
    return {
        "authorisation/advisory_approval_trace.json",
        "authorisation/authorisation_evidence.json",
        "controls/control_set.json",
        "controls/control_validation.json",
        "design/design_plan.json",
        "design/design_plan.md",
        "design/design_plan.pdf",
        "environment/derivation_environment.json",
        "events/design_events.json",
        "manifest.json",
        "metadata/export_metadata.json",
        "primers/primers.csv",
        "primers/primers.fasta",
        "screening/screening_verdict.json",
        "sequences/construct.fasta",
        "sequences/construct.gb",
        "sequences/construct.sbol3.ttl",
        "sop/sop_linked_protocol.json",
        "sop/sop_linked_protocol.md",
        "sop/sop_linked_protocol.pdf",
    }
