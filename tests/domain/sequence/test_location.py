"""
module_id: tests.domain.sequence
file: tests/domain/sequence/test_location.py
task_id: T-301
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from domain.sequence import CompoundLocationKind, LocationFuzziness, LocationV14


@settings(max_examples=1000)
@given(
    parent_length=st.integers(min_value=1, max_value=10_000),
    start=st.integers(min_value=0, max_value=9_999),
    width=st.integers(min_value=0, max_value=200),
)
def test_linear_location_length_invariant(parent_length: int, start: int, width: int) -> None:
    start %= parent_length
    end = min(parent_length, start + width)
    location = LocationV14(start=start, end=end, strand="+", phase=".")

    assert location.sequence_length_invariant_satisfied(parent_length)
    assert location.span_length(parent_length) == end - start


@settings(max_examples=1000)
@given(
    parent_length=st.integers(min_value=2, max_value=10_000),
    start=st.integers(min_value=1, max_value=9_999),
    end=st.integers(min_value=0, max_value=9_998),
)
def test_circular_wrap_location_length_invariant(parent_length: int, start: int, end: int) -> None:
    start = 1 + (start % (parent_length - 1))
    end %= start
    location = LocationV14(start=start, end=end, strand="-", phase=0, circular_wrap=True)

    assert location.sequence_length_invariant_satisfied(parent_length)
    assert location.span_length(parent_length) == parent_length - start + end


def test_between_base_location_has_zero_span() -> None:
    location = LocationV14(
        start=42,
        end=43,
        strand=".",
        phase=".",
        start_fuzziness=LocationFuzziness.BETWEEN,
        end_fuzziness=LocationFuzziness.BETWEEN,
        between_base=True,
    )

    assert location.sequence_length_invariant_satisfied(100)
    assert location.span_length(100) == 0


def test_between_base_location_requires_between_fuzziness() -> None:
    with pytest.raises(ValueError, match="between-base"):
        LocationV14(start=42, end=43, strand=".", phase=".", between_base=True)


def test_compound_location_requires_kind() -> None:
    child = LocationV14(start=0, end=10, strand="+", phase=".")
    with pytest.raises(ValueError, match="sub_kind"):
        LocationV14(start=0, end=10, strand="+", phase=".", sub_locations=(child,))


def test_location_rejects_negative_coordinates_and_empty_compound() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        LocationV14(start=-1, end=10, strand="+", phase=".")
    with pytest.raises(ValueError, match="sub_locations"):
        LocationV14(start=0, end=10, strand="+", phase=".", sub_kind=CompoundLocationKind.ORDER)


def test_compound_location_sums_child_lengths() -> None:
    first = LocationV14(start=0, end=10, strand="+", phase=".")
    second = LocationV14(start=20, end=25, strand="+", phase=".")
    parent = LocationV14(
        start=0,
        end=25,
        strand="+",
        phase=".",
        sub_locations=(first, second),
        sub_kind=CompoundLocationKind.JOIN,
    )

    assert parent.sequence_length_invariant_satisfied(100)
    assert parent.span_length(100) == 15


def test_invalid_parent_length_and_out_of_bounds_fail_invariant() -> None:
    zero_parent = LocationV14(start=0, end=1, strand="+", phase=".")
    out_of_bounds = LocationV14(start=0, end=11, strand="+", phase=".")
    invalid_wrap = LocationV14(
        start=2,
        end=5,
        strand="+",
        phase=".",
        circular_wrap=True,
    )

    assert not zero_parent.sequence_length_invariant_satisfied(0)
    assert not out_of_bounds.sequence_length_invariant_satisfied(10)
    assert not invalid_wrap.sequence_length_invariant_satisfied(10)
