"""
module_id: domain.types.screening
file: src/domain/types/screening.py
task_id: audit-fix-M5

Domain-layer value types for the screening subsystem.

These types are CANONICAL — the runtime engine, the app composition layer, and
the adapter implementations all dispatch on them. They were originally defined
inline in `adapter/screening/base.py` (T-1002) which created an architectural
inversion: the App layer (`app.authorisation_decision`, `app.screening_orchestrator`)
had to import value types via the adapter package, structurally binding App to
the adapter path.

The collaborative audit (2026-05-23 Architect § 1.2 Finding 1.3) called this
out as a hexagonal-layering defect. v0.2.1 fix M5 relocates the definitions
to `domain.types.screening` (this file). `adapter.screening.base` continues
to re-export the names for backward compatibility with existing direct
imports.

The import-linter contract `[importlinter:contract:domain-boundary]` requires
that `domain.*` MUST NOT import from `adapter.*` — which is what this move
correctly inverts. After the move, the adapter is allowed to import from
the domain (which is the canonical hexagonal direction).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from domain.sequence import Sha256


class ScreeningVerdict(Enum):
    CLEAR = "CLEAR"
    WATCHLIST = "WATCHLIST"
    HIT = "HIT"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


class NotApplicableReason(Enum):
    BELOW_MINIMUM_LENGTH = "below_minimum_length"
    POLICY_EXCLUDED_FRAGMENT = "policy_excluded_fragment"
    POLICY_EXCLUDED_ORF = "policy_excluded_orf"
    UNSUPPORTED_SCOPE = "unsupported_scope"


class ScreeningScope(Enum):
    ASSEMBLED_PRODUCT = "assembled_product"
    ORDER_FRAGMENT = "order_fragment"
    TRANSLATED_ORF = "translated_orf"


@dataclass(frozen=True)
class ScreeningProviderPolicy:
    provider_id: str
    name: str
    trust_level: str
    query_privacy_mode: str
    accepted_verdicts: frozenset[ScreeningVerdict]
    canonical_at_this_scope: bool

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id cannot be empty")
        if not self.accepted_verdicts:
            raise ValueError("provider policy requires at least one accepted verdict")


@dataclass(frozen=True)
class ScreeningTrustPolicy:
    policy_id: str
    policy_version: str
    minimum_synthetic_na_nt: int
    screen_assembled_product: bool
    screen_order_fragments: bool
    screen_translated_orfs_when_applicable: bool
    preserve_query_privacy_when_supported: bool
    verdict_blocks: Mapping[ScreeningVerdict, frozenset[str]]
    providers: Mapping[str, ScreeningProviderPolicy]
    policy_content_hash: Sha256

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id cannot be empty")
        if self.minimum_synthetic_na_nt <= 0:
            raise ValueError("minimum_synthetic_na_nt must be positive")

    def provider_policy(self, provider_id: str, scope: ScreeningScope) -> ScreeningProviderPolicy:
        try:
            provider = self.providers[provider_id]
        except KeyError as exc:
            raise ValueError(f"unknown screening provider: {provider_id}") from exc
        return ScreeningProviderPolicy(
            provider_id=provider.provider_id,
            name=provider.name,
            trust_level=provider.trust_level,
            query_privacy_mode=provider.query_privacy_mode,
            accepted_verdicts=provider.accepted_verdicts,
            canonical_at_this_scope=self._canonical_for(provider, scope),
        )

    def scope_applicable(self, scope: ScreeningScope) -> tuple[bool, NotApplicableReason | None]:
        if scope is ScreeningScope.ASSEMBLED_PRODUCT:
            return self.screen_assembled_product, NotApplicableReason.UNSUPPORTED_SCOPE
        if scope is ScreeningScope.ORDER_FRAGMENT:
            return self.screen_order_fragments, NotApplicableReason.POLICY_EXCLUDED_FRAGMENT
        if scope is ScreeningScope.TRANSLATED_ORF:
            return (
                self.screen_translated_orfs_when_applicable,
                NotApplicableReason.POLICY_EXCLUDED_ORF,
            )
        return False, NotApplicableReason.UNSUPPORTED_SCOPE

    def _canonical_for(
        self,
        provider: ScreeningProviderPolicy,
        scope: ScreeningScope,
    ) -> bool:
        scope_applicable, _reason = self.scope_applicable(scope)
        if not scope_applicable:
            return False
        return provider.provider_id != "institutional_blacklist"


__all__ = [
    "NotApplicableReason",
    "ScreeningProviderPolicy",
    "ScreeningScope",
    "ScreeningTrustPolicy",
    "ScreeningVerdict",
]
