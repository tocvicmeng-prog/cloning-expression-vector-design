"""
module_id: tools.ci.determinism_check
file: tools/ci/determinism_check.py
task_id: T-1303

Release determinism check for white-paper UAT and the 100-realisation library benchmark.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.uat import example_a_bacterial, example_b_mammalian, example_c_plant
from tests.uat.helpers import WhitePaperExample, assert_common_acceptance, run_white_paper_example
from tests.uat.library_benchmark import load_expected_hashes, run_library_benchmark

ROOT = Path(__file__).resolve().parents[2]


def run_check(root: Path = ROOT) -> tuple[str, ...]:
    messages: list[str] = []
    example_factories: tuple[Callable[[], WhitePaperExample], ...] = (
        example_a_bacterial.example,
        example_b_mammalian.example,
        example_c_plant.example,
    )
    with TemporaryDirectory(prefix="cev-determinism-") as tmp:
        tmp_root = Path(tmp)
        for factory in example_factories:
            example = factory()
            first = run_white_paper_example(example, tmp_root / example.key / "first")
            second = run_white_paper_example(example, tmp_root / example.key / "second")
            assert_common_acceptance(first)
            assert_common_acceptance(second)
            if first.bundle_hash != second.bundle_hash:
                raise AssertionError(f"{example.key} bundle hash is not deterministic")
            messages.append(f"{example.key}: {first.bundle_hash}")

    expected = load_expected_hashes(
        root / "tests/uat/library_benchmark_fixtures/expected_hashes.json"
    )
    library = run_library_benchmark(
        root / "tests/uat/library_benchmark_fixtures/100_realisation_input.json"
    )
    if str(library.content_hash) != expected["library-100:result_hash"]:
        raise AssertionError("100-realisation library benchmark hash drifted")
    messages.append(f"library-100: {library.content_hash}")
    return tuple(messages)


def main() -> int:
    for message in run_check():
        print(f"determinism-check: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
