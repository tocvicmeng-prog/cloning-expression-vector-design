"""
module_id: engine.validation.predicates.host
file: src/engine/validation/predicates/host.py
task_id: T-503

Host-compatibility report predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.ids import MetricId
from domain.types.validation_rule import ValidationRule
from engine.validation.validation_context import ValidationContext


def host_compatibility_report_clear(context: ValidationContext, rule: ValidationRule) -> Severity:
    metric = context.metrics.get(MetricId("compatibility.report.passed"))
    if metric is None:
        return Severity.INFO
    return Severity.INFO if bool(metric) else rule.severity


HOST_PREDICATES = {
    "mr_01": host_compatibility_report_clear,
    "mr_02": host_compatibility_report_clear,
    "mr_04": host_compatibility_report_clear,
}


__all__ = [
    "HOST_PREDICATES",
    "host_compatibility_report_clear",
]
