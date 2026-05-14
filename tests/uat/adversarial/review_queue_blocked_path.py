"""
module_id: tests.uat.adversarial.review_queue_blocked_path
file: tests/uat/adversarial/review_queue_blocked_path.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "review_queue_blocked_path"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
