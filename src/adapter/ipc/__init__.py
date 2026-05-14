"""
module_id: adapter.ipc
file: src/adapter/ipc/__init__.py
task_id: T-313b

IPC clients.
"""

from __future__ import annotations

from adapter.ipc.audit_service_client import (
    AuditServiceClient,
    AuditServiceUnreachableError,
    InProcessAuditServiceTransport,
)

__all__ = [
    "AuditServiceClient",
    "AuditServiceUnreachableError",
    "InProcessAuditServiceTransport",
]
