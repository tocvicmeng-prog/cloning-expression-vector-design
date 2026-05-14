"""
module_id: interface.api
file: src/interface/api/__init__.py
task_id: T-1102

Public API surface for HTTP and WebSocket adapters.
"""

from __future__ import annotations

from interface.api.routes import (
    ADMIN_COMMAND_ROUTES,
    API_COMMAND_NAMES,
    API_ROUTES,
    PUBLIC_COMMAND_ROUTES,
    SYSTEM_ROUTES,
    ApiRouteSpec,
    openapi_route_index,
    route_for_command,
)
from interface.api.runtime import (
    AdminTokenProvider,
    ApiError,
    ApiResponse,
    ApiRuntime,
    ApiStreamEvent,
    ValidationStreamHandler,
    command_route_summary,
    default_runtime,
    fastapi_available,
)
from interface.api.server import build_app, main

MODULE_ID = "interface.api"
OWNING_TASKS = ("T-1102",)

__all__ = [
    "ADMIN_COMMAND_ROUTES",
    "API_COMMAND_NAMES",
    "API_ROUTES",
    "PUBLIC_COMMAND_ROUTES",
    "SYSTEM_ROUTES",
    "AdminTokenProvider",
    "ApiError",
    "ApiResponse",
    "ApiRouteSpec",
    "ApiRuntime",
    "ApiStreamEvent",
    "ValidationStreamHandler",
    "build_app",
    "command_route_summary",
    "default_runtime",
    "fastapi_available",
    "main",
    "openapi_route_index",
    "route_for_command",
]
