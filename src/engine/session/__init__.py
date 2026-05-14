"""
module_id: engine.session
file: src/engine/session/__init__.py
task_id: T-309

Design-session state machine, replay, snapshots, and safety-gate registry.
"""

from __future__ import annotations

from engine.session.events import (
    ReplayIntegrityFailure,
    ensure_cross_stream_invariants,
    replay_canonical_json,
    replay_design_events,
)
from engine.session.gates_pending import (
    BLOCK_COMPILE,
    BLOCK_EXPORT,
    BLOCK_OPERATIONAL_PROTOCOL,
    BLOCK_VENDOR_SUBMISSION,
    SAFETY_GATES,
    GatePredicateNotYetActivated,
    GatePredicateRegistry,
    GateRegistration,
    GateState,
    GateVerdict,
    UnknownGateError,
    blocked_verdict,
    open_verdict,
)
from engine.session.predicate_versioning import (
    PredicateRegistration,
    PredicateVersionHistory,
    PredicateVersionUnavailable,
    predicate_content_hash,
)
from engine.session.snapshots import InMemorySnapshotStore, SessionSnapshot
from engine.session.state_machine import (
    DesignSession,
    SessionState,
    SessionTransitionError,
    empty_session,
)

__all__ = [
    "BLOCK_COMPILE",
    "BLOCK_EXPORT",
    "BLOCK_OPERATIONAL_PROTOCOL",
    "BLOCK_VENDOR_SUBMISSION",
    "SAFETY_GATES",
    "DesignSession",
    "GatePredicateNotYetActivated",
    "GatePredicateRegistry",
    "GateRegistration",
    "GateState",
    "GateVerdict",
    "InMemorySnapshotStore",
    "PredicateRegistration",
    "PredicateVersionHistory",
    "PredicateVersionUnavailable",
    "ReplayIntegrityFailure",
    "SessionSnapshot",
    "SessionState",
    "SessionTransitionError",
    "UnknownGateError",
    "blocked_verdict",
    "empty_session",
    "ensure_cross_stream_invariants",
    "open_verdict",
    "predicate_content_hash",
    "replay_canonical_json",
    "replay_design_events",
]
