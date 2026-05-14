"""
module_id: engine.session.predicate_versioning
file: src/engine/session/predicate_versioning.py
task_id: T-309

Gate-predicate version selection for deterministic replay.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.sequence import Sha256, sha256_text
from domain.types.derivation import DerivationEnvironment, GateName, PredicateVersion


class PredicateVersionUnavailable(ValueError):
    """Raised when replay requests a predicate version that is not registered."""


@dataclass(frozen=True)
class PredicateRegistration:
    gate: GateName
    predicate_version: PredicateVersion
    predicate_content_hash: Sha256
    canonical_source: str

    def __post_init__(self) -> None:
        if not str(self.gate):
            raise ValueError("gate cannot be empty")
        if not str(self.predicate_version):
            raise ValueError("predicate_version cannot be empty")
        if not str(self.predicate_content_hash):
            raise ValueError("predicate_content_hash cannot be empty")
        if not self.canonical_source:
            raise ValueError("canonical_source cannot be empty")


@dataclass(frozen=True)
class PredicateVersionHistory:
    registrations: tuple[PredicateRegistration, ...]

    def registration_for(
        self,
        gate: GateName,
        predicate_version: PredicateVersion,
        predicate_content_hash: Sha256,
    ) -> PredicateRegistration:
        for registration in self.registrations:
            if (
                registration.gate == gate
                and registration.predicate_version == predicate_version
                and registration.predicate_content_hash == predicate_content_hash
            ):
                return registration
        raise PredicateVersionUnavailable(
            f"no predicate registered for {gate} {predicate_version} {predicate_content_hash}"
        )

    def registration_for_environment(
        self,
        gate: GateName,
        environment: DerivationEnvironment,
    ) -> PredicateRegistration:
        try:
            version = environment.gate_predicate_versions[gate]
            content_hash = environment.gate_predicate_content_hashes[gate]
        except KeyError as exc:
            raise PredicateVersionUnavailable(
                f"derivation environment has no predicate metadata for {gate}"
            ) from exc
        return self.registration_for(gate, version, content_hash)

    def with_registration(self, registration: PredicateRegistration) -> PredicateVersionHistory:
        return PredicateVersionHistory((*self.registrations, registration))


def predicate_content_hash(canonical_source: str) -> Sha256:
    return sha256_text(canonical_source)
