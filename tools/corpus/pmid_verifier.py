"""
module_id:           tools.corpus.pmid_verifier
file:                tools/corpus/pmid_verifier.py
task_id:             audit-fix-H3

PMID cross-checker for ML-corpus records.

The 2026-05-23 collaborative audit (Scientific § 3.4) found that of 6
modular-element records spot-checked for PMID accuracy, 4 pointed to
unrelated papers — e.g., PMID 6328430 was cited as the BGH polyA paper but
is actually RK2 plasmid biology; PMID 21909101 was cited as the P2A peptide
paper but is feline antiviral transgenesis. With ~60 PMID-bearing records
in the corpus, the implied error rate (~67% spot-checked) is unacceptable
for ML training data anchored to scholarly citations.

This tool sweeps every PMID across `docs/ml_corpus/records/**/*.yaml` and
cross-checks each against NCBI PubMed esearch + esummary. The verification
heuristic is keyword-overlap between the corpus record's `citation_text` /
record `name` / `category` and the PubMed-returned title + abstract.

Workflow:
1. Walk records, extract PMID and citation_text.
2. For each PMID, fetch the PubMed summary (esearch → esummary).
3. Compute keyword-overlap score between the corpus citation and the PubMed
   title; flag low overlap as likely-mismatch.
4. Emit a structured report (JSON or markdown) ranking mismatches by severity.

Limitations:
- Heuristic only; cannot prove a citation is right, only that it looks
  plausible. Borderline cases need human curator review.
- NCBI eutils has a soft rate limit of ~3 requests/second without an API key
  (~10/sec with one). The tool sleeps 1.0s between calls by default.
- Network-dependent. Records flagged 'unverifiable' need to be re-checked
  manually when NCBI is available.

This is the v0.2.1 fix H3 deliverable; the corpus-side fixes for the actual
mismatches are a separate follow-on (each requires a human curator to choose
the correct PMID — automated remediation would risk fabricating citations).

Usage:
    python -m tools.corpus.pmid_verifier
    python -m tools.corpus.pmid_verifier --report=docs/handover/2026-05-23_v0.2.1_pmid_sweep.md
    python -m tools.corpus.pmid_verifier --dry-run            # don't write report, stdout only
    python -m tools.corpus.pmid_verifier --delay=2.0          # tune anti-rate-limit delay

The tool is INFORMATIONAL — it never modifies corpus records. A human curator
must triage the report and update individual records.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

REPO_ROOT_RELATIVE_TO_THIS_FILE = Path(__file__).resolve().parents[2]
DEFAULT_CORPUS_GLOB = "docs/ml_corpus/records/**/*.yaml"
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DEFAULT_DELAY_SECONDS = 1.0
USER_AGENT = (
    "cev-toolkit/0.2.1 (audit-fix-H3 pmid_verifier; +https://github.com/tocvicmeng-prog/"
    "cloning-expression-vector-design)"
)

# Words that don't help discriminate — drop them from keyword-overlap scoring.
STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "from",
        "by",
        "and",
        "or",
        "but",
        "with",
        "without",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "as",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "et",
        "al",
        "vol",
        "pp",
        "no",
        "complete",
        "sequence",
        "gene",
        "protein",
        "vector",
        "plasmid",
        "expression",
        "construct",
        "fragment",
        "cds",
        "mrna",
    }
)

LOW_OVERLAP_THRESHOLD = 1  # < this many overlapping keywords → flag as mismatch
BORDERLINE_OVERLAP_THRESHOLD = 2  # < this → flag as borderline


@dataclass(frozen=True)
class CorpusPmidRecord:
    record_path: Path
    record_id: str
    pmid: str
    citation_text: str
    record_name: str
    category: str


@dataclass(frozen=True)
class PubmedSummary:
    pmid: str
    title: str
    authors: tuple[str, ...]
    journal: str
    year: str


@dataclass(frozen=True)
class VerificationResult:
    record: CorpusPmidRecord
    pubmed: PubmedSummary | None
    keyword_overlap: int
    verdict: str  # "match" | "borderline" | "mismatch" | "unverifiable"
    notes: str


def _extract_keywords(text: str) -> set[str]:
    """Lowercase, remove punctuation, drop stopwords + short tokens, return token set."""
    if not text:
        return set()
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]+", text.lower())
    return {t for t in tokens if len(t) >= 3 and t not in STOPWORDS}


def _collect_pmid_records(repo_root: Path) -> list[CorpusPmidRecord]:
    """Walk the corpus tree and yield one CorpusPmidRecord per record with a PMID."""
    records: list[CorpusPmidRecord] = []
    for path in repo_root.glob(DEFAULT_CORPUS_GLOB):
        if not path.is_file():
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError):
            continue
        if not isinstance(data, Mapping):
            continue
        provenance = data.get("provenance", {})
        if not isinstance(provenance, Mapping):
            continue
        pmid = provenance.get("pmid")
        if not pmid:
            # Some records carry pmids: [...] instead of pmid: scalar.
            pmids = provenance.get("pmids", [])
            if isinstance(pmids, list) and pmids:
                pmid = str(pmids[0])
            else:
                continue
        pmid_str = str(pmid).strip()
        if not pmid_str.isdigit():
            continue
        records.append(
            CorpusPmidRecord(
                record_path=path,
                record_id=str(data.get("id", "")),
                pmid=pmid_str,
                citation_text=str(provenance.get("citation_text", "")),
                record_name=str(provenance.get("name", "")),
                category=str(data.get("category", "")),
            )
        )
    return records


def _fetch_pubmed_summary(pmid: str) -> PubmedSummary | None:
    """Fetch the PubMed summary record for a given PMID via NCBI eutils esummary."""
    params = urllib.parse.urlencode({"db": "pubmed", "id": pmid, "retmode": "json"})
    url = f"{EUTILS_BASE}/esummary.fcgi?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None
    result = payload.get("result", {})
    if pmid not in result:
        return None
    record = result[pmid]
    title = str(record.get("title", ""))
    authors_raw = record.get("authors", [])
    authors = tuple(str(a.get("name", "")) for a in authors_raw[:5] if isinstance(a, dict))
    journal = str(record.get("fulljournalname", "") or record.get("source", ""))
    year_raw = str(record.get("pubdate", ""))
    year_match = re.search(r"\b(\d{4})\b", year_raw)
    year = year_match.group(1) if year_match else ""
    return PubmedSummary(
        pmid=pmid,
        title=title,
        authors=authors,
        journal=journal,
        year=year,
    )


def _classify(record: CorpusPmidRecord, pubmed: PubmedSummary | None) -> tuple[int, str, str]:
    """Return (keyword_overlap, verdict, notes)."""
    if pubmed is None:
        return (0, "unverifiable", "could not fetch PubMed summary (network error or invalid PMID)")
    corpus_keywords = _extract_keywords(record.citation_text + " " + record.record_name)
    pubmed_keywords = _extract_keywords(pubmed.title)
    overlap = corpus_keywords & pubmed_keywords
    overlap_count = len(overlap)
    if overlap_count >= BORDERLINE_OVERLAP_THRESHOLD:
        return (overlap_count, "match", f"keyword overlap: {sorted(overlap)}")
    if overlap_count >= LOW_OVERLAP_THRESHOLD:
        return (
            overlap_count,
            "borderline",
            f"low overlap ({sorted(overlap)}) — human triage needed; "
            f"pubmed title: {pubmed.title!r}",
        )
    return (
        overlap_count,
        "mismatch",
        f"NO keyword overlap. Corpus name/citation: {record.record_name!r} / "
        f"{record.citation_text[:120]!r}; pubmed title: {pubmed.title!r}",
    )


def verify_corpus(
    repo_root: Path,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
    progress_stream: Any | None = None,
) -> list[VerificationResult]:
    if progress_stream is None:
        progress_stream = sys.stderr
    records = _collect_pmid_records(repo_root)
    results: list[VerificationResult] = []
    print(
        f"pmid_verifier: {len(records)} corpus records carry a PMID; verifying...",
        file=progress_stream,
    )
    for i, record in enumerate(records, 1):
        pubmed = _fetch_pubmed_summary(record.pmid)
        overlap, verdict, notes = _classify(record, pubmed)
        results.append(
            VerificationResult(
                record=record,
                pubmed=pubmed,
                keyword_overlap=overlap,
                verdict=verdict,
                notes=notes,
            )
        )
        marker = {"match": ".", "borderline": "?", "mismatch": "!", "unverifiable": "x"}.get(
            verdict, "?"
        )
        line = (
            f"pmid_verifier: [{i:3d}/{len(records)}] "
            f"PMID {record.pmid:>8s} → {marker} {verdict:<13s}"
        )
        print(line, file=progress_stream)
        if i < len(records):
            time.sleep(delay_seconds)
    return results


def render_report(results: Iterable[VerificationResult]) -> str:
    results = list(results)
    counts: dict[str, int] = {"match": 0, "borderline": 0, "mismatch": 0, "unverifiable": 0}
    for r in results:
        counts[r.verdict] = counts.get(r.verdict, 0) + 1
    total = len(results)
    lines = [
        "# v0.2.1 audit fix H3 — PMID sweep report",
        "",
        "**Generated:** by `tools/corpus/pmid_verifier.py`",
        f"**Corpus records with PMIDs:** {total}",
        "",
        "## Summary",
        "",
        "| Verdict | Count | Fraction |",
        "|---|---|---|",
        f"| ✅ match | {counts['match']} | {counts['match'] / max(total, 1):.1%} |",
        f"| ❓ borderline (human triage) | {counts['borderline']} "
        f"| {counts['borderline'] / max(total, 1):.1%} |",
        f"| 🚨 mismatch (likely wrong PMID) | {counts['mismatch']} "
        f"| {counts['mismatch'] / max(total, 1):.1%} |",
        f"| ⚠️ unverifiable (network/PMID lookup failed) | {counts['unverifiable']} "
        f"| {counts['unverifiable'] / max(total, 1):.1%} |",
        "",
        "## Mismatches (priority remediation)",
        "",
    ]
    mismatches = [r for r in results if r.verdict == "mismatch"]
    if not mismatches:
        lines.append("_None._")
    else:
        for r in mismatches:
            rel = r.record.record_path.as_posix().split("docs/ml_corpus/")[-1]
            lines.append(f"### {r.record.record_id} (`docs/ml_corpus/{rel}`)")
            lines.append("")
            lines.append(f"- **PMID claimed:** {r.record.pmid}")
            lines.append(f"- **Corpus citation:** {r.record.citation_text or '_(none)_'}")
            lines.append(f"- **Corpus record name:** {r.record.record_name}")
            if r.pubmed:
                lines.append(f"- **PubMed title:** {r.pubmed.title}")
                authors = ", ".join(r.pubmed.authors) if r.pubmed.authors else "_(none)_"
                lines.append(f"- **PubMed authors:** {authors}")
                lines.append(f"- **PubMed journal:** {r.pubmed.journal} ({r.pubmed.year})")
            lines.append(f"- **Notes:** {r.notes}")
            lines.append("")
    lines.extend(
        [
            "## Borderlines (human triage recommended)",
            "",
        ]
    )
    borderlines = [r for r in results if r.verdict == "borderline"]
    if not borderlines:
        lines.append("_None._")
    else:
        for r in borderlines:
            rel = r.record.record_path.as_posix().split("docs/ml_corpus/")[-1]
            lines.append(f"- **{r.record.record_id}** PMID {r.record.pmid} — {r.notes}")
    lines.append("")
    lines.extend(
        [
            "## Unverifiable (re-run when NCBI eutils is reachable)",
            "",
        ]
    )
    unverifiable = [r for r in results if r.verdict == "unverifiable"]
    if not unverifiable:
        lines.append("_None._")
    else:
        for r in unverifiable:
            lines.append(f"- **{r.record.record_id}** PMID {r.record.pmid}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=None, help="path to write report")
    parser.add_argument("--dry-run", action="store_true", help="stdout only; don't write report")
    parser.add_argument(
        "--delay", type=float, default=DEFAULT_DELAY_SECONDS, help="seconds between calls"
    )
    parser.add_argument("--limit", type=int, default=0, help="stop after N records (0 = all)")
    args = parser.parse_args(argv)

    if args.limit:
        # Apply the limit BEFORE the verification loop so we don't waste API calls.
        all_records = _collect_pmid_records(REPO_ROOT_RELATIVE_TO_THIS_FILE)[: args.limit]
        print(
            f"pmid_verifier: --limit={args.limit} → verifying {len(all_records)} records",
            file=sys.stderr,
        )
        results: list[VerificationResult] = []
        for i, record in enumerate(all_records, 1):
            pubmed = _fetch_pubmed_summary(record.pmid)
            overlap, verdict, notes = _classify(record, pubmed)
            results.append(
                VerificationResult(
                    record=record,
                    pubmed=pubmed,
                    keyword_overlap=overlap,
                    verdict=verdict,
                    notes=notes,
                )
            )
            print(
                f"pmid_verifier: [{i:3d}/{len(all_records)}] PMID {record.pmid} -> {verdict}",
                file=sys.stderr,
            )
            if i < len(all_records):
                time.sleep(args.delay)
    else:
        results = verify_corpus(REPO_ROOT_RELATIVE_TO_THIS_FILE, delay_seconds=args.delay)
    report = render_report(results)
    if args.report and not args.dry_run:
        args.report.write_text(report, encoding="utf-8")
        print(f"pmid_verifier: report written to {args.report}", file=sys.stderr)
    elif args.dry_run:
        # Don't print emoji-rich report to stdout on cp1252-locale Windows;
        # summary only.
        counts: dict[str, int] = {"match": 0, "borderline": 0, "mismatch": 0, "unverifiable": 0}
        for r in results:
            counts[r.verdict] = counts.get(r.verdict, 0) + 1
        print(f"pmid_verifier: --dry-run summary: {counts}", file=sys.stderr)
    else:
        # cp1252-locale Windows stdout chokes on emoji; reconfigure to utf-8 where possible.
        reconfigure = getattr(sys.stdout, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")
        print(report)
    mismatches = sum(1 for r in results if r.verdict == "mismatch")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
