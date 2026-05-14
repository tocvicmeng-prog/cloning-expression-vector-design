"""
module_id: engine.validation.engine
file: src/engine/validation/engine.py
task_id: T-502

Pure validation DAG executor.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from domain.types.enums import Severity
from domain.types.ids import MetricId, RuleId
from domain.types.validation_rule import FieldPath, ValidationRule
from engine.dependencies import DependencyGraph, build_dependency_graph
from engine.validation.predicates import PREDICATE_REGISTRY
from engine.validation.predicates._stub import Predicate
from engine.validation.report import RuleEvaluation, RuleEvaluationError, ValidationReport
from engine.validation.validation_context import ValidationContext
from engine.validation.worker_pool_factory import WorkerPoolFactory, default_worker_pool_factory


@dataclass(frozen=True)
class RuleEvaluationTask:
    rule: ValidationRule
    context: ValidationContext
    predicate: Predicate


@dataclass(frozen=True)
class RuleEvaluationOutcome:
    evaluation: RuleEvaluation | None = None
    error: RuleEvaluationError | None = None


def evaluate_rule_task(task: RuleEvaluationTask) -> RuleEvaluationOutcome:
    predicate_name = _predicate_label(task.predicate, task.rule.predicate_name)
    try:
        observed = task.predicate(task.context, task.rule)
        if not isinstance(observed, Severity):
            raise TypeError(
                f"validation predicate must return Severity, got {type(observed).__name__}"
            )
        return RuleEvaluationOutcome(
            evaluation=RuleEvaluation(
                rule_id=task.rule.rule_id,
                predicate_name=predicate_name,
                declared_severity=task.rule.severity,
                severity_policy=task.rule.severity_policy,
                observed_severity=observed,
                blocks=task.rule.blocks,
            )
        )
    except Exception as exc:
        return RuleEvaluationOutcome(
            error=RuleEvaluationError(
                rule_id=task.rule.rule_id,
                predicate_name=predicate_name,
                cause_type=type(exc).__name__,
                message=str(exc),
            )
        )


def validate(
    context: ValidationContext,
    rules: Iterable[ValidationRule],
    *,
    predicate_registry: Mapping[str, Predicate] | None = None,
    graph: DependencyGraph | None = None,
    worker_pool_factory: WorkerPoolFactory | None = None,
    changed_fields: Iterable[FieldPath] | None = None,
    changed_metrics: Iterable[MetricId | str] | None = None,
) -> ValidationReport:
    active_graph = graph or build_dependency_graph(rules)
    active_registry = predicate_registry or PREDICATE_REGISTRY
    selected_rule_ids = _selected_rule_ids(
        active_graph,
        changed_fields=changed_fields,
        changed_metrics=changed_metrics,
    )
    tasks: list[RuleEvaluationTask] = []
    slots: list[RuleEvaluationTask | RuleEvaluationOutcome] = []
    for rule_id in selected_rule_ids:
        rule = active_graph.rules[rule_id]
        predicate = active_registry.get(rule.predicate_name)
        if predicate is None:
            slots.append(
                RuleEvaluationOutcome(
                    error=RuleEvaluationError(
                        rule_id=rule.rule_id,
                        predicate_name=rule.predicate_name,
                        cause_type="LookupError",
                        message=f"unknown validation predicate: {rule.predicate_name}",
                    )
                )
            )
            continue
        task = RuleEvaluationTask(rule=rule, context=context, predicate=predicate)
        tasks.append(task)
        slots.append(task)

    factory = worker_pool_factory or default_worker_pool_factory()
    if tasks:
        with factory.create() as pool:
            outcomes = pool.map(evaluate_rule_task, tasks)
    else:
        outcomes = ()

    mapped_outcomes = iter(outcomes)
    evaluations: list[RuleEvaluation] = []
    errors: list[RuleEvaluationError] = []
    for slot in slots:
        outcome = next(mapped_outcomes) if isinstance(slot, RuleEvaluationTask) else slot
        if outcome.evaluation is not None:
            evaluations.append(outcome.evaluation)
        if outcome.error is not None:
            errors.append(outcome.error)
    return ValidationReport(evaluations=tuple(evaluations), errors=tuple(errors))


def validate_all(
    context: ValidationContext,
    rules: Iterable[ValidationRule],
    *,
    predicate_registry: Mapping[str, Predicate] | None = None,
    graph: DependencyGraph | None = None,
    worker_pool_factory: WorkerPoolFactory | None = None,
) -> ValidationReport:
    return validate(
        context,
        rules,
        predicate_registry=predicate_registry,
        graph=graph,
        worker_pool_factory=worker_pool_factory,
    )


def _selected_rule_ids(
    graph: DependencyGraph,
    *,
    changed_fields: Iterable[FieldPath] | None,
    changed_metrics: Iterable[MetricId | str] | None,
) -> tuple[RuleId, ...]:
    if changed_fields is None and changed_metrics is None:
        return graph.topological_rule_order()

    selected: set[RuleId] = set()
    if changed_fields is not None:
        selected.update(graph.affected_by_fields(tuple(changed_fields)).affected_rules)
    if changed_metrics is not None:
        metrics = tuple(MetricId(str(metric)) for metric in changed_metrics)
        selected.update(graph.affected_by_metrics(metrics).affected_rules)
    return graph.topological_rule_order(selected)


def _predicate_label(predicate: Predicate, fallback: str) -> str:
    name = getattr(predicate, "__name__", None)
    if isinstance(name, str) and name:
        return name
    return fallback


__all__ = [
    "RuleEvaluationOutcome",
    "RuleEvaluationTask",
    "evaluate_rule_task",
    "validate",
    "validate_all",
]
