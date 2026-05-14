"""
module_id: tests.interface.cli.test_cli_t1101
file: tests/interface/cli/test_cli_t1101.py
task_id: T-1101
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import cast

from domain.types.admin_ipc import AdminServiceVerb
from interface.cli import (
    ADMIN_COMMAND_NAMES,
    PUBLIC_COMMAND_NAMES,
    CliRuntime,
    get_command_spec,
    run_cli,
)
from tests.fakes.admin_service.client import InMemoryAdminServiceClient, signed_admin_token

NOW = datetime(2026, 5, 14, tzinfo=UTC)

EXPECTED_PUBLIC_COMMANDS = {
    "new",
    "open",
    "validate",
    "compile",
    "screen",
    "export",
    "library",
    "replay",
    "audit",
    "rule-index",
    "list-sessions",
    "acknowledge-advisory",
    "decline-advisory",
    "escalate-advisory",
    "status",
}

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


def test_phase_11_command_registry_matches_agenda_surface() -> None:
    assert set(PUBLIC_COMMAND_NAMES) == EXPECTED_PUBLIC_COMMANDS
    assert set(ADMIN_COMMAND_NAMES) == set(EXPECTED_ADMIN_VERBS)
    assert len((*PUBLIC_COMMAND_NAMES, *ADMIN_COMMAND_NAMES)) == 25
    assert all(get_command_spec(name).name == name for name in ADMIN_COMMAND_NAMES)


def test_public_commands_delegate_to_configured_runtime_handlers() -> None:
    def handler(command_name: str, payload: Mapping[str, object]) -> Mapping[str, object]:
        return {"payload": dict(payload), "seen_command": command_name}

    runtime = CliRuntime(public_handlers={"new": handler})

    result = runtime.run_command("new", {"project_name": "fixture"})

    assert result.status == "ok"
    assert result.payload == {
        "payload": {"project_name": "fixture"},
        "seen_command": "new",
    }


def test_admin_commands_route_through_admin_service_client_port() -> None:
    client = InMemoryAdminServiceClient(clock=lambda: NOW)
    runtime = CliRuntime(
        admin_client=client,
        admin_token_provider=lambda: signed_admin_token(now=NOW),
        clock=lambda: NOW,
    )

    for command_name in ADMIN_COMMAND_NAMES:
        result = runtime.run_command(
            command_name,
            {"fixture": command_name, "request_id": f"request-{command_name}"},
        )
        assert result.status == "accepted"
        assert result.exit_code == 0

    assert [request.verb for request in client.requests] == [
        EXPECTED_ADMIN_VERBS[command_name] for command_name in ADMIN_COMMAND_NAMES
    ]
    assert [request.payload["cli_command"] for request in client.requests] == list(
        ADMIN_COMMAND_NAMES
    )
    review_queue_ops = {
        request.payload["cli_command"]: request.payload.get("admin_operation")
        for request in client.requests
        if request.verb is AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM
    }
    assert review_queue_ops == {
        "submit-extension-request": "submit_extension_request",
        "list-review-queue": "list_review_queue",
        "triage-request": "triage_request",
    }


def test_fallback_cli_runner_emits_status_json() -> None:
    stdout = StringIO()

    exit_code = run_cli(["status"], runtime=CliRuntime(), stdout=stdout)

    payload = _json_object(stdout.getvalue())
    assert exit_code == 0
    assert payload["command"] == "status"
    assert payload["status"] == "ok"
    status_payload = cast(dict[str, object], payload["payload"])
    assert status_payload["admin_client_configured"] is False
    assert status_payload["public_commands"] == list(PUBLIC_COMMAND_NAMES)


def test_fallback_cli_runner_dispatches_admin_command_to_injected_client() -> None:
    client = InMemoryAdminServiceClient(clock=lambda: NOW)
    runtime = CliRuntime(
        admin_client=client,
        admin_token_provider=lambda: signed_admin_token(now=NOW),
        clock=lambda: NOW,
    )
    stdout = StringIO()

    exit_code = run_cli(
        [
            "admin-mint",
            "--request-id",
            "mint-1",
            "--profile-id",
            "profile-1",
            "--draft",
            '{"scope":"fixture"}',
        ],
        runtime=runtime,
        stdout=stdout,
    )

    payload = _json_object(stdout.getvalue())
    assert exit_code == 0
    assert payload["command"] == "admin-mint"
    assert client.requests[0].request_id == "mint-1"
    assert client.requests[0].payload["profile_id"] == "profile-1"
    assert client.requests[0].payload["draft"] == {"scope": "fixture"}


def test_admin_cli_requires_admin_service_client_binding() -> None:
    stderr = StringIO()

    exit_code = run_cli(
        ["admin-mint", "--request-id", "missing-client"],
        runtime=CliRuntime(admin_token_provider=lambda: signed_admin_token(now=NOW)),
        stderr=stderr,
    )

    payload = _json_object(stderr.getvalue())
    assert exit_code == 2
    assert payload["status"] == "error"
    assert "AdminServiceClientPort" in str(payload["message"])


def test_cli_source_does_not_directly_import_admin_action_handler() -> None:
    root = Path(__file__).resolve().parents[3]
    cli_sources = (root / "src" / "interface" / "cli").glob("*.py")

    for source_path in cli_sources:
        source = source_path.read_text(encoding="utf-8")
        assert "app.admin_action_handler" not in source
        assert "AdminActionHandler" not in source


def _json_object(text: str) -> dict[str, object]:
    raw = json.loads(text)
    assert isinstance(raw, dict)
    return cast(dict[str, object], raw)
