# Joint Development Plan — Host / Marker / ML-Corpus Enrichment

**Project:** Cloning & Expression Vector Design Toolkit (post-`v0.1.0`, GPL-3.0, GMExpression / GMES-owned)
**Document type:** Three-skill joint development plan (cadence step 7)
**Authors (jointly):** `/scientific-advisor` + `/architect` + `/dev-orchestrator`
**Lead author this turn:** `/dev-orchestrator` (operational planning author; synthesises the prior accepted inputs from the other two roles)
**Date:** 2026-05-23
**Status:** **DRAFT — pending user acceptance (step 7 → step 8).** No `ARCHITECTURE.md`, `CODING_AGENDA.md`, `TASK_BOARD.md`, `schemas/*`, `catalogues/*`, `src/*`, or `docs/ml_corpus/*` changes have been made in this turn.

---

## 0. Working principle reference

This plan is produced under the project's standing 10-step cadence ([[cev-workflow-discipline]]). The plan completes step 7 and teesup the binding architecture / agenda / task-board updates at steps 8–10.

---

## 1. Provenance (cadence trail)

| Step | Owner | Artefact | Status |
|---|---|---|---|
| 1 | `/scientific-advisor` | `docs/handover/2026-05-23_host_marker_ml_corpus_initial_report.md` | ✅ Accepted |
| 2 | User | (acceptance of the initial report) | ✅ Accepted |
| 3 | `/architect` | `docs/handover/2026-05-23_host_marker_ml_corpus_architect_analysis.md` | ✅ Accepted |
| 4 | `/ip-auditor` | `docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit.md` | ✅ Accepted |
| 5 | User | (acceptance of both analyses) | ✅ Accepted |
| 6 | `/scientific-advisor` | `REQUIREMENTS.md` v0.2 amendment (§ 11) | ✅ Landed; `agenda_consistency_check.py` green (71 tasks, 50 ports) |
| **7** | **`/scientific-advisor` + `/dev-orchestrator` + `/architect`** | **This document** | **🟡 In progress** |
| 8 | `/architect` | `ARCHITECTURE.md` update (includes fork-readiness memorandum) | ⏳ Pending |
| 9 | `/dev-orchestrator` | `CODING_AGENDA.md` task-card additions + new CI gates | ⏳ Pending |
| 10 | `/dev-orchestrator` | `TASK_BOARD.md` update + implementation kickoff | ⏳ Pending |

---

## 2. Scope reaffirmation (three tracks)

| Track | Deliverable | Owning role(s) |
|---|---|---|
| **A — Host phenotype model expansion** | `hosts.schema.json` v1.0 → v1.1 (additive, all-optional); 9 new strain records (Origami(DE3), Origami B(DE3), Rosetta(DE3)pLysS, PichiaPink series, KM71, SMD1168H, AH109, Y187, EGY48) + opportunistic enrichment of overlapping pre-existing records via a deferred backfill task; new MR-55..60 rules become machine-checkable. | `/architect` (schema), `/scientific-advisor` (curation), `/dev-orchestrator` (sequencing) |
| **B — Selection-markers catalogue split** | New `catalogues/markers.yaml` + `schemas/markers.schema.json` v1.0; new `MarkersCataloguePort` as canonical port #51; new domain types `Marker / MarkerId / MarkerClass / HostClass / WorkingConcentration / CounterSelection`; dual-read migration window for `parts.yaml::markers`. 23 markers covered at v0.2 (9 bacterial + 6 yeast auxotrophic + 4 dominant yeast + 4 mammalian). | All three |
| **C — ML training corpus** | New `docs/ml_corpus/` sibling subsystem with manifests, schemas, license matrix, exclusions, SnapGene cross-check log; runtime-isolated via `import-linter` contract; split `sequence_license` + `annotation_license` per IP-auditor § 5.2; CC-BY-SA partition with **`partition: sa_free` as DEFAULT** per IPQ-1 resolution; SnapGene cross-check is process-only artefact; ~120 records at v0.2 (40 backbones + 80 modular elements). | All three |
| Cross-cutting | `IP_POLICY.md` at repo root; `LICENSES/THIRD_PARTY_NOTICES.md`; quarterly ToS re-check schedule; fork-readiness memorandum landing in `ARCHITECTURE.md` at step 8. | `/architect` + `/ip-auditor` |

---

## 3. Open-question resolutions (Architect Q1–Q10 + IP-auditor IPQ-1..IPQ-10)

### 3.1 Architect open questions

| # | Question | **Resolution** | Reasoning |
|---|---|---|---|
| **Q1** | Phase placement for new task cards. | **SPLIT.** Tracks A+B land as **Phase 4.2 extension** (Phase 4 was "Catalogues" and these tracks genuinely extend that scope). Track C lands as a **new Phase 14** (a fundamentally new subsystem with different governance — training data vs runtime config). | Keeps the existing Phase 4 module-boundary intact; isolates the ML corpus's separate license posture from the runtime catalogue's compliance gates. |
| **Q2** | Which new MR/WR/BR/SR rules are in-scope? | **MR-55..60 + BR-15..17 as captured in REQUIREMENTS.md v0.2 § 11.6–11.7. No additional SR-* or WR-* rules in v0.2.** | Audit confirms completeness. One candidate WR ("verify PCR template host genotype is dam+/dcm- as needed by downstream enzymes") would duplicate MR-55; defer to v0.3 if needed. |
| **Q3** | Port count drift. | **Canonical port count goes 50 → 51 (MarkersCataloguePort).** The six speculative v1.6 biological ports (FusionElementCatalogue, PolycistronicElementCatalogue, etc., per stale user memory) stay OUT of scope; they were never landed in `docs/port_manifest.yaml` and cannot be added without their own cadence pass. | Avoids opportunistically adding speculative scope. The drift in user memory is corrected by the port-count consistency CI check (architect § 4.4). |
| **Q4** | Existing-record v1.1 backfill. | **Deferred to T-408a** (a backfill task that runs in M-C, after new strain ingestion validates the schema end-to-end). Existing records remain valid under v1.1 (all fields optional). | Don't double the QA burden during M-A/M-B; exercise the schema on the 9 new strains first. |
| **Q5** | Cell-free hosts (PURE, myTXTL). | **Exempt via `chassis_class: cell_free` discriminator.** Schema CI check skips v1.1 phenotype field expectations for cell_free entries (no genome → no lon/ompT/trxB-gor applicable). | Recommended in architect § 6 Q5; no contention. |
| **Q6** | ML corpus in-tree vs Git LFS. | **Per-record in-tree (JSON ~few KB each). Release tar.gz bundles in LFS** when total > 100 MB. v0.2 corpus is expected ~120 records × ~10 KB = ~1.2 MB → no LFS needed at v0.2. | Smallest-friction option; matches architect § 6 Q6 recommendation. |
| **Q7** | iGEM CC-BY-SA contagion. | **Accepted.** Subfolder routing `docs/ml_corpus/records/cc-by-sa/` + dual-partition (`partition: full` and `partition: sa_free`) per IP-auditor § 6.3, with `partition: sa_free` as DEFAULT per IPQ-1 resolution. | Direct consequence of IPQ-1 (research-primary, commercial-fork-possible). |
| **Q8** | Split sequence/annotation license amendment. | **Fold into step 8 ARCHITECTURE.md update.** No re-issue of step 3. | Small backward-incompatible change; architect already accepted; loop-avoidance preferred. |
| **Q9** | Working-concentration regional variation. | **Sambrook 4th ed. Appendix A1 default with `working_concentrations[].notes` field carrying variant info.** Vendor-specific overrides via the same `notes` field. Institutional overrides via the existing `institutional_policy.yaml` mechanism. | Matches REQUIREMENTS FR-MARK-09 (already drafted). |
| **Q10** | Mammalian markers count. | **In-scope at v0.2** (FR-MARK-08). Mammalian markers covered: Puromycin (pac), Blasticidin (bsr/bsd), Hygromycin B (hph-mammalian), G418 / Geneticin (neo, mammalian context). | Avoids near-immediate v0.3 bump. |

### 3.2 IP-auditor open questions

| # | Question | **Resolution** | Reasoning |
|---|---|---|---|
| **IPQ-1** | Commercial deployment intent. | **RESOLVED by user 2026-05-23: research-primary, commercial-fork-possible.** Implications: (a) `partition: sa_free` is the **DEFAULT** training partition, not opt-in; (b) a **fork-readiness memorandum** lands in `ARCHITECTURE.md` at step 8 (see § 10 of this plan). | Direct user decision. The fork-readiness memo is NORMATIVE for any future fork attempt. |
| **IPQ-2** | Maintain both partitions or commit to one? | **Maintain both.** `partition: sa_free` is default for the model and what release-gate checks. `partition: full` is opt-in for research-only training runs that explicitly accept share-alike. Both partitions CI-checked and release-tracked. | Required by IPQ-1: research use accepts share-alike; commercial fork needs sa_free. |
| **IPQ-3** | Proactively seek vendor ML-training licenses? | **Deferred to a future cadence.** Useful long-term (could unlock cleaner ingestion of vendor manual content) but not blocking v0.2. Flagged as a follow-up item in the risk register. | Scope discipline; v0.2 already substantial. |
| **IPQ-4** | Quarterly ToS re-check schedule. | **Yes.** Owner: `/dev-orchestrator` (run); `/ip-auditor` (review). Cadence: quarterly. Archive method: perma.cc snapshots of each ToS page committed to `docs/ip_policy/tos_snapshots/{YYYY-QQ}/`. **First snapshot due 2026-Q3 (by 2026-09-30).** | Counteracts the IP-auditor § 1.1 knowledge-cutoff drift; makes vendor-ToS changes visible. |
| **IPQ-5** | SnapGene cross-check coverage release-gate threshold. | **90%** at release-tag time per architect § 5.2. Below 90% blocks release-tag promotion; does NOT block PR merges. | Statistical confidence + leaves headroom for new records; matches architect's number. |
| **IPQ-6** | Sequence/annotation license split — re-issue step 3 or fold? | **Fold into step 8** (same answer as architect Q8). | Loop-avoidance. |
| **IPQ-7** | Formal `IP_POLICY.md` at repo root? | **Yes.** Lands in step 9 (new task T-1410). Contents: source tier list (IP-auditor § 8.1), SnapGene posture (§ 3), CC-BY-SA partition strategy (§ 6.3), fork-readiness memo pointer, quarterly ToS re-check schedule (IPQ-4). | Counsel-facing artefact; IP-auditor explicitly recommended; reduces ambiguity at fork time. |
| **IPQ-8** | Trademark / nominative-use disclaimer location. | **One canonical file** at `LICENSES/THIRD_PARTY_NOTICES.md`. Short pointer in each README that names SnapGene. | Reduces drift; centralises the disclaimer for one-line update if counsel revises. |
| **IPQ-9** | CI heuristic for vendor-annotation contamination. | **Yes.** New CI gate `corpus-annotation-provenance-check` (T-1408) — scans each record's annotation `qualifiers` for long-string patterns matching known vendor-manual phrasing. Heuristic-based. Lands in `informational` mode at v0.2; promote to `enforced` after observation. | Catches accidental verbatim ingestion; cheap insurance. |
| **IPQ-10** | Training pipeline (`ml/` or `training/` folder) stub. | **Deferred.** Out of scope for v0.2. v0.2 produces the corpus; the consumer (training pipeline) is a separate cadence. | Scope discipline. |

---

## 4. Phase + task-card design

20 new task cards total: 9 in Phase 4.2, 11 in Phase 14. All cards follow the existing `T-NNN` convention. Total post-v0.2: 71 + 20 = **91 task cards**.

### 4.1 Phase 4.2 — Catalogue extension (Tracks A + B)

| ID | Title | Tier | Inputs / Dependencies | Deliverables | Acceptance |
|---|---|---|---|---|---|
| **T-407** | Host schema v1.1 amendment | **Sonnet** | REQUIREMENTS.md FR-HOST-13..20; architect § 2.1 fragments | `schemas/hosts.schema.json` v1.1 (additive optional fields); migration test asserting existing `hosts.yaml` v1.0 records validate cleanly under v1.1; schema-version bump CI check extension. | Existing `hosts.yaml` parses unchanged; v1.1 fields validate per architect fragments. |
| **T-408** | Markers schema v1.0 (new file) | **Sonnet** | T-407; architect § 2.2; IP-auditor § 5.2 license-split implications acknowledged (sequence/annotation split is on the **corpus** record, not the markers record — no schema impact here) | `schemas/markers.schema.json` v1.0 with `marker / citation / maintenance / working_concentrations / counter_selection / host_genotype_requirement` `$defs`; JSON-schema validator wiring; auxotrophic-sanity CI extension. | Empty `catalogues/markers.yaml` shell validates; auxotrophic sanity warns on accidental non-zero concentrations. |
| **T-408a** | Existing host-record v1.1 backfill | **Sonnet** | T-407, T-410, T-411 (must observe schema in production first); architect § 6 Q4 deferred-backfill plan | DH5α, TOP10, JM109, XL1-Blue, Stbl3, BL21 baseline, cell-free (with `chassis_class: cell_free` discriminator added), yeast / mammalian / insect / plant / phage-VLP records enriched with v1.1 fields where applicable. ~6–8 records touched. | `host-marker-link-integrity-check` green; agenda check green; no behavioural diff in existing engine tests. |
| **T-409** | `MarkersCataloguePort` + adapter + domain types | **Sonnet** | T-408 | `src/domain/ports/markers_catalogue.py`; `src/domain/types/markers.py`; `src/adapter/catalogue/yaml_markers_catalogue.py`; composition-root wiring in `src/app/composition_root.py`; port_manifest bumped 50 → 51. | Port-inventory test passes (51 ports); read methods return correctly typed data on empty + populated catalogue fixtures. |
| **T-410** | `markers.yaml` content population | **Opus** *(scientific curation; high judgement load — per-host concentrations, citation grading, host-genotype requirements)* | T-409; REQUIREMENTS.md FR-MARK-05..08 | `catalogues/markers.yaml` with 23 markers (9 bacterial + 6 yeast auxotrophic + 4 dominant yeast + 4 mammalian); every entry cited (Sambrook 4th ed. + primary lit where divergent). | `markers-citation-presence-check` green; Sambrook citations verified for all working concentrations. |
| **T-411** | New `hosts.yaml` strain entries (9 new) | **Opus** *(scientific curation; per-strain phenotype field population)* | T-407, T-410 (so `recommended_selection_markers[]` can link) | Origami(DE3), Origami B(DE3), Rosetta(DE3)pLysS, PichiaPink series (PP1–PP4), KM71, SMD1168H, AH109, Y187, EGY48 — full v1.1 fields populated; primary-lit citations (Bessette 1999, Cregg 2000, James 1996, etc.). | `host-marker-link-integrity-check` green; FR-HOST-16 inventory check green. |
| **T-412** | `engine.compatibility` migration to MarkersCataloguePort | **Sonnet** | T-409, T-410, T-411 | Migration code; dual-read shim (first try `MarkersCataloguePort`, on miss fall back to `parts.yaml::markers` with WARN-level log line); existing engine tests unchanged-result. | Existing compatibility-engine tests pass; new MR-MARKER-MISMATCH advisory test passes. |
| **T-413** | `engine.validation` migration to MarkersCataloguePort | **Sonnet** | T-409, T-412 | Same dual-read shim mechanism; validator-rule predicates that touch markers re-pointed; shim-hit telemetry logged. | Existing validator tests pass; shim-hit log lines emitted under controlled fixture. |
| **T-414** | New MR-55..60 rule predicates | **Sonnet** | T-411 (host fields), T-410 (markers), T-413 (port wiring) | Rule manifests in `catalogues/rules/MR.yaml`; predicate implementations under `src/engine/validation/predicates/`; rule fixtures (2 per rule). | Each rule fires on its positive fixture and stays silent on its negative fixture. |
| **T-415** | New CI gates landing for Tracks A+B | **Sonnet** | T-410, T-411 | `tools/ci/markers_citation_presence_check.py`; `tools/ci/host_marker_link_integrity_check.py`; `agenda_consistency_check.py` extensions (port count, schema_version monotonicity, hosts-v1.1-field-coverage soft check). | All three gates `enforced` and green. |

### 4.2 Phase 14 — ML training corpus subsystem (Track C)

| ID | Title | Tier | Inputs / Dependencies | Deliverables | Acceptance |
|---|---|---|---|---|---|
| **T-1401** | `docs/ml_corpus/` scaffold + import-linter contract | **Haiku** *(boilerplate)* | Architect § 5.1 layout | Folder tree with empty manifests / exclusions / crosscheck_log; README.md with working-principle preamble + nominative-use disclaimer; `pyproject.toml` import-linter contract `ml-corpus-is-not-runtime` (forbidden: `src.*` → `docs.ml_corpus.*`). | `import-linter` green; tree exists. |
| **T-1402** | Corpus record schema v1.0 (with split license) | **Sonnet** | T-1401; architect § 2.3 + IP-auditor § 5.2 (split sequence/annotation license folded in atomically — Q8/IPQ-6 resolution) | `docs/ml_corpus/schemas/corpus_record.schema.json` v1.0 with `license { sequence_license, annotation_license }` block, snapgene_crosscheck block, provenance enum (allowlist per FR-ML-04). | Empty corpus validates; one positive + one negative record fixture exercise the schema. |
| **T-1403** | `ml-corpus-license-check` CI gate | **Sonnet** | T-1402 | `tools/ci/ml_corpus_license_check.py`; default-deny on missing license block; dual-read shim-hit telemetry (extended scope to also count BR-16 violations). | Gate `informational` initially; promoted `enforced` after T-1407. |
| **T-1404** | Initial backbone corpus seed (~40 records) | **Opus** *(scientific curation; per-backbone provenance, license, cross-check)* | T-1402, T-1403 | 40 backbone records under `records/backbones/{ecoli,kphaffii,scerevisiae,mammalian}/`; sources: NCBI Nucleotide / EBI / iGEM CC0 entries / vendor primary publications. CC-BY-SA entries (if any) routed to `cc-by-sa/`. | All 40 records validate; `provenance.source` ∈ allowlist; `snapgene_crosscheck.checked: false` allowed at this stage; license aggregate reports populated. |
| **T-1405** | Initial modular-element corpus seed (~80 records) | **Opus** *(scientific curation)* | T-1402, T-1403 | 80 modular element records (promoters, terminators, RBS/Kozak, polyA, IRES/2A, MCS, tags, fluorescent proteins, selection cassettes, insulators, introns/WPRE) under `records/elements/{...}/`. | Same as T-1404. |
| **T-1406** | BR-16 SnapGene pipeline-scan CI gate | **Sonnet** | T-1401 | `tools/ci/snapgene_pipeline_scan.py` — scans `.github/workflows/`, `tools/*.py`, `Dockerfile`, `mkdocs.yml`, any CI-config or pipeline script for invocations of `curl`, `wget`, `httpx`, `requests`, `playwright`, `selenium`, or MCP web-fetch targeting `snapgene.com`. | Gate `enforced` from day one (defensive default-deny). |
| **T-1407** | CC-BY-SA partition routing + manifest generation | **Sonnet** | T-1404, T-1405 | `tools/corpus/partition_router.py` (routes records into `cc-by-sa/` based on license block); `tools/corpus/manifest_generator.py` (regenerates `corpus_manifest.yaml::license_aggregate` after each PR); `corpus_manifest.yaml` populated with two partitions (`full` + `sa_free`); **`partition_default: sa_free`** locked in. | Manifest aggregate matches the on-disk records; both partitions queryable; `partition: sa_free` is default. |
| **T-1408** | IPQ-9 `corpus-annotation-provenance-check` CI gate | **Sonnet** | T-1404, T-1405 | `tools/ci/corpus_annotation_provenance_check.py` — heuristic scanner that flags annotation `qualifiers` containing long string patterns matching known vendor-manual phrasing (Invitrogen, Novagen, Stratagene, Takara, Promega, NEB, Lucigen, SnapGene). | Lands `informational` at v0.2; promote to `enforced` in v0.3 after observing false-positive rate. |
| **T-1409** | `corpus_release_gate.py` (release-tag time) | **Sonnet** | T-1407 | `tools/release/corpus_release_gate.py` — enforces release-time criteria: `fraction_checked >= 0.90` (SnapGene cross-check), `attribution_text_file` exists, no Tier-3 sources, no missing license blocks. | Gate fires on tag promotion only; PR merges unaffected. |
| **T-1410** | `IP_POLICY.md` + `LICENSES/THIRD_PARTY_NOTICES.md` | **Sonnet** | T-1407, T-1409 | `IP_POLICY.md` at repo root (source tier list, SnapGene posture, partition strategy, fork-readiness pointer, quarterly ToS re-check schedule); `LICENSES/THIRD_PARTY_NOTICES.md` (consolidated trademark / attribution disclaimers; SnapGene nominative-use disclaimer canonical form). | Both files committed; README files referencing SnapGene shortened to one-line pointers. |
| **T-1411** | Fork-readiness memorandum drafting (for ARCHITECTURE.md at step 8) | **Opus** *(strategic content; counsel-facing)* | T-1410 (must observe the policy artefacts first) | Draft of the memorandum content under § 10 of this plan, ready for `/architect` to fold into `ARCHITECTURE.md` at step 8. | Memo enumerates (a) datasets to exclude, (b) workflows to retune, (c) design elements to re-point, (d) license/IP posture for the fork, (e) regulatory posture for commercial release. NORMATIVE status. |

---

## 5. Milestone breakdown

### M-A — Foundations (schemas + scaffold)
**Duration target:** ~1 week of focused work.
**Tasks:** T-407 (hosts schema v1.1), T-408 (markers schema v1.0), T-1401 (corpus scaffold), T-1402 (corpus record schema), T-1406 (BR-16 pipeline-scan CI gate landed early as defensive measure).
**Exit conditions:**
- All four new schemas committed and validating.
- `import-linter ml-corpus-is-not-runtime` contract green.
- `snapgene-pipeline-scan` CI gate green (no existing pipeline accesses snapgene.com).
- `agenda_consistency_check.py` green: 71 + 0 = 71 tasks (no new tasks visible in agenda yet — they land at step 9), 50 + 1 = 51 ports.

### M-B — Core implementations (catalogues populated, engines migrated, corpus seeded)
**Duration target:** ~2–3 weeks.
**Tasks:** T-409 (port + adapter), T-410 (markers.yaml population — Opus), T-411 (new strain records — Opus), T-412 (engine.compatibility migration with dual-read shim), T-413 (engine.validation migration), T-414 (MR-55..60 predicates), T-1403 (ml-corpus-license-check), T-1404 (backbone seed — Opus), T-1405 (element seed — Opus).
**Exit conditions:**
- 23 markers committed; 9 new strain records committed.
- ~120 corpus records committed.
- Engine migrations green; dual-read shim hit-rate baseline established (logged for one full release cycle observation in M-C).
- MR-55..60 fire correctly on positive fixtures and stay silent on negatives.
**Compression checkpoint:** between M-B and M-C — the curation work in M-B is the heaviest scientific-judgement load of the plan; a context-reset before M-C policy + CI work is recommended.

### M-C — CI gates + policy (release-readiness)
**Duration target:** ~1 week.
**Tasks:** T-415 (markers + host-marker-link CI gates), T-408a (existing host-record backfill), T-1407 (CC-BY-SA partition routing + manifest generation), T-1408 (annotation-provenance heuristic CI), T-1409 (release-gate), T-1410 (IP_POLICY.md + THIRD_PARTY_NOTICES.md), T-1411 (fork-readiness memo draft for step 8).
**Exit conditions:**
- All six new CI gates green and lifecycle-stamped (`enforced` for the four hard gates; `informational` for the two soft gates).
- `corpus_manifest.yaml::license_aggregate` populated and reporting both partitions.
- `partition: sa_free` is the default; the release-gate's commercial-fork posture is enforceable.
- Fork-readiness memorandum drafted and handed off to `/architect` for step 8 inclusion.

---

## 6. Tier selection + dialogue compression

### 6.1 Tier-by-task

| Tier | Tasks | Total |
|---|---|---|
| **Opus** | T-410 (markers.yaml curation), T-411 (new strain records), T-1404 (backbone seed), T-1405 (element seed), T-1411 (fork-readiness memo) | 5 |
| **Sonnet** | T-407, T-408, T-408a, T-409, T-412, T-413, T-414, T-415, T-1402, T-1403, T-1406, T-1407, T-1408, T-1409, T-1410 | 15 |
| **Haiku** | T-1401 (scaffold) | 1 |

Opus tasks share two characteristics: (i) scientific or strategic judgement load, (ii) citation/provenance correctness directly affecting release-gate compliance. Sonnet covers engineering-implementation tasks where the spec is concrete. Haiku reserved for the single pure-boilerplate task.

### 6.2 Compression checkpoints

| Boundary | Rationale | Action |
|---|---|---|
| Before M-A | Sufficient context exists; no compression needed unless the session is YELLOW or RED. | Proceed normally. |
| Between M-A and M-B | M-B is the largest work block (9 tasks including 4 Opus curation tasks). | If post-M-A context is YELLOW, compress before M-B starts. |
| Between M-B and M-C | M-C is shorter (7 tasks) but spans policy + CI + memo work that benefits from a clean slate. | **Compress checkpoint** — generate milestone handover for M-B; reset context for M-C. |
| Before T-1411 | Fork-readiness memo is strategic content; should not be drafted under context pressure. | Pre-compress to ensure Opus has ample budget. |

---

## 7. Module registry sketch

### 7.1 New modules introduced

| Module | Purpose | Owning task |
|---|---|---|
| `domain.ports.markers_catalogue` | New read-only port (canonical #51) over the markers catalogue | T-409 |
| `domain.types.markers` | `Marker`, `MarkerId`, `MarkerClass`, `HostClass`, `WorkingConcentration`, `CounterSelection` value types | T-409 |
| `adapter.catalogue.yaml_markers_catalogue` | YAML loader + JSONSchema validator + immutable in-memory model | T-409 |
| `tools.ci.markers_citation_presence_check` | Validates citation grade on every marker entry + working-concentration entry | T-415 |
| `tools.ci.host_marker_link_integrity_check` | Validates every `recommended_selection_markers[]` link resolves | T-415 |
| `tools.ci.ml_corpus_license_check` | Validates every corpus record has complete license block; dual-read shim telemetry | T-1403 |
| `tools.ci.snapgene_pipeline_scan` | Forbidden-tool-invocation scanner (BR-16) | T-1406 |
| `tools.ci.corpus_annotation_provenance_check` | Vendor-annotation contamination heuristic (IPQ-9) | T-1408 |
| `tools.corpus.partition_router` | Routes records into `cc-by-sa/` based on license; regenerates manifest | T-1407 |
| `tools.corpus.manifest_generator` | Computes `corpus_manifest.yaml::license_aggregate` | T-1407 |
| `tools.release.corpus_release_gate` | Release-tag-time gate (≥ 90% cross-check coverage, attribution complete, no Tier-3 sources, no missing license) | T-1409 |

### 7.2 Updated modules

| Module | Update | Owning task |
|---|---|---|
| `engine.compatibility` | Add `MarkersCataloguePort` dependency; dual-read shim for `parts.yaml::markers` fallback during migration window | T-412 |
| `engine.validation` | Same dual-read pattern; rule predicates that reference markers re-pointed | T-413 |
| `app.composition_root` | Wire `YamlMarkersCatalogue` instance; inject into compatibility + validation engines | T-409 |
| `catalogues/rules/MR.yaml` | Add MR-55..60 rule entries with fixtures | T-414 |
| `docs/port_manifest.yaml` | Add port #51 (`MarkersCataloguePort`); bump `canonical_port_count` 50 → 51 | T-409 |
| `tools/agenda_consistency_check.py` | New checks: port-count consistency, schema_version monotonicity, hosts-v1.1-field-coverage soft check | T-415 |

### 7.3 Out-of-runtime subsystem

`docs/ml_corpus/*` — training data, **not** runtime configuration. Enforced by the `import-linter` contract (`src.*` → `docs.ml_corpus.*` forbidden). Has its own schema, its own CI gates, its own manifest, its own release-time gate, its own subfolder structure.

---

## 8. CI gate landing order

| Order | Gate | Landing task | Initial mode | Promoted to `enforced` after |
|---|---|---|---|---|
| 1 | `agenda_consistency_check.py` port-count extension | T-407 | `enforced` (atomically with `hosts.yaml` schema_version bump) | (already enforced) |
| 2 | `snapgene-pipeline-scan` (BR-16) | T-1406 | **`enforced` from day one** (defensive default-deny) | (already enforced) |
| 3 | `ml-corpus-license-check` | T-1403 | `informational` | T-1407 lands the routed corpus |
| 4 | `markers-citation-presence-check` | T-415 | `informational` | T-410 lands the populated `markers.yaml` |
| 5 | `host-marker-link-integrity-check` | T-415 | `informational` | T-411 lands the new strain records with `recommended_selection_markers[]` |
| 6 | `corpus-annotation-provenance-check` (IPQ-9) | T-1408 | `informational` | **Stays `informational` at v0.2**; promote in v0.3 once false-positive rate is observed |
| 7 | `corpus_release_gate.py` | T-1409 | `enforced` at release-tag time only | (already enforced for tags; not on PR) |

Existing CI gates remain at their v0.1.0 status; no v0.2 task modifies them.

---

## 9. Risk register

| # | Risk | Severity | Owner | Mitigation |
|---|---|---|---|---|
| **R-V0.2-01** | `MarkersCataloguePort` migration breakage during dual-read window. | HIGH | `/dev-orchestrator` + `/scientific-coder` | Dual-read shim with WARN-level telemetry; data-driven cut-over decision (close shim only after zero hit-rate for one full release cycle); rollback path documented (revert to `parts.yaml::markers` until shim hits are eliminated). |
| **R-V0.2-02** | Fork-readiness memorandum gap — commercial fork attempted without consulting the memo, share-alike obligations leak into commercial product. | HIGH | `/architect` + `/dev-orchestrator` + counsel | Memo lands in `ARCHITECTURE.md` at step 8 with NORMATIVE status; fork attempts MUST cite the memo's exclusion list; `IP_POLICY.md` at repo root forces the memo into the fork's review path. |
| **R-V0.2-03** | Vendor ToS revision mid-cadence invalidates BR-16 posture (e.g., SnapGene adds explicit ML-training clause). | MEDIUM | `/ip-auditor` + `/dev-orchestrator` | Quarterly ToS re-check (IPQ-4 schedule); first snapshot due 2026-Q3 by 2026-09-30; archive method perma.cc → `docs/ip_policy/tos_snapshots/{YYYY-QQ}/`. |
| **R-V0.2-04** | CC-BY-SA contagion at commercial-fork time — content from `partition: full` accidentally retained in commercial model. | MEDIUM | `/ip-auditor` + counsel | `partition: sa_free` is default; release-gate (T-1409) checks training-manifest partition declaration; fork-readiness memo enumerates exclusion list. |
| **R-V0.2-05** | SnapGene cross-check coverage gap at release time (< 90%). | MEDIUM | `/scientific-advisor` | Release-gate (T-1409) enforces ≥ 90%; coverage reported in `corpus_manifest.yaml::license_aggregate.cross_check_coverage`; surface in TASK_BOARD.md M-C exit condition. |
| **R-V0.2-06** | Schema v1.1 backward-compatibility break (existing records fail to validate). | LOW | `/architect` | Additive-only design; all v1.1 fields optional; T-407 includes a migration test that asserts existing `hosts.yaml` v1.0 records parse cleanly under v1.1. |
| **R-V0.2-07** | Stale "56 canonical ports" memory drift confuses future sessions. | LOW | `/dev-orchestrator` | Port-count consistency CI check (T-415); memory entry already corrected; the v1.6 biological-ports speculation is now explicitly out-of-scope (Q3). |
| **R-V0.2-08** | New strain-record citation quality drift (vendor manual where primary lit exists). | LOW | `/scientific-advisor` | `markers-citation-presence-check` (T-415) enforces grade A1/A2/A3/B1/B2 only; T-411 acceptance gate includes manual citation audit. |
| **R-V0.2-09** | Annotation-provenance heuristic false-positive rate too high (IPQ-9). | LOW | `/dev-orchestrator` | Gate lands `informational` at v0.2; observe FP rate; tune patterns before promoting to `enforced` in v0.3. |
| **R-V0.2-10** | Vendor ML-training license outreach (IPQ-3) deferred too long; vendor materials remain unusable in corpus. | LOW | `/dev-orchestrator` | Tracked as a future-cadence item; not blocking v0.2; revisit during v0.3 planning. |

---

## 10. Fork-readiness memorandum scope (per IPQ-1)

This memorandum will be drafted in **T-1411** and folded by `/architect` into `ARCHITECTURE.md` at step 8 as a new top-level section. Its status is NORMATIVE: any future attempt to fork the project for commercial deployment must consult and comply with it.

### 10.1 (a) Datasets to exclude or substitute

| Class | Exclusion / Substitution rule |
|---|---|
| `docs/ml_corpus/records/cc-by-sa/` | **Exclude entirely** from commercial fork. CC-BY-SA share-alike obligation precludes commercial-friendly redistribution. |
| Records where `sequence_license.commercial_use_allowed == false` | Exclude. |
| Records where `annotation_license.commercial_use_allowed == false` | Strip annotation; retain sequence (per FR-ML-07 stripping rule). |
| Records where `sequence_license.ml_training_allowed == false` | Exclude entirely. |
| Records where `annotation_license.ml_training_allowed == false` | Strip annotation; retain sequence. |
| Records with `provenance.source == addgene_metadata_only` | Already default-deny per FR-ML-04; never enters the corpus. Double-check at fork time. |
| Records added after the last counsel review | Quarantine until counsel-reviewed for the fork's commercial context. |

### 10.2 (b) Workflows to relax / tighten

| Workflow | Research posture (current) | Commercial-fork posture |
|---|---|---|
| Default training partition | `partition: sa_free` (per IPQ-1) | **`partition: sa_free` ONLY** — `partition: full` is unavailable for commercial training. |
| Release-tag gate | `corpus_release_gate.py` enforces v0.2 criteria | **+ commercial criteria**: 100% records have `commercial_use_allowed: true` on both sequence and annotation licenses; counsel-review certificate attached. |
| SnapGene cross-check coverage threshold | ≥ 90% | **≥ 95%** (tighter for commercial) — quality bar is higher when liability is higher. |
| ToS re-check cadence | Quarterly | **Re-run immediately on fork creation**, then continue quarterly with commercial-lens questions added. |
| Counsel review | Optional / pre-release | **MANDATORY for every commercial release** — IP-auditor § 8.3 #5 explicit. |

### 10.3 (c) Design elements to re-point

| Element | Re-point action |
|---|---|
| `corpus_manifest.yaml::partition_default` | Lock to `sa_free`; remove the `full` option from the commercial fork's manifest entirely. |
| Trained-model checkpoints | Any checkpoint produced from `partition: full` is **not distributable** in the commercial fork. Only `partition: sa_free` checkpoints survive. |
| Training manifests | Must declare partition AND have `counsel_review_passed: true` AND `counsel_review_date`. |
| Trademark / branding | New trademark / product name distinct from "Cloning Expression Vector Design Toolkit" (which may be construed as research-product branding). |
| Project root `IP_POLICY.md` | Replaced with a commercial-edition policy referencing the memo. |

### 10.4 (d) License + IP posture for the fork

| Surface | Posture |
|---|---|
| Toolkit code license | GPL-3.0 inherited as-is. The toolkit *code* remains GPL on the fork; this is independent of training data + model licensing decisions. |
| Trained-model weights | Must be released under a commercially-friendly license (Apache-2.0, MIT, or proprietary). **Not** CC-BY-SA, **not** GPL. (GPL on weights is contested but a known-risk posture.) |
| Attribution | Aggregate via fork's `THIRD_PARTY_NOTICES.md`. Every CC-BY record's attribution preserved. |
| Trademark | SnapGene nominative-use disclaimer retained; new fork's own branding documented; any vendor trademarks used in fork branding require separate counsel review. |
| Fresh ToS re-check | All vendor ToS pages re-verified at fork-creation time and at every commercial release. |
| Counsel review | Mandatory before any commercial release; one full-corpus + full-model pass per release tag. |

### 10.5 (e) Regulatory posture

| Surface | Posture |
|---|---|
| Biosafety floor (MS-01..06) | Already in place; sufficient for research; **re-evaluate** for commercial deployment in case stricter screening is needed when the tool is used at scale by external parties. |
| Export control (US EAR) | Biotechnology software may fall under ECCN 1E001 (technology for production of micro-organisms) or related; verify with counsel before US commercial export. |
| DURC (Dual Use Research of Concern) | Commercial use at scale may attract NIH OSP DURC review; engage NIH Office of Science Policy if US-based commercial release. |
| Australian biosecurity legislation | GPL distribution for research is generally fine; commercial distribution from an Australian entity (GMExpression / GMES) may trigger Defence Trade Controls Act 2012 review. Verify with AU counsel. |
| EU AI Act + EU GPAI obligations | If the commercial fork is offered in EU, the AI Act's GPAI requirements (transparency, training-data summaries, copyright respect) apply. Out of project's stated jurisdictions (AU + US) but relevant if commercial scope is global. |
| Quarterly re-check of all regulatory items | Same cadence as ToS re-check (IPQ-4). |

---

## 11. Step 8 / 9 / 10 hand-off specification

### 11.1 Step 8 — `ARCHITECTURE.md` update (owner: `/architect`)

The architect must, at step 8:

1. **Bump `hosts.yaml` schema_version language** from v1.0 to v1.1 in the architecture document; reference T-407.
2. **Add `MarkersCataloguePort` to § 4.5 port inventory** as port #51, category `catalogue`, owning task `T-409`; bump `canonical_port_count: 50 → 51` in the prose and ensure consistency with `docs/port_manifest.yaml`.
3. **Add the corpus subsystem to the module map** under an "out-of-runtime" boundary section; document the `import-linter` contract preventing `src.*` → `docs.ml_corpus.*`.
4. **Fold the IP-auditor § 5.2 split sequence/annotation license schema** into the corpus_record description (Q8 / IPQ-6 resolution: fold, don't re-issue step 3).
5. **Add the `partition: sa_free` DEFAULT** posture per IPQ-1 to the corpus subsystem section.
6. **Add the quarterly ToS re-check schedule** (IPQ-4) to the operational concerns section, with the first-snapshot deadline 2026-09-30.
7. **Add `IP_POLICY.md` to the repo-root document inventory** with a one-sentence summary.
8. **Add the FORK-READINESS MEMORANDUM** as a new top-level section (template provided in § 10 of this plan); status NORMATIVE for future fork attempts.
9. **Document the 56-port memory-drift correction**: the canonical port count is and remains 50 (now → 51 with this amendment); the six speculative v1.6 biological catalogue ports referenced in earlier session memory never landed and are explicitly out of scope for this amendment.

### 11.2 Step 9 — `CODING_AGENDA.md` update (owner: `/dev-orchestrator`)

The dev-orchestrator must, at step 9:

1. **Add Phase 4.2 section** with T-407..T-415 (9 tasks).
2. **Add Phase 14 section** with T-1401..T-1411 (11 tasks).
3. **Update `EXPECTED_TOTAL`** in `tools/agenda_consistency_check.py`: 71 → 91.
4. **Update `EXPECTED_COUNTS`**: add `"4.2": 9` and `"14": 11`.
5. **Update `EXPECTED_PHASES`**: insert `"4.2"` after `"4"`; append `"14"`.
6. **Update `EXPECTED_PHASE4_2`** = ["T-407", "T-408", "T-408a", "T-409", "T-410", "T-411", "T-412", "T-413", "T-414", "T-415"].
   (Note: T-408a is a sub-task numerically inserted; agenda's range grammar supports this.)
7. **Update `EXPECTED_PHASE14`** = ["T-1401", "T-1402", "T-1403", "T-1404", "T-1405", "T-1406", "T-1407", "T-1408", "T-1409", "T-1410", "T-1411"].
8. **Add `STALE_IDS`**: `"T-MARKERS-SHIM"` (will fire after T-412/T-413 close the dual-read window).
9. **Add the six new CI gates** to § 3.5 lifecycle table.
10. **Add the new port** to § 0.3 / § 3 / module manifest / port manifest references.
11. **Add `IP_POLICY.md` and `LICENSES/THIRD_PARTY_NOTICES.md`** to the Files-list under Phase 14.
12. **Maintain `agenda_consistency_check.py` green** throughout — every PR must keep the check green.

### 11.3 Step 10 — `TASK_BOARD.md` update + implementation kickoff (owner: `/dev-orchestrator`)

The dev-orchestrator must, at step 10:

1. **Add Phase 4.2 and Phase 14 rows** to § 1 "Global progress" with status ⚪ planned.
2. **Add the 20 new tasks** to § 3 "Active task queue" with status ⚪ planned, model tier per § 6.1 of this plan, dependencies declared.
3. **Add the three milestones** (M-A, M-B, M-C) to a new § 2.X "Milestones" sub-section with exit conditions per § 5 of this plan.
4. **Add the 10 risk register entries** to § 4 (or wherever the existing risk register lives in TASK_BOARD.md).
5. **Add the six new CI gates** to § 7 "CI gate lifecycle" with initial state.
6. **Update the "Next milestone" header** to point at M-A entry-point tasks T-407 + T-1401 (both Sonnet/Haiku — no Opus tasks at M-A entry, allowing immediate kickoff without compression).
7. **Update the cumulative task count** in the dashboard's headline metrics: 71 (v0.1.0) + 20 (v0.2) = 91.
8. **Trigger implementation kickoff**: T-407 and T-1401 transition from ⚪ planned to 🟡 in-progress as M-A begins.

---

## 12. Acceptance checklist (JP-1 … JP-14) — mirrors architect AC-* and IP-auditor AC-* format

Before this joint plan is accepted (cadence step 7 → step 8), please confirm or amend the following:

| # | Item | Default |
|---|---|---|
| **JP-1** | Phase placement: Phase 4.2 extension for Tracks A+B; new Phase 14 for Track C. | Accept. |
| **JP-2** | 20 new task cards as scoped in § 4 (T-407..T-415 + T-1401..T-1411 + T-408a backfill). | Accept. |
| **JP-3** | Three milestones M-A, M-B, M-C with stated exit conditions per § 5. | Accept. |
| **JP-4** | Tier selection per § 6.1: 5 Opus, 15 Sonnet, 1 Haiku. Compression checkpoint between M-B and M-C. | Accept. |
| **JP-5** | `MarkersCataloguePort` as canonical port **#51**; the six speculative v1.6 biological ports explicitly **out of scope** for this amendment. | Accept. |
| **JP-6** | Six new CI gates land in the order per § 8 (with `snapgene-pipeline-scan` enforced from day one as defensive default-deny). | Accept. |
| **JP-7** | Risk register with 10 entries; owners and mitigations defined. | Accept. |
| **JP-8** | Fork-readiness memorandum scope per § 10 — NORMATIVE for future commercial fork attempts. | Accept. |
| **JP-9** | `partition: sa_free` is the **DEFAULT** training partition (consequence of IPQ-1 resolution). | Accept. |
| **JP-10** | `IP_POLICY.md` lands at repo root; `LICENSES/THIRD_PARTY_NOTICES.md` centralises trademark / attribution disclaimers. | Accept. |
| **JP-11** | Quarterly ToS re-check schedule starts **2026-Q3 (by 2026-09-30)**; perma.cc snapshots archived under `docs/ip_policy/tos_snapshots/{YYYY-QQ}/`. | Accept. |
| **JP-12** | SnapGene cross-check release-gate threshold = **90%** (research posture); commercial fork must tighten to ≥ 95% per § 10.2. | Accept. |
| **JP-13** | All 19 remaining open questions (Architect Q2–Q10 + IPQ-2..IPQ-10) resolved as listed in § 3. | Accept. |
| **JP-14** | Step 8 / 9 / 10 hand-off specifications complete; downstream owners can proceed without further joint planning. | Accept. |

---

> **Disclaimer:** This joint development plan is provided for development and operational planning purposes. The fork-readiness memorandum content in § 10 is a planning-level scope (not legal advice); the binding commercial-fork checklist must be reviewed by AU and US counsel before any commercial release. All scientific curation tasks (Opus tier, § 6.1) require primary-literature citation verification before commit; vendor manuals (B2 grade) are acceptable only where primary literature is silent. Wet-lab execution is not in scope for this amendment.
