"""
module_id: tests.security.audit_service_helpers
file: tests/security/audit_service_helpers.py
task_id: T-313b
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from adapter.persistence import JsonlEventLog, SqliteAuditLogWriter
from adapter.security.audit_key import FileAuditKeyProvider
from adapter.security.decision_record_signing import (
    PerPrincipalDecisionRecordSigner,
    PerPrincipalDecisionRecordVerifier,
    signed_decision_to_json,
)
from app.decision_record_key_management import DecisionRecordKeyManagementService
from domain.ports.audit_append import AuditEntry
from domain.security import (
    AdminPrincipal,
    DeveloperBootstrapPrincipal,
    InstitutionId,
    Principal,
    PrincipalId,
    SecurityRole,
    ServiceName,
    ServicePrincipal,
)
from domain.sequence import Sha256
from domain.types.governance import DecisionRecord, RoleSnapshot
from interface.audit_service.governance_event_writer import AuditServiceGovernanceEventWriter
from interface.audit_service.handlers import AuditServiceHandlers
from interface.audit_service.server import AuditServiceServer
from tests.fakes.security.profile_signing.fixtures import admin_principal, decision_record
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner
from tests.security.audit_key.helpers import deterministic_key_factory

NOW = datetime(2026, 5, 14, tzinfo=UTC)


class AuditServiceFixture:
    def __init__(self, tmp_path: Path) -> None:
        self.audit_db = tmp_path / "audit.sqlite"
        self.event_dir = tmp_path / "events"
        self.audit_key_provider = FileAuditKeyProvider(
            tmp_path / "audit-key.json",
            key_factory=deterministic_key_factory(),
            emit_warning=False,
        )
        self.decision_archive = tmp_path / "decision-keys.json"
        self._key_service = DecisionRecordKeyManagementService(
            archive_path=self.decision_archive,
            governance_event_log=JsonlEventLog(tmp_path / "key-events"),
            clock=lambda: NOW,
        )
        self._provision_principal(_service_token_principal(ServiceName.AUTHORISATION_DECISION))
        self._provision_principal(admin_principal())
        self.signer = PerPrincipalDecisionRecordSigner(self.decision_archive)
        self.verifier = PerPrincipalDecisionRecordVerifier(self.decision_archive)
        self.governance_writer = AuditServiceGovernanceEventWriter(
            str(self.event_dir),
            institution_id="inst",
            clock=lambda: NOW,
        )
        self.writer = SqliteAuditLogWriter(self.audit_db, self.audit_key_provider)
        self.server = AuditServiceServer(
            AuditServiceHandlers(
                writer=self.writer,
                verifier=self.verifier,
                governance_writer=self.governance_writer,
            )
        )

    def token_provider(
        self,
        caller: ServicePrincipal | AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> bytes:
        principal: Principal | AdminPrincipal | DeveloperBootstrapPrincipal
        if isinstance(caller, ServicePrincipal):
            principal = _service_token_principal(caller.service_name)
        else:
            principal = caller
        signed = self.signer.sign(_token_decision(principal), principal)
        return signed_decision_to_json(signed).encode("utf-8")

    def _provision_principal(self, principal: Principal | AdminPrincipal) -> None:
        self._key_service.provision_principal_key(
            admin_principal(),
            principal_id=str(principal.id),
            reason="audit-service token provisioning",
            signed_decision_record=FakeDecisionRecordSigner().sign(
                decision_record(),
                admin_principal(),
            ),
        )


def audit_entry(entry_type: str = "test") -> AuditEntry:
    return AuditEntry(
        entry_type=entry_type,
        payload={"decision_id": "decision-1"},
        occurred_at_utc=NOW,
    )


def service_principal() -> ServicePrincipal:
    return ServicePrincipal(
        service_name=ServiceName.AUTHORISATION_DECISION,
        token=b"transport-auth-token",
    )


def bad_token_provider(_caller: object) -> bytes:
    return b"not-json"


def _service_token_principal(service_name: ServiceName) -> Principal:
    return Principal(
        id=PrincipalId(f"service:{service_name.value}"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def _token_decision(principal: Principal) -> DecisionRecord:
    snapshot = RoleSnapshot(
        principal_id=principal.id,
        role=principal.role,
        institution_id=str(principal.institution),
        captured_at_utc=NOW,
        credentials_verified_at_utc=principal.credentials_verified_at,
    )
    return DecisionRecord(
        decision_id=f"audit-service-token-{principal.id}",
        decision_type="audit_service_ipc_token",
        role_snapshot=snapshot,
        profile_content_hash=Sha256("0" * 64),
        policy_version="policy-v1",
        signed_payload_hash=Sha256("1" * 64),
        signature_bytes=b"placeholder",
        signed_at_utc=NOW,
    )


def token_provider_type() -> Callable[[ServicePrincipal | AdminPrincipal], bytes]:
    return lambda _caller: b""
