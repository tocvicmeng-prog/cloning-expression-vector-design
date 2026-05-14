"""
module_id: tools.ci_gates.test_task_manifest_phase_order
file: tools/ci_gates/test_task_manifest_phase_order.py
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
    order = [entry["task_id"] for entry in manifest["tasks"]]
    messages: list[str] = []
    for before, after in (("T-1001", "T-803"), ("T-1002", "T-803")):
        if order.index(before) > order.index(after):
            messages.append(f"{before} must precede {after}")
    if messages:
        return fail_gate(*messages)
    return pass_gate("phase order is consistent")


def main() -> int:
    return run_gate("test-task-manifest-phase-order", check)


if __name__ == "__main__":
    raise SystemExit(main())
