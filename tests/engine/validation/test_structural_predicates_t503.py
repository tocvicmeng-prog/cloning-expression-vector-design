"""
module_id: tests.engine.validation.test_structural_predicates_t503
file: tests/engine/validation/test_structural_predicates_t503.py
task_id: T-503
"""

from __future__ import annotations

import pickle
from datetime import date

from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, SafetyGate, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates import IMPLEMENTED_PREDICATE_REGISTRY
from engine.validation.predicates.frame import mr_10_reading_frame, mr_11_tandem_stop
from engine.validation.predicates.host import host_compatibility_report_clear
from engine.validation.predicates.internal_sites import mr_22_forbidden_internal_sites
from engine.validation.validation_context import ValidationContext


def test_t503_implemented_predicate_registry_covers_structural_subset_without_br14() -> None:
    assert len(IMPLEMENTED_PREDICATE_REGISTRY) >= 50
    assert "br_13" in IMPLEMENTED_PREDICATE_REGISTRY
    assert "br_14" not in IMPLEMENTED_PREDICATE_REGISTRY
    for predicate in IMPLEMENTED_PREDICATE_REGISTRY.values():
        assert pickle.loads(pickle.dumps(predicate)) is not None


def test_structural_metric_predicate_uses_metric_or_payload_violation_flags() -> None:
    predicate = IMPLEMENTED_PREDICATE_REGISTRY["wr_06"]
    rule = _rule("WR-06", "wr_06", severity=Severity.SOFT)

    metric_report = predicate(
        ValidationContext(metrics={MetricId("predicate.wr_06.violated"): True}),
        rule,
    )
    payload_report = predicate(
        ValidationContext(design_payload={"predicate_violations": {"wr_06": True}}),
        rule,
    )
    passing_report = predicate(ValidationContext(), rule)

    assert metric_report is Severity.SOFT
    assert payload_report is Severity.SOFT
    assert passing_report is Severity.INFO


def test_frame_predicates_evaluate_orf_start_stop_and_tandem_stop_strategy() -> None:
    rule = _rule("MR-10", "mr_10")
    tandem_rule = _rule("MR-11", "mr_11", severity=Severity.SOFT)

    assert (
        mr_10_reading_frame(
            ValidationContext(design_payload={"coding_sequences": ["ATGAAATAA"]}),
            rule,
        )
        is Severity.INFO
    )
    assert (
        mr_10_reading_frame(
            ValidationContext(design_payload={"coding_sequences": ["ATGTAGTAA"]}),
            rule,
        )
        is Severity.HARD
    )
    assert (
        mr_11_tandem_stop(
            ValidationContext(design_payload={"coding_sequences": ["ATGAAATAA"]}),
            tandem_rule,
        )
        is Severity.SOFT
    )
    assert (
        mr_11_tandem_stop(
            ValidationContext(design_payload={"coding_sequences": ["ATGAAATAATAA"]}),
            tandem_rule,
        )
        is Severity.INFO
    )


def test_internal_site_predicate_uses_sequence_analysis_site_finder() -> None:
    rule = _rule("MR-22", "mr_22")

    assert (
        mr_22_forbidden_internal_sites(
            ValidationContext(
                design_payload={
                    "sequence": "AAAGAATTCCCC",
                    "forbidden_restriction_sites": [
                        {"name": "EcoRI", "recognition_site": "GAATTC", "cut_index": 1}
                    ],
                }
            ),
            rule,
        )
        is Severity.HARD
    )
    assert (
        mr_22_forbidden_internal_sites(
            ValidationContext(
                design_payload={
                    "sequence": "AAAACCCCGGGG",
                    "forbidden_restriction_sites": [
                        {"name": "EcoRI", "recognition_site": "GAATTC", "cut_index": 1}
                    ],
                }
            ),
            rule,
        )
        is Severity.INFO
    )


def test_host_predicate_consumes_t504_compatibility_metric() -> None:
    rule = _rule("MR-01", "mr_01")

    assert (
        host_compatibility_report_clear(
            ValidationContext(metrics={MetricId("compatibility.report.passed"): False}),
            rule,
        )
        is Severity.HARD
    )
    assert (
        host_compatibility_report_clear(
            ValidationContext(metrics={MetricId("compatibility.report.passed"): True}),
            rule,
        )
        is Severity.INFO
    )


def _rule(
    rule_id: str,
    predicate_name: str,
    *,
    severity: Severity = Severity.HARD,
) -> ValidationRule:
    return ValidationRule(
        rule_id=RuleId(rule_id),
        predicate_name=predicate_name,
        severity=severity,
        severity_policy=(
            SeverityPolicy.BLOCK if severity is Severity.HARD else SeverityPolicy.WARN_ACKNOWLEDGE
        ),
        blocks=frozenset({SafetyGate.COMPILE}) if severity is Severity.HARD else frozenset(),
        reads=frozenset({"construct"}),
        depends_on_metrics=frozenset(),
        produces_metrics=frozenset({MetricId(f"metric.{predicate_name}")}),
        invalidates=frozenset(),
        preconditions=(),
        target_context=ContextScope.CONSTRUCT,
        external_adapters=(),
        threshold_profile="thresholds.test",
        citation=GradedCitation(
            text="T-503 predicate fixture",
            grade="B2",
            accessed=date(2026, 5, 14),
            url="CODING_AGENDA.md",
        ),
        last_reviewed=date(2026, 5, 14),
        reviewed_by=ReviewerId("tester"),
        test_fixtures=("triggering.json", "passing.json"),
        suggested_remediation="fix structural predicate fixture",
    )
