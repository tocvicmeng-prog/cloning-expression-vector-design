"""
module_id: engine.validation.predicates.internal_sites
file: src/engine/validation/predicates/internal_sites.py
task_id: T-503

Internal restriction-site predicates.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.sequence_analysis import RestrictionEnzyme, find_sites
from engine.validation.validation_context import ValidationContext


def mr_22_forbidden_internal_sites(context: ValidationContext, rule: ValidationRule) -> Severity:
    sequence = context.design_payload.get("sequence")
    forbidden_sites = context.design_payload.get("forbidden_restriction_sites", ())
    if not isinstance(sequence, str) or not isinstance(forbidden_sites, list | tuple):
        return Severity.INFO
    for raw_site in forbidden_sites:
        if not isinstance(raw_site, dict):
            continue
        name = str(raw_site.get("name", "forbidden"))
        recognition_site = raw_site.get("recognition_site")
        if not isinstance(recognition_site, str):
            continue
        enzyme = RestrictionEnzyme(
            name=name,
            recognition_site=recognition_site,
            cut_index=int(raw_site.get("cut_index", 0)),
        )
        if find_sites(sequence, enzyme, topology="linear"):
            return rule.severity
    return Severity.INFO


INTERNAL_SITE_PREDICATES = {
    "mr_22": mr_22_forbidden_internal_sites,
}


__all__ = [
    "INTERNAL_SITE_PREDICATES",
    "mr_22_forbidden_internal_sites",
]
