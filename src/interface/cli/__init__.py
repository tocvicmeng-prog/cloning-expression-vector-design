"""
module_id: interface.cli
file: src/interface/cli/__init__.py
task_id: T-1101

Public CLI surface for the local-first design platform.
"""

from __future__ import annotations

from interface.cli.commands import (
    ADMIN_COMMAND_NAMES,
    ADMIN_COMMANDS,
    ALL_COMMAND_NAMES,
    PUBLIC_COMMAND_NAMES,
    PUBLIC_COMMANDS,
    CliCommandSpec,
    get_command_spec,
)
from interface.cli.entrypoint import build_app, main, run_cli
from interface.cli.runtime import (
    AdminTokenProvider,
    CliCommandResult,
    CliError,
    CliRuntime,
    PublicCommandHandler,
    admin_token_from_environment,
    command_help_text,
    default_runtime,
    help_text,
    parse_cli_payload,
    typer_available,
)

MODULE_ID = "interface.cli"
OWNING_TASKS = ("T-1101",)

__all__ = [
    "ADMIN_COMMANDS",
    "ADMIN_COMMAND_NAMES",
    "ALL_COMMAND_NAMES",
    "PUBLIC_COMMANDS",
    "PUBLIC_COMMAND_NAMES",
    "AdminTokenProvider",
    "CliCommandResult",
    "CliCommandSpec",
    "CliError",
    "CliRuntime",
    "PublicCommandHandler",
    "admin_token_from_environment",
    "build_app",
    "command_help_text",
    "default_runtime",
    "get_command_spec",
    "help_text",
    "main",
    "parse_cli_payload",
    "run_cli",
    "typer_available",
]
