"""
module_id: tests.uat.adversarial.construct_checksum_mismatch
file: tests/uat/adversarial/construct_checksum_mismatch.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "construct_checksum_mismatch"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
