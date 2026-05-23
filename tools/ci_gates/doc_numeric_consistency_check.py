"""
module_id:           tools.ci_gates.doc_numeric_consistency_check
file:                tools/ci_gates/doc_numeric_consistency_check.py
task_id:             audit-fix-M4
lifecycle_state:     enforced
owning_task_id:      audit-fix-M4

Cross-doc numeric consistency CI gate.

The 2026-05-23 collaborative audit (Architect § 7 doc integrity + Orchestrator
§ 0 issue #1) found that the v0.2 Enrichment Amendment had three different
"total task card" counts in circulation across load-bearing documents:
- `CODING_AGENDA.md` line 7 prose said "92 task cards" (correct)
- `CODING_AGENDA.md` line 14 changelog said "EXPECTED_TOTAL 71 → 91" (stale)
- `ARCHITECTURE.md § 9.7` said "9 task cards" for Phase 4.2 (off by 1)
- `docs/handover/.../development_plan.md` § 4 said "9 in Phase 4.2... 91 task cards" (stale)
- `agenda_consistency_check.py::EXPECTED_TOTAL = 92` (authoritative)

The actual landed implementation matches the checker (92/51). The drift was
silent because nothing cross-checks doc-to-doc consistency.

This gate fixes that:
1. Read the authoritative values from `tools/agenda_consistency_check.py`:
   - `EXPECTED_TOTAL` (currently 92)
   - port_manifest.yaml `canonical_port_count` (currently 51)
2. Search load-bearing docs for numeric tokens that should match.
3. Fail with a structured drift report if any disagree.

Scope of doc-numeric-consistency checks at v0.2.1 landing:
- Total active-task-card count appears in: `CODING_AGENDA.md`, `TASK_BOARD.md`,
  `ARCHITECTURE.md § 9`, `docs/release/v0.2.0_release_notes.md`,
  `docs/handover/2026-05-23_host_marker_ml_corpus_development_plan.md`.
- Canonical port count appears in: same docs + `docs/port_manifest.yaml`.

The gate uses targeted regex patterns rather than blanket "find every number
in every doc" to avoid false positives on years/dates/PMIDs/etc. The patterns
match phrases like "NNN task cards", "NNN active task headings", "EXPECTED_TOTAL N",
"NNN canonical ports", "Total: NNN canonical ports".

Lifecycle: `enforced` from landing. Drift would have prevented the v0.2.0
release's release notes from being internally consistent had this gate been
in place; landing it now closes the loop.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

import yaml  # type: ignore[import-untyped]

# v0.2.1 audit fix M4 — import the authoritative constants directly so the gate
# fails the moment they drift from the docs (vs the docs drifting from the constants).
from tools.agenda_consistency_check import EXPECTED_TOTAL
from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

# Documents that participate in the numeric-consistency contract. Each entry is
# (relative_path, scopes_described) where scopes_described is a short label used
# in failure messages.
WATCHED_DOCS: tuple[tuple[str, str], ...] = (
    ("CODING_AGENDA.md", "preamble + changelog block + section headings"),
    ("TASK_BOARD.md", "cumulative dashboard + global progress + milestones"),
    ("ARCHITECTURE.md", "§ 9 V0.2 Enrichment Amendment narrative"),
    ("docs/release/v0.2.0_release_notes.md", "Architecture changes section"),
    (
        "docs/handover/2026-05-23_host_marker_ml_corpus_development_plan.md",
        "§ 4 phase + task-card design",
    ),
)

# Patterns that legitimately reference the active-task-card total. Each match's
# captured number must equal EXPECTED_TOTAL.
TASK_TOTAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(\d{2,4})\s+active\s+(?:Section\s+2\s+)?task\s+headings?", re.IGNORECASE),
    re.compile(r"(\d{2,4})\s+active\s+task\s+cards?", re.IGNORECASE),
    re.compile(r"Post-v0\.2\s+totals?:\s+\*\*?(\d{2,4})\s+task\s+cards?", re.IGNORECASE),
    re.compile(
        r"post-v0\.2:\s*71\s*\+\s*(\d{1,2})\s*=\s*\*\*?(\d{2,4})\s+task\s+cards?", re.IGNORECASE
    ),
    re.compile(r"EXPECTED_TOTAL\s*[=:]\s*(\d{2,4})\b"),
    re.compile(
        r"`EXPECTED_TOTAL`\s*(?:in\s+`tools/agenda_consistency_check\.py`)?:?\s*71\s*→\s*\*\*?(\d{2,4})",
        re.IGNORECASE,
    ),
)

# Patterns that reference the canonical port count.
PORT_COUNT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(\d{1,3})\s+canonical\s+ports?", re.IGNORECASE),
    re.compile(r"canonical_port_count:\s*(\d{1,3})\b"),
    re.compile(r"Total:\s*(\d{1,3})\s+canonical\s+ports?", re.IGNORECASE),
)


def _load_canonical_port_count(root: Path) -> int:
    """Read the authoritative port count from docs/port_manifest.yaml."""
    manifest = yaml.safe_load((root / "docs" / "port_manifest.yaml").read_text(encoding="utf-8"))
    if not isinstance(manifest, Mapping):
        raise ValueError("docs/port_manifest.yaml must be a mapping")
    count = manifest.get("canonical_port_count")
    if not isinstance(count, int):
        raise ValueError(
            f"docs/port_manifest.yaml::canonical_port_count must be an int; got {count!r}"
        )
    return count


_HISTORICAL_MARKERS = re.compile(
    r"\b(was|previously|baseline|historical|prior|earlier|stale|drift|memory|"
    r"speculation|speculative|out-of-scope|out\s+of\s+scope|"
    r"v0\.1\.0|v1\.[0-9]+|B[2-9][A-Z]?-\d+|"
    r"reconciled|originally\s+said|originally\s+specified|originally|"
    r"pre-T-\d+|never\s+landed|jointly\s+plan-era|"
    r"audit\s+fix\s+M4|fix\s+M4|→|->|⇒)\b",
    re.IGNORECASE,
)
_QUOTED_CONTEXT = re.compile(
    r'"[^"]*\d+\s+(?:canonical\s+ports?|task\s+(?:cards?|headings?))[^"]*"', re.IGNORECASE
)


def _is_historical_context(text: str, match: re.Match[str], window: int = 200) -> bool:
    """Return True if the match is inside a sentence that flags historical/stale content."""
    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    surrounding = text[start:end]
    if _HISTORICAL_MARKERS.search(surrounding):
        return True
    if _QUOTED_CONTEXT.search(text[match.start() - 5 : match.end() + 5]):
        return True
    # Check if the line itself contains a delta arrow indicating "was X → now Y".
    line_start = text.rfind("\n", 0, match.start()) + 1
    line_end = text.find("\n", match.end())
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    return bool(re.search(r"\d+\s*(?:→|->|⇒)\s*\d+", line))


def check_doc_numeric_consistency(root: Path) -> GateResult:
    failures: list[str] = []
    canonical_port_count = _load_canonical_port_count(root)

    for rel_path, scope_label in WATCHED_DOCS:
        path = root / rel_path
        if not path.exists():
            failures.append(f"{rel_path}: missing (expected at {scope_label})")
            continue
        text = path.read_text(encoding="utf-8")

        # Task-total drift.
        for pattern in TASK_TOTAL_PATTERNS:
            for match in pattern.finditer(text):
                groups = [int(g) for g in match.groups() if g and g.isdigit()]
                if not groups:
                    continue
                claimed = groups[-1]
                if claimed != EXPECTED_TOTAL and not _is_historical_context(text, match):
                    line_no = text[: match.start()].count("\n") + 1
                    failures.append(
                        f"{rel_path}:{line_no}: doc claims {claimed} task cards/headings "
                        f"but authoritative EXPECTED_TOTAL = {EXPECTED_TOTAL}. "
                        f"Match: {match.group(0)!r}. Scope: {scope_label}."
                    )

        # Port-count drift.
        for pattern in PORT_COUNT_PATTERNS:
            for match in pattern.finditer(text):
                groups = [int(g) for g in match.groups() if g and g.isdigit()]
                if not groups:
                    continue
                claimed = groups[-1]
                if claimed != canonical_port_count and not _is_historical_context(text, match):
                    line_no = text[: match.start()].count("\n") + 1
                    failures.append(
                        f"{rel_path}:{line_no}: doc claims {claimed} canonical ports "
                        f"but authoritative canonical_port_count = {canonical_port_count}. "
                        f"Match: {match.group(0)!r}. Scope: {scope_label}."
                    )

    if failures:
        return fail_gate(
            f"Doc-to-doc numeric drift detected ({len(failures)} site(s)):",
            *failures,
            "",
            "Authoritative sources:",
            f"  - tools/agenda_consistency_check.py::EXPECTED_TOTAL = {EXPECTED_TOTAL}",
            f"  - docs/port_manifest.yaml::canonical_port_count = {canonical_port_count}",
            "Update the offending doc(s) to match — or, if the authoritative value is wrong,",
            "update agenda_consistency_check.py + port_manifest.yaml FIRST.",
        )
    return pass_gate(
        f"doc-numeric-consistency: all watched docs agree with EXPECTED_TOTAL = {EXPECTED_TOTAL} "
        f"and canonical_port_count = {canonical_port_count}"
    )


def main() -> int:
    return run_gate("doc-numeric-consistency-check", check_doc_numeric_consistency)


if __name__ == "__main__":
    raise SystemExit(main())
