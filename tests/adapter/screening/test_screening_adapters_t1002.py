"""
module_id: tests.adapter.screening.test_screening_adapters_t1002
file: tests/adapter/screening/test_screening_adapters_t1002.py
task_id: T-1002
"""

from __future__ import annotations

from pathlib import Path

from adapter.screening import (
    IgscAdapter,
    InternalBlacklistAdapter,
    ScreeningAdapterFailureClass,
    ScreeningError,
    ScreeningRequest,
    ScreeningResult,
    ScreeningScope,
    ScreeningTrustPolicy,
    ScreeningVerdict,
    load_screening_trust_policy,
)
from domain.sequence import DnaSequence

ROOT = Path(__file__).resolve().parents[3]


def test_policy_derived_canonical_trust_and_igsc_verdicts() -> None:
    policy = _policy()
    adapter = IgscAdapter(policy)

    clear = adapter.screen(_request("clear", DnaSequence("G" * 210)))
    watchlist = adapter.screen(
        _request("watch", DnaSequence("G" * 50 + "TTTTCCCCAAAAGGGG" + "A" * 150))
    )
    hit = adapter.screen(_request("hit", DnaSequence("G" * 50 + "ACGTACGTACGTACGT" + "A" * 150)))

    assert isinstance(clear, ScreeningResult)
    assert clear.verdict is ScreeningVerdict.CLEAR
    assert clear.canonical_at_this_scope is True
    assert clear.policy_content_hash == policy.policy_content_hash

    assert isinstance(watchlist, ScreeningResult)
    assert watchlist.verdict is ScreeningVerdict.WATCHLIST

    assert isinstance(hit, ScreeningResult)
    assert hit.verdict is ScreeningVerdict.HIT


def test_not_applicable_reason_is_policy_derived_for_short_sequences() -> None:
    result = IgscAdapter(_policy()).screen(_request("short", DnaSequence("G" * 100)))

    assert isinstance(result, ScreeningResult)
    assert result.verdict is ScreeningVerdict.NOT_APPLICABLE
    assert result.not_applicable_reason is not None
    assert result.not_applicable_reason.value == "below_minimum_length"


def test_internal_blacklist_is_noncanonical_and_never_returns_clear() -> None:
    result = InternalBlacklistAdapter(_policy()).screen(
        _request("fallback", DnaSequence("G" * 210))
    )

    assert isinstance(result, ScreeningResult)
    assert result.verdict is ScreeningVerdict.MANUAL_REVIEW_REQUIRED
    assert result.canonical_at_this_scope is False


def test_batch_preserves_order_and_partial_provider_failures() -> None:
    adapter = IgscAdapter(_policy(), provider_available=False)
    requests = (
        _request("first", DnaSequence("G" * 210)),
        _request("second", DnaSequence("C" * 210)),
    )

    outcomes = adapter.screen_batch(requests)

    assert len(outcomes) == len(requests)
    assert [outcome.request_id for outcome in outcomes] == ["first", "second"]
    assert all(isinstance(outcome, ScreeningError) for outcome in outcomes)
    first = outcomes[0]
    assert isinstance(first, ScreeningError)
    assert first.failure_class is ScreeningAdapterFailureClass.PROVIDER_UNAVAILABLE


def test_fragment_screening_is_allowed_only_by_policy_scope() -> None:
    result = IgscAdapter(_policy()).screen(
        _request("fragment", DnaSequence("G" * 210), scope=ScreeningScope.ORDER_FRAGMENT)
    )

    assert isinstance(result, ScreeningResult)
    assert result.verdict is ScreeningVerdict.CLEAR
    assert result.scope is ScreeningScope.ORDER_FRAGMENT
    assert result.canonical_at_this_scope is True


def _policy() -> ScreeningTrustPolicy:
    return load_screening_trust_policy(ROOT / "catalogues", schema_root=ROOT / "schemas")


def _request(
    request_id: str,
    sequence: DnaSequence,
    *,
    scope: ScreeningScope = ScreeningScope.ASSEMBLED_PRODUCT,
) -> ScreeningRequest:
    return ScreeningRequest(
        request_id=request_id,
        sequence=sequence,
        session_id="session-1",
        construct_id="construct-1",
        construct_checksum="checksum-1",
        scope=scope,
    )
