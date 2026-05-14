"""
module_id: tests.ci_gates.test_llm_output_policy_t1201
file: tests/ci_gates/test_llm_output_policy_t1201.py
task_id: T-1201
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates.llm_output_policy_check import check_llm_output_policy


def test_llm_output_policy_check_passes_on_repo() -> None:
    root = Path(__file__).resolve().parents[2]

    result = check_llm_output_policy(root)

    assert result.passed
