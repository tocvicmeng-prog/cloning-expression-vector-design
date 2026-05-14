"""
module_id: tests.engine.test_export_gate_t903
file: tests/engine/test_export_gate_t903.py
task_id: T-903
"""

from __future__ import annotations

from engine.export_gate import activate_final_export_gate, final_export_gate_allows_bundle
from engine.screening_gate import activate_screening_verdict_gates
from engine.session import (
    BLOCK_EXPORT,
    DesignSession,
    GatePredicateRegistry,
    GateState,
    SessionState,
)


def test_final_export_gate_blocks_missing_screening_authorisation_and_sop() -> None:
    registry = activate_final_export_gate(GatePredicateRegistry.with_pending_defaults())

    missing_screening = registry.verdict(
        BLOCK_EXPORT,
        DesignSession(session_id="session-1", state=SessionState.READY_TO_EXPORT),
    )
    assert missing_screening.state is GateState.BLOCKED
    assert missing_screening.reason == "screening verdict is missing"

    missing_authorisation = registry.verdict(
        BLOCK_EXPORT,
        DesignSession(
            session_id="session-1",
            state=SessionState.READY_TO_EXPORT,
            screening_verdict="CLEAR",
        ),
    )
    assert missing_authorisation.state is GateState.BLOCKED
    assert missing_authorisation.reason == "operational protocol authorisation is missing"

    missing_sop = registry.verdict(
        BLOCK_EXPORT,
        DesignSession(
            session_id="session-1",
            state=SessionState.AWAITING_SOP_RENDER,
            screening_verdict="CLEAR",
            authorisation_profile_id="auth-profile-1",
            decision_record_hash="decision",
        ),
    )
    assert missing_sop.state is GateState.BLOCKED
    assert missing_sop.reason == "SOP rendered evidence is missing"


def test_final_export_gate_opens_when_all_evidence_is_present() -> None:
    registry = activate_final_export_gate(GatePredicateRegistry.with_pending_defaults())

    verdict = registry.verdict(
        BLOCK_EXPORT,
        DesignSession(
            session_id="session-1",
            state=SessionState.READY_TO_EXPORT,
            screening_verdict="CLEAR",
            authorisation_profile_id="auth-profile-1",
            decision_record_hash="decision",
            sop_bundle_hash="sop-bundle",
        ),
    )

    assert final_export_gate_allows_bundle(verdict)
    assert verdict.reason == "screening, authorisation, and SOP evidence permit final export"


def test_final_export_gate_composes_screening_export_predicate() -> None:
    registry = activate_screening_verdict_gates(GatePredicateRegistry.with_pending_defaults())
    registry = activate_final_export_gate(registry)

    verdict = registry.verdict(
        BLOCK_EXPORT,
        DesignSession(
            session_id="session-1",
            state=SessionState.READY_TO_EXPORT,
            screening_verdict="HIT",
            authorisation_profile_id="auth-profile-1",
            decision_record_hash="decision",
            sop_bundle_hash="sop-bundle",
        ),
    )

    assert verdict.state is GateState.BLOCKED
    assert verdict.reason == "export_blocked_by_existing_predicate:screening_verdict_blocks:HIT"
