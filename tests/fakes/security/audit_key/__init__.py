"""
module_id: tests.fakes.security.audit_key
file: tests/fakes/security/audit_key/__init__.py
task_id: T-312a

Audit-key provider test fake.
"""

from __future__ import annotations

from tests.fakes.security.audit_key.provider import AuditKeyRotation, TestAuditKeyProvider

__all__ = [
    "AuditKeyRotation",
    "TestAuditKeyProvider",
]
