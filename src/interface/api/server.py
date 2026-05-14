"""
module_id: interface.api
file: src/interface/api/server.py
task_id: T-1102

Optional FastAPI server adapter for the Phase 11 API runtime.
"""

from __future__ import annotations

import importlib
import json
import sys
from collections.abc import Callable, Sequence
from typing import Any, cast

from interface.api.routes import API_ROUTES, ApiRouteSpec, openapi_route_index
from interface.api.runtime import ApiError, ApiRuntime, default_runtime

MODULE_ID = "interface.api"
OWNING_TASKS = ("T-1102",)


def build_app(runtime: ApiRuntime | None = None) -> object:
    try:
        fastapi_module = cast(Any, importlib.import_module("fastapi"))
    except ModuleNotFoundError as exc:
        raise ApiError("FastAPI is not installed; install the project with the api extra") from exc

    app = fastapi_module.FastAPI(
        title="Cloning Expression Vector Design API",
        version="0.1.0",
    )
    resolved_runtime = runtime or default_runtime()

    app.add_api_route(
        "/v1/health",
        _make_health_handler(resolved_runtime),
        methods=["GET"],
        name="health",
    )
    app.add_api_route(
        "/v1/openapi-route-index",
        _make_route_index_handler(resolved_runtime),
        methods=["GET"],
        name="openapi_route_index",
    )
    for route in API_ROUTES:
        if route.command_name is None or route.websocket:
            continue
        app.add_api_route(
            route.path,
            _make_command_handler(route, resolved_runtime, fastapi_module),
            methods=[route.method],
            name=route.name,
        )
    app.websocket("/v1/ws/validation")(_make_validation_websocket(resolved_runtime))
    return cast(object, app)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"-h", "--help"}:
        print("Run with the api extra installed: uvicorn interface.api.server:build_app")
        return 0
    try:
        build_app()
    except ApiError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(json.dumps(openapi_route_index(), sort_keys=True))
    return 0


def _make_health_handler(runtime: ApiRuntime) -> Callable[[], dict[str, object]]:
    def handler() -> dict[str, object]:
        return runtime.health().to_payload()

    return handler


def _make_route_index_handler(runtime: ApiRuntime) -> Callable[[], dict[str, object]]:
    def handler() -> dict[str, object]:
        return runtime.route_index().to_payload()

    return handler


def _make_command_handler(
    route: ApiRouteSpec,
    runtime: ApiRuntime,
    fastapi_module: Any,
) -> Callable[[dict[str, object]], dict[str, object]]:
    def handler(payload: dict[str, object] | None = None) -> dict[str, object]:
        response = runtime.handle_command(route.command_name or "", payload or {})
        if response.http_status >= 400:
            raise fastapi_module.HTTPException(
                status_code=response.http_status,
                detail=response.to_payload(),
            )
        return response.to_payload()

    return handler


def _make_validation_websocket(runtime: ApiRuntime) -> Callable[[object], Any]:
    async def websocket_handler(websocket: object) -> None:
        await _websocket_call(websocket, "accept")
        try:
            payload = await _websocket_call(websocket, "receive_json")
        except Exception:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        for event in runtime.stream_validation(cast(dict[str, object], payload)):
            await _websocket_call(websocket, "send_json", event.to_payload())

    return websocket_handler


async def _websocket_call(websocket: object, method_name: str, *args: object) -> Any:
    method = getattr(websocket, method_name)
    return await method(*args)


__all__ = [
    "build_app",
    "main",
]
