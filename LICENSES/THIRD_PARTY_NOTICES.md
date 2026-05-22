# Third-Party Notices

This document consolidates the trademark, attribution, and nominative-use disclaimers required by the third-party resources referenced by this project.

**Authority:** `IP_POLICY.md` (repo root) § 2 + § 7; `ARCHITECTURE.md` § 9.6; IP-auditor analysis § 3.4 + § 8.2.
**Maintained by:** `/dev-orchestrator` + `/ip-auditor` (T-1410, v0.2 Enrichment Amendment 2026-05-23).
**Update cadence:** quarterly, alongside the ToS re-check schedule (IPQ-4 — first snapshot due 2026-09-30).

---

## 1. SnapGene® (Dotmatics)

**SnapGene®** is a registered trademark of Dotmatics (formerly GSL Biotech LLC, then Insightful Science). This project uses the SnapGene name nominatively — that is, to refer to the SnapGene product itself — in a small number of contexts, all governed by the rules in `IP_POLICY.md` § 2.

### Nominative-use disclaimer (canonical form)

> SnapGene® is a registered trademark of Dotmatics. This project is not affiliated with, endorsed by, sponsored by, or in any way officially connected to Dotmatics or SnapGene. SnapGene is referenced as a third-party scientific reference resource used for manual QC of sequences ingested from independent sources.

### Where to use the disclaimer

Wherever the SnapGene name appears in public-facing project documentation, either inline the full disclaimer above OR include a one-line pointer to this section. Currently:

- `docs/ml_corpus/README.md` — inline shortened reference + pointer here
- `docs/handover/*.md` — pointer here (handover documents are working artefacts, less public)
- Future `traceability_index.md` entries that name SnapGene — pointer here

### Hard rules (NORMATIVE — see BR-16)

1. No pipeline this project runs may access `snapgene.com` via any non-browser tool. `tools/ci_gates/snapgene_pipeline_scan.py` (T-1406) enforces.
2. No SnapGene-authored content (annotations, descriptions, images, `.dna` payloads) is copied into this repository.
3. SnapGene is used as a manual human-browsed QC reference; cross-check entries in `docs/ml_corpus/crosscheck_log.yaml` carry only researcher-authored, factual descriptions (≤ 200 characters) with no verbatim quotation of SnapGene-authored content.

### Legal basis for nominative use

- United States: nominative fair use per *New Kids on the Block v. News America Publ'g, Inc.*, 971 F.2d 302 (9th Cir. 1992) — three-factor test satisfied: (1) product not readily identifiable without the trademark; (2) only as much of the mark used as necessary; (3) no implication of sponsorship.
- Australia: Trade Marks Act 1995 s122(1)(b)(i) good-faith descriptive use + s122(1)(c) good-faith indication of intended purpose.

Per IP-auditor § 3.4. Binding determination remains with qualified IP counsel.

---

## 2. Open-data sequence sources (INSDC + community registries)

The project's ML training corpus ingests sequences from public-domain and openly-licensed sources. The following attributions apply to records that originate from these sources:

| Source | Attribution / Notice |
|---|---|
| **NCBI Nucleotide / GenBank** | US-government records; no copyright on records. Customary citation: NCBI accession + version, e.g., `GenBank: M77789.2`. https://www.ncbi.nlm.nih.gov/genbank/ |
| **EBI ENA** | INSDC partner; no copyright on records. https://www.ebi.ac.uk/ena/ |
| **DDBJ** | INSDC partner; no copyright on records. https://www.ddbj.nig.ac.jp/ |
| **iGEM Registry of Standard Biological Parts** | Per-part license tag; CC-BY-SA parts carry share-alike obligation and are routed to `docs/ml_corpus/records/cc-by-sa/`. Attribution: iGEM Registry BBa_* identifier. https://parts.igem.org/ |
| **JBEI ICE** | Per-deposit license. https://public-registry.jbei.org/ |
| **DNASU Plasmid Repository** | Arizona State University Biodesign Institute; in-silico use of public sequence records typically inherits the upstream INSDC posture. https://dnasu.org/ |
| **FPbase** | Operated by Talley Lambert at Harvard Medical School; mostly CC0 or CC-BY. https://www.fpbase.org/ |

The `docs/ml_corpus/corpus_manifest.yaml::license_aggregate` block reports per-source license distribution and aggregate attribution obligations.

---

## 3. Open-source software dependencies

The project depends on a set of open-source Python libraries. Their licenses are tracked separately by the project's dependency-management tooling. A consolidated SBOM is generated at release-tag time. Key categories:

- BSD-3-Clause: numpy, pyyaml, jsonschema-utilities (none used directly at v0.2)
- MIT: pytest, hypothesis, mypy, ruff, uv, importlinter
- Apache-2.0: typing-extensions
- GPL: none ingested as runtime dependencies (toolkit code is GPL-3.0-only; deps remain permissive)

Full dependency tree with versions and license SPDX IDs is in `pyproject.toml`. Release builds attach an SBOM artefact.

---

## 4. Primary scientific literature (citations, not redistribution)

The catalogues (`catalogues/hosts.yaml`, `catalogues/parts.yaml`, `catalogues/markers.yaml`, `catalogues/enzymes.yaml`, `catalogues/rules/*.yaml`) cite primary-literature sources with grade-A1/A2/A3/B1/B2 citations. The cited papers are referenced (PMID, DOI, citation text) but not redistributed. Authors retain all rights to their published work; journals retain their publication-rights posture.

Where this project's release notes, documentation, or training-corpus annotations reference scientific findings, the citation is presented in standard scholarly form. No paper text or figures are reproduced.

---

## 5. Update protocol

This document is updated whenever:

- A new third-party trademark is referenced by the project
- A vendor ToS revision is detected during the quarterly re-check (IPQ-4 — first snapshot due 2026-09-30)
- A new corpus source is added to the source-tier list in `IP_POLICY.md` § 1
- Counsel issues a revised disclaimer template

Owner: `/dev-orchestrator` runs the update; `/ip-auditor` reviews.

---

> **Disclaimer:** This document is a counsel-facing internal artefact. It is not legal advice. Binding determinations on trademark use, fair use / fair dealing, and license compatibility remain with qualified IP counsel in the relevant jurisdiction.
