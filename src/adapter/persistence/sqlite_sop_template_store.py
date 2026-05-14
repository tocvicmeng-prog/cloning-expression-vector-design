"""
module_id: adapter.persistence.sqlite_sop_template_store
file: src/adapter/persistence/sqlite_sop_template_store.py
task_id: T-316b

Signed SQLite SOP-template store and catalogue bootstrap.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from adapter.catalogue import load_catalogue, schema_for_catalogue
from adapter.persistence.jsonl_event_log import JsonlEventLog
from adapter.security.sop_template_signing import sop_template_from_json, sop_template_to_json
from domain.events import CanonicalPayload, SopTemplateMinted
from domain.ports.sop_template import SopTemplateSigner, SopTemplateVerifier
from domain.security import AdminPrincipal, DeveloperBootstrapPrincipal, Principal, SecurityRole
from domain.types.derivation import Semver, SopTemplateId
from domain.types.sop_template import (
    SopTemplate,
    SopTemplateRevocation,
    SopTemplateSignature,
    SopTemplateVersion,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS templates (
    template_id TEXT PRIMARY KEY,
    active_version TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    template_json TEXT NOT NULL,
    signing_key_version TEXT NOT NULL,
    signed_at_utc TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'revoked'))
);

CREATE TABLE IF NOT EXISTS template_versions (
    version_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id TEXT NOT NULL,
    version TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    template_json TEXT NOT NULL,
    signing_key_version TEXT NOT NULL,
    signed_at_utc TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE(template_id, version, content_hash)
);

CREATE TABLE IF NOT EXISTS template_revocations (
    revocation_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id TEXT NOT NULL,
    version TEXT NOT NULL,
    revoked_by_principal_id TEXT NOT NULL,
    revoked_at_utc TEXT NOT NULL,
    reason TEXT NOT NULL,
    UNIQUE(template_id, version)
);

CREATE INDEX IF NOT EXISTS idx_template_versions_template
ON template_versions(template_id, version_sequence DESC);
"""


class SopTemplateNotFoundError(KeyError):
    """Raised when a requested SOP template is absent or revoked."""


class SopTemplateAlreadyExistsError(ValueError):
    """Raised when minting would overwrite an active template."""


class SopTemplateBootstrapConfigurationError(RuntimeError):
    """Raised when bootstrap dependencies were not supplied."""


@dataclass(frozen=True)
class SqliteSopTemplateStore:
    path: Path
    _verifier: SopTemplateVerifier
    _signer: SopTemplateSigner | None
    _catalogue_dir: Path | None
    _schema_root: Path | None
    _governance_event_log: JsonlEventLog | None
    _clock: Callable[[], datetime]
    _event_sequence: int

    def __init__(
        self,
        path: str | Path,
        verifier: SopTemplateVerifier,
        *,
        signer: SopTemplateSigner | None = None,
        catalogue_dir: str | Path | None = None,
        schema_root: str | Path | None = None,
        governance_event_log: JsonlEventLog | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        db_path = Path(path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        object.__setattr__(self, "path", db_path)
        object.__setattr__(self, "_verifier", verifier)
        object.__setattr__(self, "_signer", signer)
        object.__setattr__(
            self,
            "_catalogue_dir",
            None if catalogue_dir is None else Path(catalogue_dir),
        )
        object.__setattr__(self, "_schema_root", None if schema_root is None else Path(schema_root))
        object.__setattr__(self, "_governance_event_log", governance_event_log)
        object.__setattr__(self, "_clock", clock or (lambda: datetime.now(UTC)))
        object.__setattr__(self, "_event_sequence", 0)
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def get_template(self, template_id: SopTemplateId) -> SopTemplate:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT template_json, status
                FROM templates
                WHERE template_id = ?
                """,
                (str(template_id),),
            ).fetchone()
        if row is None or str(row["status"]) != "active":
            raise SopTemplateNotFoundError(str(template_id))
        template = sop_template_from_json(str(row["template_json"]))
        self._require_valid_signature(template)
        return template

    def list_templates(self) -> tuple[SopTemplate, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT template_id FROM templates WHERE status = 'active' ORDER BY template_id"
            ).fetchall()
        return tuple(self.get_template(SopTemplateId(str(row["template_id"]))) for row in rows)

    def write_mint(
        self,
        template: SopTemplate,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateVersion:
        _require_template_admin(principal)
        if self._exists(str(template.template_id), include_revoked=False):
            raise SopTemplateAlreadyExistsError(str(template.template_id))
        return self._write_template(template)

    def write_modify(
        self,
        template: SopTemplate,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateVersion:
        _require_template_admin(principal)
        if not self._exists(str(template.template_id), include_revoked=False):
            raise SopTemplateNotFoundError(str(template.template_id))
        return self._write_template(template)

    def write_revoke(
        self,
        template_id: SopTemplateId,
        reason: str,
        principal: AdminPrincipal | DeveloperBootstrapPrincipal,
    ) -> SopTemplateRevocation:
        _require_template_admin(principal)
        clean_reason = reason.strip()
        if not clean_reason:
            raise ValueError("SOP-template revocation reason cannot be empty")
        template = self.get_template(template_id)
        revoked_at = self._clock()
        revocation = SopTemplateRevocation(
            template_id=template.template_id,
            version=template.version,
            revoked_by_principal_id=principal.id,
            revoked_at_utc=revoked_at,
            reason=clean_reason,
        )
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                UPDATE templates
                SET status = 'revoked'
                WHERE template_id = ?
                """,
                (str(template_id),),
            )
            connection.execute(
                """
                INSERT INTO template_revocations(
                    template_id,
                    version,
                    revoked_by_principal_id,
                    revoked_at_utc,
                    reason
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(template_id, version) DO NOTHING
                """,
                (
                    str(revocation.template_id),
                    str(revocation.version),
                    str(revocation.revoked_by_principal_id),
                    _datetime_to_json(revocation.revoked_at_utc),
                    revocation.reason,
                ),
            )
            connection.commit()
        return revocation

    def bootstrap_initial_templates(
        self,
        developer: DeveloperBootstrapPrincipal,
    ) -> tuple[SopTemplateVersion, ...]:
        if not developer.has_bootstrap_authority:
            raise PermissionError("SOP-template bootstrap requires DeveloperBootstrapPrincipal")
        if self._signer is None or self._catalogue_dir is None or self._schema_root is None:
            raise SopTemplateBootstrapConfigurationError(
                "bootstrap requires signer, catalogue_dir, and schema_root"
            )
        written: list[SopTemplateVersion] = []
        for template in self._catalogue_templates():
            signed = _with_signature(template, self._signer.sign(template, developer))
            if self._is_same_active_template(signed):
                continue
            version = self._write_template(signed)
            written.append(version)
            self._append_bootstrap_event(developer, "SopTemplateMinted", signed)
        return tuple(written)

    def _write_template(self, template: SopTemplate) -> SopTemplateVersion:
        self._require_valid_signature(template)
        assert template.signature is not None
        content_hash = str(template.content_hash())
        template_json = sop_template_to_json(template)
        created_at = self._clock()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                INSERT INTO template_versions(
                    template_id,
                    version,
                    content_hash,
                    template_json,
                    signing_key_version,
                    signed_at_utc,
                    created_at_utc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(template_id, version, content_hash) DO NOTHING
                """,
                (
                    str(template.template_id),
                    str(template.version),
                    content_hash,
                    template_json,
                    str(template.signature.signing_key_version),
                    _datetime_to_json(template.signature.signed_at_utc),
                    _datetime_to_json(created_at),
                ),
            )
            connection.execute(
                """
                INSERT INTO templates(
                    template_id,
                    active_version,
                    content_hash,
                    template_json,
                    signing_key_version,
                    signed_at_utc,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, 'active')
                ON CONFLICT(template_id) DO UPDATE SET
                    active_version = excluded.active_version,
                    content_hash = excluded.content_hash,
                    template_json = excluded.template_json,
                    signing_key_version = excluded.signing_key_version,
                    signed_at_utc = excluded.signed_at_utc,
                    status = 'active'
                """,
                (
                    str(template.template_id),
                    str(template.version),
                    content_hash,
                    template_json,
                    str(template.signature.signing_key_version),
                    _datetime_to_json(template.signature.signed_at_utc),
                ),
            )
            connection.commit()
        return SopTemplateVersion(
            template_id=template.template_id,
            version=template.version,
            content_hash=template.content_hash(),
            created_at_utc=created_at,
        )

    def _require_valid_signature(self, template: SopTemplate) -> None:
        if template.signature is None:
            raise ValueError("SOP template must be signed before persistence")
        result = self._verifier.verify(template)
        if not result.success:
            assert result.error is not None
            raise result.error

    def _exists(self, template_id: str, *, include_revoked: bool) -> bool:
        query = "SELECT status FROM templates WHERE template_id = ?"
        with self._connect() as connection:
            row = connection.execute(query, (template_id,)).fetchone()
        if row is None:
            return False
        return include_revoked or str(row["status"]) == "active"

    def _is_same_active_template(self, template: SopTemplate) -> bool:
        try:
            current = self.get_template(template.template_id)
        except SopTemplateNotFoundError:
            return False
        return (
            current.version == template.version
            and current.content_hash() == template.content_hash()
        )

    def _catalogue_templates(self) -> tuple[SopTemplate, ...]:
        assert self._catalogue_dir is not None
        assert self._schema_root is not None
        templates: list[SopTemplate] = []
        for path in sorted(self._catalogue_dir.glob("*.yaml")):
            document = load_catalogue(path, schema_for_catalogue(path, self._schema_root))
            for item in _expect_list(document.payload, "templates"):
                templates.append(_template_from_catalogue_item(item))
        return tuple(templates)

    def _append_bootstrap_event(
        self,
        developer: DeveloperBootstrapPrincipal,
        event_type: str,
        template: SopTemplate,
    ) -> None:
        if self._governance_event_log is None:
            return
        event = SopTemplateMinted(
            event_id=self._next_event_id(event_type),
            occurred_at_utc=self._clock(),
            actor_id=str(developer.id),
            institution_id=str(developer.institution),
            template_id=str(template.template_id),
            template_payload_hash=str(template.content_hash()),
            signed_template_payload=_signed_template_payload(template),
        )
        self._governance_event_log.append_event(str(developer.institution), event)

    def _next_event_id(self, prefix: str) -> str:
        next_sequence = self._event_sequence + 1
        object.__setattr__(self, "_event_sequence", next_sequence)
        return f"{prefix}-{next_sequence:06d}"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection


def _with_signature(template: SopTemplate, signature: SopTemplateSignature) -> SopTemplate:
    return SopTemplate(
        template_id=template.template_id,
        version=template.version,
        name=template.name,
        description=template.description,
        content_markdown=template.content_markdown,
        hazard_notes=template.hazard_notes,
        required_approval_gate=template.required_approval_gate,
        signature=signature,
    )


def _template_from_catalogue_item(raw: object) -> SopTemplate:
    data = _expect_dict(raw, "SOP-template catalogue item")
    return SopTemplate(
        template_id=SopTemplateId(_expect_str(data, "id")),
        version=Semver(_expect_str(data, "version")),
        name=_expect_str(data, "name"),
        description=_expect_str(data, "description"),
        content_markdown=_expect_str(data, "content_markdown"),
        hazard_notes=tuple(
            _expect_str(item, "hazard_notes") for item in _expect_list(data, "hazard_notes")
        ),
        required_approval_gate=_expect_str(data, "required_approval_gate"),
    )


def _require_template_admin(principal: Principal) -> AdminPrincipal | DeveloperBootstrapPrincipal:
    if isinstance(principal, AdminPrincipal) and principal.can_act_as(SecurityRole.ADMINISTRATOR):
        return principal
    if isinstance(principal, DeveloperBootstrapPrincipal) and principal.has_bootstrap_authority:
        return principal
    raise PermissionError("SOP-template write requires administrator or bootstrap authority")


def _signed_template_payload(template: SopTemplate) -> CanonicalPayload:
    if template.signature is None:
        raise ValueError("signed template payload requires signature")
    return (
        ("template_id", str(template.template_id)),
        ("version", str(template.version)),
        ("template_content_hash", str(template.signature.template_content_hash)),
        ("signing_key_version", str(template.signature.signing_key_version)),
        ("signed_at_utc", _datetime_to_json(template.signature.signed_at_utc)),
        ("signature_bytes_hex", template.signature.signature_bytes.hex()),
    )


def _expect_dict(raw: object, field_name: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise TypeError(f"{field_name} must be a JSON object")
    return dict(raw)


def _expect_list(data: dict[str, object], key: str) -> list[object]:
    value = data.get(key)
    if not isinstance(value, list):
        raise TypeError(f"{key} must be a list")
    return value


def _expect_str(data: dict[str, object] | object, key: str) -> str:
    value = data.get(key) if isinstance(data, dict) else data
    if not isinstance(value, str) or not value:
        raise TypeError(f"{key} must be a non-empty string")
    return value


def _datetime_to_json(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
