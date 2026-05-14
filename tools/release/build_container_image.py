"""
module_id: tools.release.build_container_image
file: tools/release/build_container_image.py
task_id: T-1303

Pinned Docker image build wrapper for release verification.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TAG = "cev-design:0.1.0"


@dataclass(frozen=True)
class ContainerBuildPlan:
    command: tuple[str, ...]
    dockerfile: Path
    tag: str
    platform: str

    def to_payload(self) -> dict[str, object]:
        return {
            "command": list(self.command),
            "dockerfile": str(self.dockerfile),
            "platform": self.platform,
            "tag": self.tag,
        }


def build_plan(
    root: Path = ROOT,
    *,
    dockerfile: Path | None = None,
    tag: str = DEFAULT_TAG,
    platform: str = "linux/amd64",
) -> ContainerBuildPlan:
    resolved_dockerfile = dockerfile or root / "Dockerfile"
    return ContainerBuildPlan(
        command=(
            "docker",
            "build",
            "--pull",
            "--platform",
            platform,
            "--label",
            "org.opencontainers.image.title=Cloning Expression Vector Design",
            "--label",
            "org.opencontainers.image.version=0.1.0",
            "--tag",
            tag,
            "--file",
            str(resolved_dockerfile),
            str(root),
        ),
        dockerfile=resolved_dockerfile,
        tag=tag,
        platform=platform,
    )


def run_build(plan: ContainerBuildPlan, *, dry_run: bool = False) -> int:
    if dry_run:
        print(json.dumps(plan.to_payload(), sort_keys=True, indent=2))
        return 0
    return subprocess.run(plan.command, cwd=ROOT, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the pinned release container image.")
    parser.add_argument("--dockerfile", type=Path, default=ROOT / "Dockerfile")
    parser.add_argument("--platform", default="linux/amd64")
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return run_build(
        build_plan(dockerfile=args.dockerfile, platform=args.platform, tag=args.tag),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
