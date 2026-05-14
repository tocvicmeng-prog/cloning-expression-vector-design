"""
module_id: tests.uat.adversarial.developer_post_bootstrap_denied
file: tests/uat/adversarial/developer_post_bootstrap_denied.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "developer_post_bootstrap_denied"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
