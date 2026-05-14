"""
module_id: tools.ci_gates.no_direct_admin_handler_import_check
file: tools/ci_gates/no_direct_admin_handler_import_check.py
task_id: T-204
lifecycle_state: not_implemented
owning_task_id: T-204
"""

from __future__ import annotations

from tools.ci_gates._gate import run_not_implemented


def main() -> int:
    return run_not_implemented("no-direct-admin-handler-import-check")


if __name__ == "__main__":
    raise SystemExit(main())
