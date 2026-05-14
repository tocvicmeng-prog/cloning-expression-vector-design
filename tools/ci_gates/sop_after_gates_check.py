"""
module_id: tools.ci_gates.sop_after_gates_check
file: tools/ci_gates/sop_after_gates_check.py
task_id: T-204
lifecycle_state: not_implemented
owning_task_id: T-204
"""

from __future__ import annotations

from tools.ci_gates._gate import run_not_implemented


def main() -> int:
    return run_not_implemented("sop-after-gates-check")


if __name__ == "__main__":
    raise SystemExit(main())
