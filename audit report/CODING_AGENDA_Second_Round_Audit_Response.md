# Second-Round CODING_AGENDA.md Audit — Three-Role Response

**Audit input:** `audit report/CODING_AGENDA_Second_Round_Audit_Report.md`.
**Subject:** `CODING_AGENDA.md` v1.1.
**Result:** **29 / 29 findings accepted (9 blocking + 11 high + 9 moderate); 0 defended.**
**Output:** `CODING_AGENDA.md` v1.2; `ROADMAP.md` regenerated; `TASK_BOARD.md` regenerated; memory pointer updated.
**Adjudicating roles:** `/architect`, `/scientific-advisor`, `/dev-orchestrator`.
**Date:** 2026-05-14.

## Executive summary

The auditor's overall verdict is sound: v1.1 fixed the task-card layer but did not propagate every fix through the **roadmap, dependency DAG, composition root, event-stream wiring, persistence wiring, CI lifecycle, dashboard, traceability appendices, and context-budget tables.** The most consequential residual defect was that `ROADMAP.md` still encoded a single Phase 8 with SOP/authorisation *before* Phase 10 screening, while `CODING_AGENDA.md` v1.1 had already moved SOP/authorisation to Phase 8b (post-Phase-10). The two source-of-truth files contradicted each other.

The three roles convened, walked each finding against `ARCHITECTURE.md` v1.5, `REQUIREMENTS.md`, the v1.1 patch set, and the existing wiring, and accepted every finding without defence. The required corrections all converge on a single synchronization pass: bring `ROADMAP.md`, the agenda's § 3 (wiring), the CI lifecycle tables, `TASK_BOARD.md`, and the appendices into agreement with the v1.1 task-card semantics, and close the **five** remaining structural gaps (admin handler ownership, design-plan application orchestrator, audit-key management, event-stream ownership, export ordering).

| Severity | Total | Accepted | Defended |
|---:|---:|---:|---:|
| Blocking | 9 | 9 | 0 |
| High | 11 | 11 | 0 |
| Moderate | 9 | 9 | 0 |

## Adjudication method

For each finding the three roles asked four questions in sequence:

1. **Is the finding factually correct against v1.1?** (Does the cited line actually say what the auditor claims it says?)
2. **Is the impact correct against ARCHITECTURE.md v1.5 and REQUIREMENTS.md?** (Does the defect actually break a binding contract?)
3. **Can it be defended without breaking the agenda?** (Is there an existing escape hatch — e.g., a documented exception, an out-of-scope clarification, a different ownership model that v1.1 implicitly relies on?)
4. **What is the smallest correction that closes the defect?** (Surgical patch vs structural change.)

Where the answer to 1 and 2 was yes and to 3 was no, the finding was accepted.

## Blocking findings

### B2-01 — Roadmap not regenerated. **Accepted.**

**Adjudication.** Verified at `ROADMAP.md:274-349`. The roadmap still encodes a single Phase 8 containing design plan + SOP protocol + admin handler + authorisation + advisory workflow, followed by Phase 9 export and Phase 10 screening. This contradicts `CODING_AGENDA.md` v1.1 § 2.8 (Phase 8 split into 8a/8b with phase order 8a → 9 → 10 → 8b → 11). The auditor's impact statement is correct: developers following `ROADMAP.md` will implement SOP/auth before screening; developers following `CODING_AGENDA.md` will not. The architecture's screening-before-SOP invariant (`ARCHITECTURE.md` v1.4 B2) is violated by `ROADMAP.md` as written.

**v1.2 correction.**

- **Regenerate `ROADMAP.md`** so its phase ordering matches the agenda: split Phase 8 into Phase 8a (pre-screening) and Phase 8b (post-Phase-10 + post-Phase-9a); split Phase 9 into Phase 9a (sequence I/O + SnapGene file-watch, pre-screening) and Phase 9b (final export orchestrator, post-Phase-8b). Final phase order: **0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8a → 9a → 10 → 8b → 9b → 11 → 12 → 13.**
- Add a Roadmap header note stating that `CODING_AGENDA.md` v1.2 is the canonical phasing reference; `ROADMAP.md` is regenerated from it.

### B2-02 — Export scheduled before screening, authorisation, SOP rendering. **Accepted.**

**Adjudication.** Verified against `ARCHITECTURE.md` v1.5 § 4.4 (state machine) and `REQUIREMENTS.md` FR-PROTO-SOP-* (SOP emits only after acceptable screening + authorisation; bundle includes screening verdict). Phase 9 in v1.1 ran before Phase 10 and Phase 8b; T-903's acceptance demands a complete bundle (including `SopLinkedProtocol`, `ScreeningCompleted`, `OperationalProtocolAuthorised`, `DerivationEnvironment` + advisory approval trace) which simply does not exist at Phase 9 time. T-903 as written in v1.1 could only ship an incomplete or fake bundle.

**v1.2 correction.**

- **Split Phase 9 into Phase 9a (pre-screening) and Phase 9b (post-Phase-8b).**
- **Phase 9a** contains: T-901 (EMBL + GFF3 adapters) and T-902 (`SnapGeneFileWatcher`). These are I/O channels and do not produce a final operational export.
- **Phase 9b** contains: T-903 (`app.export_orchestrator` + redaction + final bundle export). T-903's acceptance can now reference real `ScreeningCompleted`, `OperationalProtocolAuthorised`, and `SopRendered` events.
- For the "early non-operational export" use case (sharing a draft design plan with a reviewer pre-screening), the agenda will produce a `DraftDesignBundle` — explicitly *not* a vendor-export bundle, and structurally incapable of containing `SopLinkedProtocol` or `BlockVendorSubmission` clearance. T-805a (new — see B2-09) owns this bundle.

### B2-03 — Dependency DAG + composition root stale. **Accepted.**

**Adjudication.** The DAG in v1.1 § 3.1 (lines 896-967) still presents the old single Phase 8 with `engine.sop_protocol` + `app.protocol_orchestrator` + `app.authorisation_decision` before Phase 10 screening. It says "`engine.assembly (8 strategies)`" even though v1.1 added SLIC making it nine strategy families. The composition root (lines 986-1077) omits or fails to wire `engine.session`, `engine.compatibility`, `engine.vlp_policy`, `app.design_service`, `app.decision_tree`, `app.plugin_governance`, lifecycle hooks, and a separate admin-write port. Confirmed against `ARCHITECTURE.md` v1.5 § 4.2-4.5 and against v1.1's own task catalogue.

**v1.2 correction.**

- **Rewrite § 3.1 dependency DAG end-to-end** to reflect 8a → 9a → 10 → 8b → 9b → 11 → 12 → 13. Show `engine.assembly (9 strategies)` and every new v1.1/v1.2 module in its correct phase position. Add lifecycle hooks edge.
- **Rewrite § 3.2 composition root** to construct: `engine.session`, `engine.compatibility`, `engine.vlp_policy`, `app.design_service`, `app.decision_tree`, `app.plugin_governance`, `app.design_plan_orchestrator` (new — B2-09), `app.sop_protocol_orchestrator` (renamed half of T-805), `app.admin_action_handler` (now with a proper `AuthorisationAdminWritePort` + `AuthorisationBootstrapPort` parameter, B2-04). Add explicit `Lifecycle.start()` / `Lifecycle.stop()` calls after composition and before shutdown.
- **Rewrite § 3.3 event-stream wiring** (cross-resolution with B2-05): place `ScreeningCompleted`, `OperationalProtocolAuthorised`, `SopRendered` in the design stream; place reviewer/admin/advisory/plugin governance events in the governance stream.
- **Rewrite § 3.4 persistence wiring**: explicit `authorisation.sqlite` writer = `app.admin_action_handler` running in a separate admin-service process; readers = engine + User-role processes in `mode=ro`.
- **Rewrite § 3.5 CI table** to use a lifecycle-state column (cross-resolution with B2-07).

### B2-04 — `app.admin_action_handler` has no concrete task card. **Accepted.**

**Adjudication.** Confirmed against `ARCHITECTURE.md` v1.5 § 4.2.2 and `CODING_AGENDA.md` v1.1 § 2.3.10 (T-310 references the handler at line 530) and the composition root (line 1058). The handler is the sole write path to `AuthorisationStore`, `SopTemplateLibrary`, and the authorisation-related portion of the audit log. v1.1 never gave it a task card. Worse, the composition root passes `authorisation_store: AuthorisationReadPort` into `AdminActionHandler`, which contradicts its purpose.

**v1.2 correction.**

- **Add T-311 `app.admin_action_handler` (foundational)** in Phase 3, immediately after T-310. Deliverables: `src/app/admin_action_handler.py` (sole admin-write entry point); `src/domain/ports/authorisation.py` with three protocols (`AuthorisationReadPort`, `AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`); `src/adapter/persistence/sqlite_authorisation_store.py` (write side, lifted out of T-310's read-side); CLI subcommands `mint-profile`, `modify-profile`, `revoke-profile`, `list-profiles`, `view-auth-audit-log` exposed via the foundational admin-service runner (full CLI/API surface lands in Phase 11); adversarial tests denying `UserPrincipal` and `ReviewerPrincipal` writes.
- Composition root in § 3.2 wires `admin_action_handler: AdminActionHandler = AdminActionHandler(authorisation_admin_write_port, audit_log, governance_event_log, audit_key_provider)`. The admin-service process is a separate executable boundary; the engine process holds only `authorisation_read_port`.
- Phase 8a's authorisation-related surface extends T-311 with the institutional SOP-template admin-write operations (handled inside T-803 in Phase 8b once SOP templates exist).

### B2-05 — Event-stream wiring conflicts with replay contract. **Accepted.**

**Adjudication.** Verified against `ARCHITECTURE.md` v1.5 lines 2148-2178. The architecture places `ScreeningCompleted`, `OperationalProtocolAuthorised`, `SopRendered` in the **design** stream (lines 2148-2159). v1.1's § 3.3 wiring (line 1089) instead lists `app.screening_orchestrator` as a governance writer and omits screening from the design-stream writer column. T-806b at line 810 says it consumes a real `ScreeningCompleted` event for the gate decision, but the event table told implementers to write it to the wrong stream.

**v1.2 correction.**

Rewrite § 3.3 event-stream wiring:

| Stream | Writer | Reader |
|---|---|---|
| `events/design/<session>.jsonl` | `engine.session`, `app.design_service`, `app.assembly_orchestrator`, `app.validation_orchestrator`, `app.screening_orchestrator` (`ScreeningCompleted`), `app.authorisation_decision` (`OperationalProtocolAuthorised`), `app.sop_protocol_orchestrator` (`SopRendered`) | replay, UI, `app.export_orchestrator` |
| `events/governance/<institution>.jsonl` | `app.admin_action_handler`, `app.advisory_acknowledgement` (presentation/acknowledgement/decline/escalate), reviewer sign-off, `app.plugin_governance`, `app.screening_orchestrator` (reviewer/admin sign-off side only — *not* `ScreeningCompleted`) | audit, `audit-traceability-check` |
| `events/export/<institution>.jsonl` | `app.export_orchestrator` | release retrospectives |

Add a new contract test in T-309 (`engine.session` replay determinism): "replay-of-design-stream-plus-referenced-governance-records reproduces the same session state and gate verdicts" — fails if a screening verdict needed for a state transition lives in the wrong stream.

### B2-06 — T-203 missing port inventory. **Accepted.**

**Adjudication.** Verified at v1.1 § 2.2.3 lines 348-357. T-203 still says only "Mark every port (`Protocol` class) under `src/domain/ports/`". The v1.1 audit response promised T-203c would enumerate every split port (auth read/admin-write/bootstrap, lifecycle, refresh) and ship `tests/ports/test_port_inventory.py`. v1.1 never landed that text. The defect H-01 from the first audit is therefore not actually closed in the agenda body.

**v1.2 correction.**

Rewrite T-203c with an explicit numbered port inventory (covering every Protocol declared in `ARCHITECTURE.md` v1.5 § 4.5 plus the v1.2 additions — `AuthorisationReadPort`, `AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`, `AuditLog`, `AuditKeyProvider` (new in v1.2 per B2-08), `Lifecycle`, `RefreshableAdapter`, every catalogue port, every screening port, every plugin port). Add `tests/ports/test_port_inventory.py` that imports each named port and fails if any is missing or merged into a wrong interface. The test list is the canonical port catalogue.

### B2-07 — CI gate lifecycle contradicted by CI / dashboard tables. **Accepted.**

**Adjudication.** Verified at § 3.5 CI table (lines 1107-1134) and `TASK_BOARD.md:149-163`. T-204 introduces lifecycle states (`not_implemented` / `informational` / `enforced`) at line 363-368, but § 3.5 still has a single "Blocks merge: yes/no" column and `TASK_BOARD.md`'s gate table has only Gate / Status / Owning task with no lifecycle column. The "TODO-green" failure mode is reintroduced in a different form: either CI blocks merge on unimplemented gates (causing forced disables), or gates ad-hoc disabled.

**v1.2 correction.**

- Replace § 3.5's "Blocks merge" column with a four-state lifecycle column: `not_implemented` (absent from workflow) / `informational` (runs with `continue-on-error: true`) / `enforced` (merge-blocking) / `enforced-green` (merge-blocking and observed-passing at least once). Per-gate initial state declared by the gate's `lifecycle_state` header (per T-204 SOP step 1).
- Regenerate `TASK_BOARD.md` § 7 with the same four-state column, plus the owning task, the current workflow mode, and the last observed CI result.
- The `gate-lifecycle-check` meta-test (introduced in T-204) cross-validates the agenda's CI table, the workflow YAML, and `TASK_BOARD.md` § 7 — drift fails the gate.

### B2-08 — HMAC audit-log key has no lifecycle. **Accepted.**

**Adjudication.** Verified at T-310 line 529. v1.1 says "HMAC chain keyed by an institutional audit key" but never owns: key provisioning, storage, rotation, backup, access control, compromise response, or multi-user trust boundaries. The architecture demands signed `DecisionRecord` / `RoleSnapshot` and strict separation of duties (`ARCHITECTURE.md:21,84`) — but the agenda's HMAC key was effectively a *promise* with no concrete plan. Without a key-management plan, HMAC tamper-detection is theatrical: an attacker who can mutate the SQLite database can probably read the keying material co-located with it.

**v1.2 correction.**

Add **T-312 `audit-key management + AuditKeyProvider port`** in Phase 3 (after T-310 and T-311). Deliverables:

- `src/domain/ports/audit_key.py` — `AuditKeyProvider` Protocol with `current_key()`, `key_version()`, `verify_with_archived(key_version, message)`, `rotate(reason, principal: AdminPrincipal | DeveloperPrincipal)`.
- `src/adapter/security/audit_key/{file_keystore.py, os_keystore_windows.py, os_keystore_posix.py}` — three concrete adapters with adapter-selection driven by `config.audit_key_backend`. File-keystore is the developer/dev-loop default with the key stored under a separate filesystem ACL away from `audit.sqlite`. OS-keystore (Windows DPAPI / DPAPI-NG / POSIX Linux Keyring) is the production default.
- Separation between *event signatures* (per `DecisionRecord`, asymmetric, principal-keyed) and *log-integrity HMAC* (per-row chain, symmetric, institutional-keyed) is documented and tested.
- **Tests**: `key_absent` (engine refuses to start; `AuditLogTamperDetectionUnavailable` error); `wrong_key` (verification fails on every row); `rotated_key` (rows signed under previous key version verify with archived key); `tampered_row` (single-byte mutation detected); `offline_verification` (key escrow file + standalone CLI verifier produces correct verdicts without the live engine).
- **Operational procedure** in `docs/security/audit_key_runbook.md`: provisioning, rotation cadence, key-loss recovery, compromise response.

T-310's HMAC chain in v1.2 consumes the `AuditKeyProvider` port (no concrete keystore in T-310 itself — that's T-312's responsibility). T-310 lands first because the persistence layer is concrete; T-312 follows and replaces the test-only key stub.

### B2-09 — Phase 8a lacks an application service for the always-renderable design plan. **Accepted.**

**Adjudication.** Verified at v1.1 § 2.8.5 (T-805 MOVED to Phase 8b, line 752-754) and § 2.8b.2 (line 801). The v1.1 split correctly moved SOP-rendering and authorisation to Phase 8b, but in doing so it removed the application entry point for the safe half — the always-renderable design plan + controls + advisory presentation. T-903 expects bundled design artefacts before Phase 8b exists (line 827-830), and interfaces (Phase 11) need an entry point to compile and present a design plan before screening. v1.1's wiring leaves implementers tempted to call `engine.design_plan` directly, bypassing the application-event-logging layer.

**v1.2 correction.**

Split T-805 into two phase-keyed task cards:

- **T-805a `app.design_plan_orchestrator`** (Phase 8a, new). Owns dispatch to `engine.design_plan`, `engine.controls`, `engine.risk_classification`, advisory presentation surface (`app.advisory_acknowledgement`'s presentation half). Renders a `DraftDesignBundle` (no SOP, no operational clearance). Always available, runs before screening. Emits the design events for these renders.
- **T-805b `app.sop_protocol_orchestrator`** (Phase 8b, supersedes the v1.1 `app.protocol_orchestrator` in 8b). Owns dispatch to `engine.sop_protocol` only after `OperationalProtocolAuthorised` is observed. Renders a `SopProtocolBundle`. Cannot run before authorisation.

T-805 in the v1.1 placeholder positions is removed; cross-reference paragraphs replace the duplicate `####` headings (cross-resolution with H2-01).

## High findings

### H2-01 — Duplicate task headings for moved tasks. **Accepted.**

**v1.2 correction.** Remove the v1.1 placeholder `#### 2.8.3 T-803 — engine.sop_protocol (gated) — MOVED to Phase 8b per B-03` and `#### 2.8.5 T-805 — app.protocol_orchestrator (dispatch) — MOVED to Phase 8b per B-03`. Replace with prose cross-reference paragraphs (no `####` headings) so task parsers and module-coverage checks do not double-count. The Phase 8a heading explicitly enumerates the seven 8a tasks (T-801, T-802, T-804, T-805a, T-806a, T-807, T-808).

### H2-02 — Stale supporting metadata. **Accepted.**

**v1.2 correction.** Regenerate from the canonical task list:

- Phase 2 heading: "5 tasks" (T-201..T-205).
- Phase 3 heading: "12 tasks" (T-301..T-310 plus new T-311 and T-312).
- Phase 4 heading: "6 tasks" (unchanged).
- Phase 5 heading: "4 tasks" (T-501..T-504, unchanged).
- Phase 6 heading: "5 tasks" (T-601..T-603, T-606, T-607).
- Phase 7 heading: "5 tasks" with T-703 carrying five sub-tasks (a..e).
- Phase 8a heading: "7 tasks" (T-801, T-802, T-804, T-805a, T-806a, T-807, T-808).
- Phase 9a heading: "2 tasks" (T-901, T-902).
- Phase 8b heading: "3 tasks" (T-803, T-805b, T-806b).
- Phase 9b heading: "1 task" (T-903).
- Appendix B traceability rows: T-803, T-805b moved to Phase 8b; new rows for T-311, T-312, T-805a; T-805 renamed to T-805a/T-805b in the matrix.
- Appendix C context-budget rows: T-703 shows 5 sub-tasks; add T-311, T-312, T-805a, T-805b, T-903 (Phase 9b).

### H2-03 — `RiskAdvisoryAcknowledgement` duplicated. **Accepted.**

**v1.2 correction.** Single authoritative ownership in `domain.types.risk_advisory` (T-306b). T-305 (`domain.events`) ships only `RiskAdvisoryAcknowledged` event (the *governance event*) which carries a typed *reference* (`RiskAdvisoryAcknowledgementRef = (acknowledgement_id, content_hash, construct_checksum, signature_hash)`) to the value-object in `domain.types.risk_advisory`. Same applies to `DecisionRecord` and `RoleSnapshot` — value objects in `domain.types.governance` (a new sub-module of `domain.types`); events reference them by ID + content hash. T-306 traceability row in Appendix B is updated accordingly.

### H2-04 — T-902 still owns `dna_reader.py`. **Accepted.**

**v1.2 correction.** Remove `dna_reader.py` from T-902's files list. T-902 imports `SnapGeneDnaReader` from `adapter.snapgene` (T-308e's namespace) and owns only `file_watcher.py` (the watcher) + the watch-trigger / debounce / output-emission logic.

### H2-05 — T-606 acceptance requires future phases. **Accepted.**

**v1.2 correction.** T-606's acceptance becomes phase-local: create / open / amend / compile / replay with deterministic fakes and **explicit pending states** for screening (`AwaitingScreening`), authorisation (`AwaitingAuthorisation`), SOP rendering (`AwaitingSopRender`), and export (`AwaitingExport`). The full happy-path UAT ("create → add parts → compile → screen → authorise → export") is owned by **T-1301** (white-paper-example UAT). A new acceptance line in T-606 forbids stubbing downstream services inside T-606 itself; integration with screening + authorisation + export ports is exercised only via in-memory fakes that emit the appropriate `*Completed` events at the test boundary.

### H2-06 — T-309 overclaims gate routing too early. **Accepted.**

**v1.2 correction.** Split T-309 into:

- **T-309a (Phase 3)** — state enum, event-sourced replay skeleton, snapshot format, transition table with **typed pending predicates** (`GateOpen | GateBlocked | GatePending`). Pending predicates raise `GatePredicateNotYetActivated` rather than freezing semantics; tests confirm the predicate maturity matches the gate lifecycle. Owns replay determinism (M2-01 cross-resolution).
- **T-309b (per owning phase)** — activate concrete gate predicates as their owning modules land:
  - `BlockCompile` predicate becomes real in Phase 5 (T-502).
  - `BlockExport` predicate becomes real in Phase 9b (T-903) consuming Phase 10's `ScreeningCompleted` and Phase 8b's `OperationalProtocolAuthorised`.
  - `BlockVendorSubmission` predicate becomes real in Phase 10 (T-1002).
  - `BlockOperationalProtocol` predicate becomes real in Phase 8b (T-806b) consuming Phase 10's `ScreeningCompleted` and T-806a's acknowledgement chain.

T-309b is the umbrella label; concrete gate-activation lives in the owning task. The CI lifecycle column reflects predicate maturity per gate.

### H2-07 — T-205 tests file-watch debounce before watcher contract exists. **Accepted.**

**v1.2 correction.** In T-205, the file-watch debounce test exercises **only a generic-filesystem debounce harness** (`tests/platform/filewatch_debounce_harness.py`) — not `SnapGeneFileWatcher`. The harness implements the generic debounce algorithm against a temp directory using `pathlib` + `watchdog` primitives. T-902's `SnapGeneFileWatcher` (Phase 9a) re-uses the same algorithm and provides the SnapGene-specific watcher acceptance (real OneDrive-style behaviour on `.dna` and `.gb` files). T-205's acceptance is explicit that it tests filesystem primitives, not the platform's production watcher.

### H2-08 — ProcessPoolExecutor spawn policy too brittle. **Accepted.**

**v1.2 correction.** Move multiprocessing policy from "set globally at engine init" to:

- A `WorkerPoolFactory` (new in T-502) that uses `multiprocessing.get_context("spawn")` locally (does **not** mutate the global interpreter state via `set_start_method`).
- Production entry-points (the CLI's `__main__`, the API server's startup) declare `multiprocessing.set_start_method('spawn', force=True)` early if needed; library imports never do.
- Inside FastAPI, tests, and notebook contexts the `WorkerPoolFactory` falls back to `concurrent.futures.ThreadPoolExecutor` (for I/O-bound work) or `SequentialExecutor` (for deterministic small fixtures). Validation correctness is **deterministic** under every executor.
- T-205 platform tests no longer require global spawn semantics; instead they verify the `WorkerPoolFactory` honours its configured executor and that the worker function table is picklable under spawn.

The `T-502-bench` benchmark records latency under each executor mode; `WorkerPoolFactory` picks the right one per platform + workload.

### H2-09 — Dependency-group CI matrix ambiguous + too heavy. **Accepted.**

**v1.2 correction.** Replace `core+dev+all` with explicit install profiles:

| Profile | Extras | OS matrix | Cadence |
|---|---|---|---|
| `core+dev` | none | ubuntu-latest, windows-latest | every PR |
| `core+dev+io` | `io` | ubuntu-latest, windows-latest | every PR |
| `core+dev+biology-fakes` | none (uses tests/fakes/biology/*) | ubuntu-latest, windows-latest | every PR |
| `core+dev+biology-vienna` | `biology-vienna` (pinned 2.6.x) | ubuntu-latest | nightly + biology-touching PR |
| `core+dev+biology-spliceai` | `biology-spliceai` (TensorFlow/HTTP-client) | ubuntu-latest | nightly + biology-touching PR |
| `core+dev+biology-signalp` | `biology-signalp` | ubuntu-latest | nightly + biology-touching PR |
| `core+dev+primer` | `primer3-py` | ubuntu-latest, windows-latest | every PR |
| `core+dev+api` | `api` (FastAPI/uvicorn) | ubuntu-latest, windows-latest | every PR |
| `core+dev+cli` | `cli` (typer/rich) | ubuntu-latest, windows-latest | every PR |
| `core+dev+llm-local` | `llm-local` | ubuntu-latest | nightly |
| `core+dev+llm-openai` | `llm-openai` | ubuntu-latest | nightly (gated on secret) |
| `core+dev+llm-anthropic` | `llm-anthropic` | ubuntu-latest | nightly (gated on secret) |
| `ui` | (separate `ui/` package; `pnpm install`) | ubuntu-latest | every UI-touching PR |

No CI job pulls *all* optional dependencies into a single environment. Windows CI never installs ViennaRNA / SpliceAI / SignalP / LLM providers unless an Anthropic / OpenAI / model-vendor key is provisioned and the dependency is known Windows-safe.

### H2-10 — SnapGene `.dna` fixtures may have licensing risk. **Accepted.**

**v1.2 correction.** Replace any third-party `.dna` fixtures with **permissively-redistributable synthetic plasmids** generated locally by the developer on a licensed SnapGene installation, derived from synthetic constructs whose underlying sequences are public domain (e.g., synthetic promoters from the open SBOL parts library). Each fixture ships with `tests/fixtures/snapgene/<fixture_id>/PROVENANCE.md` documenting: synthetic source, generation date, licensed SnapGene installation used, hash. Fixtures whose provenance cannot be cleared are kept out of the repo and referenced only by a Developer-machine path; the corresponding tests are marked `@pytest.mark.requires_local_snapgene_fixture` and skipped in CI. `snapgene-reader`'s own bundled examples (whose licence permits redistribution for testing) are also acceptable when used.

### H2-11 — BR-14 wrongly listed as a structural predicate. **Accepted.**

**v1.2 correction.** Remove BR-14 from T-503's structural-predicate list (`BR-01..BR-13` only; BR-14 is dropped from the structural-predicate scope). BR-14's predicate is owned by `app.authorisation_decision` (T-806b) and the `no-passive-advisory-bypass-check` CI gate. T-806a (the advisory presentation surface) supplies the pure predicate `all_required_advisories_acknowledged(report, events) → (bool, frozenset[AdvisoryId])`; T-806b consumes it. The `engine.sequence_analysis` package has no opinion on advisory acknowledgement state.

## Moderate findings

### M2-01 — Replay determinism test ownership stale. **Accepted.**

**v1.2 correction.** Replay determinism is owned by **T-309a** (`engine.session` event-sourced replay skeleton) and **T-310b** (`JsonlEventLog` correctness). T-501 owns DAG-evaluator determinism (a *different* property: same rule registry → same DAG → same affected-rules computation). T-1302 reserves end-to-end replay-determinism for adversarial fixtures (e.g., replay a session with a tampered governance event → reproduces the same blocked state and emits a `ReplayIntegrityFailure` event).

### M2-02 — FR-ADV-07 adversarial UAT incomplete. **Accepted.**

**v1.2 correction.** Add two test rows to § 4.3 adversarial UAT:

- `test_construct_checksum_mismatched_acknowledgement` — acknowledge against `construct_checksum` X; then modify the construct (recompute to Y); the gate detects the mismatch and blocks.
- `test_programmatic_event_construction_bypass` — a malicious or buggy module attempts to write an `OperationalProtocolAuthorised` event without the prior governance chain (`AdvisoryWarningPresented` → `RiskAdvisoryAcknowledged` → `ScreeningCompleted`); the `no-passive-advisory-bypass-check` static check + the runtime gate `app.authorisation_decision` both reject. Cross-checked at replay time by T-309a's invariant test.

### M2-03 — Module-coverage gate runs too late and parses prose. **Accepted.**

**v1.2 correction.** Replace prose Markdown parsing in `module_coverage_check.py` with a **machine-readable module manifest** `docs/module_manifest.yaml` (generated from `ARCHITECTURE.md` § 4.2 by a script in `tools/architecture_manifest_generator.py`). The gate parses the YAML, not the prose. The gate's lifecycle:

- `informational` after T-203 lands (Phase 2) — covers all stubs.
- `enforced` after T-310 + T-311 land (Phase 3 exit) — every architecture module must map to ≥ 1 task with declared files + tests + acceptance.

The richer task-acceptance check (was the v1.1 plan) becomes a separate gate `task-acceptance-completeness-check`, scoped to verify that each task's acceptance criteria are themselves machine-readable (a YAML block inside each task brief), lifecycle `informational` until Phase 3 exit, then `enforced`.

### M2-04 — PDF / renderer implementation under-specified. **Accepted.**

**v1.2 correction.** Add explicit renderer implementation files to the design-plan / SOP-protocol / export tasks:

- T-802 deliverables include `src/engine/design_plan/renderers/{markdown,pdf,json}.py` + pinned `weasyprint` / `markdown-it-py` versions + a pinned font (Noto Sans / Noto Mono).
- T-803 deliverables include `src/engine/sop_protocol/renderers/{markdown,pdf,json}.py` using the same renderer policy.
- T-903 deliverables include `src/app/export_orchestrator/renderers/{bundle_zip,manifest}.py`.
- A new **deterministic-rendering policy** in `docs/rendering_determinism.md`: pinned fonts (no system-font fallback), no embedded timestamps in PDFs (use a canonical `creation_date = derivation_environment.created_at_utc`), no metadata fields whose value differs across runs (`/CreationDate`, `/ID` overridden).
- The renderer tests in § 4.6a now reference these implementation files.

### M2-05 — Canonical-JSON decimal-wrapper collision policy. **Accepted.**

**v1.2 correction.** Reserve a project type-tag namespace: any string key beginning with `$$cev:` (e.g., `$$cev:decimal`, `$$cev:datetime`, `$$cev:enum`, `$$cev:bytes`) is reserved for v1.2 canonicalisation tagged-union encoding. User dictionaries containing reserved keys raise `CanonicalisationError` at serialise time. The v1.1 `$decimal` wrapper is renamed to `$$cev:decimal` in v1.2 (golden vectors updated). A migration test ensures all v1.1 golden vectors with `$decimal` are accepted under a compatibility shim during the v1.1 → v1.2 transition and produce identical bytes when re-serialised under the v1.2 tag.

### M2-06 — T-502 benchmark ownership not traceable. **Accepted.**

**v1.2 correction.** Add explicit deliverables to T-502:

- `tests/benchmark/T_502_validation_bench.py` — the benchmark file; not a manifest.
- `tests/benchmark/results/T_502_validation_bench_<git_sha>.json` — recorded results, committed on nightly runs.
- CI cadence: runs on nightly + every PR that touches `src/engine/validation/` or `tools/ci_gates/no_domain_impurity_check.py`. PR-time results are informational; nightly regressions exceeding 50 % over the previous nightly fail the PR and open a follow-up task.
- The validation-engine performance metadata (per-run median latency) is recorded in `tests/benchmark/results/` rather than in per-adapter manifests.

### M2-07 — `TASK_BOARD.md` contradicts regeneration claim. **Accepted.**

**v1.2 correction.** Regenerate `TASK_BOARD.md` § 7 with the four-state lifecycle column, the owning task, the current workflow mode (`informational` / `enforced`), and the last observed CI result (`unknown` until the gate has run at least once). Add a § 1.1 "v1.2 changes" note in `TASK_BOARD.md` linking back to this response document.

### M2-08 — Architecture excerpt shows combined `AuthorisationStore`. **Accepted.**

**v1.2 correction.** Since `CODING_AGENDA.md` v1.2 supersedes the combined `AuthorisationStore` excerpt in `ARCHITECTURE.md:860-904` with the split-port version (B2-04 cross-resolution), add a paragraph in T-203c + a paragraph in the agenda § 0.3 source-of-truth hierarchy explicitly noting that `ARCHITECTURE.md`'s in-text code excerpt at lines 860-904 is a legacy combined form; the **binding port surface** is the split-port enumeration in T-203c. The split form is also the form that `import-linter` enforces and `test_port_inventory.py` tests. (`ARCHITECTURE.md`'s text excerpt does not get amended in this audit-response pass — that would be an architecture amendment, requiring a v1.6 sign-off. The agenda explicitly overrides for implementation purposes per § 0.2 binding-priority.)

### M2-09 — OneDrive path policy needed. **Accepted.**

**v1.2 correction.** Define two path-fixture classes in T-205:

- **`SyncLikePath`** — a path with the characteristics of an actively-syncing OneDrive folder (spaces, non-ASCII, deep nesting) but located *outside* an actively-syncing folder. Used by all CI SQLite concurrency tests, file-watch tests, atomic-write tests.
- **`ActiveSyncPath`** — a path inside an actively-syncing OneDrive folder. Used only by an **optional non-blocking smoke test** that runs on the developer's local machine and emits a warning if OneDrive sync interferes with SQLite locking. Marked `@pytest.mark.requires_active_onedrive_sync`, skipped in CI.

T-201's README note is amended: "Project DBs MUST NOT live inside an actively-syncing OneDrive folder. The default `--db-outside-sync` flag is enabled; setting it to `False` enters an experimental path that the platform actively warns against. Active-sync compatibility is verified only by the optional smoke test in T-205."

## Scientific soundness and engineering rationality — three-role concurrence

`/scientific-advisor`: "The auditor's findings on event-stream ownership (B2-05), advisory acknowledgement ownership (H2-03), and BR-14 placement (H2-11) are correct. Advisory acknowledgement is a governance act with a value-object payload — it belongs in `domain.types.risk_advisory`, not duplicated in `domain.events`. BR-14 is structurally not a sequence-analysis predicate. The export-before-screening defect (B2-02) is the most critical: an export bundle that ships before screening completes would, by definition, be unsafe and unauditable."

`/architect`: "B2-03 and B2-04 are the architecturally most-consequential. The composition root is the single point at which implementation diverges from architecture if the wiring goes wrong. v1.1's composition root passed `AuthorisationReadPort` into `AdminActionHandler` — a structural impossibility. The split-port inventory (B2-06) closes that defect at the type system level. Audit-key management (B2-08) is a separate hole: a tamper-detection chain whose key is co-located with the database it protects is theatrical. v1.2's `AuditKeyProvider` port with three concrete keystore adapters is the smallest correct fix."

`/dev-orchestrator`: "The synchronization pass is the heart of v1.2: bring `ROADMAP.md`, `TASK_BOARD.md`, § 3 wiring, and the appendix tables into agreement. Phase order 8a → 9a → 10 → 8b → 9b → 11 → 12 → 13 is the binding sequence going forward. CI lifecycle column (B2-07), module-manifest gate (M2-03), and benchmark ownership (M2-06) make the QC layer actually self-consistent. Duplicate task IDs (H2-01) are a correctness defect, not a cosmetic one — they would have broken the task parser the moment automated module-coverage CI ran."

## Summary table

| Finding | Severity | Verdict | v1.2 change action |
|---|---|---|---|
| B2-01 | Blocking | Accepted | `ROADMAP.md` regenerated; phase order 0→1→2→3→4→5→6→7→**8a**→**9a**→10→**8b**→**9b**→11→12→13 |
| B2-02 | Blocking | Accepted | Phase 9 split: 9a (I/O + watcher) pre-screening; 9b (final export) post-Phase-8b; T-903 moves to 9b; T-805a renders pre-screening `DraftDesignBundle` |
| B2-03 | Blocking | Accepted | § 3.1/3.2/3.3/3.4/3.5 rewritten end-to-end with all v1.1/v1.2 modules and corrected ordering |
| B2-04 | Blocking | Accepted | **T-311** `app.admin_action_handler` (Phase 3) with `AuthorisationAdminWritePort` + `AuthorisationBootstrapPort`; foundational mint/modify/revoke/list/view-audit; adversarial denial tests |
| B2-05 | Blocking | Accepted | Event-stream wiring corrected: `ScreeningCompleted` / `OperationalProtocolAuthorised` / `SopRendered` to design stream; new cross-stream replay-determinism invariant |
| B2-06 | Blocking | Accepted | T-203c rewritten with explicit numbered port inventory + `tests/ports/test_port_inventory.py` acceptance |
| B2-07 | Blocking | Accepted | § 3.5 CI table + `TASK_BOARD.md` § 7 carry four-state lifecycle column (`not_implemented`/`informational`/`enforced`/`enforced-green`) |
| B2-08 | Blocking | Accepted | **T-312** `AuditKeyProvider` port + three keystore adapters + lifecycle (provisioning/rotation/recovery/offline verification); separation of signature key vs HMAC key |
| B2-09 | Blocking | Accepted | T-805 split into **T-805a** (`app.design_plan_orchestrator`, Phase 8a) and **T-805b** (`app.sop_protocol_orchestrator`, Phase 8b) |
| H2-01 | High | Accepted | MOVED `####` placeholders removed; replaced with prose cross-references |
| H2-02 | High | Accepted | All phase counts + traceability rows + budget rows regenerated |
| H2-03 | High | Accepted | `RiskAdvisoryAcknowledgement` owned by `domain.types.risk_advisory`; events carry typed reference; `DecisionRecord` / `RoleSnapshot` owned by `domain.types.governance` |
| H2-04 | High | Accepted | `dna_reader.py` removed from T-902 file list; T-902 imports `SnapGeneDnaReader` from T-308e namespace |
| H2-05 | High | Accepted | T-606 acceptance phase-local with explicit `AwaitingScreening`/`AwaitingAuthorisation`/`AwaitingSopRender`/`AwaitingExport` pending states; full happy-path moved to T-1301 |
| H2-06 | High | Accepted | T-309 split: T-309a (Phase 3, skeleton + replay determinism + pending predicates); T-309b (per-phase gate activation) |
| H2-07 | High | Accepted | T-205 uses generic `filewatch_debounce_harness.py` only; real watcher acceptance in T-902 |
| H2-08 | High | Accepted | `WorkerPoolFactory` using `get_context("spawn")` locally; production entry-points may set globally, libraries never; sequential fallback for tests/notebooks |
| H2-09 | High | Accepted | CI matrix profiles enumerated; `core+dev+all` removed; heavy adapters Linux-only; Windows excludes ViennaRNA/SpliceAI/SignalP/LLM |
| H2-10 | High | Accepted | Synthetic redistributable `.dna` fixtures + `PROVENANCE.md`; proprietary fixtures marked `requires_local_snapgene_fixture` and skipped in CI |
| H2-11 | High | Accepted | BR-14 removed from T-503 structural predicates; owned by T-806b + `no-passive-advisory-bypass-check` |
| M2-01 | Moderate | Accepted | Replay determinism owned by T-309a + T-310b; T-501 keeps DAG determinism; T-1302 keeps adversarial replay |
| M2-02 | Moderate | Accepted | `test_construct_checksum_mismatched_acknowledgement` + `test_programmatic_event_construction_bypass` added to § 4.3 |
| M2-03 | Moderate | Accepted | `module-coverage-check` parses `docs/module_manifest.yaml` (machine-readable); flips to `enforced` after Phase 3 exit; `task-acceptance-completeness-check` added |
| M2-04 | Moderate | Accepted | Renderer implementation files explicit in T-802 / T-803 / T-903; `docs/rendering_determinism.md` policy |
| M2-05 | Moderate | Accepted | Type-tag namespace `$$cev:` reserved; v1.1 `$decimal` renamed to `$$cev:decimal` with migration shim |
| M2-06 | Moderate | Accepted | `tests/benchmark/T_502_validation_bench.py` + `tests/benchmark/results/` + nightly cadence with PR-time informational mode |
| M2-07 | Moderate | Accepted | `TASK_BOARD.md` § 7 regenerated with lifecycle column + workflow mode + last CI result |
| M2-08 | Moderate | Accepted | T-203c paragraph + agenda § 0.3 paragraph noting architecture's `AuthorisationStore` excerpt is legacy combined form; split form binding via agenda |
| M2-09 | Moderate | Accepted | Two path-fixture classes: `SyncLikePath` (CI) + `ActiveSyncPath` (manual smoke); T-201 README amended |

**Sign-off:** Three roles unanimously approve v1.2.

`/architect`: "The synchronization across roadmap, DAG, composition root, event-stream wiring, persistence wiring, CI tables, and traceability is the deliverable. v1.2 is internally consistent for the first time."

`/scientific-advisor`: "Scientific safety semantics are correct: screening → authorisation → SOP → export ordering, event-stream ownership of screening/authorisation/SOP, advisory acknowledgement ownership in `domain.types.risk_advisory`, BR-14 in the gate not in structural validation. v1.2 reflects what the biology actually requires."

`/dev-orchestrator`: "Lifecycle columns, manifest-driven module coverage, benchmark ownership, and the elimination of duplicate task IDs make the QC layer self-consistent. The plan is implementation-ready."

---

*End of CODING_AGENDA_Second_Round_Audit_Response.md.*
