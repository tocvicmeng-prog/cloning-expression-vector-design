"""
module_id: tests.engine.test_operational_protocol_gate_t806b
file: tests/engine/test_operational_protocol_gate_t806b.py
task_id: T-806b
"""

from __future__ import annotations

from engine.operational_protocol_gate import (
    activate_block_operational_protocol_gate,
    operational_protocol_allows_render,
)
from engine.session import (
    BLOCK_OPERATIONAL_PROTOCOL,
    DesignSession,
    GatePredicateRegistry,
    GateState,
)


def test_block_operational_protocol_gate_blocks_until_authorisation_is_present() -> None:
    registry = activate_block_operational_protocol_gate(
        GatePredicateRegistry.with_pending_defaults()
    )

    verdict = registry.verdict(
        BLOCK_OPERATIONAL_PROTOCOL,
        DesignSession(session_id="session-1", screening_verdict="CLEAR"),
    )

    assert verdict.state is GateState.BLOCKED
    assert "authorisation profile is missing" in verdict.reason


def test_block_operational_protocol_gate_opens_after_authorisation_decision() -> None:
    registry = activate_block_operational_protocol_gate(
        GatePredicateRegistry.with_pending_defaults()
    )

    verdict = registry.verdict(
        BLOCK_OPERATIONAL_PROTOCOL,
        DesignSession(
            session_id="session-1",
            screening_verdict="CLEAR",
            authorisation_profile_id="profile-1",
            decision_record_hash="decision-hash",
        ),
    )

    assert verdict.state is GateState.OPEN
    assert operational_protocol_allows_render(verdict)


def test_block_operational_protocol_gate_rejects_tampered_hit_session() -> None:
    registry = activate_block_operational_protocol_gate(
        GatePredicateRegistry.with_pending_defaults()
    )

    verdict = registry.verdict(
        BLOCK_OPERATIONAL_PROTOCOL,
        DesignSession(
            session_id="session-1",
            screening_verdict="HIT",
            authorisation_profile_id="profile-1",
            decision_record_hash="decision-hash",
        ),
    )

    assert verdict.state is GateState.BLOCKED
    assert "screening_verdict_blocks_operational_protocol:HIT" in verdict.reason
