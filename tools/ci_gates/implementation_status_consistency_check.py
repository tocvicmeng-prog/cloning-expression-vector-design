"""
module_id: tools.ci_gates.implementation_status_consistency_check
file: tools/ci_gates/implementation_status_consistency_check.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-405
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from domain.types.enums import Severity
from engine.validation.predicates import PREDICATE_REGISTRY
from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

_RULE_FILES = ("MR.yaml", "WR.yaml", "SR.yaml", "BR.yaml", "MS.yaml")


def check_implementation_status(root: Path) -> GateResult:
    failures: list[str] = []
    for filename in _RULE_FILES:
        path = root / "catalogues" / "rules" / filename
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            failures.append(f"{path.relative_to(root)}: root must be a mapping")
            continue
        rules = loaded.get("rules")
        if not isinstance(rules, list):
            failures.append(f"{path.relative_to(root)}: rules must be a list")
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                failures.append(f"{path.relative_to(root)}: rule entry must be a mapping")
                continue
            rule_id = str(rule.get("rule_id", "<missing>"))
            predicate_name = rule.get("predicate_name")
            status = rule.get("implementation_status")
            if not isinstance(predicate_name, str) or not predicate_name:
                failures.append(f"{filename} {rule_id}: missing predicate_name")
                continue
            predicate = PREDICATE_REGISTRY.get(predicate_name)
            if predicate is None:
                failures.append(f"{filename} {rule_id}: predicate not registered: {predicate_name}")
                continue
            if status == "stub":
                result = predicate({})
                if result is not Severity.INFO:
                    failures.append(
                        f"{filename} {rule_id}: stub predicate must return Severity.INFO"
                    )
            elif status == "real":
                failures.append(
                    f"{filename} {rule_id}: real predicates are not enabled until Phase 5/6"
                )
            else:
                failures.append(f"{filename} {rule_id}: invalid implementation_status {status!r}")
    if failures:
        return fail_gate(*failures)
    return pass_gate("all rule implementation statuses match registered predicates")


def main() -> int:
    return run_gate("implementation-status-consistency-check", check_implementation_status)


if __name__ == "__main__":
    raise SystemExit(main())
