"""
module_id: tests.engine.validation.test_validation_engine
file: tests/engine/validation/test_validation_engine.py
task_id: T-502
"""

from __future__ import annotations

import pickle
from datetime import date
from typing import cast

from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, SafetyGate, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId
from domain.types.validation_rule import ValidationRule
from engine.validation import (
    PREDICATE_REGISTRY,
    ValidationContext,
    WorkerPoolFactory,
    validate,
)
from engine.validation.predicates._stub import Predicate


def hard_predicate(context: ValidationContext, rule: ValidationRule) -> Severity:
    del context, rule
    return Severity.HARD


def soft_predicate(context: ValidationContext, rule: ValidationRule) -> Severity:
    del context, rule
    return Severity.SOFT


def info_predicate(context: ValidationContext, rule: ValidationRule) -> Severity:
    del context, rule
    return Severity.INFO


def required_metric_predicate(context: ValidationContext, rule: ValidationRule) -> Severity:
    del rule
    context.require_metric("metric.required")
    return Severity.INFO


def failing_predicate(context: ValidationContext, rule: ValidationRule) -> Severity:
    del context, rule
    raise RuntimeError("predicate exploded")


def bad_return_predicate(context: ValidationContext, rule: ValidationRule) -> object:
    del context, rule
    return "not-a-severity"


def test_validate_walks_rules_in_dependency_order() -> None:
    rules = (
        _rule(
            "R-B",
            predicate_name="info_predicate",
            depends=("metric.produced",),
            produces=("metric.final",),
        ),
        _rule(
            "R-A",
            predicate_name="soft_predicate",
            reads=("construct.sequence",),
            produces=("metric.produced",),
            severity=Severity.SOFT,
        ),
    )

    report = validate(ValidationContext(), rules, predicate_registry=_registry())

    assert not report.errors
    assert tuple(evaluation.rule_id for evaluation in report.evaluations) == (
        RuleId("R-A"),
        RuleId("R-B"),
    )


def test_validate_routes_hard_soft_and_info_severity() -> None:
    rules = (
        _rule("R-HARD", predicate_name="hard_predicate"),
        _rule("R-SOFT", predicate_name="soft_predicate", severity=Severity.SOFT),
        _rule("R-INFO", predicate_name="info_predicate", severity=Severity.INFO),
    )

    report = validate(ValidationContext(), rules, predicate_registry=_registry())

    assert not report.errors
    assert report.blocked_gates == frozenset({SafetyGate.COMPILE})
    assert tuple(evaluation.rule_id for evaluation in report.findings) == (
        RuleId("R-HARD"),
        RuleId("R-SOFT"),
    )
    assert not report.passed


def test_validate_incrementally_evaluates_affected_rules_only() -> None:
    rules = (
        _rule(
            "R-A",
            predicate_name="info_predicate",
            reads=("construct.sequence",),
            produces=("metric.changed",),
        ),
        _rule(
            "R-B",
            predicate_name="info_predicate",
            depends=("metric.changed",),
            produces=("metric.downstream",),
        ),
        _rule(
            "R-C",
            predicate_name="info_predicate",
            reads=("host_context",),
            produces=("metric.host",),
        ),
    )

    report = validate(
        ValidationContext(),
        rules,
        predicate_registry=_registry(),
        changed_fields=("construct",),
    )
    metric_report = validate(
        ValidationContext(),
        rules,
        predicate_registry=_registry(),
        changed_metrics=("metric.changed",),
    )

    assert tuple(evaluation.rule_id for evaluation in report.evaluations) == (
        RuleId("R-A"),
        RuleId("R-B"),
    )
    assert tuple(evaluation.rule_id for evaluation in metric_report.evaluations) == (RuleId("R-B"),)


def test_validate_aggregates_missing_predicate_and_runtime_errors() -> None:
    rules = (
        _rule("R-BAD-RETURN", predicate_name="bad_return_predicate"),
        _rule("R-FAILING", predicate_name="failing_predicate"),
        _rule("R-MISSING", predicate_name="missing_predicate"),
        _rule("R-METRIC", predicate_name="required_metric_predicate"),
    )
    registry = _registry()
    registry["bad_return_predicate"] = cast(Predicate, bad_return_predicate)

    report = validate(ValidationContext(), rules, predicate_registry=registry)

    assert report.evaluations == ()
    assert [error.cause_type for error in report.errors] == [
        "TypeError",
        "RuntimeError",
        "MissingValidationMetricError",
        "LookupError",
    ]
    assert not report.passed


def test_validation_report_canonical_json_is_stable_over_repeated_runs() -> None:
    rules = tuple(
        _rule(
            f"R-{index:03d}",
            predicate_name="soft_predicate" if index % 2 else "info_predicate",
            reads=(f"construct.feature_{index}",),
            severity=Severity.SOFT if index % 2 else Severity.INFO,
        )
        for index in range(12)
    )

    reports = {
        validate(
            ValidationContext(random_seed=99), rules, predicate_registry=_registry()
        ).canonical_json()
        for _ in range(100)
    }

    assert len(reports) == 1


def test_thread_worker_pool_matches_sequential_report() -> None:
    rules = tuple(
        _rule(
            f"R-{index:03d}",
            predicate_name="soft_predicate" if index % 2 else "info_predicate",
            reads=(f"construct.feature_{index}",),
            severity=Severity.SOFT if index % 2 else Severity.INFO,
        )
        for index in range(10)
    )
    context = ValidationContext(random_seed=17)

    sequential = validate(
        context,
        rules,
        predicate_registry=_registry(),
        worker_pool_factory=WorkerPoolFactory("sequential"),
    )
    threaded = validate(
        context,
        rules,
        predicate_registry=_registry(),
        worker_pool_factory=WorkerPoolFactory("thread", max_workers=3),
    )

    assert threaded.to_payload() == sequential.to_payload()


def test_validation_context_seed_is_stable_and_context_is_picklable() -> None:
    rule = _rule("R-SEED")
    context = ValidationContext(metrics={MetricId("metric.required"): 7}, random_seed=123)
    restored = pickle.loads(pickle.dumps(context))

    assert isinstance(restored, ValidationContext)
    assert restored.require_metric(MetricId("metric.required")) == 7
    assert context.predicate_seed(rule) == ValidationContext(random_seed=123).predicate_seed(rule)
    assert context.predicate_seed(rule) != ValidationContext(random_seed=124).predicate_seed(rule)


def test_registered_predicates_are_picklable() -> None:
    for predicate in PREDICATE_REGISTRY.values():
        restored = pickle.loads(pickle.dumps(predicate))
        assert restored is not None


def _registry() -> dict[str, Predicate]:
    return {
        "failing_predicate": failing_predicate,
        "hard_predicate": hard_predicate,
        "info_predicate": info_predicate,
        "required_metric_predicate": required_metric_predicate,
        "soft_predicate": soft_predicate,
    }


def _rule(
    rule_id: str,
    *,
    predicate_name: str = "info_predicate",
    severity: Severity = Severity.HARD,
    blocks: frozenset[SafetyGate] | None = None,
    reads: tuple[str, ...] = ("construct",),
    depends: tuple[str, ...] = (),
    produces: tuple[str, ...] | None = None,
    invalidates: tuple[MetricId | RuleId, ...] = (),
) -> ValidationRule:
    resolved_blocks = (
        blocks
        if blocks is not None
        else frozenset({SafetyGate.COMPILE})
        if severity is Severity.HARD
        else frozenset()
    )
    resolved_produces = produces if produces is not None else (f"metric.{rule_id.lower()}",)
    return ValidationRule(
        rule_id=RuleId(rule_id),
        predicate_name=predicate_name,
        severity=severity,
        severity_policy=_severity_policy(severity),
        blocks=resolved_blocks,
        reads=frozenset(reads),
        depends_on_metrics=frozenset(MetricId(metric) for metric in depends),
        produces_metrics=frozenset(MetricId(metric) for metric in resolved_produces),
        invalidates=frozenset(invalidates),
        preconditions=(),
        target_context=ContextScope.CONSTRUCT,
        external_adapters=(),
        threshold_profile="thresholds.test",
        citation=GradedCitation(
            text="test citation",
            grade="B2",
            accessed=date(2026, 5, 14),
            url="REQUIREMENTS.md",
        ),
        last_reviewed=date(2026, 5, 14),
        reviewed_by=ReviewerId("tester"),
        test_fixtures=("triggering.json", "passing.json"),
        suggested_remediation="fix the test rule",
    )


def _severity_policy(severity: Severity) -> SeverityPolicy:
    if severity is Severity.HARD:
        return SeverityPolicy.BLOCK
    if severity is Severity.SOFT:
        return SeverityPolicy.WARN_ACKNOWLEDGE
    return SeverityPolicy.REPORT_ONLY
