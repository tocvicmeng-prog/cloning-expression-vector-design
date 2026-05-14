"""
module_id: engine.validation.predicates.structural
file: src/engine/validation/predicates/structural.py
task_id: T-503

Metric-backed structural predicate helpers for Phase-5 activation.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.enums import Severity
from domain.types.ids import MetricId
from domain.types.validation_rule import ValidationRule
from engine.validation.validation_context import ValidationContext

STRUCTURAL_RULE_NAMES = (
    "mr_01",
    "mr_02",
    "mr_03",
    "mr_04",
    "mr_05",
    "mr_06",
    "mr_17",
    "mr_18",
    "mr_19",
    "mr_22",
    "mr_23",
    "mr_29",
    "mr_30",
    "mr_31",
    "mr_32",
    "mr_33",
    "mr_34",
    "mr_35",
    "mr_37",
    "mr_38",
    "mr_39",
    "mr_40",
    "mr_41",
    "mr_42",
    "mr_43",
    "mr_44",
    "mr_50",
    "mr_51",
    "mr_52",
    "mr_53",
    "wr_01",
    "wr_02",
    "wr_03",
    "wr_04",
    "wr_05",
    "wr_06",
    "wr_07",
    "wr_11",
    "wr_12",
    "wr_13",
    "wr_14",
    "wr_15",
    "wr_16",
    "wr_17",
    "wr_18",
    "wr_19",
    "wr_20",
    "wr_21",
    "br_01",
    "br_02",
    "br_03",
    "br_04",
    "br_05",
    "br_06",
    "br_07",
    "br_08",
    "br_09",
    "br_10",
    "br_11",
    "br_12",
    "br_13",
)


@dataclass(frozen=True)
class StructuralMetricPredicate:
    name: str

    def __call__(self, context: ValidationContext, rule: ValidationRule) -> Severity:
        return rule.severity if _violation_declared(context, self.name) else Severity.INFO

    @property
    def __name__(self) -> str:
        return self.name


def _violation_declared(context: ValidationContext, predicate_name: str) -> bool:
    metric_key = MetricId(f"predicate.{predicate_name}.violated")
    if bool(context.metrics.get(metric_key, False)):
        return True
    violations = context.design_payload.get("predicate_violations", {})
    return isinstance(violations, dict) and bool(violations.get(predicate_name, False))


IMPLEMENTED_STRUCTURAL_PREDICATES = {
    name: StructuralMetricPredicate(name) for name in STRUCTURAL_RULE_NAMES
}


__all__ = [
    "IMPLEMENTED_STRUCTURAL_PREDICATES",
    "STRUCTURAL_RULE_NAMES",
    "StructuralMetricPredicate",
]
