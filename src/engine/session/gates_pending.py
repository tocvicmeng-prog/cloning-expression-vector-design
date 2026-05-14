"""
module_id: engine.session.gates_pending
file: src/engine/session/gates_pending.py
task_id: T-309

Pending safety-gate predicate registry.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from domain.sequence import Sha256, sha256_text
from domain.types.derivation import GateName, PredicateVersion
from engine.session.state_machine import DesignSession

BLOCK_COMPILE = GateName("BlockCompile")
BLOCK_VENDOR_SUBMISSION = GateName("BlockVendorSubmission")
BLOCK_OPERATIONAL_PROTOCOL = GateName("BlockOperationalProtocol")
BLOCK_EXPORT = GateName("BlockExport")

SAFETY_GATES = (
    BLOCK_COMPILE,
    BLOCK_VENDOR_SUBMISSION,
    BLOCK_OPERATIONAL_PROTOCOL,
    BLOCK_EXPORT,
)


class GateState(Enum):
    PENDING_NOT_YET_ACTIVATED = "PENDING_NOT_YET_ACTIVATED"
    OPEN = "OPEN"
    BLOCKED = "BLOCKED"


class GatePredicateNotYetActivated(RuntimeError):
    """Raised when production code tries to evaluate a pending safety gate."""


class UnknownGateError(KeyError):
    """Raised when a gate lookup is not present in the registry."""


@dataclass(frozen=True)
class GateVerdict:
    gate: GateName
    state: GateState
    reason: str
    predicate_version: PredicateVersion
    predicate_content_hash: Sha256

    def __post_init__(self) -> None:
        if not str(self.gate):
            raise ValueError("gate cannot be empty")
        if not self.reason:
            raise ValueError("gate verdict reason cannot be empty")
        if not str(self.predicate_version):
            raise ValueError("predicate_version cannot be empty")
        if not str(self.predicate_content_hash):
            raise ValueError("predicate_content_hash cannot be empty")


GatePredicate = Callable[[DesignSession], GateVerdict]


@dataclass(frozen=True)
class GateRegistration:
    gate: GateName
    predicate_version: PredicateVersion
    predicate_content_hash: Sha256
    predicate: GatePredicate | None = None

    @property
    def is_pending(self) -> bool:
        return self.predicate is None

    def pending_verdict(self) -> GateVerdict:
        return GateVerdict(
            gate=self.gate,
            state=GateState.PENDING_NOT_YET_ACTIVATED,
            reason="gate predicate is pending until its owning task activates it",
            predicate_version=self.predicate_version,
            predicate_content_hash=self.predicate_content_hash,
        )

    def evaluate(self, session: DesignSession) -> GateVerdict:
        if self.predicate is None:
            raise GatePredicateNotYetActivated(str(self.gate))
        verdict = self.predicate(session)
        if verdict.gate != self.gate:
            raise ValueError("gate predicate returned a verdict for the wrong gate")
        if verdict.predicate_version != self.predicate_version:
            raise ValueError("gate predicate returned a mismatched predicate version")
        if verdict.predicate_content_hash != self.predicate_content_hash:
            raise ValueError("gate predicate returned a mismatched predicate content hash")
        return verdict


@dataclass(frozen=True)
class GatePredicateRegistry:
    registrations: dict[GateName, GateRegistration]

    @classmethod
    def with_pending_defaults(cls) -> GatePredicateRegistry:
        return cls(
            {
                gate: GateRegistration(
                    gate=gate,
                    predicate_version=PredicateVersion("0.0.0-pending"),
                    predicate_content_hash=sha256_text(f"{gate}:pending"),
                )
                for gate in SAFETY_GATES
            }
        )

    def activate(
        self,
        gate: GateName,
        predicate: GatePredicate,
        *,
        version: PredicateVersion,
        content_hash: Sha256,
    ) -> GatePredicateRegistry:
        self._require_known(gate)
        updated = dict(self.registrations)
        updated[gate] = GateRegistration(
            gate=gate,
            predicate_version=version,
            predicate_content_hash=content_hash,
            predicate=predicate,
        )
        return GatePredicateRegistry(updated)

    def verdict(
        self,
        gate: GateName,
        session: DesignSession,
        *,
        allow_pending: bool = False,
    ) -> GateVerdict:
        registration = self._require_known(gate)
        if registration.is_pending and allow_pending:
            return registration.pending_verdict()
        return registration.evaluate(session)

    def environment_versions(self) -> dict[GateName, PredicateVersion]:
        return {gate: item.predicate_version for gate, item in self.registrations.items()}

    def environment_content_hashes(self) -> dict[GateName, Sha256]:
        return {gate: item.predicate_content_hash for gate, item in self.registrations.items()}

    def _require_known(self, gate: GateName) -> GateRegistration:
        try:
            return self.registrations[gate]
        except KeyError as exc:
            raise UnknownGateError(str(gate)) from exc


def open_verdict(
    gate: GateName,
    version: PredicateVersion,
    content_hash: Sha256,
    reason: str = "gate predicate allowed the session",
) -> GateVerdict:
    return GateVerdict(
        gate=gate,
        state=GateState.OPEN,
        reason=reason,
        predicate_version=version,
        predicate_content_hash=content_hash,
    )


def blocked_verdict(
    gate: GateName,
    version: PredicateVersion,
    content_hash: Sha256,
    reason: str,
) -> GateVerdict:
    return GateVerdict(
        gate=gate,
        state=GateState.BLOCKED,
        reason=reason,
        predicate_version=version,
        predicate_content_hash=content_hash,
    )
