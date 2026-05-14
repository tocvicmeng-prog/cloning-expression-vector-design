"""
module_id: engine.dependencies
file: src/engine/dependencies.py
task_id: T-501

Validation dependency graph over rule reads and metric production.
"""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Literal

from domain.types.ids import MetricId, RuleId
from domain.types.validation_rule import FieldPath, ValidationRule

NodeKind = Literal["field", "metric", "rule"]
EdgeReason = Literal["reads", "depends_on_metric", "produces_metric", "invalidates"]


class DependencyCycleError(ValueError):
    """Raised when rule metric dependencies contain a producer cycle."""


@dataclass(frozen=True, order=True)
class DependencyNode:
    kind: NodeKind
    identifier: str


@dataclass(frozen=True, order=True)
class DependencyEdge:
    source: DependencyNode
    target: DependencyNode
    reason: EdgeReason


@dataclass(frozen=True)
class DependencyImpact:
    changed_fields: frozenset[FieldPath]
    changed_metrics: frozenset[MetricId]
    affected_rules: tuple[RuleId, ...]
    required_metrics: frozenset[MetricId]
    invalidated_metrics: frozenset[MetricId]
    invalidated_rules: frozenset[RuleId]
    traversal_order: tuple[RuleId, ...]


class DependencyGraph:
    def __init__(self, rules: Iterable[ValidationRule]) -> None:
        self._rules = _index_rules(rules)
        self._field_readers = _field_readers(self._rules)
        self._metric_consumers = _metric_consumers(self._rules)
        self._metric_producers = _metric_producers(self._rules)
        self._rule_to_consumers = _rule_to_metric_consumers(
            self._rules,
            self._metric_consumers,
        )
        self._edges = _edges(self._rules)

    @property
    def rules(self) -> Mapping[RuleId, ValidationRule]:
        return self._rules

    @property
    def edges(self) -> tuple[DependencyEdge, ...]:
        return self._edges

    @property
    def nodes(self) -> tuple[DependencyNode, ...]:
        nodes: set[DependencyNode] = set()
        for edge in self._edges:
            nodes.add(edge.source)
            nodes.add(edge.target)
        return tuple(sorted(nodes))

    def affected_by_fields(self, changed_fields: Iterable[FieldPath]) -> DependencyImpact:
        changed = frozenset(changed_fields)
        initial_rules = {
            rule_id for field in changed for rule_id in self._rules_affected_by_field(field)
        }
        return self._impact(
            changed_fields=changed, changed_metrics=frozenset(), initial_rules=initial_rules
        )

    def affected_by_metrics(self, changed_metrics: Iterable[MetricId]) -> DependencyImpact:
        changed = frozenset(changed_metrics)
        initial_rules = {
            rule_id
            for metric in changed
            for rule_id in self._metric_consumers.get(metric, frozenset())
        }
        return self._impact(
            changed_fields=frozenset(), changed_metrics=changed, initial_rules=initial_rules
        )

    def required_metrics_for_rules(self, rule_ids: Iterable[RuleId]) -> frozenset[MetricId]:
        return frozenset(
            metric
            for rule_id in rule_ids
            for metric in self._rules[_expect_rule(rule_id, self._rules)].depends_on_metrics
        )

    def topological_rule_order(
        self, rule_ids: Iterable[RuleId] | None = None
    ) -> tuple[RuleId, ...]:
        selected = frozenset(
            self._rules
            if rule_ids is None
            else (_expect_rule(rule, self._rules) for rule in rule_ids)
        )
        dependencies: dict[RuleId, set[RuleId]] = {rule_id: set() for rule_id in selected}
        dependents: dict[RuleId, set[RuleId]] = {rule_id: set() for rule_id in selected}
        for producer, consumers in self._rule_to_consumers.items():
            if producer not in selected:
                continue
            for consumer in consumers & selected:
                dependencies[consumer].add(producer)
                dependents[producer].add(consumer)
        ready = deque(sorted(rule_id for rule_id, deps in dependencies.items() if not deps))
        ordered: list[RuleId] = []
        while ready:
            current = ready.popleft()
            ordered.append(current)
            for dependent in sorted(dependents[current]):
                dependencies[dependent].discard(current)
                if not dependencies[dependent]:
                    ready.append(dependent)
        if len(ordered) != len(selected):
            remaining = ", ".join(
                sorted(str(rule_id) for rule_id, deps in dependencies.items() if deps)
            )
            raise DependencyCycleError(f"validation rule dependency cycle: {remaining}")
        return tuple(ordered)

    def _impact(
        self,
        *,
        changed_fields: frozenset[FieldPath],
        changed_metrics: frozenset[MetricId],
        initial_rules: set[RuleId],
    ) -> DependencyImpact:
        affected = set(initial_rules)
        invalidated_metrics: set[MetricId] = set(changed_metrics)
        invalidated_rules: set[RuleId] = set()
        queue = deque(sorted(initial_rules))
        while queue:
            rule_id = queue.popleft()
            rule = self._rules[rule_id]
            newly_invalidated_metrics = set(rule.produces_metrics)
            newly_invalidated_rules = {
                RuleId(str(item)) for item in rule.invalidates if RuleId(str(item)) in self._rules
            }
            newly_invalidated_metrics.update(
                MetricId(str(item))
                for item in rule.invalidates
                if RuleId(str(item)) not in self._rules
            )
            invalidated_metrics.update(newly_invalidated_metrics)
            invalidated_rules.update(newly_invalidated_rules)
            downstream = set(newly_invalidated_rules)
            for metric in newly_invalidated_metrics:
                downstream.update(self._metric_consumers.get(MetricId(str(metric)), frozenset()))
            for downstream_rule in sorted(downstream):
                if downstream_rule not in affected:
                    affected.add(downstream_rule)
                    queue.append(downstream_rule)
        order = self.topological_rule_order(affected)
        return DependencyImpact(
            changed_fields=changed_fields,
            changed_metrics=changed_metrics,
            affected_rules=order,
            required_metrics=self.required_metrics_for_rules(order),
            invalidated_metrics=frozenset(invalidated_metrics),
            invalidated_rules=frozenset(invalidated_rules),
            traversal_order=order,
        )

    def _rules_affected_by_field(self, changed_field: FieldPath) -> frozenset[RuleId]:
        return frozenset(
            rule_id
            for read_field, rules in self._field_readers.items()
            if _field_paths_overlap(changed_field, read_field)
            for rule_id in rules
        )


def build_dependency_graph(rules: Iterable[ValidationRule]) -> DependencyGraph:
    return DependencyGraph(rules)


def _index_rules(rules: Iterable[ValidationRule]) -> dict[RuleId, ValidationRule]:
    indexed: dict[RuleId, ValidationRule] = {}
    for rule in rules:
        if rule.rule_id in indexed:
            raise ValueError(f"duplicate validation rule: {rule.rule_id}")
        indexed[rule.rule_id] = rule
    return indexed


def _field_readers(rules: Mapping[RuleId, ValidationRule]) -> dict[FieldPath, frozenset[RuleId]]:
    readers: dict[FieldPath, set[RuleId]] = defaultdict(set)
    for rule_id, rule in rules.items():
        for field in rule.reads:
            readers[field].add(rule_id)
    return {field: frozenset(rule_ids) for field, rule_ids in readers.items()}


def _metric_consumers(rules: Mapping[RuleId, ValidationRule]) -> dict[MetricId, frozenset[RuleId]]:
    consumers: dict[MetricId, set[RuleId]] = defaultdict(set)
    for rule_id, rule in rules.items():
        for metric in rule.depends_on_metrics:
            consumers[metric].add(rule_id)
    return {metric: frozenset(rule_ids) for metric, rule_ids in consumers.items()}


def _metric_producers(rules: Mapping[RuleId, ValidationRule]) -> dict[MetricId, frozenset[RuleId]]:
    producers: dict[MetricId, set[RuleId]] = defaultdict(set)
    for rule_id, rule in rules.items():
        for metric in rule.produces_metrics:
            producers[metric].add(rule_id)
    return {metric: frozenset(rule_ids) for metric, rule_ids in producers.items()}


def _rule_to_metric_consumers(
    rules: Mapping[RuleId, ValidationRule],
    metric_consumers: Mapping[MetricId, frozenset[RuleId]],
) -> dict[RuleId, frozenset[RuleId]]:
    consumer_map: dict[RuleId, set[RuleId]] = defaultdict(set)
    for rule_id, rule in rules.items():
        for metric in rule.produces_metrics:
            consumer_map[rule_id].update(metric_consumers.get(metric, frozenset()))
    return {rule_id: frozenset(consumers) for rule_id, consumers in consumer_map.items()}


def _edges(rules: Mapping[RuleId, ValidationRule]) -> tuple[DependencyEdge, ...]:
    edges: set[DependencyEdge] = set()
    for rule_id, rule in rules.items():
        rule_node = DependencyNode("rule", str(rule_id))
        for field in rule.reads:
            edges.add(DependencyEdge(DependencyNode("field", field), rule_node, "reads"))
        for metric in rule.depends_on_metrics:
            edges.add(
                DependencyEdge(
                    DependencyNode("metric", str(metric)), rule_node, "depends_on_metric"
                )
            )
        for metric in rule.produces_metrics:
            edges.add(
                DependencyEdge(rule_node, DependencyNode("metric", str(metric)), "produces_metric")
            )
        for item in rule.invalidates:
            kind: NodeKind = "rule" if item in rules else "metric"
            edges.add(DependencyEdge(rule_node, DependencyNode(kind, str(item)), "invalidates"))
    return tuple(sorted(edges))


def _expect_rule(rule_id: RuleId, rules: Mapping[RuleId, ValidationRule]) -> RuleId:
    if rule_id not in rules:
        raise KeyError(f"unknown validation rule: {rule_id}")
    return rule_id


def _field_paths_overlap(changed: str, declared_read: str) -> bool:
    return (
        changed == declared_read
        or changed.startswith(f"{declared_read}.")
        or declared_read.startswith(f"{changed}.")
    )
