"""
module_id: tools.ci_gates.no_direct_admin_handler_import_check
file: tools/ci_gates/no_direct_admin_handler_import_check.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-204
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, read_text, run_gate

FORBIDDEN_MODULE = "app.admin_action_handler"
FORBIDDEN_APP_ATTRIBUTE = "admin_action_handler"
DEFAULT_BOUNDARY_ROOTS = (Path("src/interface/cli"), Path("src/interface/api"))


def direct_admin_handler_import_violations(
    root: Path,
    boundary_roots: Iterable[Path] = DEFAULT_BOUNDARY_ROOTS,
) -> tuple[str, ...]:
    violations: list[str] = []
    for boundary_root in boundary_roots:
        base = root / boundary_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            violations.extend(_file_violations(root, path))
    return tuple(violations)


def check_no_direct_admin_handler_imports(root: Path) -> GateResult:
    violations = direct_admin_handler_import_violations(root)
    if violations:
        return fail_gate(*violations)
    return pass_gate("CLI/API code paths do not import AdminActionHandler directly")


def main() -> int:
    return run_gate("no-direct-admin-handler-import-check", check_no_direct_admin_handler_imports)


def _file_violations(root: Path, path: Path) -> tuple[str, ...]:
    relative_path = path.relative_to(root).as_posix()
    try:
        tree = ast.parse(read_text(path), filename=relative_path)
    except SyntaxError as exc:
        return (f"{relative_path}:{exc.lineno or 0}: syntax error blocks import scan",)

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == FORBIDDEN_MODULE:
                    violations.append(f"{relative_path}:{node.lineno}: imports {FORBIDDEN_MODULE}")
        elif isinstance(node, ast.ImportFrom):
            if node.module == FORBIDDEN_MODULE:
                violations.append(f"{relative_path}:{node.lineno}: imports {FORBIDDEN_MODULE}")
            if node.module == "app" and any(
                alias.name == FORBIDDEN_APP_ATTRIBUTE for alias in node.names
            ):
                violations.append(
                    f"{relative_path}:{node.lineno}: imports app.{FORBIDDEN_APP_ATTRIBUTE}"
                )
    return tuple(violations)


if __name__ == "__main__":
    raise SystemExit(main())
