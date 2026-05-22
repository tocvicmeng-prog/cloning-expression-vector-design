# Initial Report — Host / Marker / Plasmid-Library Enrichment

**Project:** Cloning & Expression Vector Design Toolkit (post-`v0.1.0`)
**Document type:** Initial advisory report + multi-skill handover brief
**Author:** `/scientific-advisor`
**Date:** 2026-05-23
**Status:** **DRAFT — pending user acceptance.** No catalogue, schema, REQUIREMENTS.md, ARCHITECTURE.md, CODING_AGENDA.md, or TASK_BOARD.md changes have been made. This report is the artefact that the user is expected to accept (or amend) before the project workflow advances to the requirements-update step.

---

## 0. Standing project working principle (recorded 2026-05-23)

Every body of work on this project, from this point forward, follows the same fixed cadence to keep scientific intent, architecture, and implementation in lockstep:

1. **`/scientific-advisor`** produces an **initial report** scoping the new work.
2. **User accepts** the report (or asks for amendments until accepted).
3. **`REQUIREMENTS.md` is updated** to capture the newly accepted requirements (new UR / FR / MR / WR / SR / BR / MS / ADV entries as appropriate).
4. **`/scientific-advisor` + `/dev-orchestrator` + `/architect`** jointly draft a well-considered development plan for the work.
5. **`ARCHITECTURE.md` is updated** to reflect the planned work structure (new modules, ports, catalogues, gates, persistence, event streams as appropriate).
6. **`CODING_AGENDA.md` is updated** with a clearly defined coding-agent workflow — new task cards, tier assignments, dependencies, deliverables, acceptance criteria.
7. **`TASK_BOARD.md` is updated** to enable real-time progress tracking against the new tasks.
8. **Implementation begins** — typically routed through `/scientific-coder` or `/scientific-advisor` per the CODING_AGENDA.md task-card assignment, with `/dev-orchestrator` coordinating model tiers, dialogue compression, and milestone handovers.

This cadence is non-optional and applies to every future enrichment, feature, refactor, or quality pass on the project. Its purpose is to maintain the highest possible software quality by preventing drift between (a) the scientific knowledge base, (b) the requirements layer, (c) the architecture binding, (d) the coding plan, and (e) the executed code.

---

## 1. Decisions confirmed by user (2026-05-23)

| # | Question | Decision |
|---|---|---|
| 1 | Markers catalogue location | **Split** — new `catalogues/markers.yaml` + new `schemas/markers.schema.json`. Existing `parts.yaml::markers` content will be deprecated and migrated; the citation presets there will be preserved and re-cited under the new file. |
| 2 | *Pichia pastoris* taxonomy | **`Komagataella phaffii`** is the canonical genus + species. `Pichia pastoris` is registered as an `alias` so all legacy references (vendor manuals, literature pre-2009, user inputs) resolve unambiguously. |
| 3 | ML corpus location | **Sibling folder inside the repo**: `docs/ml_corpus/` with its own README, manifest, schemas, and license matrix. Co-versioned with the source tree; gated by its own CI block but governed separately from `catalogues/` because its data model and license posture are different. |
| 4 | SnapGene posture | **Index-only**, with one explicit additional use: **sequences ingested from cleaner sources (NCBI / EBI / iGEM / vendor manuals / primary literature) must be double-cross-checked against the corresponding SnapGene record as a manual scientific-validation step.** SnapGene is treated as a known-good *reference oracle for QC*, never as a *data source for redistribution or ML training*. No automated scraping of `snapgene.com` is performed in any pipeline. |
| 5 | Antibiotic working-concentration reference | **Sambrook 4th ed. Appendix A1** is the canonical B2 source. Primary literature is preferred where it disagrees with Sambrook (e.g., Bessette 1999 for Origami-specific kanamycin handling; Goldstein & McCusker 1999 for KanMX/NatMX/HphMX in *S. cerevisiae*). Vendor manuals supplement for vendor-specific strains where Sambrook is silent. |

---

## 2. Confirmed scope of this enrichment

### 2.1 Track A — Host catalogue extension
Add the following 30 strains (some already partly present and to be upgraded under the new schema):

- **E. coli (15):** Stbl3, Stbl4, JM109, TOP10, DH5α, BL21(DE3), BL21 Star, Rosetta(DE3), Origami(DE3), Origami B(DE3), C41(DE3), C43(DE3), BL21(DE3)pLysS, BL21(DE3)pLysE, Rosetta(DE3)pLysS.
- **Komagataella phaffii (6, canonical) — aliased *Pichia pastoris*:** PichiaPink series, wild-type X-33, GS115, KM71 / KM71H, SMD1168 / SMD1168H.
- **S. cerevisiae (5):** BY4741, BY4742, AH109, Y187, EGY48, INVSc1.

### 2.2 Track B — Selection-marker catalogue
A new `catalogues/markers.yaml` carrying:

- **Bacterial markers (~9):** Amp / Carb (TEM-1), Kan (neo / aph), Cm (cat), Tet (tetA-class), Spec (aadA), Zeo (ble-Sh), Gen (aac3), Hyg (hph-bacterial), Erm.
- **Yeast auxotrophic markers (~6):** URA3, LEU2, HIS3, TRP1, MET15 / MET17, LYS2.
- **Dominant yeast markers (~4):** KanMX (G418), HphMX (Hygromycin B), NatMX (clonNAT / nourseothricin), BlepMX (Zeocin).

Each marker carries: gene, resistance mechanism, **per-host working concentration ranges** (μg/mL), recommended medium, recommended use cases, incompatibilities, counter-selection method where applicable (e.g., 5-FOA for URA3), and Sambrook-anchored citations.

### 2.3 Track C — ML training corpus
A new `docs/ml_corpus/` sibling folder with:
- Curated empty bacterial / yeast / mammalian backbones.
- Curated modular elements (promoters, terminators, RBS / Kozak, polyA, IRES / 2A, MCS layouts, purification tags, fluorescent-protein CDS, selection cassettes).
- A `corpus_manifest.yaml` with provenance, license, retrieval URL/accession, retrieval timestamp, and sequence checksum per record.
- An `exclusions.yaml` recording every record considered but rejected, with reason.
- A **SnapGene cross-check log** documenting, per record, whether the ingested sequence was visually compared to the SnapGene reference record, who performed the check, the date, and whether discrepancies were resolved (and how).

### 2.4 Out of scope (Phase 14+ stretch — explicitly not included here)
Multi-user collaborative server; live vendor APIs; genome-context features; Addgene-publishing pipeline; liquid-handler integration.

---

## 3. Briefing for `/architect` (handoff #1)

`/architect` is asked to produce **a schema + composition-root design proposal** before any data is written. Specifically:

### 3.1 New / amended schemas

| File | Status | Required fields (summary — full proposal in § 3 of the prior advisory plan) |
|---|---|---|
| `schemas/hosts.schema.json` v1.0 → v1.1 | Amend | `t7_lysogen`, `protease_status {lon, ompT}`, `disulfide_environment` (+ `trxB_status`, `gor_status`), `rare_codon_supplementation`, `plasmid_addons[]`, `t7_lysozyme_load`, `recombination_phenotype {recA, endA, recBCD_status}`, `methylation_phenotype {dam, dcm, hsdRMS}`, `recommended_selection_markers[] → marker_id`, `vendor_strain_refs[]`, `aliases[]` (to support *Pichia* ↔ *Komagataella*). |
| `schemas/markers.schema.json` v1.0 | New | `id`, `name`, `class {bacterial_antibiotic / yeast_auxotrophic / yeast_dominant / mammalian / counterselection}`, `gene`, `mechanism`, `plasmid_borne`, `chromosomal`, `working_concentrations[]` (per host_class with min / typical / max in μg/mL + medium), `counter_selection`, `incompatibilities[]`, `use_cases[]`, `citation_preset_id`. |
| `docs/ml_corpus/schemas/corpus_record.schema.json` v1.0 | New (lives outside `catalogues/` deliberately) | `id`, `category {backbone / promoter / terminator / RBS / Kozak / polyA / IRES / 2A / MCS / tag / FP / selection_cassette}`, `sequence`, `annotation[]` (GFF3-style), `provenance {source, accession_or_url, retrieved_at}`, `license {spdx_id, redistribution_allowed, ml_training_allowed, attribution_required, source_text_url}`, `host_topology {circular_linear, length_bp}`, `snapgene_crosscheck {checked, checked_at, checker, match, discrepancy_resolution}`, `intended_use_category[]`, `checksum`. |

### 3.2 Composition-root + ports

- Add `MarkersCataloguePort` (read-only) symmetric with existing `HostCataloguePort` / `PartCataloguePort` / `EnzymeCataloguePort`.
- Update `engine.compatibility` so host rules can resolve `recommended_selection_markers[]` against the markers catalogue.
- Update `engine.validation` so any rule referencing a marker resolves via the new port, not via `parts.yaml::markers`.
- Decide migration path: cut-over date for deprecating `parts.yaml::markers`; transitional dual-read window or hard switch.

### 3.3 CI gates

- New `markers-citation-presence-check` (every marker has a citation_preset; every preset links to a primary or Sambrook reference).
- New `host-marker-link-integrity-check` (every `recommended_selection_markers[]` entry resolves).
- New `ml-corpus-license-check` (every `docs/ml_corpus/records/**/*.json` carries a license block with `redistribution_allowed` and `ml_training_allowed` set explicitly; default-deny if missing).
- Extend `agenda_consistency_check.py` to enforce the schema-version bump on `hosts.yaml`.

### 3.4 Architecture-binding question for `/architect`
Decide whether the SnapGene cross-check log is (a) a **catalogue-side runtime gate** (an enforced check inside the ingestion pipeline) or (b) a **process-only artefact** (a markdown log that a scientific reviewer signs off on, with no runtime gate). The advisor's recommendation is (b) — process-only, no runtime gate — because the cross-check is human-judgement against a third-party tool and shouldn't fail-stop the pipeline.

---

## 4. Briefing for `/ip-auditor` (handoff #2)

`/ip-auditor` is asked to produce a **written ToS + license opinion**, AU + US (California-focus) jurisdictions, covering:

### 4.1 SnapGene specifically
- Current ToS text (date-stamped) for `snapgene.com` and SnapGene desktop product, with the relevant clauses on automated extraction, redistribution, and derivative-data use quoted.
- Opinion on the "**index-only with cross-check**" posture confirmed by the user in Decision #4: is human-eyeball visual comparison against a SnapGene record (without automated extraction, scraping, or redistribution of any SnapGene content) within the ToS?
- Opinion on whether *naming* SnapGene as a QC reference in our public-facing documentation (e.g., README, traceability index) creates any trademark or attribution exposure.

### 4.2 Per-source license matrix for ML-corpus inputs
For each of the candidate sources below, deliver: redistribution-allowed (yes / no / conditional), ML-training-allowed (yes / no / conditional), attribution-required (yes / no / conditional), and the controlling text URL.

- NCBI Nucleotide / GenBank (INSDC)
- EBI ENA (INSDC)
- DDBJ (INSDC)
- iGEM Registry of Standard Biological Parts
- JBEI ICE (public instance)
- DNASU Plasmid Repository (ASU/Biodesign)
- Addgene (metadata vs. depositor sequence files separately)
- Vendor-published maps + manuals (Invitrogen / Thermo Fisher, Novagen / Merck Millipore, Lucigen, NEB, Stratagene / Agilent, Takara, Promega, Clontech, Invitrogen Pichia kit K1710, etc.) — vendor-by-vendor.
- FPbase (fluorescent protein database)
- Primary-literature sequence deposits (per-journal posture).

### 4.3 Sequencing
`/ip-auditor` work is **independent of `/architect` work** and should be triggered in parallel. The ML-corpus ingestion (Track C) cannot begin until `/ip-auditor` has delivered.

---

## 5. Post-acceptance sequence (the rest of the cadence)

Assuming the user accepts this initial report:

| Step | Owner | Deliverable | Gates |
|---|---|---|---|
| 1 | `/scientific-advisor` | Update **REQUIREMENTS.md** — add new UR/FR/MR/WR/SR/BR/MS entries for host coverage, markers catalogue (per-host working concentrations), ML corpus governance (license + SnapGene cross-check), and biosafety inheritance from existing MS-* rules. | Requires this report accepted. |
| 2 | `/scientific-advisor` + `/dev-orchestrator` + `/architect` | Joint development plan — module decomposition, port amendments, CI-gate amendments, task-card outlines, milestone breakdown, model-tier assignments, dialogue-compression strategy. | Requires step 1 + `/architect` § 3 deliverable + `/ip-auditor` § 4 deliverable. |
| 3 | `/architect` | Update **ARCHITECTURE.md** to reflect the planned work structure (schema deltas, port additions, gates, ML-corpus subsystem). | Requires step 2. |
| 4 | `/dev-orchestrator` | Update **CODING_AGENDA.md** with new task cards (likely a new Phase 14 or a `Phase 4 extension` block depending on the architect's call) — IDs, tier assignments, dependencies, deliverables, acceptance criteria. | Requires step 3. |
| 5 | `/dev-orchestrator` | Update **TASK_BOARD.md** with the new tasks under "Active task queue" with real-time status tracking; risk register entries for the new IP-exposure surface; CI-gate lifecycle rows. | Requires step 4. |
| 6 | `/scientific-advisor` (per CODING_AGENDA assignment) | Begin implementation of the first task card. | Requires step 5 + `agenda_consistency_check.py` green. |

---

## 6. Open items requiring user confirmation

| # | Item | Default if no answer |
|---|---|---|
| (none — all 5 prior questions answered) | — | — |

The next decision point is **acceptance of this report** (in whole or with marked amendments). On acceptance, the cadence in § 5 begins immediately.

---

## 7. Recommended next user action

Invoke `/architect` and `/ip-auditor` (in either order or in parallel — they are independent) with this report as the briefing input. The `/architect` invocation should reference **§ 3** of this report; the `/ip-auditor` invocation should reference **§ 4**. Once both have delivered, return to `/scientific-advisor` to begin the REQUIREMENTS.md update (§ 5 step 1).

---

> **Disclaimer:** This scientific advisory report is provided for informational, research, and advisory purposes only. It does not constitute professional engineering advice or legal advice. The IP / ToS posture in § 4 is a scientific-advisor's risk-framed view; the binding determination must come from `/ip-auditor` and, if required, qualified IP counsel in the relevant jurisdiction. All strain, marker, and ML-corpus records to be drafted following this report's acceptance must be cross-verified against vendor genotype declarations, primary literature, and (per Decision #4) SnapGene reference records before being committed to the runtime catalogue or training corpus.
