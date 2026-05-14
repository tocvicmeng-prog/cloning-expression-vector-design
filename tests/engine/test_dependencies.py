"""
module_id: tests.engine.test_dependencies
file: tests/engine/test_dependencies.py
task_id: T-501
"""

from __future__ import annotations

from datetime import date

import pytest

from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, SafetyGate, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId
from domain.types.validation_rule import ValidationRule
from engine.dependencies import DependencyCycleError, DependencyGraph, build_dependency_graph


def test_dependency_graph_marks_field_readers_and_metric_consumers_affected() -> None:
    graph = build_dependency_graph(
        (
            _rule(
                "MR-01",
                reads=("construct.sequence",),
                produces=("metric.promoter.compatibility",),
            ),
            _rule(
                "WR-01",
                reads=("host_context",),
                depends=("metric.promoter.compatibility",),
                produces=("metric.warning",),
            ),
        )
    )

    impact = graph.affected_by_fields(("construct",))

    assert impact.affected_rules == (RuleId("MR-01"), RuleId("WR-01"))
    assert impact.required_metrics == frozenset({MetricId("metric.promoter.compatibility")})
    assert impact.invalidated_metrics == frozenset(
        {MetricId("metric.promoter.compatibility"), MetricId("metric.warning")}
    )
    assert impact.traversal_order == impact.affected_rules


def test_dependency_graph_supports_metric_first_revalidation() -> None:
    graph = DependencyGraph(
        (
            _rule("MR-01", produces=("metric.compatibility",)),
            _rule("MR-02", depends=("metric.compatibility",), produces=("metric.final",)),
        )
    )

    impact = graph.affected_by_metrics((MetricId("metric.compatibility"),))

    assert impact.changed_metrics == frozenset({MetricId("metric.compatibility")})
    assert impact.affected_rules == (RuleId("MR-02"),)
    assert impact.invalidated_metrics == frozenset(
        {MetricId("metric.compatibility"), MetricId("metric.final")}
    )


def test_dependency_graph_tracks_explicit_invalidated_rules_and_metrics() -> None:
    graph = DependencyGraph(
        (
            _rule(
                "MR-01",
                produces=("metric.primary",),
                invalidates=(MetricId("metric.cached"), RuleId("WR-01")),
            ),
            _rule("WR-01", depends=("metric.cached",), produces=("metric.warning",)),
        )
    )

    impact = graph.affected_by_fields(("construct",))

    assert RuleId("WR-01") in impact.invalidated_rules
    assert MetricId("metric.cached") in impact.invalidated_metrics
    assert impact.affected_rules == (RuleId("MR-01"), RuleId("WR-01"))


def test_dependency_graph_topological_order_rejects_cycles() -> None:
    graph = DependencyGraph(
        (
            _rule("MR-01", depends=("metric.two",), produces=("metric.one",)),
            _rule("MR-02", depends=("metric.one",), produces=("metric.two",)),
        )
    )

    with pytest.raises(DependencyCycleError, match="MR-01"):
        graph.topological_rule_order()


def test_dependency_graph_rejects_duplicate_rules_and_unknown_rule_queries() -> None:
    rule = _rule("MR-01")

    with pytest.raises(ValueError, match="duplicate"):
        DependencyGraph((rule, rule))
    with pytest.raises(KeyError, match="unknown validation rule"):
        DependencyGraph((rule,)).required_metrics_for_rules((RuleId("MR-99"),))


def test_dependency_graph_exposes_nodes_and_edges_for_diagnostics() -> None:
    graph = DependencyGraph(
        (
            _rule(
                "MR-01",
                reads=("construct",),
                depends=("metric.input",),
                produces=("metric.output",),
            ),
        )
    )

    edge_reasons = {edge.reason for edge in graph.edges}
    node_ids = {node.identifier for node in graph.nodes}
    assert edge_reasons == {"reads", "depends_on_metric", "produces_metric"}
    assert {"construct", "MR-01", "metric.input", "metric.output"} <= node_ids


def _rule(
    rule_id: str,
    *,
    reads: tuple[str, ...] = ("construct",),
    depends: tuple[str, ...] = (),
    produces: tuple[str, ...] = ("metric.result",),
    invalidates: tuple[MetricId | RuleId, ...] = (),
) -> ValidationRule:
    return ValidationRule(
        rule_id=RuleId(rule_id),
        predicate_name=rule_id.lower().replace("-", "_"),
        severity=Severity.HARD,
        severity_policy=SeverityPolicy.BLOCK,
        blocks=frozenset({SafetyGate.COMPILE}),
        reads=frozenset(reads),
        depends_on_metrics=frozenset(MetricId(metric) for metric in depends),
        produces_metrics=frozenset(MetricId(metric) for metric in produces),
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
