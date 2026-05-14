"""
module_id: engine.validation.predicates.kozak
file: src/engine/validation/predicates/kozak.py
task_id: T-602

Mammalian Kozak predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates.metric_helpers import metric_float, payload_mapping
from engine.validation.validation_context import ValidationContext


def mr_13_kozak_pwm_threshold(context: ValidationContext, rule: ValidationRule) -> Severity:
    score = metric_float(context, "biology.kozak.score")
    payload = payload_mapping(context, "kozak_metric")
    if score is None and payload is not None:
        value = payload.get("score")
        score = float(value) if isinstance(value, int | float) else None
    if score is None:
        return Severity.INFO
    return Severity.INFO if score >= 0.8 else rule.severity


KOZAK_PREDICATES = {
    "mr_13": mr_13_kozak_pwm_threshold,
}


__all__ = [
    "KOZAK_PREDICATES",
    "mr_13_kozak_pwm_threshold",
]
