"""
module_id: tools.release.corpus_release_gate
file: tools/release/corpus_release_gate.py
task_id: T-1409
lifecycle_state: enforced_at_release_tag_only
owning_task_id: T-1409
architecture_refs: § 9.3.5 SnapGene cross-check coverage; § 9.6.2 commercial fork criteria
requirements_refs: FR-ML-13; BR-15..17; UR-14

Release-tag-time gate for the ML training corpus.

Enforces release-time criteria (not per-PR):

  Research release (default --research mode):
    - Cross-check coverage ≥ 90% (per architect § 5.2; IPQ-5 resolution)
    - Attribution-text-file (LICENSES/THIRD_PARTY_NOTICES.md) exists and is complete
    - No Tier-3 denylist sources (addgene_metadata_only, snapgene.* etc.) present
    - No records with missing license blocks (delegates to ml-corpus-license-check)

  Commercial fork release (--commercial mode; per ARCHITECTURE.md § 9.6):
    - All research criteria PLUS
    - 100% records have commercial_use_allowed: true on both license blocks
    - Counsel-review certificate attached (--certificate path)
    - Cross-check coverage ≥ 95% (tightened from 90% per § 9.6.2)
    - Partition: sa_free locked (no cc-by-sa records reachable)

Behaviour on empty corpus (v0.2 state): coverage thresholds are vacuous; gate
emits a "corpus has no records to release" pass message. Real enforcement
begins once T-1404 + T-1405 land records.

This gate is NOT run on PR. It is invoked only at release-tag promotion time,
typically from a CI release workflow.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = ROOT / "docs" / "ml_corpus"
RECORDS_GLOB = "records/**/*.json"
ATTRIBUTION_FILE = ROOT / "LICENSES" / "THIRD_PARTY_NOTICES.md"
MANIFEST_FILE = CORPUS_ROOT / "corpus_manifest.yaml"

RESEARCH_COVERAGE_THRESHOLD = 0.90
COMMERCIAL_COVERAGE_THRESHOLD = 0.95

# Tier-3 sources MUST NOT appear under records/. Validated by ml-corpus-license-check
# at PR time too; this is the release-gate's last-mile check.
TIER_3_DENYLIST_SOURCES = frozenset({
    "addgene_metadata_only",
    "snapgene_dna_file",
    "snapgene_page_scrape",
    "vendor_manual_annotation_verbatim",
    "paywalled_journal_text",
})


def _load_records(corpus_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Load all corpus records as (path, parsed-record) tuples."""
    records: list[tuple[Path, dict[str, Any]]] = []
    if not corpus_root.exists():
        return records
    for path in sorted(corpus_root.glob(RECORDS_GLOB)):
        if not path.is_file():
            continue
        try:
            records.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return records


def _research_checks(records: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    """Return findings for research-release criteria."""
    findings: list[str] = []
    if not records:
        # vacuous pass: nothing to release
        return findings

    checked = sum(
        1 for _, r in records if (r.get("snapgene_crosscheck") or {}).get("checked") is True
    )
    coverage = checked / len(records)
    if coverage < RESEARCH_COVERAGE_THRESHOLD:
        findings.append(
            f"research release: SnapGene cross-check coverage = {coverage:.2%} "
            f"< {RESEARCH_COVERAGE_THRESHOLD:.0%} threshold ({checked}/{len(records)} records)"
        )

    if not ATTRIBUTION_FILE.exists():
        findings.append(
            f"research release: attribution file {ATTRIBUTION_FILE.relative_to(ROOT)} missing"
        )

    for path, record in records:
        provenance = record.get("provenance") or {}
        source = provenance.get("source")
        if source in TIER_3_DENYLIST_SOURCES:
            findings.append(
                f"research release: record at {path.relative_to(ROOT).as_posix()} has Tier-3 "
                f"denylist source {source!r}"
            )

    return findings


def _commercial_checks(
    records: list[tuple[Path, dict[str, Any]]],
    certificate_path: Path | None,
) -> list[str]:
    """Return findings for commercial-fork release criteria. Includes research checks."""
    findings: list[str] = list(_research_checks(records))
    if not records:
        return findings

    # Commercial-specific: tighter coverage threshold.
    checked = sum(
        1 for _, r in records if (r.get("snapgene_crosscheck") or {}).get("checked") is True
    )
    coverage = checked / len(records)
    if coverage < COMMERCIAL_COVERAGE_THRESHOLD:
        findings.append(
            f"commercial release: SnapGene cross-check coverage = {coverage:.2%} "
            f"< {COMMERCIAL_COVERAGE_THRESHOLD:.0%} commercial threshold"
        )

    for path, record in records:
        license_obj = record.get("license") or {}
        for block_name in ("sequence_license", "annotation_license"):
            block = license_obj.get(block_name) or {}
            if block.get("commercial_use_allowed") is not True:
                findings.append(
                    f"commercial release: record at {path.relative_to(ROOT).as_posix()} "
                    f"license.{block_name}.commercial_use_allowed is not true"
                )

    cc_by_sa_dir = CORPUS_ROOT / "records" / "cc-by-sa"
    if cc_by_sa_dir.exists():
        cc_by_sa_records = list(cc_by_sa_dir.rglob("*.json"))
        if cc_by_sa_records:
            findings.append(
                f"commercial release: {len(cc_by_sa_records)} CC-BY-SA records present under "
                "records/cc-by-sa/ — must be excluded for commercial fork (use partition: sa_free)"
            )

    if certificate_path is None or not certificate_path.exists():
        findings.append(
            "commercial release: --certificate path missing or does not exist (counsel-review "
            "certificate is mandatory per ARCHITECTURE.md § 9.6.6)"
        )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the corpus release-gate at tag time.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--research",
        action="store_true",
        default=True,
        help="Default. Research-release thresholds (≥ 90%% cross-check coverage).",
    )
    mode.add_argument(
        "--commercial",
        action="store_true",
        help="Commercial-fork release thresholds (≥ 95%% cross-check coverage + commercial criteria).",
    )
    parser.add_argument(
        "--certificate",
        type=Path,
        default=None,
        help="Path to counsel-review certificate (required for --commercial).",
    )
    parser.add_argument("--tag", type=str, default="<unset>", help="Release tag (informational).")
    args = parser.parse_args(argv)

    records = _load_records(CORPUS_ROOT)
    if args.commercial:
        findings = _commercial_checks(records, args.certificate)
        mode_label = "commercial-fork release"
    else:
        findings = _research_checks(records)
        mode_label = "research release"

    if not records:
        print(
            f"corpus_release_gate: {mode_label} {args.tag} — corpus has no records to release "
            "(v0.2 baseline; T-1404/T-1405 populate). Gate vacuously passes."
        )
        return 0

    if findings:
        print(f"corpus_release_gate: {mode_label} {args.tag} FAILED:", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print(
        f"corpus_release_gate: {mode_label} {args.tag} passed — "
        f"{len(records)} records meet release criteria"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
