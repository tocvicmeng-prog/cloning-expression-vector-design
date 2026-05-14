"""
module_id: tests.uat.helpers
file: tests/uat/helpers.py
task_id: T-1301

Shared deterministic harness for the three white-paper-example UAT flows.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

from adapter.catalogue import load_catalogue, schema_for_catalogue
from adapter.io import FastaAdapter, GenBankAdapter, ImportedConstruct, Sbol3Adapter
from adapter.screening import IgscAdapter, ScreeningRequest, ScreeningScope
from adapter.snapgene import SnapGeneFileWatcher
from app.advisory_acknowledgement import (
    AdvisoryAcknowledgementService,
    AdvisoryActionRequest,
    AdvisoryPresentationRequest,
    all_required_advisories_acknowledged,
)
from app.assembly_orchestrator import AssemblyOrchestrationRequest, AssemblyOrchestrator
from app.authorisation_decision import (
    AuthorisationDecisionRequest,
    AuthorisationDecisionService,
    OperationalAuthorisationScope,
)
from app.decision_flow import DECISION_STEP_ORDER, DecisionStep
from app.decision_tree import DecisionTree
from app.design_plan_orchestrator import DesignPlanOrchestrator, DraftDesignBundleRequest
from app.design_service import DesignService
from app.export_orchestrator import (
    ExportBundle,
    ExportBundleRequest,
    ExportOrchestrator,
    ExportSequenceArtefacts,
)
from app.screening_orchestrator import ScreeningOrchestrator, ScreeningRunRequest
from app.sop_protocol_orchestrator import SopProtocolBundleRequest, SopProtocolOrchestrator
from domain.canonicalisation import canonical_sha256
from domain.events import (
    DesignEvent,
    DomainEvent,
    ExportEvent,
    GovernanceEvent,
    HostSelected,
    OperationalProtocolAuthorised,
    RiskAdvisoryAcknowledged,
    ScreeningCompleted,
    SopRendered,
)
from domain.graph import ConstructGraph, GraphNode, NodeId
from domain.ports.profile_signing import AuthorisationProfileVerifier
from domain.security import (
    AdminId,
    AdminPrincipal,
    AuthorisationProfile,
    BiosafetyApprovalId,
    CoveredBiologicalScope,
    ExportClass,
    InstitutionId,
    KeyVersionId,
    OperationalRole,
    PrincipalId,
    ProfileSignature,
    SecurityRole,
    SopLibraryId,
    UnsignedAuthorisationProfileDraft,
    UserDeclaration,
    UserId,
    UserPrincipal,
)
from domain.security import (
    AuthProfileId as SecurityAuthProfileId,
)
from domain.sequence import (
    DnaSequence,
    FeatureV14,
    LocationV14,
    MoleculeType,
    Qualifier,
    SequenceRecord,
    Sha256,
    sha256_text,
)
from domain.types import (
    AssemblyMethodId,
    BiosafetyTier,
    ChassisClass,
    Construct,
    ConstructId,
    DownstreamUse,
    GradedCitation,
    Host,
    HostCompatibilityConstraints,
    HostContext,
    HostId,
    HostRole,
    MarkerId,
    Module,
    ModuleId,
    ModuleLayer,
    OriginId,
    Part,
    PartId,
    SequenceOntologyTerm,
    SlotKind,
)
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
    Semver,
    SopTemplateId,
    UnitsProfile,
    UserOverride,
)
from domain.types.derivation import (
    ScreeningScope as DerivationScreeningScope,
)
from domain.types.governance import DecisionRecord, RoleSnapshot
from domain.types.risk_advisory import RiskAdvisoryReport
from domain.types.signing_errors import ProfileVerificationResult
from domain.types.sop_template import SopTemplate
from engine.assembly import AssemblyPart
from engine.codon import DEFAULT_CODON_USAGE_TABLE, CodingSequenceDesign, ProtectedInterval
from engine.compatibility import CompatibilityChecker, CompatibilityReport
from engine.controls import ControlGenerationInput
from engine.design_plan import DesignPlanInput
from engine.export_gate import activate_final_export_gate, final_export_gate_allows_bundle
from engine.operational_protocol_gate import (
    activate_block_operational_protocol_gate,
    operational_protocol_allows_render,
)
from engine.risk_classification import (
    RiskAdvisoryCatalogue,
    RiskClassificationEngine,
    RiskClassificationInput,
)
from engine.screening_gate import activate_screening_verdict_gates, screening_verdict_allows_export
from engine.session import (
    BLOCK_EXPORT,
    BLOCK_OPERATIONAL_PROTOCOL,
    DesignSession,
    GatePredicateRegistry,
    InMemorySnapshotStore,
    SessionState,
)
from engine.sop_protocol import SopProtocolGenerationRequest, SopProtocolGenerator
from engine.vlp_policy import VlpPolicyReport
from tests.fakes.sop_template.fixtures import (
    admin_principal as sop_admin_principal,
)
from tests.fakes.sop_template.fixtures import (
    signed_template,
    unsigned_template,
)
from tests.fakes.sop_template.signer import FakeSopTemplateSigner

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 5, 14, 14, 0, tzinfo=UTC)
INSTITUTION_ID = InstitutionId("institution-1")
SOP_LIBRARY_ID = SopLibraryId("institutional-sop")
EXPORT_CLASS = ExportClass("internal-review")


@dataclass(frozen=True)
class SelectionIds:
    objective: str
    host: str
    cargo: str
    expression: str
    tagging: str
    cloning_chemistry: str
    biosafety_tier: str

    def by_step(self) -> Mapping[DecisionStep, str]:
        return {
            DecisionStep.OBJECTIVE: self.objective,
            DecisionStep.HOST: self.host,
            DecisionStep.CARGO: self.cargo,
            DecisionStep.EXPRESSION: self.expression,
            DecisionStep.TAGGING: self.tagging,
            DecisionStep.CLONING_CHEMISTRY: self.cloning_chemistry,
            DecisionStep.BIOSAFETY_TIER: self.biosafety_tier,
        }


@dataclass(frozen=True)
class HostFixture:
    host_id: str
    role: HostRole


@dataclass(frozen=True)
class ExampleChecks:
    required_risk_advisory_ids: frozenset[str] = frozenset()
    expected_vlp_blocked_rule_ids: frozenset[str] = frozenset()
    expected_host_roles: frozenset[HostRole] = frozenset()
    dual_control_required: bool = False


@dataclass(frozen=True)
class WhitePaperExample:
    key: str
    title: str
    project_name: str
    selections: SelectionIds
    extra_hosts: tuple[HostFixture, ...]
    host_contexts: tuple[HostFixture, ...]
    assembly_method_id: AssemblyMethodId
    coding_part_id: str
    coding_sequence: str
    assembly_parts: tuple[AssemblyPart, ...]
    biosafety_tier: BiosafetyTier
    host_class: ChassisClass
    downstream_use: DownstreamUse
    control_host_role: str
    control_cargo_classes: tuple[str, ...]
    vector_system_classes: tuple[str, ...]
    intended_readout: str
    risk_trigger_tags: tuple[str, ...]
    risk_cargo_classes: tuple[str, ...]
    risk_vector_system_classes: tuple[str, ...]
    risk_host_roles: tuple[str, ...]
    risk_intended_uses: tuple[str, ...] = ()
    replication_competent: bool = False
    antibiotic_resistance_marker: bool = False
    external_export: bool = False
    vlp_report: VlpPolicyReport | None = None
    compatibility_origin_id: str = "origin.col_e1"
    compatibility_marker_id: str = "marker.kan"
    institutional_protocol_id: str | None = None
    profile_constraints: tuple[str, ...] = ("biosafety_approval_required",)
    checks: ExampleChecks = ExampleChecks()

    @property
    def session_id(self) -> str:
        return f"uat-{self.key}"

    @property
    def fixture_dir(self) -> Path:
        return ROOT / "tests" / "uat" / "fixtures" / self.key


@dataclass(frozen=True)
class ValidationReport:
    findings: tuple[str, ...] = ()
    hard_failures: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    stage: str
    report: ValidationReport


@dataclass(frozen=True)
class UatGateVerdicts:
    screening_export_green: bool
    operational_protocol_green: bool
    final_export_green: bool


@dataclass(frozen=True)
class WhitePaperUatResult:
    example: WhitePaperExample
    export_bundle: ExportBundle
    selected_part_ids: tuple[str, ...]
    host_events: tuple[HostSelected, ...]
    design_events: tuple[DesignEvent, ...]
    governance_events: tuple[GovernanceEvent, ...]
    export_events: tuple[ExportEvent, ...]
    risk_report: RiskAdvisoryReport
    compatibility_report: CompatibilityReport
    validation_results: tuple[ValidationResult, ...]
    gate_verdicts: UatGateVerdicts
    genbank_roundtrip: ImportedConstruct
    snapgene_roundtrip: ImportedConstruct

    @property
    def bundle_hash(self) -> str:
        return str(self.export_bundle.content_hash)

    @property
    def risk_advisory_ids(self) -> frozenset[str]:
        return frozenset(str(advisory.advisory_id) for advisory in self.risk_report.advisories)


@dataclass
class InMemoryDesignEventLog:
    events: dict[str, list[DomainEvent]] = field(default_factory=dict)

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id

    def read_events(self, stream_id: str) -> tuple[DomainEvent, ...]:
        return tuple(self.events.get(stream_id, ()))


@dataclass
class InMemoryGovernanceEventLog:
    events: dict[str, list[GovernanceEvent]] = field(default_factory=dict)

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        if not isinstance(event, GovernanceEvent):
            raise TypeError("governance log only accepts governance events")
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


@dataclass
class InMemoryExportEventLog:
    events: dict[str, list[ExportEvent]] = field(default_factory=dict)

    def append_event(self, stream_id: str, event: ExportEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


@dataclass
class InMemoryProjectStore:
    sessions: dict[str, DesignSession] = field(default_factory=dict)

    def save_session(self, session: DesignSession) -> str:
        self.sessions[session.session_id] = session
        return session.session_id


@dataclass(frozen=True)
class InMemoryCatalogue:
    items: tuple[Mapping[str, object], ...]

    def list_items(self) -> tuple[Mapping[str, object], ...]:
        return self.items


@dataclass
class StableValidationRunner:
    payloads: list[Mapping[str, object]] = field(default_factory=list)

    def validate_design(
        self,
        *,
        session_id: str,
        design_payload: Mapping[str, object],
        rule_registry: Iterable[object],
        derivation_environment_hash: str,
        changed_fields: Iterable[str] | None = None,
    ) -> ValidationResult:
        del session_id, rule_registry, derivation_environment_hash, changed_fields
        self.payloads.append(dict(design_payload))
        return ValidationResult(
            stage=str(design_payload.get("stage", "unknown")),
            report=ValidationReport(),
        )


class AcceptingProfileVerifier:
    def verify(self, profile: AuthorisationProfile) -> ProfileVerificationResult:
        del profile
        return ProfileVerificationResult.ok(None)


@dataclass(frozen=True)
class TemplateReadPort:
    template: SopTemplate

    def get_template(self, template_id: SopTemplateId) -> SopTemplate:
        if template_id != self.template.template_id:
            raise KeyError(str(template_id))
        return self.template

    def list_templates(self) -> tuple[SopTemplate, ...]:
        return (self.template,)


def run_white_paper_example(example: WhitePaperExample, tmp_path: Path) -> WhitePaperUatResult:
    design_log = InMemoryDesignEventLog()
    governance_log = InMemoryGovernanceEventLog()
    export_log = InMemoryExportEventLog()
    design_service = DesignService(
        design_event_log=design_log,
        project_store=InMemoryProjectStore(),
        snapshot_store=InMemorySnapshotStore(),
        clock=_clock(),
    )
    principal = _user_principal()
    tree = DecisionTree(
        part_catalogue=InMemoryCatalogue(_part_items()),
        host_catalogue=InMemoryCatalogue(_host_items()),
        design_service=design_service,
    )

    design_service.create_session(principal, example.session_id, project_name=example.project_name)
    context = tree.new_context(example.session_id)
    selections = example.selections.by_step()
    for step in DECISION_STEP_ORDER:
        if step is DecisionStep.HOST:
            context = tree.advance(principal, context, step, selections[step]).context
            for extra in example.extra_hosts:
                design_service.select_host(
                    principal,
                    example.session_id,
                    host_id=extra.host_id,
                    host_role=extra.role.value,
                )
            continue
        free_text = f"{example.title} acceptance fixture" if step is DecisionStep.CARGO else None
        context = tree.advance(
            principal,
            context,
            step,
            selections[step],
            free_text=free_text,
        ).context

    draft = tree.compileable_construct(context)
    tree.compile_current_design(principal, context)

    validation_runner = StableValidationRunner()
    assembly = AssemblyOrchestrator(validation_runner=validation_runner).orchestrate(
        AssemblyOrchestrationRequest(
            session_id=example.session_id,
            coding_design=CodingSequenceDesign(
                sequence=example.coding_sequence,
                algorithm="avoid_only",
                host_codon_usage=DEFAULT_CODON_USAGE_TABLE,
                protected_intervals=(ProtectedInterval(0, 3, "start-codon"),),
                avoid_motifs=("ACGTACGTACGTACGT", "TTTTCCCCAAAAGGGG"),
            ),
            assembly_parts=example.assembly_parts,
            derivation_environment_hash=str(sha256_text(f"{example.key}:derivation")),
            assembly_method_id=example.assembly_method_id,
            coding_part_id=example.coding_part_id,
            design_payload={"example": example.key, "construct_id": draft.construct_id},
            max_iterations=3,
        )
    )
    if not assembly.converged:
        raise AssertionError("assembly orchestration did not converge")

    compatibility = _compatibility_checker().check(_compatibility_construct(example))
    if not compatibility.passed:
        raise AssertionError(compatibility.canonical_json())

    draft_bundle = DesignPlanOrchestrator(_risk_engine(), event_log=design_log).render_draft_bundle(
        DraftDesignBundleRequest(
            design_session_id=example.session_id,
            actor_id="app.design_plan_orchestrator",
            occurred_at_utc=NOW + timedelta(minutes=10),
            event_id_prefix=f"{example.session_id}.draft",
            design_plan_input=DesignPlanInput(
                design_session_id=example.session_id,
                construct_id=draft.construct_id,
                construct_version="1",
                assembly_plan=assembly.assembly_plan,
                primer_set=_primer_names(assembly.primer_set.pairs),
                biosafety_classification=example.biosafety_tier.value,
                validation_report_hashes=(
                    str(canonical_sha256(tuple(validation_runner.payloads))),
                    str(compatibility.content_hash()),
                ),
                reviewer_notes=(example.title,),
            ),
            control_input=ControlGenerationInput(
                construct_id=draft.construct_id,
                host_role=example.control_host_role,
                assembly_method=str(example.assembly_method_id),
                cargo_classes=example.control_cargo_classes,
                vector_system_classes=example.vector_system_classes,
                intended_readout=example.intended_readout,
                library_size=1,
            ),
            risk_classification_input=RiskClassificationInput(
                design_session_id=example.session_id,
                construct_id=draft.construct_id,
                construct_checksum=assembly.assembly_plan.expected_product.checksum,
                construct_version="1",
                trigger_tags=example.risk_trigger_tags,
                biosafety_tier=example.biosafety_tier.value,
                cargo_classes=example.risk_cargo_classes,
                vector_system_classes=example.risk_vector_system_classes,
                host_roles=example.risk_host_roles,
                intended_uses=example.risk_intended_uses,
                replication_competent=example.replication_competent,
                external_export=example.external_export,
                antibiotic_resistance_marker=example.antibiotic_resistance_marker,
            ),
        )
    )

    advisory_events = _acknowledge_required_advisories(
        draft_bundle.risk_advisory_report,
        governance_log,
        event_prefix=example.session_id,
    )
    acknowledged, missing = all_required_advisories_acknowledged(
        draft_bundle.risk_advisory_report,
        advisory_events,
    )
    if not acknowledged:
        raise AssertionError(f"missing advisory acknowledgements: {sorted(missing)}")

    imported_construct = _imported_construct(
        construct_id=draft.construct_id,
        record=assembly.assembly_plan.expected_product,
        selected_part_ids=draft.selected_part_ids,
    )
    sequence_artefacts = _sequence_artefacts(imported_construct, assembly.primer_set.pairs)

    product_sequence = assembly.assembly_plan.expected_product.sequence
    if not isinstance(product_sequence, DnaSequence):
        raise TypeError("assembled UAT product must be DNA")
    screening_request = ScreeningRequest(
        request_id=f"{example.session_id}.assembled-product",
        sequence=product_sequence,
        session_id=example.session_id,
        construct_id=draft.construct_id,
        construct_checksum=str(assembly.assembly_plan.expected_product.checksum),
        scope=ScreeningScope.ASSEMBLED_PRODUCT,
        realisation_id="assembled-product",
        metadata={"example": example.key},
    )
    screening = ScreeningOrchestrator(
        IgscAdapter.from_catalogues(ROOT / "catalogues", ROOT / "schemas"),
        design_event_log=design_log,
    ).screen_batch(
        ScreeningRunRequest(
            batch_id=f"{example.session_id}.screening",
            requests=(screening_request,),
            event_id=f"{example.session_id}.screening-completed",
            occurred_at_utc=NOW + timedelta(minutes=20),
        )
    )
    if screening.aggregate_verdict.value != "CLEAR":
        raise AssertionError(f"expected CLEAR screening verdict, got {screening.aggregate_verdict}")

    authorisation = AuthorisationDecisionService(
        design_event_log=design_log,
        profile_verifier=cast(AuthorisationProfileVerifier, AcceptingProfileVerifier()),
    ).decide(
        AuthorisationDecisionRequest(
            design_session_id=example.session_id,
            event_id=f"{example.session_id}.authorised",
            occurred_at_utc=NOW + timedelta(minutes=30),
            actor_id="app.authorisation_decision",
            screening_event=screening.event,
            user_declaration=_user_declaration(),
            authorisation_profile=_authorisation_profile(example),
            requested_scope=_authorisation_scope(example),
            risk_advisory_report=draft_bundle.risk_advisory_report,
            governance_events=advisory_events,
        )
    )
    if not authorisation.allowed or authorisation.authorised_event is None:
        raise AssertionError(f"authorisation blocked: {authorisation.blocked_by}")

    sop_bundle = SopProtocolOrchestrator(
        SopProtocolGenerator(TemplateReadPort(_signed_sop_template())),
        design_event_log=design_log,
    ).render_sop_bundle(
        SopProtocolBundleRequest(
            design_session_id=example.session_id,
            actor_id="app.sop_protocol_orchestrator",
            occurred_at_utc=NOW + timedelta(minutes=40),
            event_id_prefix=f"{example.session_id}.sop",
            generation_request=SopProtocolGenerationRequest(
                construct_id=draft.construct_id,
                template_id=SopTemplateId("sop-template-1"),
                observed_design_events=(authorisation.authorised_event,),
                assembly_method=str(example.assembly_method_id),
                host_id=example.selections.host,
                biosafety_tier=example.biosafety_tier.value,
            ),
        )
    )

    design_events = _design_events(design_log, example.session_id)
    export_bundle = ExportOrchestrator(export_event_log=export_log).create_bundle(
        ExportBundleRequest(
            bundle_id=f"{example.session_id}.bundle",
            design_session_id=example.session_id,
            institution_id=str(INSTITUTION_ID),
            actor_id="user-1",
            occurred_at_utc=NOW + timedelta(minutes=50),
            export_profile=ExportProfile.INTERNAL_AUDIT,
            derivation_environment=_environment(
                example=example,
                construct_checksum=assembly.assembly_plan.expected_product.checksum,
                authorisation_event=authorisation.authorised_event,
                draft_bundle_hash=draft_bundle.content_hash,
                sop_bundle_hash=sop_bundle.content_hash,
                advisory_events=advisory_events,
            ),
            draft_design_bundle=draft_bundle,
            sop_protocol_bundle=sop_bundle,
            screening_event=screening.event,
            authorisation_event=authorisation.authorised_event,
            sop_rendered_event=sop_bundle.sop_rendered_event,
            sequence_artefacts=sequence_artefacts,
            advisory_governance_events=advisory_events,
            design_events=design_events,
            event_id_prefix=f"{example.session_id}.export",
        )
    )

    gate_verdicts = _gate_verdicts(
        example.session_id,
        screening.event,
        authorisation.authorised_event,
        sop_bundle.sop_rendered_event,
    )
    genbank_roundtrip = GenBankAdapter().read(sequence_artefacts.genbank)
    snapgene_roundtrip = _snapgene_roundtrip(
        sequence_artefacts.genbank,
        tmp_path / f"{example.key}-snapgene",
    )

    return WhitePaperUatResult(
        example=example,
        export_bundle=export_bundle,
        selected_part_ids=draft.selected_part_ids,
        host_events=tuple(event for event in design_events if isinstance(event, HostSelected)),
        design_events=design_events,
        governance_events=advisory_events,
        export_events=tuple(export_log.events.get(str(INSTITUTION_ID), ())),
        risk_report=draft_bundle.risk_advisory_report,
        compatibility_report=compatibility,
        validation_results=_validation_results(assembly.validation_results),
        gate_verdicts=gate_verdicts,
        genbank_roundtrip=genbank_roundtrip,
        snapgene_roundtrip=snapgene_roundtrip,
    )


def assert_common_acceptance(result: WhitePaperUatResult) -> None:
    assert result.bundle_hash == expected_bundle_hash(result.example)
    assert result.gate_verdicts.screening_export_green
    assert result.gate_verdicts.operational_protocol_green
    assert result.gate_verdicts.final_export_green
    assert result.compatibility_report.passed
    assert all(not item.report.hard_failures for item in result.validation_results)
    assert _event_types(result.design_events)[-3:] == (
        "ScreeningCompleted",
        "OperationalProtocolAuthorised",
        "SopRendered",
    )
    assert {
        "AdvisoryWarningPresented",
        "RiskAdvisoryAcknowledged",
    } <= set(_event_types(result.governance_events))
    assert _event_types(result.export_events) == (
        "ExportProfileRedactionApplied",
        "ExportBundleCreated",
    )
    assert result.genbank_roundtrip.features
    assert result.snapgene_roundtrip.features
    assert result.selected_part_ids == _fixture_selected_part_ids(result.example)
    assert _host_payload(result.host_events) == _fixture_host_events(result.example)


def expected_bundle_hash(example: WhitePaperExample) -> str:
    path = example.fixture_dir / "expected_bundle_hash.txt"
    return path.read_text(encoding="utf-8").strip()


def _validation_results(items: Iterable[object]) -> tuple[ValidationResult, ...]:
    results: list[ValidationResult] = []
    for item in items:
        if not isinstance(item, ValidationResult):
            raise TypeError("assembly validation hook returned an unexpected result type")
        results.append(item)
    return tuple(results)


def _clock() -> Callable[[], datetime]:
    counter = 0

    def next_time() -> datetime:
        nonlocal counter
        counter += 1
        return NOW + timedelta(seconds=counter)

    return next_time


def _user_principal() -> UserPrincipal:
    return UserPrincipal(
        id=PrincipalId("user-1"),
        role=SecurityRole.USER,
        institution=INSTITUTION_ID,
        credentials_verified_at=NOW,
    )


def _admin_principal() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=INSTITUTION_ID,
        credentials_verified_at=NOW,
    )


def _decision_record(seed: str) -> DecisionRecord:
    return DecisionRecord(
        decision_id=f"decision-{seed}",
        decision_type="risk_advisory_acknowledgement",
        role_snapshot=RoleSnapshot(
            principal_id=PrincipalId("admin-1"),
            role=SecurityRole.ADMINISTRATOR,
            institution_id=str(INSTITUTION_ID),
            captured_at_utc=NOW,
            credentials_verified_at_utc=NOW,
        ),
        profile_content_hash=sha256_text("uat-profile"),
        policy_version="policy-v1",
        signed_payload_hash=sha256_text(f"payload:{seed}"),
        signature_bytes=b"uat-signature",
        signed_at_utc=NOW,
    )


def _acknowledge_required_advisories(
    report: RiskAdvisoryReport,
    event_log: InMemoryGovernanceEventLog,
    *,
    event_prefix: str,
) -> tuple[GovernanceEvent, ...]:
    service = AdvisoryAcknowledgementService(event_log)
    presentation = service.present(
        AdvisoryPresentationRequest(
            report=report,
            recipient=_admin_principal(),
            presenting_surface="uat-harness==T-1301",
            occurred_at_utc=NOW + timedelta(minutes=11),
            event_id=f"{event_prefix}.advisory-presented",
        )
    )
    for index, advisory_id in enumerate(sorted(report.required_acknowledgements()), start=1):
        service.acknowledge(
            AdvisoryActionRequest(
                report=report,
                advisory_id=advisory_id,
                actor=_admin_principal(),
                presentation_event=presentation,
                justification=(
                    "Administrator and scientific advisor reviewed this UAT example against "
                    "the signed institutional fixture."
                ),
                decision_record=_decision_record(f"{event_prefix}.ack.{index}"),
                occurred_at_utc=NOW + timedelta(minutes=12, seconds=index),
                event_id=f"{event_prefix}.advisory-ack-{index}",
            )
        )
    return tuple(event_log.events[str(INSTITUTION_ID)])


def _user_declaration() -> UserDeclaration:
    return UserDeclaration(
        declared_at=NOW + timedelta(minutes=25),
        declared_by=UserId("user-1"),
        sop_library_id=SOP_LIBRARY_ID,
        biosafety_approval_id=BiosafetyApprovalId("IBC-2026-UAT-001"),
        role_of_operation=OperationalRole.DESIGNER,
        intended_export_class=EXPORT_CLASS,
        intended_vendor_submission=False,
    )


def _authorisation_profile(example: WhitePaperExample) -> AuthorisationProfile:
    draft = UnsignedAuthorisationProfileDraft(
        profile_id=SecurityAuthProfileId(f"profile-{example.key}"),
        subject_user_id=UserId("user-1"),
        issued_by_admin_id=AdminId("admin-1"),
        issuer_principal_id=PrincipalId("admin-1"),
        institution=INSTITUTION_ID,
        profile_version=1,
        valid_from=NOW - timedelta(days=1),
        valid_until=NOW + timedelta(days=365),
        covered_scope=CoveredBiologicalScope(
            covered_biosafety_tiers=frozenset(
                {BiosafetyTier.BSL_1, BiosafetyTier.BSL_2, BiosafetyTier.BSL_2_PLUS}
            ),
            covered_host_classes=frozenset(
                {ChassisClass.BACTERIAL, ChassisClass.MAMMALIAN, ChassisClass.PLANT}
            ),
            covered_assembly_chemistries=frozenset(
                {
                    AssemblyMethodId("gibson"),
                    AssemblyMethodId("golden-gate"),
                    AssemblyMethodId("moclo"),
                }
            ),
            covered_downstream_uses=frozenset(
                {DownstreamUse.EXPRESSION, DownstreamUse.VLP_OR_PHAGE_DISPLAY}
            ),
            covered_sop_libraries=frozenset({SOP_LIBRARY_ID}),
            covered_vendor_submission=False,
            covered_export_classes=frozenset({EXPORT_CLASS}),
            role_of_operation_allowed=frozenset({OperationalRole.DESIGNER}),
            institutional_protocol_ids=frozenset(
                item for item in (example.institutional_protocol_id,) if item is not None
            ),
        ),
        additional_constraints=example.profile_constraints,
    )
    return AuthorisationProfile.from_draft(
        draft,
        ProfileSignature(
            signed_payload_hash=draft.content_hash(),
            signature_bytes=b"uat-profile-signature",
            signing_key_version=KeyVersionId("profile-uat-key-v1"),
            signed_at_utc=NOW,
        ),
    )


def _authorisation_scope(example: WhitePaperExample) -> OperationalAuthorisationScope:
    return OperationalAuthorisationScope(
        biosafety_tier=example.biosafety_tier,
        host_class=example.host_class,
        assembly_chemistry=example.assembly_method_id,
        downstream_use=example.downstream_use,
        sop_library_id=SOP_LIBRARY_ID,
        export_class=EXPORT_CLASS,
        vendor_submission=False,
        role_of_operation=OperationalRole.DESIGNER,
        cargo_classes=frozenset(example.risk_cargo_classes),
        vector_system_classes=frozenset(example.risk_vector_system_classes),
        insert_size_bp=len(example.coding_sequence),
        institutional_protocol_id=example.institutional_protocol_id,
    )


def _signed_sop_template() -> SopTemplate:
    template = unsigned_template()
    signature = FakeSopTemplateSigner().sign(template, sop_admin_principal())
    return signed_template(signature)


def _risk_engine() -> RiskClassificationEngine:
    path = ROOT / "catalogues" / "risk_advisories.yaml"
    payload = load_catalogue(path, schema_for_catalogue(path, ROOT / "schemas")).payload
    return RiskClassificationEngine(RiskAdvisoryCatalogue.from_payload(payload))


def _sequence_artefacts(
    construct: ImportedConstruct,
    primer_pairs: Iterable[Any],
) -> ExportSequenceArtefacts:
    genbank = GenBankAdapter().write(construct).data
    fasta = FastaAdapter().write(construct).data
    sbol3 = Sbol3Adapter().write(construct).data
    primer_rows = ["name,sequence,direction"]
    primer_fasta: list[str] = []
    for pair in primer_pairs:
        for primer in (pair.forward, pair.reverse):
            primer_rows.append(f"{primer.name},{primer.sequence},{primer.direction}")
            primer_fasta.extend((f">{primer.name}", primer.sequence))
    return ExportSequenceArtefacts(
        genbank=genbank,
        fasta=fasta,
        sbol3=sbol3,
        primer_csv=("\n".join(primer_rows) + "\n").encode("utf-8"),
        primer_fasta=("\n".join(primer_fasta) + "\n").encode("utf-8"),
    )


def _imported_construct(
    *,
    construct_id: str,
    record: SequenceRecord,
    selected_part_ids: tuple[str, ...],
) -> ImportedConstruct:
    length = len(record.sequence.body)
    third = max(1, length // 3)
    features = (
        _feature(record.id, "promoter", 0, third, selected_part_ids[1]),
        _feature(record.id, "CDS", third, min(length, third * 2), selected_part_ids[0]),
        _feature(record.id, "terminator", min(length, third * 2), length, selected_part_ids[2]),
    )
    return ImportedConstruct(
        construct_id=construct_id,
        sequence_record=record,
        features=features,
        source_format="uat-fixture",
        source_metadata={"task_id": "T-1301"},
    )


def _feature(
    parent_id: str,
    role: str,
    start: int,
    end: int,
    label: str,
) -> FeatureV14:
    return FeatureV14(
        role=role,
        qualifiers=(
            Qualifier(
                namespace="genbank",
                key="label",
                value=label,
                value_type="string",
                order=0,
            ),
        ),
        locations=(LocationV14(start=start, end=end, strand="+", phase="."),),
        parent_sequence_id=parent_id,
    )


def _snapgene_roundtrip(source: bytes, root: Path) -> ImportedConstruct:
    watch_dir = root / "input"
    output_dir = root / "output"
    watch_dir.mkdir(parents=True, exist_ok=True)
    source_path = watch_dir / "construct.gb"
    source_path.write_bytes(source)
    watcher = SnapGeneFileWatcher(watch_dir, output_dir, debounce_ms=0)
    watcher.record_write(source_path, timestamp_ms=0)
    results = watcher.flush_ready(now_ms=1)
    if len(results) != 1:
        raise AssertionError("SnapGene file-watch fallback did not emit one result")
    return GenBankAdapter().read(results[0].output_path.read_bytes())


def _gate_verdicts(
    session_id: str,
    screening_event: ScreeningCompleted,
    authorisation_event: OperationalProtocolAuthorised,
    sop_event: SopRendered,
) -> UatGateVerdicts:
    screening_session = DesignSession(
        session_id=session_id,
        screening_verdict=dict(screening_event.verdict_payload)["verdict"],
    )
    screening_registry = activate_screening_verdict_gates(
        GatePredicateRegistry.with_pending_defaults()
    )
    authorised_session = DesignSession(
        session_id=session_id,
        screening_verdict=dict(screening_event.verdict_payload)["verdict"],
        authorisation_profile_id=authorisation_event.profile_id,
        decision_record_hash=authorisation_event.decision_record_hash,
    )
    operational_registry = activate_block_operational_protocol_gate(
        GatePredicateRegistry.with_pending_defaults()
    )
    export_session = DesignSession(
        session_id=session_id,
        state=SessionState.READY_TO_EXPORT,
        screening_verdict=dict(screening_event.verdict_payload)["verdict"],
        authorisation_profile_id=authorisation_event.profile_id,
        decision_record_hash=authorisation_event.decision_record_hash,
        sop_bundle_hash=sop_event.sop_bundle_hash,
    )
    export_registry = activate_final_export_gate(
        activate_screening_verdict_gates(GatePredicateRegistry.with_pending_defaults())
    )
    return UatGateVerdicts(
        screening_export_green=screening_verdict_allows_export(
            screening_registry.verdict(BLOCK_EXPORT, screening_session)
        ),
        operational_protocol_green=operational_protocol_allows_render(
            operational_registry.verdict(BLOCK_OPERATIONAL_PROTOCOL, authorised_session)
        ),
        final_export_green=final_export_gate_allows_bundle(
            export_registry.verdict(BLOCK_EXPORT, export_session)
        ),
    )


def _environment(
    *,
    example: WhitePaperExample,
    construct_checksum: Sha256,
    authorisation_event: OperationalProtocolAuthorised,
    draft_bundle_hash: Sha256,
    sop_bundle_hash: Sha256,
    advisory_events: tuple[GovernanceEvent, ...],
) -> DerivationEnvironment:
    return DerivationEnvironment(
        rule_registry_version=Semver("1.0.0"),
        rule_manifest_hashes={"MR": sha256_text("uat-rule-manifest")},
        catalogue_versions={CatalogueId("parts"): Semver("2026.5.14")},
        catalogue_content_hashes={CatalogueId("parts"): sha256_text("uat-parts")},
        plugin_versions={PluginId("codon"): Semver("1.0.0")},
        plugin_configurations={PluginId("codon"): sha256_text(example.key)},
        external_database_versions={DatabaseId("rebase"): "2026-05"},
        sop_template_versions={SopTemplateId("sop-template-1"): Semver("1.0.0")},
        container_image_digest=ContainerDigest("sha256:uat-container"),
        cpu_arch="x86_64",
        locale="C.UTF-8",
        units_profile=UnitsProfile("si-v1"),
        rounding_policy=RoundingPolicy("half-even-6dp"),
        random_seeds={RandomSeedId("uat"): 1301},
        optimisation_settings=OptimisationSettings(
            strategy="deterministic-uat",
            objective_weights=(("traceability", Decimal("1.0")),),
            max_iterations=3,
        ),
        user_overrides=(
            UserOverride(
                override_id=f"{example.key}.fixture",
                path="/uat/example",
                value=example.key,
                reason="T-1301 deterministic UAT fixture",
            ),
        ),
        reviewer_decisions=(
            ReviewerDecision(
                decision_id=f"{example.key}.scientific-advisor-signoff",
                reviewer_id="scientific-advisor",
                decision_type="approve",
                decision_content_hash=sha256_text(
                    (example.fixture_dir / "scientific_advisor_signoff.json").read_text(
                        encoding="utf-8"
                    )
                ),
            ),
        ),
        construct_checksum=construct_checksum,
        authorisation_profile_id=AuthProfileId(authorisation_event.profile_id),
        authorisation_profile_content_hash=sha256_text("uat-authorisation-profile"),
        sop_template_content_hashes={SopTemplateId("sop-template-1"): sha256_text("uat-sop")},
        screening_provider_trust_policy_version=Semver("1.0.0"),
        screening_query_scope=DerivationScreeningScope.ASSEMBLED_PRODUCT,
        screening_threshold_policy_version=Semver("1.0.0"),
        screening_submitted_sequence_hash=construct_checksum,
        plugin_package_hashes={PluginId("codon"): sha256_text("uat-plugin-package")},
        llm_prompt_template_versions={PromptTemplateId("advisory"): Semver("1.0.0")},
        llm_model_identifiers={LLMUseSite("advisory_text"): LLMModelIdentifier("none")},
        institutional_policy_version=Semver("2026.05"),
        user_declaration_hash=sha256_text("uat-user-declaration"),
        export_profile=ExportProfile.INTERNAL_AUDIT,
        redaction_policy_version=Semver("1.0.0"),
        risk_advisory_catalogue_version=Semver("2026.05"),
        risk_advisory_catalogue_content_hash=sha256_text("uat-risk-catalogue"),
        privacy_classification=PrivacyClassification.SENSITIVE,
        advisory_approval_trace_hash=canonical_sha256(
            tuple(event.canonical_json() for event in advisory_events)
        ),
        advisory_acknowledgement_event_ids=tuple(
            event.event_id
            for event in advisory_events
            if isinstance(event, RiskAdvisoryAcknowledged)
        ),
        gate_predicate_versions={
            GateName("BlockExport"): PredicateVersion("1.0.0-t903-final-export-readiness")
        },
        gate_predicate_content_hashes={
            GateName("BlockExport"): sha256_text("T-903:final-export-readiness"),
            GateName("DraftDesignBundle"): draft_bundle_hash,
            GateName("SopProtocolBundle"): sop_bundle_hash,
        },
    )


def _part_items() -> tuple[Mapping[str, object], ...]:
    return (
        _part_item("cargo.enzyme_a.egfp", "EGFP-tagged Enzyme A", "reporter_cds", "bacterial"),
        _part_item("promoter.t7", "T7 promoter", "promoter", "bacterial"),
        _part_item("tag.his6_tev", "His6-TEV tag", "protein_tag", "bacterial"),
        _part_item(
            "cargo.crispri_krab_sgrna",
            "CRISPRi KRAB guide cassette",
            "crispr_guide_scaffold",
            "mammalian",
        ),
        _part_item("promoter.ef1a", "EF1a promoter", "promoter", "mammalian"),
        _part_item(
            "tag.nls",
            "Nuclear localisation signal",
            "nuclear_localisation_signal",
            "mammalian",
        ),
        _part_item("cargo.plant_egfp", "Plant EGFP reporter", "reporter_cds", "plant"),
        _part_item("promoter.35s", "CaMV 35S promoter", "promoter", "plant"),
        _part_item("tag.ha", "HA epitope tag", "protein_tag", "plant"),
    )


def _part_item(part_id: str, name: str, role: str, *hosts: str) -> Mapping[str, object]:
    return {
        "citation": {"url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#18"},
        "host_compatibility": list(hosts),
        "id": part_id,
        "name": name,
        "role_label": role,
    }


def _host_items() -> tuple[Mapping[str, object], ...]:
    citation = {"url": "Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md#18"}
    return (
        {
            "biosafety_tier": "BSL-1",
            "chassis_class": "bacterial",
            "citation": citation,
            "host_roles": ["expression", "protein_expression"],
            "id": "host.ecoli_bl21_de3",
            "name": "E. coli BL21(DE3)",
        },
        {
            "biosafety_tier": "BSL-2",
            "chassis_class": "mammalian",
            "citation": citation,
            "host_roles": ["producer"],
            "id": "host.hek293t_producer",
            "name": "HEK293T producer cells",
        },
        {
            "biosafety_tier": "BSL-1",
            "chassis_class": "plant",
            "citation": citation,
            "host_roles": ["target"],
            "id": "host.n_benthamiana",
            "name": "N. benthamiana",
        },
    )


def _compatibility_checker() -> CompatibilityChecker:
    hosts = (
        _host("host.ecoli_bl21_de3", ChassisClass.BACTERIAL),
        _host("host.ecoli_k12", ChassisClass.BACTERIAL),
        _host("host.agrobacterium_gv3101", ChassisClass.BACTERIAL),
        _host("host.hek293t_producer", ChassisClass.MAMMALIAN),
        _host("host.hek293t_target", ChassisClass.MAMMALIAN),
        _host("host.n_benthamiana", ChassisClass.PLANT),
    )
    return CompatibilityChecker(
        host_catalogue={host.id: host for host in hosts},
        constraints={
            HostRole.CLONING_PROPAGATION: _constraint(
                HostRole.CLONING_PROPAGATION,
                ChassisClass.BACTERIAL,
            ),
            HostRole.DELIVERY: _constraint(HostRole.DELIVERY, ChassisClass.BACTERIAL),
            HostRole.PRODUCER: _constraint(HostRole.PRODUCER, ChassisClass.MAMMALIAN),
            HostRole.EXPRESSION: _constraint(
                HostRole.EXPRESSION,
                ChassisClass.BACTERIAL,
                ChassisClass.MAMMALIAN,
                ChassisClass.PLANT,
            ),
            HostRole.TARGET: _constraint(
                HostRole.TARGET,
                ChassisClass.MAMMALIAN,
                ChassisClass.PLANT,
            ),
        },
    )


def _host(host_id: str, chassis: ChassisClass) -> Host:
    return Host(
        id=HostId(host_id),
        name=host_id.replace("host.", "").replace("_", " "),
        chassis=chassis,
        genotype="T-1301 deterministic host fixture",
        compatible_origins=frozenset({OriginId("origin.col_e1"), OriginId("origin.binary")}),
        compatible_markers=frozenset({MarkerId("marker.kan"), MarkerId("marker.hyg")}),
        expression_features=frozenset(),
        codon_usage_table=f"{host_id}.codon",
        growth_conditions="fixture-only",
        biosafety_tier=(
            BiosafetyTier.BSL_1 if chassis is not ChassisClass.MAMMALIAN else BiosafetyTier.BSL_2
        ),
        references=(_citation(),),
    )


def _constraint(role: HostRole, *allowed: ChassisClass) -> HostCompatibilityConstraints:
    return HostCompatibilityConstraints(role=role, allowed_chassis=frozenset(allowed))


def _compatibility_construct(example: WhitePaperExample) -> Construct:
    record = SequenceRecord(
        id=f"{example.key}.compatibility",
        sequence=DnaSequence("GCTGACGAATTCGGTACC"),
        topology="linear",
        molecule_type=MoleculeType.DS_DNA,
    )
    graph = ConstructGraph(
        nodes=(GraphNode(id=NodeId("construct-root"), kind="part", payload=example.key),),
        edges=(),
        topology="linear",
        sequence_record=record,
    )
    return Construct(
        id=ConstructId(f"construct.{example.key}.compatibility"),
        version="1.0.0",
        modules=(
            _module(
                "module.origin",
                ModuleLayer.PROPAGATION,
                _part(example.compatibility_origin_id, "origin"),
            ),
            _module(
                "module.marker",
                ModuleLayer.PROPAGATION,
                _part(example.compatibility_marker_id, "selection_marker"),
            ),
            _module("module.cargo", ModuleLayer.CARGO, _part(example.selections.cargo, "cargo")),
        ),
        graph=graph,
        hosts=tuple(
            HostContext(role=fixture.role, host_id=HostId(fixture.host_id))
            for fixture in example.host_contexts
        ),
        biosafety_tier=example.biosafety_tier,
        downstream_use=example.downstream_use,
        feature_table=graph.feature_table,
        sbol_record=None,
        checksum=graph.sequence_record.checksum,
        provenance="T-1301 fixture",
    )


def _module(module_id: str, layer: ModuleLayer, part: Part) -> Module:
    return Module(
        id=ModuleId(module_id),
        layer=layer,
        slot_kind=SlotKind.REQUIRED,
        parts=(part,),
    )


def _part(part_id: str, role: str) -> Part:
    sequence = DnaSequence("GCTGACGAATTC")
    return Part(
        id=PartId(part_id),
        name=part_id,
        role=SequenceOntologyTerm(role),
        sequence=sequence,
        annotations=(),
        parent=None,
        licence="Apache-2.0",
        provenance="T-1301 fixture",
        checksum=sha256_text(sequence.body),
    )


def _citation() -> GradedCitation:
    return GradedCitation(
        text="T-1301 UAT fixture citation",
        grade="B2",
        accessed=NOW.date(),
        url="Cloning_Expression_Vector_Design_White_Paper.md",
    )


def _primer_names(pairs: Iterable[Any]) -> tuple[str, ...]:
    names: list[str] = []
    for pair in pairs:
        names.extend((str(pair.forward.name), str(pair.reverse.name)))
    return tuple(names)


def _design_events(log: InMemoryDesignEventLog, session_id: str) -> tuple[DesignEvent, ...]:
    return tuple(event for event in log.read_events(session_id) if isinstance(event, DesignEvent))


def _event_types(events: Iterable[DomainEvent]) -> tuple[str, ...]:
    return tuple(event.event_type for event in events)


def _host_payload(host_events: tuple[HostSelected, ...]) -> list[dict[str, str]]:
    return [{"host_id": event.host_id, "role": event.host_role} for event in host_events]


def _fixture_input_parts(example: WhitePaperExample) -> Mapping[str, object]:
    return _load_json_object(example.fixture_dir / "input_parts.json")


def _fixture_host_context(example: WhitePaperExample) -> Mapping[str, object]:
    return _load_json_object(example.fixture_dir / "host_context.json")


def _fixture_selected_part_ids(example: WhitePaperExample) -> tuple[str, ...]:
    raw = _fixture_input_parts(example).get("selected_part_ids")
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise TypeError("selected_part_ids must be a list of strings")
    return tuple(raw)


def _fixture_host_events(example: WhitePaperExample) -> list[dict[str, str]]:
    raw = _fixture_host_context(example).get("host_events")
    if not isinstance(raw, list):
        raise TypeError("host_events must be a list")
    events: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise TypeError("host_events entries must be JSON objects")
        host_id = item.get("host_id")
        role = item.get("role")
        if not isinstance(host_id, str) or not isinstance(role, str):
            raise TypeError("host_events entries must include string host_id and role")
        events.append({"host_id": host_id, "role": role})
    return events


def _load_json_object(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return cast(Mapping[str, object], payload)


def coding_sequence(seed: str, codon_count: int) -> str:
    codons = (
        "ATG",
        "GCT",
        "GAC",
        "GAA",
        "TTC",
        "CAG",
        "AAA",
        "CTG",
        "GGT",
        "ACC",
        "TGG",
        "GCA",
        "GAT",
        "GCC",
        "AAG",
        "TAT",
    )
    offset = sum(ord(char) for char in seed) % len(codons)
    body = [codons[(offset + index) % len(codons)] for index in range(codon_count)]
    body[0] = "ATG"
    body[-1] = "TAA"
    return "".join(body)


def fixed_part(part_id: str, sequence: str, *, annotations: tuple[str, ...] = ()) -> AssemblyPart:
    return AssemblyPart(id=part_id, sequence=sequence, annotations=annotations)
