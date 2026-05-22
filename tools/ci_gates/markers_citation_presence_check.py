"""
module_id: tools.ci_gates.markers_citation_presence_check
file: tools/ci_gates/markers_citation_presence_check.py
task_id: T-415
lifecycle_state: informational
owning_task_id: T-415
architecture_refs: § 4.1 catalogue maintenance; § 9.1 v0.2 amendment
requirements_refs: FR-MARK-09, FR-MARK-11

Markers-citation-presence CI gate.

Validates that every marker in `catalogues/markers.yaml` carries a citation
block with grade in {A1, A2, A3, B1, B2} — grade C is rejected at the runtime
catalogue level (architect § 4.1 source-grade citation gate convention). Every
`working_concentrations[].citation` and (if present) `counter_selection.citation`
is also validated.

Lifecycle: `informational` at landing (T-415); promotes to `enforced` after T-410
lands the populated catalogues/markers.yaml (per joint plan § 8).

Behaviour on absent catalogue (v0.2 state — T-410 has not yet run):
returns PASS with "catalogue absent" message.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

MARKERS_YAML = Path("catalogues/markers.yaml")
ACCEPTABLE_GRADES = frozenset({"A1", "A2", "A3", "B1", "B2"})


def _check_citation(
    cite: object,
    where: str,
) -> list[str]:
    findings: list[str] = []
    if not isinstance(cite, dict):
        return [f"{where}: missing or non-object citation"]
    grade = cite.get("grade")
    if grade not in ACCEPTABLE_GRADES:
        findings.append(
            f"{where}: citation grade {grade!r} not in {sorted(ACCEPTABLE_GRADES)} (grade C is "
            "explicitly rejected for runtime catalogue entries)"
        )
    if not cite.get("text"):
        findings.append(f"{where}: citation missing `text`")
    if not cite.get("accessed"):
        findings.append(f"{where}: citation missing `accessed` date")
    return findings


def check_markers_citation_presence(root: Path) -> GateResult:
    markers_path = root / MARKERS_YAML
    if not markers_path.exists():
        return pass_gate(
            f"{MARKERS_YAML.as_posix()} not present yet (T-410 populates); gate vacuous at v0.2"
        )
    catalogue = yaml.safe_load(markers_path.read_text(encoding="utf-8")) or {}
    items = catalogue.get("items", [])
    if not isinstance(items, list) or not items:
        return pass_gate(f"{MARKERS_YAML.as_posix()} has no items yet — gate vacuous")
    findings: list[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append(f"{MARKERS_YAML.as_posix()}::items[{idx}]: not an object")
            continue
        marker_id = str(item.get("id", f"<item-{idx}>"))
        findings.extend(_check_citation(item.get("citation"), f"{marker_id}.citation"))
        wcs = item.get("working_concentrations", []) or []
        if isinstance(wcs, list):
            for wc_idx, wc in enumerate(wcs):
                if isinstance(wc, dict):
                    findings.extend(
                        _check_citation(
                            wc.get("citation"),
                            f"{marker_id}.working_concentrations[{wc_idx}].citation",
                        )
                    )
        cs = item.get("counter_selection")
        if isinstance(cs, dict):
            findings.extend(_check_citation(cs.get("citation"), f"{marker_id}.counter_selection.citation"))
    if findings:
        return fail_gate(*tuple(sorted(findings)))
    return pass_gate(
        f"all {len(items)} markers in {MARKERS_YAML.as_posix()} carry grade A1/A2/A3/B1/B2 citations"
    )


def main() -> int:
    return run_gate("markers-citation-presence-check", check_markers_citation_presence)


if __name__ == "__main__":
    raise SystemExit(main())
