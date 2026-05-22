"""
module_id:           tools.ci_gates.override_log_check
file:                tools/ci_gates/override_log_check.py
task_id:             T-1404
lifecycle_state:     informational
owning_task_id:      T-1404 (backlog Rec-4: corpus completion strategies, BR-16 cross-check pass scaffolding)
architecture_refs:   ARCHITECTURE.md § 9.6.4 Fork-Readiness Memorandum
requirements_refs:   BR-16 (NORMATIVE)
citations:           docs/handover/2026-05-23_corpus_completion_strategies.md Rec-4

NORMATIVE override-log enforcement gate.

Walks `docs/ml_corpus/records/**/*.yaml` and enforces, per Backlog Rec-4:

  1.  Any corpus record whose `snapgene_crosscheck.checked` is `true` MUST be
      referenced by at least one entry in `docs/ml_corpus/override_log.yaml`
      with `override_type: snapgene_cross_check_pass` and `batch_outcome:
      approved`.

  2.  Override-log entries MUST carry every required field
      (batch_id, override_type, batch_records, proposed_at, approval_date,
      approval_owner, normative_section, rationale, delta_from_normative,
      batch_outcome). Missing fields are a hard fail.

  3.  Override-log entries with `approval_date: pending` MUST NOT have any
      record in their `batch_records` flipped to `checked: true`. (Approval
      must precede the flip — Rec-4 workflow step 3.)

Lifecycle: `informational` at landing. Promote to `enforced` after the first
real cross-check batch lands and the workflow has proven itself.

Behaviour on empty corpus or empty override_log (the v0.2 state where 0/111
records are `checked: true`): returns PASS — the gate is vacuous.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

CORPUS_RECORDS_ROOT = Path("docs/ml_corpus/records")
OVERRIDE_LOG_PATH = Path("docs/ml_corpus/override_log.yaml")
REQUIRED_ENTRY_FIELDS = (
    "batch_id",
    "override_type",
    "batch_records",
    "proposed_at",
    "approval_date",
    "approval_owner",
    "normative_section",
    "rationale",
    "delta_from_normative",
    "batch_outcome",
)
VALID_OUTCOMES = frozenset({"pending", "approved", "rejected", "partial"})
VALID_OVERRIDE_TYPES = frozenset({
    "snapgene_cross_check_pass",
    "addgene_depositor_side",
    "vendor_proprietary_sequence",
    "curator_backtranslation",
})


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError):
        return None


def _collect_checked_records(root: Path) -> dict[str, Path]:
    """Map record id -> relative path for every record with snapgene_crosscheck.checked: true."""
    checked: dict[str, Path] = {}
    for record_path in root.rglob("*.yaml"):
        record = _load_yaml(record_path)
        if not isinstance(record, dict):
            continue
        crosscheck = record.get("snapgene_crosscheck", {})
        if not isinstance(crosscheck, dict):
            continue
        if crosscheck.get("checked") is True:
            record_id = str(record.get("id", record_path.name))
            checked[record_id] = record_path
    return checked


def _validate_entry(entry: Mapping[str, Any], idx: int) -> list[str]:
    """Return findings for a single override-log entry."""
    findings: list[str] = []
    for field in REQUIRED_ENTRY_FIELDS:
        if field not in entry:
            findings.append(
                f"override_log.yaml entries[{idx}]: missing required field {field!r}"
            )
    override_type = entry.get("override_type")
    if isinstance(override_type, str) and override_type not in VALID_OVERRIDE_TYPES:
        findings.append(
            f"override_log.yaml entries[{idx}]: override_type={override_type!r} "
            f"not in valid set {sorted(VALID_OVERRIDE_TYPES)}"
        )
    outcome = entry.get("batch_outcome")
    if isinstance(outcome, str) and outcome not in VALID_OUTCOMES:
        findings.append(
            f"override_log.yaml entries[{idx}]: batch_outcome={outcome!r} "
            f"not in valid set {sorted(VALID_OUTCOMES)}"
        )
    batch_records = entry.get("batch_records")
    if batch_records is not None and not isinstance(batch_records, list):
        findings.append(
            f"override_log.yaml entries[{idx}]: batch_records must be a list, "
            f"got {type(batch_records).__name__}"
        )
    return findings


def check_override_log(root: Path) -> GateResult:
    corpus_root = root / CORPUS_RECORDS_ROOT
    log_path = root / OVERRIDE_LOG_PATH
    if not corpus_root.exists():
        return pass_gate(
            f"{CORPUS_RECORDS_ROOT.as_posix()} not present — gate vacuous"
        )

    checked_records = _collect_checked_records(corpus_root)
    log_data = _load_yaml(log_path) if log_path.exists() else None

    # Empty corpus + empty log = vacuous pass
    if not checked_records and (not log_data or not log_data.get("entries")):
        return pass_gate(
            "no records carry snapgene_crosscheck.checked: true and override_log "
            "carries no entries; gate vacuous (v0.2 baseline state)"
        )

    findings: list[str] = []

    if not isinstance(log_data, dict):
        if checked_records:
            return fail_gate(
                f"{OVERRIDE_LOG_PATH.as_posix()} missing or malformed but "
                f"{len(checked_records)} record(s) carry snapgene_crosscheck.checked: true; "
                "Rec-4 requires every checked record to have an approval log entry"
            )
        return pass_gate(
            f"{OVERRIDE_LOG_PATH.as_posix()} missing but no checked records exist; "
            "gate vacuous"
        )

    entries = log_data.get("entries", []) or []
    if not isinstance(entries, list):
        return fail_gate(
            f"{OVERRIDE_LOG_PATH.as_posix()}: entries must be a list, "
            f"got {type(entries).__name__}"
        )

    # Validate every entry's shape
    approved_record_ids: set[str] = set()
    pending_record_ids: set[str] = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.append(
                f"override_log.yaml entries[{idx}]: must be a mapping, "
                f"got {type(entry).__name__}"
            )
            continue
        findings.extend(_validate_entry(entry, idx))
        batch_records = entry.get("batch_records") or []
        outcome = entry.get("batch_outcome")
        approval_date = entry.get("approval_date")
        if outcome == "approved" and approval_date and approval_date != "pending":
            for rid in batch_records:
                approved_record_ids.add(str(rid))
        if approval_date == "pending":
            for rid in batch_records:
                pending_record_ids.add(str(rid))

    # Every record with `checked: true` MUST be in an approved batch
    for record_id, record_path in checked_records.items():
        if record_id not in approved_record_ids:
            findings.append(
                f"{record_path.relative_to(root).as_posix()}: record {record_id!r} "
                "carries snapgene_crosscheck.checked: true but is NOT covered by an "
                "approved override_log entry (Rec-4 requires per-batch approval before flip)"
            )

    # Records in PENDING batches MUST NOT yet be flipped to `checked: true`
    for record_id in pending_record_ids:
        if record_id in checked_records:
            findings.append(
                f"override_log.yaml: record {record_id!r} is in a pending batch but "
                "already carries snapgene_crosscheck.checked: true (approval must "
                "precede the flip per Rec-4 workflow step 3)"
            )

    if findings:
        return fail_gate(*tuple(sorted(findings)))
    return pass_gate(
        f"override_log invariants hold: {len(entries)} batch entries, "
        f"{len(checked_records)} cross-checked record(s) all covered by approved entries"
    )


def main() -> int:
    return run_gate("override-log-check", check_override_log)


if __name__ == "__main__":
    raise SystemExit(main())
