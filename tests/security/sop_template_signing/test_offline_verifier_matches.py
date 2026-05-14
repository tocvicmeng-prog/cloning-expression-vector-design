"""
module_id: tests.security.sop_template_signing.test_offline_verifier_matches
file: tests/security/sop_template_signing/test_offline_verifier_matches.py
task_id: T-316c
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateSigner,
    sop_template_to_json,
)
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template
from tools.sop_template_signature_verifier import main, verify_sop_template_file


def test_sop_template_offline_verifier_matches_engine_verdict(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    template_path = tmp_path / "sop-template.json"
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))
    template_path.write_text(sop_template_to_json(template), encoding="utf-8")

    assert verify_sop_template_file(template_path, archive).success
    assert main(["--template-json", str(template_path), "--key-archive", str(archive)]) == 0
    assert "valid" in capsys.readouterr().out


def test_sop_template_offline_verifier_returns_one_for_tamper(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    payload = json.loads(
        sop_template_to_json(signed_template(signer.sign(unsigned_template(), admin_principal())))
    )
    payload["signature"]["signature_bytes_hex"] = "00" * 64
    template_path = tmp_path / "sop-template.json"
    template_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--template-json", str(template_path), "--key-archive", str(archive)]) == 1
    assert "invalid" in capsys.readouterr().err
