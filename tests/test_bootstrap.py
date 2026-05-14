"""
module_id: tests.bootstrap
file: tests/test_bootstrap.py
task_id: T-201
"""

from __future__ import annotations

import cev_design


def test_package_version_is_defined() -> None:
    assert cev_design.__version__ == "0.1.0"
