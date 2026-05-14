"""
module_id: tests.domain.types.test_derivation_environment
file: tests/domain/types/test_derivation_environment.py
task_id: T-307
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from domain.canonicalisation import CanonicalisationError
from domain.sequence import Sha256, sha256_text
from domain.types.derivation import (
    CatalogueId,
    ContainerDigest,
    DatabaseId,
    DerivationEnvironmentV14,
    ExportProfile,
    GateName,
    LLMModelIdentifier,
    LLMUseSite,
    OptimisationSettings,
    PluginId,
    PredicateVersion,
    PrivacyClassification,
    PromptTemplateId,
    RandomSeedId,
    ReviewerDecision,
    RoundingPolicy,
    ScreeningScope,
    Semver,
    SopTemplateId,
    UnitsProfile,
    UserOverride,
)


def _environment(random_seeds: dict[RandomSeedId, int] | None = None) -> DerivationEnvironmentV14:
    return DerivationEnvironmentV14(
        rule_registry_version=Semver("1.0.0"),
        rule_manifest_hashes={"MR": sha256_text("mr")},
        catalogue_versions={CatalogueId("parts"): Semver("2026.5.14")},
        catalogue_content_hashes={CatalogueId("parts"): sha256_text("parts")},
        plugin_versions={PluginId("codon"): Semver("1.2.3")},
        plugin_configurations={PluginId("codon"): sha256_text("plugin-config")},
        external_database_versions={DatabaseId("rebase"): "2026-05"},
        sop_template_versions={SopTemplateId("sop-assembly"): Semver("2.0.0")},
        container_image_digest=ContainerDigest("sha256:container"),
        cpu_arch="x86_64",
        locale="C.UTF-8",
        units_profile=UnitsProfile("si-v1"),
        rounding_policy=RoundingPolicy("half-even-6dp"),
        random_seeds=random_seeds or {RandomSeedId("optimiser"): 7},
        optimisation_settings=OptimisationSettings(
            strategy="deterministic",
            objective_weights=(("gc_balance", Decimal("0.50")),),
            max_iterations=10,
        ),
        user_overrides=(
            UserOverride(
                override_id="override-1",
                path="/assembly/max_fragments",
                value=6,
                reason="Institutional fixture for deterministic test",
            ),
        ),
        reviewer_decisions=(
            ReviewerDecision(
                decision_id="decision-1",
                reviewer_id="reviewer-1",
                decision_type="approve",
                decision_content_hash=sha256_text("decision"),
            ),
        ),
        construct_checksum=sha256_text("construct"),
        authorisation_profile_id=None,
        authorisation_profile_content_hash=None,
        sop_template_content_hashes={SopTemplateId("sop-assembly"): sha256_text("sop")},
        screening_provider_trust_policy_version=Semver("1.0.0"),
        screening_query_scope=ScreeningScope.ASSEMBLED_PRODUCT,
        screening_threshold_policy_version=Semver("1.0.0"),
        screening_submitted_sequence_hash=sha256_text("submitted"),
        plugin_package_hashes={PluginId("codon"): sha256_text("plugin-package")},
        llm_prompt_template_versions={PromptTemplateId("advisory"): Semver("1.0.0")},
        llm_model_identifiers={LLMUseSite("advisory_text"): LLMModelIdentifier("none")},
        institutional_policy_version=Semver("2026.05"),
        user_declaration_hash=sha256_text("declaration"),
        export_profile=ExportProfile.INTERNAL_AUDIT,
        redaction_policy_version=Semver("1.0.0"),
        risk_advisory_catalogue_version=Semver("2026.05"),
        risk_advisory_catalogue_content_hash=sha256_text("risk-catalogue"),
        privacy_classification=PrivacyClassification.SENSITIVE,
        advisory_approval_trace_hash=Sha256("sha256:trace"),
        advisory_acknowledgement_event_ids=("event-1",),
        gate_predicate_versions={GateName("BlockCompile"): PredicateVersion("1.0.0")},
        gate_predicate_content_hashes={GateName("BlockCompile"): sha256_text("predicate")},
    )


def test_derivation_environment_canonical_json_includes_v14_and_v15_fields() -> None:
    canonical = _environment().canonical_json().decode("utf-8")

    assert '"risk_advisory_catalogue_content_hash"' in canonical
    assert '"privacy_classification":"sensitive"' in canonical
    assert '"advisory_approval_trace_hash":"sha256:trace"' in canonical
    assert '"gate_predicate_versions":{"BlockCompile":"1.0.0"}' in canonical
    assert len(str(_environment().hash())) == 64


@given(
    st.dictionaries(
        keys=st.sampled_from(
            [
                RandomSeedId("optimiser"),
                RandomSeedId("library-expansion"),
                RandomSeedId("primer-search"),
            ]
        ),
        values=st.integers(min_value=0, max_value=2**31 - 1),
        min_size=1,
        max_size=3,
    )
)
def test_equal_derivation_environment_values_have_identical_bytes_and_hashes(
    seeds: dict[RandomSeedId, int],
) -> None:
    left = _environment(dict(seeds))
    right = _environment(dict(reversed(tuple(seeds.items()))))

    assert left.canonical_json() == right.canonical_json()
    assert left.hash() == right.hash()


def test_derivation_environment_rejects_nan_during_canonicalisation() -> None:
    environment = _environment()
    broken = DerivationEnvironmentV14(
        **{
            **environment.__dict__,
            "user_overrides": (
                UserOverride(
                    override_id="override-nan",
                    path="/unsafe",
                    value=float("nan"),
                    reason="Exercise canonicalisation rejection.",
                ),
            ),
        }
    )

    with pytest.raises(CanonicalisationError, match="NaN and Infinity"):
        broken.canonical_json()
