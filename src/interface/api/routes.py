"""
module_id: interface.api
file: src/interface/api/routes.py
task_id: T-1102

HTTP and WebSocket route registry for the Phase 11 API surface.
"""

from __future__ import annotations

from dataclasses import dataclass

from interface.cli.commands import ADMIN_COMMANDS, PUBLIC_COMMANDS, CliCommandSpec

MODULE_ID = "interface.api"
OWNING_TASKS = ("T-1102",)


@dataclass(frozen=True, slots=True)
class ApiRouteSpec:
    name: str
    method: str
    path: str
    command_name: str | None
    summary: str
    requires_admin_service: bool = False
    websocket: bool = False


PUBLIC_COMMAND_ROUTES: tuple[ApiRouteSpec, ...] = tuple(
    ApiRouteSpec(
        name=f"command_{spec.name.replace('-', '_')}",
        method="POST",
        path=f"/v1/commands/{spec.name}",
        command_name=spec.name,
        summary=spec.description,
    )
    for spec in PUBLIC_COMMANDS
)

ADMIN_COMMAND_ROUTES: tuple[ApiRouteSpec, ...] = tuple(
    ApiRouteSpec(
        name=f"admin_{spec.name.replace('-', '_')}",
        method="POST",
        path=f"/v1/admin/{spec.name}",
        command_name=spec.name,
        summary=spec.description,
        requires_admin_service=True,
    )
    for spec in ADMIN_COMMANDS
)

SYSTEM_ROUTES: tuple[ApiRouteSpec, ...] = (
    ApiRouteSpec(
        name="health",
        method="GET",
        path="/v1/health",
        command_name=None,
        summary="Report process health.",
    ),
    ApiRouteSpec(
        name="openapi",
        method="GET",
        path="/v1/openapi-route-index",
        command_name=None,
        summary="Return the dependency-free route index used by tests and clients.",
    ),
    ApiRouteSpec(
        name="validation_stream",
        method="WEBSOCKET",
        path="/v1/ws/validation",
        command_name="validate",
        summary="Stream validation progress events for a design payload.",
        websocket=True,
    ),
)

API_ROUTES: tuple[ApiRouteSpec, ...] = (
    *SYSTEM_ROUTES,
    *PUBLIC_COMMAND_ROUTES,
    *ADMIN_COMMAND_ROUTES,
)
API_COMMAND_NAMES = tuple(
    route.command_name for route in (*PUBLIC_COMMAND_ROUTES, *ADMIN_COMMAND_ROUTES)
)


def route_for_command(command_name: str) -> ApiRouteSpec:
    for route in (*PUBLIC_COMMAND_ROUTES, *ADMIN_COMMAND_ROUTES):
        if route.command_name == command_name:
            return route
    raise ValueError(f"unknown API command route: {command_name}")


def command_spec_for_route(route: ApiRouteSpec) -> CliCommandSpec:
    if route.command_name is None:
        raise ValueError(f"route is not command-backed: {route.name}")
    for spec in (*PUBLIC_COMMANDS, *ADMIN_COMMANDS):
        if spec.name == route.command_name:
            return spec
    raise ValueError(f"unknown command-backed route: {route.command_name}")


def openapi_route_index() -> dict[str, object]:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Cloning Expression Vector Design API",
            "version": "0.1.0",
        },
        "paths": {
            route.path: {
                route.method.lower(): {
                    "operationId": route.name,
                    "summary": route.summary,
                    "x-command-name": route.command_name,
                    "x-requires-admin-service": route.requires_admin_service,
                    "x-websocket": route.websocket,
                }
            }
            for route in API_ROUTES
        },
    }


__all__ = [
    "ADMIN_COMMAND_ROUTES",
    "API_COMMAND_NAMES",
    "API_ROUTES",
    "PUBLIC_COMMAND_ROUTES",
    "SYSTEM_ROUTES",
    "ApiRouteSpec",
    "command_spec_for_route",
    "openapi_route_index",
    "route_for_command",
]
