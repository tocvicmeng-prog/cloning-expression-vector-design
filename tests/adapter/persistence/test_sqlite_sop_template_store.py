"""
module_id: tests.adapter.persistence.test_sqlite_sop_template_store
file: tests/adapter/persistence/test_sqlite_sop_template_store.py
task_id: T-316b
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from adapter.persistence import JsonlEventLog, SopTemplateNotFoundError, SqliteSopTemplateStore
from adapter.security.sop_template_signing import (
    Ed25519InstitutionalSopTemplateSigner,
    Ed25519InstitutionalSopTemplateVerifier,
)
from domain.events import EventStream, SopTemplateMinted
from domain.security import DeveloperBootstrapPrincipal, InstitutionId, PrincipalId, SecurityRole
from domain.types.signing_errors import SopTemplateTamperDetectedError
from tests.fakes.sop_template.fixtures import admin_principal, signed_template, unsigned_template

NOW = datetime(2026, 5, 14, tzinfo=UTC)
LATER = datetime(2030, 1, 1, tzinfo=UTC)


def test_sqlite_sop_template_store_writes_and_reads_signed_template(tmp_path: Path) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    store = SqliteSopTemplateStore(
        tmp_path / "sop_templates.sqlite",
        Ed25519InstitutionalSopTemplateVerifier(archive),
    )
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))

    version = store.write_mint(template, admin_principal())

    assert version.content_hash == template.content_hash()
    assert store.get_template(template.template_id) == template
    assert store.list_templates() == (template,)


def test_sqlite_sop_template_store_rejects_tampered_persisted_template(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    db_path = tmp_path / "sop_templates.sqlite"
    store = SqliteSopTemplateStore(db_path, Ed25519InstitutionalSopTemplateVerifier(archive))
    template = signed_template(signer.sign(unsigned_template(), admin_principal()))
    store.write_mint(template, admin_principal())
    payload = json.loads(_stored_template_json(db_path, str(template.template_id)))
    payload["signature"]["signature_bytes_hex"] = "00" * 64
    _replace_template_json(db_path, str(template.template_id), json.dumps(payload))

    try:
        store.get_template(template.template_id)
    except SopTemplateTamperDetectedError as exc:
        assert "signature" in str(exc)
    else:  # pragma: no cover - defensive assertion branch
        raise AssertionError("tampered SOP template unexpectedly loaded")


def test_sqlite_sop_template_bootstrap_reads_catalogue_and_is_idempotent(
    tmp_path: Path,
) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    event_log = JsonlEventLog(tmp_path / "events", EventStream.GOVERNANCE)
    store = SqliteSopTemplateStore(
        tmp_path / "sop_templates.sqlite",
        Ed25519InstitutionalSopTemplateVerifier(archive),
        signer=signer,
        catalogue_dir=Path("catalogues/sop_templates"),
        schema_root=Path("schemas"),
        governance_event_log=event_log,
        clock=lambda: NOW,
    )

    first = store.bootstrap_initial_templates(_bootstrap_principal())
    second = store.bootstrap_initial_templates(_bootstrap_principal())

    assert len(first) == 1
    assert second == ()
    template = store.get_template(first[0].template_id)
    assert template.signature is not None
    events = event_log.read_events("inst")
    assert len(events) == 1
    assert isinstance(events[0], SopTemplateMinted)
    assert events[0].template_id == str(first[0].template_id)


def test_sqlite_sop_template_revoke_hides_active_template(tmp_path: Path) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    store = SqliteSopTemplateStore(
        tmp_path / "sop_templates.sqlite",
        Ed25519InstitutionalSopTemplateVerifier(archive),
    )
    original = unsigned_template()
    template = signed_template(signer.sign(original, admin_principal()))
    store.write_mint(template, admin_principal())

    revocation = store.write_revoke(template.template_id, "retired", admin_principal())

    assert revocation.version == template.version
    try:
        store.get_template(template.template_id)
    except SopTemplateNotFoundError:
        pass
    else:  # pragma: no cover - defensive assertion branch
        raise AssertionError("revoked SOP template unexpectedly loaded")


def test_sqlite_sop_template_modify_requires_existing_active_template(tmp_path: Path) -> None:
    archive = tmp_path / "sop-template-keys.json"
    signer = Ed25519InstitutionalSopTemplateSigner(archive)
    store = SqliteSopTemplateStore(
        tmp_path / "sop_templates.sqlite",
        Ed25519InstitutionalSopTemplateVerifier(archive),
    )
    modified = replace(unsigned_template(), content_markdown="Updated controlled SOP.")
    signed = replace(modified, signature=signer.sign(modified, admin_principal()))

    try:
        store.write_modify(signed, admin_principal())
    except SopTemplateNotFoundError:
        pass
    else:  # pragma: no cover - defensive assertion branch
        raise AssertionError("modify unexpectedly created an absent SOP template")


def _bootstrap_principal() -> DeveloperBootstrapPrincipal:
    return DeveloperBootstrapPrincipal(
        id=PrincipalId("developer-bootstrap-1"),
        role=SecurityRole.DEVELOPER,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
        is_bootstrap=True,
        bootstrap_expires_at=LATER,
    )


def _stored_template_json(db_path: Path, template_id: str) -> str:
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT template_json FROM templates WHERE template_id = ?",
            (template_id,),
        ).fetchone()
    assert row is not None
    return str(row[0])


def _replace_template_json(db_path: Path, template_id: str, template_json: str) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE templates SET template_json = ? WHERE template_id = ?",
            (template_json, template_id),
        )
