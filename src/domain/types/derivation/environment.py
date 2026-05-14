"""
module_id: domain.types.derivation.environment
file: src/domain/types/derivation/environment.py
task_id: T-307

Replay-deterministic derivation environment.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, NewType

from domain.canonicalisation import canonical_json
from domain.sequence import Sha256
from domain.types.derivation.policies import ExportProfile, PrivacyClassification, ScreeningScope

Semver = NewType("Semver", str)
CatalogueId = NewType("CatalogueId", str)
PluginId = NewType("PluginId", str)
DatabaseId = NewType("DatabaseId", str)
SopTemplateId = NewType("SopTemplateId", str)
ContainerDigest = NewType("ContainerDigest", str)
UnitsProfile = NewType("UnitsProfile", str)
RoundingPolicy = NewType("RoundingPolicy", str)
RandomSeedId = NewType("RandomSeedId", str)
AuthProfileId = NewType("AuthProfileId", str)
PromptTemplateId = NewType("PromptTemplateId", str)
LLMUseSite = NewType("LLMUseSite", str)
LLMModelIdentifier = NewType("LLMModelIdentifier", str)
GateName = NewType("GateName", str)
PredicateVersion = NewType("PredicateVersion", str)


@dataclass(frozen=True)
class OptimisationSettings:
    strategy: str
    objective_weights: tuple[tuple[str, Decimal], ...] = ()
    max_iterations: int = 0

    def __post_init__(self) -> None:
        _require_non_empty(self.strategy, "optimisation strategy")
        if self.max_iterations < 0:
            raise ValueError("max_iterations cannot be negative")
        _require_unique_keys(self.objective_weights, "objective_weights")


@dataclass(frozen=True)
class UserOverride:
    override_id: str
    path: str
    value: object
    reason: str

    def __post_init__(self) -> None:
        _require_non_empty(self.override_id, "override_id")
        _require_non_empty(self.path, "path")
        _require_non_empty(self.reason, "reason")


@dataclass(frozen=True)
class ReviewerDecision:
    decision_id: str
    reviewer_id: str
    decision_type: str
    decision_content_hash: Sha256

    def __post_init__(self) -> None:
        _require_non_empty(self.decision_id, "decision_id")
        _require_non_empty(self.reviewer_id, "reviewer_id")
        _require_non_empty(self.decision_type, "decision_type")
        _require_non_empty(str(self.decision_content_hash), "decision_content_hash")


@dataclass(frozen=True)
class DerivationEnvironmentV14:
    rule_registry_version: Semver
    rule_manifest_hashes: dict[str, Sha256]
    catalogue_versions: dict[CatalogueId, Semver]
    catalogue_content_hashes: dict[CatalogueId, Sha256]
    plugin_versions: dict[PluginId, Semver]
    plugin_configurations: dict[PluginId, Sha256]
    external_database_versions: dict[DatabaseId, str]
    sop_template_versions: dict[SopTemplateId, Semver]
    container_image_digest: ContainerDigest
    cpu_arch: str
    locale: str
    units_profile: UnitsProfile
    rounding_policy: RoundingPolicy
    random_seeds: dict[RandomSeedId, int]
    optimisation_settings: OptimisationSettings
    user_overrides: tuple[UserOverride, ...]
    reviewer_decisions: tuple[ReviewerDecision, ...]
    construct_checksum: Sha256
    authorisation_profile_id: AuthProfileId | None
    authorisation_profile_content_hash: Sha256 | None
    sop_template_content_hashes: dict[SopTemplateId, Sha256]
    screening_provider_trust_policy_version: Semver
    screening_query_scope: ScreeningScope
    screening_threshold_policy_version: Semver
    screening_submitted_sequence_hash: Sha256
    plugin_package_hashes: dict[PluginId, Sha256]
    llm_prompt_template_versions: dict[PromptTemplateId, Semver]
    llm_model_identifiers: dict[LLMUseSite, LLMModelIdentifier]
    institutional_policy_version: Semver
    user_declaration_hash: Sha256
    export_profile: ExportProfile
    redaction_policy_version: Semver
    risk_advisory_catalogue_version: Semver
    risk_advisory_catalogue_content_hash: Sha256
    privacy_classification: PrivacyClassification
    advisory_approval_trace_hash: Sha256 | None = None
    advisory_acknowledgement_event_ids: tuple[str, ...] = ()
    gate_predicate_versions: dict[GateName, PredicateVersion] = field(default_factory=dict)
    gate_predicate_content_hashes: dict[GateName, Sha256] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty(str(self.rule_registry_version), "rule_registry_version")
        _require_non_empty(str(self.container_image_digest), "container_image_digest")
        _require_non_empty(self.cpu_arch, "cpu_arch")
        _require_non_empty(self.locale, "locale")
        _require_non_empty(str(self.units_profile), "units_profile")
        _require_non_empty(str(self.rounding_policy), "rounding_policy")
        _require_non_empty(str(self.construct_checksum), "construct_checksum")
        _require_non_empty(
            str(self.screening_provider_trust_policy_version),
            "screening_provider_trust_policy_version",
        )
        _require_non_empty(
            str(self.screening_threshold_policy_version),
            "screening_threshold_policy_version",
        )
        _require_non_empty(
            str(self.screening_submitted_sequence_hash),
            "screening_submitted_sequence_hash",
        )
        _require_non_empty(str(self.institutional_policy_version), "institutional_policy_version")
        _require_non_empty(str(self.user_declaration_hash), "user_declaration_hash")
        _require_non_empty(str(self.redaction_policy_version), "redaction_policy_version")
        _require_non_empty(
            str(self.risk_advisory_catalogue_version),
            "risk_advisory_catalogue_version",
        )
        _require_non_empty(
            str(self.risk_advisory_catalogue_content_hash),
            "risk_advisory_catalogue_content_hash",
        )
        _require_optional_non_empty(
            self.authorisation_profile_id,
            "authorisation_profile_id",
        )
        _require_optional_non_empty(
            self.authorisation_profile_content_hash,
            "authorisation_profile_content_hash",
        )
        _require_optional_non_empty(
            self.advisory_approval_trace_hash,
            "advisory_approval_trace_hash",
        )
        _require_non_empty_mapping(self.rule_manifest_hashes, "rule_manifest_hashes")
        _require_non_empty_mapping(self.catalogue_versions, "catalogue_versions")
        _require_non_empty_mapping(self.catalogue_content_hashes, "catalogue_content_hashes")
        _require_no_empty_values(self.random_seeds, "random_seeds")
        _require_no_empty_values(self.advisory_acknowledgement_event_ids, "event_id")
        _require_unique_keys(self.optimisation_settings.objective_weights, "objective_weights")

    def canonical_json(self) -> bytes:
        return canonical_json(self)

    def hash(self) -> Sha256:
        return Sha256(hashlib.sha256(self.canonical_json()).hexdigest())


DerivationEnvironment = DerivationEnvironmentV14


def _require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} cannot be empty")


def _require_optional_non_empty(value: object | None, field_name: str) -> None:
    if value is not None:
        _require_non_empty(str(value), field_name)


def _require_non_empty_mapping(mapping: Mapping[Any, Any], field_name: str) -> None:
    if not mapping:
        raise ValueError(f"{field_name} cannot be empty")
    _require_no_empty_values(mapping.keys(), f"{field_name} key")
    _require_no_empty_values(mapping.values(), f"{field_name} value")


def _require_no_empty_values(values: Iterable[object], field_name: str) -> None:
    for value in values:
        _require_non_empty(str(value), field_name)


def _require_unique_keys(pairs: tuple[tuple[str, object], ...], field_name: str) -> None:
    seen: set[str] = set()
    for key, _value in pairs:
        _require_non_empty(key, f"{field_name} key")
        if key in seen:
            raise ValueError(f"{field_name} contains duplicate key: {key}")
        seen.add(key)
