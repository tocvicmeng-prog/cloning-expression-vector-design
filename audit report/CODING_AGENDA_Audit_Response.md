# Response to Codex's Audit of CODING_AGENDA.md

**Document type:** Audit-response and adjudication record.
**Date:** 2026-05-14.
**Audit reviewed:** `audit report/CODING_AGENDA_Audit_Report.md` (Codex; senior software-architect, senior implementation-engineer, QC reviewer, scientific-software reviewer stance).
**Respondents:** `/architect`, `/scientific-advisor`, `/dev-orchestrator`.
**Companion deliverable:** `CODING_AGENDA.md` v1.1 (binding; patched per accepted findings); `TASK_BOARD.md` regenerated to reflect new tasks and CI-gate lifecycle states.
**Result tally:** **21 / 21 findings accepted.** No defense raised. All concerns were either pure-implementation defects, missing-task gaps, or honest weak spots that the three-role collaboration agrees should be repaired before Phase 2 implementation begins in earnest.

---

## 0. Method

Each finding processed through the three-role protocol, two operating rules:

1. **Defend only when defensible.** Every Codex finding was cross-checked against `ARCHITECTURE.md` v1.5 and `REQUIREMENTS.md`; where the audit's claim resolves correctly against the binding documents, no defense is mounted.
2. **Every accepted finding produces a concrete v1.1 change.** Each finding lists the specific section, task ID, or CI gate the v1.1 patch touches.

Per-finding format: **Finding restated → three-role assessment → verdict → v1.1 change action (file:section:test).**

---

## 1. Blocking findings (B-01 … B-05) — all accepted

### B-01. Non-operational types incorrectly placed in `sop_protected`

**Finding restated.** v1.0 T-306 places `design_realisation_plan.py`, `control_set.py`, `risk_advisory.py` under `src/domain/types/sop_protected/`, but v1.0 T-802 forbids `engine.design_plan` from importing that namespace — so the engine cannot import the type it is required to emit.

**`/architect`:** Conceded. Type placement is a pure-engineering bug. Operational types (`ProtocolStep`, `ProtocolDAG`, `SopLinkedProtocol`, hazard / quantity / temperature / duration / deviation) belong in `sop_protected`; everything renderable before screening — `DesignRealisationPlan`, `ControlSet`, `RiskAdvisoryReport` — does not.

**`/scientific-advisor`:** Conceded. `RiskAdvisoryReport` is generated *before* screening; it is by definition non-operational. Calling it "sop_protected" mis-classifies its safety stance.

**`/dev-orchestrator`:** Conceded. `import-linter` would either fail correct code or force developers to weaken the gate. Either way is unsafe.

**Verdict.** **Accept. No defense.**

**v1.1 change action.** Re-shape the type packages in T-306 and downstream:

- `src/domain/types/design_plan/` — `DesignRealisationPlan`, verification artefacts, reviewer packet summaries.
- `src/domain/types/controls/` — `ControlSet`, `ControlDesign`.
- `src/domain/types/risk_advisory/` — `RiskAdvisory`, `RiskAdvisoryReport`, `RiskAdvisoryAcknowledgement`, `AdvisoryAcknowledgementDecision`.
- `src/domain/types/sop_protected/` — only `ProtocolStep`, `ProtocolDAG`, `SopLinkedProtocol`, hazard / quantity / temperature / duration / deviation types.
- T-306 renamed "Operational types namespace + design-plan / controls / advisory namespaces"; deliverable list, SOP, and acceptance updated.
- T-802 import contract amended: `engine.design_plan` imports `domain.types.design_plan`, `domain.types.controls`, `domain.types.risk_advisory` — and is *forbidden* from importing `domain.types.sop_protected`.
- T-801 / T-804 / T-806 import contracts updated.
- `import-linter` config rule added: `domain.types.sop_protected` may be imported only from `engine.sop_protocol`, `domain.types.sop_protected` itself, and the `sop_protected` test suite.
- New static test fixture proves `DesignRealisationPlan` cannot reference `ProtocolStep` at type level.

### B-02. Build queue omits architecture-critical modules

**Finding restated.** `engine.session`, `engine.compatibility`, `engine.vlp_policy`, `adapter.persistence` (Sqlite project store / EventLog / AuditLog / authorisation store), `app.plugin_governance` are referenced in wiring but have no implementation tasks.

**`/architect`:** Conceded. Wiring without implementation is an audit-trail bug. The composition root in v1.0 § 3.2 uses these names assuming they exist.

**`/scientific-advisor`:** Conceded. Without `engine.compatibility` the host-role validation degenerates into a scatter of predicates; without `engine.vlp_policy` MS2/VLP work has manifest entries but no policy engine.

**`/dev-orchestrator`:** Conceded — and this is exactly why a `module-coverage` CI gate is necessary: every entry in `ARCHITECTURE.md` § 4.2 must map to at least one task.

**Verdict.** **Accept. No defense.**

**v1.1 change action.** Add explicit task cards:

- **T-309** `engine.session` — design-session state machine, event sourcing, snapshotting, session transitions, four-gate routing. Phase 3. Opus. ≤ 60 k.
- **T-310** `adapter.persistence` — `SqliteProjectStore`, `JsonlEventLog` (×3), `SqliteAuditLog`, `SqliteAuthorisationStore`, with schemas + migrations + append-only writers + audit-log tamper detection + read-only enforcement tests + crash-recovery tests + snapshot schema keyed by `DerivationEnvironment.hash()`. Phase 3. Opus. ≤ 70 k.
- **T-504** `engine.compatibility` — role-keyed `HostContext` iteration + `HostCompatibilityConstraints` evaluation + threshold-profile resolution. Phase 5. Opus. ≤ 50 k.
- **T-807** `engine.vlp_policy` — MS2 / VLP / phage-derived design policy module consuming `MS.yaml`. Phase 8a. Opus. ≤ 50 k.
- **T-606** `app.design_service` + **T-607** `app.decision_tree` — application-layer entry points for session lifecycle and decision-tree flow. Phase 6/7 boundary. Sonnet/Opus. ≤ 40 k each.
- **T-808** `app.plugin_governance` — plugin manifest signature verification + sandbox enforcement + `PluginManifestApproved` governance events. Phase 8a. Sonnet. ≤ 40 k.
- New CI gate: **`module-coverage-check`** — every module in `ARCHITECTURE.md` § 4.2 maps to ≥ 1 task with files + tests + acceptance. Wired in T-204.

### B-03. Phase order conflicts with screening-before-SOP architecture

**Finding restated.** v1.0 Phase 8 schedules `engine.sop_protocol`, `app.authorisation_decision` *before* Phase 10 implements the screening adapters and `app.screening_orchestrator`. Per v1.4 B2, SOP rendering must come strictly after screening completes.

**`/architect`:** Conceded — and this is exactly the trap v1.4 B2 was designed to prevent.

**`/scientific-advisor`:** Conceded. A placeholder screening contract in Phase 8 would mark safety behaviour "green" before the real `ScreeningCompleted` contract exists.

**`/dev-orchestrator`:** Conceded. We choose **Codex's option 2**: split Phase 8 into 8a and 8b; 8b runs *after* Phase 10.

**Verdict.** **Accept. No defense.**

**v1.1 change action.** Split Phase 8:

- **Phase 8a — Design-plan + controls + advisory data + advisory acknowledgement (non-operational; pre-screening).** Contains: T-801 (`engine.risk_classification`), T-802 (`engine.design_plan`), T-804 (`engine.controls`), T-806a (`app.advisory_acknowledgement` — advisory presentation, acknowledgement record types, governance events emit), T-807 (`engine.vlp_policy`), T-808 (`app.plugin_governance`).
- **Phase 8b — SOP rendering + authorisation decision (post-screening).** Runs *after* Phase 10 completes. Contains: T-803 (`engine.sop_protocol`), T-805 (`app.protocol_orchestrator`), T-806b (`app.authorisation_decision` — the *gate* that consumes a real `ScreeningCompleted` event + acknowledgement chain).
- Phase 8a → Phase 9 → Phase 10 → Phase 8b → Phase 11 → ... ROADMAP regenerated accordingly.
- Acceptance: no Phase 8b task may mark SOP-gating green until a test fixture supplies a real `ScreeningCompleted` event with policy-derived trust.

### B-04. CI gate skeletons that pass with TODOs create false safety

**Finding restated.** v1.0 T-204 says CI gate skeletons return exit 0 with a TODO. The architecture treats these gates as release-blocking safety controls; a TODO-passing gate creates dashboard green without enforcement.

**`/architect`:** Conceded. Lifecycle states are needed.

**`/scientific-advisor`:** Conceded. Especially dangerous for `no-self-authorisation-check`, `no-passive-advisory-bypass-check`, `sop-after-gates-check`, `plugin-manifest-signature`, `llm-output-policy-check`.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.1 change action.** Introduce gate lifecycle states:

- `not_implemented` — stub absent; gate excluded from merge-blocking. CI workflow does not run it.
- `informational` — stub runs and reports; results visible in CI logs but `exit 1` on TODO; *not* merge-blocking; permitted only when the gate's owning task is `planned` or `in-progress`.
- `enforced` — real predicate, real fixtures, merge-blocking.

T-204 deliverable updated:

- Each stub returns exit 1 if a TODO marker remains in its own file *and* the run mode is `--enforce`. Under `--informational` (default in early phases), it logs and exits 0.
- Each gate lists, in `tools/ci_gates/<gate>.py` header, its current lifecycle state + owning task ID.
- CI workflow runs gates under `--informational` mode initially; transitions to `--enforce` per gate when the owning task moves to `verified`.
- `TASK_BOARD.md` distinguishes `planned` / `informational` / `enforced` for each gate (already present in v1.0 § 7 status table; now formally bound to gate lifecycle).
- **New meta-test** (`tools/ci_gates/_meta/check_no_todo_in_enforced.py`): fails if any CI job listed as `enforced` in TASK_BOARD.md contains a TODO marker.

### B-05. Rule-fixture ownership not in T-405 deliverables

**Finding restated.** v1.0 § 7.1 (Round 1 rebuttal) says fixtures are populated in the *same* task as the rule manifest entry — but v1.0 T-405 deliverable list only requires the rule YAML + stub predicate.

**`/architect`:** Conceded. The agenda contradicts itself between § 7 and § 2.4.5.

**`/scientific-advisor`:** Conceded. Fixtures at rule-curation time are essential for scientific review.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.1 change action.** T-405 deliverables updated:

- For each rule in the manifest, add: `tests/fixtures/rules/<category>/triggering/<rule_id>.json` and `tests/fixtures/rules/<category>/passing/<rule_id>.json`.
- Add per-category `tests/fixtures/rules/<category>/README.md` documenting biological rationale and expected predicate outcome.
- Rule manifest schema extended with `test_fixtures: {triggering: <path>, passing: <path>}`; these paths must resolve at startup (enforced by `T-401` loader's manifest-validation pass).
- Phase 4 exit criterion: every manifest rule has triggering + passing fixture; no rule lacks fixtures.
- Phase 5 / 6 acceptance flips from `informational` to `enforced` on `rule-validation coverage` per rule when the real predicate replaces the stub.
- Rule manifest schema additionally extended with `implementation_status: stub | real` (cf. M-05) so phase exits can detect lingering stubs.

---

## 2. High-severity findings (H-01 … H-08) — all accepted

| ID | Finding | Verdict | v1.1 change action |
|---|---|---|---|
| **H-01** | T-203 doesn't explicitly stub the v1.4/v1.5 split ports (AuthorisationReadPort / AuthorisationAdminWritePort / AuthorisationBootstrapPort / AuditLog / RiskAdvisoryCatalogue / InstitutionalPolicyCatalogue / ExportProfileCatalogue / PluginManifestRegistry / Lifecycle / RefreshingAdapter). | Accept. | T-203c (ports sub-task) updated to list every v1.4/v1.5 port explicitly with architecture-line references. New sub-test `tests/ports/test_port_inventory.py` asserts every port is present and importable. |
| **H-02** | `.dna` read-only input wrongly scheduled in T-902 (file-watch) instead of T-308 (core I/O). | Accept. | Add **T-308e** `adapter.io.SnapGeneDnaReader` (read-only) in Phase 3 with graceful-fallback error when proprietary parsing is unavailable. T-902 *depends on* T-308e, does not own it. |
| **H-03** | `engine.compatibility` absence weakens host-scientific validation. | Accept (already covered by B-02 fix). | T-504 added; fixtures cover plant transient (3 hosts), lentivirus (3 hosts), AAV (3 hosts), VLP (4 hosts), cell-free (no propagation host). |
| **H-04** | `engine.vlp_policy` required by v1.4 M9 but missing. | Accept (already covered by B-02 fix). | T-807 added with explicit constraint set: packaging signal, capsid expression, helper-function separation, cargo-size limits, replication/infectivity boundaries, assembly + assay controls, MS2-vs-phage-VLP-vs-AAV-vs-lenti distinction. |
| **H-05** | Persistence / audit stores under-specified for implementation. | Accept (already covered by B-02 fix). | T-310 expanded SOP: SQLite schemas + migrations (alembic-style); fsync + atomic-append; audit-log tamper detection via HMAC chain; read-only enforcement at OS-mode level for User-role processes; snapshot schema keyed by `DerivationEnvironment.hash()`; crash-recovery integration test. |
| **H-06** | Canonical JSON underspecified — "sort by key bytes" is insufficient (NaN/Infinity, Decimal vs float, timezones, Unicode normalisation, enum representation, non-string dict keys). | Accept. | T-307 SOP rewritten to specify **RFC 8785-style JSON Canonicalization Scheme** with project-specific rules: NaN / +Inf / -Inf rejected at serialise; numbers serialised per RFC 8785 §3.2.2.3 (no Decimal — use string-encoded Decimal in a wrapper); timestamps as ISO-8601 UTC with microsecond precision; enums as their `.value`; Unicode NFC normalisation; non-string dict keys forbidden (raise at serialise). Cross-platform golden vector tests committed in `tests/fixtures/canonicalisation/`. |
| **H-07** | Windows / OneDrive / SQLite locking / file-watch debounce / non-ASCII paths / atomic writes / Windows ProcessPoolExecutor spawn not planned. | Accept. | New **T-205** "Platform-readiness baseline" inserted in Phase 2 before T-203. CI matrix runs on `ubuntu-latest` *and* `windows-latest`. Test fixtures use a temp path containing a space and a non-ASCII character (`tests/tmp_with space + 文档/`). SQLite WAL + locking tests (concurrent reader/writer; sync conflict simulation). File-watch debounce test. Atomic-write test (write to `.tmp` + rename). Recommendation in README: project DBs should not live inside an actively-syncing OneDrive folder; opt-in `--db-outside-sync` configuration provided in T-201. |
| **H-08** | Adapter-heavy dependencies (ViennaRNA / SpliceAI / Primer3 / FastAPI / pySBOL3 / SnapGene) wrongly bundled in core bootstrap. | Accept. | T-201 SOP updated to use **dependency groups (`uv` extras)**: `core` (domain + engine + YAML + pydantic at boundary), `io` (biopython + pysbol3 + snapgene-reader), `biology-vienna` (viennarna), `biology-spliceai` (tensorflow + spliceai *or* HTTP-client-only), `biology-signalp`, `primer` (primer3-py), `api` (fastapi + uvicorn), `cli` (typer), `llm-local` / `llm-openai` / `llm-anthropic`, `ui` (separate package). T-201 bootstrap installs only `core` + `dev`. Adapter tasks add their own extras. CI matrix has a "minimal-core" job that verifies `core` + `dev` alone is sufficient to build the domain + engine layers. |

---

## 3. Medium-severity findings (M-01 … M-08) — all accepted

| ID | Finding | Verdict | v1.1 change action |
|---|---|---|---|
| **M-01** | `ProcessPoolExecutor` needs Windows-spawn semantics, stable result ordering, deterministic exception aggregation, picklable functions. | Accept. | T-502 SOP extended: workers seeded via `multiprocessing.set_start_method('spawn')`; results aggregated in `submit-order` (not arrival order); exceptions wrapped in typed `RuleEvaluationError` with rule_id; benchmark task `T-502-bench` compares sequential / thread / process modes and records median latency in `Manifest.measured_typical_latency_ms`. Functions are top-level (no closures) for pickle safety; `__main__` guard enforced via runtime check. |
| **M-02** | SLIC (REQUIREMENTS § 1.2) not explicitly mapped to a strategy. | Accept. | T-703 strategy hierarchy updated: explicit `SLICStrategy` added as a sibling of `GibsonLikeStrategy` (SLIC's T4-polymerase-only chew-back is mechanically different from Gibson's three-enzyme cocktail). New sub-task T-703e covers SLIC. Test fixture covers a 3-fragment SLIC assembly. |
| **M-03** | Threshold-profile calibration governance is thin. | Accept. | Each `threshold_profile` in `catalogues/threshold_profiles/*.yaml` carries: `source_citation` (graded), `intended_host_or_role_scope`, `default_value` + `allowed_override_range`, `triggering` + `passing` fixtures at boundary values, `reviewed_by` + `last_reviewed`. The `source-grade-citation-check` CI gate extended to validate threshold profiles. |
| **M-04** | PDF / Markdown rendering under-tested. | Accept. | T-802 / T-803 / T-903 add renderer tests: structural output check (sections present, headings in order), absence-of-operational-fields check on `DesignRealisationPlan` (no `ProtocolStep` reachable in rendered output), redaction-by-`ExportProfile` check, reproducible-PDF test (byte-identical PDF inside the container determinism harness given the same `DerivationEnvironment`). |
| **M-05** | Rule stubs returning `INFO` need an `implementation_status` flag. | Accept (folds into B-05 fix). | Manifest schema adds `implementation_status: stub | real`. Phase 5 / 6 exit fails if any required rule still has `stub`. |
| **M-06** | File-header traceability may drift; consider generating from manifests instead of hand-maintaining in every file. | Accept (partial). | Headers kept *lightweight* — only `module_id` / `file` / `task_id` are mandatory inline. The full traceability chain (architecture-refs, requirements-refs, citations, purity, migration-notes) is *generated* from `tasks/task_brief/T-<id>.md` + module manifest into `docs/traceability_index.md` by a script invoked in CI; the `audit-traceability-check` gate compares the generated index against the in-file lightweight headers and flags any drift. |
| **M-07** | Calibration tests need lifecycle governance: drift magnitude that blocks release; baseline refresh approval; baseline capture in `DerivationEnvironment.external_database_versions`. | Accept. | T-601 SOP extended with an explicit `CalibrationDriftPolicy` per adapter: tolerance (`relative_error ≤ 0.05` default; per-adapter override allowed), drift events emitted nightly, refresh requires `/scientific-advisor` sign-off recorded as a `CalibrationBaselineRefreshed` governance event, and the refreshed baseline's hash recorded in `DerivationEnvironment.external_database_versions`. |
| **M-08** | `app.design_service` and `app.decision_tree` thin / missing. | Accept (already covered by B-02 fix). | T-606 (`app.design_service`) and T-607 (`app.decision_tree`) added; ordered between Phase 6 and Phase 7 so interface layer (Phase 11) has them ready. |

---

## 4. Tally and final verdict

| Severity | Count | Accepted | Defended | Notes |
|---|---|---|---|---|
| Blocking (B-01 … B-05) | 5 | 5 | 0 | All execution-time defects acknowledged. |
| High (H-01 … H-08) | 8 | 8 | 0 | All architectural / type-placement / port / environment defects acknowledged. |
| Medium (M-01 … M-08) | 8 | 8 | 0 | All quality / governance / coverage gaps acknowledged. |
| **Total** | **21** | **21** | **0** | Net result: regenerate CODING_AGENDA.md to v1.1 before T-201 begins. |

---

## 5. Implementation impact map

The v1.1 patch touches `CODING_AGENDA.md` § 0 (version), § 1.6 (file header → lightweight + generated index), § 2.2 (Phase 2: add T-205; rewrite T-201 with dependency groups; rewrite T-204 with gate lifecycle), § 2.3 (Phase 3: rewrite T-306 with corrected type placement; rewrite T-307 with RFC 8785 canonicalisation; add T-308e for SnapGene `.dna`; add T-309 `engine.session`; add T-310 `adapter.persistence`), § 2.4 (Phase 4: rewrite T-405 with fixture deliverables + `implementation_status`), § 2.5 (Phase 5: add T-504 `engine.compatibility`), § 2.6 (Phase 6/7 boundary: add T-606 `app.design_service`, T-607 `app.decision_tree`; extend T-601 with calibration-drift policy), § 2.7 (Phase 7: add T-703e SLIC sub-task; extend T-502 with ProcessPoolExecutor semantics — moved to Phase 5 task), § 2.8 (Phase 8 → 8a + 8b split; add T-807 `engine.vlp_policy`, T-808 `app.plugin_governance`; reorder T-803 + T-805 + T-806b to Phase 8b), § 3 (wiring updated for new modules), § 4 (test strategy: add M-04 renderer tests, M-07 calibration drift policy), § 4 (CI gate matrix: add `module-coverage-check` gate), § 7 (add Round 5 — Codex audit summary), § 8 Appendix B (traceability table extended for new tasks).

Plus `TASK_BOARD.md` regenerated with: gate lifecycle states column; new tasks T-205, T-308e, T-309, T-310, T-504, T-606, T-607, T-703e, T-807, T-808; Phase 8 → 8a + 8b split reflected in § 1 Global progress.

---

## 6. Sign-off

**`/architect` (v1.1):** "Every architectural defect the audit found is correct. The type-placement bug (B-01), missing modules (B-02), and phase-order safety bug (B-03) are the most serious — they would have produced a scaffold that looks v1.5-aligned but contains structural inconsistencies that would force expensive rewrites in Phase 3 – Phase 8. v1.1 closes all three. The `domain.ports/` separation now extends cleanly into v1.4/v1.5 split-port territory (H-01). Approved."

**`/scientific-advisor` (v1.1):** "The scientific defects matter. Rule fixtures at curation time (B-05) is non-negotiable for scientific review; SLIC mapping (M-02) and `engine.vlp_policy` (H-04) close real scope gaps; calibration-drift governance (M-07) makes biology-adapter drift detectable instead of silent. Approved."

**`/dev-orchestrator` (v1.1):** "The operational defects are clean wins. CI-gate lifecycle states (B-04) eliminate the 'TODO-green' failure mode. Dependency groups (H-08) prevent install fragility cascading. Windows / OneDrive platform tests (H-07) match the actual environment instead of an idealised one. `module-coverage-check` (B-02 verification) prevents future drift between architecture and agenda. Approved."

The audit served its purpose. v1.1 is the new authoritative coding agenda; this response is the audit trail justifying every change.

---

*End of CODING_AGENDA_Audit_Response.md.*
