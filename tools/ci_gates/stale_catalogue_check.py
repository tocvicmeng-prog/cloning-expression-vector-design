"""
module_id: tools.ci_gates.stale_catalogue_check
file: tools/ci_gates/stale_catalogue_check.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-401
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from adapter.catalogue import (
    CatalogueValidationError,
    catalogue_yaml_paths,
    load_catalogue,
    schema_for_catalogue,
)
from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate


def check_catalogues(root: Path) -> GateResult:
    today = datetime.now(UTC).date()
    failures: list[str] = []
    for path in catalogue_yaml_paths(root / "catalogues"):
        try:
            document = load_catalogue(path, schema_for_catalogue(path, root / "schemas"))
        except CatalogueValidationError as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")
            continue
        if document.maintenance.is_stale(today):
            failures.append(f"{path.relative_to(root)}: maintenance metadata is stale")
    if failures:
        return fail_gate(*failures)
    return pass_gate("all catalogue maintenance windows are current")


def main() -> int:
    return run_gate("stale-catalogue-check", check_catalogues)


if __name__ == "__main__":
    raise SystemExit(main())
