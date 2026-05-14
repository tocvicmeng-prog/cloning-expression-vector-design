"""
module_id: interface.ui
file: src/interface/ui.py
task_id: T-1202

Public metadata helpers for the React/TypeScript workspace package.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

MODULE_ID = "interface.ui"
OWNING_TASKS = ("T-1202",)


@dataclass(frozen=True)
class UiRoute:
    """A route that the SPA owns at runtime."""

    path: str
    label: str


@dataclass(frozen=True)
class UiPackageManifest:
    """Resolved metadata for the UI package."""

    package_name: str
    package_root: Path
    package_json: Path
    source_root: Path
    index_html: Path
    routes: tuple[UiRoute, ...]


DEFAULT_ROUTES: tuple[UiRoute, ...] = (
    UiRoute(path="/", label="Vector design workspace"),
    UiRoute(path="/admin", label="Admin console"),
    UiRoute(path="/audit", label="Audit log viewer"),
)


def project_root_from_module() -> Path:
    """Return the repository root inferred from this source module."""
    return Path(__file__).resolve().parents[2]


def ui_package_root(project_root: Path | None = None) -> Path:
    """Return the expected React package root."""
    return (project_root or project_root_from_module()) / "ui"


def load_ui_package_json(project_root: Path | None = None) -> dict[str, Any]:
    """Load the UI package.json as structured metadata."""
    package_json = ui_package_root(project_root) / "package.json"
    try:
        parsed: Any = json.loads(package_json.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"UI package manifest not found at {package_json}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"UI package manifest at {package_json} must be a JSON object")
    return cast(dict[str, Any], parsed)


def ui_package_manifest(project_root: Path | None = None) -> UiPackageManifest:
    """Return resolved UI package metadata used by launchers and tests."""
    root = ui_package_root(project_root)
    manifest_data = load_ui_package_json(project_root)
    package_name = str(manifest_data.get("name") or "@cloning-expression-vector-design/ui")
    return UiPackageManifest(
        package_name=package_name,
        package_root=root,
        package_json=root / "package.json",
        source_root=root / "src",
        index_html=root / "index.html",
        routes=DEFAULT_ROUTES,
    )


def assert_ui_package_present(project_root: Path | None = None) -> UiPackageManifest:
    """Validate that the checked-out UI package has the required entry points."""
    manifest = ui_package_manifest(project_root)
    missing = [
        path
        for path in (
            manifest.package_json,
            manifest.index_html,
            manifest.source_root / "main.tsx",
            manifest.source_root / "App.tsx",
        )
        if not path.exists()
    ]
    if missing:
        formatted = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"UI package is missing required files: {formatted}")
    return manifest
