"""
module_id: tools.ci_gates.no_stale_task_ids_in_active_sections_check
file: tools/ci_gates/no_stale_task_ids_in_active_sections_check.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-204
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

RETIRED_IDS = ("T-309a", "T-309b")


def check(root: Path) -> GateResult:
    agenda = (root / "CODING_AGENDA.md").read_text(encoding="utf-8")
    active_agenda = agenda.split("## 2. Module catalogue", 1)[1].split("## 3.", 1)[0]
    messages = [
        f"active agenda contains retired task id {task_id}"
        for task_id in RETIRED_IDS
        if task_id in active_agenda
    ]
    if messages:
        return fail_gate(*messages)
    return pass_gate("active agenda contains no retired task IDs")


def main() -> int:
    return run_gate("no-stale-task-ids-in-active-sections-check", check)


if __name__ == "__main__":
    raise SystemExit(main())
