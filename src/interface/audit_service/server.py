"""
module_id: interface.audit_service.server
file: src/interface/audit_service/server.py
task_id: T-313b

Framed JSON audit-service server.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from threading import RLock

from interface.audit_service.handlers import AuditServiceHandlers, entry_from_payload


class AuditServiceProtocolError(ValueError):
    """Raised when an audit-service IPC frame is malformed."""


class AuditServiceServer:
    def __init__(self, handlers: AuditServiceHandlers) -> None:
        self._handlers = handlers
        self._lock = RLock()

    def handle_frame(self, frame: bytes) -> bytes:
        with self._lock:
            try:
                request = _decode_frame(frame)
                verb = _expect_str(request.get("verb"), "verb")
                if verb == "engine_append":
                    entry_id = self._handlers.engine_append(
                        entry_from_payload(_expect_dict(request.get("entry"), "entry")),
                        _expect_str(request.get("service_name"), "service_name"),
                        base64.b64decode(_expect_str(request.get("token"), "token")),
                    )
                elif verb == "admin_append":
                    entry_id = self._handlers.admin_append(
                        entry_from_payload(_expect_dict(request.get("entry"), "entry")),
                        _expect_str(request.get("principal_id"), "principal_id"),
                        base64.b64decode(_expect_str(request.get("token"), "token")),
                    )
                else:
                    raise AuditServiceProtocolError(f"unsupported audit-service verb: {verb}")
                return _encode_frame({"entry_id": str(entry_id), "ok": True})
            except Exception as exc:
                return _encode_frame({"error": str(exc), "ok": False})


def audit_service_endpoint_for_platform(name: str = "cev-audit-service") -> str:
    if os.name == "nt":
        return rf"\\.\pipe\{name}"
    return str(Path("/var/run/cev-audit") / "socket")


def _decode_frame(frame: bytes) -> dict[str, object]:
    try:
        raw = json.loads(frame.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise AuditServiceProtocolError(f"invalid audit-service frame JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise AuditServiceProtocolError("audit-service frame must be a JSON object")
    return dict(raw)


def _encode_frame(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _expect_dict(raw: object, field_name: str) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise AuditServiceProtocolError(f"{field_name} must be a JSON object")
    return dict(raw)


def _expect_str(raw: object, field_name: str) -> str:
    if not isinstance(raw, str):
        raise AuditServiceProtocolError(f"{field_name} must be a string")
    return raw
