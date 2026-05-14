"""
module_id: engine.export_gate
file: src/engine/export_gate.py
task_id: T-903

Final export readiness safety-gate predicate.
"""

from __future__ import annotations

from collections.abc import Callable

from domain.sequence import Sha256, sha256_text
from domain.types.derivation import PredicateVersion
from engine.screening_gate import SCREENING_OPEN_VERDICTS
from engine.session import (
    BLOCK_EXPORT,
    DesignSession,
    GatePredicateRegistry,
    GateRegistration,
    GateState,
    GateVerdict,
    SessionState,
    blocked_verdict,
    open_verdict,
)

MODULE_ID = "engine.export_gate"
OWNING_TASKS = ("T-903",)

EXPORT_GATE_VERSION = PredicateVersion("1.0.0-t903-final-export-readiness")
EXPORT_GATE_HASH = sha256_text("T-903:final-export-readiness")


def activate_final_export_gate(
    registry: GatePredicateRegistry,
    *,
    version: PredicateVersion = EXPORT_GATE_VERSION,
    content_hash: Sha256 = EXPORT_GATE_HASH,
) -> GatePredicateRegistry:
    prior_export_registration = registry.registrations[BLOCK_EXPORT]
    return registry.activate(
        BLOCK_EXPORT,
        _export_predicate(
            prior_export_registration,
            version=version,
            content_hash=content_hash,
        ),
        version=version,
        content_hash=content_hash,
    )


def final_export_gate_allows_bundle(verdict: GateVerdict) -> bool:
    if verdict.gate != BLOCK_EXPORT:
        raise ValueError("verdict is not for BlockExport")
    return verdict.state is GateState.OPEN


def _export_predicate(
    prior_registration: GateRegistration,
    *,
    version: PredicateVersion,
    content_hash: Sha256,
) -> Callable[[DesignSession], GateVerdict]:
    def predicate(session: DesignSession) -> GateVerdict:
        if not prior_registration.is_pending:
            prior = prior_registration.evaluate(session)
            if prior.state is GateState.BLOCKED:
                return blocked_verdict(
                    BLOCK_EXPORT,
                    version,
                    content_hash,
                    reason=f"export_blocked_by_existing_predicate:{prior.reason}",
                )
        return _final_export_readiness(session, version=version, content_hash=content_hash)

    return predicate


def _final_export_readiness(
    session: DesignSession,
    *,
    version: PredicateVersion,
    content_hash: Sha256,
) -> GateVerdict:
    screening_verdict = session.screening_verdict
    if screening_verdict is None:
        return blocked_verdict(
            BLOCK_EXPORT,
            version,
            content_hash,
            reason="screening verdict is missing",
        )
    normalized_verdict = screening_verdict.upper()
    if normalized_verdict not in SCREENING_OPEN_VERDICTS:
        return blocked_verdict(
            BLOCK_EXPORT,
            version,
            content_hash,
            reason=f"screening_verdict_blocks:{normalized_verdict}",
        )
    if not session.authorisation_profile_id:
        return blocked_verdict(
            BLOCK_EXPORT,
            version,
            content_hash,
            reason="operational protocol authorisation is missing",
        )
    if not session.decision_record_hash:
        return blocked_verdict(
            BLOCK_EXPORT,
            version,
            content_hash,
            reason="authorisation decision record hash is missing",
        )
    if not session.sop_bundle_hash:
        return blocked_verdict(
            BLOCK_EXPORT,
            version,
            content_hash,
            reason="SOP rendered evidence is missing",
        )
    if session.state is not SessionState.READY_TO_EXPORT:
        return blocked_verdict(
            BLOCK_EXPORT,
            version,
            content_hash,
            reason=f"session state is not ready for export:{session.state.value}",
        )
    return open_verdict(
        BLOCK_EXPORT,
        version,
        content_hash,
        reason="screening, authorisation, and SOP evidence permit final export",
    )


__all__ = [
    "EXPORT_GATE_HASH",
    "EXPORT_GATE_VERSION",
    "activate_final_export_gate",
    "final_export_gate_allows_bundle",
]
