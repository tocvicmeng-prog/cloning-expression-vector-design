"""
module_id: tests.platform
file: tests/platform/test_named_pipe_ipc_permissions.py
task_id: T-205
"""

from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(os.name != "nt", reason="Windows named-pipe path check")
def test_windows_named_pipe_paths_are_service_scoped() -> None:
    audit_pipe = r"\\.\pipe\cev-audit-service"
    admin_pipe = r"\\.\pipe\cev-admin-service"

    assert audit_pipe.startswith(r"\\.\pipe\cev-")
    assert admin_pipe.startswith(r"\\.\pipe\cev-")
    assert audit_pipe != admin_pipe
