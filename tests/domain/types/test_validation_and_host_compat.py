"""
module_id: tests.domain.types
file: tests/domain/types/test_validation_and_host_compat.py
task_id: T-303
"""

from __future__ import annotations

from datetime import date

import pytest

from domain.types import (
    BiosafetyTier,
    ChassisClass,
    ContextScope,
    GradedCitation,
    HostCompatibilityConstraints,
    HostRole,
    MetricId,
    ReviewerId,
    RuleId,
    SafetyGate,
    Severity,
    SeverityPolicy,
    ValidationRule,
)


def _citation() -> GradedCitation:
    return GradedCitation(
        text="Fixture source",
        grade="A1",
        accessed=date(2026, 5, 14),
        doi="10.0000/example",
    )


def _rule(
    severity: Severity = Severity.HARD,
    blocks: frozenset[SafetyGate] | None = None,
) -> ValidationRule:
    severity_policy = (
        SeverityPolicy.BLOCK if severity is Severity.HARD else SeverityPolicy.REPORT_ONLY
    )
    return ValidationRule(
        rule_id=RuleId("MR-001"),
        predicate_name="check_marker_origin_compatibility",
        severity=severity,
        severity_policy=severity_policy,
        blocks=frozenset({SafetyGate.COMPILE}) if blocks is None else blocks,
        reads=frozenset({"construct.modules"}),
        depends_on_metrics=frozenset({MetricId("insert_length")}),
        produces_metrics=frozenset(),
        invalidates=frozenset(),
        preconditions=(),
        target_context=ContextScope.CONSTRUCT,
        external_adapters=(),
        threshold_profile="default",
        citation=_citation(),
        last_reviewed=date(2026, 5, 14),
        reviewed_by=ReviewerId("reviewer-1"),
        test_fixtures=("fixture-a",),
        suggested_remediation="Choose a compatible marker/origin pair.",
    )


def test_validation_rule_accepts_hard_rule_with_blocking_gate() -> None:
    assert _rule().blocks == frozenset({SafetyGate.COMPILE})


def test_validation_rule_rejects_invalid_gate_and_fixture_shapes() -> None:
    with pytest.raises(ValueError, match="HARD"):
        _rule(blocks=frozenset())
    with pytest.raises(ValueError, match="INFO"):
        _rule(severity=Severity.INFO, blocks=frozenset({SafetyGate.COMPILE}))
    with pytest.raises(ValueError, match="read"):
        ValidationRule(
            rule_id=RuleId("MR-001"),
            predicate_name="predicate",
            severity=Severity.SOFT,
            severity_policy=SeverityPolicy.WARN_ACKNOWLEDGE,
            blocks=frozenset(),
            reads=frozenset(),
            depends_on_metrics=frozenset(),
            produces_metrics=frozenset(),
            invalidates=frozenset(),
            preconditions=(),
            target_context=ContextScope.CONSTRUCT,
            external_adapters=(),
            threshold_profile="default",
            citation=_citation(),
            last_reviewed=date(2026, 5, 14),
            reviewed_by=ReviewerId("reviewer-1"),
            test_fixtures=("fixture-a",),
            suggested_remediation="Fix it.",
        )


def test_host_compatibility_constraints_validate_chassis_and_notes() -> None:
    constraints = HostCompatibilityConstraints(
        role=HostRole.EXPRESSION,
        allowed_chassis=frozenset({ChassisClass.BACTERIAL}),
        notes=("E. coli expression only",),
    )

    assert constraints.role is HostRole.EXPRESSION

    with pytest.raises(ValueError, match="allowed_chassis"):
        HostCompatibilityConstraints(role=HostRole.EXPRESSION, allowed_chassis=frozenset())
    with pytest.raises(ValueError, match="notes"):
        HostCompatibilityConstraints(
            role=HostRole.EXPRESSION,
            allowed_chassis=frozenset({ChassisClass.BACTERIAL}),
            notes=("",),
        )


def test_biosafety_tier_enum_exposes_unsupported_tier_for_later_gate() -> None:
    assert BiosafetyTier.BSL_4.value == "BSL-4"
