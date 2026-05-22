# ML Training Corpus

**Subsystem:** `docs/ml_corpus/` — curated ML training corpus for plasmid backbones and modular design elements.
**Status:** Scaffolded at T-1401 (v0.2 Enrichment Amendment, 2026-05-23). Schema lands at T-1402; records seeded at T-1404 + T-1405; partitioning + manifest at T-1407.
**Owner:** `/scientific-advisor` (curation) + `/dev-orchestrator` (release-gate, license aggregate).

## What this folder is — and what it is not

This folder is **training data, not runtime configuration.** It is read by tooling for ML model training and analytics only. The runtime engine (`src/*`) **must not** import from this folder; the `import-linter` contract `ml-corpus-is-not-runtime` enforces this boundary (see `.importlinter`).

The corpus has its own schema (`schemas/corpus_record.schema.json`, landed at T-1402), its own CI gates (`ml-corpus-license-check`, `snapgene-pipeline-scan`, `corpus-annotation-provenance-check`), its own manifest (`corpus_manifest.yaml`), and its own release-time gate (`tools/release/corpus_release_gate.py`). It is governed independently of the runtime catalogue.

## Working principle (mirror of `cev-workflow-discipline`)

Every change to this corpus follows the project's standing 10-step cadence:

1. `/scientific-advisor` initial report → 2. user accepts → 3. `/architect` analysis → 4. `/ip-auditor` analysis → 5. user accepts both → 6. `REQUIREMENTS.md` update → 7. three-skill joint plan → 8. `ARCHITECTURE.md` update → 9. `CODING_AGENDA.md` task cards → 10. `TASK_BOARD.md` + implementation.

See `feedback/cev-workflow-discipline` in user memory for the canonical phrasing.

## Folder layout

```
docs/ml_corpus/
├── README.md                          # this file
├── corpus_manifest.yaml               # license_aggregate + cross_check_coverage + partition counts
├── exclusions.yaml                    # records considered + rejected, with reason
├── crosscheck_log.yaml                # append-only SnapGene cross-check log (process artefact)
├── schemas/                           # corpus_record.schema.json lands here at T-1402
└── records/
    ├── backbones/{ecoli,kphaffii,scerevisiae,mammalian}/
    ├── elements/{promoters,terminators,rbs_kozak,polyA,ires_2a,mcs,tags,
    │             fluorescent_proteins,selection_cassettes,insulators,introns_wpre}/
    └── cc-by-sa/                       # CC-BY-SA-routed records (excluded from partition: sa_free)
```

## Partition strategy (per IPQ-1 resolution, NORMATIVE)

- **`partition: sa_free` is the DEFAULT training partition.** Records under `cc-by-sa/` are excluded.
- **`partition: full`** exists for research-only training runs that explicitly accept share-alike. It is opt-in.
- Every model release ships with a manifest declaring which partition trained it.
- For any commercial-fork attempt, see `ARCHITECTURE.md` § 9.6 Fork-Readiness Memorandum (NORMATIVE) — only `partition: sa_free`-trained checkpoints survive the fork.

## SnapGene posture (NORMATIVE per BR-16)

This project uses SnapGene as an **index-only manual QC reference**. Sequences ingested from cleaner-licensed sources (NCBI / EBI / iGEM / vendor primary publications) are double-cross-checked against SnapGene reference records **by a human in a browser**. No pipeline this project runs may access `snapgene.com` via any non-browser tool — enforced by `tools/ci/snapgene_pipeline_scan.py` (T-1406, enforced from day one).

SnapGene® is a registered trademark of Dotmatics. This project is not affiliated with, endorsed by, sponsored by, or in any way officially connected to Dotmatics or SnapGene. Full nominative-use disclaimer will land at `LICENSES/THIRD_PARTY_NOTICES.md` (T-1410).

## Cross-references

- ARCHITECTURE.md § 9 — V0.2 Enrichment Amendment + Fork-Readiness Memorandum
- REQUIREMENTS.md § 11 — FR-ML-01..15, BR-15..17, NFR-COMPLY-06
- CODING_AGENDA.md § 2.14 — Phase 14 task cards (T-1401 .. T-1411)
- `docs/handover/2026-05-23_host_marker_ml_corpus_*.md` — cadence handover docs
