# IP Policy

**Project:** Cloning & Expression Vector Design Toolkit
**Owner:** General Molecular Expression Service Pty Ltd (GMExpression / GMES)
**Toolkit code license:** GPL-3.0-only
**Policy version:** v0.2 (2026-05-23 — v0.2 Enrichment Amendment landed via cadence step 10, task T-1410)
**Authority:** This document is a CHECKED-IN counsel-facing policy. Binding architectural overrides live in `ARCHITECTURE.md` § 9.6 (Fork-Readiness Memorandum, NORMATIVE) and `REQUIREMENTS.md` § 11.7 (BR-15..BR-17).

This document codifies the project's intellectual-property and terms-of-service posture for the v0.2 toolkit and its ML training corpus. It is the artefact a future engineer or counsel reviewer should consult first when initiating a commercial fork, a corpus expansion, a model release, or a quarterly ToS re-check.

---

## 1. Source-tier list (v0.2)

Per IP-auditor analysis § 8.1 (`docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit.md`):

### Tier-1 — allowlist (ingest freely with customary attribution)

| Source | Controlling URL | Notes |
|---|---|---|
| NCBI Nucleotide / GenBank (INSDC) | https://www.ncbi.nlm.nih.gov/genbank/policy/ | US-government records; no copyright on records (INSDC policy). |
| EBI ENA (INSDC) | https://www.ebi.ac.uk/ena/browser/about/policies | INSDC partner; same posture as NCBI. |
| DDBJ (INSDC) | https://www.ddbj.nig.ac.jp/policies-e.html | INSDC partner; same posture. |
| FPbase CC0 entries | https://www.fpbase.org/about/ | Verify per-entry license tag. |
| Primary literature, INSDC accession | journal + accession | Sequence data deposited at INSDC by depositor; paper text is the journal's copyright. |

### Tier-2 — flagged (ingest with per-record review)

| Source | Notes |
|---|---|
| iGEM Registry of Standard Biological Parts | Per-part license tag; CC-BY-SA parts route to `docs/ml_corpus/records/cc-by-sa/` per architect Q7 + IP-auditor § 6.3. |
| JBEI ICE (public instance) | Per-deposit license; review each before ingestion. |
| DNASU Plasmid Repository (ASU/Biodesign) | MTA covers physical DNA shipment; in-silico use of sequences typically governed by upstream GenBank accession. |
| FPbase CC-BY entries | Attribution required; ingest with provenance. |
| Vendor-published maps + manuals (discovery aid only) | Sequence ingestion goes through the underlying primary publication, NOT the vendor manual. |

### Tier-3 — denylist (do not ingest)

| Source | Posture |
|---|---|
| `snapgene.com` (any path) | Index-only via human browser; no automated extraction per BR-16 (`tools/ci_gates/snapgene_pipeline_scan.py` enforces). SnapGene `.dna` files MUST NOT enter the corpus. |
| SnapGene-authored annotations / descriptions / images | Same. |
| Addgene bulk metadata | Discovery aid only — fetch the underlying depositor INSDC accession. The `corpus_record.schema.json::provenance.source` enum deliberately excludes `addgene_metadata_only` per FR-ML-04. |
| Paywalled journal figures / text | Cite, do not redistribute. |
| Vendor manual annotation layers | Use the underlying primary-literature sequence, not the vendor's annotation overlay. |

---

## 2. SnapGene posture (NORMATIVE per BR-16 + IP-auditor § 3)

SnapGene is used as a **human-browsed manual QC reference oracle**. Sequences ingested from cleaner-licensed sources are visually cross-checked against the corresponding SnapGene reference record by a researcher in a browser, and the result is recorded in `docs/ml_corpus/crosscheck_log.yaml`.

**Hard rules:**

1. **No automated access.** No pipeline this project runs may access `snapgene.com` via any non-browser tool — no `curl`, `wget`, `httpx`, `requests`, `playwright`, `selenium`, MCP web-fetch, or other automated HTTP client. The CI gate `tools/ci_gates/snapgene_pipeline_scan.py` (T-1406) enforces this defensively, landing `enforced-green` from day one.
2. **No redistribution.** SnapGene-authored content (annotations, descriptions, images, `.dna` file payloads) is NEVER copied into this repository.
3. **Constrained `discrepancy_resolution` text.** When a researcher records a discrepancy in `crosscheck_log.yaml`, the resolution text is researcher-authored, factual, ≤ 200 characters, with no verbatim quotation of SnapGene-authored content. Documented in the schema and enforced editorially.
4. **Nominative-use trademark only.** Public-facing references to "SnapGene" carry the nominative-use disclaimer (see `LICENSES/THIRD_PARTY_NOTICES.md`).

This posture follows the IP-auditor's risk-framed reading of the SaaS-ToS pattern and the AU + US/California fair-use / fair-dealing posture at training-cutoff date. **The 2026 SnapGene ToS MUST be re-verified at every quarterly checkpoint** (§ 4 below) and at every corpus-ingestion campaign.

---

## 3. CC-BY-SA partition strategy (NORMATIVE per IPQ-1 + IP-auditor § 6.3)

The trained model is **research-primary with a planned commercial-fork path** (user IPQ-1 resolution, 2026-05-23). Consequence:

- **`partition: sa_free` is the DEFAULT training partition.** Records with `sequence_license.spdx_id` or `annotation_license.spdx_id` matching `CC-BY-SA-*` are routed to `docs/ml_corpus/records/cc-by-sa/` and excluded from this partition.
- **`partition: full`** exists for research-only training runs that explicitly accept share-alike. It is opt-in.
- Every model release ships with a manifest declaring which partition trained it (enforced by `tools/release/corpus_release_gate.py` at T-1409).
- For any commercial-fork attempt, **only `partition: sa_free`-trained checkpoints survive** — see ARCHITECTURE.md § 9.6.

---

## 4. Quarterly ToS re-check schedule (NORMATIVE per IPQ-4)

| Aspect | Setting |
|---|---|
| Cadence | Quarterly |
| First snapshot due | **2026-Q3 (by 2026-09-30)** |
| Archive location | `docs/ip_policy/tos_snapshots/{YYYY-QQ}/` |
| Archive method | perma.cc snapshots (or equivalent timestamped immutable archival) |
| Owner: runs the check | `/dev-orchestrator` |
| Owner: reviews findings | `/ip-auditor` |
| Sources to re-verify | snapgene.com, addgene.org, vendor manual hosting sites, INSDC/NCBI/EBI/DDBJ policy pages, iGEM Registry policy, FPbase, JBEI ICE, DNASU, primary-literature journal-by-journal sequence-deposit policies |
| Drift-detected action | If a vendor adds an explicit ML-training prohibition or scraping clause that conflicts with current posture, halt the corresponding ingestion stream and re-issue an IP-auditor analysis. |

---

## 5. Fork-readiness pointer

Any future commercial-fork attempt MUST consult **`ARCHITECTURE.md` § 9.6 Fork-Readiness Memorandum** (NORMATIVE) and its operational mirror at **`docs/fork-readiness/checklist.md`** (T-1411). The memorandum enumerates:

- (a) Datasets to exclude or substitute for commercial fork
- (b) Workflows to relax or tighten
- (c) Design elements to re-point
- (d) License + IP posture for the fork
- (e) Regulatory posture for commercial release (US EAR ECCN 1E001, NIH DURC, AU Defence Trade Controls Act 2012, EU AI Act if global)
- (f) Sign-off requirement: counsel-review certificate attached to every commercial release tag

**No commercial release tag is valid unless all § 9.6 items have been verified and a counsel-review certificate is attached to the release manifest.**

---

## 6. Project licensing posture

| Layer | License | Notes |
|---|---|---|
| Toolkit code | GPL-3.0-only | Inherited as-is on any fork. The GPL governs the *code* that processes data; it does not require the *data being processed* to be GPL-licensed. |
| Training corpus data | Per-record (CC0 / CC-BY / CC-BY-SA / vendor / public-domain) | Each record's `license.sequence_license` + `license.annotation_license` blocks are explicit; missing-or-default is a hard CI failure (BR-15 default-deny). |
| Trained model weights | TBD by the user per release | NOT redistributed under GPL-3.0. Commercial-fork model weights MUST be Apache-2.0 / MIT / proprietary — NOT CC-BY-SA, NOT GPL (per ARCHITECTURE.md § 9.6.4). |

---

## 7. Counsel-review checkpoints

| Trigger | Action |
|---|---|
| Pre-commercial release | Mandatory counsel review of the corpus + model + trademark posture. Release-gate (`tools/release/corpus_release_gate.py`) checks for the counsel-review certificate at tag time. |
| Quarterly ToS drift | `/ip-auditor` reviews the perma.cc snapshots and issues a drift report. |
| New corpus source proposal | `/ip-auditor` opinion before ingestion stream is opened. |
| Vendor license outreach (deferred IPQ-3) | Track future-cadence. Useful long-term to unlock cleaner vendor-manual content. |

---

## 8. Cross-references

- **`ARCHITECTURE.md` § 9.6** — NORMATIVE Fork-Readiness Memorandum
- **`REQUIREMENTS.md` § 11.7** — BR-15 (ML license enforcement), BR-16 (SnapGene posture), BR-17 (CC-BY-SA partition)
- **`docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit.md`** — IP-auditor full analysis (basis for this policy)
- **`docs/handover/2026-05-23_host_marker_ml_corpus_development_plan.md`** § 10 — joint-plan fork-readiness scope
- **`docs/fork-readiness/checklist.md`** — operational checklist mirroring § 9.6 (T-1411)
- **`docs/ml_corpus/corpus_manifest.yaml`** — partition + license aggregate
- **`tools/ci_gates/snapgene_pipeline_scan.py`** — BR-16 enforcement
- **`tools/release/corpus_release_gate.py`** — release-time gate (T-1409)
- **`LICENSES/THIRD_PARTY_NOTICES.md`** — trademark + attribution disclaimers

---

> **Disclaimer:** This policy is a counsel-facing internal document. It is not legal advice. Binding determinations belong to qualified IP counsel in the relevant jurisdiction (AU registered patent / IP attorney + California-licensed counsel for project owner's jurisdiction of operation). All commercial-release decisions require a current counsel-review certificate.
