"""
module_id: tests.uat.adversarial.dual_control_two_admins_accepted
file: tests/uat/adversarial/dual_control_two_admins_accepted.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "dual_control_two_admins_accepted"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
