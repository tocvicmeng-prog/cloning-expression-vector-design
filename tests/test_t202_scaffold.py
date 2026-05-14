"""
module_id: tests.scaffold
file: tests/test_t202_scaffold.py
task_id: T-202
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRECTORIES = (
    "catalogues/rules",
    "catalogues/vendor_profiles",
    "catalogues/screening_profiles",
    "catalogues/sop_templates",
    "catalogues/plugin_manifests",
    "benchmarks",
    "docs/handover",
    "events/design",
    "events/governance",
    "events/export",
    "exports",
    "snapshots",
    "task_artefacts",
    "tasks/task_brief",
    "tests/uat",
    "src/domain/ports",
    "src/engine",
    "src/app",
    "src/adapter",
    "src/interface",
)

REQUIRED_FILES = (
    "catalogues/parts.yaml",
    "catalogues/hosts.yaml",
    "catalogues/enzymes.yaml",
    "catalogues/rules/MR.yaml",
    "catalogues/rules/WR.yaml",
    "catalogues/rules/SR.yaml",
    "catalogues/rules/BR.yaml",
    "catalogues/rules/MS.yaml",
    "catalogues/vendor_profiles/twist.yaml",
    "catalogues/vendor_profiles/idt.yaml",
    "catalogues/vendor_profiles/genscript.yaml",
    "catalogues/risk_advisories.yaml",
    "catalogues/screening_trust_policy.yaml",
    "catalogues/institutional_policy.yaml",
    "catalogues/export_profiles.yaml",
    "src/domain/__init__.py",
    "src/domain/ports/__init__.py",
    "src/engine/__init__.py",
    "src/app/__init__.py",
    "src/adapter/__init__.py",
    "src/interface/__init__.py",
)

EXPECTED_WHEEL_PACKAGES = {
    "src/adapter",
    "src/app",
    "src/cev_design",
    "src/domain",
    "src/engine",
    "src/interface",
}


def test_t202_directories_exist() -> None:
    missing = [path for path in REQUIRED_DIRECTORIES if not (ROOT / path).is_dir()]
    assert missing == []


def test_t202_files_exist() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_wheel_includes_scaffold_packages() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    packages = set(pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"])
    assert packages >= EXPECTED_WHEEL_PACKAGES
