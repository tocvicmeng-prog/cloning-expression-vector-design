"""
module_id: tools.ci_gates.task_acceptance_completeness_check
file: tools/ci_gates/task_acceptance_completeness_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-204
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

YAML_BLOCK_RE = re.compile(r"```yaml\n(?P<body>.*?)\n```", re.DOTALL)


def _load_acceptance(path: Path) -> dict[str, object] | None:
    match = YAML_BLOCK_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        return None
    loaded = yaml.safe_load(match.group("body"))
    return loaded if isinstance(loaded, dict) else None


def check(root: Path) -> GateResult:
    messages: list[str] = []
    for brief in sorted((root / "tasks" / "task_brief").glob("T-*.md")):
        acceptance = _load_acceptance(brief)
        if acceptance is None:
            messages.append(f"{brief.relative_to(root)} missing YAML acceptance block")
            continue
        if acceptance.get("task_id") != brief.stem:
            messages.append(f"{brief.relative_to(root)} task_id does not match filename")
        checks = acceptance.get("required_checks")
        if not isinstance(checks, list):
            messages.append(f"{brief.relative_to(root)} required_checks must be a list")
    if messages:
        return fail_gate(*messages)
    count = len(list((root / "tasks" / "task_brief").glob("T-*.md")))
    return pass_gate(f"{count} task briefs have parseable acceptance blocks")


def main() -> int:
    return run_gate("task-acceptance-completeness-check", check)


if __name__ == "__main__":
    raise SystemExit(main())
