"""
module_id: tools.ci_gates.gate_lifecycle_check
file: tools/ci_gates/gate_lifecycle_check.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-204
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

VALID_STATES = {"not_implemented", "informational", "enforced", "enforced-green"}
SKIP = {"__init__.py", "_gate.py"}


def _header_value(text: str, key: str) -> str | None:
    marker = f"{key}:"
    for line in text.splitlines()[:20]:
        if line.startswith(marker):
            return line.split(":", 1)[1].strip()
    return None


def check(root: Path) -> GateResult:
    messages: list[str] = []
    for path in sorted((root / "tools" / "ci_gates").glob("*.py")):
        if path.name in SKIP:
            continue
        text = path.read_text(encoding="utf-8")
        state = _header_value(text, "lifecycle_state")
        owner = _header_value(text, "owning_task_id")
        if state not in VALID_STATES:
            messages.append(f"{path.relative_to(root)} has invalid lifecycle_state {state!r}")
        if not owner:
            messages.append(f"{path.relative_to(root)} missing owning_task_id")
        if state in {"enforced", "enforced-green"} and "predicate not implemented yet" in text:
            messages.append(f"{path.relative_to(root)} is enforced but still a stub")
    if messages:
        return fail_gate(*messages)
    return pass_gate("gate lifecycle headers are valid")


def main() -> int:
    return run_gate("gate-lifecycle-check", check)


if __name__ == "__main__":
    raise SystemExit(main())
