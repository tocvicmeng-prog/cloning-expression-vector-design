"""
module_id: tests.engine.session.test_gates_pending
file: tests/engine/session/test_gates_pending.py
task_id: T-309
"""

from __future__ import annotations

import pytest

from domain.sequence import sha256_text
from domain.types.derivation import GateName, PredicateVersion
from engine.session import (
    BLOCK_COMPILE,
    SAFETY_GATES,
    DesignSession,
    GatePredicateNotYetActivated,
    GatePredicateRegistry,
    GateState,
    GateVerdict,
    PredicateRegistration,
    PredicateVersionHistory,
    PredicateVersionUnavailable,
    blocked_verdict,
    empty_session,
    open_verdict,
    predicate_content_hash,
)


def test_pending_registry_declares_all_safety_gates_without_activation() -> None:
    registry = GatePredicateRegistry.with_pending_defaults()
    session = empty_session("session-1")

    assert tuple(registry.registrations) == SAFETY_GATES
    for gate in SAFETY_GATES:
        verdict = registry.verdict(gate, session, allow_pending=True)
        assert verdict.state is GateState.PENDING_NOT_YET_ACTIVATED

        with pytest.raises(GatePredicateNotYetActivated):
            registry.verdict(gate, session)


def test_activate_replaces_pending_gate_with_versioned_predicate() -> None:
    version = PredicateVersion("1.0.0")
    content_hash = sha256_text("block-compile-v1")

    def predicate(_session: DesignSession) -> GateVerdict:
        return open_verdict(BLOCK_COMPILE, version, content_hash)

    registry = GatePredicateRegistry.with_pending_defaults().activate(
        BLOCK_COMPILE,
        predicate,
        version=version,
        content_hash=content_hash,
    )

    verdict = registry.verdict(BLOCK_COMPILE, empty_session("session-1"))

    assert verdict.state is GateState.OPEN
    assert registry.environment_versions()[BLOCK_COMPILE] == version
    assert registry.environment_content_hashes()[BLOCK_COMPILE] == content_hash


def test_blocked_verdict_carries_reason_and_predicate_identity() -> None:
    version = PredicateVersion("2.0.0")
    content_hash = sha256_text("block-export-v2")
    verdict = blocked_verdict(
        GateName("BlockExport"),
        version,
        content_hash,
        reason="missing screening clearance",
    )

    assert verdict.state is GateState.BLOCKED
    assert verdict.reason == "missing screening clearance"


def test_predicate_version_history_selects_captured_version_not_current() -> None:
    old = PredicateRegistration(
        gate=BLOCK_COMPILE,
        predicate_version=PredicateVersion("1.0.0"),
        predicate_content_hash=predicate_content_hash("old source"),
        canonical_source="old source",
    )
    current = PredicateRegistration(
        gate=BLOCK_COMPILE,
        predicate_version=PredicateVersion("1.1.0"),
        predicate_content_hash=predicate_content_hash("new source"),
        canonical_source="new source",
    )
    history = PredicateVersionHistory((old, current))

    assert (
        history.registration_for(BLOCK_COMPILE, old.predicate_version, old.predicate_content_hash)
        == old
    )
    with pytest.raises(PredicateVersionUnavailable):
        history.registration_for(
            BLOCK_COMPILE, PredicateVersion("9.9.9"), old.predicate_content_hash
        )
