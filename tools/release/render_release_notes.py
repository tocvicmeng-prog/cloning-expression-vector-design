"""
module_id: tools.release.render_release_notes
file: tools/release/render_release_notes.py
task_id: T-1303

Render release notes from the task manifest and release-note template.
"""

from __future__ import annotations

import argparse
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "tools" / "release" / "release_notes_template.md"
TASK_MANIFEST = ROOT / "docs" / "task_manifest.yaml"


@dataclass(frozen=True)
class ReleaseNotesContext:
    version: str
    release_date: str
    active_task_count: int
    final_task_id: str
    phase_count: int


def context(root: Path = ROOT, *, release_date: str = "2026-05-14") -> ReleaseNotesContext:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((root / "docs" / "task_manifest.yaml").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("task manifest must contain a mapping")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("task manifest must contain tasks")
    project = pyproject.get("project")
    if not isinstance(project, dict):
        raise ValueError("pyproject.toml must contain [project]")
    version = project.get("version")
    if not isinstance(version, str):
        raise ValueError("project.version must be a string")
    phase_order = manifest.get("phase_order")
    if not isinstance(phase_order, list):
        raise ValueError("task manifest must contain phase_order")
    final_task = tasks[-1]
    if not isinstance(final_task, dict) or not isinstance(final_task.get("task_id"), str):
        raise ValueError("final task manifest entry must contain task_id")
    active_count = manifest.get("active_task_card_count")
    if not isinstance(active_count, int):
        raise ValueError("active_task_card_count must be an integer")
    return ReleaseNotesContext(
        version=version,
        release_date=release_date,
        active_task_count=active_count,
        final_task_id=final_task["task_id"],
        phase_count=len(phase_order),
    )


def render_release_notes(
    root: Path = ROOT,
    *,
    template_path: Path = TEMPLATE,
    release_date: str = "2026-05-14",
) -> str:
    release_context = context(root, release_date=release_date)
    template = template_path.read_text(encoding="utf-8")
    return template.format(
        active_task_count=release_context.active_task_count,
        final_task_id=release_context.final_task_id,
        phase_count=release_context.phase_count,
        release_date=release_context.release_date,
        version=release_context.version,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render release notes from the task manifest.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/release/v0.1.0_release_notes.md",
    )
    parser.add_argument("--release-date", default="2026-05-14")
    args = parser.parse_args(argv)
    rendered = render_release_notes(release_date=args.release_date)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
