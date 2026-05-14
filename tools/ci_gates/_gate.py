"""
module_id: tools.ci_gates._gate
file: tools/ci_gates/_gate.py
task_id: T-204

Shared command-line helper for lifecycle-aware CI gate skeletons.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class GateResult:
    passed: bool
    messages: tuple[str, ...] = ()


GateCheck = Callable[[Path], GateResult]


def pass_gate(message: str = "ok") -> GateResult:
    return GateResult(True, (message,))


def fail_gate(*messages: str) -> GateResult:
    return GateResult(False, tuple(messages))


def run_gate(name: str, check: GateCheck) -> int:
    parser = argparse.ArgumentParser(description=f"Run {name}.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--informational", action="store_true", help="Report but never fail.")
    mode.add_argument("--enforce", action="store_true", help="Fail when the gate detects drift.")
    args = parser.parse_args()

    result = check(ROOT)
    for message in result.messages:
        print(f"{name}: {message}")
    if result.passed:
        return 0
    return 0 if args.informational and not args.enforce else 1


def run_not_implemented(name: str) -> int:
    return run_gate(name, lambda _root: fail_gate("predicate not implemented yet"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
