"""
module_id: tools.ci_gates.test_task_count_consistency
file: tools/ci_gates/test_task_count_consistency.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-204
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate


def check(root: Path) -> GateResult:
    manifest = yaml.safe_load((root / "docs" / "task_manifest.yaml").read_text(encoding="utf-8"))
    expected = int(manifest["active_task_card_count"])
    actual = len(manifest["tasks"])
    if expected != actual:
        return fail_gate(f"active_task_card_count={expected}, tasks={actual}")
    return pass_gate(f"{actual} active tasks")


def main() -> int:
    return run_gate("test-task-count-consistency", check)


if __name__ == "__main__":
    raise SystemExit(main())
