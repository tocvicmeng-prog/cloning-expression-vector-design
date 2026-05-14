"""
module_id: interface.api
file: src/interface/api/runtime.py
task_id: T-1102

Injectable runtime for HTTP and WebSocket API handlers.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from domain.canonicalisation import canonical_json
from domain.ports import AdminServiceClientPort
from domain.types.admin_ipc import AdminIpcStatus, SignedAdminPrincipalToken
from interface.api.routes import API_ROUTES, openapi_route_index
from interface.cli import (
    ADMIN_COMMAND_NAMES,
    PUBLIC_COMMAND_NAMES,
    CliCommandResult,
    CliRuntime,
    PublicCommandHandler,
    typer_available,
)
from interface.cli.runtime import admin_token_from_environment

MODULE_ID = "interface.api"
OWNING_TASKS = ("T-1102",)

JsonObject = dict[str, object]
AdminTokenProvider = Callable[[], SignedAdminPrincipalToken]


class ValidationStreamHandler(Protocol):
    def __call__(self, payload: Mapping[str, object]) -> Iterable[Mapping[str, object]]: ...


class ApiError(RuntimeError):
    """Raised when the API runtime or server adapter is misconfigured."""


@dataclass(frozen=True, slots=True)
class ApiResponse:
    status: str
    payload: Mapping[str, object]
    http_status: int = 200
    message: str | None = None

    def to_payload(self) -> JsonObject:
        return {
            "message": self.message,
            "payload": dict(self.payload),
            "status": self.status,
        }

    def canonical_json(self) -> str:
        return canonical_json(self.to_payload()).decode("utf-8")


@dataclass(frozen=True, slots=True)
class ApiStreamEvent:
    event: str
    payload: Mapping[str, object]

    def to_payload(self) -> JsonObject:
        return {"event": self.event, "payload": dict(self.payload)}

    def canonical_json(self) -> str:
        return canonical_json(self.to_payload()).decode("utf-8")


class ApiRuntime:
    def __init__(
        self,
        *,
        admin_client: AdminServiceClientPort | None = None,
        admin_token_provider: AdminTokenProvider | None = None,
        public_handlers: Mapping[str, PublicCommandHandler] | None = None,
        validation_stream_handler: ValidationStreamHandler | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._cli_runtime = CliRuntime(
            admin_client=admin_client,
            admin_token_provider=admin_token_provider,
            public_handlers=public_handlers,
            clock=clock,
        )
        self._validation_stream_handler = validation_stream_handler
        self._clock = clock or (lambda: datetime.now(UTC))

    @property
    def has_admin_client(self) -> bool:
        return self._cli_runtime.has_admin_client

    def health(self) -> ApiResponse:
        return ApiResponse(
            status="ok",
            payload={
                "admin_client_configured": self.has_admin_client,
                "api_extra_fastapi_available": fastapi_available(),
                "cli_extra_typer_available": typer_available(),
                "checked_at_utc": _datetime_to_wire(self._clock()),
            },
        )

    def route_index(self) -> ApiResponse:
        return ApiResponse(status="ok", payload=openapi_route_index())

    def handle_command(
        self,
        command_name: str,
        payload: Mapping[str, object] | None = None,
        *,
        request_id: str | None = None,
    ) -> ApiResponse:
        command_payload = {} if payload is None else dict(payload)
        try:
            result = self._cli_runtime.run_command(
                command_name,
                command_payload,
                request_id=request_id,
            )
        except Exception as exc:
            return ApiResponse(
                status="error",
                payload={},
                http_status=400,
                message=str(exc),
            )
        return self._response_from_cli_result(result)

    def stream_validation(
        self,
        payload: Mapping[str, object] | None = None,
    ) -> tuple[ApiStreamEvent, ...]:
        validation_payload = {} if payload is None else dict(payload)
        started = ApiStreamEvent(
            "accepted",
            {
                "command": "validate",
                "received_at_utc": _datetime_to_wire(self._clock()),
            },
        )
        if self._validation_stream_handler is None:
            result = self.handle_command("validate", validation_payload)
            return (
                started,
                ApiStreamEvent(
                    "backend_required",
                    {
                        "http_status": result.http_status,
                        "message": result.message,
                        "payload": result.to_payload(),
                    },
                ),
                ApiStreamEvent("complete", {"status": result.status}),
            )

        events = [started]
        for event_payload in self._validation_stream_handler(validation_payload):
            events.append(
                ApiStreamEvent(
                    str(event_payload.get("event", "validation_event")),
                    {key: value for key, value in event_payload.items() if key != "event"},
                )
            )
        events.append(ApiStreamEvent("complete", {"status": "ok"}))
        return tuple(events)

    def _response_from_cli_result(self, result: CliCommandResult) -> ApiResponse:
        if result.command in ADMIN_COMMAND_NAMES:
            http_status = _admin_http_status(result)
        elif result.status == "backend_required":
            http_status = 501
        else:
            http_status = 200
        return ApiResponse(
            status=result.status,
            payload={
                "command": result.command,
                "command_payload": result.to_payload()["payload"],
            },
            http_status=http_status,
            message=result.message,
        )


def default_runtime() -> ApiRuntime:
    return ApiRuntime(admin_token_provider=admin_token_from_environment)


def fastapi_available() -> bool:
    return importlib.util.find_spec("fastapi") is not None


def command_route_summary() -> dict[str, object]:
    return {
        "admin_commands": list(ADMIN_COMMAND_NAMES),
        "public_commands": list(PUBLIC_COMMAND_NAMES),
        "routes": [
            {
                "method": route.method,
                "path": route.path,
                "command_name": route.command_name,
                "requires_admin_service": route.requires_admin_service,
                "websocket": route.websocket,
            }
            for route in API_ROUTES
        ],
    }


def _admin_http_status(result: CliCommandResult) -> int:
    admin_response = result.payload.get("admin_response")
    if not isinstance(admin_response, Mapping):
        return 502
    status = admin_response.get("status")
    if status == AdminIpcStatus.ACCEPTED.value:
        return 202
    if status == AdminIpcStatus.DENIED.value:
        return 403
    return 502


def _datetime_to_wire(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


__all__ = [
    "AdminTokenProvider",
    "ApiError",
    "ApiResponse",
    "ApiRuntime",
    "ApiStreamEvent",
    "ValidationStreamHandler",
    "command_route_summary",
    "default_runtime",
    "fastapi_available",
]
