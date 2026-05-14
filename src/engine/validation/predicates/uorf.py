"""
module_id: engine.validation.predicates.uorf
file: src/engine/validation/predicates/uorf.py
task_id: T-602

Upstream ORF predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates.metric_helpers import metric_bool, payload_str
from engine.validation.validation_context import ValidationContext


def mr_14_upstream_orf_scan(context: ValidationContext, rule: ValidationRule) -> Severity:
    detected = metric_bool(context, "biology.uorf.detected")
    if detected is not None:
        return rule.severity if detected else Severity.INFO
    utr = payload_str(context, "five_prime_utr")
    if not utr:
        return Severity.INFO
    return rule.severity if _has_strong_uorf(utr.upper().replace("U", "T")) else Severity.INFO


def _has_strong_uorf(utr: str) -> bool:
    start = utr.find("ATG")
    while start >= 0:
        minus_3 = utr[start - 3] if start >= 3 else "N"
        plus_4 = utr[start + 3] if start + 3 < len(utr) else "N"
        if minus_3 in {"A", "G"} and plus_4 == "G":
            return True
        start = utr.find("ATG", start + 1)
    return False


UORF_PREDICATES = {
    "mr_14": mr_14_upstream_orf_scan,
}


__all__ = [
    "UORF_PREDICATES",
    "mr_14_upstream_orf_scan",
]
