"""
module_id:           tests.engine.validation.test_mr_59_marker_host_compat_h4
file:                tests/engine/validation/test_mr_59_marker_host_compat_h4.py
task_id:             audit-fix-H4

Tests for the v0.2.1 MR-59 real predicate (marker-host auxotrophic compatibility).

Exercises the chain wired by audit fixes C3 (MarkersCataloguePort wiring),
C5 (canonical yeast genotype tokens on BY4741/BY4742/W303/etc.), and H4
(MR-59 real predicate implementation).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from adapter.catalogue.yaml_markers_catalogue import YamlMarkersCatalogue
from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, SafetyGate, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId
from domain.types.validation_rule import ValidationRule
from engine.markers_resolver import MarkersResolver
from engine.validation.predicates.marker_host_compat import (
    mr_59_marker_host_genotype_compat,
)
from engine.validation.validation_context import ValidationContext

REPO_ROOT = Path(__file__).resolve().parents[3]


def _make_mr_59_rule() -> ValidationRule:
    return ValidationRule(
        rule_id=RuleId("MR-59"),
        predicate_name="mr_59",
        severity=Severity.HARD,
        severity_policy=SeverityPolicy.BLOCK,
        blocks=frozenset({SafetyGate.COMPILE}),
        reads=frozenset({"construct", "host_context"}),
        depends_on_metrics=frozenset(),
        produces_metrics=frozenset({MetricId("metric.mr-59.result")}),
        invalidates=frozenset(),
        preconditions=(),
        target_context=ContextScope.CONSTRUCT,
        external_adapters=(),
        threshold_profile="thresholds.molecular.default",
        citation=GradedCitation(
            text="MR-59 fixture for v0.2.1 audit-fix-H4 unit test",
            grade="A1",
            accessed=date(2026, 5, 23),
            url="https://pubmed.ncbi.nlm.nih.gov/2659436/",
        ),
        last_reviewed=date(2026, 5, 23),
        reviewed_by=ReviewerId("audit-fix-h4"),
        test_fixtures=("tests/fixtures/rules/MR/triggering/MR-59.json",),
        suggested_remediation="Use BY4741/BY4742 (ura3Δ0) instead of S288C reference.",
    )


@pytest.fixture
def mr_59_rule() -> ValidationRule:
    return _make_mr_59_rule()


@pytest.fixture
def real_resolver() -> MarkersResolver:
    catalogue = YamlMarkersCatalogue(
        catalogue_path=REPO_ROOT / "catalogues" / "markers.yaml",
        schema_path=REPO_ROOT / "schemas" / "markers.schema.json",
    )
    return MarkersResolver(port=catalogue)


def test_mr_59_returns_info_when_no_resolver_wired(mr_59_rule: ValidationRule) -> None:
    """v0.1.0 baseline: no resolver → stub semantic (INFO), per the v0.2 phase contract."""
    context = ValidationContext(
        design_payload={
            "markers": ["marker.ura3"],
            "host": {"genotype": "MATa SUC2 gal2 mal mel flo1 hap1 ho"},
        },
        markers_resolver=None,
    )
    assert mr_59_marker_host_genotype_compat(context, mr_59_rule) is Severity.INFO


def test_mr_59_fires_hard_when_ura3_marker_in_ura3_intact_host(
    mr_59_rule: ValidationRule, real_resolver: MarkersResolver
) -> None:
    """A URA3 selection marker in a host with URA3 INTACT → no selection → HARD."""
    context = ValidationContext(
        design_payload={
            "markers": ["marker.ura3"],
            # S288C reference background has URA3 intact (it's the canonical wild-type)
            "host": {"genotype": "MATα SUC2 gal2 mal mel flo1 flo8-1 hap1 ho bio1 bio6"},  # noqa: RUF001
        },
        markers_resolver=real_resolver,
    )
    assert mr_59_marker_host_genotype_compat(context, mr_59_rule) is Severity.HARD


def test_mr_59_passes_with_info_when_ura3_marker_in_ura3_deleted_host(
    mr_59_rule: ValidationRule, real_resolver: MarkersResolver
) -> None:
    """A URA3 selection marker in BY4741 (ura3Δ0) → selection works → INFO."""
    context = ValidationContext(
        design_payload={
            "markers": ["marker.ura3"],
            # BY4741 carries ura3Δ0 (post-audit-fix C5 canonical genotype)
            "host": {"genotype": "MATa his3Δ1 leu2Δ0 met15Δ0 ura3Δ0 (BY4741)"},
        },
        markers_resolver=real_resolver,
    )
    assert mr_59_marker_host_genotype_compat(context, mr_59_rule) is Severity.INFO


def test_mr_59_passes_with_info_when_leu2_marker_in_w303_host(
    mr_59_rule: ValidationRule, real_resolver: MarkersResolver
) -> None:
    """A LEU2 selection marker in W303 (leu2-3,112) → selection works → INFO."""
    context = ValidationContext(
        design_payload={
            "markers": ["marker.leu2"],
            "host": {"genotype": "MATa/α leu2-3,112 trp1-1 can1-100 ura3-1 ade2-1 his3-11,15"},  # noqa: RUF001
        },
        markers_resolver=real_resolver,
    )
    assert mr_59_marker_host_genotype_compat(context, mr_59_rule) is Severity.INFO


def test_mr_59_skips_placeholder_host_genotype_strings(
    mr_59_rule: ValidationRule, real_resolver: MarkersResolver
) -> None:
    """A 'verify supplier genotype' placeholder is NOT actionable → INFO not HARD."""
    context = ValidationContext(
        design_payload={
            "markers": ["marker.ura3"],
            "host": {
                "genotype": (
                    "commercial auxotrophic expression background; verify supplier genotype."
                )
            },
        },
        markers_resolver=real_resolver,
    )
    # Placeholder is INFO not HARD; the predicate's "verify" check explicitly defers
    # to human curator action rather than firing a false positive.
    assert mr_59_marker_host_genotype_compat(context, mr_59_rule) is Severity.INFO


def test_mr_59_ignores_non_auxotrophic_markers(
    mr_59_rule: ValidationRule, real_resolver: MarkersResolver
) -> None:
    """A bacterial-only marker (e.g., marker.kanamycin) → INFO (no host_genotype_requirement)."""
    context = ValidationContext(
        design_payload={
            "markers": ["marker.kanamycin"],
            "host": {"genotype": "F- endA1 glnV44 thi-1 recA1 relA1 gyrA96 hsdR17"},
        },
        markers_resolver=real_resolver,
    )
    assert mr_59_marker_host_genotype_compat(context, mr_59_rule) is Severity.INFO


def test_mr_59_in_implemented_predicate_registry_overrides_stub() -> None:
    """The orchestrator's IMPLEMENTED_PREDICATE_REGISTRY must use the real MR-59 predicate."""
    from engine.validation.predicates import IMPLEMENTED_PREDICATE_REGISTRY

    assert "mr_59" in IMPLEMENTED_PREDICATE_REGISTRY
    # The real predicate is a function, not a StructuralMetricPredicate stub instance.
    predicate = IMPLEMENTED_PREDICATE_REGISTRY["mr_59"]
    assert callable(predicate)
    # The function's __name__ should be the real predicate name (not the stub class name).
    assert getattr(predicate, "__name__", "") == "mr_59_marker_host_genotype_compat"
