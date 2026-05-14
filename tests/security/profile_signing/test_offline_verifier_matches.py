"""
module_id: tests.security.profile_signing.test_offline_verifier_matches
file: tests/security/profile_signing/test_offline_verifier_matches.py
task_id: T-314b
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapter.persistence import profile_to_json
from adapter.security.profile_signing import Ed25519InstitutionalProfileSigner
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    signed_profile,
    unsigned_profile,
)
from tools.profile_signature_verifier import main, verify_profile_file


def test_profile_offline_verifier_matches_engine_verdict(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    archive = tmp_path / "profile-keys.json"
    signer = Ed25519InstitutionalProfileSigner(archive)
    profile_path = tmp_path / "profile.json"
    profile = signed_profile(signer.sign(unsigned_profile(), admin_principal()))
    profile_path.write_text(profile_to_json(profile), encoding="utf-8")

    assert verify_profile_file(profile_path, archive).success
    assert main(["--profile-json", str(profile_path), "--key-archive", str(archive)]) == 0
    assert "valid" in capsys.readouterr().out


def test_profile_offline_verifier_returns_one_for_tamper(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    archive = tmp_path / "profile-keys.json"
    signer = Ed25519InstitutionalProfileSigner(archive)
    profile_path = tmp_path / "profile.json"
    payload = json.loads(
        profile_to_json(signed_profile(signer.sign(unsigned_profile(), admin_principal())))
    )
    payload["profile_signature"]["signature_bytes_hex"] = "00" * 64
    profile_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--profile-json", str(profile_path), "--key-archive", str(archive)]) == 1
    assert "invalid" in capsys.readouterr().err
