"""
module_id: tests.uat.adversarial.helpers
file: tests/uat/adversarial/helpers.py
task_id: T-1302

Shared deterministic harness for Phase 13 adversarial UAT scenarios.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Literal, cast
from zipfile import ZipFile

from adapter.ipc import AuditServiceClient, InProcessAuditServiceTransport
from adapter.persistence import (
    AuditLogTamperDetectionUnavailable,
    AuthorisationProfileNotFoundError,
    AuthorisationProfileTamperDetectedError,
    JsonlEventLog,
    SqliteAuditLog,
    SqliteAuthorisationStoreRead,
    SqliteAuthorisationStoreWrite,
)
from app.admin_action_handler import AdminActionHandler
from app.advisory_acknowledgement import (
    AdvisoryAcknowledgementService,
    AdvisoryActionRequest,
    AdvisoryPresentationRequest,
    all_required_advisories_acknowledged,
)
from app.authorisation_decision import AuthorisationDecisionService
from app.export_orchestrator import ExportOrchestrator
from app.plugin_governance import PluginGovernanceService
from domain.events import (
    DomainEvent,
    EventStream,
    GovernanceEvent,
    RiskAdvisoryAcknowledged,
)
from domain.security import (
    AdminPrincipal,
    DualControlFlags,
    InstitutionId,
    PrincipalId,
    SecurityRole,
    ServiceName,
    UserId,
)
from domain.types import BiosafetyTier
from domain.types.admin_ipc import AdminIpcErrorCode, AdminIpcStatus
from domain.types.derivation import ExportProfile
from domain.types.review_queue import ReviewQueueStatus
from domain.types.risk_advisory import RiskAdvisoryReport
from domain.types.signing_errors import SopTemplateTamperDetectedError
from engine.session import ReplayIntegrityFailure, replay_design_events
from engine.sop_protocol import SopProtocolGenerator
from tests.adapter.persistence.test_sqlite_audit_log import _seed_audit_rows
from tests.adapter.persistence.test_sqlite_authorisation_store_read import (
    _seed_profile,
    _signed_profile_json,
)
from tests.app.admin_action_handler.test_admin_action_handler import (
    _bootstrap_principal,
    _developer_principal,
    _reviewer_principal,
    _user_principal,
)
from tests.app.admin_action_handler.test_admin_action_handler import (
    _handler as _admin_handler_stack,
)
from tests.app.review_queue.helpers import (
    admin_resolution_stack,
    requested_scope,
    review_queue_stack,
)
from tests.app.review_queue.helpers import (
    service_principal as review_queue_service_principal,
)
from tests.app.test_authorisation_decision_t806b import (
    MemoryDesignEventLog,
    _acknowledged_advisory_events,
    _admin,
    _advisory_bypass_events,
    _decision_record,
    _presentation_request,
    _report,
    _requested_scope,
    _screening_completed,
)
from tests.app.test_authorisation_decision_t806b import (
    _request as _authorisation_request,
)
from tests.app.test_export_orchestrator_t903 import (
    _CapturingExportLog,
)
from tests.app.test_export_orchestrator_t903 import (
    _request as _export_request,
)
from tests.app.test_plugin_governance_t808 import (
    _request as _plugin_request,
)
from tests.app.test_plugin_governance_t808 import (
    _write_manifest,
)
from tests.engine.session.test_replay_determinism import (
    BASE_TIME,
    _reviewer_event,
    _session_events,
)
from tests.engine.sop_protocol.test_sop_protocol_t803 import (
    FakeTemplateReadPort,
)
from tests.engine.sop_protocol.test_sop_protocol_t803 import (
    _request as _sop_request,
)
from tests.fakes.security.audit_append.brokers import AuditChainRow, FakeAdminAuditBroker
from tests.fakes.security.audit_key.provider import TestAuditKeyProvider
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    unsigned_profile_draft,
)
from tests.fakes.security.profile_signing.signers import FakeProfileSigner, FakeProfileVerifier
from tests.fakes.sop_template.fixtures import unsigned_template
from tests.interface.admin_service.helpers import NOW as ADMIN_SERVICE_NOW
from tests.interface.admin_service.helpers import harness, token
from tests.security.audit_service_helpers import (
    AuditServiceFixture,
    audit_entry,
    bad_token_provider,
)
from tests.security.audit_service_helpers import (
    service_principal as audit_service_principal,
)
from tools.ci_gates.no_direct_admin_handler_import_check import (
    direct_admin_handler_import_violations,
)

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
NOW = datetime(2026, 5, 14, tzinfo=UTC)
Verdict = Literal["blocked", "accepted"]


@dataclass(frozen=True)
class AdversarialScenarioResult:
    scenario: str
    verdict: Verdict
    blocked_by: tuple[str, ...] = ()
    event_types: tuple[str, ...] = ()
    audit_event_types: tuple[str, ...] = ()
    authorised_event_emitted: bool = False
    notes: tuple[str, ...] = ()


ScenarioRunner = Callable[[Path], AdversarialScenarioResult]


def run_scenario(scenario: str, tmp_path: Path) -> AdversarialScenarioResult:
    runners: dict[str, ScenarioRunner] = {
        "self_elevation": run_self_elevation,
        "advisory_bypass": run_advisory_bypass,
        "reviewer_escalation": run_reviewer_escalation,
        "unsupported_tier": run_unsupported_tier,
        "plugin_trust": run_plugin_trust,
        "export_leak": run_export_leak,
        "audit_key_absent": run_audit_key_absent,
        "audit_key_compromise": run_audit_key_compromise,
        "replay_integrity": run_replay_integrity,
        "construct_checksum_mismatch": run_construct_checksum_mismatch,
        "programmatic_event_bypass": run_programmatic_event_bypass,
        "profile_tamper": run_profile_tamper,
        "sop_template_tamper": run_sop_template_tamper,
        "governance_reference_only_rejected": run_governance_reference_only_rejected,
        "review_queue_blocked_path": run_review_queue_blocked_path,
        "developer_post_bootstrap_denied": run_developer_post_bootstrap_denied,
        "admin_service_unauthenticated": run_admin_service_unauthenticated,
        "dual_control_same_admin_rejected": run_dual_control_same_admin_rejected,
        "dual_control_two_admins_accepted": run_dual_control_two_admins_accepted,
        "dual_control_advisory_signoff_pair_required": (
            run_dual_control_advisory_signoff_pair_required
        ),
        "audit_service_dual_writer_chain_integrity": (
            run_audit_service_dual_writer_chain_integrity
        ),
        "admin_command_direct_handler_import_rejected": (
            run_admin_command_direct_handler_import_rejected
        ),
    }
    scenario_path = tmp_path / scenario
    scenario_path.mkdir(parents=True, exist_ok=True)
    return runners[scenario](scenario_path)


def assert_scenario_matches_fixture(result: AdversarialScenarioResult) -> None:
    expected = _load_expected(result.scenario)
    assert result.scenario == _expected_str(expected, "scenario")
    assert result.verdict == _expected_str(expected, "verdict")
    assert result.authorised_event_emitted is _expected_bool(
        expected,
        "authorised_event_emitted",
    )
    _assert_contains(result.blocked_by, _expected_str_tuple(expected, "blocked_by_contains"))
    _assert_contains(result.event_types, _expected_str_tuple(expected, "event_types_contains"))
    _assert_contains(
        result.audit_event_types,
        _expected_str_tuple(expected, "audit_event_types_contains"),
    )
    _assert_contains(result.notes, _expected_str_tuple(expected, "notes_contains"))


def run_self_elevation(tmp_path: Path) -> AdversarialScenarioResult:
    handler, _writer, governance_log, _audit = _admin_handler_stack(tmp_path)

    try:
        handler.mint_profile(
            _user_principal(),
            unsigned_profile_draft(),
            justification="Attempted self elevation through the admin profile path.",
        )
    except PermissionError as exc:
        events = governance_log.read_events("inst")
        return _blocked(
            "self_elevation",
            f"PermissionError:{exc}",
            event_types=_event_types(events),
        )
    raise AssertionError("self-elevation unexpectedly minted an authorisation profile")


def run_advisory_bypass(_tmp_path: Path) -> AdversarialScenarioResult:
    design_log = MemoryDesignEventLog()
    report = _report()
    presentation = AdvisoryAcknowledgementService().present(_presentation_request(report, _admin()))
    result = AuthorisationDecisionService(design_event_log=design_log).decide(
        _authorisation_request(
            screening_event=_screening_completed("CLEAR"),
            report=report,
            governance_events=(presentation,),
        )
    )
    _require_blocked(result.allowed, "passive advisory presentation unexpectedly authorised")
    return _blocked(
        "advisory_bypass",
        *result.blocked_by,
        authorised_event_emitted=result.authorised_event is not None,
        notes=("design_log_empty",) if not design_log.events else (),
    )


def run_reviewer_escalation(tmp_path: Path) -> AdversarialScenarioResult:
    handler, _writer, governance_log, _audit = _admin_handler_stack(tmp_path)

    try:
        handler.mint_profile(
            _reviewer_principal(),
            unsigned_profile_draft(),
            justification="Reviewer attempted to escalate through an admin-only operation.",
        )
    except PermissionError as exc:
        events = governance_log.read_events("inst")
        return _blocked(
            "reviewer_escalation",
            f"PermissionError:{exc}",
            event_types=_event_types(events),
        )
    raise AssertionError("reviewer escalation unexpectedly minted an authorisation profile")


def run_unsupported_tier(_tmp_path: Path) -> AdversarialScenarioResult:
    design_log = MemoryDesignEventLog()
    report = _report()
    requested_scope = replace(_requested_scope(), biosafety_tier=BiosafetyTier.BSL_4)
    result = AuthorisationDecisionService(design_event_log=design_log).decide(
        _authorisation_request(
            screening_event=_screening_completed("CLEAR"),
            report=report,
            governance_events=_acknowledged_advisory_events(report),
            requested_scope=requested_scope,
        )
    )
    _require_blocked(result.allowed, "unsupported biosafety tier unexpectedly authorised")
    return _blocked(
        "unsupported_tier",
        *result.blocked_by,
        authorised_event_emitted=result.authorised_event is not None,
    )


def run_plugin_trust(tmp_path: Path) -> AdversarialScenarioResult:
    service = PluginGovernanceService()
    unsigned = service.review(
        _plugin_request(
            _write_manifest(tmp_path / "unsigned", "plugin.unsigned", signed=False),
            "event-unsigned",
        )
    )
    hash_mismatch = service.review(
        _plugin_request(
            _write_manifest(
                tmp_path / "hash-mismatch",
                "plugin.hash-mismatch",
                declared_artifact_hash="0" * 64,
            ),
            "event-hash",
        )
    )
    if unsigned.approved or hash_mismatch.approved:
        raise AssertionError("adversarial plugin manifest unexpectedly approved")
    return _blocked(
        "plugin_trust",
        _reason(unsigned.reason),
        _reason(hash_mismatch.reason),
        event_types=(unsigned.event.event_type, hash_mismatch.event.event_type),
    )


def run_export_leak(_tmp_path: Path) -> AdversarialScenarioResult:
    log = _CapturingExportLog()
    bundle = ExportOrchestrator(export_event_log=log).create_bundle(
        _export_request(export_profile=ExportProfile.VENDOR)
    )
    with ZipFile(BytesIO(bundle.zip_bytes)) as archive:
        names = set(archive.namelist())
        metadata = cast(
            Mapping[str, object],
            json.loads(archive.read("metadata/export_metadata.json")),
        )
        design_plan = cast(
            Mapping[str, object],
            json.loads(archive.read("design/design_plan.json")),
        )

    if any(name.startswith(("authorisation/", "screening/", "events/")) for name in names):
        raise AssertionError("vendor export leaked internal evidence artefacts")
    if metadata.get("actor_id") != "REDACTED" or design_plan.get("actor_id") != "REDACTED":
        raise AssertionError("vendor export leaked actor metadata")
    return _accepted(
        "export_leak",
        event_types=_event_types(log.events),
        notes=("vendor_profile_redacted",),
    )


def run_audit_key_absent(tmp_path: Path) -> AdversarialScenarioResult:
    path = tmp_path / "audit.sqlite"
    _seed_audit_rows(path, TestAuditKeyProvider())

    try:
        SqliteAuditLog(path, None).verify_chain()
    except AuditLogTamperDetectionUnavailable as exc:
        return _blocked("audit_key_absent", type(exc).__name__)
    raise AssertionError("audit chain verification unexpectedly ran without an audit key provider")


def run_audit_key_compromise(tmp_path: Path) -> AdversarialScenarioResult:
    fixture = AuditServiceFixture(tmp_path)
    client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server),
        token_provider=bad_token_provider,
    )

    try:
        client.append(audit_entry(), audit_service_principal())
    except PermissionError as exc:
        events = fixture.governance_writer.read_events()
        if fixture.writer.last_row() is not None:
            raise AssertionError("invalid audit-service token still wrote an audit row") from exc
        return _blocked(
            "audit_key_compromise",
            f"PermissionError:{exc}",
            event_types=_event_types(events),
            notes=("audit_row_absent",),
        )
    raise AssertionError("invalid audit-service token unexpectedly appended an audit row")


def run_replay_integrity(_tmp_path: Path) -> AdversarialScenarioResult:
    events = _session_events("session-replay-tamper", 200)

    try:
        replay_design_events(events, governance_events=(_reviewer_event(201),))
    except ReplayIntegrityFailure as exc:
        return _blocked(
            "replay_integrity",
            f"{type(exc).__name__}:{exc}",
            authorised_event_emitted=True,
        )
    raise AssertionError("tampered replay governance event unexpectedly passed")


def run_construct_checksum_mismatch(_tmp_path: Path) -> AdversarialScenarioResult:
    design_log = MemoryDesignEventLog()
    report = _report()
    result = AuthorisationDecisionService(design_event_log=design_log).decide(
        _authorisation_request(
            screening_event=_screening_completed("CLEAR"),
            report=report,
            governance_events=_advisory_bypass_events(report, "construct_checksum_mismatch"),
        )
    )
    _require_blocked(result.allowed, "construct checksum mismatch unexpectedly authorised")
    return _blocked(
        "construct_checksum_mismatch",
        *result.blocked_by,
        authorised_event_emitted=result.authorised_event is not None,
        notes=("design_log_empty",) if not design_log.events else (),
    )


def run_programmatic_event_bypass(_tmp_path: Path) -> AdversarialScenarioResult:
    events = _session_events("session-programmatic-bypass", 300)

    try:
        replay_design_events(events, governance_events=())
    except ReplayIntegrityFailure as exc:
        return _blocked(
            "programmatic_event_bypass",
            f"{type(exc).__name__}:{exc}",
            authorised_event_emitted=True,
        )
    raise AssertionError("programmatic authorisation without governance chain replayed cleanly")


def run_profile_tamper(tmp_path: Path) -> AdversarialScenarioResult:
    path = tmp_path / "authorisation.sqlite"
    payload = cast(dict[str, object], json.loads(_signed_profile_json()))
    signature = cast(dict[str, object], payload["profile_signature"])
    signature["signature_bytes_hex"] = "00"
    _seed_profile(path, json.dumps(payload, sort_keys=True, separators=(",", ":")))
    store = SqliteAuthorisationStoreRead(path, FakeProfileVerifier())

    try:
        store.get("profile-1")
    except AuthorisationProfileTamperDetectedError as exc:
        return _blocked("profile_tamper", f"{type(exc).__name__}:{exc}")
    raise AssertionError("tampered authorisation profile unexpectedly loaded")


def run_sop_template_tamper(_tmp_path: Path) -> AdversarialScenarioResult:
    generator = SopProtocolGenerator(FakeTemplateReadPort(unsigned_template(), []))

    try:
        generator.generate(_sop_request())
    except SopTemplateTamperDetectedError as exc:
        return _blocked("sop_template_tamper", f"{type(exc).__name__}:{exc}")
    raise AssertionError("unsigned SOP template unexpectedly rendered")


def run_governance_reference_only_rejected(_tmp_path: Path) -> AdversarialScenarioResult:
    design_events = _session_events("session-reference", 400)[:4]
    reference_only = RiskAdvisoryAcknowledged(
        event_id="reference-only-ack",
        occurred_at_utc=BASE_TIME + timedelta(seconds=5),
        actor_id="admin-1",
        institution_id="institution-1",
        acknowledgement_payload=(),
        acknowledgement_content_hash="reference-only",
    )

    try:
        replay_design_events(design_events, governance_events=(reference_only,))
    except ReplayIntegrityFailure as exc:
        return _blocked(
            "governance_reference_only_rejected",
            f"{type(exc).__name__}:{exc}",
            event_types=(reference_only.event_type,),
        )
    raise AssertionError("reference-only governance payload unexpectedly passed replay")


def run_review_queue_blocked_path(tmp_path: Path) -> AdversarialScenarioResult:
    authorisation_writer = SqliteAuthorisationStoreWrite(tmp_path / "authorisation.sqlite")
    authorisation_reader = SqliteAuthorisationStoreRead(
        authorisation_writer.path,
        FakeProfileVerifier(),
    )
    service, store, governance_log, _audit = review_queue_stack(tmp_path)
    item = service.route_blocked_authorisation(
        "session-1",
        "missing profile coverage",
        review_queue_service_principal(ServiceName.AUTHORISATION_DECISION),
        subject_user_id=UserId("user-1"),
        institution_id=InstitutionId("inst"),
        requested_scope=requested_scope(),
    ).item

    if len(store.list_pending(admin_principal())) != 1:
        raise AssertionError("blocked path did not create exactly one pending review item")
    try:
        authorisation_reader.read_own_profile("user-1")
    except AuthorisationProfileNotFoundError:
        pass
    else:
        raise AssertionError("blocked review queue path granted a profile before approval")

    resolver, _admin_audit, admin = admin_resolution_stack(store, governance_log)
    try:
        resolver.resolve_item(
            _user_principal(),
            str(item.item_id),
            ReviewQueueStatus.APPROVED,
            justification="Self approval must remain blocked.",
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("user unexpectedly self-approved a review queue item")

    if store.get(str(item.item_id)).status is not ReviewQueueStatus.PENDING:
        raise AssertionError("self-approval attempt mutated the pending review queue item")
    resolver.resolve_item(
        admin,
        str(item.item_id),
        ReviewQueueStatus.APPROVED,
        justification="Approved after institutional review.",
    )

    admin_governance_log = JsonlEventLog(
        tmp_path / "admin-events",
        expected_stream=EventStream.GOVERNANCE,
    )
    handler = AdminActionHandler(
        authorisation_store=authorisation_writer,
        profile_signer=FakeProfileSigner(),
        audit_append=FakeAdminAuditBroker(TestAuditKeyProvider()),
        governance_event_log=admin_governance_log,
        clock=lambda: item.created_at_utc,
    )
    handler.mint_profile(
        admin_principal(),
        unsigned_profile_draft(),
        justification="Grant scope after approved review-queue item.",
    )
    if authorisation_reader.read_own_profile("user-1").subject_user_id != UserId("user-1"):
        raise AssertionError("admin grant after review approval did not unblock the user profile")
    return _accepted(
        "review_queue_blocked_path",
        event_types=(
            *_event_types(governance_log.read_events("inst")),
            *_event_types(admin_governance_log.read_events("inst")),
        ),
        notes=("single_pending_request", "self_approval_blocked", "admin_grant_unblocked"),
    )


def run_developer_post_bootstrap_denied(tmp_path: Path) -> AdversarialScenarioResult:
    handler, _writer, governance_log, _audit = _admin_handler_stack(tmp_path)
    handler.mint_profile(
        _bootstrap_principal(),
        unsigned_profile_draft(),
        justification="Bootstrap first administrator.",
    )

    try:
        handler.mint_profile(
            _developer_principal(),
            unsigned_profile_draft(),
            justification="Developer attempted mint after bootstrap.",
        )
    except PermissionError as exc:
        return _blocked(
            "developer_post_bootstrap_denied",
            f"PermissionError:{exc}",
            event_types=_event_types(governance_log.read_events("inst")),
        )
    raise AssertionError("ordinary developer unexpectedly minted after bootstrap")


def run_admin_service_unauthenticated(_tmp_path: Path) -> AdversarialScenarioResult:
    app = harness()
    issued_at = datetime(2026, 1, 1, tzinfo=UTC)
    response = app.client.list_profiles(
        token(issued_at=issued_at, expires_at=issued_at + timedelta(days=1)),
        {},
        requested_at_utc=ADMIN_SERVICE_NOW,
    )

    if (
        response.status is not AdminIpcStatus.ERROR
        or response.error_code is not AdminIpcErrorCode.AUTHENTICATION_FAILED
    ):
        raise AssertionError("expired admin-service token unexpectedly authenticated")
    return _blocked(
        "admin_service_unauthenticated",
        response.error_code.value,
        event_types=(app.security_log.events[-1].event_type,),
    )


def run_dual_control_same_admin_rejected(tmp_path: Path) -> AdversarialScenarioResult:
    handler, _writer, governance_log, audit = _dual_control_admin_handler(tmp_path)
    admin = admin_principal()
    handler.mint_profile(
        admin,
        unsigned_profile_draft(),
        justification="Mint profile under dual-control fixture.",
    )

    try:
        handler.revoke_profile(admin, "profile-1", reason="Same-admin revocation attempt.")
    except PermissionError as exc:
        return _blocked(
            "dual_control_same_admin_rejected",
            f"PermissionError:{exc}",
            event_types=_event_types(governance_log.read_events("inst")),
            audit_event_types=_audit_event_types(audit.rows),
        )
    raise AssertionError("same administrator unexpectedly revoked a dual-control profile")


def run_dual_control_two_admins_accepted(tmp_path: Path) -> AdversarialScenarioResult:
    handler, writer, governance_log, audit = _dual_control_admin_handler(tmp_path)
    handler.mint_profile(
        admin_principal(),
        unsigned_profile_draft(),
        justification="Mint profile under dual-control fixture.",
    )
    handler.revoke_profile(
        _second_admin_principal(),
        "profile-1",
        reason="Second administrator confirmed revocation.",
    )
    stored = writer.get_profile("profile-1")
    if stored.revoked_at is None:
        raise AssertionError("two-admin revocation did not persist revoked profile state")
    return _accepted(
        "dual_control_two_admins_accepted",
        event_types=_event_types(governance_log.read_events("inst")),
        audit_event_types=_audit_event_types(audit.rows),
        notes=("second_admin_revoked",),
    )


def run_dual_control_advisory_signoff_pair_required(
    _tmp_path: Path,
) -> AdversarialScenarioResult:
    report = _report()
    flags = DualControlFlags(advisory_acknowledgement_requires_pair=True)
    single_events = _acknowledged_advisory_events(report)
    single_ok, single_missing = all_required_advisories_acknowledged(
        report,
        single_events,
        flags,
    )
    if single_ok:
        raise AssertionError("single advisory signoff unexpectedly passed pair-required mode")

    pair_events = (*single_events, *_second_admin_advisory_events(report))
    pair_ok, pair_missing = all_required_advisories_acknowledged(report, pair_events, flags)
    if not pair_ok:
        raise AssertionError(f"paired advisory signoff unexpectedly missing: {pair_missing}")
    return _accepted(
        "dual_control_advisory_signoff_pair_required",
        blocked_by=tuple(f"single_admin_missing:{item}" for item in sorted(single_missing)),
        event_types=_event_types(pair_events),
        notes=("single_admin_blocked", "pair_acknowledged"),
    )


def run_audit_service_dual_writer_chain_integrity(tmp_path: Path) -> AdversarialScenarioResult:
    fixture = AuditServiceFixture(tmp_path)
    client = AuditServiceClient(
        transport=InProcessAuditServiceTransport(fixture.server),
        token_provider=fixture.token_provider,
    )
    callers = [audit_service_principal(), admin_principal()] * 10

    with ThreadPoolExecutor(max_workers=4) as pool:
        entry_ids = list(pool.map(lambda caller: client.append(audit_entry(), caller), callers))

    if len(set(entry_ids)) != 20 or not fixture.writer.verify_chain():
        raise AssertionError("audit-service dual-writer append chain lost linear integrity")
    replayed = SqliteAuditLog(fixture.audit_db, fixture.audit_key_provider).replay()
    if len(replayed) != 20:
        raise AssertionError("audit-service replay row count did not match appended entries")
    return _accepted(
        "audit_service_dual_writer_chain_integrity",
        audit_event_types=("test",),
        notes=("linear_hmac_chain_verified", "audit_rows:20"),
    )


def run_admin_command_direct_handler_import_rejected(tmp_path: Path) -> AdversarialScenarioResult:
    synthetic_root = tmp_path / "synthetic"
    synthetic_cli = synthetic_root / "src" / "interface" / "cli"
    synthetic_cli.mkdir(parents=True)
    (synthetic_cli / "bad_admin_command.py").write_text(
        "from app.admin_action_handler import AdminActionHandler\n",
        encoding="utf-8",
        newline="\n",
    )
    synthetic_violations = direct_admin_handler_import_violations(synthetic_root)
    if not synthetic_violations:
        raise AssertionError("direct AdminActionHandler import fixture was not detected")

    repository_violations = direct_admin_handler_import_violations(ROOT)
    if repository_violations:
        raise AssertionError("\n".join(repository_violations))
    return _blocked(
        "admin_command_direct_handler_import_rejected",
        *synthetic_violations,
        notes=("repository_cli_api_clean",),
    )


def _dual_control_admin_handler(
    tmp_path: Path,
) -> tuple[AdminActionHandler, SqliteAuthorisationStoreWrite, JsonlEventLog, FakeAdminAuditBroker]:
    writer = SqliteAuthorisationStoreWrite(tmp_path / "authorisation.sqlite")
    governance_log = JsonlEventLog(
        tmp_path / "events" / "governance",
        expected_stream=EventStream.GOVERNANCE,
    )
    audit = FakeAdminAuditBroker(TestAuditKeyProvider())
    handler = AdminActionHandler(
        authorisation_store=writer,
        profile_signer=FakeProfileSigner(),
        audit_append=audit,
        governance_event_log=governance_log,
        dual_control_flags=DualControlFlags(require_two_admins_for_profile_revocation=True),
        clock=lambda: NOW,
    )
    return handler, writer, governance_log, audit


def _second_admin_principal() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("principal-admin-2"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def _second_admin_advisory_events(report: RiskAdvisoryReport) -> tuple[GovernanceEvent, ...]:
    event_log = _MemoryGovernanceEventLog()
    service = AdvisoryAcknowledgementService(event_log)
    second_admin = _second_admin_principal()
    presentation = service.present(
        AdvisoryPresentationRequest(
            report=report,
            recipient=second_admin,
            presenting_surface="cli==0.3.2",
            occurred_at_utc=NOW,
            event_id="present-admin-2",
        )
    )
    service.acknowledge(
        AdvisoryActionRequest(
            report=report,
            advisory_id="risk.caution",
            actor=second_admin,
            presentation_event=presentation,
            justification="Second administrator reviewed the advisory for dual-control signoff.",
            decision_record=_decision_record("ack-2"),
            occurred_at_utc=NOW,
            event_id="ack-2",
        )
    )
    return tuple(event_log.events)


class _MemoryGovernanceEventLog:
    def __init__(self) -> None:
        self.events: list[GovernanceEvent] = []

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        if not isinstance(event, GovernanceEvent):
            raise TypeError("expected governance event")
        self.events.append(event)
        return event.event_id


def _blocked(
    scenario: str,
    *blocked_by: str,
    event_types: tuple[str, ...] = (),
    audit_event_types: tuple[str, ...] = (),
    authorised_event_emitted: bool = False,
    notes: tuple[str, ...] = (),
) -> AdversarialScenarioResult:
    return AdversarialScenarioResult(
        scenario=scenario,
        verdict="blocked",
        blocked_by=blocked_by,
        event_types=event_types,
        audit_event_types=audit_event_types,
        authorised_event_emitted=authorised_event_emitted,
        notes=notes,
    )


def _accepted(
    scenario: str,
    *,
    blocked_by: tuple[str, ...] = (),
    event_types: tuple[str, ...] = (),
    audit_event_types: tuple[str, ...] = (),
    authorised_event_emitted: bool = False,
    notes: tuple[str, ...] = (),
) -> AdversarialScenarioResult:
    return AdversarialScenarioResult(
        scenario=scenario,
        verdict="accepted",
        blocked_by=blocked_by,
        event_types=event_types,
        audit_event_types=audit_event_types,
        authorised_event_emitted=authorised_event_emitted,
        notes=notes,
    )


def _event_types(events: Iterable[DomainEvent]) -> tuple[str, ...]:
    return tuple(event.event_type for event in events)


def _audit_event_types(rows: Iterable[AuditChainRow]) -> tuple[str, ...]:
    return tuple(row.entry.entry_type for row in rows)


def _reason(reason: str | None) -> str:
    if reason is None:
        raise AssertionError("expected rejection reason")
    return reason


def _require_blocked(allowed: bool, message: str) -> None:
    if allowed:
        raise AssertionError(message)


def _load_expected(scenario: str) -> Mapping[str, object]:
    path = FIXTURE_ROOT / scenario / "expected.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return cast(Mapping[str, object], payload)


def _expected_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise AssertionError(f"expected fixture key {key!r} to be a string")
    return value


def _expected_bool(data: Mapping[str, object], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise AssertionError(f"expected fixture key {key!r} to be a bool")
    return value


def _expected_str_tuple(data: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = data.get(key, ())
    if not isinstance(value, list):
        raise AssertionError(f"expected fixture key {key!r} to be a list")
    strings: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise AssertionError(f"expected fixture key {key!r} to contain only strings")
        strings.append(item)
    return tuple(strings)


def _assert_contains(actual: tuple[str, ...], expected_items: tuple[str, ...]) -> None:
    for expected in expected_items:
        assert expected in actual
