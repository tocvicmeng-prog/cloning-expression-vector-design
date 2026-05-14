"""
module_id: interface.cli
file: src/interface/cli/commands.py
task_id: T-1101

Command registry for the Phase 11 command-line interface.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.types.admin_ipc import AdminServiceVerb

MODULE_ID = "interface.cli"
OWNING_TASKS = ("T-1101",)


@dataclass(frozen=True, slots=True)
class CliCommandSpec:
    name: str
    category: str
    description: str
    admin_verb: AdminServiceVerb | None = None
    admin_method: str | None = None
    admin_operation: str | None = None

    @property
    def requires_admin_service(self) -> bool:
        return self.admin_verb is not None


PUBLIC_COMMANDS: tuple[CliCommandSpec, ...] = (
    CliCommandSpec("new", "design", "Create a design session."),
    CliCommandSpec("open", "design", "Open a design session."),
    CliCommandSpec("validate", "design", "Validate a design session."),
    CliCommandSpec("compile", "design", "Compile a design session."),
    CliCommandSpec("screen", "screening", "Run screening for a design session."),
    CliCommandSpec("export", "export", "Create an export bundle."),
    CliCommandSpec("library", "catalogue", "Query the local part library."),
    CliCommandSpec("replay", "audit", "Replay a design session from events."),
    CliCommandSpec("audit", "audit", "Read audit records through the configured audit surface."),
    CliCommandSpec("rule-index", "catalogue", "List validation rule catalogue metadata."),
    CliCommandSpec("list-sessions", "design", "List known design sessions."),
    CliCommandSpec(
        "acknowledge-advisory",
        "governance",
        "Record a signed advisory acknowledgement.",
    ),
    CliCommandSpec("decline-advisory", "governance", "Record an advisory decline."),
    CliCommandSpec("escalate-advisory", "governance", "Escalate an advisory for review."),
    CliCommandSpec("status", "dashboard", "Show CLI and backend readiness."),
)

ADMIN_COMMANDS: tuple[CliCommandSpec, ...] = (
    CliCommandSpec(
        "admin-mint",
        "admin",
        "Mint an authorisation profile.",
        AdminServiceVerb.MINT_PROFILE,
        "mint_profile",
    ),
    CliCommandSpec(
        "admin-modify",
        "admin",
        "Modify an authorisation profile.",
        AdminServiceVerb.MODIFY_PROFILE,
        "modify_profile",
    ),
    CliCommandSpec(
        "admin-revoke",
        "admin",
        "Revoke an authorisation profile.",
        AdminServiceVerb.REVOKE_PROFILE,
        "revoke_profile",
    ),
    CliCommandSpec(
        "admin-mint-sop-template",
        "admin",
        "Mint a signed SOP template.",
        AdminServiceVerb.MINT_SOP_TEMPLATE,
        "mint_sop_template",
    ),
    CliCommandSpec(
        "admin-modify-sop-template",
        "admin",
        "Modify a signed SOP template.",
        AdminServiceVerb.MODIFY_SOP_TEMPLATE,
        "modify_sop_template",
    ),
    CliCommandSpec(
        "admin-revoke-sop-template",
        "admin",
        "Revoke a signed SOP template.",
        AdminServiceVerb.REVOKE_SOP_TEMPLATE,
        "revoke_sop_template",
    ),
    CliCommandSpec(
        "audit-key-rotate",
        "admin",
        "Rotate the audit-key archive.",
        AdminServiceVerb.ROTATE_AUDIT_KEY,
        "rotate_audit_key",
    ),
    CliCommandSpec(
        "submit-extension-request",
        "review_queue",
        "Submit an authorisation extension request through the admin-service boundary.",
        AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM,
        "triage_review_queue_item",
        "submit_extension_request",
    ),
    CliCommandSpec(
        "list-review-queue",
        "review_queue",
        "List pending review-queue items through the admin-service boundary.",
        AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM,
        "triage_review_queue_item",
        "list_review_queue",
    ),
    CliCommandSpec(
        "triage-request",
        "review_queue",
        "Triage a review-queue item.",
        AdminServiceVerb.TRIAGE_REVIEW_QUEUE_ITEM,
        "triage_review_queue_item",
        "triage_request",
    ),
)

COMMANDS_BY_NAME = {spec.name: spec for spec in (*PUBLIC_COMMANDS, *ADMIN_COMMANDS)}
PUBLIC_COMMAND_NAMES = tuple(spec.name for spec in PUBLIC_COMMANDS)
ADMIN_COMMAND_NAMES = tuple(spec.name for spec in ADMIN_COMMANDS)
ALL_COMMAND_NAMES = tuple(COMMANDS_BY_NAME)


def get_command_spec(command_name: str) -> CliCommandSpec:
    try:
        return COMMANDS_BY_NAME[command_name]
    except KeyError as exc:
        raise ValueError(f"unknown CLI command: {command_name}") from exc


__all__ = [
    "ADMIN_COMMANDS",
    "ADMIN_COMMAND_NAMES",
    "ALL_COMMAND_NAMES",
    "COMMANDS_BY_NAME",
    "PUBLIC_COMMANDS",
    "PUBLIC_COMMAND_NAMES",
    "CliCommandSpec",
    "get_command_spec",
]
