"""
module_id: engine.validation.predicates.metric_helpers
file: src/engine/validation/predicates/metric_helpers.py
task_id: T-602

Typed helpers for metric-backed predicates.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from domain.types.ids import MetricId
from engine.validation.validation_context import ValidationContext


def metric(context: ValidationContext, key: str) -> object | None:
    return context.metrics.get(MetricId(key))


def payload_mapping(context: ValidationContext, key: str) -> Mapping[str, object] | None:
    raw = context.design_payload.get(key)
    return raw if isinstance(raw, Mapping) else None


def metric_float(context: ValidationContext, *keys: str) -> float | None:
    for key in keys:
        value = metric(context, key)
        if isinstance(value, int | float):
            return float(value)
    return None


def metric_bool(context: ValidationContext, *keys: str) -> bool | None:
    for key in keys:
        value = metric(context, key)
        if isinstance(value, bool):
            return value
    return None


def metric_sequence(context: ValidationContext, key: str) -> Sequence[object]:
    value = metric(context, key)
    if isinstance(value, Sequence) and not isinstance(value, str):
        return value
    return ()


def payload_str(context: ValidationContext, key: str) -> str | None:
    value = context.design_payload.get(key)
    return value if isinstance(value, str) else None
