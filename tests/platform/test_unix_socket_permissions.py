"""
module_id: tests.platform
file: tests/platform/test_unix_socket_permissions.py
task_id: T-205
"""

from __future__ import annotations

import os
import socket
import stat

import pytest


@pytest.mark.skipif(os.name == "nt", reason="POSIX socket permission test")
def test_unix_socket_path_owner_and_mode(tmp_path) -> None:  # type: ignore[no-untyped-def]
    socket_path = tmp_path / "cev-audit-service.sock"
    af_unix = getattr(socket, "AF_UNIX", None)
    if af_unix is None:
        pytest.skip("AF_UNIX is not available on this platform")
    server = socket.socket(af_unix, socket.SOCK_STREAM)
    try:
        server.bind(str(socket_path))
        os.chmod(socket_path, 0o600)
        mode = stat.S_IMODE(socket_path.stat().st_mode)
        assert mode == 0o600
        assert len(str(socket_path)) < 100
    finally:
        server.close()
