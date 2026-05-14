"""
module_id: engine.validation.predicates.splice
file: src/engine/validation/predicates/splice.py
task_id: T-602

Splice-site score predicates.
"""

from __future__ import annotations

from collections.abc import Mapping

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates.metric_helpers import metric_float, metric_sequence
from engine.validation.validation_context import ValidationContext


def mr_16_splice_score_threshold(context: ValidationContext, rule: ValidationRule) -> Severity:
    max_score = metric_float(context, "biology.splice.max_score")
    if max_score is None:
        scores: list[float] = []
        for item in metric_sequence(context, "biology.splice.predictions"):
            if isinstance(item, Mapping):
                score = item.get("score")
                if isinstance(score, int | float):
                    scores.append(float(score))
        max_score = max(scores) if scores else None
    if max_score is None:
        return Severity.INFO
    return rule.severity if max_score >= 0.5 else Severity.INFO


SPLICE_PREDICATES = {
    "mr_16": mr_16_splice_score_threshold,
}


__all__ = [
    "SPLICE_PREDICATES",
    "mr_16_splice_score_threshold",
]
