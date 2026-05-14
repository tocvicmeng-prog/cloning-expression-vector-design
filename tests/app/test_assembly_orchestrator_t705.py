"""
module_id: tests.app.test_assembly_orchestrator_t705
file: tests/app/test_assembly_orchestrator_t705.py
task_id: T-705
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.assembly_orchestrator import (
    AssemblyMethodPicker,
    AssemblyMethodPickerInput,
    AssemblyOrchestrationRequest,
    AssemblyOrchestrator,
)
from domain.types.ids import AssemblyMethodId
from domain.types.validation_rule import FieldPath, ValidationRule
from engine.assembly import AssemblyPart
from engine.codon import (
    DEFAULT_CODON_USAGE_TABLE,
    CodingSequenceDesign,
    ProtectedInterval,
)


def test_orchestrator_converges_through_codon_assembly_and_primer_steps() -> None:
    runner = StableValidationRunner()
    result = AssemblyOrchestrator(validation_runner=runner).orchestrate(
        AssemblyOrchestrationRequest(
            session_id="session-705",
            coding_design=_coding_design(),
            assembly_parts=_parts(),
            coding_part_id="orf",
            assembly_method_id=AssemblyMethodId("moclo"),
            derivation_environment_hash="env-705",
            max_iterations=3,
        )
    )

    assert result.converged
    assert result.iterations == 2
    assert result.codon_result.protein_preserved
    assert result.codon_result.protected_intervals_preserved
    assert result.assembly_plan.method == "moclo"
    assert len(result.primer_set.pairs) == 3
    assert len(runner.payloads) == 4
    assert result.history[-1].priority == (0, 0, 0)


def test_orchestrator_surfaces_structured_convergence_failure() -> None:
    runner = OscillatingValidationRunner()
    result = AssemblyOrchestrator(validation_runner=runner).orchestrate(
        AssemblyOrchestrationRequest(
            session_id="session-oscillating",
            coding_design=_coding_design(),
            assembly_parts=_parts(),
            coding_part_id="orf",
            assembly_method_id=AssemblyMethodId("moclo"),
            derivation_environment_hash="env-705",
            max_iterations=2,
        )
    )

    assert not result.converged
    assert result.convergence_failure is not None
    assert result.convergence_failure.reason == "fixed-point iteration cap reached"
    assert any(
        conflict.startswith("validation:unstable-")
        for conflict in result.convergence_failure.residual_conflicts
    )


def test_method_picker_prefers_high_fragment_or_library_golden_gate() -> None:
    picker = AssemblyMethodPicker()

    assert picker.pick(AssemblyMethodPickerInput(fragment_count=2)) == "restriction-ligation"
    assert (
        picker.pick(AssemblyMethodPickerInput(fragment_count=3, scarless_required=True))
        == "gibson"
    )
    assert picker.pick(AssemblyMethodPickerInput(fragment_count=6)) == "moclo"
    assert picker.pick(AssemblyMethodPickerInput(fragment_count=3, library_size=200)) == "moclo"


def test_missing_coding_part_is_rejected() -> None:
    orchestrator = AssemblyOrchestrator()
    request = AssemblyOrchestrationRequest(
        session_id="session-missing",
        coding_design=_coding_design(),
        assembly_parts=_parts(),
        coding_part_id="missing",
        assembly_method_id=AssemblyMethodId("moclo"),
        derivation_environment_hash="env-705",
    )

    try:
        orchestrator.orchestrate(request)
    except ValueError as error:
        assert "coding_part_id not found" in str(error)
    else:  # pragma: no cover
        raise AssertionError("missing coding part should fail")


def _coding_design() -> CodingSequenceDesign:
    sequence = _coding_sequence()
    return CodingSequenceDesign(
        sequence=sequence,
        algorithm="avoid_only",
        host_codon_usage=DEFAULT_CODON_USAGE_TABLE,
        protected_intervals=(ProtectedInterval(0, 3, "start"),),
        avoid_motifs=(),
        max_iterations=5,
    )


def _parts() -> tuple[AssemblyPart, ...]:
    return (
        AssemblyPart(id="promoter", sequence="ACGTTGCAAGTCGATCGGATCCTAGGCTAACCGTACGATG"),
        AssemblyPart(id="orf", sequence=_coding_sequence()),
        AssemblyPart(id="terminator", sequence="TTGACCGTTAACGGCATTCGATCGTACCGGATTAACCGTA"),
    )


def _coding_sequence() -> str:
    return "ATGGCCGACGAACTGTTCCAGGATGTTAAACCGGGTGACTGGTAA"


@dataclass(frozen=True)
class _Report:
    findings: tuple[object, ...] = ()


@dataclass(frozen=True)
class _ValidationResult:
    report: _Report


class StableValidationRunner:
    def __init__(self) -> None:
        self.payloads: list[Mapping[str, object]] = []

    def validate_design(
        self,
        *,
        session_id: str,
        design_payload: Mapping[str, object],
        rule_registry: Iterable[ValidationRule],
        derivation_environment_hash: str,
        changed_fields: Iterable[FieldPath] | None = None,
    ) -> _ValidationResult:
        del session_id, rule_registry, derivation_environment_hash, changed_fields
        self.payloads.append(dict(design_payload))
        return _ValidationResult(report=_Report())


class OscillatingValidationRunner:
    def __init__(self) -> None:
        self.calls = 0

    def validate_design(
        self,
        *,
        session_id: str,
        design_payload: Mapping[str, object],
        rule_registry: Iterable[ValidationRule],
        derivation_environment_hash: str,
        changed_fields: Iterable[FieldPath] | None = None,
    ) -> _ValidationResult:
        del session_id, design_payload, rule_registry, derivation_environment_hash, changed_fields
        self.calls += 1
        return _ValidationResult(report=_Report(findings=(f"unstable-{self.calls}",)))
