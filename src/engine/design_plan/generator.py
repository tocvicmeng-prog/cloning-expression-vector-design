"""
module_id: engine.design_plan.generator
file: src/engine/design_plan/generator.py
task_id: T-802

Pure generator for non-operational design realisation plans.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.canonicalisation import canonical_sha256
from domain.types.assembly_plan import AssemblyPlanSummary
from domain.types.design_plan import DesignRealisationPlan, ReviewerPacket, VerificationArtefact
from domain.types.risk_advisory import RiskAdvisoryReport


@dataclass(frozen=True)
class DesignPlanInput:
    design_session_id: str
    construct_id: str
    construct_version: str
    assembly_plan: AssemblyPlanSummary
    primer_set: tuple[str, ...]
    biosafety_classification: str = "not-classified"
    extra_qc_checkpoints: tuple[str, ...] = ()
    expected_verification_artefacts: tuple[VerificationArtefact, ...] = ()
    institutional_approvals_required: tuple[str, ...] = ()
    reviewer_notes: tuple[str, ...] = ()
    validation_report_hashes: tuple[str, ...] = ()
    risk_advisory_report: RiskAdvisoryReport | None = None

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise ValueError("design_session_id cannot be empty")
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not self.construct_version:
            raise ValueError("construct_version cannot be empty")
        if not self.primer_set:
            raise ValueError("DesignPlanInput requires a primer_set")
        if not self.biosafety_classification:
            raise ValueError("biosafety_classification cannot be empty")
        _require_non_empty_items(self.extra_qc_checkpoints, "extra_qc_checkpoints")
        _require_non_empty_items(
            self.institutional_approvals_required,
            "institutional_approvals_required",
        )
        _require_non_empty_items(self.reviewer_notes, "reviewer_notes")
        _require_non_empty_items(self.validation_report_hashes, "validation_report_hashes")


class DesignPlanGenerator:
    """Build always-renderable design plans from validated upstream summaries."""

    def generate(self, request: DesignPlanInput) -> DesignRealisationPlan:
        return DesignRealisationPlan(
            construct_id=request.construct_id,
            assembly_plan=request.assembly_plan,
            primer_set=request.primer_set,
            qc_checkpoints=_qc_checkpoints(request),
            expected_verification_artefacts=_verification_artefacts(request),
            institutional_approvals_required=_institutional_approvals(request),
            reviewer_packet=ReviewerPacket(
                summary=_reviewer_summary(request),
                evidence_hashes=_evidence_hashes(request),
            ),
        )


def generate_design_plan(request: DesignPlanInput) -> DesignRealisationPlan:
    return DesignPlanGenerator().generate(request)


def _qc_checkpoints(request: DesignPlanInput) -> tuple[str, ...]:
    route = str(request.assembly_plan.method)
    base = request.assembly_plan.verification_checkpoints or (
        f"Confirm fragment order for {route}: {_fragment_route(request.assembly_plan)}",
        f"Verify expected product checksum {request.assembly_plan.expected_product.checksum}",
        f"Review every {route} junction against the assembled-product map",
    )
    return _deduplicate((*base, *request.extra_qc_checkpoints))


def _verification_artefacts(request: DesignPlanInput) -> tuple[VerificationArtefact, ...]:
    product = request.assembly_plan.expected_product
    base = (
        VerificationArtefact(
            name="Fragment input manifest",
            description=f"Ordered fragments: {_fragment_route(request.assembly_plan)}",
        ),
        VerificationArtefact(
            name="Assembly route summary",
            description=(
                f"{request.assembly_plan.method} route for construct {request.construct_id} "
                f"version {request.construct_version}"
            ),
        ),
        VerificationArtefact(
            name="Expected product checksum",
            description=f"{product.id} canonical checksum {product.checksum}",
        ),
        VerificationArtefact(
            name="Junction verification record",
            description="Evidence that all planned fragment junctions match the design map",
        ),
    )
    risk = (
        (
            VerificationArtefact(
                name="Risk advisory report",
                description=(
                    "Advisory report "
                    f"{request.risk_advisory_report.report_content_hash} "
                    f"from catalogue {request.risk_advisory_report.advisory_catalogue_version}"
                ),
            ),
        )
        if request.risk_advisory_report is not None
        else ()
    )
    validation = tuple(
        VerificationArtefact(
            name=f"Validation report {index + 1}",
            description=f"Validation report content hash {content_hash}",
        )
        for index, content_hash in enumerate(request.validation_report_hashes)
    )
    return _deduplicate_artefacts(
        (*base, *risk, *validation, *request.expected_verification_artefacts)
    )


def _institutional_approvals(request: DesignPlanInput) -> tuple[str, ...]:
    approvals: list[str] = list(request.institutional_approvals_required)
    if _requires_biosafety_review(request.biosafety_classification):
        approvals.append(
            "Institutional biosafety review required before operational protocol "
            f"authorisation for {request.biosafety_classification}"
        )
    if request.risk_advisory_report is not None:
        required = sorted(request.risk_advisory_report.required_acknowledgements())
        if required:
            approvals.append(
                "Signed risk-advisory acknowledgement required for: " + ", ".join(required)
            )
    return _deduplicate(tuple(approvals))


def _reviewer_summary(request: DesignPlanInput) -> str:
    fragments = request.assembly_plan.fragments
    advisory_count = 0
    acknowledgement_count = 0
    if request.risk_advisory_report is not None:
        advisory_count = len(request.risk_advisory_report.advisories)
        acknowledgement_count = len(request.risk_advisory_report.required_acknowledgements())
    notes = f" Notes: {'; '.join(request.reviewer_notes)}." if request.reviewer_notes else ""
    return (
        f"Design session {request.design_session_id}; construct {request.construct_id} "
        f"v{request.construct_version}. Assembly route {request.assembly_plan.method} combines "
        f"{len(fragments)} fragment(s): {_fragment_route(request.assembly_plan)}. "
        f"Biosafety classification: {request.biosafety_classification}. "
        f"Risk advisories: {advisory_count}; required acknowledgements: "
        f"{acknowledgement_count}.{notes}"
    )


def _evidence_hashes(request: DesignPlanInput) -> tuple[str, ...]:
    hashes = [
        str(canonical_sha256(request.assembly_plan)),
        str(request.assembly_plan.expected_product.checksum),
    ]
    hashes.extend(request.validation_report_hashes)
    if request.risk_advisory_report is not None:
        hashes.append(str(request.risk_advisory_report.report_content_hash))
    return _deduplicate(tuple(hashes))


def _fragment_route(assembly_plan: AssemblyPlanSummary) -> str:
    return " -> ".join(assembly_plan.fragments)


def _requires_biosafety_review(classification: str) -> bool:
    normalised = classification.strip().lower().replace("_", "-")
    return normalised not in {"bsl-1", "not-classified", "not classified", "none"}


def _deduplicate(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)


def _deduplicate_artefacts(
    artefacts: tuple[VerificationArtefact, ...],
) -> tuple[VerificationArtefact, ...]:
    seen: set[str] = set()
    result: list[VerificationArtefact] = []
    for artefact in artefacts:
        if artefact.name in seen:
            continue
        seen.add(artefact.name)
        result.append(artefact)
    return tuple(result)


def _require_non_empty_items(values: tuple[str, ...], field_name: str) -> None:
    if any(not value for value in values):
        raise ValueError(f"{field_name} cannot contain empty values")
