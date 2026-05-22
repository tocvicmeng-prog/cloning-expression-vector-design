"""
module_id: tools.ci_gates.snapgene_pipeline_scan
file: tools/ci_gates/snapgene_pipeline_scan.py
task_id: T-1406
lifecycle_state: enforced
owning_task_id: T-1406
architecture_refs: § 9.3.5 SnapGene cross-check — process-only artefact; BR-16 tooling boundary
requirements_refs: BR-16; UR-14
citations: v0.2 Enrichment Amendment (2026-05-23)

BR-16 defensive default-deny scanner.

Per ARCHITECTURE.md § 9.3.5 + REQUIREMENTS.md BR-16 (v0.2 Enrichment Amendment):

    No pipeline this project runs may access `snapgene.com` via any non-browser
    tool. SnapGene is index-only, accessed by humans in browsers, with cross-check
    results recorded in `docs/ml_corpus/crosscheck_log.yaml`. Any attempt to
    introduce automated SnapGene access into a build pipeline MUST be detected
    and blocked by CI.

This gate walks the project's pipeline-relevant file set looking for invocations
of common HTTP-fetch tools (`curl`, `wget`, `requests`, `httpx`, `urllib`,
`aiohttp`, `playwright`, `selenium`, MCP web-fetch) that mention `snapgene.com`
on the same line. Any match fails the gate.

Files in scope (NOT docs/**/*.md or src/**, which serve different purposes):
- `.github/workflows/*.{yml,yaml}` — CI workflow scripts
- `tools/**/*.py` — build / release tools
- `Dockerfile`, `Dockerfile.*` — container build instructions
- `mkdocs.yml` — docs build config
- `pyproject.toml` — Python build config
- `.importlinter` — import-linter config
- Top-level `*.sh`, `*.bat`, `*.ps1` — shell scripts
- `Makefile` — make config (if present)
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

# Regex captures common fetch-tool invocations that reference snapgene.com on the same line.
# Each alternative requires the tool-name token AND a snapgene.com reference within a small window.
# Case-insensitive so attempts like `Requests.GET` or `Curl` are caught.
# The patterns target the canonical invocation forms used in CI workflows + Python scripts.
SNAPGENE_DOMAIN = r"snapgene\.com"
FORBIDDEN_PATTERNS = (
    re.compile(rf"\bcurl\b[^\n]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\bwget\b[^\n]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\brequests\.(?:get|post|put|delete|head|options|patch|request)\([^)]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\bhttpx\.[a-z_]+\([^)]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\burllib(?:\.request)?\.urlopen\([^)]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\baiohttp[^\n]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\bplaywright[^\n]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\bselenium[^\n]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\bmcp_[a-z_]+[^\n]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\bwebfetch[^\n]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
    re.compile(rf"\bfetch\([^)]*{SNAPGENE_DOMAIN}", re.IGNORECASE),
)

# File globs in scope — pipeline / build / CI scripts only.
# Documentation (docs/**/*.md) and source code (src/**/*.py, tests/**/*.py)
# are intentionally OUT of scope. Documentation discusses snapgene.com legitimately;
# `src/` is shielded by the ml-corpus-is-not-runtime import-linter contract;
# `tests/` may use snapgene.com URLs as test fixtures (string data, not requests).
IN_SCOPE_GLOBS = (
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    "tools/**/*.py",
    "Dockerfile",
    "Dockerfile.*",
    "mkdocs.yml",
    "pyproject.toml",
    ".importlinter",
    "*.sh",
    "*.bat",
    "*.ps1",
    "Makefile",
)

# Self-reference exception: this file itself MUST contain `snapgene.com` (as a regex
# pattern target) and we'd flag ourselves. Exclude this file from the scan.
SELF_EXCLUDE = (
    "tools/ci_gates/snapgene_pipeline_scan.py",
)


def _scan_file(path: Path, root: Path) -> tuple[str, ...]:
    """Return findings (relative path + matched pattern) for a single file, or () if clean."""
    rel = path.relative_to(root).as_posix()
    if rel in SELF_EXCLUDE:
        return ()
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return ()
    findings: list[str] = []
    for pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0)
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            findings.append(f"{rel}: forbidden snapgene.com fetch invocation: {snippet!r}")
    return tuple(findings)


def check_snapgene_pipeline_scan(root: Path) -> GateResult:
    """Scan in-scope pipeline files for snapgene.com fetch invocations.

    BR-16 defensive default-deny — no automated access to snapgene.com from any
    pipeline this project runs.
    """
    findings: list[str] = []
    seen: set[Path] = set()
    for glob_pattern in IN_SCOPE_GLOBS:
        for path in sorted(root.glob(glob_pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            findings.extend(_scan_file(path, root))
    if findings:
        return fail_gate(*tuple(sorted(findings)))
    return pass_gate(
        "no forbidden snapgene.com fetch invocations in pipeline files (BR-16 default-deny holds)"
    )


def main() -> int:
    return run_gate("snapgene-pipeline-scan", check_snapgene_pipeline_scan)


if __name__ == "__main__":
    raise SystemExit(main())
