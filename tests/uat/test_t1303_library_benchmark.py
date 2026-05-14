"""
module_id: tests.uat.test_t1303_library_benchmark
file: tests/uat/test_t1303_library_benchmark.py
task_id: T-1303
"""

from __future__ import annotations

import pytest

from domain.canonicalisation import canonical_sha256
from domain.events import EventStream
from tests.uat.library_benchmark import (
    fixture_path,
    load_expected_hashes,
    run_library_benchmark,
)


def test_100_realisation_library_benchmark_is_deterministic() -> None:
    first = run_library_benchmark(fixture_path("100_realisation_input.json"))
    second = run_library_benchmark(fixture_path("100_realisation_input.json"))
    expected = load_expected_hashes()

    assert first == second
    assert first.realisation_count == 100
    assert first.all_scores_meet_threshold
    assert first.screening_event.stream is EventStream.DESIGN
    assert dict(first.screening_event.verdict_payload)["realisation_count"] == "100"
    assert expected["library-100:result_hash"] == str(first.content_hash)
    assert expected["library-100:first_realisation_hash"] == first.realisation_hashes[0]
    assert expected["library-100:last_realisation_hash"] == first.realisation_hashes[-1]
    assert expected["library-100:screening_payload_hash"] == str(
        canonical_sha256(first.screening_event.verdict_payload)
    )


@pytest.mark.slow
def test_1000_realisation_library_benchmark_stretch_fixture_is_deterministic() -> None:
    result = run_library_benchmark(fixture_path("1000_realisation_input.json"))
    expected = load_expected_hashes()

    assert result.realisation_count == 1000
    assert result.all_scores_meet_threshold
    assert dict(result.screening_event.verdict_payload)["realisation_count"] == "1000"
    assert expected["library-1000:result_hash"] == str(result.content_hash)
    assert expected["library-1000:first_realisation_hash"] == result.realisation_hashes[0]
    assert expected["library-1000:last_realisation_hash"] == result.realisation_hashes[-1]
    assert expected["library-1000:screening_payload_hash"] == str(
        canonical_sha256(result.screening_event.verdict_payload)
    )
