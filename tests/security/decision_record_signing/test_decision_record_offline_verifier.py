"""
module_id: tests.security.decision_record_signing.test_decision_record_offline_verifier
file: tests/security/decision_record_signing/test_decision_record_offline_verifier.py
task_id: T-314b
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapter.persistence import JsonlEventLog
from adapter.security.decision_record_signing import (
    PerPrincipalDecisionRecordSigner,
    signed_decision_to_json,
)
from app.decision_record_key_management import DecisionRecordKeyManagementService
from domain.events import EventStream
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    decision_record,
    reviewer_principal,
)
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner
from tools.decision_record_verifier import main, verify_decision_record_file


def test_decision_record_offline_verifier_matches_engine_verdict(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    archive = tmp_path / "decision-keys.json"
    _provision(archive, tmp_path)
    signed = PerPrincipalDecisionRecordSigner(archive).sign(decision_record(), reviewer_principal())
    signed_path = tmp_path / "signed-decision.json"
    signed_path.write_text(signed_decision_to_json(signed), encoding="utf-8")

    assert verify_decision_record_file(signed_path, archive).success
    assert main(["--signed-record-json", str(signed_path), "--key-archive", str(archive)]) == 0
    assert "valid" in capsys.readouterr().out


def test_decision_record_offline_verifier_returns_one_for_tamper(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    archive = tmp_path / "decision-keys.json"
    _provision(archive, tmp_path)
    signed = PerPrincipalDecisionRecordSigner(archive).sign(decision_record(), reviewer_principal())
    payload = json.loads(signed_decision_to_json(signed))
    payload["signature_bytes_hex"] = "00" * 64
    signed_path = tmp_path / "signed-decision.json"
    signed_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--signed-record-json", str(signed_path), "--key-archive", str(archive)]) == 1
    assert "invalid" in capsys.readouterr().err


def _provision(archive: Path, tmp_path: Path) -> None:
    service = DecisionRecordKeyManagementService(
        archive_path=archive,
        governance_event_log=JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE),
    )
    service.provision_principal_key(
        admin_principal(),
        principal_id=str(reviewer_principal().id),
        reason="initial provisioning",
        signed_decision_record=FakeDecisionRecordSigner().sign(
            decision_record(), reviewer_principal()
        ),
    )
