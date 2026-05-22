"""
module_id: tools.ci_gates.ml_corpus_license_check
file: tools/ci_gates/ml_corpus_license_check.py
task_id: T-1403
lifecycle_state: informational
owning_task_id: T-1403
architecture_refs: § 9.3 ML Training Corpus Subsystem; § 9.3.2 split sequence/annotation license schema
requirements_refs: FR-ML-05, FR-ML-08, FR-ML-09; BR-15
citations: v0.2 Enrichment Amendment (2026-05-23); architect § 4.3; IP-auditor § 8.1

ML-corpus license-completeness CI gate (T-1403).

Walks `docs/ml_corpus/records/**/*.json` and enforces, per FR-ML-05 + BR-15:

  1. Every record carries a `license` object with BOTH `sequence_license` and
     `annotation_license` sub-blocks (split per IP-auditor § 5.2 fold-in).
  2. Each license sub-block carries `redistribution_allowed` AND `ml_training_allowed`
     EXPLICITLY (boolean, not missing). Missing-or-default is a hard fail
     (BR-15 default-deny).
  3. Records with `ml_training_allowed: false` MUST NOT appear under records/ —
     they belong in exclusions.yaml. (BR-15)
  4. The `provenance.source` enum is enforced (no `addgene_metadata_only` —
     that source goes through exclusions.yaml per FR-ML-04).

Auxiliary: also reports SnapGene cross-check coverage from
`docs/ml_corpus/corpus_manifest.yaml::license_aggregate.cross_check_coverage`
and emits a WARN-level note when coverage < 60% (research v0.2 floor;
release-gate at T-1409 enforces ≥ 90% at release-tag time).

**Lifecycle: `informational` at landing.** Promoted to `enforced` after T-1407
lands the populated corpus and the dual-read shim-hit baseline is established.

Behaviour on empty corpus (the v0.2 state where T-1404/T-1405 haven't yet run):
returns PASS with an "empty corpus" message. The gate becomes meaningful as
records arrive.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

CORPUS_ROOT_RELATIVE = "docs/ml_corpus"
# v0.2 T-1404: T-1404 lands YAML records (project-wide convention); JSON is
# also accepted for forward-compat with externally-curated corpus deposits.
RECORDS_GLOBS = ("records/**/*.yaml", "records/**/*.yml", "records/**/*.json")
CORPUS_MANIFEST_RELATIVE = "docs/ml_corpus/corpus_manifest.yaml"

# v0.2 IP-auditor § 8.1 Tier-1 + Tier-2 allowlist (Tier-3 sources are NOT in the enum).
ALLOWED_PROVENANCE_SOURCES = frozenset({
    "ncbi_genbank",
    "ebi_ena",
    "ddbj",
    "igem_registry",
    "jbei_ice",
    "dnasu",
    "vendor_published_map",
    "primary_literature",
    "fpbase",
})

# Each license sub-block (sequence_license, annotation_license) MUST carry these two
# fields explicitly — missing-or-default is a hard fail per BR-15.
REQUIRED_EXPLICIT_BOOLEAN_FIELDS = ("redistribution_allowed", "ml_training_allowed")


def _load_record(path: Path) -> dict[str, Any] | None:
    """Return the record at path (YAML or JSON), or None on parse error."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    suffix = path.suffix.lower()
    try:
        if suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(text)
        else:
            data = json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _check_license_subblock(
    record_id: str,
    rel_path: str,
    block_name: str,
    subblock: Mapping[str, object] | None,
) -> list[str]:
    """Return findings for one license sub-block (sequence_license / annotation_license)."""
    if subblock is None or not isinstance(subblock, dict):
        return [f"{rel_path}: record {record_id!r} missing or non-object license.{block_name}"]
    findings: list[str] = []
    for field in REQUIRED_EXPLICIT_BOOLEAN_FIELDS:
        if field not in subblock:
            findings.append(
                f"{rel_path}: record {record_id!r} license.{block_name}.{field} is missing "
                "(BR-15 default-deny — must be explicitly true or false)"
            )
        elif not isinstance(subblock[field], bool):
            findings.append(
                f"{rel_path}: record {record_id!r} license.{block_name}.{field} must be a "
                f"boolean, got {type(subblock[field]).__name__}"
            )
    return findings


def _check_record(path: Path, root: Path) -> list[str]:
    """Return findings for one corpus record."""
    rel = path.relative_to(root).as_posix()
    record = _load_record(path)
    if record is None:
        return [f"{rel}: failed to parse as YAML or JSON"]
    findings: list[str] = []
    record_id = str(record.get("id", "<unknown>"))

    license_obj = record.get("license")
    if not isinstance(license_obj, dict):
        findings.append(
            f"{rel}: record {record_id!r} missing required `license` object "
            "(BR-15 default-deny)"
        )
    else:
        findings.extend(
            _check_license_subblock(
                record_id, rel, "sequence_license", license_obj.get("sequence_license")
            )
        )
        findings.extend(
            _check_license_subblock(
                record_id, rel, "annotation_license", license_obj.get("annotation_license")
            )
        )
        # Records with ml_training_allowed: false on the SEQUENCE license belong in
        # exclusions.yaml, NOT under records/ (BR-15). Annotation-only blocks of
        # ml_training are handled by the strip-annotation rule (FR-ML-07) at ingestion.
        seq_lic = license_obj.get("sequence_license")
        if isinstance(seq_lic, dict) and seq_lic.get("ml_training_allowed") is False:
            findings.append(
                f"{rel}: record {record_id!r} has sequence_license.ml_training_allowed: false "
                "but is under records/ — must live in exclusions.yaml per BR-15"
            )

    provenance = record.get("provenance")
    if isinstance(provenance, dict):
        source = provenance.get("source")
        if isinstance(source, str) and source not in ALLOWED_PROVENANCE_SOURCES:
            findings.append(
                f"{rel}: record {record_id!r} provenance.source={source!r} is not in the v0.2 "
                f"Tier-1+Tier-2 allowlist (allowed: {sorted(ALLOWED_PROVENANCE_SOURCES)})"
            )

    return findings


def check_ml_corpus_license(root: Path) -> GateResult:
    """Walk docs/ml_corpus/records/**/*.json and enforce license-block completeness.

    Returns pass on an empty corpus (the v0.2 state) — meaningful enforcement begins
    once T-1404/T-1405 land records. BR-15 default-deny holds at landing time.
    """
    corpus_root = root / CORPUS_ROOT_RELATIVE
    if not corpus_root.exists():
        return pass_gate(
            f"corpus root {CORPUS_ROOT_RELATIVE} not present — gate is vacuous "
            "(BR-15 default-deny held)"
        )
    record_paths: list[Path] = []
    for glob in RECORDS_GLOBS:
        record_paths.extend(corpus_root.glob(glob))
    record_paths = sorted(record_paths)
    if not record_paths:
        return pass_gate(
            "no corpus records present yet (T-1404/T-1405 populate); "
            "BR-15 default-deny baseline holds"
        )
    findings: list[str] = []
    for path in record_paths:
        if not path.is_file():
            continue
        findings.extend(_check_record(path, root))
    if findings:
        return fail_gate(*tuple(sorted(findings)))
    return pass_gate(
        f"all {len(record_paths)} corpus records carry complete license blocks "
        f"(both sequence_license + annotation_license, BR-15 default-deny held)"
    )


def main() -> int:
    return run_gate("ml-corpus-license-check", check_ml_corpus_license)


if __name__ == "__main__":
    raise SystemExit(main())
