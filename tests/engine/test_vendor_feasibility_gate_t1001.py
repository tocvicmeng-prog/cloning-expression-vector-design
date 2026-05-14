"""
module_id: tests.engine.test_vendor_feasibility_gate_t1001
file: tests/engine/test_vendor_feasibility_gate_t1001.py
task_id: T-1001
"""

from __future__ import annotations

from adapter.vendor import IdtVendorAdapter, VendorFeasibilityRequest, VendorRejectionClass
from engine.session import BLOCK_VENDOR_SUBMISSION, DesignSession, GatePredicateRegistry, GateState
from engine.vendor_feasibility_gate import (
    activate_block_vendor_submission_for_vendor_failures,
    vendor_feasibility_allows_submission,
)
from tests.adapter.vendor.test_vendor_adapters_t1001 import CATALOGUES, SCHEMAS, _balanced_sequence


def test_vendor_feasibility_gate_blocks_rejected_report_even_when_screening_clear() -> None:
    adapter = IdtVendorAdapter.from_catalogues(CATALOGUES, SCHEMAS)
    report = adapter.check(
        VendorFeasibilityRequest(
            request_id="blocked",
            sequence=_balanced_sequence(3001),
            product_type="gblocks",
            service_id="idt.gblocks",
            session_id="session-1",
            construct_id="construct-1",
        )
    )
    registry = activate_block_vendor_submission_for_vendor_failures(
        GatePredicateRegistry.with_pending_defaults(),
        (report,),
    )
    session = DesignSession(
        session_id="session-1",
        construct_id="construct-1",
        screening_verdict="CLEAR",
    )

    verdict = registry.verdict(BLOCK_VENDOR_SUBMISSION, session)

    assert verdict.state is GateState.BLOCKED
    assert VendorRejectionClass.LENGTH_OVERFLOW.value in verdict.reason
    assert not vendor_feasibility_allows_submission(verdict)


def test_vendor_feasibility_gate_opens_when_registered_reports_accept() -> None:
    adapter = IdtVendorAdapter.from_catalogues(CATALOGUES, SCHEMAS)
    report = adapter.check(
        VendorFeasibilityRequest(
            request_id="accepted",
            sequence=_balanced_sequence(400),
            product_type="gblocks",
            service_id="idt.gblocks",
            session_id="session-2",
            construct_id="construct-2",
        )
    )
    registry = activate_block_vendor_submission_for_vendor_failures(
        GatePredicateRegistry.with_pending_defaults(),
        (report,),
    )

    verdict = registry.verdict(
        BLOCK_VENDOR_SUBMISSION,
        DesignSession(session_id="session-2", construct_id="construct-2"),
    )

    assert verdict.state is GateState.OPEN
    assert vendor_feasibility_allows_submission(verdict)
