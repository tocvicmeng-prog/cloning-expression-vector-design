"""
module_id: engine.vendor_feasibility_gate
file: src/engine/vendor_feasibility_gate.py
task_id: T-1001

Vendor-profile portion of BlockVendorSubmission.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from domain.sequence import Sha256, sha256_text
from domain.types.derivation import PredicateVersion
from engine.session import (
    BLOCK_VENDOR_SUBMISSION,
    DesignSession,
    GatePredicateRegistry,
    GateState,
    GateVerdict,
    blocked_verdict,
    open_verdict,
)

VENDOR_FEASIBILITY_GATE_VERSION = PredicateVersion("1.0.0-t1001-vendor-feasibility")
VENDOR_FEASIBILITY_GATE_HASH = sha256_text("T-1001:vendor-profile-feasibility")


class VendorFeasibilityReportLike(Protocol):
    @property
    def vendor_id(self) -> str: ...

    @property
    def service_id(self) -> str: ...

    @property
    def rejected(self) -> bool: ...

    @property
    def rejection_classes(self) -> frozenset[object]: ...

    @property
    def session_id(self) -> str | None: ...

    @property
    def construct_id(self) -> str | None: ...

    @property
    def construct_checksum(self) -> str | None: ...


def activate_block_vendor_submission_for_vendor_failures(
    registry: GatePredicateRegistry,
    reports: Iterable[VendorFeasibilityReportLike],
    *,
    version: PredicateVersion = VENDOR_FEASIBILITY_GATE_VERSION,
    content_hash: Sha256 = VENDOR_FEASIBILITY_GATE_HASH,
) -> GatePredicateRegistry:
    report_tuple = tuple(reports)

    def predicate(session: DesignSession) -> GateVerdict:
        matching_reports = tuple(
            report for report in report_tuple if _report_applies_to_session(report, session)
        )
        rejected = tuple(report for report in matching_reports if report.rejected)
        if rejected:
            first = rejected[0]
            classes = ",".join(
                sorted(_rejection_class_value(item) for item in first.rejection_classes)
            )
            return blocked_verdict(
                BLOCK_VENDOR_SUBMISSION,
                version,
                content_hash,
                reason=(
                    f"vendor_feasibility_rejected:{first.vendor_id}:{first.service_id}:{classes}"
                ),
            )
        return open_verdict(
            BLOCK_VENDOR_SUBMISSION,
            version,
            content_hash,
            reason="vendor-profile feasibility permits vendor submission",
        )

    return registry.activate(
        BLOCK_VENDOR_SUBMISSION,
        predicate,
        version=version,
        content_hash=content_hash,
    )


def vendor_feasibility_allows_submission(verdict: GateVerdict) -> bool:
    if verdict.gate != BLOCK_VENDOR_SUBMISSION:
        raise ValueError("verdict is not for BlockVendorSubmission")
    return verdict.state is GateState.OPEN


def _report_applies_to_session(
    report: VendorFeasibilityReportLike,
    session: DesignSession,
) -> bool:
    if report.session_id is not None:
        return report.session_id == session.session_id
    if report.construct_id is not None:
        return report.construct_id == session.construct_id
    if report.construct_checksum is not None:
        return report.construct_checksum == session.construct_checksum
    return True


def _rejection_class_value(value: object) -> str:
    enum_value = getattr(value, "value", None)
    return str(enum_value if enum_value is not None else value)
