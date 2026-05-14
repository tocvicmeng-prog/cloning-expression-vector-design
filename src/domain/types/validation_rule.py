"""
module_id: domain.types.validation_rule
file: src/domain/types/validation_rule.py
task_id: T-303

Expanded validation-rule manifest entity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, SafetyGate, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId, require_non_empty

FieldPath = str
Precondition = str
AdapterRef = str
ThresholdProfileRef = str
FixtureRef = str


@dataclass(frozen=True)
class ValidationRule:
    rule_id: RuleId
    predicate_name: str
    severity: Severity
    severity_policy: SeverityPolicy
    blocks: frozenset[SafetyGate]
    reads: frozenset[FieldPath]
    depends_on_metrics: frozenset[MetricId]
    produces_metrics: frozenset[MetricId]
    invalidates: frozenset[MetricId | RuleId]
    preconditions: tuple[Precondition, ...]
    target_context: ContextScope
    external_adapters: tuple[AdapterRef, ...]
    threshold_profile: ThresholdProfileRef
    citation: GradedCitation
    last_reviewed: date
    reviewed_by: ReviewerId
    test_fixtures: tuple[FixtureRef, ...]
    suggested_remediation: str

    def __post_init__(self) -> None:
        require_non_empty(str(self.rule_id), "rule_id")
        require_non_empty(self.predicate_name, "predicate_name")
        require_non_empty(self.threshold_profile, "threshold_profile")
        require_non_empty(str(self.reviewed_by), "reviewed_by")
        require_non_empty(self.suggested_remediation, "suggested_remediation")
        if self.severity is Severity.HARD and not self.blocks:
            raise ValueError("HARD validation rules must block at least one safety gate")
        if self.severity is Severity.INFO and self.blocks:
            raise ValueError("INFO validation rules cannot block safety gates")
        if not self.reads:
            raise ValueError("validation rules must declare read field paths")
        if not self.test_fixtures:
            raise ValueError("validation rules must declare test fixtures")
