"""
module_id: tests.uat.test_t1301_white_paper_examples
file: tests/uat/test_t1301_white_paper_examples.py
task_id: T-1301
"""

from __future__ import annotations

from pathlib import Path

from tests.uat import example_a_bacterial, example_b_mammalian, example_c_plant
from tests.uat.helpers import (
    WhitePaperExample,
    WhitePaperUatResult,
    assert_common_acceptance,
    run_white_paper_example,
)


def test_example_a_bacterial_uat(tmp_path: Path) -> None:
    _assert_example(example_a_bacterial.example(), tmp_path)


def test_example_b_mammalian_lentiviral_uat(tmp_path: Path) -> None:
    example = example_b_mammalian.example()
    result = _assert_example(example, tmp_path)

    assert example.vlp_report is not None
    assert not example.vlp_report.passed
    assert example.vlp_report.blocked_rule_ids == example.checks.expected_vlp_blocked_rule_ids
    assert example.checks.dual_control_required
    assert "risk.replication_competent_viral_vector" in result.risk_advisory_ids


def test_example_c_plant_three_host_uat(tmp_path: Path) -> None:
    _assert_example(example_c_plant.example(), tmp_path)


def _assert_example(example: WhitePaperExample, tmp_path: Path) -> WhitePaperUatResult:
    result = run_white_paper_example(example, tmp_path)
    assert_common_acceptance(result)
    assert example.checks.required_risk_advisory_ids <= result.risk_advisory_ids
    assert {event.role for event in example.host_contexts} == example.checks.expected_host_roles
    return result
