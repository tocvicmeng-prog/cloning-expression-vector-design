"""
module_id: interface.cli
file: src/interface/cli/entrypoint.py
task_id: T-1101

Command-line runner and optional Typer application builder.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Sequence
from typing import Any, TextIO, cast

from interface.cli.commands import ALL_COMMAND_NAMES
from interface.cli.runtime import (
    CliCommandResult,
    CliError,
    CliRuntime,
    command_help_text,
    default_runtime,
    help_text,
    parse_cli_payload,
    typer_available,
)

MODULE_ID = "interface.cli"
OWNING_TASKS = ("T-1101",)


def build_app(runtime: CliRuntime | None = None) -> object:
    try:
        typer_module = cast(Any, importlib.import_module("typer"))
    except ModuleNotFoundError as exc:
        raise CliError("Typer is not installed; install the project with the cli extra") from exc
    app = typer_module.Typer(
        add_completion=False,
        help="Cloning expression vector design command-line interface.",
    )
    resolved_runtime = runtime or default_runtime()
    context_settings = {"allow_extra_args": True, "ignore_unknown_options": True}
    for command_name in ALL_COMMAND_NAMES:
        callback = _make_typer_callback(command_name, resolved_runtime, typer_module)
        callback.__name__ = command_name.replace("-", "_")
        callback.__annotations__ = {"ctx": typer_module.Context, "return": None}
        app.command(name=command_name, context_settings=context_settings)(callback)
    return cast(object, app)


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    runtime: CliRuntime | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    resolved_runtime = runtime or default_runtime()

    if not args or args[0] in {"-h", "--help"}:
        out.write(help_text() + "\n")
        return 0

    command_name = args[0]
    if len(args) > 1 and args[1] in {"-h", "--help"}:
        try:
            out.write(command_help_text(command_name) + "\n")
        except ValueError as exc:
            _write_error(command_name, exc, err)
            return 2
        return 0

    try:
        payload = parse_cli_payload(args[1:])
        result = resolved_runtime.run_command(command_name, payload)
    except (CliError, ValueError) as exc:
        _write_error(command_name, exc, err)
        return 2

    out.write(result.canonical_json() + "\n")
    return result.exit_code


def main(argv: Sequence[str] | None = None) -> int:
    if argv is not None or not typer_available():
        return run_cli(argv)
    typer_entry = cast(Callable[[], None], build_app())
    typer_entry()
    return 0


def _make_typer_callback(
    command_name: str,
    runtime: CliRuntime,
    typer_module: Any,
) -> Callable[[object], None]:
    def callback(ctx: object) -> None:
        raw_args = getattr(ctx, "args", ())
        args = [command_name, *[str(item) for item in raw_args]]
        exit_code = run_cli(args, runtime=runtime)
        if exit_code != 0:
            raise typer_module.Exit(exit_code)

    return callback


def _write_error(command_name: str, exc: Exception, stream: TextIO) -> None:
    result = CliCommandResult(
        command=command_name,
        status="error",
        payload={},
        exit_code=2,
        message=str(exc),
    )
    stream.write(result.canonical_json() + "\n")


__all__ = [
    "build_app",
    "main",
    "run_cli",
]
