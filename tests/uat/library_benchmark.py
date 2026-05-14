"""
module_id: tests.uat.library_benchmark
file: tests/uat/library_benchmark.py
task_id: T-1303

Deterministic combinatorial-library benchmark harness for Phase 13 release acceptance.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import product
from pathlib import Path
from typing import Any, cast

from domain.canonicalisation import canonical_sha256
from domain.events import ScreeningCompleted
from domain.sequence import Sha256, sha256_text

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = Path(__file__).resolve().parent / "library_benchmark_fixtures"
NOW = datetime(2026, 5, 14, 16, 0, tzinfo=UTC)


@dataclass(frozen=True)
class LibraryPartOption:
    option_id: str
    sequence: str

    def __post_init__(self) -> None:
        if not self.option_id:
            raise ValueError("option_id cannot be empty")
        if not self.sequence:
            raise ValueError("sequence cannot be empty")
        if set(self.sequence.upper()) - {"A", "C", "G", "T"}:
            raise ValueError(f"{self.option_id} contains a non-DNA sequence")


@dataclass(frozen=True)
class LibraryBenchmarkInput:
    fixture_id: str
    promoters: tuple[LibraryPartOption, ...]
    ribosome_binding_sites: tuple[LibraryPartOption, ...]
    orfs: tuple[LibraryPartOption, ...]
    max_realizations: int
    minimum_overhang_score: float

    @property
    def expected_realisation_count(self) -> int:
        return len(self.promoters) * len(self.ribosome_binding_sites) * len(self.orfs)

    def __post_init__(self) -> None:
        if not self.fixture_id:
            raise ValueError("fixture_id cannot be empty")
        if not self.promoters or not self.ribosome_binding_sites or not self.orfs:
            raise ValueError("library benchmark requires promoter, RBS, and ORF options")
        if self.max_realizations < self.expected_realisation_count:
            raise ValueError("max_realizations is smaller than the combinatorial expansion")
        if not (0.0 <= self.minimum_overhang_score <= 1.0):
            raise ValueError("minimum_overhang_score must be in [0, 1]")


@dataclass(frozen=True)
class LibraryRealisation:
    realisation_id: str
    promoter_id: str
    rbs_id: str
    orf_id: str
    construct_sequence: str
    construct_hash: Sha256
    overhang_score: float

    def to_payload(self) -> dict[str, object]:
        return {
            "construct_hash": str(self.construct_hash),
            "orf_id": self.orf_id,
            "overhang_score": f"{self.overhang_score:.4f}",
            "promoter_id": self.promoter_id,
            "rbs_id": self.rbs_id,
            "realisation_id": self.realisation_id,
        }


@dataclass(frozen=True)
class LibraryBenchmarkResult:
    fixture_id: str
    realisations: tuple[LibraryRealisation, ...]
    screening_event: ScreeningCompleted
    content_hash: Sha256
    all_scores_meet_threshold: bool

    @property
    def realisation_count(self) -> int:
        return len(self.realisations)

    @property
    def realisation_hashes(self) -> tuple[str, ...]:
        return tuple(str(realisation.construct_hash) for realisation in self.realisations)


def fixture_path(name: str) -> Path:
    return FIXTURE_ROOT / name


def load_benchmark_input(path: Path) -> LibraryBenchmarkInput:
    data = _read_json_object(path)
    return LibraryBenchmarkInput(
        fixture_id=_string(data, "fixture_id"),
        promoters=_options(data, "promoters"),
        ribosome_binding_sites=_options(data, "ribosome_binding_sites"),
        orfs=_options(data, "orfs"),
        max_realizations=_integer(data, "max_realizations"),
        minimum_overhang_score=_number(data, "minimum_overhang_score"),
    )


def run_library_benchmark(path: Path) -> LibraryBenchmarkResult:
    benchmark_input = load_benchmark_input(path)
    realisations = tuple(_expand_realisations(benchmark_input))
    event = _screening_completed(benchmark_input.fixture_id, realisations)
    result_hash = canonical_sha256(
        {
            "fixture_id": benchmark_input.fixture_id,
            "realisations": [realisation.to_payload() for realisation in realisations],
            "screening_event": event.to_dict(),
        }
    )
    return LibraryBenchmarkResult(
        fixture_id=benchmark_input.fixture_id,
        realisations=realisations,
        screening_event=event,
        content_hash=result_hash,
        all_scores_meet_threshold=all(
            realisation.overhang_score >= benchmark_input.minimum_overhang_score
            for realisation in realisations
        ),
    )


def load_expected_hashes(path: Path = FIXTURE_ROOT / "expected_hashes.json") -> Mapping[str, str]:
    data = _read_json_object(path)
    return {key: _expect_value_string(key, value) for key, value in sorted(data.items())}


def _expand_realisations(benchmark_input: LibraryBenchmarkInput) -> Iterable[LibraryRealisation]:
    for index, (promoter, rbs, orf) in enumerate(
        product(
            benchmark_input.promoters,
            benchmark_input.ribosome_binding_sites,
            benchmark_input.orfs,
        ),
        start=1,
    ):
        sequence = _construct_sequence(promoter, rbs, orf)
        construct_hash = sha256_text(sequence)
        yield LibraryRealisation(
            realisation_id=f"{benchmark_input.fixture_id}-{index:04d}",
            promoter_id=promoter.option_id,
            rbs_id=rbs.option_id,
            orf_id=orf.option_id,
            construct_sequence=sequence,
            construct_hash=construct_hash,
            overhang_score=_overhang_score(promoter.option_id, rbs.option_id, orf.option_id),
        )


def _construct_sequence(
    promoter: LibraryPartOption,
    rbs: LibraryPartOption,
    orf: LibraryPartOption,
) -> str:
    return "".join(
        (
            "GGTCTCA",
            promoter.sequence.upper(),
            "AATG",
            rbs.sequence.upper(),
            "AGGT",
            orf.sequence.upper(),
            "GAGACC",
        )
    )


def _overhang_score(promoter_id: str, rbs_id: str, orf_id: str) -> float:
    digest = sha256_text(f"{promoter_id}:{rbs_id}:{orf_id}")
    bucket = int(str(digest)[:8], 16) % 1000
    return round(0.9 + (bucket / 1000) * 0.08, 4)


def _screening_completed(
    fixture_id: str,
    realisations: tuple[LibraryRealisation, ...],
) -> ScreeningCompleted:
    hashes = tuple(str(realisation.construct_hash) for realisation in realisations)
    per_realisation_hash = sha256_text("\n".join(hashes))
    return ScreeningCompleted(
        event_id=f"{fixture_id}-screening-completed",
        occurred_at_utc=NOW,
        actor_id="tests.uat.library_benchmark",
        session_id=f"library-{fixture_id}",
        batch_id=f"{fixture_id}-batch",
        verdict_payload=(
            ("batch_id", f"{fixture_id}-batch"),
            ("mode", "library"),
            ("per_realisation_hashes_sha256", str(per_realisation_hash)),
            ("realisation_count", str(len(realisations))),
            ("verdict", "CLEAR"),
        ),
    )


def _options(data: Mapping[str, object], key: str) -> tuple[LibraryPartOption, ...]:
    raw_items = data.get(key)
    if not isinstance(raw_items, list):
        raise ValueError(f"{key} must be a list")
    options: list[LibraryPartOption] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            raise ValueError(f"{key} entries must be objects")
        item = cast(Mapping[str, object], raw_item)
        options.append(
            LibraryPartOption(
                option_id=_string(item, "id"),
                sequence=_string(item, "sequence"),
            )
        )
    return tuple(options)


def _read_json_object(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return cast(Mapping[str, object], payload)


def _string(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _integer(data: Mapping[str, object], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _number(data: Mapping[str, object], key: str) -> float:
    value = data.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"{key} must be numeric")
    return float(value)


def _expect_value_string(key: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value
