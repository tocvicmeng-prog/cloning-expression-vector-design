# IP / ToS Audit — Host / Marker / ML-Corpus Enrichment

**Project:** Cloning & Expression Vector Design Toolkit (post-`v0.1.0`, GPL-3.0, owned by GMExpression Pty Ltd / GMES)
**Document type:** IP-auditor analysis (cadence step 4) — ToS opinion + per-source license matrix
**Author:** `/ip-auditor`
**Date:** 2026-05-23
**Jurisdictions:** Australia + United States (California focus)
**Upstream briefs:**
- `docs/handover/2026-05-23_host_marker_ml_corpus_initial_report.md` (accepted)
- `docs/handover/2026-05-23_host_marker_ml_corpus_architect_analysis.md` (parallel step 3)
**Status:** **DRAFT — pending user acceptance.** No `REQUIREMENTS.md`, `ARCHITECTURE.md`, `CODING_AGENDA.md`, `TASK_BOARD.md`, `schemas/*`, `catalogues/*`, `src/*`, or `docs/ml_corpus/*` changes have been made in this turn.

---

## 0. Working principle reference

This audit is produced under the project's standing 10-step cadence ([[cev-workflow-discipline]]). Step 4 runs in parallel with step 3 (architect analysis, delivered). Both must be accepted by the user (step 5) before the cadence advances to step 6 (REQUIREMENTS.md update).

---

## 1. Methodological caveats — read first

These caveats apply to every clause citation, license-grade verdict, and caselaw reference in this document.

### 1.1 Knowledge cutoff
The author's training data cutoff is **January 2026**. The user's stated session date is 2026-05-23 — a ~5-month gap. Within that gap:
- SnapGene / Dotmatics may have published a new ToS or EULA edition (vendor ToS revisions are typically quarterly).
- US and Australian AI-training caselaw is actively evolving (multiple pending cases — see § 1.4).
- iGEM / parts.igem.org transitioned governance to the AfterParty Foundation in 2024 and may have refined its default-license posture further.
- Addgene, NCBI/INSDC, FPbase, and JBEI ICE policy pages may have changed.

**Consequence:** every ToS clause citation in this document is **REQUIRES FRESH RETRIEVAL** before any committed action. The fresh retrieval must be performed by a human (not by automated scraping of the very pages whose ToS we are assessing).

### 1.2 No fabricated clause text
Per the ip-auditor protocol, I will not quote a ToS clause unless I can identify it from training data. Where the *general pattern* of such a clause is well-known but I cannot identify a verbatim 2026-edition clause, I describe the pattern, label it as **pattern-based inference**, and flag a verification action.

### 1.3 Author is not a licensed attorney
This document is an AI-assistant analysis. It is not legal advice. For any commercial deployment, training-run, or public-facing release decision based on this audit, the user should engage:
- An Australian registered patent / IP attorney (for AU posture).
- A US-licensed attorney with copyright + AI-data-rights practice (California-licensed counsel preferred for project owner's jurisdiction of operation).

### 1.4 Caselaw posture as of training cutoff
The following US cases are real and were active or recently decided as of the training cutoff. Holdings on AI training data are jurisdiction-by-jurisdiction and case-by-case. **Do not rely on a single-case rule for project-wide policy.**

- *Authors Guild v. OpenAI* (S.D.N.Y., filed 2023) — class action re: training on copyrighted books.
- *New York Times v. Microsoft & OpenAI* (S.D.N.Y., filed 2023-12) — large news-corpus training case.
- *Bartz v. Anthropic* (N.D. Cal., filed 2024) — book-training fair-use dispute; partial summary-judgment ruling in 2024 held the training step itself was fair use but ingestion of pirated copies was not — **verify current status**.
- *Andersen v. Stability AI* (N.D. Cal., filed 2023) — image-generation training; some claims survived motion to dismiss.
- *Getty Images v. Stability AI* (E.D. Va., filed 2023; UK High Court parallel) — image-training and trademark issues.

Australian equivalents are sparser. The Australian Copyright Act 1968 does **not** have a US-style fair-use doctrine; it has *fair dealing* under specific purposes (s40 research/study, s41 criticism/review, s41A parody/satire, s43 judicial proceedings, s103C reporting of news), and a narrower text-and-data-mining posture than the EU. There is no Australian appellate ruling specifically endorsing commercial ML training on third-party copyrighted data as of training cutoff.

### 1.5 Database compilation rights — the *Feist* / *Telstra* axis
- **United States:** *Feist Publications, Inc. v. Rural Telephone Service Co.*, 499 U.S. 340 (1991). Facts are not copyrightable; mere compilations lacking creative selection/arrangement are not copyrightable ("sweat of the brow" rejected).
- **Australia:** *Telstra Corporation Ltd v Phone Directories Co Pty Ltd* [2010] FCAFC 149. Australian courts followed *Feist* in substance: telephone directories without human creative input not protected as original literary works.
- **Consequence for sequence databases:** a database of natural DNA sequences (e.g., NCBI/INSDC) is not protected by copyright in either jurisdiction. **Annotation overlays** that involve curator judgement (gene boundaries, functional labels, qualifier text) may be protected as creative selection/expression, jurisdiction-dependent.

---

## 2. Scope inherited from initial report (confirmed)

| Item | Posture |
|---|---|
| Track A (host strains) | No IP exposure — strain names + genotypes are factual; vendor catalogue IDs are factual references. Audit out of scope here. |
| Track B (markers catalogue) | No IP exposure — antibiotic + gene names + working concentrations are factual; Sambrook 4th ed. citations follow standard scientific-citation fair-dealing. Audit out of scope here. |
| **Track C (ML training corpus)** | **In scope.** Per-source license matrix + SnapGene posture + iGEM contagion + GPL compatibility all live here. |

User Decision #4 (SnapGene index-only + manual cross-check) is the central question for § 3 below.

---

## 3. SnapGene — Section A

### 3.1 Vendor and product surfaces

- **Operator:** SnapGene is a Dotmatics product line (formerly GSL Biotech LLC; transitioned via Insightful Science → Dotmatics; the Dotmatics corporate identity dates from the Insightful Science merger circa 2021–2022).
- **Two relevant ToS / EULA surfaces:**
  - `snapgene.com` website Terms of Service (governs web access to the plasmid collection at `snapgene.com/plasmids` and deeper pages).
  - SnapGene Desktop / SnapGene Viewer End-User License Agreement (governs software use and the `.dna` file format).
- **Trademarks:** SnapGene® is a registered trademark of Dotmatics in multiple jurisdictions. USPTO and IP Australia trademark records can confirm specifics — **REQUIRES FRESH RETRIEVAL** at filing time.

### 3.2 Pattern-based clause inventory (NOT verbatim quotes)

Based on the general SaaS-of-this-class ToS pattern that I can identify across the cohort (Benchling, Geneious, Snapgene, GENEWIZ tools, etc.) as of training cutoff:

| Clause family | Typical posture | Confidence | Action |
|---|---|---|---|
| Automated extraction / scraping | Prohibited. Standard clause forbids "use of crawlers, robots, scripts, or automated data-extraction tools to access or copy any portion of the Service or its content". | High pattern-confidence; specific 2026 wording requires fresh retrieval | Verify before any pipeline that touches `snapgene.com`. |
| Rate-limit / bandwidth bypass | Prohibited. Typical clause forbids circumventing technical measures or accessing the Service in a manner that imposes "unreasonable load". | High pattern-confidence | Same. |
| Redistribution of platform content | Prohibited. Typical clause grants a personal, non-transferable license to USE displayed content for the user's own research; explicitly forbids "reproducing, redistributing, republishing, or making available to third parties" the Service's content. | High pattern-confidence | Same. |
| Derivative-data creation for distribution | Prohibited where the derivative substantively reproduces platform content; typically silent on derivative analyses that don't include the source content. | Medium pattern-confidence | Verify; this is the line our "index-only + cross-check" posture sits on. |
| AI/ML training restrictions | Increasingly explicit since ~2023–2024. Many vendor ToS now include a specific clause: "You may not use the Service or its content to train, test, evaluate, fine-tune, or develop machine-learning models." | Medium pattern-confidence (rapidly evolving — many vendors added this language late 2023 / 2024) | Critical: verify the SnapGene 2026 ToS for an explicit ML clause. **REQUIRES FRESH RETRIEVAL.** |
| Trademark / branding | Standard nominative-fair-use carve-out is rare in vendor ToS; the typical clause asserts trademark protection broadly. | High pattern-confidence | Use the SnapGene name nominatively only (see § 3.4). |

**I am not able to quote the verbatim SnapGene 2026 ToS clauses from training data with confidence.** A user (or counsel) must retrieve the current ToS pages at filing time, archive them with a timestamp (e.g., perma.cc), and confirm or refute these pattern inferences. The recommendation in § 3.3 below assumes the patterns above hold; if the actual 2026 ToS is materially looser (e.g., explicit "you may use this for research reference") or stricter (e.g., explicit ML-training prohibition), the recommendation must be re-issued.

### 3.3 Opinion on user Decision #4: "INDEX-ONLY + MANUAL CROSS-CHECK"

The proposed posture, restated for legal analysis:
- A human researcher legitimately accesses `snapgene.com/plasmids/...` pages via a standard web browser.
- The researcher does not run any automated extraction.
- The researcher does not store any sequence, annotation, description, image, or other SnapGene-authored content into the project repository.
- The researcher *may* store, in `crosscheck_log.yaml`, the SnapGene record IDENTIFIER (a plasmid name or a SnapGene URL), the date of check, a boolean match flag, and — if there is a discrepancy — a short researcher-authored description of the discrepancy.
- The ingested sequence in `docs/ml_corpus/records/...` is obtained from a separate, cleaner-licensed source (NCBI, EBI, iGEM, vendor primary publication).

**Legal posture:**

**United States (California):**
- **Access to the page itself:** Provided the researcher is using a standard browser and is not bypassing technical measures, mere browser-display use is consistent with the standard ToS licence-to-use grant. The *hiQ Labs v. LinkedIn* (9th Cir. 2022) line of authority addressed automated scraping under the CFAA but did not authorise unlimited use — and we are not scraping in this scenario.
- **Visual fact-checking of a sequence:** Comparing two sequences in one's head is not a "use" of SnapGene's expression. The factual content (which bases are at which positions) is not copyrightable per *Feist*. The researcher's eyes processing it is not a derivative-use act.
- **Storing the SnapGene plasmid NAME and URL:** Names of vendor-published plasmids (e.g., "pET-28a(+)") are not SnapGene's IP — they are community-standard names from the originating vendor (Novagen in this example). URLs are themselves not copyrightable per *Ticketmaster v. Tickets.com* (C.D. Cal. 2003) and related authority. Storing the URL slug is a citation, not a reproduction.
- **The discrepancy-resolution free-text field is the risk surface.** If the researcher writes verbatim what a SnapGene annotation says ("SnapGene labels positions 1234–1456 as 'lacI repressor (V20A)'"), they have quoted SnapGene-authored annotation text. A short, factual quotation for cross-check purposes likely falls within US fair use (17 U.S.C. § 107) given (i) transformative purpose (scientific QC), (ii) tiny amount used, (iii) no market harm. But this is fact-dependent and not absolute.
- **Conclusion (US):** The "index-only + cross-check" posture as described is **likely permissible**, subject to (a) verification that the 2026 SnapGene ToS does not include an explicit ML-pipeline clause that this activity might be deemed to fall within, and (b) keeping `discrepancy_resolution` text minimal, factual, and researcher-authored (no verbatim long quotations from SnapGene).

**Australia:**
- **No fair use; fair dealing only.** The relevant exceptions under Copyright Act 1968 are s40 (research/study), s41 (criticism/review), and s103C (news reporting). s40 fair dealing for research and study is the applicable exception for the cross-check scenario.
- **s40 fair dealing factors (s40(2)):** purpose and character; nature of the work; possibility of obtaining the work commercially within reasonable time at ordinary commercial price; effect of dealing on potential market; amount and substantiality. A brief manual cross-check for scientific QC purposes, copying nothing into the repository, plausibly satisfies s40.
- **Contract overrides:** Australian doctrine recognises that contractual terms (including ToS) can override default copyright exceptions — *Re Copyright Act 1968 (Cth) and Phonographic Performance Co of Australia Ltd's application* [1981]. So if the SnapGene 2026 ToS expressly prohibits use for research cross-check or ML-pipeline purposes, that contractual term may bind the researcher regardless of s40.
- **Conclusion (AU):** Same as US — likely permissible, but subject to the same two caveats, with extra weight on the ToS-contract-override risk because AU has no broad fair-use safety net.

**Recommendation:** Adopt the posture, with these guardrails:
1. Re-verify the SnapGene 2026 ToS at the time of any ingestion activity (and re-verify quarterly thereafter).
2. Constrain `discrepancy_resolution` text to researcher-authored, factual, ≤ 200 characters per entry. Include explicit field guidance in `docs/ml_corpus/README.md`: *"Describe the discrepancy in your own words. Do not quote SnapGene annotation or description text."*
3. Do not access `snapgene.com` via any non-browser tool from any pipeline this project runs. No `curl`, no `wget`, no headless browser, no scraping framework, no MCP web-fetch. The access path is "a human opens a tab in their personal browser".
4. If the 2026 ToS includes an explicit prohibition on use of SnapGene-displayed information for ML-related purposes, halt the cross-check programme even if our use is fact-only — until counsel reviews.

### 3.4 Naming SnapGene in public-facing project documentation

**Legal posture:** Nominative use of a registered trademark to refer to the product itself is generally permissible.

- **United States:** *New Kids on the Block v. News America Publ'g, Inc.*, 971 F.2d 302 (9th Cir. 1992) — three-factor nominative fair-use test: (1) product not readily identifiable without the trademark; (2) only as much of the mark used as reasonably necessary; (3) nothing done to suggest sponsorship or endorsement.
- **Australia:** No formal "nominative fair use" doctrine; the equivalent protection comes from Trade Marks Act 1995 s122(1)(b)(i) (good-faith descriptive use) and s122(1)(c) (good-faith indication of intended purpose). Use of "SnapGene" to factually describe what it is is generally allowed if the use is in good faith and does not suggest endorsement.

**Risk:** False-endorsement / sponsored-by impression. If our README implies "SnapGene-verified" as a quality badge, both jurisdictions could find a misleading-association claim.

**Recommended language for all public-facing references (README.md, traceability_index.md, ML-corpus README, crosscheck_log.yaml header):**

> SnapGene® is a registered trademark of Dotmatics. This project is not affiliated with, endorsed by, sponsored by, or in any way officially connected to Dotmatics or SnapGene. SnapGene is referenced as a third-party scientific reference resource used for manual QC of sequences ingested from independent sources.

Place this disclaimer (or equivalent counsel-approved wording) wherever SnapGene is named.

### 3.5 Storing SnapGene record identifiers in `crosscheck_log.yaml`

| What you store | Posture |
|---|---|
| The plasmid's community-standard name (e.g., `"pET-28a(+)"`, `"pPICZ-α-A"`, `"pUC19"`) | **Safe.** This is the originating vendor's name, not SnapGene's IP. It is also a scientific fact-of-identity. |
| A `snapgene.com` URL slug (e.g., `"snapgene.com/plasmids/pet_and_duet_vectors/pet-28a(+)"`) | **Safe as a citation.** Per *Ticketmaster v. Tickets.com* (US) and analogous AU authority, URLs are not copyrightable as such. |
| A SnapGene-INTERNAL identifier system (e.g., a numeric ID SnapGene assigns to its plasmid records, if any exists) | **Avoid.** If SnapGene operates an internal cataloguing system that they consider proprietary, lifting those identifiers wholesale could be argued as misappropriation of their compilation. |
| Cross-check date + researcher name + match flag | **Safe.** This is project-authored metadata about an activity, not reproduction of any SnapGene content. |
| Discrepancy resolution text | **Safe iff researcher-authored, factual, brief.** See § 3.3 recommendation #2. |

**Recommendation:** prefer the community-standard plasmid name + a SnapGene URL slug as the cross-check anchor. Document this convention explicitly in `docs/ml_corpus/README.md`.

---

## 4. Per-source license matrix — Section B

**Legend:**
- ✅ = clear and unambiguous in source documents within training data
- ⚠️ = conditional, depends on per-record or per-deposit license; case-by-case review required
- ❌ = restricted; do not use without specific permission
- ❓ = uncertain in training data; **REQUIRES FRESH RETRIEVAL** before any reliance

### 4.1 INSDC partners (NCBI / EBI / DDBJ)

| Field | NCBI Nucleotide / GenBank | EBI ENA | DDBJ |
|---|---|---|---|
| Controlling URL | https://www.ncbi.nlm.nih.gov/genbank/policy/ | https://www.ebi.ac.uk/ena/browser/about/policies | https://www.ddbj.nig.ac.jp/policies-e.html |
| Redistribution_allowed | ✅ Yes | ✅ Yes | ✅ Yes |
| ML_training_allowed | ✅ Yes (no restriction from data source) | ✅ Yes | ✅ Yes |
| Attribution_required | ⚠️ Not strictly required (records are factual/public-domain); customary scientific citation expected | ⚠️ Same | ⚠️ Same |
| Commercial_use_allowed | ✅ Yes | ✅ Yes | ✅ Yes |
| Notes | US federal records — public domain. INSDC partner policy explicitly states no restrictions on use. Sequence is factual data (*Feist*) — not copyrightable in either AU or US. | EBI is INSDC partner; EBI also has its own "EMBL-EBI Terms of Use" — confirm at fresh retrieval. | INSDC partner; Japanese government / National Institute of Genetics. |

**Verdict:** Tier-1 input sources. Ingest freely with customary attribution.

### 4.2 iGEM Registry of Standard Biological Parts

| Field | Value |
|---|---|
| Controlling URL | https://parts.igem.org/Help:Contents (and the iGEM Foundation / AfterParty Foundation policy pages) ❓ |
| Operator history | iGEM Foundation operated the registry historically; transitioned to the AfterParty Foundation in 2024 governance restructure. Confirm current operator at fresh retrieval. |
| Redistribution_allowed | ⚠️ Yes for parts with explicit CC0 / CC-BY / CC-BY-SA tags; per-part variable |
| ML_training_allowed | ⚠️ CC0 yes; CC-BY yes (with attribution); CC-BY-SA conditional on share-alike acceptance (see § 6 below); explicit-prohibition parts: no |
| Attribution_required | ⚠️ Depends on per-part license tag |
| Commercial_use_allowed | ⚠️ CC0 / CC-BY yes; CC-BY-SA yes but share-alike binds; explicit "non-commercial" parts: no |
| Notes | iGEM's overall use policy historically encouraged research use; commercial use was technically allowed but informally discouraged. Many parts retain CC-BY-SA from the original BioBrick spec era. New deposits since the 2024 transition trend toward CC0 — **confirm current default at fresh retrieval.** |

**Verdict:** Tier-2 input source. Per-record license review is mandatory. Architect Q7 contagion question is real and unresolved (see § 6 below).

### 4.3 JBEI ICE (public instance)

| Field | Value |
|---|---|
| Controlling URL | https://public-registry.jbei.org/ — operating policy is at the site's About page ❓ |
| ICE software license | BSD (the platform code itself is open source). |
| Per-deposit license | ⚠️ Variable. ICE supports a per-record license field; deposits range from public-domain to MTA-restricted. |
| ML_training_allowed | ⚠️ Per-record; review each. |
| Notes | JBEI public registry deposits are often associated with peer-reviewed publications and follow journal/depositor policy. ICE platform code is BSD but that doesn't license the deposit content. |

**Verdict:** Tier-2 source. Per-record review mandatory.

### 4.4 DNASU Plasmid Repository (ASU / Biodesign)

| Field | Value |
|---|---|
| Controlling URL | https://dnasu.org/DNASU/UseRestrictions.do (or the DNASU policy page) ❓ |
| Physical MTA vs in-silico use | The DNASU MTA governs PHYSICAL DNA shipment between research labs. It is not engaged by purely in-silico use of the publicly-available sequence record. |
| ML_training_allowed | ⚠️ Sequence records that originate from public deposits (linked to GenBank accessions) inherit the public-domain posture. DNASU-curated metadata may have additional posture — confirm. |
| Notes | The natural workflow is to fetch the underlying GenBank accession (which is INSDC, public-domain) and use DNASU only as a discovery aid. |

**Verdict:** Tier-1 if used via the upstream GenBank accession; Tier-2 if relying on DNASU-curated metadata.

### 4.5 Addgene — metadata vs depositor sequence files (treated separately)

| Field | Addgene metadata (descriptions, depositor notes, Addgene-authored content) | Addgene-hosted depositor sequence files |
|---|---|---|
| Controlling URL | https://www.addgene.org/terms-of-use/ ❓ + https://www.addgene.org/privacy/ ❓ | Per-depositor license; usually points to the publication that deposited the plasmid. |
| Redistribution_allowed | ⚠️ Conditional. Addgene website terms typically restrict redistribution of their site content; metadata fields curated by Addgene staff have a clearer Addgene-authored posture. | ⚠️ Per-depositor. Depositor sequences are typically from published research and often public-domain-equivalent in substance, but Addgene's site is the delivery channel and the website ToS may impose secondary restrictions. |
| ML_training_allowed | ❌ / ⚠️ Treat conservatively — Addgene-authored metadata text should not be bulk-ingested for training. | ⚠️ Trace each sequence back to its underlying published source (GenBank accession or primary literature). |
| Attribution_required | Yes (Addgene credit) | Yes (depositor + publication credit) |
| Commercial_use_allowed | ⚠️ Subject to Addgene's terms | ⚠️ Subject to depositor's posture |
| Recommendation | **Use Addgene as a discovery index only.** Browse to find plasmids of interest; then fetch the actual sequence from the depositor's underlying NCBI / EBI accession (which Addgene records consistently link). Do NOT bulk-download Addgene's SnapGene `.dna` files or HTML pages into the corpus. | **Fetch upstream.** Never include "Addgene-hosted" as the corpus `provenance.source`; always cite the underlying INSDC accession or primary publication. |

**Verdict:** Discovery aid only. Architecturally this means the `provenance.source` enum in the corpus record schema (§ 2.3 of architect analysis) should remove `addgene_metadata_only` as an in-corpus option OR clarify that records carrying that source are flagged for case-by-case clearance, never ingested as a default-allow.

### 4.6 Vendor-published maps and manuals

The general legal pattern for vendor materials:
- Vendor manuals are copyrighted by the vendor; verbatim reproduction is not permitted.
- The **biological sequence** of a vendor's empty backbone is typically published in primary literature (e.g., Studier 1990 for the pET system, Cregg 1988 for Pichia vectors). Cite the primary literature for the sequence; the vendor manual is the rough discovery aid.
- The **annotation** in a vendor manual is the vendor's curated layer — handle as a copyrightable expression for the same reasons as the SnapGene annotation question.

| Vendor | Comments | Verdict |
|---|---|---|
| Invitrogen / Thermo Fisher (incl. Pichia Expression Kit K1710 manual) | Sequences for pET-like, pTrc-like, pBAD-like, pPICZ, pPIC, pAO815, pYES2 etc. mostly traceable to primary publications + NCBI deposits. | Use primary-lit + NCBI; do not bulk-ingest manual annotation. |
| Novagen / Merck Millipore (pET system Tech Bull TB055) | pET vector lineages — Studier 1990 (PMID 2199796, *Methods Enzymol.*) is the canonical primary reference. | Same. |
| Lucigen | Stbl3, Stbl4 vendor genotypes — cite vendor manual for genotype (factual); strain itself is BSL-1 *E. coli*. | Manual citation for genotype is fine (factual). |
| NEB (New England Biolabs) | BL21(DE3), BL21 Star, and various lambda-DE3 derivatives are NEB SKUs but the underlying biology is from primary lit (Studier line). | Cite primary lit; NEB catalogue ID is a factual SKU citation. |
| Stratagene / Agilent | XL1-Blue, Origami, Origami B, SHuffle lineage references — Bessette 1999 (PMID 10590025) is canonical primary for Origami. | Same. |
| Takara / Clontech | pIRES, pCMV, yeast two-hybrid (AH109, Y187) — vendor manuals carry strain genotype tables; underlying biology from primary lit. | Same. |
| Promega | pGEM family + accessory backbones — primary-lit traceability strong. | Same. |
| IDT (Integrated DNA Technologies) | Mostly oligonucleotide synthesis service, not a backbone-supplier in the corpus sense. | Out of corpus scope. |
| Twist Bioscience | Same as IDT — synthesis service. | Out of corpus scope. |

**Verdict (vendors):** Tier-2 source, used as discovery aids. Final sequence + annotation come from primary lit or INSDC.

### 4.7 FPbase (fluorescent-protein database)

| Field | Value |
|---|---|
| Controlling URL | https://www.fpbase.org/about/ — review FPbase data-use policy ❓ |
| Operator | Operated by Talley Lambert at Harvard Medical School; community-curated. |
| Per-record license | Most FPbase entries are CC0 or CC-BY-equivalent. Sequences themselves are derived from published PDB/UniProt/primary-lit deposits. |
| ML_training_allowed | ✅ Likely yes for CC0 entries; ⚠️ for CC-BY (attribution required). |
| Notes | FPbase maintains attribution to the underlying primary publication for each protein. |

**Verdict:** Tier-1 for CC0 entries; Tier-2 for CC-BY.

### 4.8 Primary literature (journal-by-journal)

The default pattern: **sequence data** deposited in support of a paper is required by most major journals to be in INSDC at the time of publication. The INSDC deposit is what we ingest. The PAPER TEXT and PAPER FIGURES are copyrighted by the journal (or under journal-specific open-access licenses).

| Journal | Sequence-deposit policy | Posture |
|---|---|---|
| Nature, Science, Cell, PNAS | All require INSDC deposit for new sequences. | Fetch sequence from INSDC; cite paper. |
| Nucleic Acids Research (NAR) | Open access (CC-BY); requires INSDC deposit. | Same; paper text is CC-BY. |
| PLoS (One, Biology, etc.) | CC-BY; requires INSDC deposit. | Same. |
| ACS Synth Biol, ACS journals | Subscription; requires INSDC deposit. | Same. |
| MBoC, J Bacteriol, J Virol (ASM journals) | Subscription / hybrid; requires INSDC deposit. | Same. |

**Verdict:** Tier-1 for the underlying sequence deposit. Paper text is the journal's IP — do not ingest paper figures or paper text into the training corpus; cite only.

---

## 5. Sequence vs annotation license divergence — Section C (and architect Q8)

### 5.1 Substantive opinion

**Yes, the corpus_record schema should split `license` into `sequence_license` + `annotation_license`.**

Legal reasoning:
- **Sequence (the ACGT bases):** factual data per *Feist* (US) and *Telstra* (AU). Not copyrightable. A pUC19 backbone sequence retrieved from NCBI (accession L09137) is in the public domain regardless of who hosts it.
- **Annotation overlay:** involves curator judgement — choice of which features to label, where exactly to draw feature boundaries, which qualifier terms to use, what notes to attach. This curatorial work is potentially copyrightable as a creative selection/expression. A vendor-curated annotation atop a public-domain sequence has a vendor-claimed expression layer.
- **The risk pattern:** ingesting a sequence with its annotation from a vendor manual or from Addgene-hosted depositor-curated files mixes a clean-license sequence with a potentially-encumbered annotation. The current single-license corpus_record schema cannot represent this divergence cleanly.

### 5.2 Schema fragment (proposed extension to architect § 2.3)

```json
{
  "license": {
    "type": "object",
    "required": ["sequence_license", "annotation_license"],
    "properties": {
      "sequence_license": {"$ref": "#/$defs/license_block"},
      "annotation_license": {"$ref": "#/$defs/license_block"}
    }
  },
  "$defs": {
    "license_block": {
      "type": "object",
      "required": [
        "spdx_id",
        "redistribution_allowed",
        "ml_training_allowed",
        "attribution_required",
        "source_text_url"
      ],
      "properties": {
        "spdx_id": {"type": "string", "minLength": 1},
        "redistribution_allowed": {"type": "boolean"},
        "ml_training_allowed": {"type": "boolean"},
        "attribution_required": {"type": "boolean"},
        "attribution_text": {"type": "string"},
        "commercial_use_allowed": {"type": "boolean"},
        "source_text_url": {"type": "string", "minLength": 1},
        "notes": {"type": "string"}
      }
    }
  }
}
```

This is a backward-incompatible change to the architect's § 2.3 draft (single-license block becomes two). Recommend the schema is bumped to v1.1 before any record is committed; alternatively the architect's § 2.3 draft is amended in step 8 of the cadence to bake this in from v1.0.

### 5.3 Recommended ingestion rule

Every corpus record's effective license is the **minimum** (least permissive) of `sequence_license` and `annotation_license`. The aggregate `corpus_manifest.yaml` reports both per-field license coverage and the resulting effective-license distribution.

If `annotation_license.ml_training_allowed` is `false` while `sequence_license.ml_training_allowed` is `true`, the record may still enter the training corpus **with the annotation stripped** — i.e., a sequence-only entry. Implementation rule: the ingestion tooling enforces this stripping automatically and logs each strip event for auditability.

---

## 6. iGEM CC-BY-SA contagion — Section D (and architect Q7)

This is a **genuinely unsettled** legal question. The honest answer below splits it into three sub-questions and gives the most defensible posture for each.

### 6.1 Does CC-BY-SA training data make the trained model a "derivative work"?

**Posture varies by jurisdiction and is unsettled:**

- **United States:** No appellate ruling directly on point as of training cutoff. Trial-court trends (see *Bartz v. Anthropic* partial summary judgment 2024) suggest the act of *training* a model may be fair use, but this is fact-specific and the model itself may or may not be a "derivative work" of the training data. The Creative Commons organization has published informal guidance suggesting that CC-BY-SA's share-alike obligation depends on whether the trained model embodies the licensed content in a "recognizable form" — many AI models do not, but some image-generation and verbatim-text-emission models arguably do.
- **Australia:** No authoritative ruling. The Copyright Act 1968's reproduction-and-adaptation framework would need a case to settle the question.
- **European Union (informational reference; project's stated jurisdictions are AU + US):** The EU DSM Directive (2019/790) Article 4 TDM exception provides a path that may sidestep this — but the project's jurisdictions are AU + US, where no equivalent applies.

**Defensible posture:** treat the trained model as **potentially a derivative work** of CC-BY-SA training data, and design the ingestion pipeline so that a CC-BY-SA-free training run is always available.

### 6.2 Does the SA obligation propagate to (a) the corpus, (b) the model, (c) model outputs?

| Layer | If CC-BY-SA propagates | If it doesn't |
|---|---|---|
| (a) Corpus itself | Must be distributed under CC-BY-SA-compatible terms. | Can be distributed under any terms. |
| (b) Trained model | Model weights must be CC-BY-SA-compatible (if redistributed). | Model weights can be any license. |
| (c) Model outputs | Each generated sequence inherits CC-BY-SA. | Outputs are unencumbered. |

The CC license family explicitly addresses "adaptations" and "share-alike." Whether ML model weights are "adaptations" is the contested point.

### 6.3 Recommended posture for this project

**Adopt the architect's Q7 split-folder recommendation (which is correct):**

1. Records with `sequence_license.spdx_id` or `annotation_license.spdx_id` of `CC-BY-SA-*` (any version) are stored in `docs/ml_corpus/records/cc-by-sa/` (and only there).
2. The `corpus_manifest.yaml` maintains two effective training-set partitions:
   - **`partition: full`** — includes all records (CC0, CC-BY, CC-BY-SA, public-domain).
   - **`partition: sa_free`** — excludes the cc-by-sa subfolder. Used when training a model intended for commercial deployment without share-alike obligation.
3. Any model release ships with metadata declaring which partition it was trained on.
4. If `partition: full` is used to train a release candidate that will be deployed commercially without share-alike, **counsel review is required before release**.

This is the gating mechanism the user can choose between later — it doesn't force the choice today; it makes the choice explicit and reversible.

---

## 7. Project licensing posture — Section E

### 7.1 GPL-3.0 (the project) vs CC-BY-SA training data: any conflict?

**Three layers, three license regimes, no direct conflict:**

| Layer | License | Relationship |
|---|---|---|
| Project software (the toolkit, training scripts, ingestion pipeline) | GPL-3.0 | The GPL governs the *code* that processes data. It does not require the *data being processed* to be GPL-licensed. |
| Training corpus data | Per-record (CC0 / CC-BY / CC-BY-SA / vendor / public-domain) | Data carries its own license; not GPL. |
| Trained model weights | TBD by the user (separate licensing decision) | Per § 6, may or may not carry obligations from the training data. |

**Confirmation:** the trained model is NOT being redistributed under GPL-3.0 — it's a separate artefact. The GPL on the toolkit code is unaffected by the data licenses, and no GPL-vs-CC-BY-SA "compatibility" question arises at the source-code layer.

### 7.2 Attribution-required data and GPL

GPL-3.0 § 7 permits "additional terms" that require attribution. A CC-BY training-data attribution requirement satisfied via the `corpus_manifest.yaml` aggregate report does not conflict with GPL-3.0 of the toolkit code.

### 7.3 Practical recommendation

Add a `LICENSES/` directory under `docs/ml_corpus/` containing the full text of each license referenced in the corpus (CC0, CC-BY-4.0, CC-BY-SA-4.0 family, etc.). This is the canonical way to ship multi-licensed data; corresponds to SPDX best practice.

---

## 8. Risks + recommendations — Section F

### 8.1 Source tier list (recommended explicit denylist / allowlist / flag-list)

| Tier | Sources | Posture |
|---|---|---|
| **Allowlist (Tier-1, ingest freely)** | NCBI Nucleotide / GenBank; EBI ENA; DDBJ; FPbase CC0 entries; primary-literature deposits via their INSDC accessions. | Default-allow. |
| **Flag-list (Tier-2, ingest with per-record review)** | iGEM Registry (per-part license check; CC-BY-SA routed to subfolder); JBEI ICE (per-deposit license check); DNASU (use as discovery aid; ingest via upstream GenBank); FPbase CC-BY entries (attribution captured); vendor-published maps + manuals (use as discovery aid; ingest sequence from primary lit). | Per-record check; logged in `provenance.notes`. |
| **Denylist (Tier-3, do not ingest)** | SnapGene `.dna` files; SnapGene plasmid-page HTML; SnapGene-authored annotations or descriptions; Addgene bulk metadata; paywalled journal figures / text; vendor manual annotations (only the underlying sequence from primary lit, never the vendor's annotation layer). | Hard exclusion. Enforce via `corpus.source` enum (no Tier-3 source IDs in the schema). |

### 8.2 Corpus manifest license-aggregate reporting

`corpus_manifest.yaml` should expose, for an upcoming release gate:

```yaml
license_aggregate:
  total_records: <N>
  by_sequence_license:
    CC0-1.0: <count>
    CC-BY-4.0: <count>
    CC-BY-SA-4.0: <count>
    public-domain: <count>
    "other-or-unknown": <count>
  by_annotation_license:
    # same shape
  effective_license_distribution:
    # min of sequence + annotation, per record, aggregated
  partition_sa_free:
    record_count: <N - cc_by_sa_count>
    fraction: <N / total>
  attribution_obligations:
    records_requiring_attribution: <count>
    attribution_text_file: "docs/ml_corpus/ATTRIBUTIONS.md"
  cross_check_coverage:
    # per architect § 5.2
    checked: <count>
    unchecked: <count>
    fraction_checked: <0.0–1.0>
```

The release-gate script (architect § 5.2 mentions `tools/release/corpus_release_gate.py`) reads this aggregate and enforces release-time criteria — for example:
- `fraction_checked >= 0.90` (SnapGene cross-check coverage)
- `effective_license_distribution['restricted'] == 0` (no records mislabelled as ingestable)
- `attribution_text_file` exists and is complete.

### 8.3 Specific recommendations for the joint plan

1. **Adopt the architect's `provenance.source` enum unchanged** but remove `addgene_metadata_only` as a default-allow source; route it through `exclusions.yaml` with a per-case override.
2. **Adopt the split sequence/annotation license schema** (§ 5.2 above) instead of the architect's single-license-block draft. This is a small schema change but important for legal clarity.
3. **Adopt the CC-BY-SA subfolder + partition strategy** (§ 6.3 above).
4. **Re-verify all ToS clauses cited in this audit at the time of ingestion implementation** — both `snapgene.com` and all vendor manuals' published-as-of-2026-05-23 ToS pages — by a human checker, with archival timestamping (perma.cc or equivalent).
5. **Engage IP counsel for one pass over the corpus release gate** before any commercial-deployment model is released. The release gate's automated checks reduce counsel cost but do not eliminate the need for a human review.
6. **Publish the SnapGene nominative-use disclaimer** (§ 3.4) in all public-facing documents that name SnapGene.

---

## 9. Open questions for joint plan — Section G

| # | Question | Needs input from |
|---|---|---|
| **IPQ-1** | Will the model trained on this corpus ever be deployed commercially, or is this a research-only artefact? Decision drives § 6 partition strategy and § 8.3 #5 (counsel review trigger). | **User decision.** |
| **IPQ-2** | Should the project maintain two training partitions (`full` + `sa_free`) in perpetuity, or commit now to one of them and reject the other? | User + scientific-advisor. |
| **IPQ-3** | Should we proactively seek explicit ML-training licenses from key vendors (Invitrogen/Thermo, NEB, Stratagene/Agilent) for their backbone sequences? Likely-easy yes for the underlying primary-lit deposits; might unlock cleaner ingestion of vendor-manual content. | User + counsel. |
| **IPQ-4** | Quarterly ToS re-check schedule — who runs it, what's archived, how is drift surfaced? | dev-orchestrator. |
| **IPQ-5** | Architect § 5.2 sets the SnapGene cross-check coverage release-gate at ≥ 90%. Is this the right number, given the legal posture in § 3? Higher coverage strengthens the "QC reference" framing; lower coverage weakens it. | scientific-advisor + architect. |
| **IPQ-6** | The split sequence/annotation license schema (§ 5.2) is a small backward-incompatible amendment to the architect's draft. Should architect's analysis be re-issued (formal step-3 re-emit), or is amending in step 8 acceptable? | architect + dev-orchestrator. |
| **IPQ-7** | Does the project want a formal `IP_POLICY.md` at the repo root that codifies the tier list (§ 8.1), the SnapGene posture (§ 3), and the CC-BY-SA partition strategy (§ 6.3)? Recommended yes — it's a counsel-facing artefact. | User decision. |
| **IPQ-8** | Trademark / nominative-use disclaimer (§ 3.4): one canonical location (e.g., `LICENSES/THIRD_PARTY_NOTICES.md`) or repeated in every README that names SnapGene? Recommended: one canonical file plus one-line references elsewhere. | architect. |
| **IPQ-9** | Should we add a CI gate that scans `docs/ml_corpus/records/**/*.json` for any field value that looks like a verbatim long quotation from vendor annotation (heuristic: long strings matching vendor manual phrasing)? Would catch accidental contamination. | dev-orchestrator. |
| **IPQ-10** | The training pipeline itself (`ml/` or `training/` folder per architect § 5.3) is out of scope for this enrichment, but its license-aware data loader will need to read `partition` from the corpus manifest. Should we stub the loader interface now or defer entirely? | scientific-advisor + architect. |

---

## 10. Acceptance checklist (mirrors architect format)

Before this audit is accepted (cadence step 5), please confirm or amend the following:

| # | Item | Default |
|---|---|---|
| AC-1 | All ToS clause citations in § 3 are pattern-based inferences requiring fresh retrieval at implementation time. | Accept. |
| AC-2 | The "INDEX-ONLY + MANUAL CROSS-CHECK" SnapGene posture (§ 3.3) is acceptable subject to the four guardrails listed. | Accept. |
| AC-3 | Public-facing references to SnapGene carry the nominative-use disclaimer text in § 3.4 (or counsel-approved equivalent). | Accept. |
| AC-4 | Allowlist / flag-list / denylist tier structure in § 8.1 is adopted as the corpus's source-allowability policy. | Accept. |
| AC-5 | Sequence-license vs annotation-license split (§ 5.2) is adopted; this is a small backward-incompatible amendment to the architect's § 2.3 draft. | Accept. |
| AC-6 | CC-BY-SA records are routed to `docs/ml_corpus/records/cc-by-sa/` with a `partition: sa_free` corpus-manifest variant maintained (§ 6.3). | Accept. |
| AC-7 | Trained model weights are NOT redistributed under GPL-3.0 — they are a separate artefact with their own licensing decision (§ 7.1). | Accept. |
| AC-8 | Tooling (any pipeline this project runs) must NOT access `snapgene.com` via any non-browser tool. Cross-check is performed by a human in a browser. | Accept. |
| AC-9 | All ten IPQ-1..IPQ-10 open questions are deferred to the three-skill joint plan (step 7), not resolved in this audit. | Accept. |
| AC-10 | This audit can proceed to step 5 user acceptance once paired with the architect analysis. | Accept. |

---

> **Disclaimer:** This analysis is provided for informational and research purposes only. It does not constitute legal advice. Patent, copyright, contract, and trademark law are complex and jurisdiction-specific. ToS clause citations in this document are pattern-based inferences from training data within the author's cutoff of January 2026; current 2026-05-23 vendor ToS pages must be retrieved and reviewed before any committed ingestion or training activity. For binding legal opinions, the user should engage a registered Australian patent / IP attorney and a US-licensed attorney with copyright + AI-data-rights practice (California-licensed counsel preferred for project owner's jurisdiction of operation). The author of this report is an AI assistant and is not a licensed legal practitioner in any jurisdiction.
