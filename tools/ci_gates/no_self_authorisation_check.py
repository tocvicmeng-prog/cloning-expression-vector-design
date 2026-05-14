"""
module_id: tools.ci_gates.no_self_authorisation_check
file: tools/ci_gates/no_self_authorisation_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-1302
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, read_text, run_gate
from tools.ci_gates.audit_append_port_only_check import audit_append_port_only_violations
from tools.ci_gates.no_direct_admin_handler_import_check import (
    direct_admin_handler_import_violations,
)
from tools.ci_gates.sop_template_admin_port_only_check import (
    sop_template_admin_port_violations,
)

REQUIRED_SOURCE_TOKENS = {
    Path("src/app/admin_action_handler.py"): (
        "_require_admin",
        "_require_sop_template_admin",
        "AuthorisationAttemptDenied",
        "DeveloperBootstrapPrincipal",
    ),
    Path("src/interface/admin_service/handlers.py"): (
        "BOOTSTRAP_ALLOWED_VERBS",
        "_require_authority",
        "AdminServiceAuthorisationError",
        "DeveloperBootstrapPrincipal",
    ),
    Path("src/interface/cli/runtime.py"): (
        "AdminServiceClientPort",
        "admin_client",
    ),
    Path("src/interface/api/runtime.py"): (
        "AdminServiceClientPort",
        "admin_client",
    ),
}

REQUIRED_TEST_TOKENS = {
    Path("tests/app/admin_action_handler/test_admin_action_handler.py"): (
        "test_user_and_reviewer_are_denied_with_governance_event",
        "test_developer_bootstrap_is_one_shot_and_ordinary_developer_is_rejected",
    ),
    Path("tests/app/sop_template/test_admin_handler_sop_templates.py"): (
        "test_user_and_reviewer_cannot_write_sop_templates",
    ),
    Path("tests/app/review_queue/test_cli_api_cannot_resolve_without_admin_service.py"): (
        "test_cli_api_paths_have_no_user_facing_resolution_surface",
    ),
    Path("tests/interface/admin_service/test_admin_credentials_routed.py"): (
        "test_admin_credentials_routed",
    ),
    Path("tests/interface/admin_service/test_developer_denied_post_bootstrap.py"): (
        "test_developer_denied_post_bootstrap",
    ),
    Path("tests/interface/admin_service/test_reviewer_credentials_denied.py"): (
        "test_reviewer_credentials_denied",
    ),
    Path("tests/interface/admin_service/test_user_credentials_denied.py"): (
        "test_user_credentials_denied",
    ),
    Path("tests/uat/adversarial/helpers.py"): (
        "run_admin_command_direct_handler_import_rejected",
        "run_admin_service_unauthenticated",
        "run_audit_service_dual_writer_chain_integrity",
        "run_developer_post_bootstrap_denied",
        "run_reviewer_escalation",
        "run_self_elevation",
    ),
}


def check_no_self_authorisation(root: Path) -> GateResult:
    messages: list[str] = []
    messages.extend(direct_admin_handler_import_violations(root))
    messages.extend(audit_append_port_only_violations(root))
    messages.extend(sop_template_admin_port_violations(root))
    messages.extend(_missing_tokens(root, REQUIRED_SOURCE_TOKENS, "source"))
    messages.extend(_missing_tokens(root, REQUIRED_TEST_TOKENS, "test evidence"))
    if messages:
        return fail_gate(*messages)
    return pass_gate("self-authorisation and admin-boundary bypass surfaces are covered")


def main() -> int:
    return run_gate("no-self-authorisation-check", check_no_self_authorisation)


def _missing_tokens(
    root: Path,
    required: dict[Path, tuple[str, ...]],
    label: str,
) -> tuple[str, ...]:
    messages: list[str] = []
    for relative_path, tokens in required.items():
        path = root / relative_path
        if not path.is_file():
            messages.append(f"{relative_path.as_posix()} missing required {label} file")
            continue
        text = read_text(path)
        for token in tokens:
            if token not in text:
                messages.append(f"{relative_path.as_posix()} missing {label} token: {token}")
    return tuple(messages)


if __name__ == "__main__":
    raise SystemExit(main())
