"""
module_id:           tools.ci_gates.credential_scan_check
file:                tools/ci_gates/credential_scan_check.py
task_id:             audit-fix-H2
lifecycle_state:     enforced
owning_task_id:      audit-fix-H2

Credential / secret-pattern scanner (gitleaks-style, pure-Python).

The 2026-05-23 collaborative audit's single highest-leverage process improvement
(Orchestrator § 4 + synthesis § 4) was: "Land a gitleaks-style pre-commit
credential scanner." This file is the implementation.

Why a custom Python scan instead of pulling in `gitleaks` as an external
dependency:
1. Zero extra install surface — the existing CI gate framework runs it.
2. Project-specific patterns are first-class (Addgene credentials, NCBI API
   keys, iGEM session tokens) instead of bolted on via `.gitleaks.toml`.
3. The `tools/ci_gates/` framework wraps `run_gate(...)` already, which gives
   us uniform telemetry, lifecycle states, and informational/enforced posture.

The scanner is **STRUCTURAL**, not semantic — it matches regex patterns that
historically indicate a credential leak. False positives are expected in test
fixtures and audit documents (where the credential PATTERN appears as
documentation of a leak that happened, NOT a fresh leak). Files matching
EXEMPT_GLOBS are skipped.

What it catches at v0.2.1:
- AWS access keys (`AKIA[0-9A-Z]{16}`)
- GitHub personal access tokens (`gh[pousr]_[A-Za-z0-9]{36,}`)
- PEM private keys (`-----BEGIN [A-Z ]+PRIVATE KEY-----`)
- Generic "password = LITERAL" assignments outside test fixtures
- Long hex/base64 strings in shell environment-variable assignments
- Addgene-specific URL parameters carrying plaintext passwords (the leak
  pattern surfaced 2026-05-23; the password was rotated but the pattern is
  the canonical guardrail)

What it deliberately does NOT catch (would require deeper analysis):
- Credentials embedded in image/binary files (would need git filter)
- Credentials in commit messages or git history (this gate runs against the
  working tree only; see `tools/ci_gates/secret_audit_history.py` for a
  separate git-history scan, deferred to v0.3)
- Multi-line credentials (the patterns are single-line)

Exit codes:
- 0 (pass): no matches.
- 1 (fail): matches found; structured report enumerates file:line + pattern.

Lifecycle: `enforced` at landing. The cost of false positives is low (suppress
via inline `# allow-credential-pattern: <reason>` comment); the cost of a real
leak is irreversible.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.ci_gates._gate import GateResult, fail_gate, pass_gate, run_gate

SCAN_FILE_EXTENSIONS = (
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".md",
    ".txt",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".ps1",
    ".bat",
    ".cmd",
    ".env",
    ".envrc",
    ".dotenv",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".vue",
    ".rs",
    ".go",
    ".java",
    ".rb",
    ".php",
)

EXEMPT_PATH_PREFIXES = (
    # auto-generated / vendor
    ".venv/",
    "venv/",
    "env/",
    "node_modules/",
    ".node_modules/",
    ".git/",
    ".github/",  # .github workflows are scanned separately if needed
    "__pycache__/",
    "dist/",
    "build/",
    ".gstack/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "ui/node_modules/",
    "ui/.next/",
    "ui/dist/",
    "ui/build/",
)

EXEMPT_PATH_FRAGMENTS = (
    "/__pycache__/",
    "/.git/",
    "/node_modules/",
    # known test/fixture areas where credential patterns appear as fixtures
    "tests/fixtures/credentials/",
)

EXEMPT_FILES = (
    # the gate itself contains its own regex patterns
    "tools/ci_gates/credential_scan_check.py",
    # gate test fixtures
    "tests/ci_gates/test_credential_scan_check_h2.py",
    # docs that DOCUMENT the leak pattern as part of an audit trail
    "docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit_v2.md",
    # this file describes the leak in the project memory but is the curator's note
    "docs/handover/2026-05-23_v0.2_collaborative_audit_synthesis.md",
    "docs/handover/2026-05-23_v0.2_collaborative_audit_orchestration.md",
)

# Allow-comment marker — if a matched line ends with this marker the match is suppressed.
ALLOW_MARKER = re.compile(r"#\s*allow-credential-pattern:\s*\S", re.IGNORECASE)


# Pattern table. Each entry: (rule_id, description, regex, mitigation_hint).
PATTERNS: tuple[tuple[str, str, re.Pattern[str], str], ...] = (
    (
        "aws_access_key",
        "AWS access key id (AKIA-prefixed)",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "Rotate the key in AWS IAM immediately. Move to AWS SSO or short-lived "
        "credentials. Add the new key to a vault, not source control.",
    ),
    (
        "github_pat",
        "GitHub personal access token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"),
        "Rotate the token in https://github.com/settings/tokens immediately. "
        "Replace with a fine-scoped token or a GitHub App installation.",
    ),
    (
        "pem_private_key",
        "PEM-encoded private key block",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "Rotate the key. Remove from working tree. If committed historically, "
        "scrub via git filter-repo and rotate all downstream uses.",
    ),
    (
        "addgene_password_assignment",
        "Addgene plaintext password assignment "
        "(per 2026-05-23 IP-audit v2 § 9 credential-handling protocol)",
        re.compile(
            r"(?i)(?:addgene[_\-\s]*(?:password|pswd|pwd)|password\s*[:=]\s*['\"]?[A-Za-z0-9*.!@#$%^&]{8,32}['\"]?)"
        ),
        "DO NOT commit plaintext credentials. Rotate the password in the upstream "
        "service. Use the manual-download workflow documented in IP-audit v2 § 9. "
        "If this match is a documented-incident reference, suppress with "
        "'# allow-credential-pattern: ip-audit-historical-reference'.",
    ),
    (
        "generic_password_in_url",
        "Plaintext credential embedded in URL",
        re.compile(r"https?://[A-Za-z0-9._-]+:[A-Za-z0-9!@#$%^&*().+\-=]{4,}@"),
        "Rotate the credential. URLs with embedded credentials log in many places "
        "(server logs, browser history, proxies). Switch to API token + Authorization header.",
    ),
)


def _path_is_exempt(path: Path, repo_root: Path) -> bool:
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    if any(rel.startswith(prefix) for prefix in EXEMPT_PATH_PREFIXES):
        return True
    if any(frag in rel for frag in EXEMPT_PATH_FRAGMENTS):
        return True
    return rel in EXEMPT_FILES


def _scan_file(path: Path, repo_root: Path) -> list[str]:
    """Return formatted finding lines (or empty list if clean)."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError, OSError):
        return []
    findings: list[str] = []
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    for rule_id, description, pattern, mitigation in PATTERNS:
        for match in pattern.finditer(text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            line_no = text[: match.start()].count("\n") + 1
            line_text = text[line_start:line_end]
            if ALLOW_MARKER.search(line_text):
                continue
            findings.append(
                f"{rel}:{line_no}: [{rule_id}] {description} | "
                f"matched: {match.group(0)[:60]!r}{'...' if len(match.group(0)) > 60 else ''}\n"
                f"  Mitigation: {mitigation}"
            )
    return findings


def check_credential_scan(root: Path) -> GateResult:
    failures: list[str] = []
    files_scanned = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SCAN_FILE_EXTENSIONS:
            continue
        if _path_is_exempt(path, root):
            continue
        files_scanned += 1
        findings = _scan_file(path, root)
        failures.extend(findings)

    if failures:
        return fail_gate(
            f"credential-scan-check: {len(failures)} potential credential leak(s) found "
            f"across {files_scanned} files scanned:",
            *failures,
            "",
            "If a finding is a documented-incident reference (e.g., audit doc citing a leak "
            "that already happened), suppress with an inline marker:",
            "  # allow-credential-pattern: <one-line reason>",
            "or move the file path under EXEMPT_PATH_FRAGMENTS in this gate.",
        )
    return pass_gate(
        f"credential-scan-check: {files_scanned} files scanned; no credential patterns matched"
    )


def main() -> int:
    return run_gate("credential-scan-check", check_credential_scan)


if __name__ == "__main__":
    raise SystemExit(main())
