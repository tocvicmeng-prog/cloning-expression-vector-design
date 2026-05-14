"""
module_id: tests.scaffold
file: tests/test_t203_module_manifest.py
task_id: T-203
"""

from __future__ import annotations

import importlib
from pathlib import Path

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
SOURCE_LAYERS = {"domain", "engine", "app", "adapter", "interface"}


def _source_module_ids() -> list[str]:
    manifest = yaml.safe_load((ROOT / "docs" / "module_manifest.yaml").read_text(encoding="utf-8"))
    return [
        entry["module_id"]
        for entry in manifest["modules"]
        if entry["module_id"].split(".", 1)[0] in SOURCE_LAYERS
    ]


def test_all_source_manifest_modules_are_importable() -> None:
    missing = []
    for module_id in _source_module_ids():
        try:
            importlib.import_module(module_id)
        except ModuleNotFoundError as exc:
            missing.append(f"{module_id}: {exc}")
    assert missing == []


def test_manifest_module_stubs_have_lightweight_headers() -> None:
    missing = []
    for module_id in _source_module_ids():
        relative = Path("src") / Path(*module_id.split("."))
        module_file = relative.with_suffix(".py")
        package_file = relative / "__init__.py"
        path = module_file if (ROOT / module_file).exists() else package_file
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in (f"module_id: {module_id}", "task_id:"):
            if token not in text:
                missing.append(f"{path}: missing {token}")
    assert missing == []
