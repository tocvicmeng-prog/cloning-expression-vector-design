"""
module_id: engine.validation
file: src/engine/validation/__init__.py
task_id: T-405

Validation package scaffold with T-405 predicate stubs.
"""

from __future__ import annotations

from typing import NoReturn

from engine.validation.engine import (
    RuleEvaluationOutcome,
    RuleEvaluationTask,
    evaluate_rule_task,
    validate,
    validate_all,
)
from engine.validation.predicates import PREDICATE_REGISTRY, Predicate, resolve_predicate
from engine.validation.report import RuleEvaluation, RuleEvaluationError, ValidationReport
from engine.validation.validation_context import MissingValidationMetricError, ValidationContext
from engine.validation.worker_pool_factory import (
    ProcessWorkerPool,
    SequentialWorkerPool,
    ThreadWorkerPool,
    WorkerPool,
    WorkerPoolFactory,
    WorkerPoolMode,
    default_worker_pool_factory,
)

MODULE_ID = "engine.validation"
OWNING_TASKS = ("T-502", "T-503", "T-602")


class PublicApiStub:
    """Marker class replaced by the owning implementation task."""


def module_not_implemented() -> NoReturn:
    """Raise until engine.validation's public API is implemented by its owning task."""
    raise NotImplementedError(f"{MODULE_ID} public API is scheduled in {OWNING_TASKS}")


__all__ = [
    "PREDICATE_REGISTRY",
    "MissingValidationMetricError",
    "Predicate",
    "ProcessWorkerPool",
    "PublicApiStub",
    "RuleEvaluation",
    "RuleEvaluationError",
    "RuleEvaluationOutcome",
    "RuleEvaluationTask",
    "SequentialWorkerPool",
    "ThreadWorkerPool",
    "ValidationContext",
    "ValidationReport",
    "WorkerPool",
    "WorkerPoolFactory",
    "WorkerPoolMode",
    "default_worker_pool_factory",
    "evaluate_rule_task",
    "module_not_implemented",
    "resolve_predicate",
    "validate",
    "validate_all",
]
