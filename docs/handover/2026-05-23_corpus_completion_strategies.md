# Corpus Completion Strategies — molecular-biology methodology for closing T-1404/T-1405 backlog

**Author:** `/scientific-advisor` (practical R&D support, sub-mode 5: resource identification)
**Date:** 2026-05-23
**Context:** v0.2 corpus at 107 records (commits 5305e3f → a3b7a37 → c24a597). User authorisation to relax BR-16 and IP-audit constraints "if necessary." Standing project working principle per [[cev-workflow-discipline]].
**Cadence position:** Post-v0.2 backlog progression; this document advises the next curation pass and identifies which strategies require explicit BR-16 / IP-audit override versus which sit comfortably inside the existing compliance envelope.

---

## 0. Executive summary

The remaining v0.2 backlog (~12 vendor backbones + 1 FP + 1 insulator + 0/107 SnapGene cross-check) is **not uniformly blocked.** Critical empirical findings from this session's source-hunting:

1. **Addgene now requires login for GenBank file download.** The previously-assumed "Addgene depositor-side bypass" — fetching depositor-owned sequences while ignoring Addgene-authored metadata — is **operationally non-viable for unattended pipelines** as of 2026-05-23 retrieval. Per-record manual download is still possible for a researcher with an Addgene account; automated batch fetches are not.

2. **Addgene's GenBank files are served via `media.addgene.org/snapgene-media/...` CDN.** Even with login, the file URLs route through SnapGene CDN infrastructure. This is BR-16 grey zone: not a direct `snapgene.com` fetch, but an Addgene endpoint that happens to use SnapGene's CDN. **Recommendation:** treat as a borderline BR-16 case — fine for human-in-browser download, not for automated tools.

3. **NCBI nuccore is dramatically more complete than the v0.2 cadence assumed.** This session's direct NCBI searches (after the FPbase round) caught seven FPs that FPbase had marked as having no GenBank deposit. The same likely applies to vendor backbones — a more aggressive NCBI query strategy will yield 3-5 more vendor backbones without any compliance friction.

4. **Patent disclosures are an untapped legitimate source.** USPTO and EPO published patents routinely disclose full plasmid sequences as figures or text. Public patent disclosures are public-domain for research use and citable under the project's existing `primary_literature` provenance source.

5. **EuropePMC + Nature Methods supplementary materials** carry full vector and FP sequences. mScarlet3 (Bindels 2024) supplementary should contain its CDS as a downloadable .gb or FASTA file. This is a single targeted retrieval, not a strategy-wide reroute.

6. **iGEM Registry has 23,000+ standardised parts** with permissive CC-BY-SA terms. The project already has CC-BY-SA partition routing (`partition: full` + `partition: sa_free`). Many of the missing modular elements (more polyA signals, RBS variants, terminators) have iGEM equivalents.

**Net recommendation:** invoke the user's override **only for** the SnapGene cross-check pass (separate user-approval-per-record gate), and pursue the rest via:
(A) aggressive NCBI re-search with new query strategies (3-5 vendor backbones expected to surface);
(B) patent-disclosure mining (3-5 more backbones expected);
(C) supplementary-material fetching from Nature Methods, PNAS, EMBO J for mScarlet3 and any vendor-pubished vectors;
(D) iGEM Registry mining for ~5-10 more modular elements.

This combined strategy is expected to add **~15-25 corpus records without invoking BR-16 / IP-audit overrides**, taking the corpus from 107 to ~125-130 records and closing 3 of the 4 backlog items.

---

## 1. Backlog inventory (as of 2026-05-23, post-c24a597)

| # | Item | Origin | Records pending | Curator-tractability |
|---|---|---|---|---|
| 1 | Vendor-only backbones | T-1404 INSDC-only constraint | ~12 (pET-28a, pPICZ-A, pPICZ-α-A, pGAPZ-A, pPICZ-B, pcDNA3.4-TOPO, pVAX1, psPAX2, pMD2.G, pLKO.1, pCAGGS, pET-22b) | Mixed — some retrievable via NCBI re-search or patent disclosure; others genuinely behind vendor paywall |
| 2 | mScarlet3 (Bindels 2024) | T-1405 FPbase follow-up | 1 | High — supplementary material likely contains sequence |
| 3 | USP / chicken β-globin 5' HS5 insulator | T-1405 placeholder cleanup | 1 | Low — no public INSDC deposit; would need patent or supplementary mining |
| 4 | SnapGene cross-check pass | T-1404 + T-1405 BR-16 NORMATIVE process artefact | 107 records pending | None without override — BR-16 explicitly forbids automated SnapGene access |

---

## 2. Source landscape — 12 alternative sources for missing elements

### 2.1 Tier-1 (already in provenance enum, compliance-clean)

| Source | URL / endpoint | Compliance posture | Yield estimate for v0.2 backlog |
|---|---|---|---|
| **NCBI nuccore (aggressive re-search)** | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi | INSDC public domain; explicit in IP-audit § 4.1 allowlist | **3-5 vendor backbones** likely surface with broader query terms (pT7Blue, pCMV-Tag, pcDNA3.4, etc.) |
| **EBI ENA** | https://www.ebi.ac.uk/ena/browser/api/embl/{accession} | INSDC mirror; same posture as NCBI | Duplicates NCBI; use as fallback when NCBI is rate-limited |
| **DDBJ** | https://getentry.ddbj.nig.ac.jp/getentry/na/{accession}/?format=flatfile | INSDC mirror; same posture | Same as ENA — fallback |
| **iGEM Registry** | https://parts.igem.org/Part:BBa_XXXXXX | CC-BY-SA 3.0; route via `cc-by-sa/` partition per project IPQ-1 resolution | **~5-10 modular elements** (RBSs, terminators, polyA-like signals, MCS variants); already-implemented partition routing handles license cleanly |
| **JBEI ICE (public instance)** | https://public-registry.jbei.org/api/parts/{id}/sequence | Per-deposit license variability; require explicit per-record license read | **2-3 specialty backbones** (lignocellulose biorefinery context not load-bearing for cloning corpus but some general vectors) |
| **DNASU Plasmid Repository** | https://dnasu.org/DNASU/AdvancedSearchOptions.do | MTA for physical plasmid; sequence records typically permissive | **1-2 backbones** (DNASU's strength is mammalian Gateway entry vectors, lower priority for general corpus) |

### 2.2 Tier-2 (in provenance enum but require careful handling)

| Source | URL / endpoint | Compliance posture | Yield estimate |
|---|---|---|---|
| **`primary_literature` — Nature Methods / PNAS / Cell / NAR / EMBO J supplementary materials** | https://www.nature.com/articles/{doi}#Sec-MaterialsAndMethods + supplementary files | Publisher's "text reuse for research" clause + Feist (factual sequences not copyrightable) | **mScarlet3** (Bindels 2024) + **2-3 specialty FPs** (e.g., GreenLantern variants); curator extracts sequence from supplementary GenBank/FASTA file |
| **`primary_literature` — USPTO / EPO published patents** | https://patentscope.wipo.int/search/en/search.jsf + https://patents.google.com | Published patent disclosures are public-domain for research use; protected against use that practices the claims (commercial implementation), not against use that documents the structures | **3-5 vendor backbones** — Studier's pET system (US 4,952,496), Invitrogen's pPICZ/AOX1 system patents, lentiviral 3rd-gen patents |
| **`vendor_published_map`** | Vendor manual PDFs (TB055 Novagen pET, K1710 Invitrogen Pichia, Trono lab https://lentiweb.com, etc.) | Vendor manuals: factual sequence content per Feist; trademark posture requires careful citation; Trono Lab plasmids are openly distributed for academic use | **3-4 vendor backbones** if curator extracts annotated sequences from vendor PDFs (manual step) |
| **`fpbase` (already covered)** | https://www.fpbase.org/api/proteins/ | CC-BY 4.0; sequence content is factual | Mostly exhausted for v0.2; mScarlet3 entry exists at https://www.fpbase.org/protein/mscarlet3/ but lacks `genbank` field |

### 2.3 Tier-3 (NOT in provenance enum — would require override)

| Source | Compliance issue | Override risk |
|---|---|---|
| **Addgene depositor-side (login-gated)** | Login wall; CDN routes via snapgene-media (BR-16 grey zone); Addgene-authored metadata is Tier-2-excluded but depositor sequences should be fine in principle. *Operationally non-viable for unattended pipelines as of 2026-05-23.* | **LOW** if a researcher manually downloads and curator-strips Addgene-authored fields; **HIGH** if automated batch retrieval is attempted |
| **SnapGene Lab / snapgene.com direct** | BR-16 NORMATIVE: "no pipeline this project runs may access snapgene.com via any non-browser tool" | **HIGH** — explicit project NORMATIVE rule; would require user-per-record approval |
| **GenScript / IDT / Twist proprietary sequences** | Vendor terms typically forbid redistribution | **HIGH** — would need vendor written permission |

---

## 3. Per-source license matrix (NEW columns for v0.2 corpus_record schema compliance)

| Source | `provenance.source` enum value | `spdx_id` | `redistribution_allowed` | `ml_training_allowed` | `attribution_required` | `commercial_use_allowed` |
|---|---|---|---|---|---|---|
| NCBI/ENA/DDBJ INSDC | `ncbi_genbank` / `ebi_ena` / `ddbj` | `NCBI-PD` | true | true | false | true |
| iGEM Registry | `igem_registry` | `CC-BY-SA-3.0` | true (with sa-route) | true (full partition) | true | true (with sa-route compliance) |
| JBEI ICE | `jbei_ice` | per-record (typically `CC0-1.0` or `CC-BY-4.0`) | true | true | conditional | true |
| DNASU | `dnasu` | typically `CC-BY-4.0` | true | true | true | true |
| Patent disclosures (USPTO/EPO) | `primary_literature` | `patent-public-disclosure` | true | true | true (cite patent number + assignee) | true (for documentation; restricted for practising claims) |
| Nature/Cell/Science supp | `primary_literature` | `primary-literature-public-record` | true | true | true | true |
| Vendor manuals (factual content) | `vendor_published_map` | `vendor-published-factual` | true (sequence only) | true | true (cite vendor + product) | true |
| FPbase | `fpbase` | `CC-BY-4.0` | true | true | true | true |

---

## 4. Risk / yield matrix — combined assessment

| Strategy | Implementation cost | Expected records added | Compliance risk | Curator override needed |
|---|---|---|---|---|
| **A. Aggressive NCBI re-search** (broader query terms, synonym expansion, partial accession matches) | LOW (1-2 hours scripted) | 3-5 vendor backbones | None | No |
| **B. Patent-disclosure mining** (USPTO Patent Public Search + EPO Espacenet for pET / pPICZ / lentiviral 3rd-gen patents) | MEDIUM (2-3 hours; patents need careful citation) | 3-5 backbones | Low (citation + claim-non-practice attestation) | No |
| **C. Supplementary-material fetching** (Nature Methods, PNAS) for mScarlet3 + a few specialty vectors | LOW (single-file fetches) | 2-4 records (incl. mScarlet3) | None (factual sequence content + Feist) | No |
| **D. iGEM Registry mining** (CC-BY-SA partition routing per IPQ-1) | MEDIUM (iGEM API + sa-route compliance) | 5-10 modular elements | None (sa_free partition already plumbed) | No |
| **E. Addgene depositor-side** (manual per-record download by researcher) | HIGH (login + per-record handling) | ~12 backbones | Low if researcher-mediated, high if automated | YES — explicit per-record approval; LOW BR-16 risk via Addgene CDN |
| **F. SnapGene Lab direct** | HIGH | ~107 cross-checks | HIGH | YES — explicit BR-16 NORMATIVE override; this is the load-bearing user authorization |
| **G. Codon-optimization backtranslation** (for FP AA-only records — backtranslate to nucleotide using E. coli K12 codon table) | LOW | 2-3 FPs (ECFP, USP/HS5 from peptide context) | Low (clearly flagged as "curator-derived back-translation, not authoritative") | No, but record must carry explicit `provenance.notes` warning |

**Cumulative yield without invoking overrides (A+B+C+D+G):** ~15-25 records.
**With Addgene override (E):** +~12.
**With BR-16 override (F):** SnapGene cross-check pass for all 107 records.

---

## 5. Strategy selection — what to implement now (no override)

Following the user's "ignore BR deny if necessary" qualifier — only invoke overrides where actually necessary — the optimal v0.2 next-pass strategy is:

### 5.1 Implement immediately (this session)

- **C1. mScarlet3 supplementary fetch** — single targeted retrieval from the Bindels 2024 Nature Methods paper. Single record but closes a documented gap and validates the supplementary-material workflow.
- **A1. NCBI re-search for vendor backbones** — broader query terms catching titles that earlier searches missed.
- **B1. Patent-disclosure mining for 2-3 well-known backbones** — Studier pET (US 4,952,496), Invitrogen pPICZ (US 5,166,329), lentiviral 3rd-gen (US 6,924,123) — extract sequences from the published patent text.

### 5.2 Defer to a focused follow-up curation session

- **D. iGEM Registry mining** — needs the project's CC-BY-SA partition routing to be exercised; deserves its own session with explicit license-scan-per-record discipline.
- **G. Codon-optimization backtranslation** — needs a documented backtranslation policy (which codon table per host) before being applied.

### 5.3 Require explicit per-case user approval

- **E. Addgene depositor-side download** — for the most critical missing backbones the user wants to land (suggested: psPAX2, pMD2.G, pLKO.1 — Trono Lab lentiviral system, very widely-cited). User to download manually + provide the .gb files; curator processes them.
- **F. SnapGene cross-check pass for the 107 existing records** — the BR-16 override the user named explicitly. Approval per-batch (e.g., 20 records at a time) lets us audit-trail the deviation from NORMATIVE.

### 5.4 Documented out-of-scope until future scope decision

- **USP / chicken β-globin 5' HS5 insulator** — no public deposit; would require backtranslation from amino-acid level which is not appropriate for a regulatory-element record. Remains in `corpus_manifest.yaml::maintenance.population_notes` as backlog.

---

## 6. Override invocation log (template for any record where the user must approve a deviation)

```yaml
# Append to docs/ml_corpus/override_log.yaml (lands at next curation pass)
- record_id: corpus.backbone.mammalian.plko1
  override_type: addgene_depositor_side
  approval_date: 2026-05-XX  # to be filled by user
  approval_owner: tocvicmeng@gmail.com (project owner / Holocyte GMExpression)
  ip_audit_section: § 5.2 fold-in (depositor-owned sequence) + § 8.1 Tier-2 (Addgene general)
  rationale: |
    Trono Lab's psPAX2 / pMD2.G / pLKO.1 are widely-cited in academic research
    and Trono Lab themselves publish the sequences openly via Addgene depositor
    submissions. The IP-audit § 5.2 nuance distinguishes depositor-owned content
    (covered by depositor's terms, typically open) from Addgene-authored metadata
    (Tier-2 risk). This override is for depositor-owned content only; Addgene's
    own description text is stripped.
  delta_from_normative: |
    Standard v0.2 corpus posture excludes Addgene-mediated sequence ingestion.
    This override permits depositor-owned sequence content with Addgene-authored
    metadata stripped. Strip protocol documented in tools/corpus/addgene_safe_strip.py
    (lands at next curation pass).
```

---

## 7. Recommendations

**Recommendation 1 (no-override, executable now):** Land mScarlet3 via Nature Methods supplementary fetch. Land 2-3 vendor backbones via aggressive NCBI re-search. Total expected yield: 4-6 records, no compliance friction.

**Recommendation 2 (defer):** Schedule a dedicated curation session for iGEM Registry mining (CC-BY-SA partition routing exercise) and patent-disclosure mining (Studier pET, Invitrogen pPICZ, lentiviral patents). Expected yield: 8-12 records.

**Recommendation 3 (user approval required, propose):** For each of the 4 lentiviral / pCAGGS / pET-28a backbones that the v0.2 cadence flagged as critical for ML training, request the user to manually download the depositor-deposited Addgene GenBank file via their Addgene account, and supply the .gb file to the curator. Curator strips Addgene-authored metadata and emits a `provenance.notes` field documenting the depositor-owned source distinction. **No automated Addgene access; no BR-16 violation.** Expected yield: 4-6 records.

**Recommendation 4 (user approval required, defer):** The 107-record SnapGene cross-check pass — the only genuine BR-16 override case in this backlog — should be batched (e.g., 20 records per batch) with explicit per-batch user approval logged in `docs/ml_corpus/override_log.yaml`. Each batch lands as `snapgene_crosscheck.checked: true` with `discrepancy_resolution` populated. This unlocks the release-gate's ≥ 90% / ≥ 95% threshold.

**Final recommendation: invoke the override only at Recommendation 4** (BR-16 cross-check pass). Recommendations 1-3 sit inside the existing compliance envelope and do not require any override.

---

## 8. What this session delivers

This session implements **Recommendation 1 only.** The implementation comprises:

1. mScarlet3 fetch via Nature Methods supplementary URL.
2. Aggressive NCBI re-search yielding 2-3 vendor backbones if available.
3. Updated `corpus_manifest.yaml` aggregates.
4. CI gates re-verified all green.
5. This document committed for the user's review of Recommendations 2-4.

Recommendations 2, 3, and 4 remain documented backlog and require the user's explicit go-ahead before further action. No BR-16 override has been invoked in this session.

---

## Disclaimer

> **Disclaimer**: This scientific analysis is provided for informational, research, and
> advisory purposes only. It does not constitute professional engineering advice, medical
> advice, or formal peer review. All hypotheses and experimental designs should be
> validated through appropriate laboratory experimentation and, where applicable, reviewed
> by qualified domain experts before implementation. The author is an AI assistant and
> the analysis should be treated as a structured starting point for further investigation.

---

## Cross-references

- [[cev-workflow-discipline]] — standing 10-step working principle
- [[pitfall-cp1252-path-print]] — avoid printing absolute Paths on Windows stdout
- ARCHITECTURE.md § 9.6 — Fork-Readiness Memorandum (NORMATIVE)
- REQUIREMENTS.md § 11.7 — BR-15..17 (BR-16 SnapGene posture)
- IP-audit § 5.2 — sequence/annotation license split
- IP-audit § 8.1 — Tier-1/Tier-2/Tier-3 provenance allowlist
- corpus_manifest.yaml::maintenance.population_notes — running backlog
