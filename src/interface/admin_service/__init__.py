"""
module_id: interface.admin_service
file: src/interface/admin_service/__init__.py
task_id: T-1103b

Production admin-service IPC boundary.
"""

from __future__ import annotations

from interface.admin_service.auth import (
    AdminPrincipalTokenVerifier,
    AdminSecurityEvent,
    AdminServiceAuthenticationError,
    AdminServiceAuthenticator,
    AdminServiceAuthorisationError,
    AuthenticatedAdminCaller,
    InMemoryAdminServiceSecurityLog,
)
from interface.admin_service.handlers import AdminServiceHandlers
from interface.admin_service.ipc import (
    AdminServiceAccessPolicy,
    AdminServiceProtocolError,
    AdminServiceServer,
    admin_service_access_policy_for_platform,
    admin_service_endpoint_for_platform,
    decode_admin_frame,
    encode_admin_frame,
    validate_admin_service_access_policy,
)
from interface.admin_service.review_queue_admin import AdminServiceReviewQueueHandler

__all__ = [
    "AdminPrincipalTokenVerifier",
    "AdminSecurityEvent",
    "AdminServiceAccessPolicy",
    "AdminServiceAuthenticationError",
    "AdminServiceAuthenticator",
    "AdminServiceAuthorisationError",
    "AdminServiceHandlers",
    "AdminServiceProtocolError",
    "AdminServiceReviewQueueHandler",
    "AdminServiceServer",
    "AuthenticatedAdminCaller",
    "InMemoryAdminServiceSecurityLog",
    "admin_service_access_policy_for_platform",
    "admin_service_endpoint_for_platform",
    "decode_admin_frame",
    "encode_admin_frame",
    "validate_admin_service_access_policy",
]
