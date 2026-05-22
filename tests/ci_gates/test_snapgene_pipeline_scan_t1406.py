"""
module_id: tests.ci_gates.test_snapgene_pipeline_scan_t1406
file: tests/ci_gates/test_snapgene_pipeline_scan_t1406.py
task_id: T-1406
architecture_refs: § 9.3.5 SnapGene cross-check — process-only artefact; BR-16
requirements_refs: BR-16; UR-14

Tests for the snapgene-pipeline-scan CI gate (T-1406).

Two-part contract:
  1. On the REAL codebase, the gate passes (no v0.1.0 / v0.2 pipeline file invokes a
     fetch tool against snapgene.com).
  2. On a SYNTHETIC fixture that contains a forbidden invocation, the gate fails
     with a useful finding message.
"""

from __future__ import annotations

from pathlib import Path

from tools.ci_gates.snapgene_pipeline_scan import (
    FORBIDDEN_PATTERNS,
    check_snapgene_pipeline_scan,
)

ROOT = Path(__file__).resolve().parents[2]


def test_snapgene_pipeline_scan_passes_on_real_codebase() -> None:
    """The v0.1.0 + v0.2 codebase MUST have no forbidden snapgene.com fetch invocations.

    BR-16 default-deny holds at landing time.
    """
    result = check_snapgene_pipeline_scan(ROOT)
    assert result.passed, (
        "BR-16 default-deny baseline broken on the real codebase. "
        f"Findings: {result.messages}"
    )


def test_snapgene_pipeline_scan_fails_on_synthetic_curl_fixture(tmp_path: Path) -> None:
    """A fake CI workflow that uses curl against snapgene.com MUST be flagged."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "bad.yml").write_text(
        "name: bad\non: push\njobs:\n  scrape:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: curl https://www.snapgene.com/plasmids/ > out.html\n",
        encoding="utf-8",
    )
    result = check_snapgene_pipeline_scan(tmp_path)
    assert not result.passed
    assert any("snapgene.com" in msg for msg in result.messages)


def test_snapgene_pipeline_scan_fails_on_synthetic_requests_fixture(tmp_path: Path) -> None:
    """A Python script in tools/ that calls requests.get against snapgene.com MUST be flagged."""
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    (tools_dir / "scrape_snapgene.py").write_text(
        "import requests\n"
        "response = requests.get('https://www.snapgene.com/plasmids/pet-28a/')\n",
        encoding="utf-8",
    )
    result = check_snapgene_pipeline_scan(tmp_path)
    assert not result.passed
    assert any("snapgene.com" in msg for msg in result.messages)


def test_snapgene_pipeline_scan_fails_on_synthetic_playwright_fixture(tmp_path: Path) -> None:
    """A pipeline script with a single-line playwright invocation against snapgene.com MUST be flagged.

    Note: the regex requires the tool token and `snapgene.com` to appear on the same line.
    Multi-line obfuscation (variable indirection) is a known limitation of regex heuristics;
    deeper review catches those cases.
    """
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    (tools_dir / "headless_scrape.py").write_text(
        "from playwright.sync_api import sync_playwright\n"
        "playwright_browser.goto('https://www.snapgene.com/plasmids/')\n",
        encoding="utf-8",
    )
    result = check_snapgene_pipeline_scan(tmp_path)
    assert not result.passed
    assert any("snapgene.com" in msg for msg in result.messages)


def test_snapgene_pipeline_scan_does_not_flag_snapgene_string_data(tmp_path: Path) -> None:
    """A Python file that contains the snapgene.com string as DATA (not a fetch call) MUST NOT be flagged.

    This case matters because test fixtures legitimately mention SnapGene URLs as
    cross-check log entries (per ARCHITECTURE.md § 9.3.5 process-only artefact).
    """
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    (tools_dir / "fixture_data.py").write_text(
        "# Cross-check log fixture\n"
        "SNAPGENE_RECORD_URLS = [\n"
        "    'https://www.snapgene.com/plasmids/pet-28a/',\n"
        "    'https://www.snapgene.com/plasmids/pUC19/',\n"
        "]\n",
        encoding="utf-8",
    )
    result = check_snapgene_pipeline_scan(tmp_path)
    assert result.passed, (
        f"BR-16 scanner false-positives on string-data references to snapgene.com. "
        f"Findings: {result.messages}"
    )


def test_snapgene_pipeline_scan_excludes_self() -> None:
    """The scanner's own file references snapgene.com as a regex target — exclude self.

    The SELF_EXCLUDE list in the scanner module must contain the scanner's own path.
    """
    from tools.ci_gates.snapgene_pipeline_scan import SELF_EXCLUDE

    assert "tools/ci_gates/snapgene_pipeline_scan.py" in SELF_EXCLUDE


def test_forbidden_patterns_cover_expected_tools() -> None:
    """The FORBIDDEN_PATTERNS tuple MUST cover the canonical fetch-tool families per BR-16."""
    pattern_sources = [p.pattern.lower() for p in FORBIDDEN_PATTERNS]
    pattern_blob = " ".join(pattern_sources)
    for tool in ("curl", "wget", "requests", "httpx", "urllib", "aiohttp", "playwright", "selenium"):
        assert tool in pattern_blob, f"FORBIDDEN_PATTERNS missing coverage for {tool!r}"
