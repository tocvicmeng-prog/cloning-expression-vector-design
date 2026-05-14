"""
module_id: tests.ci_gates.test_t401_catalogue_gates
file: tests/ci_gates/test_t401_catalogue_gates.py
task_id: T-401
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_gate(module_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", f"tools.ci_gates.{module_name}", "--enforce"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_t401_catalogue_gates_pass_in_enforce_mode() -> None:
    failures = []
    for module_name in ("stale_catalogue_check", "source_grade_citation_check"):
        result = _run_gate(module_name)
        if result.returncode != 0:
            failures.append(f"{module_name}: {result.stdout}")

    assert failures == []
