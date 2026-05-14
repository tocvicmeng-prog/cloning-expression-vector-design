"""
module_id: tests.app.test_validation_orchestrator_t603
file: tests/app/test_validation_orchestrator_t603.py
task_id: T-603
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

import pytest

from app.validation_orchestrator import (
    RBS_METRICS,
    RNA_FOLD_METRICS,
    BiologyAdapterSet,
    DesignSessionMetricCache,
    MissingBiologyAdapterError,
    ValidationOrchestrator,
)
from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId
from domain.types.validation_rule import ValidationRule


class CountingTirPredictor:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def predict_tir(
        self,
        sequence: str,
        host_context: Mapping[str, object],
    ) -> dict[str, object]:
        del host_context
        self.calls.append(sequence)
        if "AGGAGG" in sequence:
            return {
                "shine_dalgarno_motif": "AGGAGG",
                "spacing_nt": 6,
                "translation_initiation_rate": 15000.0,
            }
        return {
            "shine_dalgarno_motif": None,
            "spacing_nt": None,
            "translation_initiation_rate": 0.0,
        }


class CountingRnaFolder:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def fold(self, sequence: str) -> dict[str, object]:
        self.calls.append(sequence)
        return {"mfe_kcal_mol": -5.0 if "AGGAGG" in sequence else -12.0}


class CountingKozakScorer:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def score_kozak(
        self,
        sequence: str,
        host_context: Mapping[str, object],
    ) -> dict[str, object]:
        del host_context
        self.calls.append(sequence)
        return {"score": 1.0 if sequence.startswith("GCCACC") else 0.2}


def test_incremental_module_change_recomputes_only_affected_rules_and_metrics() -> None:
    tir = CountingTirPredictor()
    rna = CountingRnaFolder()
    kozak = CountingKozakScorer()
    orchestrator = ValidationOrchestrator(
        biology_adapters=BiologyAdapterSet(
            rna_folder=rna,
            tir_predictor=tir,
            kozak_scorer=kozak,
        ),
        metric_cache=DesignSessionMetricCache(),
        max_metric_workers=3,
    )
    rules = (
        _rule(
            "MR-12",
            "mr_12",
            reads=("rbs_module",),
            depends=(
                "biology.rbs.shine_dalgarno_motif",
                "biology.rbs.spacing_nt",
                "biology.rbs.translation_initiation_rate",
                "biology.rna.mfe_kcal_mol",
            ),
        ),
        _rule("MR-13", "mr_13", reads=("kozak_module",), depends=("biology.kozak.score",)),
    )

    first = orchestrator.validate_design(
        session_id="session-1",
        design_payload={
            "rbs_sequence": "TTTAGGAGGAAAAAAATGGCT",
            "kozak_sequence": "GCCACCATGGCT",
            "host_context": {"host_id": "ecoli"},
        },
        rule_registry=rules,
        derivation_environment_hash="env-a",
    )
    second = orchestrator.validate_design(
        session_id="session-1",
        design_payload={
            "rbs_sequence": "TTTAAAAAAATGGCT",
            "kozak_sequence": "GCCACCATGGCT",
            "host_context": {"host_id": "ecoli"},
        },
        rule_registry=rules,
        derivation_environment_hash="env-a",
        changed_fields=("rbs_module",),
    )

    assert [evaluation.rule_id for evaluation in first.report.evaluations] == [
        RuleId("MR-12"),
        RuleId("MR-13"),
    ]
    assert first.report.findings == ()
    assert [evaluation.rule_id for evaluation in second.report.evaluations] == [RuleId("MR-12")]
    assert [finding.rule_id for finding in second.report.findings] == [RuleId("MR-12")]
    assert second.computed_metric_ids == RBS_METRICS | RNA_FOLD_METRICS
    assert second.reused_metric_ids == frozenset()
    assert second.tier2_budget_met
    assert tir.calls == ["TTTAGGAGGAAAAAAATGGCT", "TTTAAAAAAATGGCT"]
    assert rna.calls == ["TTTAGGAGGAAAAAAATGGCT", "TTTAAAAAAATGGCT"]
    assert kozak.calls == ["GCCACCATGGCT"]


def test_metric_cache_is_bound_to_derivation_environment_hash() -> None:
    kozak = CountingKozakScorer()
    orchestrator = ValidationOrchestrator(
        biology_adapters=BiologyAdapterSet(kozak_scorer=kozak),
        metric_cache=DesignSessionMetricCache(),
    )
    rules = (_rule("MR-13", "mr_13", reads=("kozak_module",), depends=("biology.kozak.score",)),)
    payload = {"kozak_sequence": "GCCACCATGGCT", "host_context": {"host_id": "hek293"}}

    first = orchestrator.validate_design(
        session_id="session-2",
        design_payload=payload,
        rule_registry=rules,
        derivation_environment_hash="env-a",
    )
    reused = orchestrator.validate_design(
        session_id="session-2",
        design_payload=payload,
        rule_registry=rules,
        derivation_environment_hash="env-a",
        changed_fields=("kozak_module",),
    )
    rebound = orchestrator.validate_design(
        session_id="session-2",
        design_payload=payload,
        rule_registry=rules,
        derivation_environment_hash="env-b",
        changed_fields=("kozak_module",),
    )

    assert first.computed_metric_ids == frozenset({MetricId("biology.kozak.score")})
    assert reused.computed_metric_ids == frozenset()
    assert reused.reused_metric_ids == frozenset({MetricId("biology.kozak.score")})
    assert rebound.computed_metric_ids == frozenset({MetricId("biology.kozak.score")})
    assert kozak.calls == ["GCCACCATGGCT", "GCCACCATGGCT"]


def test_none_metric_values_are_reused_from_cache() -> None:
    tir = CountingTirPredictor()
    rna = CountingRnaFolder()
    orchestrator = ValidationOrchestrator(
        biology_adapters=BiologyAdapterSet(
            rna_folder=rna,
            tir_predictor=tir,
        ),
        metric_cache=DesignSessionMetricCache(),
    )
    rules = (
        _rule(
            "MR-12",
            "mr_12",
            reads=("rbs_module",),
            depends=(
                "biology.rbs.shine_dalgarno_motif",
                "biology.rbs.spacing_nt",
                "biology.rbs.translation_initiation_rate",
                "biology.rna.mfe_kcal_mol",
            ),
        ),
    )
    payload = {"rbs_sequence": "TTTAAAAAAATGGCT", "host_context": {"host_id": "ecoli"}}

    first = orchestrator.validate_design(
        session_id="session-none-cache",
        design_payload=payload,
        rule_registry=rules,
        derivation_environment_hash="env-a",
    )
    reused = orchestrator.validate_design(
        session_id="session-none-cache",
        design_payload=payload,
        rule_registry=rules,
        derivation_environment_hash="env-a",
        changed_fields=("rbs_module",),
    )

    assert first.context.metrics[MetricId("biology.rbs.shine_dalgarno_motif")] is None
    assert reused.computed_metric_ids == frozenset()
    assert reused.reused_metric_ids == RBS_METRICS | RNA_FOLD_METRICS
    assert tir.calls == ["TTTAAAAAAATGGCT"]
    assert rna.calls == ["TTTAAAAAAATGGCT"]


def test_missing_required_biology_adapter_fails_before_pure_validation() -> None:
    orchestrator = ValidationOrchestrator(biology_adapters=BiologyAdapterSet())
    rules = (
        _rule(
            "MR-28",
            "mr_28",
            reads=("secretory_module",),
            depends=("biology.signal_peptide.has_signal_peptide",),
        ),
    )

    with pytest.raises(MissingBiologyAdapterError, match="SignalPeptidePredictor"):
        orchestrator.validate_design(
            session_id="session-3",
            design_payload={"protein_sequence": "MKKLLLLLLLLLLLLLLAASAQA"},
            rule_registry=rules,
            derivation_environment_hash="env-a",
        )


def _rule(
    rule_id: str,
    predicate_name: str,
    *,
    reads: tuple[str, ...],
    depends: tuple[str, ...],
) -> ValidationRule:
    return ValidationRule(
        rule_id=RuleId(rule_id),
        predicate_name=predicate_name,
        severity=Severity.SOFT,
        severity_policy=SeverityPolicy.WARN_ACKNOWLEDGE,
        blocks=frozenset(),
        reads=frozenset(reads),
        depends_on_metrics=frozenset(MetricId(metric) for metric in depends),
        produces_metrics=frozenset({MetricId(f"metric.{rule_id.lower()}.result")}),
        invalidates=frozenset(),
        preconditions=(),
        target_context=ContextScope.CONSTRUCT,
        external_adapters=(),
        threshold_profile="thresholds.test",
        citation=GradedCitation(
            text="T-603 integration test fixture",
            grade="B2",
            accessed=date(2026, 5, 14),
            url="CODING_AGENDA.md#t-603",
        ),
        last_reviewed=date(2026, 5, 14),
        reviewed_by=ReviewerId("tester"),
        test_fixtures=("triggering.json", "passing.json"),
        suggested_remediation="fix the validation orchestrator test fixture",
    )
