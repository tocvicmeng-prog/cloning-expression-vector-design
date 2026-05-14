"""
module_id: tests.uat.adversarial.advisory_bypass
file: tests/uat/adversarial/advisory_bypass.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "advisory_bypass"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
