"""
module_id: adapter.screening.base
file: src/adapter/screening/base.py
task_id: T-1002

Shared static screening-adapter primitives.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TypeAlias, cast

from adapter.catalogue import load_catalogue, schema_for_catalogue
from domain.canonicalisation import canonical_sha256
from domain.sequence import DnaSequence, Sha256, sha256_text
# v0.2.1 audit fix M5 — value types moved to domain.types.screening to fix the
# hexagonal-layering inversion the Architect audit § 1.2 Finding 1.3 surfaced
# (App layer was structurally bound to adapter.* via these imports).
# Re-exported here for backward compatibility with existing direct callers.
from domain.types.screening import (
    NotApplicableReason,
    ScreeningProviderPolicy,
    ScreeningScope,
    ScreeningTrustPolicy,
    ScreeningVerdict,
)

EvidencePayload: TypeAlias = tuple[tuple[str, str], ...]
BatchScreeningOutcome: TypeAlias = tuple["ScreeningResult | ScreeningError", ...]


class ScreeningAdapterFailureClass(Enum):
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    INVALID_REQUEST = "invalid_request"
    UNSUPPORTED_SCOPE = "unsupported_scope"
    POLICY_REJECTED_VERDICT = "policy_rejected_verdict"
    ADAPTER_FAILURE = "adapter_failure"


@dataclass(frozen=True)
class ScreeningRequest:
    request_id: str
    sequence: DnaSequence
    session_id: str
    construct_id: str
    construct_checksum: str
    scope: ScreeningScope = ScreeningScope.ASSEMBLED_PRODUCT
    realisation_id: str | None = None
    metadata: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id cannot be empty")
        if not self.session_id:
            raise ValueError("session_id cannot be empty")
        if not self.construct_id:
            raise ValueError("construct_id cannot be empty")
        if not self.construct_checksum:
            raise ValueError("construct_checksum cannot be empty")
        metadata = self.metadata or {}
        object.__setattr__(self, "metadata", metadata)
        for key, value in metadata.items():
            if not key or not value:
                raise ValueError("screening metadata keys and values cannot be empty")

    @property
    def sequence_hash(self) -> Sha256:
        return sha256_text(self.sequence.body)


# ScreeningProviderPolicy + ScreeningTrustPolicy moved to domain.types.screening
# (v0.2.1 audit fix M5). Re-exported via the `from domain.types.screening import ...`
# block at the top of this file for backward compatibility.


@dataclass(frozen=True)
class ScreeningResult:
    provider_id: str
    request_id: str
    session_id: str
    construct_id: str
    construct_checksum: str
    sequence_hash: Sha256
    verdict: ScreeningVerdict
    provider_version: str
    policy_id: str
    policy_version: str
    policy_content_hash: Sha256
    canonical_at_this_scope: bool
    scope: ScreeningScope
    not_applicable_reason: NotApplicableReason | None = None
    evidence: EvidencePayload = ()
    realisation_id: str | None = None

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.provider_id, "provider_id"),
            (self.request_id, "request_id"),
            (self.session_id, "session_id"),
            (self.construct_id, "construct_id"),
            (self.construct_checksum, "construct_checksum"),
            (self.provider_version, "provider_version"),
            (self.policy_id, "policy_id"),
            (self.policy_version, "policy_version"),
        ):
            if not value:
                raise ValueError(f"{field_name} cannot be empty")
        if self.verdict is ScreeningVerdict.NOT_APPLICABLE and self.not_applicable_reason is None:
            raise ValueError("NOT_APPLICABLE results require a reason")
        if self.verdict is not ScreeningVerdict.NOT_APPLICABLE and self.not_applicable_reason:
            raise ValueError("not_applicable_reason requires NOT_APPLICABLE verdict")

    def to_payload(self) -> dict[str, object]:
        return {
            "canonical_at_this_scope": self.canonical_at_this_scope,
            "construct_checksum": self.construct_checksum,
            "construct_id": self.construct_id,
            "evidence": dict(self.evidence),
            "not_applicable_reason": None
            if self.not_applicable_reason is None
            else self.not_applicable_reason.value,
            "policy_content_hash": str(self.policy_content_hash),
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "realisation_id": self.realisation_id,
            "request_id": self.request_id,
            "scope": self.scope.value,
            "sequence_hash": str(self.sequence_hash),
            "session_id": self.session_id,
            "verdict": self.verdict.value,
        }


@dataclass(frozen=True)
class ScreeningError:
    provider_id: str
    request_id: str
    session_id: str
    failure_class: ScreeningAdapterFailureClass
    message: str
    retryable: bool

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id cannot be empty")
        if not self.request_id:
            raise ValueError("request_id cannot be empty")
        if not self.session_id:
            raise ValueError("session_id cannot be empty")
        if not self.message:
            raise ValueError("screening error message cannot be empty")

    @property
    def verdict(self) -> ScreeningVerdict:
        return ScreeningVerdict.UNAVAILABLE

    def to_payload(self) -> dict[str, object]:
        return {
            "failure_class": self.failure_class.value,
            "message": self.message,
            "provider_id": self.provider_id,
            "request_id": self.request_id,
            "retryable": self.retryable,
            "session_id": self.session_id,
            "verdict": self.verdict.value,
        }


class BaseScreeningAdapter:
    provider_id: str
    provider_version: str = "static-2026.05"
    _hit_motifs: tuple[str, ...] = ()
    _watchlist_motifs: tuple[str, ...] = ()
    _manual_review_motifs: tuple[str, ...] = ()
    _fallback_never_clear: bool = False

    def __init__(
        self,
        policy: ScreeningTrustPolicy,
        *,
        hit_motifs: Iterable[str] = (),
        watchlist_motifs: Iterable[str] = (),
        manual_review_motifs: Iterable[str] = (),
        provider_available: bool = True,
    ) -> None:
        self.policy = policy
        self.provider_available = provider_available
        self._hit_motifs = tuple(_normalise_motif(item) for item in hit_motifs) or self._hit_motifs
        self._watchlist_motifs = (
            tuple(_normalise_motif(item) for item in watchlist_motifs) or self._watchlist_motifs
        )
        self._manual_review_motifs = (
            tuple(_normalise_motif(item) for item in manual_review_motifs)
            or self._manual_review_motifs
        )

    def screen(self, request: ScreeningRequest) -> ScreeningResult | ScreeningError:
        if not self.provider_available:
            return ScreeningError(
                provider_id=self.provider_id,
                request_id=request.request_id,
                session_id=request.session_id,
                failure_class=ScreeningAdapterFailureClass.PROVIDER_UNAVAILABLE,
                message="screening provider is unavailable",
                retryable=True,
            )

        try:
            provider_policy = self.policy.provider_policy(self.provider_id, request.scope)
        except ValueError as exc:
            return ScreeningError(
                provider_id=self.provider_id,
                request_id=request.request_id,
                session_id=request.session_id,
                failure_class=ScreeningAdapterFailureClass.INVALID_REQUEST,
                message=str(exc),
                retryable=False,
            )

        applicable, reason = self.policy.scope_applicable(request.scope)
        if not applicable:
            return self._result(
                request,
                provider_policy,
                ScreeningVerdict.NOT_APPLICABLE,
                not_applicable_reason=reason or NotApplicableReason.UNSUPPORTED_SCOPE,
                evidence=(("policy_scope", "excluded"),),
            )
        if len(request.sequence) < self.policy.minimum_synthetic_na_nt:
            return self._result(
                request,
                provider_policy,
                ScreeningVerdict.NOT_APPLICABLE,
                not_applicable_reason=NotApplicableReason.BELOW_MINIMUM_LENGTH,
                evidence=(("minimum_synthetic_na_nt", str(self.policy.minimum_synthetic_na_nt)),),
            )

        verdict, evidence = self._classify(request.sequence.body)
        if verdict not in provider_policy.accepted_verdicts:
            return ScreeningError(
                provider_id=self.provider_id,
                request_id=request.request_id,
                session_id=request.session_id,
                failure_class=ScreeningAdapterFailureClass.POLICY_REJECTED_VERDICT,
                message=f"{self.provider_id} is not trusted for {verdict.value}",
                retryable=False,
            )
        return self._result(request, provider_policy, verdict, evidence=evidence)

    def screen_batch(self, requests: Iterable[ScreeningRequest]) -> BatchScreeningOutcome:
        return tuple(self.screen(request) for request in requests)

    def _classify(self, sequence: str) -> tuple[ScreeningVerdict, EvidencePayload]:
        hit = _first_motif(sequence, self._hit_motifs)
        if hit is not None:
            return ScreeningVerdict.HIT, (("matched_motif_class", "hit"), ("motif", hit))
        watchlist = _first_motif(sequence, self._watchlist_motifs)
        if watchlist is not None:
            return (
                ScreeningVerdict.WATCHLIST,
                (("matched_motif_class", "watchlist"), ("motif", watchlist)),
            )
        manual = _first_motif(sequence, self._manual_review_motifs)
        if manual is not None:
            return (
                ScreeningVerdict.MANUAL_REVIEW_REQUIRED,
                (("matched_motif_class", "manual_review"), ("motif", manual)),
            )
        if self._fallback_never_clear:
            return (
                ScreeningVerdict.MANUAL_REVIEW_REQUIRED,
                (("fallback_policy", "manual_review_until_canonical_screening"),),
            )
        return ScreeningVerdict.CLEAR, (("matched_motif_class", "none"),)

    def _result(
        self,
        request: ScreeningRequest,
        provider_policy: ScreeningProviderPolicy,
        verdict: ScreeningVerdict,
        *,
        not_applicable_reason: NotApplicableReason | None = None,
        evidence: EvidencePayload = (),
    ) -> ScreeningResult:
        return ScreeningResult(
            provider_id=self.provider_id,
            request_id=request.request_id,
            session_id=request.session_id,
            construct_id=request.construct_id,
            construct_checksum=request.construct_checksum,
            sequence_hash=request.sequence_hash,
            verdict=verdict,
            provider_version=self.provider_version,
            policy_id=self.policy.policy_id,
            policy_version=self.policy.policy_version,
            policy_content_hash=self.policy.policy_content_hash,
            canonical_at_this_scope=provider_policy.canonical_at_this_scope,
            scope=request.scope,
            not_applicable_reason=not_applicable_reason,
            evidence=tuple(sorted(evidence)),
            realisation_id=request.realisation_id,
        )


def load_screening_trust_policy(
    catalogue_root: str | Path,
    *,
    schema_root: str | Path,
) -> ScreeningTrustPolicy:
    path = Path(catalogue_root) / "screening_trust_policy.yaml"
    document = load_catalogue(path, schema_for_catalogue(path, schema_root))
    payload = document.payload
    scope = _expect_mapping(payload["screening_scope"], "screening_scope")
    verdict_policy = _expect_mapping(payload["verdict_policy"], "verdict_policy")
    providers = tuple(
        _provider_policy(item) for item in _expect_list(payload["providers"], "providers")
    )
    return ScreeningTrustPolicy(
        policy_id=_expect_str(payload, "policy_id"),
        policy_version=_expect_str(payload, "policy_version"),
        minimum_synthetic_na_nt=_expect_int(scope, "minimum_synthetic_na_nt"),
        screen_assembled_product=_expect_bool(scope, "screen_assembled_product"),
        screen_order_fragments=_expect_bool(scope, "screen_order_fragments"),
        screen_translated_orfs_when_applicable=bool(
            scope.get("screen_translated_orfs_when_applicable", False)
        ),
        preserve_query_privacy_when_supported=bool(
            scope.get("preserve_query_privacy_when_supported", False)
        ),
        verdict_blocks=_verdict_blocks(verdict_policy),
        providers={provider.provider_id: provider for provider in providers},
        policy_content_hash=canonical_sha256(payload),
    )


def _provider_policy(raw: object) -> ScreeningProviderPolicy:
    data = _expect_mapping(raw, "provider")
    return ScreeningProviderPolicy(
        provider_id=_expect_str(data, "id"),
        name=_expect_str(data, "name"),
        trust_level=_expect_str(data, "trust_level"),
        query_privacy_mode=str(data.get("query_privacy_mode", "provider_controlled")),
        accepted_verdicts=frozenset(
            ScreeningVerdict(_expect_str_value(item).upper())
            for item in _expect_list(data.get("accepted_verdicts", []), "accepted_verdicts")
        ),
        canonical_at_this_scope=False,
    )


def _verdict_blocks(
    verdict_policy: Mapping[str, object],
) -> Mapping[ScreeningVerdict, frozenset[str]]:
    parsed: dict[ScreeningVerdict, frozenset[str]] = {}
    for key, raw in verdict_policy.items():
        try:
            verdict = ScreeningVerdict(key.upper())
        except ValueError:
            continue
        data = _expect_mapping(raw, f"verdict_policy.{key}")
        parsed[verdict] = frozenset(
            _expect_str_value(item) for item in _expect_list(data.get("blocks", []), "blocks")
        )
    return parsed


def _normalise_motif(motif: str) -> str:
    return DnaSequence(motif).body


def _first_motif(sequence: str, motifs: tuple[str, ...]) -> str | None:
    for motif in motifs:
        if motif in sequence:
            return motif
    return None


def _expect_mapping(raw: object, name: str) -> Mapping[str, object]:
    if not isinstance(raw, dict):
        raise ValueError(f"{name} must be a mapping")
    return cast(Mapping[str, object], raw)


def _expect_list(raw: object, name: str) -> list[object]:
    if not isinstance(raw, list):
        raise ValueError(f"{name} must be a list")
    return raw


def _expect_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _expect_str_value(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("expected non-empty string")
    return value


def _expect_int(data: Mapping[str, object], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    return value


def _expect_bool(data: Mapping[str, object], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value
