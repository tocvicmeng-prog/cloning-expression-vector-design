"""
module_id: tests.uat.adversarial.dual_control_advisory_signoff_pair_required
file: tests/uat/adversarial/dual_control_advisory_signoff_pair_required.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "dual_control_advisory_signoff_pair_required"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
