"""
module_id: app.assembly_orchestrator
file: src/app/assembly_orchestrator.py
task_id: T-705

Fixed-point codon, validation, assembly, and primer orchestration.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from domain.types.assembly_plan import AssemblyPlanSummary
from domain.types.ids import AssemblyMethodId
from domain.types.validation_rule import FieldPath, ValidationRule
from engine.assembly import AssemblyEngine, AssemblyPart
from engine.codon import CodingSequenceDesign, CodonOptimisationResult, CodonOptimiser
from engine.primer import PrimerDesigner, PrimerSet

MODULE_ID = "app.assembly_orchestrator"
OWNING_TASKS = ("T-705",)


class ValidationRunner(Protocol):
    def validate_design(
        self,
        *,
        session_id: str,
        design_payload: Mapping[str, object],
        rule_registry: Iterable[ValidationRule],
        derivation_environment_hash: str,
        changed_fields: Iterable[FieldPath] | None = None,
    ) -> object:
        """Subset of ValidationOrchestrator used by the fixed-point loop."""


@dataclass(frozen=True)
class AssemblyMethodPickerInput:
    fragment_count: int
    scarless_required: bool = False
    library_size: int = 1

    def __post_init__(self) -> None:
        if self.fragment_count < 1:
            raise ValueError("fragment_count must be positive")
        if self.library_size < 1:
            raise ValueError("library_size must be positive")


class AssemblyMethodPicker:
    """Small deterministic method picker used until richer catalogue ranking lands."""

    def pick(self, request: AssemblyMethodPickerInput) -> AssemblyMethodId:
        if request.library_size > 100 or request.fragment_count > 5:
            return AssemblyMethodId("moclo")
        if request.scarless_required:
            return AssemblyMethodId("gibson")
        if request.fragment_count == 2:
            return AssemblyMethodId("restriction-ligation")
        return AssemblyMethodId("moclo")


@dataclass(frozen=True)
class AssemblyOrchestrationRequest:
    session_id: str
    coding_design: CodingSequenceDesign
    assembly_parts: tuple[AssemblyPart, ...]
    derivation_environment_hash: str
    assembly_method_id: AssemblyMethodId | None = None
    coding_part_id: str | None = None
    design_payload: Mapping[str, object] | None = None
    rule_registry: tuple[ValidationRule, ...] = ()
    max_iterations: int = 5
    scarless_required: bool = False
    library_size: int = 1

    def __post_init__(self) -> None:
        if not self.session_id:
            raise ValueError("session_id cannot be empty")
        if not self.assembly_parts:
            raise ValueError("assembly_parts cannot be empty")
        if not self.derivation_environment_hash:
            raise ValueError("derivation_environment_hash cannot be empty")
        if not 1 <= self.max_iterations <= 5:
            raise ValueError("max_iterations must be between 1 and 5")
        if self.design_payload is None:
            object.__setattr__(self, "design_payload", {})


@dataclass(frozen=True)
class AssemblyIteration:
    iteration: int
    coding_sequence: str
    assembly_method_id: AssemblyMethodId
    primer_pair_count: int
    validation_findings: tuple[str, ...]
    unresolved_motifs: tuple[str, ...]
    priority: tuple[int, int, int]
    fingerprint: str


@dataclass(frozen=True)
class ConvergenceFailure:
    reason: str
    iterations: int
    residual_conflicts: tuple[str, ...]


@dataclass(frozen=True)
class AssemblyOrchestrationResult:
    converged: bool
    iterations: int
    codon_result: CodonOptimisationResult
    assembly_plan: AssemblyPlanSummary
    primer_set: PrimerSet
    validation_results: tuple[object, ...]
    history: tuple[AssemblyIteration, ...]
    convergence_failure: ConvergenceFailure | None = None


class AssemblyOrchestrator:
    def __init__(
        self,
        *,
        codon_optimiser: CodonOptimiser | None = None,
        validation_runner: ValidationRunner | None = None,
        assembly_engine: AssemblyEngine | None = None,
        primer_designer: PrimerDesigner | None = None,
        method_picker: AssemblyMethodPicker | None = None,
    ) -> None:
        self._codon_optimiser = CodonOptimiser() if codon_optimiser is None else codon_optimiser
        self._validation_runner = validation_runner
        self._assembly_engine = AssemblyEngine() if assembly_engine is None else assembly_engine
        self._primer_designer = PrimerDesigner() if primer_designer is None else primer_designer
        self._method_picker = AssemblyMethodPicker() if method_picker is None else method_picker

    def orchestrate(self, request: AssemblyOrchestrationRequest) -> AssemblyOrchestrationResult:
        current_design = request.coding_design
        previous_fingerprint = ""
        history: list[AssemblyIteration] = []
        validation_results: list[object] = []
        last_codon_result: CodonOptimisationResult | None = None
        last_plan: AssemblyPlanSummary | None = None
        last_primer_set: PrimerSet | None = None

        for iteration in range(1, request.max_iterations + 1):
            codon_result = self._codon_optimiser.optimise(current_design)
            parts = _replace_coding_part(
                request.assembly_parts,
                coding_sequence=codon_result.sequence,
                coding_part_id=request.coding_part_id,
            )
            method_id = request.assembly_method_id or self._method_picker.pick(
                AssemblyMethodPickerInput(
                    fragment_count=len(parts),
                    scarless_required=request.scarless_required,
                    library_size=request.library_size,
                )
            )
            post_codon_validation = self._validate(
                request,
                stage="post_codon",
                coding_sequence=codon_result.sequence,
                assembly_plan=None,
                primer_set=None,
            )
            if post_codon_validation is not None:
                validation_results.append(post_codon_validation)

            assembly_plan = self._assembly_engine.compile_plan(method_id, parts)
            primer_set = self._primer_designer.design_for_parts(
                parts,
                full_plasmid=assembly_plan.expected_product,
            )
            post_primer_validation = self._validate(
                request,
                stage="post_primer",
                coding_sequence=codon_result.sequence,
                assembly_plan=assembly_plan,
                primer_set=primer_set,
            )
            if post_primer_validation is not None:
                validation_results.append(post_primer_validation)

            finding_labels = _finding_labels((post_codon_validation, post_primer_validation))
            priority = (
                len(codon_result.unresolved_motifs),
                len(finding_labels),
                len(primer_set.warnings),
            )
            fingerprint = _fingerprint(
                codon_result.sequence,
                assembly_plan,
                primer_set,
                finding_labels,
            )
            history.append(
                AssemblyIteration(
                    iteration=iteration,
                    coding_sequence=codon_result.sequence,
                    assembly_method_id=method_id,
                    primer_pair_count=len(primer_set.pairs),
                    validation_findings=finding_labels,
                    unresolved_motifs=codon_result.unresolved_motifs,
                    priority=priority,
                    fingerprint=fingerprint,
                )
            )

            last_codon_result = codon_result
            last_plan = assembly_plan
            last_primer_set = primer_set
            if fingerprint == previous_fingerprint:
                return AssemblyOrchestrationResult(
                    converged=True,
                    iterations=iteration,
                    codon_result=codon_result,
                    assembly_plan=assembly_plan,
                    primer_set=primer_set,
                    validation_results=tuple(validation_results),
                    history=tuple(history),
                )
            previous_fingerprint = fingerprint
            current_design = _next_design(current_design, codon_result.sequence)

        if last_codon_result is None or last_plan is None or last_primer_set is None:
            raise RuntimeError("assembly orchestration loop did not run")
        residuals = _residual_conflicts(history[-1])
        return AssemblyOrchestrationResult(
            converged=False,
            iterations=len(history),
            codon_result=last_codon_result,
            assembly_plan=last_plan,
            primer_set=last_primer_set,
            validation_results=tuple(validation_results),
            history=tuple(history),
            convergence_failure=ConvergenceFailure(
                reason="fixed-point iteration cap reached",
                iterations=len(history),
                residual_conflicts=residuals,
            ),
        )

    def _validate(
        self,
        request: AssemblyOrchestrationRequest,
        *,
        stage: str,
        coding_sequence: str,
        assembly_plan: AssemblyPlanSummary | None,
        primer_set: PrimerSet | None,
    ) -> object | None:
        if self._validation_runner is None:
            return None
        base_payload = request.design_payload or {}
        payload = {
            **base_payload,
            "stage": stage,
            "sequence": coding_sequence,
            "assembly_method": str(assembly_plan.method) if assembly_plan is not None else None,
            "primer_pair_count": len(primer_set.pairs) if primer_set is not None else 0,
        }
        return self._validation_runner.validate_design(
            session_id=request.session_id,
            design_payload=payload,
            rule_registry=request.rule_registry,
            derivation_environment_hash=request.derivation_environment_hash,
            changed_fields=("sequence", "assembly_method", "primer_pair_count"),
        )


def _replace_coding_part(
    parts: tuple[AssemblyPart, ...],
    *,
    coding_sequence: str,
    coding_part_id: str | None,
) -> tuple[AssemblyPart, ...]:
    if coding_part_id is None:
        return parts
    replaced: list[AssemblyPart] = []
    matched = False
    for part in parts:
        if part.id != coding_part_id:
            replaced.append(part)
            continue
        matched = True
        replaced.append(
            AssemblyPart(
                id=part.id,
                sequence=coding_sequence,
                topology=part.topology,
                left_overhang=part.left_overhang,
                right_overhang=part.right_overhang,
                left_overlap=part.left_overlap,
                right_overlap=part.right_overlap,
                annotations=part.annotations,
            )
        )
    if not matched:
        raise ValueError(f"coding_part_id not found: {coding_part_id}")
    return tuple(replaced)


def _next_design(
    design: CodingSequenceDesign,
    sequence: str,
) -> CodingSequenceDesign:
    return CodingSequenceDesign(
        sequence=sequence,
        algorithm=design.algorithm,
        host_codon_usage=design.host_codon_usage,
        protected_intervals=design.protected_intervals,
        functional_rna_features=design.functional_rna_features,
        avoid_motifs=design.avoid_motifs,
        target_gc_fraction=design.target_gc_fraction,
        max_iterations=design.max_iterations,
    )


def _fingerprint(
    coding_sequence: str,
    assembly_plan: AssemblyPlanSummary,
    primer_set: PrimerSet,
    finding_labels: tuple[str, ...],
) -> str:
    material = "|".join(
        (
            coding_sequence,
            str(assembly_plan.method),
            assembly_plan.expected_product.checksum,
            ",".join(
                primer.sequence
                for pair in primer_set.pairs
                for primer in (pair.forward, pair.reverse)
            ),
            ",".join(finding_labels),
            ",".join(primer_set.warnings),
        )
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _finding_labels(results: Iterable[object | None]) -> tuple[str, ...]:
    labels: list[str] = []
    for result in results:
        if result is None:
            continue
        report = getattr(result, "report", None)
        findings = getattr(report, "findings", ()) if report is not None else ()
        labels.extend(_label_for_finding(finding) for finding in findings)
    return tuple(labels)


def _label_for_finding(finding: object) -> str:
    rule_id = getattr(finding, "rule_id", None)
    if rule_id is not None:
        return str(rule_id)
    return str(finding)


def _residual_conflicts(iteration: AssemblyIteration) -> tuple[str, ...]:
    conflicts: list[str] = []
    conflicts.extend(f"unresolved_motif:{motif}" for motif in iteration.unresolved_motifs)
    conflicts.extend(f"validation:{finding}" for finding in iteration.validation_findings)
    if iteration.priority[2]:
        conflicts.append("primer_warnings")
    return tuple(conflicts) or ("fixed_point_not_reached",)


__all__ = [
    "AssemblyIteration",
    "AssemblyMethodPicker",
    "AssemblyMethodPickerInput",
    "AssemblyOrchestrationRequest",
    "AssemblyOrchestrationResult",
    "AssemblyOrchestrator",
    "ConvergenceFailure",
    "ValidationRunner",
]
