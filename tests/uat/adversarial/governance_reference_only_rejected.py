"""
module_id: tests.uat.adversarial.governance_reference_only_rejected
file: tests/uat/adversarial/governance_reference_only_rejected.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "governance_reference_only_rejected"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
