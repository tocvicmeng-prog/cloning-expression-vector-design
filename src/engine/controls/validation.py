"""
module_id: engine.controls.validation
file: src/engine/controls/validation.py
task_id: T-804

Mechanistic validation checks for generated control sets.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.types.controls import ControlKind, ControlSet
from engine.controls.generator import ControlGenerationInput


class ControlValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ControlValidationFinding:
    rule_id: str
    severity: ControlValidationSeverity
    message: str

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("rule_id cannot be empty")
        if not self.message:
            raise ValueError("message cannot be empty")


@dataclass(frozen=True)
class ControlValidationReport:
    findings: tuple[ControlValidationFinding, ...]

    @property
    def valid(self) -> bool:
        return not any(
            finding.severity is ControlValidationSeverity.ERROR for finding in self.findings
        )

    @property
    def warnings(self) -> tuple[ControlValidationFinding, ...]:
        return tuple(
            finding
            for finding in self.findings
            if finding.severity is ControlValidationSeverity.WARNING
        )

    @property
    def errors(self) -> tuple[ControlValidationFinding, ...]:
        return tuple(
            finding
            for finding in self.findings
            if finding.severity is ControlValidationSeverity.ERROR
        )


def validate_control_set(
    request: ControlGenerationInput,
    control_set: ControlSet,
) -> ControlValidationReport:
    findings: list[ControlValidationFinding] = []
    kinds = {control.kind for control in control_set.controls}
    if control_set.construct_id != request.construct_id:
        findings.append(
            _error(
                "control.construct_id_mismatch",
                "control set construct_id must match the generation request",
            )
        )
    if ControlKind.POSITIVE not in kinds:
        findings.append(_error("control.positive_missing", "positive control is required"))
    if ControlKind.NEGATIVE not in kinds:
        findings.append(_error("control.negative_missing", "negative control is required"))
    if ControlKind.PROCESS not in kinds:
        findings.append(
            _warning(
                "control.process_missing",
                "process control is recommended for assembly workflow interpretation",
            )
        )
    if request.vehicle_control_required and ControlKind.VEHICLE not in kinds:
        findings.append(
            _error(
                "control.vehicle_missing",
                "vehicle/mock control is required for this host/vector delivery context",
            )
        )
    if request.library_size > 1 and ControlKind.LIBRARY_SPECIFIC not in kinds:
        findings.append(
            _error(
                "control.library_specific_missing",
                "library-specific representative controls are required for variant libraries",
            )
        )
    if request.biological_replicates < 2:
        findings.append(
            _warning(
                "control.replicates_low",
                "biological replicate recommendation should be at least n=2",
            )
        )
    _check_positive_suitability(request, control_set, findings)
    _check_negative_absence_of_signal(control_set, findings)
    return ControlValidationReport(findings=tuple(findings))


def _check_positive_suitability(
    request: ControlGenerationInput,
    control_set: ControlSet,
    findings: list[ControlValidationFinding],
) -> None:
    host = request.host_role.strip().lower()
    for control in control_set.controls:
        if control.kind is not ControlKind.POSITIVE:
            continue
        text = f"{control.purpose} {control.expected_observation}".lower()
        if host not in text:
            findings.append(
                _warning(
                    "control.positive_host_match_unclear",
                    "positive-control description should identify the target host role",
                )
            )
        if "above" not in text and "detect" not in text:
            findings.append(
                _warning(
                    "control.positive_signal_unclear",
                    "positive-control expected observation should describe a detectable signal",
                )
            )


def _check_negative_absence_of_signal(
    control_set: ControlSet,
    findings: list[ControlValidationFinding],
) -> None:
    for control in control_set.controls:
        if control.kind is not ControlKind.NEGATIVE:
            continue
        text = control.expected_observation.lower()
        if "no " not in text and "baseline" not in text:
            findings.append(
                _error(
                    "control.negative_absence_unclear",
                    "negative-control expected observation must establish absence of signal",
                )
            )


def _error(rule_id: str, message: str) -> ControlValidationFinding:
    return ControlValidationFinding(
        rule_id=rule_id,
        severity=ControlValidationSeverity.ERROR,
        message=message,
    )


def _warning(rule_id: str, message: str) -> ControlValidationFinding:
    return ControlValidationFinding(
        rule_id=rule_id,
        severity=ControlValidationSeverity.WARNING,
        message=message,
    )
