"""
module_id: tests.engine.validation.test_predicate_rule_description_drift_c4
file: tests/engine/validation/test_predicate_rule_description_drift_c4.py
task_id: audit-fix-C4

Regression guard against predicate-name ↔ rule-description semantic drift.

The collaborative audit (2026-05-23 Scientific § 2.3) caught a HIGH-severity
case where a predicate registered under the `mr_22` key implemented
forbidden-restriction-site detection while MR.yaml rule MR-22 declared
"If wild-type WPRE detected → recommend WPRE3 (mut6) variant" — two
completely different biology checks sharing the same key.

This test enumerates known-defect predicate ↔ rule pairings that must NEVER
re-appear. It's deliberately narrow at v0.2.1 (one entry, the mr_22 case);
future audit-discovered drift cases should be added here.

The test passes when EITHER:
- The predicate is no longer bound to the rule_id under the defective name
  (preferred — see audit fix C4, where forbidden_internal_sites_predicate was
  decoupled from MR-22), OR
- The predicate has been re-implemented to match the rule's declared semantics.
"""

from __future__ import annotations

from engine.validation.predicates.internal_sites import INTERNAL_SITE_PREDICATES


def test_mr_22_is_not_bound_to_forbidden_internal_sites_predicate() -> None:
    """MR-22 declares WPRE wild-type detection — NOT forbidden restriction sites.

    Pre-v0.2.1, `INTERNAL_SITE_PREDICATES["mr_22"]` pointed to a forbidden-sites
    check function. The dict-merge ordering in `engine.validation.predicates.__init__`
    placed internal_sites AFTER structural so this incorrect binding shadowed
    the canonical StructuralMetricPredicate('mr_22').

    v0.2.1 audit fix C4 unbound forbidden-internal-sites from the mr_22 key.
    This test asserts the binding has not silently regressed.
    """
    assert "mr_22" not in INTERNAL_SITE_PREDICATES, (
        "MR-22 declares 'If wild-type WPRE detected → recommend WPRE3 (mut6) variant' "
        "(catalogues/rules/MR.yaml line ~754). Binding the forbidden-internal-sites "
        "predicate to mr_22 silently swaps the biology and was flagged HIGH by the "
        "2026-05-23 Scientific Advisor audit (§ 2.3). Either: "
        "(a) unbind from mr_22 (current v0.2.1 fix C4 — falls through to "
        "StructuralMetricPredicate which is a metric-backed stub), OR "
        "(b) implement real WPRE wild-type detection and rebind the predicate to "
        "match MR-22's declared semantics."
    )


def test_internal_site_predicates_dict_is_empty_at_v021() -> None:
    """The internal_sites registry was emptied at v0.2.1 fix C4.

    Future rules CAN opt into the forbidden-internal-sites helper, but each
    opt-in must be vetted that the rule's `description` field actually
    declares 'forbidden internal restriction sites' semantics — NOT some
    other biology that happens to share a numeric id.
    """
    assert INTERNAL_SITE_PREDICATES == {}, (
        "INTERNAL_SITE_PREDICATES was deliberately emptied at v0.2.1 (audit fix "
        "C4). If you're adding a rule_id → forbidden_internal_sites_predicate "
        "binding here, FIRST verify that the rule's description field in "
        "catalogues/rules/*.yaml declares 'forbidden internal restriction sites' "
        "semantics. If it declares a DIFFERENT biology, the binding is a "
        "Scientific Advisor § 2.3-class drift defect."
    )
