"""
module_id: tools.ci_gates.host_marker_link_integrity_check
file: tools/ci_gates/host_marker_link_integrity_check.py
task_id: T-415
lifecycle_state: informational
owning_task_id: T-415
architecture_refs: § 9.1 v0.2 amendment; § 9.2 MarkersCataloguePort cross-link
requirements_refs: FR-HOST-15, FR-MARK-12

Host-marker link-integrity CI gate.

Validates that every `recommended_selection_markers[]` entry in
`catalogues/hosts.yaml` resolves to an existing marker id in
`catalogues/markers.yaml`. Also confirms each marker id matches the canonical
`^marker\\.[a-z0-9_]+$` pattern (the project validator does not enforce regex
patterns, so we check it here at CI time).

Lifecycle: `informational` at landing (T-415); promotes to `enforced` after both
T-410 (markers populated) and T-411 (new host records with linked markers) land.

Behaviour on absent or empty markers catalogue (v0.2 state):
- If catalogues/markers.yaml does not exist, but hosts.yaml has no
  `recommended_selection_markers[]` either: PASS (baseline).
- If hosts.yaml has any `recommended_selection_markers[]` but markers.yaml is
  absent: FAIL (host points to a catalogue that doesn't exist).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

HOSTS_YAML = Path("catalogues/hosts.yaml")
MARKERS_YAML = Path("catalogues/markers.yaml")
MARKER_ID_PATTERN = re.compile(r"^marker\.[a-z0-9_]+$")


def _load_marker_ids(markers_path: Path) -> tuple[set[str], list[str]]:
    """Return (id_set, findings). findings are non-empty if pattern violations exist."""
    if not markers_path.exists():
        return set(), []
    catalogue = yaml.safe_load(markers_path.read_text(encoding="utf-8")) or {}
    items = catalogue.get("items", [])
    if not isinstance(items, list):
        return set(), [f"{MARKERS_YAML.as_posix()}: items is not a list"]
    ids: set[str] = set()
    findings: list[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        marker_id = item.get("id")
        if not isinstance(marker_id, str):
            findings.append(f"{MARKERS_YAML.as_posix()}::items[{idx}]: missing string id")
            continue
        if not MARKER_ID_PATTERN.match(marker_id):
            findings.append(
                f"{MARKERS_YAML.as_posix()}::items[{idx}].id={marker_id!r}: does not match "
                f"{MARKER_ID_PATTERN.pattern!r}"
            )
        ids.add(marker_id)
    return ids, findings


def check_host_marker_link_integrity(root: Path) -> GateResult:
    hosts_path = root / HOSTS_YAML
    markers_path = root / MARKERS_YAML
    if not hosts_path.exists():
        return pass_gate(f"{HOSTS_YAML.as_posix()} not present — gate vacuous")
    hosts_catalogue = yaml.safe_load(hosts_path.read_text(encoding="utf-8")) or {}
    host_items = hosts_catalogue.get("items", []) or []
    if not isinstance(host_items, list):
        return fail_gate(f"{HOSTS_YAML.as_posix()}: items is not a list")

    marker_ids, marker_findings = _load_marker_ids(markers_path)

    findings: list[str] = list(marker_findings)
    hosts_with_links = 0
    total_link_count = 0
    for idx, host in enumerate(host_items):
        if not isinstance(host, dict):
            continue
        host_id = str(host.get("id", f"<host-{idx}>"))
        recommended = host.get("recommended_selection_markers", []) or []
        if not isinstance(recommended, list):
            findings.append(f"{host_id}.recommended_selection_markers is not a list")
            continue
        if not recommended:
            continue
        hosts_with_links += 1
        for link in recommended:
            if not isinstance(link, str):
                findings.append(f"{host_id}.recommended_selection_markers contains non-string {link!r}")
                continue
            total_link_count += 1
            if not MARKER_ID_PATTERN.match(link):
                findings.append(
                    f"{host_id}: marker link {link!r} does not match {MARKER_ID_PATTERN.pattern!r}"
                )
            elif not markers_path.exists():
                findings.append(
                    f"{host_id}: marker link {link!r} cannot resolve — {MARKERS_YAML.as_posix()} "
                    "does not exist yet (T-410 populates)"
                )
            elif link not in marker_ids:
                findings.append(
                    f"{host_id}: marker link {link!r} does not resolve to any id in "
                    f"{MARKERS_YAML.as_posix()}"
                )

    if findings:
        return fail_gate(*tuple(sorted(findings)))
    if hosts_with_links == 0:
        return pass_gate(
            f"no hosts in {HOSTS_YAML.as_posix()} carry recommended_selection_markers[] yet "
            "(T-411 + T-408a populate); gate vacuous at v0.2"
        )
    return pass_gate(
        f"all {total_link_count} marker links across {hosts_with_links} hosts resolve cleanly"
    )


def main() -> int:
    return run_gate("host-marker-link-integrity-check", check_host_marker_link_integrity)


if __name__ == "__main__":
    raise SystemExit(main())
