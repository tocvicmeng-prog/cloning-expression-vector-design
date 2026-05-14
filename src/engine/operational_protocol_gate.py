"""
module_id: engine.operational_protocol_gate
file: src/engine/operational_protocol_gate.py
task_id: T-806b

BlockOperationalProtocol safety-gate predicate.
"""

from __future__ import annotations

from domain.sequence import Sha256, sha256_text
from domain.types.derivation import PredicateVersion
from engine.session import (
    BLOCK_OPERATIONAL_PROTOCOL,
    DesignSession,
    GatePredicateRegistry,
    GateState,
    GateVerdict,
    blocked_verdict,
    open_verdict,
)

OPERATIONAL_PROTOCOL_GATE_VERSION = PredicateVersion("1.0.0-t806b-authorisation-decision")
OPERATIONAL_PROTOCOL_GATE_HASH = sha256_text("T-806b:block-operational-protocol")
AUTHORISATION_OPEN_SCREENING_VERDICTS = frozenset(
    {"CLEAR", "NOT_APPLICABLE", "WATCHLIST", "MANUAL_REVIEW_REQUIRED", "UNAVAILABLE"}
)


def activate_block_operational_protocol_gate(
    registry: GatePredicateRegistry,
    *,
    version: PredicateVersion = OPERATIONAL_PROTOCOL_GATE_VERSION,
    content_hash: Sha256 = OPERATIONAL_PROTOCOL_GATE_HASH,
) -> GatePredicateRegistry:
    def predicate(session: DesignSession) -> GateVerdict:
        if session.authorisation_profile_id is None:
            return blocked_verdict(
                BLOCK_OPERATIONAL_PROTOCOL,
                version,
                content_hash,
                reason="operational authorisation profile is missing",
            )
        if session.decision_record_hash is None:
            return blocked_verdict(
                BLOCK_OPERATIONAL_PROTOCOL,
                version,
                content_hash,
                reason="operational authorisation decision record is missing",
            )
        screening_verdict = session.screening_verdict
        if screening_verdict is None:
            return blocked_verdict(
                BLOCK_OPERATIONAL_PROTOCOL,
                version,
                content_hash,
                reason="screening verdict is missing",
            )
        normalized = screening_verdict.upper()
        if normalized not in AUTHORISATION_OPEN_SCREENING_VERDICTS:
            return blocked_verdict(
                BLOCK_OPERATIONAL_PROTOCOL,
                version,
                content_hash,
                reason=f"screening_verdict_blocks_operational_protocol:{normalized}",
            )
        return open_verdict(
            BLOCK_OPERATIONAL_PROTOCOL,
            version,
            content_hash,
            reason="operational protocol authorisation is present",
        )

    return registry.activate(
        BLOCK_OPERATIONAL_PROTOCOL,
        predicate,
        version=version,
        content_hash=content_hash,
    )


def operational_protocol_allows_render(verdict: GateVerdict) -> bool:
    if verdict.gate != BLOCK_OPERATIONAL_PROTOCOL:
        raise ValueError("verdict is not for BlockOperationalProtocol")
    return verdict.state is GateState.OPEN


__all__ = [
    "OPERATIONAL_PROTOCOL_GATE_HASH",
    "OPERATIONAL_PROTOCOL_GATE_VERSION",
    "activate_block_operational_protocol_gate",
    "operational_protocol_allows_render",
]
