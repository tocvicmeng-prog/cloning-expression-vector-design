"""
module_id: tools.ci_gates.source_grade_citation_check
file: tools/ci_gates/source_grade_citation_check.py
task_id: T-204
lifecycle_state: informational
owning_task_id: T-401
"""

from __future__ import annotations

from pathlib import Path

from adapter.catalogue import (
    CatalogueValidationError,
    catalogue_yaml_paths,
    find_citations,
    load_catalogue,
    parse_graded_citation,
    schema_for_catalogue,
)
from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

_RELEASE_GRADES = {"A1", "A2", "A3", "B1", "B2"}


def check_citations(root: Path) -> GateResult:
    failures: list[str] = []
    for path in catalogue_yaml_paths(root / "catalogues"):
        try:
            document = load_catalogue(path, schema_for_catalogue(path, root / "schemas"))
            citations = find_citations(document.payload)
        except CatalogueValidationError as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")
            continue
        if not citations:
            failures.append(f"{path.relative_to(root)}: no graded citations found")
            continue
        for index, citation_payload in enumerate(citations, start=1):
            citation = parse_graded_citation(citation_payload)
            if citation.grade in _RELEASE_GRADES:
                continue
            if not citation_payload.get("corroborator"):
                failures.append(
                    f"{path.relative_to(root)} citation {index}: grade C requires corroborator"
                )
    if failures:
        return fail_gate(*failures)
    return pass_gate("all catalogue citations have release-acceptable grades")


def main() -> int:
    return run_gate("source-grade-citation-check", check_citations)


if __name__ == "__main__":
    raise SystemExit(main())
