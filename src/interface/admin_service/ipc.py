"""
module_id: interface.admin_service.ipc
file: src/interface/admin_service/ipc.py
task_id: T-1103b

Length-prefixed local IPC framing and ACL metadata for the admin service.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from domain.types.admin_ipc import (
    ADMIN_IPC_PROTOCOL_VERSION,
    AdminIpcErrorCode,
    AdminIpcRequest,
)
from interface.admin_service.handlers import AdminServiceHandlers

WINDOWS_ADMINISTRATORS_SID = "S-1-5-32-544"
DEFAULT_WINDOWS_SERVICE_SID = "S-1-5-80-3841409742-2387891205-2609850467-2403771797-187492902"
DEFAULT_ADMIN_SERVICE_ACCOUNT = "cev-admin-svc"
DEFAULT_ENGINE_SERVICE_ACCOUNT = "cev-engine-svc"
DEFAULT_POSIX_GROUP = "cev-admin"
DEFAULT_POSIX_MODE = 0o660


class AdminServiceProtocolError(ValueError):
    """Raised when an admin-service IPC frame is malformed."""


@dataclass(frozen=True, slots=True)
class AdminServiceAccessPolicy:
    endpoint: str
    service_account: str
    engine_account: str
    allowed_windows_sids: tuple[str, ...]
    posix_mode: int
    posix_group: str

    @property
    def service_account_separated(self) -> bool:
        return self.service_account != self.engine_account


class AdminServiceServer:
    """Serialized IPC server shim for admin-service verb dispatch."""

    def __init__(self, handlers: AdminServiceHandlers) -> None:
        self._handlers = handlers
        self._lock = RLock()

    def handle_frame(self, frame: bytes) -> bytes:
        with self._lock:
            try:
                payload = decode_admin_frame(frame)
                request = AdminIpcRequest.from_payload(payload)
                response = self._handlers.dispatch(request)
                return encode_admin_frame(response.to_payload())
            except Exception as exc:
                return encode_admin_frame(protocol_error_payload(exc))


def encode_admin_frame(payload: dict[str, object]) -> bytes:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(raw).to_bytes(4, byteorder="big") + raw


def decode_admin_frame(frame: bytes) -> dict[str, object]:
    if len(frame) < 4:
        raise AdminServiceProtocolError("admin-service frame is missing length prefix")
    expected_length = int.from_bytes(frame[:4], byteorder="big")
    body = frame[4:]
    if expected_length != len(body):
        raise AdminServiceProtocolError("admin-service frame length prefix does not match payload")
    try:
        raw = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise AdminServiceProtocolError(f"invalid admin-service frame JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise AdminServiceProtocolError("admin-service frame must be a JSON object")
    return dict(raw)


def protocol_error_payload(exc: Exception) -> dict[str, object]:
    error_code = AdminIpcErrorCode.VALIDATION_ERROR.value
    if isinstance(exc, AdminServiceProtocolError):
        error_code = AdminIpcErrorCode.VALIDATION_ERROR.value
    return {
        "error_code": error_code,
        "error_message": str(exc),
        "ok": False,
        "protocol_version": ADMIN_IPC_PROTOCOL_VERSION,
    }


def admin_service_endpoint_for_platform(name: str = "cev-admin-service") -> str:
    if os.name == "nt":
        return rf"\\.\pipe\{name}"
    return str(Path("/var/run/cev-admin") / "socket")


def admin_service_access_policy_for_platform(
    *,
    endpoint: str | None = None,
    service_account: str = DEFAULT_ADMIN_SERVICE_ACCOUNT,
    engine_account: str = DEFAULT_ENGINE_SERVICE_ACCOUNT,
    service_sid: str = DEFAULT_WINDOWS_SERVICE_SID,
    posix_group: str = DEFAULT_POSIX_GROUP,
) -> AdminServiceAccessPolicy:
    resolved_endpoint = endpoint or admin_service_endpoint_for_platform()
    if os.name == "nt":
        return AdminServiceAccessPolicy(
            endpoint=resolved_endpoint,
            service_account=service_account,
            engine_account=engine_account,
            allowed_windows_sids=(WINDOWS_ADMINISTRATORS_SID, service_sid),
            posix_mode=DEFAULT_POSIX_MODE,
            posix_group=posix_group,
        )
    return AdminServiceAccessPolicy(
        endpoint=resolved_endpoint,
        service_account=service_account,
        engine_account=engine_account,
        allowed_windows_sids=(WINDOWS_ADMINISTRATORS_SID, service_sid),
        posix_mode=DEFAULT_POSIX_MODE,
        posix_group=posix_group,
    )


def validate_admin_service_access_policy(policy: AdminServiceAccessPolicy) -> None:
    if not policy.service_account_separated:
        raise ValueError("admin-service account must be separate from engine account")
    if WINDOWS_ADMINISTRATORS_SID not in policy.allowed_windows_sids:
        raise ValueError("Windows admin-service ACL must include Administrators SID")
    if len(policy.allowed_windows_sids) < 2:
        raise ValueError("Windows admin-service ACL must include a service-account SID")
    if policy.posix_mode != DEFAULT_POSIX_MODE:
        raise ValueError("POSIX admin-service socket must use mode 0660")
    if policy.posix_group != DEFAULT_POSIX_GROUP:
        raise ValueError("POSIX admin-service socket must be owned by cev-admin group")


__all__ = [
    "DEFAULT_ADMIN_SERVICE_ACCOUNT",
    "DEFAULT_ENGINE_SERVICE_ACCOUNT",
    "DEFAULT_POSIX_GROUP",
    "DEFAULT_POSIX_MODE",
    "DEFAULT_WINDOWS_SERVICE_SID",
    "WINDOWS_ADMINISTRATORS_SID",
    "AdminServiceAccessPolicy",
    "AdminServiceProtocolError",
    "AdminServiceServer",
    "admin_service_access_policy_for_platform",
    "admin_service_endpoint_for_platform",
    "decode_admin_frame",
    "encode_admin_frame",
    "protocol_error_payload",
    "validate_admin_service_access_policy",
]
