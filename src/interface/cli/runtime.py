"""
module_id: interface.cli
file: src/interface/cli/runtime.py
task_id: T-1101

Injectable runtime for command-line command handlers.
"""

from __future__ import annotations

import importlib.util
import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, cast

from domain.canonicalisation import canonical_json
from domain.ports import AdminServiceClientPort
from domain.types.admin_ipc import AdminIpcResponse, AdminIpcStatus, SignedAdminPrincipalToken
from interface.cli.commands import (
    ADMIN_COMMAND_NAMES,
    ALL_COMMAND_NAMES,
    PUBLIC_COMMAND_NAMES,
    CliCommandSpec,
    get_command_spec,
)

MODULE_ID = "interface.cli"
OWNING_TASKS = ("T-1101",)

JsonObject = dict[str, object]
AdminTokenProvider = Callable[[], SignedAdminPrincipalToken]


class PublicCommandHandler(Protocol):
    def __call__(
        self,
        command_name: str,
        payload: Mapping[str, object],
    ) -> CliCommandResult | Mapping[str, object]: ...


class CliError(RuntimeError):
    """Raised when a CLI command cannot be executed by the configured runtime."""


@dataclass(frozen=True, slots=True)
class CliCommandResult:
    command: str
    status: str
    payload: Mapping[str, object]
    exit_code: int = 0
    message: str | None = None

    def to_payload(self) -> JsonObject:
        return {
            "command": self.command,
            "message": self.message,
            "payload": dict(self.payload),
            "status": self.status,
        }

    def canonical_json(self) -> str:
        return canonical_json(self.to_payload()).decode("utf-8")


class CliRuntime:
    def __init__(
        self,
        *,
        admin_client: AdminServiceClientPort | None = None,
        admin_token_provider: AdminTokenProvider | None = None,
        public_handlers: Mapping[str, PublicCommandHandler] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._admin_client = admin_client
        self._admin_token_provider = admin_token_provider
        self._public_handlers = dict(public_handlers or {})
        self._clock = clock or (lambda: datetime.now(UTC))

    @property
    def has_admin_client(self) -> bool:
        return self._admin_client is not None

    def run_command(
        self,
        command_name: str,
        payload: Mapping[str, object] | None = None,
        *,
        request_id: str | None = None,
    ) -> CliCommandResult:
        spec = get_command_spec(command_name)
        command_payload = {} if payload is None else dict(payload)
        if spec.requires_admin_service:
            return self.run_admin_command(spec, command_payload, request_id=request_id)
        return self.run_public_command(spec, command_payload)

    def run_public_command(
        self,
        spec: CliCommandSpec,
        payload: Mapping[str, object],
    ) -> CliCommandResult:
        if spec.name == "status":
            return self._status_result(payload)

        handler = self._public_handlers.get(spec.name)
        if handler is None:
            return CliCommandResult(
                command=spec.name,
                status="backend_required",
                payload={
                    "command_payload": dict(payload),
                    "required_handler": f"interface.cli:{spec.name}",
                },
                exit_code=2,
                message="No command handler is configured for this CLI runtime.",
            )

        handler_result = handler(spec.name, dict(payload))
        if isinstance(handler_result, CliCommandResult):
            return handler_result
        return CliCommandResult(command=spec.name, status="ok", payload=dict(handler_result))

    def run_admin_command(
        self,
        spec: CliCommandSpec,
        payload: Mapping[str, object],
        *,
        request_id: str | None = None,
    ) -> CliCommandResult:
        client = self._admin_client
        if client is None:
            raise CliError("admin commands require an AdminServiceClientPort runtime binding")
        if self._admin_token_provider is None:
            raise CliError("admin commands require a signed admin principal token provider")
        if spec.admin_method is None:
            raise CliError(f"admin command has no admin-service method: {spec.name}")

        token = self._admin_token_provider()
        admin_payload = self._admin_payload(spec, payload)
        response = self._invoke_admin_client(
            client,
            spec.admin_method,
            token,
            admin_payload,
            request_id=request_id or _optional_str(payload.get("request_id")),
        )
        return CliCommandResult(
            command=spec.name,
            status=response.status.value,
            payload={
                "admin_response": response.to_payload(),
                "admin_service_method": spec.admin_method,
                "admin_transport": "AdminServiceClientPort",
                "admin_verb": response.verb.value,
            },
            exit_code=0 if response.status is AdminIpcStatus.ACCEPTED else 1,
        )

    def _status_result(self, payload: Mapping[str, object]) -> CliCommandResult:
        return CliCommandResult(
            command="status",
            status="ok",
            payload={
                "admin_client_configured": self._admin_client is not None,
                "admin_commands": list(ADMIN_COMMAND_NAMES),
                "cli_extra_typer_available": typer_available(),
                "command_payload": dict(payload),
                "configured_public_handlers": sorted(self._public_handlers),
                "public_commands": list(PUBLIC_COMMAND_NAMES),
            },
        )

    def _admin_payload(
        self,
        spec: CliCommandSpec,
        payload: Mapping[str, object],
    ) -> JsonObject:
        command_payload: JsonObject = {
            "cli_command": spec.name,
            "requested_at_utc": _datetime_to_wire(self._clock()),
            **dict(payload),
        }
        if spec.admin_operation is not None:
            command_payload["admin_operation"] = spec.admin_operation
        return command_payload

    def _invoke_admin_client(
        self,
        client: AdminServiceClientPort,
        method_name: str,
        token: SignedAdminPrincipalToken,
        payload: Mapping[str, object],
        *,
        request_id: str | None,
    ) -> AdminIpcResponse:
        requested_at_utc = self._clock()
        if method_name == "mint_profile":
            return client.mint_profile(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        if method_name == "modify_profile":
            return client.modify_profile(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        if method_name == "revoke_profile":
            return client.revoke_profile(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        if method_name == "mint_sop_template":
            return client.mint_sop_template(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        if method_name == "modify_sop_template":
            return client.modify_sop_template(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        if method_name == "revoke_sop_template":
            return client.revoke_sop_template(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        if method_name == "rotate_audit_key":
            return client.rotate_audit_key(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        if method_name == "triage_review_queue_item":
            return client.triage_review_queue_item(
                token,
                payload,
                request_id=request_id,
                requested_at_utc=requested_at_utc,
            )
        raise CliError(f"unsupported admin-service method: {method_name}")


def default_runtime() -> CliRuntime:
    return CliRuntime(admin_token_provider=admin_token_from_environment)


def admin_token_from_environment(
    environ: Mapping[str, str] | None = None,
) -> SignedAdminPrincipalToken:
    source = os.environ if environ is None else environ
    raw_token = source.get("CEV_ADMIN_TOKEN_JSON")
    if raw_token is None:
        raise CliError("CEV_ADMIN_TOKEN_JSON is required for admin CLI commands")
    try:
        decoded = json.loads(raw_token)
    except json.JSONDecodeError as exc:
        raise CliError("CEV_ADMIN_TOKEN_JSON must be valid JSON") from exc
    return SignedAdminPrincipalToken.from_payload(_json_object(decoded))


def parse_cli_payload(args: list[str]) -> JsonObject:
    payload: JsonObject = {}
    positionals: list[str] = []
    index = 0
    while index < len(args):
        raw = args[index]
        if not raw.startswith("--"):
            positionals.append(raw)
            index += 1
            continue
        key = raw[2:].replace("-", "_")
        if not key:
            raise CliError("empty option names are not supported")
        if index + 1 >= len(args) or args[index + 1].startswith("--"):
            _store_payload_value(payload, key, True)
            index += 1
            continue
        _store_payload_value(payload, key, _coerce_cli_value(args[index + 1]))
        index += 2
    if positionals:
        payload["args"] = positionals
    return payload


def typer_available() -> bool:
    return importlib.util.find_spec("typer") is not None


def command_help_text(command_name: str) -> str:
    spec = get_command_spec(command_name)
    transport = (
        f"AdminServiceClientPort:{spec.admin_method}"
        if spec.requires_admin_service
        else "configured public command handler"
    )
    return f"{spec.name}: {spec.description} Transport: {transport}."


def help_text() -> str:
    return "\n".join(
        (
            "cloning-expression-vector-design CLI",
            "",
            "Commands:",
            *[f"  {name}" for name in ALL_COMMAND_NAMES],
            "",
            "Pass command arguments as --key value pairs. Values may be JSON scalars or objects.",
        )
    )


def _store_payload_value(payload: JsonObject, key: str, value: object) -> None:
    existing = payload.get(key)
    if existing is None:
        payload[key] = value
        return
    if isinstance(existing, list):
        existing.append(value)
        return
    payload[key] = [existing, value]


def _coerce_cli_value(raw: str) -> object:
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    return cast(object, decoded)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise CliError("request_id must be a string when supplied")
    return value


def _json_object(raw: object) -> JsonObject:
    if not isinstance(raw, Mapping):
        raise CliError("admin token JSON must be an object")
    payload: JsonObject = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise CliError("admin token JSON keys must be strings")
        payload[key] = cast(object, value)
    return payload


def _datetime_to_wire(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


__all__ = [
    "AdminTokenProvider",
    "CliCommandResult",
    "CliError",
    "CliRuntime",
    "PublicCommandHandler",
    "admin_token_from_environment",
    "command_help_text",
    "default_runtime",
    "help_text",
    "parse_cli_payload",
    "typer_available",
]
