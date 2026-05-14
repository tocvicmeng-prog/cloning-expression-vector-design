"""
module_id: engine.validation.predicates.rbs
file: src/engine/validation/predicates/rbs.py
task_id: T-602

Bacterial RBS / translation-initiation predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates.metric_helpers import metric, metric_float, payload_mapping
from engine.validation.validation_context import ValidationContext


def mr_12_rbs_window_and_accessibility(
    context: ValidationContext, rule: ValidationRule
) -> Severity:
    metric_payload = payload_mapping(context, "rbs_metric")
    motif = metric(context, "biology.rbs.shine_dalgarno_motif")
    spacing = metric_float(context, "biology.rbs.spacing_nt")
    tir = metric_float(context, "biology.rbs.translation_initiation_rate")
    mfe = metric_float(context, "biology.rna.mfe_kcal_mol", "biology.rbs.leader_mfe_kcal_mol")
    if metric_payload is not None:
        motif = motif or metric_payload.get("shine_dalgarno_motif")
        spacing = spacing if spacing is not None else _float_from(metric_payload.get("spacing_nt"))
        tir = (
            tir
            if tir is not None
            else _float_from(metric_payload.get("translation_initiation_rate"))
        )
        mfe = mfe if mfe is not None else _float_from(metric_payload.get("mfe_kcal_mol"))
    if motif is None and spacing is None and tir is None and mfe is None:
        return Severity.INFO
    motif_ok = isinstance(motif, str) and bool(motif)
    spacing_ok = spacing is not None and 5 <= spacing <= 13
    tir_ok = tir is None or tir >= 1000.0
    accessibility_ok = mfe is None or mfe > -10.0
    return (
        Severity.INFO if motif_ok and spacing_ok and tir_ok and accessibility_ok else rule.severity
    )


def _float_from(value: object) -> float | None:
    return float(value) if isinstance(value, int | float) else None


RBS_PREDICATES = {
    "mr_12": mr_12_rbs_window_and_accessibility,
}


__all__ = [
    "RBS_PREDICATES",
    "mr_12_rbs_window_and_accessibility",
]
