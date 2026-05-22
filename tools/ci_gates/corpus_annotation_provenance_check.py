"""
module_id: tools.ci_gates.corpus_annotation_provenance_check
file: tools/ci_gates/corpus_annotation_provenance_check.py
task_id: T-1408
lifecycle_state: informational
owning_task_id: T-1408
architecture_refs: § 9.3 ML Training Corpus Subsystem
requirements_refs: BR-15; UR-14
citations: v0.2 Enrichment Amendment (2026-05-23); IP-auditor IPQ-9

IPQ-9 corpus-annotation-provenance heuristic CI gate.

Scans `docs/ml_corpus/records/**/*.json` annotation `qualifiers` for long string
patterns matching known vendor-manual phrasing (Invitrogen, Novagen, Stratagene,
Takara/Clontech, Promega, NEB, Lucigen, SnapGene). Catches accidental verbatim
ingestion of vendor-authored annotation text.

**Lifecycle: `informational` at v0.2.** Per joint plan IPQ-9 resolution:
"lands `informational` at v0.2; observe FP rate; tune patterns before promoting
to `enforced` in v0.3 after FP-rate observation."

Behaviour on empty corpus (v0.2 state): PASS with "empty corpus" message.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

CORPUS_ROOT_RELATIVE = "docs/ml_corpus"
# v0.2 T-1404: T-1404 lands YAML records; JSON also accepted.
RECORDS_GLOBS = ("records/**/*.yaml", "records/**/*.yml", "records/**/*.json")

# Vendor-manual phrasing patterns. These are heuristic — they target text patterns
# that are common in vendor manuals but NOT in primary scientific literature. False
# positives are tolerable at v0.2 (informational mode); pattern tuning happens in
# v0.3 after FP-rate observation.
VENDOR_PHRASING_PATTERNS = (
    re.compile(r"For research use only\b", re.IGNORECASE),
    re.compile(r"Not for use in (?:diagnostic|therapeutic|human|clinical)", re.IGNORECASE),
    re.compile(r"This product is sold under license", re.IGNORECASE),
    re.compile(r"\bcatalog(?:ue)? number\b", re.IGNORECASE),
    re.compile(r"©\s*\d{4}.*(?:Invitrogen|Thermo Fisher|Novagen|Merck|Stratagene|Agilent|Takara|Clontech|Promega|NEB|New England Biolabs|Lucigen|SnapGene|Dotmatics)", re.IGNORECASE),
    re.compile(r"(?:Invitrogen|Thermo Fisher|Novagen|Stratagene|Agilent|Takara|Clontech|Promega|NEB|Lucigen|SnapGene|Dotmatics).*\b(?:all rights reserved|trademark|TM|\(R\)|®)\b", re.IGNORECASE),
)


def _scan_qualifier_string(s: str) -> list[str]:
    """Return pattern names that match this qualifier string."""
    hits: list[str] = []
    for pattern in VENDOR_PHRASING_PATTERNS:
        if pattern.search(s):
            hits.append(pattern.pattern)
    return hits


def _scan_record(path: Path, root: Path) -> list[str]:
    """Return findings for one corpus record."""
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yaml", ".yml"}:
            record = yaml.safe_load(text)
        else:
            record = json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError, UnicodeDecodeError):
        return []  # malformed records are caught by ml-corpus-license-check (T-1403)
    if not isinstance(record, dict):
        return []
    record_id = str(record.get("id", "<unknown>"))
    findings: list[str] = []
    annotations = record.get("annotation", [])
    if not isinstance(annotations, list):
        return findings
    for idx, annotation in enumerate(annotations):
        if not isinstance(annotation, dict):
            continue
        qualifiers = annotation.get("qualifiers", {})
        if not isinstance(qualifiers, dict):
            continue
        for key, value in qualifiers.items():
            if not isinstance(value, str):
                continue
            hits = _scan_qualifier_string(value)
            for pattern_name in hits:
                findings.append(
                    f"{rel}: record {record_id!r} annotation[{idx}].qualifiers[{key!r}] "
                    f"matches vendor-manual phrasing pattern {pattern_name!r}"
                )
    return findings


def check_corpus_annotation_provenance(root: Path) -> GateResult:
    """Walk docs/ml_corpus/records/**/*.json checking annotation qualifiers for vendor phrasing.

    Heuristic-only. Returns pass on empty corpus.
    """
    corpus_root = root / CORPUS_ROOT_RELATIVE
    if not corpus_root.exists():
        return pass_gate(
            f"corpus root {CORPUS_ROOT_RELATIVE} not present — gate is vacuous"
        )
    record_paths: list[Path] = []
    for glob in RECORDS_GLOBS:
        record_paths.extend(corpus_root.glob(glob))
    record_paths = sorted(record_paths)
    if not record_paths:
        return pass_gate("no corpus records present yet — gate vacuous at v0.2")
    findings: list[str] = []
    for path in record_paths:
        if not path.is_file():
            continue
        findings.extend(_scan_record(path, root))
    if findings:
        return fail_gate(*tuple(sorted(findings)))
    return pass_gate(
        f"all {len(record_paths)} corpus records' annotation qualifiers clear of vendor-manual phrasing"
    )


def main() -> int:
    return run_gate("corpus-annotation-provenance-check", check_corpus_annotation_provenance)


if __name__ == "__main__":
    raise SystemExit(main())
