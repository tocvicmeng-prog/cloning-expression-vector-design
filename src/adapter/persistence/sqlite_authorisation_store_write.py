"""
module_id: adapter.persistence.sqlite_authorisation_store_write
file: src/adapter/persistence/sqlite_authorisation_store_write.py
task_id: T-311

Admin-service write side for authorisation profiles.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from adapter.persistence.sqlite_authorisation_store_read import (
    SCHEMA,
    profile_from_json,
    profile_to_json,
)
from domain.security import (
    AdminPrincipal,
    AuthorisationProfile,
    DeveloperBootstrapPrincipal,
    Principal,
    SecurityRole,
)


class AlreadyBootstrappedError(RuntimeError):
    """Raised when initial-admin bootstrap is attempted more than once."""


class AuthorisationProfileAlreadyExistsError(ValueError):
    """Raised when mint attempts to overwrite an existing profile."""


@dataclass(frozen=True)
class SqliteAuthorisationStoreWrite:
    path: Path

    def __init__(self, path: str | Path) -> None:
        db_path = Path(path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        object.__setattr__(self, "path", db_path)
        with self._connect() as connection:
            connection.executescript(SCHEMA)
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS authorisation_bootstrap_state (
                    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
                    bootstrapped_profile_id TEXT NOT NULL
                )
                """
            )

    def write_mint(self, profile: AuthorisationProfile, principal: AdminPrincipal) -> str:
        _require_admin(principal)
        if self._exists(str(profile.profile_id)):
            raise AuthorisationProfileAlreadyExistsError(str(profile.profile_id))
        self._write_profile(profile)
        return str(profile.profile_id)

    def write_modify(self, profile: AuthorisationProfile, principal: AdminPrincipal) -> str:
        _require_admin(principal)
        self._write_profile(profile)
        return str(profile.profile_id)

    def write_revoke(self, profile: AuthorisationProfile, principal: AdminPrincipal) -> str:
        _require_admin(principal)
        if profile.revoked_at is None:
            raise ValueError("revoked profile must include revoked_at")
        self._write_profile(profile)
        return str(profile.profile_id)

    def bootstrap_initial_admin(
        self,
        developer: DeveloperBootstrapPrincipal,
        profile: AuthorisationProfile,
    ) -> str:
        if not developer.has_bootstrap_authority:
            raise PermissionError("bootstrap requires DeveloperBootstrapPrincipal")
        with self._connect() as connection:
            if self.is_bootstrapped():
                raise AlreadyBootstrappedError("authorisation store is already bootstrapped")
            connection.execute("BEGIN IMMEDIATE")
            self._write_profile(profile, connection=connection)
            connection.execute(
                """
                INSERT INTO authorisation_bootstrap_state(singleton_id, bootstrapped_profile_id)
                VALUES (1, ?)
                """,
                (str(profile.profile_id),),
            )
            connection.commit()
        return str(profile.profile_id)

    def get_profile(self, profile_id: str) -> AuthorisationProfile:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT profile_json FROM authorisation_profiles WHERE profile_id = ?",
                (profile_id,),
            ).fetchone()
        if row is None:
            raise KeyError(profile_id)
        return profile_from_json(str(row[0]))

    def list_profiles(self) -> tuple[AuthorisationProfile, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT profile_json FROM authorisation_profiles ORDER BY profile_id"
            ).fetchall()
        return tuple(profile_from_json(str(row[0])) for row in rows)

    def is_bootstrapped(self) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM authorisation_bootstrap_state WHERE singleton_id = 1"
            ).fetchone()
        return row is not None

    def _write_profile(
        self,
        profile: AuthorisationProfile,
        *,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        owns_connection = connection is None
        active = connection if connection is not None else self._connect()
        try:
            if owns_connection:
                active.execute("BEGIN IMMEDIATE")
            active.execute(
                """
                INSERT INTO authorisation_profiles(profile_id, subject_user_id, profile_json)
                VALUES (?, ?, ?)
                ON CONFLICT(profile_id) DO UPDATE SET
                    subject_user_id = excluded.subject_user_id,
                    profile_json = excluded.profile_json
                """,
                (str(profile.profile_id), str(profile.subject_user_id), profile_to_json(profile)),
            )
            if owns_connection:
                active.commit()
        finally:
            if owns_connection:
                active.close()

    def _exists(self, profile_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM authorisation_profiles WHERE profile_id = ?",
                (profile_id,),
            ).fetchone()
        return row is not None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection


def _require_admin(principal: Principal) -> None:
    if not principal.can_act_as(SecurityRole.ADMINISTRATOR):
        raise PermissionError("authorisation writes require administrator")
