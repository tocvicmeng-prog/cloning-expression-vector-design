"""
module_id: engine.validation.validation_context
file: src/engine/validation/validation_context.py
task_id: T-502

Pure validation context with precomputed metrics.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass, field

from domain.types.ids import MetricId
from domain.types.validation_rule import ValidationRule
from engine.markers_resolver import MarkersResolver


class MissingValidationMetricError(KeyError):
    """Raised when a rule asks for a metric absent from the context."""


@dataclass(frozen=True)
class ValidationContext:
    design_payload: Mapping[str, object] = field(default_factory=dict)
    metrics: Mapping[MetricId, object] = field(default_factory=dict)
    threshold_profile: str = "thresholds.default"
    derivation_environment_hash: str | None = None
    random_seed: int = 0
    # v0.2 Enrichment Amendment (T-413, ARCHITECTURE.md § 9.2): optional resolver
    # over MarkersCataloguePort. Predicates in this v0.2 stage are stubs returning
    # Severity.INFO (see src/engine/validation/predicates/mr.py), so a None
    # resolver is the documented v0.1.0 baseline behaviour. Phase 5/6 promotes
    # the MR-55..60 stubs to real predicates that read marker payloads via this
    # resolver (concentration, host_genotype_requirement, etc.).
    markers_resolver: MarkersResolver | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "design_payload", dict(self.design_payload))
        object.__setattr__(self, "metrics", dict(self.metrics))
        if not self.threshold_profile:
            raise ValueError("threshold_profile cannot be empty")

    def require_metric(self, metric_id: MetricId | str) -> object:
        key = MetricId(str(metric_id))
        try:
            return self.metrics[key]
        except KeyError as exc:
            raise MissingValidationMetricError(str(key)) from exc

    def predicate_seed(self, rule: ValidationRule) -> int:
        seed_material = f"{self.random_seed}:{rule.rule_id}".encode()
        digest = hashlib.sha256(seed_material).digest()
        return int.from_bytes(digest[:4], byteorder="big", signed=False)
