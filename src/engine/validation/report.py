"""
module_id: engine.validation.report
file: src/engine/validation/report.py
task_id: T-502

Validation report value objects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from domain.canonicalisation import canonical_sha256
from domain.sequence import Sha256
from domain.types.enums import SafetyGate, Severity, SeverityPolicy
from domain.types.ids import RuleId


@dataclass(frozen=True)
class RuleEvaluation:
    rule_id: RuleId
    predicate_name: str
    declared_severity: Severity
    severity_policy: SeverityPolicy
    observed_severity: Severity
    blocks: frozenset[SafetyGate]

    @property
    def triggered(self) -> bool:
        return self.observed_severity is not Severity.INFO

    @property
    def blocked_gates(self) -> frozenset[SafetyGate]:
        if self.observed_severity is Severity.HARD:
            return self.blocks
        return frozenset()

    def to_payload(self) -> dict[str, object]:
        return {
            "blocks": sorted(gate.value for gate in self.blocks),
            "declared_severity": self.declared_severity.value,
            "observed_severity": self.observed_severity.value,
            "predicate_name": self.predicate_name,
            "rule_id": str(self.rule_id),
            "severity_policy": self.severity_policy.value,
            "triggered": self.triggered,
        }


@dataclass(frozen=True)
class RuleEvaluationError(Exception):
    rule_id: RuleId
    predicate_name: str
    cause_type: str
    message: str

    def __str__(self) -> str:
        return f"{self.rule_id}:{self.predicate_name}: {self.cause_type}: {self.message}"

    def to_payload(self) -> dict[str, str]:
        return {
            "cause_type": self.cause_type,
            "message": self.message,
            "predicate_name": self.predicate_name,
            "rule_id": str(self.rule_id),
        }


@dataclass(frozen=True)
class ValidationReport:
    evaluations: tuple[RuleEvaluation, ...]
    errors: tuple[RuleEvaluationError, ...] = ()

    @property
    def findings(self) -> tuple[RuleEvaluation, ...]:
        return tuple(evaluation for evaluation in self.evaluations if evaluation.triggered)

    @property
    def blocked_gates(self) -> frozenset[SafetyGate]:
        return frozenset(
            gate for evaluation in self.evaluations for gate in evaluation.blocked_gates
        )

    @property
    def passed(self) -> bool:
        return not self.errors and not self.blocked_gates

    def to_payload(self) -> dict[str, object]:
        return {
            "blocked_gates": sorted(gate.value for gate in self.blocked_gates),
            "errors": [error.to_payload() for error in self.errors],
            "evaluations": [evaluation.to_payload() for evaluation in self.evaluations],
            "passed": self.passed,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_payload(), sort_keys=True, separators=(",", ":"))

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())
