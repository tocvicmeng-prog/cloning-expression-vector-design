"""
module_id:           tools.ci.markers_auxotrophic_sanity
file:                tools/ci/markers_auxotrophic_sanity.py
task_id:             T-408
architecture_refs:   § 9.1 v0.2 Enrichment Amendment delta summary
requirements_refs:   FR-MARK-04
purity:              tool (script; reads catalogues/markers.yaml; emits warnings)

Auxotrophic-sanity CI extension landed at T-408.

Background: per FR-MARK-04, yeast auxotrophic markers (URA3, LEU2, HIS3, TRP1,
MET15/17, LYS2) carry sentinel `concentration_ugml: {min: 0, typical: 0, max: 0}`
because selection is by auxotrophic dropout medium, not by μg/mL concentration.

The schema (schemas/markers.schema.json) accepts non-zero concentrations on
auxotrophic markers because the sentinel-zero convention is editorial discipline,
not a structural constraint. This script enforces the editorial discipline:
warns when class:yeast_auxotrophic is combined with non-zero concentration_ugml.

WARN-only at v0.2 (matches the `markers-citation-presence-check` lifecycle in
T-415); promoted to fail-on-detection if the false-positive rate is low after
T-410 lands the populated catalogue.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
MARKERS_YAML = ROOT / "catalogues" / "markers.yaml"


def find_auxotrophic_with_nonzero_concentration(
    catalogue: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    """Return (marker_id, working_concentration_entry) tuples that violate FR-MARK-04.

    A violation is: class == "yeast_auxotrophic" AND any working_concentrations[].concentration_ugml
    field (min/typical/max) is non-zero.
    """
    violations: list[tuple[str, dict[str, Any]]] = []
    for item in catalogue.get("items", []):
        if item.get("class") != "yeast_auxotrophic":
            continue
        marker_id = item.get("id", "<unknown>")
        for wc in item.get("working_concentrations", []):
            cug = wc.get("concentration_ugml", {})
            if (cug.get("min") or 0) > 0 or (cug.get("typical") or 0) > 0 or (cug.get("max") or 0) > 0:
                violations.append((marker_id, wc))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="WARN on auxotrophic markers with non-zero concentration_ugml (FR-MARK-04).",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Fail the build on violations. v0.2 lifecycle is WARN-only; --enforce flips to fail.",
    )
    parser.add_argument(
        "--markers-yaml",
        type=Path,
        default=MARKERS_YAML,
        help="Path to catalogues/markers.yaml (default: project root).",
    )
    args = parser.parse_args(argv)

    if not args.markers_yaml.exists():
        # T-410 has not yet populated catalogues/markers.yaml — the check is a no-op
        # against an absent catalogue. The check is meaningful only once content lands.
        print(
            f"markers_auxotrophic_sanity: catalogues/markers.yaml does not exist yet "
            "(T-410 populates content). Treating as pass."
        )
        return 0

    catalogue = yaml.safe_load(args.markers_yaml.read_text(encoding="utf-8"))
    violations = find_auxotrophic_with_nonzero_concentration(catalogue)

    if not violations:
        print(
            "markers_auxotrophic_sanity: pass — no auxotrophic markers carry non-zero "
            "concentration_ugml."
        )
        return 0

    print(
        "markers_auxotrophic_sanity: WARNING — "
        f"{len(violations)} auxotrophic marker entries carry non-zero concentration_ugml "
        "(FR-MARK-04 expects sentinel {min:0, typical:0, max:0}):",
        file=sys.stderr,
    )
    for marker_id, wc in violations:
        cug = wc.get("concentration_ugml", {})
        print(
            f"  - {marker_id}: host_class={wc.get('host_class')}, "
            f"min={cug.get('min')}, typical={cug.get('typical')}, max={cug.get('max')}",
            file=sys.stderr,
        )
    if args.enforce:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
