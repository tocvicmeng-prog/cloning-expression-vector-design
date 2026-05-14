"""
module_id: tools.ci_gates.test_task_brief_coverage
file: tools/ci_gates/test_task_brief_coverage.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-204
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate


def check(root: Path) -> GateResult:
    manifest = yaml.safe_load((root / "docs" / "task_manifest.yaml").read_text(encoding="utf-8"))
    expected = {entry["task_id"] for entry in manifest["tasks"]}
    actual = {path.stem for path in (root / "tasks" / "task_brief").glob("T-*.md")}
    missing = sorted(expected - actual)
    if missing:
        return fail_gate(*(f"missing task brief: {task_id}" for task_id in missing))
    return pass_gate(f"{len(actual)} task briefs cover the active manifest")


def main() -> int:
    return run_gate("test-task-brief-coverage", check)


if __name__ == "__main__":
    raise SystemExit(main())
