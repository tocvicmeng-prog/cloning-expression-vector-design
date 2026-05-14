"""
module_id: tests.benchmark.T_502_validation_bench
file: tests/benchmark/T_502_validation_bench.py
task_id: T-502
"""

from __future__ import annotations

import json
import platform
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from domain.types.citation import GradedCitation
from domain.types.enums import ContextScope, Severity, SeverityPolicy
from domain.types.ids import MetricId, ReviewerId, RuleId
from domain.types.validation_rule import ValidationRule
from engine.validation import ValidationContext, WorkerPoolFactory, validate
from engine.validation.predicates._stub import Predicate
from engine.validation.worker_pool_factory import WorkerPoolMode

RESULTS_DIR = Path("tests/benchmark/results")


def bench_info_predicate(context: ValidationContext, rule: ValidationRule) -> Severity:
    del context, rule
    return Severity.INFO


@pytest.mark.slow
def test_t502_validation_benchmark_writes_result_record() -> None:
    rules = tuple(_rule(index) for index in range(150))
    registry: dict[str, Predicate] = {"bench_info_predicate": bench_info_predicate}
    context = ValidationContext(
        design_payload={"construct": {"sequence": "A" * 10_000}},
        random_seed=502,
    )
    modes: tuple[WorkerPoolMode, ...] = (
        ("sequential", "thread", "process")
        if platform.system() != "Windows"
        else ("sequential", "thread")
    )
    baseline_json = ""
    timings: dict[str, float] = {}

    for mode in modes:
        started = time.perf_counter()
        report = validate(
            context,
            rules,
            predicate_registry=registry,
            worker_pool_factory=WorkerPoolFactory(mode, max_workers=4),
        )
        timings[mode] = round((time.perf_counter() - started) * 1000, 3)
        assert not report.errors
        report_json = report.canonical_json()
        if not baseline_json:
            baseline_json = report_json
        assert report_json == baseline_json

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_DIR / f"T_502_validation_bench_{_git_sha()}.json"
    result_path.write_text(
        json.dumps(
            {
                "mode_timings_ms": timings,
                "platform": platform.platform(),
                "recorded_at_utc": datetime.now(UTC).isoformat(),
                "reports_identical": True,
                "rule_count": len(rules),
                "task_id": "T-502",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _git_sha() -> str:
    result = subprocess.run(
        ("git", "rev-parse", "--short", "HEAD"),
        check=False,
        capture_output=True,
        text=True,
    )
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else "local"


def _rule(index: int) -> ValidationRule:
    return ValidationRule(
        rule_id=RuleId(f"BENCH-{index:03d}"),
        predicate_name="bench_info_predicate",
        severity=Severity.INFO,
        severity_policy=SeverityPolicy.REPORT_ONLY,
        blocks=frozenset(),
        reads=frozenset({f"construct.feature_{index}"}),
        depends_on_metrics=frozenset({MetricId(f"metric.bench.{index - 1:03d}")} if index else ()),
        produces_metrics=frozenset({MetricId(f"metric.bench.{index:03d}")}),
        invalidates=frozenset(),
        preconditions=(),
        target_context=ContextScope.CONSTRUCT,
        external_adapters=(),
        threshold_profile="thresholds.benchmark",
        citation=GradedCitation(
            text="T-502 benchmark citation",
            grade="B2",
            accessed=datetime(2026, 5, 14, tzinfo=UTC).date(),
            url="CODING_AGENDA.md",
        ),
        last_reviewed=datetime(2026, 5, 14, tzinfo=UTC).date(),
        reviewed_by=ReviewerId("benchmark"),
        test_fixtures=("benchmark-triggering.json", "benchmark-passing.json"),
        suggested_remediation="benchmark fixture only",
    )
