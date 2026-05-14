"""
module_id: adapter.security.decision_record_signing.serialization
file: src/adapter/security/decision_record_signing/serialization.py
task_id: T-313b

JSON helpers for signed decision-record IPC tokens.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security import KeyVersionId, PrincipalId, SecurityRole
from domain.sequence import Sha256
from domain.types.governance import DecisionRecord, RoleSnapshot


def signed_decision_to_json(signed: SignedDecisionRecord) -> str:
    decision = signed.decision
    snapshot = decision.role_snapshot
    return json.dumps(
        {
            "decision": {
                "decision_id": decision.decision_id,
                "decision_type": decision.decision_type,
                "policy_version": decision.policy_version,
                "profile_content_hash": str(decision.profile_content_hash),
                "role_snapshot": {
                    "captured_at_utc": _datetime_to_json(snapshot.captured_at_utc),
                    "credentials_verified_at_utc": _datetime_to_json(
                        snapshot.credentials_verified_at_utc
                    ),
                    "institution_id": snapshot.institution_id,
                    "principal_id": str(snapshot.principal_id),
                    "role": snapshot.role.value,
                },
                "signature_bytes_hex": decision.signature_bytes.hex(),
                "signed_at_utc": _datetime_to_json(decision.signed_at_utc),
                "signed_payload_hash": str(decision.signed_payload_hash),
            },
            "signature_bytes_hex": signed.signature_bytes.hex(),
            "signed_payload_hash": str(signed.signed_payload_hash),
            "signing_key_version": str(signed.signing_key_version),
            "signing_principal_id": str(signed.signing_principal_id),
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def signed_decision_from_json(payload: str) -> SignedDecisionRecord:
    data = _expect_dict(json.loads(payload), "signed decision")
    decision_data = _expect_dict(data.get("decision"), "decision")
    snapshot_data = _expect_dict(decision_data.get("role_snapshot"), "role_snapshot")
    snapshot = RoleSnapshot(
        principal_id=PrincipalId(_expect_str(snapshot_data, "principal_id")),
        role=SecurityRole(_expect_str(snapshot_data, "role")),
        institution_id=_expect_str(snapshot_data, "institution_id"),
        captured_at_utc=_parse_datetime(_expect_str(snapshot_data, "captured_at_utc")),
        credentials_verified_at_utc=_parse_datetime(
            _expect_str(snapshot_data, "credentials_verified_at_utc")
        ),
    )
    decision = DecisionRecord(
        decision_id=_expect_str(decision_data, "decision_id"),
        decision_type=_expect_str(decision_data, "decision_type"),
        role_snapshot=snapshot,
        profile_content_hash=Sha256(_expect_str(decision_data, "profile_content_hash")),
        policy_version=_expect_str(decision_data, "policy_version"),
        signed_payload_hash=Sha256(_expect_str(decision_data, "signed_payload_hash")),
        signature_bytes=bytes.fromhex(_expect_str(decision_data, "signature_bytes_hex")),
        signed_at_utc=_parse_datetime(_expect_str(decision_data, "signed_at_utc")),
    )
    return SignedDecisionRecord(
        decision=decision,
        signing_principal_id=PrincipalId(_expect_str(data, "signing_principal_id")),
        signing_key_version=KeyVersionId(_expect_str(data, "signing_key_version")),
        signed_payload_hash=Sha256(_expect_str(data, "signed_payload_hash")),
        signature_bytes=bytes.fromhex(_expect_str(data, "signature_bytes_hex")),
    )


def _expect_dict(raw: object, field_name: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise TypeError(f"{field_name} must be a JSON object")
    return dict(raw)


def _expect_str(data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    return value


def _datetime_to_json(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
