"""
module_id: tests.engine.test_screening_gate_t1002
file: tests/engine/test_screening_gate_t1002.py
task_id: T-1002
"""

from __future__ import annotations

from decimal import Decimal

from adapter.vendor import VendorFeasibilityIssue, VendorFeasibilityReport, VendorRejectionClass
from domain.sequence import Sha256
from engine.screening_gate import (
    activate_screening_verdict_gates,
    screening_verdict_allows_export,
    screening_verdict_allows_vendor_submission,
)
from engine.session import (
    BLOCK_EXPORT,
    BLOCK_VENDOR_SUBMISSION,
    DesignSession,
    GatePredicateRegistry,
    GateState,
)
from engine.vendor_feasibility_gate import activate_block_vendor_submission_for_vendor_failures


def test_screening_clear_opens_vendor_and_export_gates() -> None:
    registry = activate_screening_verdict_gates(GatePredicateRegistry.with_pending_defaults())
    session = DesignSession(session_id="session-1", screening_verdict="CLEAR")

    vendor = registry.verdict(BLOCK_VENDOR_SUBMISSION, session)
    export = registry.verdict(BLOCK_EXPORT, session)

    assert vendor.state is GateState.OPEN
    assert export.state is GateState.OPEN
    assert screening_verdict_allows_vendor_submission(vendor)
    assert screening_verdict_allows_export(export)


def test_screening_hit_watchlist_or_missing_verdict_blocks_gates() -> None:
    registry = activate_screening_verdict_gates(GatePredicateRegistry.with_pending_defaults())

    for verdict in (None, "HIT", "WATCHLIST", "MANUAL_REVIEW_REQUIRED", "UNAVAILABLE"):
        session = DesignSession(session_id=f"session-{verdict}", screening_verdict=verdict)
        assert registry.verdict(BLOCK_VENDOR_SUBMISSION, session).state is GateState.BLOCKED
        assert registry.verdict(BLOCK_EXPORT, session).state is GateState.BLOCKED


def test_screening_gate_composes_with_existing_vendor_feasibility_block() -> None:
    registry = activate_block_vendor_submission_for_vendor_failures(
        GatePredicateRegistry.with_pending_defaults(),
        (_rejected_vendor_report(),),
    )
    registry = activate_screening_verdict_gates(registry)
    session = DesignSession(session_id="session-1", screening_verdict="CLEAR")

    verdict = registry.verdict(BLOCK_VENDOR_SUBMISSION, session)

    assert verdict.state is GateState.BLOCKED
    assert "vendor_submission_blocked_by_existing_predicate" in verdict.reason


def _rejected_vendor_report() -> VendorFeasibilityReport:
    return VendorFeasibilityReport(
        vendor_id="twist",
        request_id="vendor-req-1",
        service_id="twist.gene_fragment",
        status="rejected",
        sequence_length_bp=6000,
        global_gc_pct=Decimal("50.00"),
        issues=(
            VendorFeasibilityIssue(
                rejection_class=VendorRejectionClass.LENGTH_OVERFLOW,
                severity="rejection",
                message="too long",
                service_id="twist.gene_fragment",
            ),
        ),
        profile_version="test",
        profile_content_hash=Sha256("0" * 64),
    )
