"""
module_id: tools.ci_gates.no_domain_impurity_check
file: tools/ci_gates/no_domain_impurity_check.py
task_id: T-204
lifecycle_state: enforced
owning_task_id: T-502
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

DOMAIN_FORBIDDEN_IMPORTS = frozenset({"adapter", "app", "engine", "interface"})
ENGINE_FORBIDDEN_IMPORTS = frozenset({"adapter", "app", "interface"})


def check_no_domain_impurity(root: Path) -> GateResult:
    messages: list[str] = []
    messages.extend(
        _check_package_imports(
            root / "src" / "domain",
            source_package="domain",
            forbidden=DOMAIN_FORBIDDEN_IMPORTS,
        )
    )
    messages.extend(
        _check_package_imports(
            root / "src" / "engine",
            source_package="engine",
            forbidden=ENGINE_FORBIDDEN_IMPORTS,
        )
    )
    if messages:
        return fail_gate(*tuple(sorted(messages)))
    return pass_gate("domain and engine imports respect purity boundaries")


def _check_package_imports(
    package_root: Path,
    *,
    source_package: str,
    forbidden: frozenset[str],
) -> tuple[str, ...]:
    findings: list[str] = []
    for path in sorted(package_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for imported_root in _imported_roots(node):
                if imported_root in forbidden:
                    findings.append(
                        f"{_display_path(path)}: {source_package} must not import {imported_root}"
                    )
    return tuple(findings)


def _imported_roots(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, ast.Import):
        return tuple(alias.name.partition(".")[0] for alias in node.names)
    if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
        return (node.module.partition(".")[0],)
    return ()


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> int:
    return run_gate("no-domain-impurity-check", check_no_domain_impurity)


if __name__ == "__main__":
    raise SystemExit(main())
