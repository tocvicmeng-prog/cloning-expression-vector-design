"""
module_id: tests.adapter.persistence.test_sqlite_authorisation_store_read
file: tests/adapter/persistence/test_sqlite_authorisation_store_read.py
task_id: T-310
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from adapter.persistence import (
    AuthorisationProfileTamperDetectedError,
    SqliteAuthorisationStoreRead,
    initialise_authorisation_schema,
    profile_to_json,
)
from tests.fakes.security.profile_signing.fixtures import (
    admin_principal,
    signed_profile,
    unsigned_profile,
)
from tests.fakes.security.profile_signing.signers import FakeProfileSigner, FakeProfileVerifier


def _signed_profile_json() -> str:
    base = unsigned_profile()
    signature = FakeProfileSigner().sign(base, admin_principal())
    return profile_to_json(signed_profile(signature))


def _seed_profile(path: Path, profile_json: str | None = None) -> None:
    initialise_authorisation_schema(path)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            INSERT INTO authorisation_profiles(profile_id, subject_user_id, profile_json)
            VALUES (?, ?, ?)
            """,
            ("profile-1", "user-1", profile_json or _signed_profile_json()),
        )


def test_sqlite_authorisation_read_verifies_profile_on_load(tmp_path: Path) -> None:
    path = tmp_path / "authorisation.sqlite"
    _seed_profile(path)
    store = SqliteAuthorisationStoreRead(path, FakeProfileVerifier())

    profile = store.get("profile-1")

    assert str(profile.profile_id) == "profile-1"
    assert store.read_own_profile("user-1") == profile
    assert dict(store.list_for_admin((("admin", "admin-1"),))[0])["subject_user_id"] == "user-1"


def test_sqlite_authorisation_read_rejects_tampered_profile(tmp_path: Path) -> None:
    path = tmp_path / "authorisation.sqlite"
    payload = json.loads(_signed_profile_json())
    payload["profile_signature"]["signature_bytes_hex"] = "00"
    _seed_profile(path, json.dumps(payload, sort_keys=True, separators=(",", ":")))
    store = SqliteAuthorisationStoreRead(path, FakeProfileVerifier())

    with pytest.raises(AuthorisationProfileTamperDetectedError, match="signature"):
        store.get("profile-1")


def test_authorisation_sqlite_is_opened_read_only(tmp_path: Path) -> None:
    path = tmp_path / "authorisation.sqlite"
    _seed_profile(path)
    store = SqliteAuthorisationStoreRead(path, FakeProfileVerifier())

    assert str(store.get("profile-1").profile_id) == "profile-1"
    with (
        sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection,
        pytest.raises(sqlite3.OperationalError, match="readonly"),
    ):
        connection.execute(
            """
            INSERT INTO authorisation_profiles(profile_id, subject_user_id, profile_json)
            VALUES ('x', 'x', '{}')
            """
        )
