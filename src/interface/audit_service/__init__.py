"""
module_id: interface.audit_service
file: src/interface/audit_service/__init__.py
task_id: T-313b

Audit-service process boundary.
"""

from __future__ import annotations

from interface.audit_service.handlers import AuditServiceHandlers
from interface.audit_service.server import AuditServiceServer, audit_service_endpoint_for_platform

__all__ = [
    "AuditServiceHandlers",
    "AuditServiceServer",
    "audit_service_endpoint_for_platform",
]
