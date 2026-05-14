"""
module_id: tests.release.test_t1303_release_scripts
file: tests/release/test_t1303_release_scripts.py
task_id: T-1303
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tools.release import build_container_image, build_wheel, render_release_notes

ROOT = Path(__file__).resolve().parents[2]


def test_wheel_build_plan_is_reproducible(tmp_path: Path) -> None:
    plan = build_wheel.build_plan(dist_dir=tmp_path / "dist")

    assert plan.command[:3] == (sys.executable, "-m", "uv")
    assert "--wheel" in plan.command
    assert dict(plan.environment)["SOURCE_DATE_EPOCH"] == build_wheel.SOURCE_DATE_EPOCH
    assert dict(plan.environment)["PYTHONHASHSEED"] == "0"


def test_container_build_plan_uses_pinned_release_image_inputs() -> None:
    plan = build_container_image.build_plan(tag="cev-design:test", platform="linux/amd64")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert plan.command[:2] == ("docker", "build")
    assert "--pull" in plan.command
    assert "linux/amd64" in plan.command
    assert "cev-design:test" in plan.command
    assert "FROM python:3.11.15-slim-bookworm" in dockerfile
    assert "UV_VERSION=0.11.14" in dockerfile
    assert "uv sync --frozen --no-editable --group dev" in dockerfile


def test_release_notes_template_renders_from_task_manifest() -> None:
    rendered = render_release_notes.render_release_notes(ROOT)

    assert "Cloning Expression Vector Design 0.1.0 Release Notes" in rendered
    assert "71 active implementation task cards" in rendered
    assert "ending at T-1303" in rendered
    assert "100-realisation combinatorial-library benchmark" in rendered


def test_release_docs_are_present_and_actionable() -> None:
    expected = (
        ROOT / "docs/release/v0.1.0_release_notes.md",
        ROOT / "docs/release/installation.md",
        ROOT / "docs/release/migration_from_v0.0_to_v0.1.md",
    )

    for path in expected:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("# ")
        assert "v0.1" in text or "0.1.0" in text


def test_release_build_dry_runs_emit_machine_readable_payloads(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert build_wheel.run_build(build_wheel.build_plan(dist_dir=tmp_path), dry_run=True) == 0
    wheel_output = capsys.readouterr().out
    assert json.loads(wheel_output)["environment"]["PYTHONHASHSEED"] == "0"

    assert (
        build_container_image.run_build(
            build_container_image.build_plan(tag="cev-design:test"),
            dry_run=True,
        )
        == 0
    )
    container_output = capsys.readouterr().out
    assert json.loads(container_output)["tag"] == "cev-design:test"
