"""
module_id: tests.uat.adversarial.reviewer_escalation
file: tests/uat/adversarial/reviewer_escalation.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "reviewer_escalation"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
