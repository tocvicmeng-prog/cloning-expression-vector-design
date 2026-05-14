"""
module_id: tools.ci_gates.test_roadmap_stale_tokens
file: tools/ci_gates/test_roadmap_stale_tokens.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-204
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

STALE_TOKENS = ("Finalised v1.3", "CODING_AGENDA.md v1.3", "SopTemplateLibrary")


def check(root: Path) -> GateResult:
    active_roadmap = (root / "ROADMAP.md").read_text(encoding="utf-8").split("## Appendix A", 1)[0]
    active_readme = (root / "README.md").read_text(encoding="utf-8")
    text = active_readme + "\n" + active_roadmap
    messages = [
        f"active support docs contain stale token {token!r}"
        for token in STALE_TOKENS
        if token in text
    ]
    if messages:
        return fail_gate(*messages)
    return pass_gate("support docs active sections contain no stale tokens")


def main() -> int:
    return run_gate("test-roadmap-stale-tokens", check)


if __name__ == "__main__":
    raise SystemExit(main())
