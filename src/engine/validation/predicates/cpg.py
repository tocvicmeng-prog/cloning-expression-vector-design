"""
module_id: engine.validation.predicates.cpg
file: src/engine/validation/predicates/cpg.py
task_id: T-602

CpG-content predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates.metric_helpers import metric_float, payload_str
from engine.validation.validation_context import ValidationContext


def mr_27_cpg_content_threshold(context: ValidationContext, rule: ValidationRule) -> Severity:
    observed_expected = metric_float(context, "biology.cpg.observed_expected")
    count_per_100bp = metric_float(context, "biology.cpg.count_per_100bp")
    sequence = payload_str(context, "sequence")
    if count_per_100bp is None and sequence:
        dna = sequence.upper().replace("U", "T")
        count_per_100bp = (dna.count("CG") / max(1, len(dna))) * 100
    if observed_expected is None and count_per_100bp is None:
        return Severity.INFO
    too_high_oe = observed_expected is not None and observed_expected > 1.2
    too_dense = count_per_100bp is not None and count_per_100bp > 8.0
    return rule.severity if too_high_oe or too_dense else Severity.INFO


CPG_PREDICATES = {
    "mr_27": mr_27_cpg_content_threshold,
}


__all__ = [
    "CPG_PREDICATES",
    "mr_27_cpg_content_threshold",
]
