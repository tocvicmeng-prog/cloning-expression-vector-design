from __future__ import annotations

import json
from pathlib import Path

import pytest

from interface.ui import assert_ui_package_present, load_ui_package_json, ui_package_manifest


def test_ui_package_manifest_resolves_react_workspace() -> None:
    manifest = assert_ui_package_present()

    assert manifest.package_name == "@cloning-expression-vector-design/ui"
    assert manifest.package_root.name == "ui"
    assert manifest.index_html.name == "index.html"
    assert manifest.source_root.joinpath("App.tsx").exists()
    assert {route.path for route in manifest.routes} == {"/", "/admin", "/audit"}


def test_load_ui_package_json_uses_structured_json() -> None:
    package_data = load_ui_package_json()

    assert package_data["type"] == "module"
    assert package_data["scripts"]["build"] == "tsc --noEmit && vite build"
    assert "react" in package_data["dependencies"]


def test_missing_ui_package_reports_required_file(tmp_path: Path) -> None:
    ui_root = tmp_path / "ui"
    ui_root.mkdir()
    ui_root.joinpath("package.json").write_text(
        json.dumps({"name": "@cloning-expression-vector-design/ui"}),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="UI package is missing required files"):
        assert_ui_package_present(tmp_path)


def test_manifest_fails_cleanly_without_package_json(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="UI package manifest not found"):
        ui_package_manifest(tmp_path)
