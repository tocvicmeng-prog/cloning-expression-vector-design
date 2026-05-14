"""
module_id: tests.engine.validation.test_biology_predicates_t602
file: tests/engine/validation/test_biology_predicates_t602.py
task_id: T-602
"""

from __future__ import annotations

from datetime import date

from adapter.biology import (
    NodererKozakAdapter,
    RbsCalcV2Adapter,
    SignalPAdapter,
    SpliceAiAdapter,
    ViennaRnaAdapter,
)
from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, SafetyGate, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId
from domain.types.validation_rule import ValidationRule
from engine.validation.predicates import IMPLEMENTED_PREDICATE_REGISTRY, PREDICATE_REGISTRY
from engine.validation.predicates.cpg import mr_27_cpg_content_threshold
from engine.validation.predicates.kozak import mr_13_kozak_pwm_threshold
from engine.validation.predicates.premature_polya import mr_15_premature_polya_scan
from engine.validation.predicates.rbs import mr_12_rbs_window_and_accessibility
from engine.validation.predicates.signal_peptide import mr_28_signal_peptide_compartment_consistency
from engine.validation.predicates.splice import mr_16_splice_score_threshold
from engine.validation.predicates.uorf import mr_14_upstream_orf_scan
from engine.validation.validation_context import ValidationContext


def test_t602_registry_adds_biology_predicates_without_mutating_stub_registry() -> None:
    names = {"mr_12", "mr_13", "mr_14", "mr_15", "mr_16", "mr_27", "mr_28"}

    assert names <= set(IMPLEMENTED_PREDICATE_REGISTRY)
    for name in names:
        assert (
            PREDICATE_REGISTRY[name](ValidationContext(), _rule(name.upper(), name))
            is Severity.INFO
        )


def test_mr12_consumes_rbs_and_rna_accessibility_metrics_from_t601() -> None:
    rule = _rule("MR-12", "mr_12", severity=Severity.SOFT)
    rbs = RbsCalcV2Adapter().predict_tir("TTTAGGAGGAAAAAAATGGCT", {"host_id": "ecoli"})
    fold = ViennaRnaAdapter().fold("AUGGCU")

    assert (
        mr_12_rbs_window_and_accessibility(
            ValidationContext(
                metrics={
                    MetricId("biology.rbs.shine_dalgarno_motif"): rbs["shine_dalgarno_motif"],
                    MetricId("biology.rbs.spacing_nt"): rbs["spacing_nt"],
                    MetricId("biology.rbs.translation_initiation_rate"): rbs[
                        "translation_initiation_rate"
                    ],
                    MetricId("biology.rna.mfe_kcal_mol"): fold["mfe_kcal_mol"],
                }
            ),
            rule,
        )
        is Severity.INFO
    )
    assert (
        mr_12_rbs_window_and_accessibility(
            ValidationContext(
                metrics={
                    MetricId("biology.rbs.shine_dalgarno_motif"): None,
                    MetricId("biology.rbs.spacing_nt"): 2,
                    MetricId("biology.rna.mfe_kcal_mol"): -12.0,
                }
            ),
            rule,
        )
        is Severity.SOFT
    )


def test_mr13_kozak_threshold_uses_precomputed_metric() -> None:
    rule = _rule("MR-13", "mr_13", severity=Severity.SOFT)
    strong = NodererKozakAdapter().score_kozak("GCCACCATGGCT", {"host_id": "hek293"})

    assert (
        mr_13_kozak_pwm_threshold(
            ValidationContext(metrics={MetricId("biology.kozak.score"): strong["score"]}),
            rule,
        )
        is Severity.INFO
    )
    assert (
        mr_13_kozak_pwm_threshold(
            ValidationContext(metrics={MetricId("biology.kozak.score"): 0.3}),
            rule,
        )
        is Severity.SOFT
    )


def test_mr14_and_mr15_scan_sequence_context_when_metrics_are_absent() -> None:
    uorf_rule = _rule("MR-14", "mr_14", severity=Severity.SOFT)
    polya_rule = _rule("MR-15", "mr_15", severity=Severity.SOFT)

    assert (
        mr_14_upstream_orf_scan(
            ValidationContext(design_payload={"five_prime_utr": "AAAGCCACCATGGGG"}),
            uorf_rule,
        )
        is Severity.SOFT
    )
    assert (
        mr_14_upstream_orf_scan(
            ValidationContext(design_payload={"five_prime_utr": "CCCCCCCC"}),
            uorf_rule,
        )
        is Severity.INFO
    )
    assert (
        mr_15_premature_polya_scan(
            ValidationContext(design_payload={"coding_sequences": ["ATGAAATAAAAACCC"]}),
            polya_rule,
        )
        is Severity.SOFT
    )
    assert (
        mr_15_premature_polya_scan(
            ValidationContext(design_payload={"coding_sequences": ["ATGGCTGATGAA"]}),
            polya_rule,
        )
        is Severity.INFO
    )


def test_mr16_splice_threshold_uses_prediction_payloads() -> None:
    rule = _rule("MR-16", "mr_16", severity=Severity.SOFT)
    predictions = SpliceAiAdapter().predict_splice_effects("AAAGTCCCTTTAGAAA")

    assert (
        mr_16_splice_score_threshold(
            ValidationContext(metrics={MetricId("biology.splice.predictions"): predictions}),
            rule,
        )
        is Severity.INFO
    )
    high_score = [dict(predictions[0]) | {"score": 0.9}]
    assert (
        mr_16_splice_score_threshold(
            ValidationContext(metrics={MetricId("biology.splice.predictions"): high_score}),
            rule,
        )
        is Severity.SOFT
    )


def test_mr27_cpg_content_uses_metrics_or_sequence_fallback() -> None:
    rule = _rule("MR-27", "mr_27", severity=Severity.SOFT)

    assert (
        mr_27_cpg_content_threshold(
            ValidationContext(metrics={MetricId("biology.cpg.observed_expected"): 1.5}),
            rule,
        )
        is Severity.SOFT
    )
    assert (
        mr_27_cpg_content_threshold(
            ValidationContext(design_payload={"sequence": "CG" * 12 + "AT" * 8}),
            rule,
        )
        is Severity.SOFT
    )
    assert (
        mr_27_cpg_content_threshold(
            ValidationContext(design_payload={"sequence": "ATGAAATTTGGG"}),
            rule,
        )
        is Severity.INFO
    )


def test_mr28_signal_peptide_compartment_consistency() -> None:
    rule = _rule("MR-28", "mr_28", severity=Severity.SOFT)
    signal = SignalPAdapter().predict_signal_peptide("MKKLLLLLLLLLLLLLLAASAQA")

    assert (
        mr_28_signal_peptide_compartment_consistency(
            ValidationContext(
                design_payload={
                    "declared_compartment": "secreted",
                    "protein_sequence": "MKKLLLLLLLLLLLLLLAASAQA",
                },
                metrics={
                    MetricId("biology.signal_peptide.has_signal_peptide"): signal[
                        "has_signal_peptide"
                    ]
                },
            ),
            rule,
        )
        is Severity.INFO
    )
    assert (
        mr_28_signal_peptide_compartment_consistency(
            ValidationContext(
                design_payload={"declared_compartment": "secreted", "protein_sequence": "MTEYK"},
                metrics={MetricId("biology.signal_peptide.has_signal_peptide"): False},
            ),
            rule,
        )
        is Severity.SOFT
    )
    assert (
        mr_28_signal_peptide_compartment_consistency(
            ValidationContext(
                design_payload={
                    "declared_compartment": "cytosol",
                    "protein_sequence": "MKKLLLLLLLLLLLLLLAASAQA",
                },
                metrics={MetricId("biology.signal_peptide.has_signal_peptide"): True},
            ),
            rule,
        )
        is Severity.SOFT
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
            text="T-602 predicate fixture",
            grade="B2",
            accessed=date(2026, 5, 14),
            url="CODING_AGENDA.md",
        ),
        last_reviewed=date(2026, 5, 14),
        reviewed_by=ReviewerId("tester"),
        test_fixtures=("triggering.json", "passing.json"),
        suggested_remediation="fix biology predicate fixture",
    )
