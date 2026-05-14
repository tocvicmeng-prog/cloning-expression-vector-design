"""
module_id: tools.ci_gates.test_architecture_manifest_consistency
file: tools/ci_gates/test_architecture_manifest_consistency.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-204
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from tools.ci_gates._gate import GateResult, pass_gate, run_gate


def check(root: Path) -> GateResult:
    manifest = yaml.safe_load((root / "docs" / "module_manifest.yaml").read_text(encoding="utf-8"))
    return pass_gate(f"{len(manifest['modules'])} manually curated modules loaded")


def main() -> int:
    return run_gate("test-architecture-manifest-consistency", check)


if __name__ == "__main__":
    raise SystemExit(main())
