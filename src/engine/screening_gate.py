"""
module_id: engine.screening_gate
file: src/engine/screening_gate.py
task_id: T-1002

Screening-verdict safety-gate predicates.
"""

from __future__ import annotations

from collections.abc import Callable

from domain.sequence import Sha256, sha256_text
from domain.types.derivation import GateName, PredicateVersion
from engine.session import (
    BLOCK_EXPORT,
    BLOCK_VENDOR_SUBMISSION,
    DesignSession,
    GatePredicateRegistry,
    GateRegistration,
    GateState,
    GateVerdict,
    blocked_verdict,
    open_verdict,
)

SCREENING_GATE_VERSION = PredicateVersion("1.0.0-t1002-screening-verdict")
SCREENING_GATE_HASH = sha256_text("T-1002:screening-verdict")
SCREENING_BLOCKING_VERDICTS = frozenset(
    {"HIT", "WATCHLIST", "MANUAL_REVIEW_REQUIRED", "UNAVAILABLE"}
)
SCREENING_OPEN_VERDICTS = frozenset({"CLEAR", "NOT_APPLICABLE"})


def activate_screening_verdict_gates(
    registry: GatePredicateRegistry,
    *,
    version: PredicateVersion = SCREENING_GATE_VERSION,
    content_hash: Sha256 = SCREENING_GATE_HASH,
) -> GatePredicateRegistry:
    prior_vendor_registration = registry.registrations[BLOCK_VENDOR_SUBMISSION]
    with_vendor = registry.activate(
        BLOCK_VENDOR_SUBMISSION,
        _vendor_submission_predicate(
            prior_vendor_registration,
            version=version,
            content_hash=content_hash,
        ),
        version=version,
        content_hash=content_hash,
    )
    return with_vendor.activate(
        BLOCK_EXPORT,
        _export_predicate(version=version, content_hash=content_hash),
        version=version,
        content_hash=content_hash,
    )


def screening_verdict_allows_vendor_submission(verdict: GateVerdict) -> bool:
    if verdict.gate != BLOCK_VENDOR_SUBMISSION:
        raise ValueError("verdict is not for BlockVendorSubmission")
    return verdict.state is GateState.OPEN


def screening_verdict_allows_export(verdict: GateVerdict) -> bool:
    if verdict.gate != BLOCK_EXPORT:
        raise ValueError("verdict is not for BlockExport")
    return verdict.state is GateState.OPEN


def _vendor_submission_predicate(
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
                    BLOCK_VENDOR_SUBMISSION,
                    version,
                    content_hash,
                    reason=f"vendor_submission_blocked_by_existing_predicate:{prior.reason}",
                )
        return _screening_verdict(
            BLOCK_VENDOR_SUBMISSION,
            session,
            version=version,
            content_hash=content_hash,
            open_reason="screening verdict permits vendor submission",
        )

    return predicate


def _export_predicate(
    *,
    version: PredicateVersion,
    content_hash: Sha256,
) -> Callable[[DesignSession], GateVerdict]:
    def predicate(session: DesignSession) -> GateVerdict:
        return _screening_verdict(
            BLOCK_EXPORT,
            session,
            version=version,
            content_hash=content_hash,
            open_reason="screening verdict permits export subject to downstream gates",
        )

    return predicate


def _screening_verdict(
    gate: GateName,
    session: DesignSession,
    *,
    version: PredicateVersion,
    content_hash: Sha256,
    open_reason: str,
) -> GateVerdict:
    verdict = session.screening_verdict
    if verdict is None:
        return blocked_verdict(
            gate,
            version,
            content_hash,
            reason="screening verdict is missing",
        )
    normalized = verdict.upper()
    if normalized in SCREENING_BLOCKING_VERDICTS:
        return blocked_verdict(
            gate,
            version,
            content_hash,
            reason=f"screening_verdict_blocks:{normalized}",
        )
    if normalized in SCREENING_OPEN_VERDICTS:
        return open_verdict(gate, version, content_hash, reason=open_reason)
    return blocked_verdict(
        gate,
        version,
        content_hash,
        reason=f"screening verdict is unsupported:{normalized}",
    )
