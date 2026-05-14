"""
module_id: tools.ci_gates.module_coverage_check
file: tools/ci_gates/module_coverage_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-204
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate


def check(root: Path) -> GateResult:
    manifest = yaml.safe_load((root / "docs" / "module_manifest.yaml").read_text(encoding="utf-8"))
    missing = [entry["module_id"] for entry in manifest["modules"] if not entry.get("tasks")]
    if missing:
        return fail_gate(*(f"module has no owning task: {module_id}" for module_id in missing))
    return pass_gate(f"{len(manifest['modules'])} modules have task ownership")


def main() -> int:
    return run_gate("module-coverage-check", check)


if __name__ == "__main__":
    raise SystemExit(main())
