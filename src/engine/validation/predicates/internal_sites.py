"""
module_id: engine.validation.predicates.internal_sites
file: src/engine/validation/predicates/internal_sites.py
task_id: T-503, audit-fix-C4

Internal restriction-site predicates.

v0.2.1 audit fix C4 — Scientific Advisor § 2.3 surfaced a HIGH-severity
semantic mismatch: the function was named `mr_22_forbidden_internal_sites`
and was registered under the `mr_22` key, but MR.yaml rule MR-22 declares
the semantics as "If wild-type WPRE detected → recommend WPRE3 (mut6)
variant" (Zanta-Boussif 2009; Schambach 2006). Same predicate name, different
biology. The dict-merge in `engine.validation.predicates.__init__` placed
internal_sites AFTER structural, so the forbidden-restriction-sites check
shadowed the canonical StructuralMetricPredicate('mr_22') from structural.

The fix:
1. Function renamed → `forbidden_internal_sites_predicate` (generic name; no
   longer claims to implement MR-22).
2. `INTERNAL_SITE_PREDICATES` no longer registers anything for the `mr_22`
   key; the slot falls through to `StructuralMetricPredicate('mr_22')` from
   the structural module, which is metric-backed and stub-faithful at v0.2.
3. The forbidden-internal-sites logic is preserved as a reusable helper for
   any future rule that wants it (a future MR-XX or WR-XX can opt in by
   adding its rule_id → forbidden_internal_sites_predicate mapping here).
4. A new CI gate (or extended consistency check) should assert that the
   predicate_name → predicate function pairing does not drift from the
   rule's `description` field at the keyword level; landed at audit fix C4
   as `tests/engine/validation/test_predicate_rule_description_drift_c4.py`.

The MR-22 fixtures at `tests/fixtures/rules/MR/{triggering,passing}/MR-22.json`
continue to validate against the stub semantic (Severity.INFO at v0.2) per
the v0.2 Phase contract.
"""

from __future__ import annotations

from domain.types.enums import Severity
from domain.types.validation_rule import ValidationRule
from engine.sequence_analysis import RestrictionEnzyme, find_sites
from engine.validation.predicates._stub import Predicate
from engine.validation.validation_context import ValidationContext


def forbidden_internal_sites_predicate(
    context: ValidationContext, rule: ValidationRule
) -> Severity:
    """Generic 'no forbidden restriction sites inside the construct' check.

    Reads `context.design_payload['sequence']` (DNA string) and
    `context.design_payload['forbidden_restriction_sites']` (list of
    `{name, recognition_site, cut_index}`) and returns `rule.severity` if any
    forbidden site is found within the sequence; `Severity.INFO` otherwise.

    Not bound to any specific rule_id at v0.2.1 (was incorrectly bound to
    `mr_22` pre-fix; see module docstring). Future rules can opt in by adding
    their rule_id to `INTERNAL_SITE_PREDICATES` below.
    """
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


# v0.2.1 audit fix C4 — empty: no rule_id → forbidden_internal_sites_predicate
# binding at v0.2.1. The mr_22 slot now resolves to StructuralMetricPredicate
# from the structural module. Phase 5/6 rules can opt in by listing their
# rule_ids here once their `description` field is updated to match the
# "forbidden internal restriction sites" semantic.
INTERNAL_SITE_PREDICATES: dict[str, Predicate] = {}


__all__ = [
    "INTERNAL_SITE_PREDICATES",
    "forbidden_internal_sites_predicate",
]
