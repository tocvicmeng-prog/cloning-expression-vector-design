"""
module_id: tests.app.test_plugin_governance_t808
file: tests/app/test_plugin_governance_t808.py
task_id: T-808
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.plugin_governance import (
    DEFAULT_PLUGIN_TRUST_KEY_ID,
    PluginGovernanceRequest,
    PluginGovernanceService,
    PluginPermissions,
    plugin_manifest_signature_payload,
)
from domain.canonicalisation import canonical_sha256
from domain.events import DomainEvent, EventStream, PluginManifestApproved, PluginManifestRejected
from domain.security import InstitutionId
from tools.ci_gates.plugin_manifest_signature_check import check_plugin_manifest_signatures

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
SEED_PRIVATE_KEY_HEX = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"


@dataclass
class FakeGovernanceEventLog:
    events: list[DomainEvent] = field(default_factory=list)

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        assert stream_id == "inst"
        self.events.append(event)
        return event.event_id


def test_signed_plugin_manifest_approves_and_emits_audit_event(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path, "plugin.good")
    event_log = FakeGovernanceEventLog()
    service = PluginGovernanceService(event_log=event_log)

    decision = service.review(_request(manifest_path, "event-approved"))

    assert decision.approved
    assert decision.reason is None
    assert isinstance(decision.event, PluginManifestApproved)
    assert decision.event.stream is EventStream.GOVERNANCE
    assert event_log.events == [decision.event]
    assert decision.sandbox_grant is not None
    decision.sandbox_grant.assert_file_access("plugins/plugin.good/config.json")
    try:
        decision.sandbox_grant.assert_network_access("example.org")
    except PermissionError:
        pass
    else:  # pragma: no cover - defensive assertion branch
        raise AssertionError("deterministic plugin grant unexpectedly allowed network access")


def test_unsigned_manifest_is_rejected_with_governance_event(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path, "plugin.unsigned", signed=False)
    event_log = FakeGovernanceEventLog()

    decision = PluginGovernanceService(event_log=event_log).review(
        _request(manifest_path, "event-unsigned")
    )

    assert not decision.approved
    assert decision.reason == "signature_missing"
    assert isinstance(decision.event, PluginManifestRejected)
    assert event_log.events == [decision.event]
    assert decision.sandbox_grant is None


def test_artefact_hash_mismatch_rejected_after_valid_signature(tmp_path: Path) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        "plugin.hash-mismatch",
        declared_artifact_hash="0" * 64,
    )

    decision = PluginGovernanceService().review(_request(manifest_path, "event-hash"))

    assert not decision.approved
    assert decision.reason == "artefact_hash_mismatch"
    assert isinstance(decision.event, PluginManifestRejected)


def test_manifest_permission_outside_sandbox_rejected(tmp_path: Path) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        "plugin.permission",
        permissions=PluginPermissions(file_access=("secrets",), deterministic_paths=True),
    )

    decision = PluginGovernanceService().review(_request(manifest_path, "event-permission"))

    assert not decision.approved
    assert decision.reason is not None
    assert decision.reason.startswith("permission_denied:")
    assert "file_access_out_of_scope:secrets" in decision.reason


def test_plugin_manifest_signature_gate_rejects_adversarial_directory(tmp_path: Path) -> None:
    manifest_root = tmp_path / "catalogues" / "plugin_manifests"
    manifest_root.mkdir(parents=True)
    _write_manifest(manifest_root, "plugin.unsigned", signed=False)

    result = check_plugin_manifest_signatures(tmp_path)

    assert not result.passed
    assert result.messages == ("plugin.unsigned: signature_missing",)


def test_repository_plugin_manifest_seed_passes_enforced_gate() -> None:
    result = check_plugin_manifest_signatures(ROOT)

    assert result.passed
    assert result.messages == ("all plugin manifests verify against the trust keyring",)


def _request(manifest_path: Path, event_id: str) -> PluginGovernanceRequest:
    return PluginGovernanceRequest(
        manifest_path=manifest_path,
        institution_id=InstitutionId("inst"),
        occurred_at_utc=NOW,
        event_id=event_id,
    )


def _write_manifest(
    root: Path,
    plugin_id: str,
    *,
    signed: bool = True,
    declared_artifact_hash: str | None = None,
    permissions: PluginPermissions | None = None,
) -> Path:
    artifact_dir = root / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{plugin_id}.txt"
    artifact_path.write_text(f"artifact for {plugin_id}\n", encoding="utf-8", newline="\n")
    artifact_hash = declared_artifact_hash or hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    active_permissions = permissions or PluginPermissions(
        file_access=(f"plugins/{plugin_id}",),
        deterministic_paths=True,
    )
    item: dict[str, object] = {
        "artefact_path": f"artifacts/{plugin_id}.txt",
        "artefact_sha256": artifact_hash,
        "citation": {
            "accessed": "2026-05-14",
            "grade": "B2",
            "text": "T-808 plugin-governance test fixture.",
            "url": "tests/app/test_plugin_governance_t808.py",
        },
        "id": plugin_id,
        "name": f"{plugin_id} manifest",
        "permissions": active_permissions.to_payload(),
        "version": "1.0.0",
    }
    if signed:
        item["signature"] = _signature_for(item)
    manifest = {
        "maintenance": {
            "retrieved_at": "2026-05-14",
            "valid_until": "2027-05-14",
            "source_url": "tests/app/test_plugin_governance_t808.py",
            "review_required_after": "2026-11-14",
        },
        "manifests": [item],
    }
    path = root / f"{plugin_id}.yaml"
    path.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
    return path


def _signature_for(unsigned_payload: dict[str, object]) -> dict[str, str]:
    private_key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(SEED_PRIVATE_KEY_HEX))
    manifest_hash = canonical_sha256(unsigned_payload)
    signature = private_key.sign(plugin_manifest_signature_payload(unsigned_payload))
    return {
        "algorithm": "ed25519",
        "key_id": DEFAULT_PLUGIN_TRUST_KEY_ID,
        "signature": base64.b64encode(signature).decode("ascii"),
        "signed_payload_hash": str(manifest_hash),
    }
