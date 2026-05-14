"""
module_id: engine.validation.predicates.signal_peptide
file: src/engine/validation/predicates/signal_peptide.py
task_id: T-602

Signal-peptide and declared-compartment consistency predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates.metric_helpers import metric_bool, payload_str
from engine.validation.validation_context import ValidationContext

SECRETORY_COMPARTMENTS = frozenset({"secreted", "extracellular", "periplasm", "membrane", "er"})
CYTOSOLIC_COMPARTMENTS = frozenset({"cytosol", "cytoplasm", "nucleus", "mitochondria"})


def mr_28_signal_peptide_compartment_consistency(
    context: ValidationContext,
    rule: ValidationRule,
) -> Severity:
    compartment = (payload_str(context, "declared_compartment") or "").lower()
    protein = (payload_str(context, "protein_sequence") or "").upper()
    has_signal = metric_bool(context, "biology.signal_peptide.has_signal_peptide")
    if has_signal is None:
        return Severity.INFO
    er_retention = protein.endswith(("KDEL", "HDEL"))
    secretory_required = compartment in SECRETORY_COMPARTMENTS
    cytosolic_required = compartment in CYTOSOLIC_COMPARTMENTS
    if secretory_required and not has_signal:
        return rule.severity
    if cytosolic_required and has_signal:
        return rule.severity
    if er_retention and compartment not in {"er", "secreted"}:
        return rule.severity
    return Severity.INFO


SIGNAL_PEPTIDE_PREDICATES = {
    "mr_28": mr_28_signal_peptide_compartment_consistency,
}


__all__ = [
    "SIGNAL_PEPTIDE_PREDICATES",
    "mr_28_signal_peptide_compartment_consistency",
]
