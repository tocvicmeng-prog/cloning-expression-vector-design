"""
module_id: tools.ci_gates.audit_append_port_only_check
file: tools/ci_gates/audit_append_port_only_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-313b
"""

from __future__ import annotations

import ast
from collections.abc import Iterable, Iterator
from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, read_text, run_gate

DEFAULT_BOUNDARY_ROOTS = (
    Path("src/app"),
    Path("src/engine"),
    Path("src/interface/api"),
    Path("src/interface/cli"),
    Path("src/interface/admin_service"),
    Path("src/adapter/ipc"),
)

FORBIDDEN_FROM_IMPORTS = {
    "adapter.persistence": {"SqliteAuditLog", "SqliteAuditLogWriter"},
    "adapter.persistence.sqlite_audit_log": {"SqliteAuditLog"},
    "adapter.persistence.sqlite_audit_log_writer": {"SqliteAuditLogWriter"},
    "tests.fakes.security.audit_append.brokers": {"FakeAuditBroker", "FakeAdminAuditBroker"},
}

FORBIDDEN_DIRECT_MODULES = {
    "adapter.persistence.sqlite_audit_log",
    "adapter.persistence.sqlite_audit_log_writer",
    "tests.fakes.security.audit_append.brokers",
}

FORBIDDEN_ATTRIBUTES = {
    "SqliteAuditLog",
    "SqliteAuditLogWriter",
    "FakeAuditBroker",
    "FakeAdminAuditBroker",
}


def audit_append_port_only_violations(
    root: Path,
    boundary_roots: Iterable[Path] = DEFAULT_BOUNDARY_ROOTS,
) -> tuple[str, ...]:
    violations: list[str] = []
    for path in _python_files(root, boundary_roots):
        violations.extend(_file_violations(root, path))
    return tuple(violations)


def check_audit_append_port_only(root: Path) -> GateResult:
    violations = audit_append_port_only_violations(root)
    if violations:
        return fail_gate(*violations)
    return pass_gate("engine and app code append audit entries only through audit append ports")


def main() -> int:
    return run_gate("audit-append-port-only-check", check_audit_append_port_only)


def _python_files(root: Path, boundary_roots: Iterable[Path]) -> Iterator[Path]:
    for boundary_root in boundary_roots:
        base = root / boundary_root
        if base.is_file() and base.suffix == ".py":
            yield base
        elif base.is_dir():
            yield from sorted(base.rglob("*.py"))


def _file_violations(root: Path, path: Path) -> tuple[str, ...]:
    relative_path = path.relative_to(root).as_posix()
    try:
        tree = ast.parse(read_text(path), filename=relative_path)
    except SyntaxError as exc:
        return (f"{relative_path}:{exc.lineno or 0}: syntax error blocks import scan",)

    module_aliases: dict[str, str] = {}
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound_name = alias.asname or alias.name.split(".", 1)[0]
                module_aliases[bound_name] = alias.name
                if alias.name in FORBIDDEN_DIRECT_MODULES:
                    violations.append(
                        f"{relative_path}:{node.lineno}: imports forbidden audit writer module "
                        f"{alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            forbidden_names = FORBIDDEN_FROM_IMPORTS.get(module, set())
            for alias in node.names:
                if alias.name == "*" and forbidden_names:
                    violations.append(
                        f"{relative_path}:{node.lineno}: wildcard import from forbidden audit "
                        f"module {module}"
                    )
                elif alias.name in forbidden_names:
                    violations.append(
                        f"{relative_path}:{node.lineno}: imports {module}.{alias.name} "
                        "instead of AuditAppendPort"
                    )
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            module_name = module_aliases.get(node.value.id)
            if (
                module_name in {"adapter.persistence", *FORBIDDEN_DIRECT_MODULES}
                and node.attr in FORBIDDEN_ATTRIBUTES
            ):
                violations.append(
                    f"{relative_path}:{node.lineno}: uses {module_name}.{node.attr} "
                    "instead of AuditAppendPort"
                )
    return tuple(violations)


if __name__ == "__main__":
    raise SystemExit(main())
