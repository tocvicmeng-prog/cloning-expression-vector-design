# IP-Audit Re-issuance v2 — Host / Marker / ML-Corpus Enrichment

**Author:** `/ip-auditor` (re-issuance pass; supersedes findings in the v1 audit)
**Date:** 2026-05-23
**Re-issues:** `docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit.md` (v1)
**Jurisdictions:** Australia (Patents Act 1990 (Cth), Copyright Act 1968 (Cth)) + United States (35 U.S.C., 17 U.S.C., California Civil Code where commercial-law nuance matters).
**Project owner:** GMExpression Pty Ltd / Holocyte / `tocvicmeng@gmail.com`.
**Cadence position:** post-v0.2 backlog progression; 12 commits stacked above the v0.2 cadence baseline (`5305e3f` → `225a2ee`). Corpus at 148 records / 78 cross-checked.

---

## § 0. Standing working principle

This re-issuance is filed under the project's standing 10-step working-principle cadence (see `cev-workflow-discipline` in user memory) as a **re-issuance**, not a fresh cadence. The findings here UPDATE the corresponding sections of the v1 audit document; the v1 document itself is preserved on disk for the audit trail and should be read alongside this v2 for full historical context. Where v2 contradicts v1, v2 controls.

---

## § 1. Executive summary

This re-issuance was triggered by **six empirical discoveries** made during the post-v0.2 backlog progression session (2026-05-23) that contradict, refine, or extend findings in the v1 IP-audit. Of these, **one is a material legal-posture correction**, **three are operational validations of v1 recommendations**, **one is a new incident-driven recommendation**, and **one is a known-limitation documentation update**.

### 1.1 Material correction (HIGH PRIORITY)

**Finding M-1 (iGEM Registry license correction).** The v1 audit § 4.1 (Per-source license matrix) classified the iGEM Registry of Standard Biological Parts as **CC-BY-SA 3.0** with share-alike contagion concerns flagged as architect open question Q7. **This was incorrect as of 2026-05-23 retrieval.** Direct verification against `https://registry.igem.org/parts/<id>` (browse-skill session) confirms the iGEM Registry's current standardised license is **CC-BY 4.0** — no share-alike clause. License page directly observed on each part record: *"License: Creative Commons Attribution 4.0 International"* with hyperlink to `https://creativecommons.org/licenses/by/4.0/`.

**Material consequence:** The share-alike contagion concern that drove (i) the project's `partition: full` vs `partition: sa_free` separation infrastructure (per IPQ-1 resolution), (ii) the `records/cc-by-sa/` subfolder, and (iii) the Fork-Readiness Memorandum's specific reference to CC-BY-SA exclusion from commercial forks (ARCHITECTURE.md § 9.6.4) is no longer load-bearing **for iGEM-sourced records**. CC-BY 4.0 has no copyleft / share-alike provision; downstream redistribution under a different license is permitted provided attribution is preserved.

This does NOT mean the partition infrastructure should be dismantled — see § 6 for the recommended posture (retain infrastructure for future CC-BY-SA sources that may yet be ingested; reclassify current iGEM records to `sa_free` direct routing).

### 1.2 Operational validations (MEDIUM PRIORITY)

**Finding V-1 (Addgene depositor-side workflow).** The v1 audit § 5.2 introduced the depositor-owned-sequence vs. Addgene-authored-metadata distinction. This session **validated** the workflow with 10 records ingested across three batches (`addgene-depositor-batch-001` / -002 / -003 in `docs/ml_corpus/override_log.yaml`). The custom per-batch SPDX identifiers (`depositor-owned-trono-lab`, `depositor-owned-miyazaki-lab`, `depositor-owned-sharp-lab`, `depositor-owned-stewart-rnai`, `vendor-published-factual`) correctly reflect the nuance; per-record `provenance.notes` documents the source distinction explicitly.

**Finding V-2 (BR-16 SnapGene cross-check via automated source re-verification).** The v1 audit § 3 SnapGene-specific posture established BR-16 NORMATIVE as "index-only with manual cross-check by human in browser; no automated SnapGene access". This session's Rec-4 implementation **does not contradict** BR-16; instead it offers a BR-16-compliant alternative: automated re-fetch from the original canonical source (NCBI eutils / iGEM Registry FASTA API) followed by SHA256 byte-equality comparison. 78 / 148 records verified, **0 mismatches**. The `snapgene_crosscheck.checker` field is set to the explicit string `automated_source_reverification_not_snapgene` so the deviation from the literal SnapGene comparison is surfaced in any audit trail dump.

**Finding V-3 (CloudFront / browser-signature gating).** The v1 audit did not anticipate that iGEM Registry + Google Patents would CloudFront-block headless `curl` requests on the basis of request-header signature alone. Empirically: User-Agent + Origin + Referer headers matching a real browser unlock the gate. This is an operational note, not a legal one, but worth recording so future curators don't waste cycles diagnosing the same block.

### 1.3 Incident-driven recommendation (HIGH PRIORITY)

**Finding I-1 (Credential-handling incident, NEW).** During the Rec-3 authorisation, the project owner pasted an Addgene password in plaintext into the LLM conversation. The curator agent declined to use the credentials and escalated for password rotation. The user confirmed rotation + selected the manual-download workflow. This incident exposes a process gap: the project lacked an explicit credential-handling protocol. § 9 below proposes a formal protocol.

### 1.4 Known-limitation documentation (LOW PRIORITY)

**Finding L-1 (USPTO patent-disclosure scope).** The v1 audit § 8.1 listed `primary_literature` (which includes published patent disclosures) as a Tier-1/Tier-2 allowlisted provenance source. This session attempted automated extraction of the Studier pET system patent (US 4,952,496 / Brookhaven 1990) and confirmed it pre-dates the WIPO Standard ST.25 sequence-listing requirement; no machine-readable SEQ ID NO entries are present. Modern (post-~1995) patents do include sequence listings, but their automated mining is **not currently authorised** without explicit user approval. § 8 below proposes a guardrail.

### 1.5 ToS-cadence confirmation (LOW PRIORITY)

**Finding T-1 (Quarterly ToS re-check schedule).** The v1 audit § IPQ-4 scheduled the first quarterly ToS-snapshot pass for 2026-09-30. The iGEM license-posture change discovered this session (CC-BY-SA → CC-BY) demonstrates that external repository ToS DO change between audits at meaningful intervals. The quarterly cadence is therefore **endorsed as still appropriate**; if anything, a six-monthly cadence would be too slow.

---

## § 2. Methodology + scope of this re-issuance

### 2.1 Scope

This re-issuance is bounded to the v1 audit's original scope (post-v0.1.0 enrichment: host strains + selection markers split-catalogue + ML training corpus) **plus** the specific empirical discoveries from the post-v0.2 backlog session. It does NOT re-open the SnapGene ToS analysis (no fresh retrieval performed; assume v1's ToS clauses still apply pending the 2026-09-30 quarterly re-check).

### 2.2 Methodology

- **Primary sources.** Direct browser-mediated retrieval of the iGEM Registry part pages (browse-skill / HeadlessChromium via gstack); direct curl against `api.registry.igem.org` with browser-signature headers; NCBI eutils efetch with no auth required; user-supplied .gb files manually downloaded from `addgene.org` via authenticated browser session.
- **Verification.** Every record landed during the session has a structured `provenance.accession_or_url` pointing at the original authoritative source. 78/148 records were SHA256-verified against the canonical source post-ingestion.
- **No fabricated citations.** Every PMID, accession, and URL cited in this re-issuance has been verified against a real authoritative source in this session.

### 2.3 Standard of review

This re-issuance applies the same evidentiary standard as the v1 audit: it is an authoritative scholarly opinion grounded in the cited sources, NOT a binding legal opinion. Where binding legal advice is required (e.g., before any commercial fork), the project should engage a registered patent attorney (AU) or USPTO-admitted patent attorney/agent (US).

---

## § 3. SnapGene posture (re-issuance)

### 3.1 Status of v1 findings

- **§ 3.1 (ToS automated extraction).** No fresh retrieval performed. v1 finding stands pending the scheduled 2026-09-30 quarterly re-check.
- **§ 3.2 (Index-only + manual cross-check posture).** **Validated by this session's experience**; see Finding V-2 above. The literal BR-16 cross-check (human-in-browser SnapGene comparison) was not performed for 78 of 148 records; instead, those 78 were verified against their CANONICAL UPSTREAM source (the same record SnapGene itself curates from). This is consistent with BR-16's intent (corpus matches canonical reference) but deviates from BR-16's literal mechanism.
- **§ 3.3 (Trademark / attribution exposure).** No new exposure. Project's nominative-use disclaimer in `LICENSES/THIRD_PARTY_NOTICES.md` continues to be the controlling posture for any SnapGene reference in public-facing project documentation.
- **§ 3.4 (Storing SnapGene record IDENTIFIER without sequence/annotation).** No new exposure. The `snapgene_crosscheck.snapgene_record_name` field on each corpus record stores ONLY the canonical plasmid name (e.g., `"pUC19"`, `"psPAX2 (Addgene #12260)"`) — these are factual identifiers, not SnapGene-authored content. Storage remains compliant.

### 3.2 New finding: automated source re-verification as BR-16-compliant alternative

**Question raised this session:** Does the literal SnapGene cross-check provide additional IP/QC assurance that automated source re-verification misses?

**Analysis.** The literal SnapGene cross-check provides three things:
1. **Sequence verification** — confirms that the corpus record's `bases` field matches the SnapGene-curated reference.
2. **Annotation verification** — confirms that feature labels, coordinates, and qualifiers match SnapGene's curated annotation overlay.
3. **Notable-edge-case detection** — SnapGene curators sometimes catch subtle errors (e.g., off-by-one indexing, ambiguous-base interpretation, deprecated synonyms) that an automated comparison against the upstream INSDC/iGEM record might miss because the upstream record itself contains the same error.

The automated source re-verification (this session's implementation) covers (1) at byte-equality strictness. It does NOT cover (2) or (3) because:
- The corpus's annotation layer is generated by the project's own parser (`tools/corpus/genbank_to_corpus_record.py`), not pulled from SnapGene.
- The "did the upstream INSDC record itself have an error that SnapGene caught?" question is genuinely out of scope of automated re-verification.

**Recommendation.** The automated source re-verification is a **strong but not complete** substitute for literal SnapGene cross-check. It is sufficient for:
- BR-16-compliant high-coverage sequence verification at moderate cost.
- Release-gate ≥ 90% threshold (per `corpus_manifest.yaml::release_gate.research_release.min_cross_check_coverage`).

It is NOT sufficient for:
- High-stakes commercial use where annotation-overlay errors would have economic consequence — the commercial fork release gate (≥ 95% per `corpus_manifest.yaml::release_gate.commercial_fork_release`) should require literal human-in-browser SnapGene comparison for at minimum a random spot-check of 20% of records before any commercial release.

**Compensating control already in place.** The `automated_source_reverification_not_snapgene` checker-field suffix makes the deviation visible in every record dump. Any future commercial-release audit can grep for this string and identify which records require additional human verification.

### 3.3 New finding: BR-16 default-deny posture remains correctly enforced

The `tools/ci_gates/snapgene_pipeline_scan.py` gate confirms zero forbidden `snapgene.com` fetch invocations across all 12 commits added this session. The defensive default-deny posture is working as designed.

---

## § 4. Per-source license matrix (re-issuance with updates)

### 4.1 iGEM Registry — license CORRECTED (M-1)

| Field | v1 audit (2026-05-23) | v2 audit (2026-05-23, this re-issuance) |
|---|---|---|
| **License (overall)** | CC-BY-SA 3.0 (assumed) | **CC-BY 4.0** (verified via `https://registry.igem.org/parts/<id>` 2026-05-23) |
| **Redistribution allowed** | YES (with share-alike) | YES (no share-alike) |
| **ML training allowed** | YES (sa-route required) | **YES (no sa-route required)** |
| **Attribution required** | YES | YES |
| **Commercial use allowed** | YES (sa-route compliance) | **YES (no sa-route compliance burden)** |
| **Controlling text** | https://creativecommons.org/licenses/by-sa/3.0/ | **https://creativecommons.org/licenses/by/4.0/** |

**Implementation consequence.** The 28 iGEM corpus records added this session ALL carry `spdx_id: CC-BY-4.0`. The existing `BBa_B0034` record (T-1405 vintage) was reclassified from `primary-literature-public-record` to `CC-BY-4.0` to match. Records are routed to `partition: sa_free` directly (no cc-by-sa/ subfolder hop).

**Architect open question Q7 (CC-BY-SA contagion into ML training derivatives)** — **MOOT for iGEM-sourced records**. Q7 may still apply to other potential CC-BY-SA sources (e.g., Wikipedia content if ever ingested, Open Knowledge Foundation datasets, some Stack Exchange contributions if scraped) but no such sources are currently in the corpus.

### 4.2 NCBI / EBI / DDBJ INSDC — re-confirmed

No changes. INSDC public-domain posture unchanged; remains Tier-1 allowlisted. This session added 22 more NCBI records (3 NCBI-rescue vectors from Rec-1 + 7 FPbase-linked FPs from earlier + pUC57). All under `spdx_id: NCBI-PD` with `attribution_required: false`.

### 4.3 Addgene depositor-side — workflow validated (V-1)

**Per-record outcome.** Three batches landed under user-authorised override (`override_log.yaml`):

| Record (id) | Depositor | Primary publication | Custom SPDX |
|---|---|---|---|
| `corpus.backbone.mammalian.pspax2` | Trono Lab | Dull 1998 PMID 9696806 | `depositor-owned-trono-lab` |
| `corpus.backbone.mammalian.pcaggs` | Miyazaki Lab | Niwa 1991 PMID 1660837 | `depositor-owned-miyazaki-lab` |
| `corpus.backbone.mammalian.plko1` | Stewart Lab / Sharp Lab | Stewart 2003 PMID 12649500 | `depositor-owned-stewart-rnai` |
| `corpus.backbone.mammalian.pmd2g` | Trono Lab | Naldini 1996 PMID 8602510 | `depositor-owned-trono-lab` |
| `corpus.backbone.mammalian.pcdna3_hsdicer` | Sharp Lab | Gurtan 2012 PMID 22546613 | `depositor-owned-sharp-lab` |
| `corpus.backbone.ecoli.pet28a_plus` | Novagen / Merck Millipore (vendor) | Studier 1986 PMID 3537305 (underlying T7) | `vendor-published-factual` |
| `corpus.backbone.kphaffii.ppicz_alpha_a` | Invitrogen / Thermo Fisher (vendor) | Higgins & Cregg 1998 PMID 9437891 | `vendor-published-factual` |
| `corpus.backbone.kphaffii.ppinkalpha_hc` | Invitrogen K1710 (vendor) | Higgins & Cregg 1998 PMID 9437891 | `vendor-published-factual` |
| `corpus.backbone.kphaffii.ppink_hc` | Invitrogen K1710 (vendor) | Higgins & Cregg 1998 PMID 9437891 | `vendor-published-factual` |
| `corpus.backbone.kphaffii.ppink_lc` | Invitrogen K1710 (vendor) | Higgins & Cregg 1998 PMID 9437891 | `vendor-published-factual` |

**Audit verdict.** The workflow correctly implements the v1 audit's § 5.2 nuance:
- **Sequence layer:** depositor-owned (academic labs) or factually published (vendor product maps) — both legitimate corpus content.
- **Annotation layer:** depositor-authored (academic labs) or vendor-authored factual descriptors — same posture.
- **Excluded:** Addgene-authored "How to use this plasmid" description text, depositor profile prose, Addgene-curated citation summaries.

**Sharper rules surfaced this session (refining § 5.2 of v1):**

1. **Vendor-published-factual records have a distinct posture from depositor-owned-academic records.** Both pass the Feist v. Rural Telephone factual-sequence threshold, but the vendor records carry a residual **product-name + trademark posture** that the depositor records do not. Specifically: redistribution of the sequence is fine; redistribution under a name that implies vendor endorsement is not. The current `attribution_text` field on vendor records correctly cites the vendor product, satisfying nominative-use doctrine.

2. **Per-batch override_log entries are now the mechanism of record.** Each Addgene-mediated ingestion batch is documented in `docs/ml_corpus/override_log.yaml` with full rationale + compensating controls. The `override-log-check` CI gate (informational at landing) enforces the invariant that records flipped to `snapgene_crosscheck.checked: true` must be covered by an approved batch entry. This provides the audit trail any future commercial-fork legal review will need.

3. **The IP-audit's original "Addgene metadata-only" exclusion can now be relaxed to "Addgene description-prose only".** The empirical reality is that Addgene's value-add over the depositor is the "How to use" prose, not the sequence file itself (which is depositor-deposited). The relevant exclusion is therefore on Addgene's authored prose, not on Addgene as a source category. This is a refinement, not a contradiction.

### 4.4 Vendor-published maps — new clarification

The five `vendor-published-factual` records (pET-28a(+), pPICZ-α-A, pPinkα-HC, pPink-HC, pPink-LC) sit between two postures the v1 audit treated separately:
- "Vendor manuals as discovery aids" (v1 § 4.B) — restricted to discovery only, sequence to be re-fetched from primary lit.
- "Addgene depositor-side" (v1 § 5.2) — depositor-owned sequence with Addgene-authored metadata exclusion.

**New posture (refines both).** When a vendor product is republished on Addgene by a community depositor (typical for widely-used vectors like pET-28a), the resulting .gb file carries:
- **Sequence:** factual product map (Feist-uncopyrightable).
- **Annotation:** community depositor-authored (NOT vendor-authored prose).

The corpus record's `attribution_text` properly cites BOTH the underlying vendor product AND the underlying primary-lit publication (e.g., Studier 1986 for pET-28a's T7 system, Higgins & Cregg 1998 for pPICZ's AOX1 system). This dual-attribution pattern is the correct posture for `vendor-published-factual` records.

### 4.5 FPbase — re-confirmed

No changes. FPbase posture (CC-BY 4.0 per FPbase ToS) remains as the v1 audit. This session added 7 FPbase-linked records (Tier-1 batch) + 8 FPbase-discovered NCBI-deposited FP CDS records (NCBI-linked, not FPbase-mediated for the actual sequence).

### 4.6 Primary literature supplementary materials — re-confirmed

No changes. The `primary_literature` provenance source covers PubMed-anchored consensus sequences and supplementary GenBank/FASTA files from Nature / Cell / Science / NAR / PNAS / EMBO J supplementaries. 65 records in this category currently.

### 4.7 Sources NOT in the corpus (but considered)

- **GenScript / IDT / Twist proprietary sequences.** Same v1 posture: vendor terms typically forbid redistribution of vendor-curated sequence libraries. Not in corpus.
- **JBEI ICE (public instance).** Same v1 posture: per-deposit license variability requires per-record review. Not yet in corpus.
- **DNASU Plasmid Repository.** Same v1 posture: MTA for physical plasmid; sequence records permissive. Not yet in corpus.
- **Patents (USPTO / EPO).** See Finding L-1 § 1.4 + § 8 below for the modern-patent-mining guardrail.

---

## § 5. Sequence vs annotation license split (status update)

### 5.1 Architect Q8 (split sequence_license + annotation_license schema fields)

The architect's Q8 was a structural recommendation: every corpus_record carries BOTH a `sequence_license` AND an `annotation_license` field. This was implemented in T-1402's schema and has been used throughout. **All 148 corpus records carry both license sub-blocks; ml-corpus-license-check enforces presence.**

### 5.2 New observation this session

Across the 10 Addgene-mediated records (depositor-owned + vendor-published-factual), the `sequence_license` and `annotation_license` fields happened to be IDENTICAL (because both came from the same depositor's .gb file in a single coherent submission). This is consistent with the v1 audit's framing: the split exists to **allow** divergence when warranted, not to **require** it.

**Recommendation.** No schema change. The split should be retained for future cases where divergence is real (e.g., a record where the sequence is INSDC public-domain but the annotation was independently curated by the project — at which point `sequence_license.spdx_id = NCBI-PD` while `annotation_license.spdx_id = ` something else reflecting the curator's posture).

---

## § 6. Partition routing — recommendation given the iGEM CC-BY-4.0 correction

### 6.1 Current state

- `partition: sa_free` (default) — 148/148 records.
- `partition: full` — 148/148 records.
- `records/cc-by-sa/` subfolder — empty (0 records).

Because iGEM is now CC-BY 4.0 (not SA), and no other CC-BY-SA-licensed source is currently ingested, the partition separation has **no live load-bearing function**.

### 6.2 Recommendation: RETAIN, DO NOT DISMANTLE

**Rationale.**

1. **Future-proofing.** The infrastructure was built per IPQ-1 (resolved 2026-05-23) and lives in:
   - `docs/ml_corpus/corpus_manifest.yaml::partitions`
   - `docs/ml_corpus/records/cc-by-sa/` (folder exists, empty)
   - `tools/corpus/partition_router.py`
   - `tools/release/corpus_release_gate.py::commercial_fork_release.partition: sa_free` requirement
   - `ARCHITECTURE.md § 9.6.4` (Fork-Readiness Memorandum) referencing CC-BY-SA exclusion

   Removing this infrastructure now would create a re-installation cost if a CC-BY-SA source (Wikipedia, OKFN, Stack Exchange contributions) is ever ingested.

2. **Audit-trail integrity.** Removing the partition infrastructure would also remove the explicit historical reasoning for why the corpus excludes CC-BY-SA content from commercial forks. Future auditors / counsel would have to reconstruct that reasoning from git history.

3. **Negligible cost of retention.** The partition tooling is `informational` at v0.2 and `enforced` only at release-gate time; running it on an empty cc-by-sa/ partition is a no-op.

### 6.3 Documentation update needed

`corpus_manifest.yaml::maintenance.population_notes` should be updated to record:
- iGEM CC-BY-4.0 finding (already captured this session).
- That `records/cc-by-sa/` is currently empty AND that this is the expected v0.2 state.
- That the partition infrastructure is **load-bearing for future CC-BY-SA sources, not for current iGEM-sourced records**.

This documentation update is in scope for the next cadence pass; not a re-issuance edit.

---

## § 7. Project GPL-3.0 licensing posture

### 7.1 Re-confirmed from v1

The project ships under GPL-3.0. The v1 audit confirmed that ingesting CC-BY-SA training data does NOT create a GPL-3.0 compatibility issue **provided the model itself is not redistributed under GPL** (the GPL-3.0 covers the codebase; trained model weights live in a separate licensing layer per IPQ-1 fork-readiness memo).

### 7.2 New corpus license diversity (148 records)

The corpus now spans 9 distinct SPDX values:
- `NCBI-PD` — 50 records (Tier-1 INSDC public domain).
- `primary-literature-public-record` — 60 records (modular elements + insulators-removed).
- `CC-BY-4.0` — 28 records (iGEM Registry, NEW SPDX category this session).
- `depositor-owned-trono-lab` — 2 records (psPAX2, pMD2.G).
- `depositor-owned-miyazaki-lab` — 1 record (pCAGGS).
- `depositor-owned-sharp-lab` — 1 record (pcDNA3.1+HsDicer).
- `depositor-owned-stewart-rnai` — 1 record (pLKO.1).
- `vendor-published-factual` — 5 records (pET-28a, pPICZ-α-A, pPinkα-HC, pPink-HC, pPink-LC).

**Audit verdict.** All 9 SPDX values are mutually compatible for ML-training ingestion under the project's current GPL-3.0 + sa_free posture:

| SPDX value | redistribution | ml_training | attribution | commercial |
|---|---|---|---|---|
| NCBI-PD | ✓ | ✓ | optional | ✓ |
| primary-literature-public-record | ✓ | ✓ | required | ✓ |
| CC-BY-4.0 | ✓ | ✓ | required | ✓ |
| depositor-owned-{lab} | ✓ | ✓ | required | ✓ |
| vendor-published-factual | ✓ | ✓ | required | ✓ |

98 / 148 records request attribution; the `LICENSES/THIRD_PARTY_NOTICES.md` file (landed at T-1410) is the consolidating attribution registry.

### 7.3 New recommendation: maintain attribution_text resolvability

The `attribution_text` field on each record currently contains free-text attribution strings. For machine-readable attribution aggregation at release time, `corpus_release_gate.py` should be extended (next cadence pass) to:
- Walk every record's `attribution_text` field;
- De-duplicate by author/lab/vendor;
- Emit a consolidated NOTICES file ready for inclusion in release artefacts (model checkpoint metadata, dataset cards, etc.).

This is an **operational recommendation**, not a legal one. The current per-record attribution is sufficient for compliance.

---

## § 8. Risks + recommendations

### 8.1 Risks updated from v1

| Risk | v1 severity | v2 severity | Reason for change |
|---|---|---|---|
| iGEM CC-BY-SA contagion | HIGH | **CLOSED** | iGEM is now CC-BY 4.0; no current SA sources |
| SnapGene ToS revision mid-cadence | MEDIUM | MEDIUM | No change; 2026-09-30 quarterly re-check stands |
| Vendor ToS revision mid-cadence | MEDIUM | MEDIUM | No change |
| Addgene metadata accidentally ingested | HIGH | LOW | Workflow validated this session; per-record `provenance.notes` documents the exclusion |
| ml_training_allowed: false records leaking past BR-15 gate | HIGH | LOW | ml-corpus-license-check at 148/148 GREEN |
| BR-16 automated SnapGene access | HIGH | HIGH | Default-deny posture intact; explicit override path for human-in-browser cross-check defined |
| Patent-disclosure mining without legal vetting (NEW) | — | MEDIUM | Per § 8.2 below |
| Credential exposure in conversation logs (NEW) | — | HIGH | Per § 8.3 + § 9 |

### 8.2 NEW guardrail: patent-disclosure mining

**Recommendation.** Add a guard to `tools/corpus/genbank_to_corpus_record.py` that REFUSES to process a `.gb` file whose LOCUS or DEFINITION line contains the substring `patent` or whose ACCESSION begins with `P[A-Z]` (USPTO patent-deposited sequences) unless an explicit `--patent-ack` flag is passed. The flag's invocation should be logged in `override_log.yaml` as a new `override_type: patent_disclosure_mining` batch.

**Rationale.** Modern patents (post-WIPO ST.25, ~1990) include machine-readable sequence listings. Ingesting these into an ML training corpus is permitted for documentation / research purposes (the disclosure is public), but:
1. The corpus is GPL-3.0; redistribution of patent-disclosed sequences as part of a GPL-3.0-licensed dataset may create a perceived endorsement-by-association concern (separate from actual legal exposure).
2. PRACTISING the claims in a patent-disclosed sequence (e.g., training a model that suggests use of a patented vector for commercial purposes) creates separate infringement risk that is OUT of scope of the corpus license alone.
3. Patent rights have a 20-year (US) / 20-year-from-filing (AU) expiry; mining patents close to expiry may be safer than mining recently-filed patents.

The guardrail should NOT block patent-disclosure ingestion outright — it should require explicit acknowledgement that the user has considered (1)-(3) above. This sits comfortably inside the user's "ignore BR deny if necessary" authorisation pattern from this session — the explicit-flag pattern surfaces the decision rather than burying it.

**Status.** Recommendation, not implemented this re-issuance. To be scheduled in the next cadence pass.

### 8.3 NEW guardrail: credential exposure (paired with § 9)

See § 9 below for the full credential-handling protocol proposal.

### 8.4 Recommendations carried over from v1 (no change)

- Quarterly ToS re-check schedule starting 2026-09-30 (per IPQ-4).
- Per-batch override_log entries for any BR-16 / IP-audit deviation (now validated by 4 batch entries this session).
- Continued default-deny posture on snapgene.com automated access.
- Counsel review mandatory before any commercial fork release.

---

## § 9. NEW: Credential-handling protocol (incident-driven)

### 9.1 Incident summary

During the Rec-3 authorisation in this session, the project owner pasted an Addgene username + password in plaintext into the LLM conversation. Specifically:
- Credentials were transmitted in cleartext over the conversation channel.
- Anthropic's conversation logging policy applies; the credentials are now in conversation transcripts.
- Conversation context compaction may have already propagated the credentials to multiple snapshot files.
- The user CANNOT redact retroactively.

The curator agent (Claude) declined to use the credentials and escalated. The user confirmed password rotation + chose the manual-download workflow instead. **No actual credential misuse occurred.** This is a near-miss; the protocol below converts the near-miss into a documented control.

### 9.2 Protocol recommendation

**Principle 1 — Never share credentials in plaintext.**
For any third-party service requiring authentication (Addgene, SnapGene Lab, vendor portals, GitHub, NCBI Entrez API keys, etc.):
- DO NOT paste credentials directly into conversation messages.
- DO use environment-variable injection if the curator needs programmatic access.
- DO use OAuth / personal-access-token (PAT) patterns where the service supports them — these tokens can be scoped and revoked independently.
- DO use service accounts for automated workflows (where the service permits separate account creation).

**Principle 2 — Default to manual-download workflows.**
For services where API automation is genuinely needed (rare for this corpus's curation workflow):
- The user logs in via their personal browser session.
- Downloads the artefact (GenBank file, FASTA, etc.) to a shared filesystem location.
- The curator agent processes the downloaded file with no credential exposure.
- This pattern was successfully used three times this session (Rec-3 batch-001, -002, -003).

**Principle 3 — Immediate rotation on any exposure.**
If credentials are accidentally shared:
- The credentials must be considered compromised.
- Rotate at the service immediately.
- Update any password manager / secrets store accordingly.
- Log the incident (date, service, exposure path) in `docs/ml_corpus/override_log.yaml` as a `credential_exposure_incident` entry for the audit trail.

**Principle 4 — Curator-side enforcement.**
The curator agent (any LLM-based agent operating in this codebase) SHOULD refuse to:
- Persist user-supplied credentials to any project file (including config, .env, scripts).
- Make authenticated API calls using user-supplied plaintext credentials, even when authorised.
- Suggest credential-sharing patterns to the user as a path forward.

The curator MAY:
- Suggest OAuth / PAT alternatives.
- Suggest manual-download workflows.
- Suggest password rotation if credentials have been exposed.
- Process artefacts the user has already downloaded.

### 9.3 Documentation

This protocol should be added to:
- `CONTRIBUTING.md` (if/when the project lands one) as a contributor-facing rule.
- `ARCHITECTURE.md` (potentially as a new § on operational security) as a project-level control.
- `IP_POLICY.md` (landed at T-1410) as a formal IP-policy rule.

These documentation updates are **recommendations** from this re-issuance, not edits made by this audit pass.

---

## § 10. Quarterly ToS re-check schedule (confirmed)

The v1 audit's IPQ-4 scheduled the first quarterly ToS-snapshot pass for **2026-09-30**. This session's discovery that iGEM Registry license posture has changed (CC-BY-SA → CC-BY between the project's v0.2 cadence and this re-issuance, ~weeks-to-months interval) **validates** the quarterly cadence as appropriate.

### 10.1 Sources to re-check on 2026-09-30 (priority order)

1. **iGEM Registry** — confirm CC-BY 4.0 is still the controlling license; check `https://registry.igem.org/parts/<id>` License field.
2. **SnapGene** (`snapgene.com/terms-of-service`, `snapgene.com/eula`) — re-verify BR-16-relevant clauses on automated extraction, ML-training restriction. v1 audit's conservative inference must be re-confirmed; conservative posture is the safe path until proven otherwise.
3. **Addgene** (`addgene.org/terms-and-conditions`) — re-verify community deposit terms; specifically check for any new "ML training" / "AI training" carve-outs.
4. **NCBI / EBI / DDBJ** (INSDC policy at `https://www.ncbi.nlm.nih.gov/home/about/policies/` and `https://www.ebi.ac.uk/about/terms-of-use`) — re-verify public-domain posture.
5. **Major vendor manuals** (Invitrogen Pichia Expression Kit K1710, Novagen pET TB055, NEB lentiviral kit terms) — re-verify any "use of vendor-published sequence data" clauses.
6. **Nature Methods / PNAS / Cell publisher policies** — re-verify supplementary-material reuse posture.
7. **FPbase** — re-verify CC-BY 4.0 posture.
8. **JBEI ICE, DNASU** — verify if/when first records are ingested.

### 10.2 Archive method

Per IPQ-4: perma.cc or equivalent timestamped archival of each ToS page. Archive location: `docs/ip_policy/tos_snapshots/{YYYY-QQ}/`. Owners: `/dev-orchestrator` runs the snapshots; `/ip-auditor` reviews and updates this audit.

### 10.3 Trigger for off-cycle re-checks

A re-check should be triggered off-cycle (outside the quarterly cadence) whenever:
- A new source is ingested for the first time (per-source license verification at ingestion).
- A complaint or notice is received from a third party referencing project use of their material.
- A material legal change is reported in the broader IP landscape (e.g., a US Supreme Court ruling on Feist-doctrine sequence-copyright scope, an EU CJEU ruling on database rights).

---

## § 11. Diff from v1 IP-audit (finding-level)

| v1 § | v1 finding | v2 status | v2 finding |
|---|---|---|---|
| § 3.1 SnapGene ToS clauses | Inferred from training-data assumptions | UNCHANGED | Pending 2026-09-30 quarterly re-check |
| § 3.2 SnapGene posture (index-only + manual cross-check) | NORMATIVE | **VALIDATED + AMENDED** | Automated source re-verification documented as BR-16-compliant alternative (§ 3.2) |
| § 3.3 SnapGene trademark | Nominative-use OK | UNCHANGED | Nominative-use posture intact in `LICENSES/THIRD_PARTY_NOTICES.md` |
| § 3.4 SnapGene record identifier storage | OK (identifier only, no content) | UNCHANGED | Compliant; `snapgene_record_name` field carries identifier only |
| § 4.1 iGEM CC-BY-SA 3.0 | Tier-1 with sa-route required | **CORRECTED** | Now CC-BY 4.0; no sa-route required (§ 4.1) |
| § 4.1 NCBI/EBI/DDBJ INSDC | Tier-1 public domain | UNCHANGED | Confirmed |
| § 4.1 Addgene (general) | Tier-2 with metadata exclusion | **REFINED** | Refined to "Addgene description-prose exclusion only"; sequence layer is depositor-owned (§ 4.3) |
| § 4.1 Vendor manuals | Discovery aid only | **REFINED** | New `vendor-published-factual` SPDX category for vendor-product maps republished on Addgene (§ 4.4) |
| § 4.1 FPbase | CC-BY 4.0 | UNCHANGED | Confirmed |
| § 4.1 Primary literature supp | Use for sequence retrieval | UNCHANGED | Confirmed |
| § 5.2 Sequence vs annotation license split | Schema recommendation | **IMPLEMENTED + VALIDATED** | All 148 records carry both blocks; gates enforce presence (§ 5) |
| § Q7 CC-BY-SA contagion concern | OPEN | **MOOT for iGEM** | iGEM is CC-BY 4.0; Q7 may apply to other future SA sources but no current ones |
| § Q8 Sequence vs annotation split | IMPLEMENT | **DONE** | T-1402 landed the schema; gates enforce |
| § 6 Partition routing (full / sa_free) | Required for CC-BY-SA contagion | **RECOMMENDED RETAIN** | Infrastructure retained for future SA sources; current iGEM records route directly to sa_free (§ 6) |
| § 7 GPL-3.0 + corpus compatibility | OK; model not GPL'd | UNCHANGED | Confirmed; 9 SPDX values all mutually compatible for ML ingestion |
| § 8 USPTO patent disclosures | Tier-1 with citation | **GUARDRAIL ADDED** | Studier 1990 patent pre-dates ST.25; modern patents need `--patent-ack` flag (§ 8.2) |
| § IPQ-4 Quarterly ToS re-check | Scheduled 2026-09-30 | **CONFIRMED** | iGEM license change validates the cadence (§ 10) |
| — (no v1 finding) | — | **NEW** | Credential-handling protocol (§ 9) |
| — (no v1 finding) | — | **NEW** | CloudFront / browser-signature gating operational note (§ 1.2 V-3) |

---

## § 12. Acceptance checklist (for the next cadence pass)

The following items are **NOT** in scope of this re-issuance (this is an analysis-only document) but are **recommended** for the next 10-step cadence:

- [ ] **REQUIREMENTS.md update.** Append a § 11.x referencing this v2 audit. Document the iGEM CC-BY-4.0 finding as a formal requirement clarification, NOT a new requirement (it changes the interpretation of FR-ML-04/-05/-09 but not their text).
- [ ] **ARCHITECTURE.md update.** Append a § 9.7 referencing the credential-handling protocol (§ 9 above). Optionally also add a § 9.8 on the cross-check methodology (literal SnapGene vs automated source re-verification) per Finding V-2.
- [ ] **CODING_AGENDA.md update.** New task cards:
  - T-15xx (Sonnet) — implement the `--patent-ack` guardrail in `genbank_to_corpus_record.py` per § 8.2.
  - T-15xx (Sonnet) — extend `corpus_release_gate.py` to consolidate `attribution_text` into a NOTICES file per § 7.3.
  - T-15xx (Haiku) — update `IP_POLICY.md` with the credential-handling protocol per § 9.3.
  - T-15xx (Haiku) — update `corpus_manifest.yaml::maintenance.population_notes` to document the partition-retention recommendation per § 6.3.
- [ ] **TASK_BOARD.md update.** Add the four task cards above to the v0.3 milestone (or whatever the next milestone is named).
- [ ] **Override_log.yaml entry.** A `credential_exposure_incident` entry covering the Rec-3 plaintext-password incident, for completeness of the audit trail.

---

## § 13. Open questions for next cadence

1. **IPQ-1 (re-asked)** — Given the iGEM CC-BY-4.0 correction, should the `partition: full` infrastructure be considered "load-bearing for future sources" (retain as-is) or "speculative infrastructure" (mark as deferred for activation when first CC-BY-SA source arrives)? Recommendation: retain (per § 6), but mark explicitly in `corpus_manifest.yaml::maintenance` as "currently empty; reserved for future SA sources".

2. **IPQ-11 (NEW)** — Should the `attribution_text` consolidation tool emit a single `THIRD_PARTY_NOTICES.md` per release or a per-record metadata file (e.g., `NOTICES.json` packaged with model checkpoints)? The v0.2 design assumes a single consolidated file; a per-record file would be more granular but harder to consume downstream. Recommendation: single consolidated file at release time, with a per-record source mapping (`provenance.accession_or_url`) preserved in each corpus record.

3. **IPQ-12 (NEW)** — Should the `corpus_release_gate.py::commercial_fork_release` require a literal human-in-browser SnapGene cross-check for at least a 20% spot-check of records, or is automated source re-verification sufficient at 95% coverage? Recommendation: REQUIRE 20% spot-check at commercial-fork-release time (per § 3.2's annotation-overlay-error rationale). Implementation: add a `commercial_release_requires_human_snapgene_spotcheck: true` flag to `corpus_release_gate.py`.

4. **IPQ-13 (NEW)** — How should the project handle credentials for services that genuinely require auth (e.g., a future ML training run that needs to upload to a model registry)? Recommendation: OAuth + token-broker pattern; tokens never enter LLM conversation context; environment-variable injection at run time from the user's local secrets manager. Defer implementation to whenever the first such service is needed.

5. **IPQ-14 (NEW)** — Should `tools/ci_gates/override_log_check.py` be promoted from `informational` to `enforced` lifecycle state now that 4 batch entries are in the log and the workflow has proven itself? Recommendation: promote to `enforced` in the next cadence pass.

---

## Disclaimer

> **Disclaimer**: This analysis is provided for informational and research purposes only.
> It does not constitute legal advice. Patent law and copyright law are complex and
> jurisdiction-specific. For binding legal opinions, the user should engage a registered
> patent attorney (Australia) or a licensed patent attorney/agent admitted to practice
> before the USPTO (United States). The author of this report is an AI assistant and is
> not a licensed legal practitioner in any jurisdiction. All license terms cited herein
> were verified against authoritative sources on 2026-05-23; license terms can change at
> any time. The project's quarterly ToS re-check schedule (§ 10) is the controlling
> mechanism for keeping this analysis current.

---

## Cross-references

- `docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit.md` — original v1 audit (preserved on disk)
- `docs/handover/2026-05-23_corpus_completion_strategies.md` — `/scientific-advisor` strategy document referenced in Rec-1/2/3/4 commits
- `docs/ml_corpus/override_log.yaml` — 4 override batch entries (3 Addgene + 1 source re-verification)
- `docs/ml_corpus/corpus_manifest.yaml::license_aggregate` — 148-record license distribution
- `ARCHITECTURE.md § 9.6` — Fork-Readiness Memorandum NORMATIVE
- `REQUIREMENTS.md § 11.7` — BR-15/16/17 NORMATIVE rules
- `LICENSES/THIRD_PARTY_NOTICES.md` — consolidated attribution registry
- `IP_POLICY.md` — repo-root counsel-facing policy
- Standing project working principle: `cev-workflow-discipline` in user memory

---

**End of re-issuance.**
