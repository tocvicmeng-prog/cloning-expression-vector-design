"""
module_id: tools.task_manifest_generator
file: tools/task_manifest_generator.py
task_id: T-204

Emit a heading-derived seed task manifest from CODING_AGENDA.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
TASK_RE = re.compile(r"^#### (?P<section>2\.[^\s]+) `(?P<task_id>T-[^`]+)` — (?P<title>.+)$")


def generate(root: Path) -> dict[str, object]:
    tasks: list[dict[str, str]] = []
    for line in (root / "CODING_AGENDA.md").read_text(encoding="utf-8").splitlines():
        match = TASK_RE.match(line)
        if match:
            tasks.append(match.groupdict())
    return {
        "generated_from": "CODING_AGENDA.md",
        "active_task_card_count": len(tasks),
        "tasks": tasks,
    }


def main() -> int:
    print(yaml.safe_dump(generate(ROOT), sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
