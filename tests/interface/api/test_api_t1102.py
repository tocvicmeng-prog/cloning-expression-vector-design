"""
module_id: tests.interface.api.test_api_t1102
file: tests/interface/api/test_api_t1102.py
task_id: T-1102
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from domain.types.admin_ipc import AdminServiceVerb
from interface.api import (
    ADMIN_COMMAND_ROUTES,
    API_ROUTES,
    PUBLIC_COMMAND_ROUTES,
    ApiError,
    ApiRuntime,
    build_app,
    fastapi_available,
    openapi_route_index,
    route_for_command,
)
from interface.cli import ADMIN_COMMAND_NAMES, PUBLIC_COMMAND_NAMES
from tests.fakes.admin_service.client import InMemoryAdminServiceClient, signed_admin_token

NOW = datetime(2026, 5, 14, tzinfo=UTC)

EXPECTED_ADMIN_VERBS = {
    "admin-mint": AdminServiceVerb.MINT_PROFILE,
    "admin-modify": AdminServiceVerb.MODIFY_PROFILE,
    "admin-revoke": AdminServiceVerb.REVOKE_PROFILE,
    "admin-mint-sop-template": AdminServiceVerb.MINT_SOP_TEMPLATE,
    "admin-modify-sop-template": AdminServiceVerb.MODIFY_SOP_TEMPLATE,
    "admin-revoke-sop-template": AdminServiceVerb.REVOKE_SOP_TEMPLATE,
    "audit-key-rotate": AdminServiceVerb.ROTATE_AUDIT_KEY,
    "submit-extension-request": AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM,
    "list-review-queue": AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM,
    "triage-request": AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM,
}


def test_api_route_registry_exposes_same_command_surface_as_cli() -> None:
    assert {route.command_name for route in PUBLIC_COMMAND_ROUTES} == set(PUBLIC_COMMAND_NAMES)
    assert {route.command_name for route in ADMIN_COMMAND_ROUTES} == set(ADMIN_COMMAND_NAMES)
    assert route_for_command("validate").path == "/v1/commands/validate"
    assert route_for_command("admin-mint").path == "/v1/admin/admin-mint"
    assert any(route.path == "/v1/ws/validation" and route.websocket for route in API_ROUTES)


def test_openapi_route_index_is_dependency_free_and_names_admin_boundary() -> None:
    route_index = openapi_route_index()
    paths = cast(dict[str, object], route_index["paths"])
    admin_route = cast(dict[str, object], paths["/v1/admin/admin-mint"])
    post_spec = cast(dict[str, object], admin_route["post"])

    assert route_index["openapi"] == "3.1.0"
    assert post_spec["x-command-name"] == "admin-mint"
    assert post_spec["x-requires-admin-service"] is True
    assert "/v1/ws/validation" in paths


def test_public_api_commands_delegate_to_configured_handlers() -> None:
    def handler(command_name: str, payload: Mapping[str, object]) -> Mapping[str, object]:
        return {"seen_command": command_name, "payload": dict(payload)}

    runtime = ApiRuntime(public_handlers={"new": handler}, clock=lambda: NOW)

    response = runtime.handle_command("new", {"project_name": "fixture"})

    assert response.status == "ok"
    assert response.http_status == 200
    command_payload = cast(dict[str, object], response.payload["command_payload"])
    assert command_payload == {
        "payload": {"project_name": "fixture"},
        "seen_command": "new",
    }


def test_admin_api_commands_route_through_admin_service_client_port() -> None:
    client = InMemoryAdminServiceClient(clock=lambda: NOW)
    runtime = ApiRuntime(
        admin_client=client,
        admin_token_provider=lambda: signed_admin_token(now=NOW),
        clock=lambda: NOW,
    )

    for command_name in ADMIN_COMMAND_NAMES:
        response = runtime.handle_command(
            command_name,
            {"fixture": command_name, "request_id": f"api-{command_name}"},
        )
        assert response.status == "accepted"
        assert response.http_status == 202

    assert [request.verb for request in client.requests] == [
        EXPECTED_ADMIN_VERBS[command_name] for command_name in ADMIN_COMMAND_NAMES
    ]
    assert [request.payload["cli_command"] for request in client.requests] == list(
        ADMIN_COMMAND_NAMES
    )
    assert {
        request.payload["cli_command"]: request.payload.get("admin_operation")
        for request in client.requests
        if request.verb is AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM
    } == {
        "submit-extension-request": "submit_extension_request",
        "list-review-queue": "list_review_queue",
        "triage-request": "triage_request",
    }


def test_admin_api_command_without_admin_client_returns_http_error_payload() -> None:
    runtime = ApiRuntime(
        admin_token_provider=lambda: signed_admin_token(now=NOW),
        clock=lambda: NOW,
    )

    response = runtime.handle_command("admin-mint", {"request_id": "missing-client"})

    assert response.status == "error"
    assert response.http_status == 400
    assert "AdminServiceClientPort" in str(response.message)


def test_validation_websocket_stream_falls_back_to_runtime_command() -> None:
    runtime = ApiRuntime(clock=lambda: NOW)

    events = runtime.stream_validation({"design_session_id": "session-1"})

    assert [event.event for event in events] == ["accepted", "backend_required", "complete"]
    assert events[1].payload["http_status"] == 501


def test_validation_websocket_stream_uses_configured_handler() -> None:
    def stream_handler(payload: Mapping[str, object]) -> Iterable[Mapping[str, object]]:
        yield {"event": "validation_started", "design_session_id": payload["design_session_id"]}
        yield {"event": "validation_result", "status": "PASS"}

    runtime = ApiRuntime(validation_stream_handler=stream_handler, clock=lambda: NOW)

    events = runtime.stream_validation({"design_session_id": "session-1"})

    assert [event.event for event in events] == [
        "accepted",
        "validation_started",
        "validation_result",
        "complete",
    ]
    assert events[2].payload == {"status": "PASS"}


def test_fastapi_app_builder_is_optional_in_base_environment() -> None:
    if fastapi_available():
        app = build_app(ApiRuntime(clock=lambda: NOW))
        assert app is not None
        return
    with pytest.raises(ApiError, match="api extra"):
        build_app(ApiRuntime(clock=lambda: NOW))


def test_api_source_does_not_directly_import_admin_action_surface() -> None:
    root = Path(__file__).resolve().parents[3]
    api_sources = (root / "src" / "interface" / "api").glob("*.py")

    for source_path in api_sources:
        source = source_path.read_text(encoding="utf-8")
        assert "app.admin_action_handler" not in source
        assert "AdminActionHandler" not in source
