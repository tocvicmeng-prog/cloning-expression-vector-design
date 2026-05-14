"""
module_id: adapter.persistence.sqlite_authorisation_store_read
file: src/adapter/persistence/sqlite_authorisation_store_read.py
task_id: T-310

Read-only SQLite authorisation profile store with verifier-on-load.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from domain.ports.profile_signing import AuthorisationProfileVerifier
from domain.security import (
    AdminId,
    AuthorisationProfile,
    AuthProfileId,
    CoveredBiologicalScope,
    ExportClass,
    InstitutionId,
    KeyVersionId,
    OperationalRole,
    PrincipalId,
    ProfileSignature,
    SopLibraryId,
    UserId,
)
from domain.sequence import Sha256
from domain.types import AssemblyMethodId, BiosafetyTier, ChassisClass, DownstreamUse

Payload = tuple[tuple[str, str], ...]

SCHEMA = """
CREATE TABLE IF NOT EXISTS authorisation_profiles (
    profile_id TEXT PRIMARY KEY,
    subject_user_id TEXT NOT NULL,
    profile_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_authorisation_profiles_subject
ON authorisation_profiles(subject_user_id);
"""


class AuthorisationProfileNotFoundError(KeyError):
    """Raised when an authorisation profile is absent."""


class AuthorisationProfileTamperDetectedError(ValueError):
    """Raised when a stored profile fails institutional signature verification."""


@dataclass(frozen=True)
class SqliteAuthorisationStoreRead:
    path: Path
    verifier: AuthorisationProfileVerifier

    def __init__(self, path: str | Path, verifier: AuthorisationProfileVerifier) -> None:
        object.__setattr__(self, "path", Path(path))
        object.__setattr__(self, "verifier", verifier)

    def get(self, profile_id: str) -> AuthorisationProfile:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT profile_json FROM authorisation_profiles WHERE profile_id = ?",
                (profile_id,),
            ).fetchone()
        if row is None:
            raise AuthorisationProfileNotFoundError(profile_id)
        return self._verified_profile(str(row[0]))

    def read_own_profile(self, principal_id: str) -> AuthorisationProfile:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT profile_json FROM authorisation_profiles
                WHERE subject_user_id = ?
                ORDER BY profile_id
                LIMIT 1
                """,
                (principal_id,),
            ).fetchone()
        if row is None:
            raise AuthorisationProfileNotFoundError(principal_id)
        return self._verified_profile(str(row[0]))

    def list_for_admin(self, _admin_principal: Payload) -> tuple[Payload, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT profile_json FROM authorisation_profiles ORDER BY profile_id"
            ).fetchall()
        return tuple(_profile_to_payload(self._verified_profile(str(row[0]))) for row in rows)

    def _verified_profile(self, profile_json: str) -> AuthorisationProfile:
        try:
            profile = profile_from_json(profile_json)
        except ValueError as exc:
            raise AuthorisationProfileTamperDetectedError(str(exc)) from exc
        result = self.verifier.verify(profile)
        if not result.success:
            raise AuthorisationProfileTamperDetectedError(str(result.error))
        return profile

    def _connect(self) -> sqlite3.Connection:
        uri = f"file:{self.path.as_posix()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        connection.execute("PRAGMA query_only=ON")
        return connection


def initialise_authorisation_schema(path: str | Path) -> None:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)


def profile_to_json(profile: AuthorisationProfile) -> str:
    return json.dumps(
        {
            "content": profile.to_content_payload(),
            "profile_content_hash": str(profile.profile_content_hash),
            "profile_signature": {
                "signed_payload_hash": str(profile.profile_signature.signed_payload_hash),
                "signature_bytes_hex": profile.profile_signature.signature_bytes.hex(),
                "signing_key_version": str(profile.profile_signature.signing_key_version),
                "signed_at_utc": _datetime_to_utc_iso(profile.profile_signature.signed_at_utc),
            },
            "profile_signature_key_version": str(profile.profile_signature_key_version),
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def profile_from_json(payload: str) -> AuthorisationProfile:
    data = _expect_dict(json.loads(payload), "profile")
    content = _expect_dict(data.get("content"), "content")
    signature_data = _expect_dict(data.get("profile_signature"), "profile_signature")
    return AuthorisationProfile(
        profile_id=AuthProfileId(_expect_str(content, "profile_id")),
        subject_user_id=UserId(_expect_str(content, "subject_user_id")),
        issued_by_admin_id=AdminId(_expect_str(content, "issued_by_admin_id")),
        issuer_principal_id=PrincipalId(_expect_str(content, "issuer_principal_id")),
        institution=InstitutionId(_expect_str(content, "institution")),
        profile_version=_expect_int(content, "profile_version"),
        valid_from=_parse_datetime(_expect_str(content, "valid_from")),
        valid_until=_parse_datetime(_expect_str(content, "valid_until")),
        covered_scope=_scope_from_dict(_expect_dict(content.get("covered_scope"), "covered_scope")),
        profile_content_hash=Sha256(_expect_str(data, "profile_content_hash")),
        profile_signature=ProfileSignature(
            signed_payload_hash=Sha256(_expect_str(signature_data, "signed_payload_hash")),
            signature_bytes=bytes.fromhex(_expect_str(signature_data, "signature_bytes_hex")),
            signing_key_version=KeyVersionId(_expect_str(signature_data, "signing_key_version")),
            signed_at_utc=_parse_datetime(_expect_str(signature_data, "signed_at_utc")),
        ),
        profile_signature_key_version=KeyVersionId(
            _expect_str(data, "profile_signature_key_version")
        ),
        additional_constraints=tuple(
            _expect_str_item(item, "additional_constraints")
            for item in _expect_list(
                content.get("additional_constraints"), "additional_constraints"
            )
        ),
        revoked_at=_optional_datetime(content.get("revoked_at")),
        revocation_reason=_optional_str(content.get("revocation_reason"), "revocation_reason"),
    )


def _scope_from_dict(data: dict[str, object]) -> CoveredBiologicalScope:
    insert_size = data.get("insert_size_range_bp")
    return CoveredBiologicalScope(
        covered_biosafety_tiers=frozenset(
            BiosafetyTier(item)
            for item in _expect_str_list(
                data.get("covered_biosafety_tiers"), "covered_biosafety_tiers"
            )
        ),
        covered_host_classes=frozenset(
            ChassisClass(item)
            for item in _expect_str_list(data.get("covered_host_classes"), "covered_host_classes")
        ),
        covered_assembly_chemistries=frozenset(
            AssemblyMethodId(item)
            for item in _expect_str_list(
                data.get("covered_assembly_chemistries"),
                "covered_assembly_chemistries",
            )
        ),
        covered_downstream_uses=frozenset(
            DownstreamUse(item)
            for item in _expect_str_list(
                data.get("covered_downstream_uses"), "covered_downstream_uses"
            )
        ),
        covered_sop_libraries=frozenset(
            SopLibraryId(item)
            for item in _expect_str_list(data.get("covered_sop_libraries"), "covered_sop_libraries")
        ),
        covered_vendor_submission=_expect_bool(data, "covered_vendor_submission"),
        covered_export_classes=frozenset(
            ExportClass(item)
            for item in _expect_str_list(
                data.get("covered_export_classes"), "covered_export_classes"
            )
        ),
        role_of_operation_allowed=frozenset(
            OperationalRole(item)
            for item in _expect_str_list(
                data.get("role_of_operation_allowed"),
                "role_of_operation_allowed",
            )
        ),
        cargo_classes=frozenset(_expect_str_list(data.get("cargo_classes"), "cargo_classes")),
        vector_system_classes=frozenset(
            _expect_str_list(data.get("vector_system_classes"), "vector_system_classes")
        ),
        replication_competence=frozenset(
            _expect_str_list(data.get("replication_competence"), "replication_competence")
        ),
        insert_size_range_bp=None
        if insert_size is None
        else _expect_int_pair(insert_size, "insert_size_range_bp"),
        target_organisms=frozenset(
            _expect_str_list(data.get("target_organisms"), "target_organisms")
        ),
        screening_exception_classes=frozenset(
            _expect_str_list(data.get("screening_exception_classes"), "screening_exception_classes")
        ),
        institutional_protocol_ids=frozenset(
            _expect_str_list(data.get("institutional_protocol_ids"), "institutional_protocol_ids")
        ),
        jurisdictions=frozenset(_expect_str_list(data.get("jurisdictions"), "jurisdictions")),
        component_lineage_trust=frozenset(
            _expect_str_list(data.get("component_lineage_trust"), "component_lineage_trust")
        ),
    )


def _profile_to_payload(profile: AuthorisationProfile) -> Payload:
    return (
        ("profile_id", str(profile.profile_id)),
        ("subject_user_id", str(profile.subject_user_id)),
        ("profile_content_hash", str(profile.profile_content_hash)),
    )


def _expect_dict(raw: object, name: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise TypeError(f"{name} must be a JSON object")
    return dict(raw)


def _expect_str(data: dict[str, object], key: str) -> str:
    return _expect_str_item(data.get(key), key)


def _expect_str_item(raw: object, name: str) -> str:
    if not isinstance(raw, str):
        raise TypeError(f"{name} must be a string")
    return raw


def _expect_int(data: dict[str, object], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{key} must be an integer")
    return value


def _expect_bool(data: dict[str, object], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a boolean")
    return value


def _expect_list(raw: object, name: str) -> list[object]:
    if not isinstance(raw, list):
        raise TypeError(f"{name} must be a list")
    return raw


def _expect_str_list(raw: object, name: str) -> list[str]:
    return [_expect_str_item(item, name) for item in _expect_list(raw, name)]


def _expect_int_pair(raw: object, name: str) -> tuple[int, int]:
    values = _expect_list(raw, name)
    if len(values) != 2:
        raise TypeError(f"{name} must contain two integers")
    left, right = values
    if not isinstance(left, int) or not isinstance(right, int):
        raise TypeError(f"{name} must contain two integers")
    return left, right


def _optional_datetime(raw: object) -> datetime | None:
    if raw is None:
        return None
    return _parse_datetime(_expect_str_item(raw, "datetime"))


def _optional_str(raw: object, name: str) -> str | None:
    if raw is None:
        return None
    return _expect_str_item(raw, name)


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _datetime_to_utc_iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
