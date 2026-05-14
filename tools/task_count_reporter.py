"""
module_id: tools.task_count_reporter
file: tools/task_count_reporter.py
task_id: T-204

Report active task counts from docs/task_manifest.yaml.
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]


def report(root: Path) -> str:
    manifest = yaml.safe_load((root / "docs" / "task_manifest.yaml").read_text(encoding="utf-8"))
    phase_counts = manifest["phase_counts"]
    lines = [f"active_task_card_count: {manifest['active_task_card_count']}"]
    lines.extend(f"phase_{phase}: {count}" for phase, count in phase_counts.items())
    return "\n".join(lines)


def main() -> int:
    print(report(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
