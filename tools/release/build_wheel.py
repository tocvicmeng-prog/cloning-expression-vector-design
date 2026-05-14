"""
module_id: tools.release.build_wheel
file: tools/release/build_wheel.py
task_id: T-1303

Reproducible wheel build wrapper for the v0.1.0 release.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DATE_EPOCH = "1778716800"


@dataclass(frozen=True)
class WheelBuildPlan:
    command: tuple[str, ...]
    environment: tuple[tuple[str, str], ...]
    dist_dir: Path

    def to_payload(self) -> dict[str, object]:
        return {
            "command": list(self.command),
            "dist_dir": str(self.dist_dir),
            "environment": dict(self.environment),
        }


def build_plan(root: Path = ROOT, dist_dir: Path | None = None) -> WheelBuildPlan:
    resolved_dist = dist_dir or root / "dist"
    return WheelBuildPlan(
        command=(
            sys.executable,
            "-m",
            "uv",
            "build",
            "--wheel",
            "--out-dir",
            str(resolved_dist),
        ),
        environment=(
            ("PYTHONHASHSEED", "0"),
            ("SOURCE_DATE_EPOCH", SOURCE_DATE_EPOCH),
        ),
        dist_dir=resolved_dist,
    )


def run_build(plan: WheelBuildPlan, *, dry_run: bool = False) -> int:
    if dry_run:
        print(json.dumps(plan.to_payload(), sort_keys=True, indent=2))
        return 0
    plan.dist_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(dict(plan.environment))
    return subprocess.run(plan.command, cwd=ROOT, env=env, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the release wheel reproducibly.")
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return run_build(build_plan(dist_dir=args.dist_dir), dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
