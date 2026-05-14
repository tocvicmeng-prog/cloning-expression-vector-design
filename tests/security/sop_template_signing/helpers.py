"""
module_id: tests.security.sop_template_signing.helpers
file: tests/security/sop_template_signing/helpers.py
task_id: T-316c
"""

from __future__ import annotations

from pathlib import Path

from adapter.persistence import JsonlEventLog
from app.decision_record_key_management import DecisionRecordKeyManagementService
from domain.events import EventStream
from domain.ports.decision_record_signing import SignedDecisionRecord
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    decision_record,
    reviewer_principal,
)
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner


def signed_decision_record() -> SignedDecisionRecord:
    return FakeDecisionRecordSigner().sign(decision_record(), reviewer_principal())


def provision_decision_record_key(archive: Path, tmp_path: Path) -> None:
    service = DecisionRecordKeyManagementService(
        archive_path=archive,
        governance_event_log=JsonlEventLog(tmp_path / "decision-events", EventStream.GOVERNANCE),
    )
    service.provision_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        reason="initial provisioning",
        signed_decision_record=signed_decision_record(),
    )
