"""
module_id: tests.uat.adversarial.audit_key_absent
file: tests/uat/adversarial/audit_key_absent.py
task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tests.uat.adversarial.helpers import AdversarialScenarioResult, run_scenario

SCENARIO = "audit_key_absent"


def run(tmp_path: Path) -> AdversarialScenarioResult:
    return run_scenario(SCENARIO, tmp_path)
