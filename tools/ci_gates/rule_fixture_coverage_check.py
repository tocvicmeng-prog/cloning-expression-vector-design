"""
module_id: tools.ci_gates.rule_fixture_coverage_check
file: tools/ci_gates/rule_fixture_coverage_check.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-405
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

_RULE_FILES = ("MR.yaml", "WR.yaml", "SR.yaml", "BR.yaml", "MS.yaml")


def check_rule_fixtures(root: Path) -> GateResult:
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
            fixtures = rule.get("test_fixtures")
            if not isinstance(fixtures, dict):
                failures.append(f"{filename} {rule_id}: missing test_fixtures mapping")
                continue
            for key in ("triggering", "passing"):
                fixture_path = fixtures.get(key)
                if not isinstance(fixture_path, str) or not fixture_path:
                    failures.append(f"{filename} {rule_id}: missing {key} fixture path")
                    continue
                if not (root / fixture_path).is_file():
                    failures.append(f"{filename} {rule_id}: fixture not found: {fixture_path}")
    if failures:
        return fail_gate(*failures)
    return pass_gate("all rule fixtures are declared and present")


def main() -> int:
    return run_gate("rule-fixture-coverage-check", check_rule_fixtures)


if __name__ == "__main__":
    raise SystemExit(main())
