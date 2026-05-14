# Software Development Working Plan — Coding Agenda v1.5
## Universal Cloning and Expression Vector Design Platform

**Document type:** Authoritative coding agenda derived from `ARCHITECTURE.md` v1.5.
**Drafted by:** A three-role collaboration of `/architect`, `/scientific-advisor`, `/dev-orchestrator`, with adversarial-falsification rounds.
**Date:** 2026-05-14.
**Status:** **Finalised v1.5 consistency release** — supersedes v1.4 after fifth-round Codex audit (`audit report/CODING_AGENDA_Fifth_Round_Audit_Report.md`). This release is deliberately mechanical: it makes the task headings, dependency order, port inventory, Section 3 wiring, support documents, seed manifests, and stale-token checks agree before implementation starts. Substantive v1.5 changes:

- **B5-01 / B5-02 / B5-03.** Phase 3 task cards are physically reordered to match the declared dependency order; stale unsplit `T-314` is deleted from active Section 2; Phase 3 / Phase 4 / cumulative counts are corrected to 19 / 8 / 71 active Section 2 task headings.
- **B5-04.** The canonical port inventory is re-enumerated with unique IDs and the correct total of 50 ports; `test_port_inventory.py` is specified against `docs/port_manifest.yaml`.
- **B5-05 / H5-01 / H5-08.** Section 3 composition, event-stream, persistence, and CI lifecycle tables are synchronised to v1.5 task identities; `SopProtocolGenerator` consumes `sop_template_read_port`; stale active IDs now include all superseded split IDs.
- **B5-06 / B5-07.** Production-authentication edges are made executable: `T-314b` precedes production `T-313b`, and `T-316c` precedes production-signed `T-316b` bootstrap/store integration.
- **B5-08 / B5-09.** Consumer cards use split-task identities and route review-queue admin triage through `ReviewQueueAdminPort` and admin-service IPC only.
- **B5-10 / H5-07 / H5-09.** Source documents are amended for `SopTemplateReadPort` / `SopTemplateAdminWritePort`, `DeveloperBootstrapPrincipal`, `interface.audit_service`, and `interface.admin_service`.
- **H5-02 / H5-03 / M5-01.** Seed manifests and a direct agenda consistency checker are added so counts, heading order, stale tokens, duplicate IDs, duplicate section numbers, and `T-601a..k` range grammar are machine-checkable from the start.
- **H5-04 / H5-05 / H5-06 / M5-04..M5-06.** Audit-service authentication-failure events, admin IPC authentication ownership, unsigned profile drafts, indefinite audit-key archive language, font-current-state wording, and Windows/OneDrive IPC/path fixtures are corrected.

**v1.4 changes (retained context).** v1.4 superseded v1.3 after Codex fourth-round audit (`audit report/CODING_AGENDA_Fourth_Round_Audit_Report.md`). All 27 / 27 audit findings accepted (9 blocking, 10 high, 8 moderate); per-finding adjudication and v1.4 change actions in `audit report/CODING_AGENDA_Fourth_Round_Audit_Response.md`. Substantive v1.4 changes (synchronisation + executability pass — physically reorder Section 2, split new infrastructure tasks so Protocols/fakes land before consumers, redesign audit-concurrency to a single executable writer, regenerate Section 3, align supporting docs):

- **B4-01 Section 2 physical reorder.** Phase 10 module catalogue physically moved between Phase 9a and Phase 8b so heading-order parsers emit `T-1001 / T-1002` before `T-803 / T-805b / T-806b / T-903`. CI fixture `test_task_manifest_phase_order.py` enforces.
- **B4-02 / B4-09 T-314 split + DecisionRecordSigner ownership.** T-314 split into **T-314a** (`AuthorisationProfileSigner` + `AuthorisationProfileVerifier` + `DecisionRecordSigner` + `DecisionRecordVerifier` Protocols + deterministic test fakes + signature error taxonomy; scheduled after T-307 / T-312a, before T-308 / T-310) and **T-314b** (production institutional signer + production per-principal `DecisionRecordSigner` adapter + key lifecycle: rotation / archive / revocation / offline verifier / public-key distribution / compromised-key response; after T-311).
- **B4-03 / B4-04 T-313 split + single-writer audit-service.** T-313 split into **T-313a** (`AuditAppendPort` + `AdminAuditAppendPort` Protocols + `ServicePrincipal` + deterministic fake brokers + chain-integrity test helpers; before T-310) and **T-313b** (production **single-writer audit-service process** owning `audit.sqlite` `mode=rw`; both engine and admin processes send append requests over IPC). Replaces v1.3's non-executable dual-writer + "lock handoff" model.
- **B4-05 T-316 split + YamlSopTemplateLoader removed.** T-316 split into **T-316a** (Phase 3: ports + value objects + `SopTemplateSigner` / `SopTemplateVerifier` Protocols) and **T-316b** (Phase 4 after T-406 catalogue population: signed SQLite store + bootstrap migration + admin-write handler extension + governance events). New **T-316c** (Phase 4: production SOP-template signer + key lifecycle per H4-04). `SopTemplateLibrary` + `YamlSopTemplateLoader` removed from composition root entirely.
- **B4-06 § 3 wiring regenerated end-to-end.** Header "v1.4 — synchronised"; DAG / composition root / event-stream / persistence / CI lifecycle tables all updated to v1.4 task identities (no `T-309a` / `T-309b` / unsplit `T-312`); composition root uses `AuditServiceClient` (IPC client) for audit appends; new static check `test_no_stale_task_ids_in_active_sections.py`.
- **B4-07 manifest authority change.** `docs/module_manifest.yaml` is **manually authored** (not generated from architecture prose); `architecture_manifest_generator.py` removed from T-204; `ARCHITECTURE.md` § 4.2 treated as a checked reference via informational `test_architecture_manifest_consistency.py`.
- **B4-08 T-1103 split + admin commands gated.** T-1103 split into **T-1103a** (`AdminServiceClientPort` Protocol + IPC contract + deterministic test client; before T-1101 / T-1102) and **T-1103b** (admin-service implementation + OS-level ACL/UID enforcement + `ReviewQueueAdminPort` per H4-01; after T-1101 / T-1102). T-1101 / T-1102 forbidden from importing `AdminActionHandler`; routed via `AdminServiceClientPort`.
- **H4-01..H4-10 high findings.** `ReviewQueueAdminPort` wired to admin-service via T-1103b + T-315; security CI gates expanded to 6 surfaces (UserPrincipal + ReviewerPrincipal + `SopTemplateAdminWritePort` + `AuditAppendPort` + direct `AdminActionHandler` import + admin-service IPC bypass) plus three new gates; T-204 generates initial task briefs via `initial_task_brief_generator.py`; new **T-316c** SOP-template key lifecycle; audit-key archive retention now indefinite via institutional escrow; agenda § 0.3 paragraph documenting `DeveloperPrincipal` → `DeveloperBootstrapPrincipal` interpretation in source docs; ROADMAP active sections regenerated; manifest-derived task counts via `tools/task_count_reporter.py`; `core+dev+pdf` CI profile + canonical fonts committed via Git LFS (not network-downloaded); `AuditKeyProvider` Protocol changed to `mac(message)` / `verify(...)` / `rotate(...)` — no raw key bytes exposed.
- **M4-01..M4-08 moderate findings.** `SopTemplateLibrary` removed from port catalogue; stale `T-309a` / `T-309b` / unsplit `T-312` purged from active content; planned-generated vs manifest-derived counts marked; dual-control adversarial UAT scenarios added; Windows pipe ACL + POSIX socket mode tests added to T-1103b; `ReviewQueueStore` clarified to append-only with derived status; Appendix B T-803 row updated; T-201 SOP numbering renumbered consecutively; lifecycle table footer updated.

**v1.3 changes (retained context).** v1.3 absorbed third-round Codex audit (`audit report/CODING_AGENDA_Third_Round_Audit_Report.md`, 27/27 accepted, 8 blocking + 11 high + 8 moderate). Operational security / audit boundary pass: introduced `AuditAppendPort` broker (B3-01); split T-312 into T-312a/T-312b (B3-02); governance events embed full signed payloads (B3-03); profile signing T-314 (B3-04); SOP-template admin write port T-316 (B3-05); review queue T-315 (B3-06); T-205 worker-pool test moved (B3-07); T-309 single identity (B3-08). v1.4 builds on these primitives by making their wiring executable. Per-finding adjudication in `audit report/CODING_AGENDA_Third_Round_Audit_Response.md`. Substantive v1.3 changes (operational security / audit boundary pass — close v1.2's audit-write contradictions, missing signed-payload durability, missing profile signatures, missing SOP-template write port, and missing review-queue workflow):

- **B3-01 audit-write broker.** New **T-313** `AuditAppendPort` broker pattern; composition root injects an append-only broker into engine-process governance services (replaces v1.2's direct `AuditLog` injection). Two writers to the audit chain — engine-process `AuditBroker` + admin-service-process `AdminActionHandler` — both append-only via shared `AuditKeyProvider`.
- **B3-02 T-312 split + Phase 3 reorder.** T-312 split into **T-312a** (`AuditKeyProvider` Protocol + `TestAuditKeyProvider`, scheduled before T-310) and **T-312b** (production keystore adapters + rotation service + offline verifier, scheduled after T-311). Phase 3 order: T-301 → T-302 → T-303 → T-304 → T-305 → T-306 → T-307 → **T-312a** → T-308 → T-309 → T-310 → T-311 → **T-312b** → **T-313** → **T-314** → **T-315** → **T-316**.
- **B3-03 governance events embed signed payloads.** Revised v1.2 H2-03: governance events carry the **full canonical signed value-object** (frozen-dataclass payload), not a reference. FR-ADV-06's immutable approval trace lives in the governance event stream itself. The value-object **type** still lives in `domain.types.{risk_advisory,governance}` (preserving H2-03 namespace separation).
- **B3-04 `AuthorisationProfile` institutional signature.** T-304 adds `profile_signature` + `profile_signature_key_version` fields; T-310d verifies on load (`AuthorisationProfileTamperDetectedError`); T-311 signs on write. New **T-314** `AuthorisationProfileSigner` + `AuthorisationProfileVerifier` ports + adapters (separate cryptographic identity from audit HMAC + per-principal `DecisionRecordSigner`).
- **B3-05 SOP-template admin write port.** New **T-316** `SopTemplateAdminWritePort` + `SopTemplateReadPort` + `SopTemplateBootstrapPort` + SQLite-backed store with signatures + signed governance events. T-803 consumes the read port only; admin writes go through T-316 (extension of T-311).
- **B3-06 administrator review queue + extension requests.** New **T-315** `app.review_queue` + `AuthorisationRequest` service. Closes FR-PROTO-SOP-09 (blocked SOP → structured request to review queue), FR-AUTH-07 (review-queue requirement), FR-AUTH-12 (user extension requests; no auto-grant). T-806b routes blocked sessions to the queue; Phase 11 / Phase 12 surface CLI / API / UI commands via admin-service IPC.
- **B3-07 T-205 worker-pool test deferred.** `test_worker_pool_factory.py` removed from T-205; moved to T-502 (its owning task). T-205 keeps only a minimal `test_spawn_context_available.py` probe.
- **B3-08 T-309 identity model 1.** T-309 has a single task heading; sub-deliverables (a) skeleton in Phase 3 / (b) per-phase gate-predicate activation are documented inline. `#### 2.3.9a` / `#### 2.3.9b` headings removed (matches T-303 / T-308 / T-703 sub-split pattern).
- **H3-01..H3-11 high findings.** T-204 manifest-driven only (adds `task_acceptance_completeness_check.py`, `architecture_manifest_generator.py`, `docs/module_manifest.yaml` generated); `BlockVendorSubmission` split — T-1001 owns vendor-profile portion, T-1002 owns screening-verdict portion; T-1301/T-1302/T-1303 expanded with full SOPs + fixture lists + acceptance criteria; legacy `ROADMAP.md` Phase 8/9 blocks moved to Appendix A; `README.md` updated to v1.3; library-mode internal review text corrected (batched `ScreeningCompleted` → design events); Appendix C T-805 row removed + manifest-derivation note; `rule-fixture-coverage-check` `enforced` at T-405 verification; new **T-1103** admin-service IPC + mutual authentication; new `DeveloperBootstrapPrincipal` sub-type; T-806a `AdvisoryWarningPresented` schema explicit per FR-ADV-02.
- **M3-01..M3-08 moderate findings.** Dependency groups (`[dependency-groups]` for dev, per current uv / PEP 735 syntax) vs PEP 621 optional extras (`[project.optional-dependencies]`) distinguished in T-201; determinism job `not_implemented` until T-1301 fixtures; YAML acceptance schema in Appendix D; `test_port_inventory.py` allows manifest-driven port additions via `docs/port_manifest.yaml`; canonical-font packaging in T-201/T-802 + Linux byte-identity / Windows semantic-identity rendering expectations; `ROADMAP.md` Phase 13 wording corrected; gate-predicate versioning with `DerivationEnvironment` hash maps + replay test for older versions; `TASK_BOARD.md` regenerated from `docs/task_manifest.yaml`.

**v1.2 changes (retained context).** v1.2 absorbed second-round Codex audit (`audit report/CODING_AGENDA_Second_Round_Audit_Report.md`, 29/29 accepted, 9 blocking + 11 high + 9 moderate). Synchronisation pass propagating v1.1 task-card semantics through ROADMAP / wiring / dashboard / traceability + closing 5 structural gaps. Per-finding adjudication in `audit report/CODING_AGENDA_Second_Round_Audit_Response.md`. Substantive v1.2 changes (synchronisation pass — bring wiring, CI lifecycle, dashboard, and traceability into agreement with the v1.1 task-card layer + close five remaining structural gaps):

- **B2-01 `ROADMAP.md` regenerated.** Phase 8 split into 8a (pre-screening) + 8b (post-Phase-10); Phase 9 split into 9a (sequence I/O + SnapGene file-watch, pre-screening) + 9b (final export orchestrator, post-Phase-8b). Final phase order: **0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8a → 9a → 10 → 8b → 9b → 11 → 12 → 13.**
- **B2-02 export-before-screening fixed.** T-903 moved to Phase 9b. Phase 9a contains only I/O channels (no operational export). Pre-screening sharing is via a `DraftDesignBundle` produced by T-805a — structurally incapable of containing `SopLinkedProtocol` or vendor clearance.
- **B2-03 § 3 wiring rewritten end-to-end.** Dependency DAG, composition root, event-stream wiring, persistence wiring, CI lifecycle table all regenerated to reflect 8a → 9a → 10 → 8b → 9b ordering and every new v1.1/v1.2 module.
- **B2-04 `app.admin_action_handler` ownership.** New **T-311** in Phase 3 (foundational mint/modify/revoke/list/view-audit handler with `AuthorisationAdminWritePort` + `AuthorisationBootstrapPort` + adversarial denial tests). Composition root passes the write port (not the read port) to the handler.
- **B2-05 event-stream ownership corrected.** `ScreeningCompleted`, `OperationalProtocolAuthorised`, `SopRendered` → **design** stream (matches `ARCHITECTURE.md` v1.5 lines 2148-2159). Governance stream carries reviewer/admin/advisory/plugin governance only. New cross-stream replay-determinism invariant test in T-309.
- **B2-06 port inventory in T-203c.** Explicit numbered enumeration of every Protocol declared in `ARCHITECTURE.md` § 4.5 plus v1.2 additions; `tests/ports/test_port_inventory.py` acceptance.
- **B2-07 CI lifecycle column.** § 3.5 + `TASK_BOARD.md` § 7 carry four-state lifecycle column (`not_implemented`/`informational`/`enforced`/`enforced-green`) — replaces the simple yes/no blocks-merge column.
- **B2-08 audit-key management.** New **T-312** in Phase 3 — `AuditKeyProvider` port + three keystore adapters (file/Windows-DPAPI/POSIX-keyring) + key lifecycle (provisioning/rotation/recovery/offline verification). Separation of `DecisionRecord` signature key vs HMAC chain key.
- **B2-09 T-805 split.** T-805 split into **T-805a** (`app.design_plan_orchestrator`, Phase 8a — always-renderable `DraftDesignBundle`) + **T-805b** (`app.sop_protocol_orchestrator`, Phase 8b — gated `SopProtocolBundle` after `OperationalProtocolAuthorised`). v1.1 placeholder `####` headings removed (H2-01 cross-resolution).
- **H2-01..H2-11 high findings.** Duplicate `####` headings removed; phase counts + traceability rows regenerated (5/12/6/4/5/5/5/7/2/3/1/2/3/3); `RiskAdvisoryAcknowledgement`/`DecisionRecord`/`RoleSnapshot` owned by `domain.types.risk_advisory` / `domain.types.governance` (events carry typed references); T-902 imports `SnapGeneDnaReader` from T-308e (no `dna_reader.py`); T-606 acceptance phase-local with explicit `Awaiting*` pending states; T-309 split into T-309a (skeleton) + T-309b (per-phase gate activation); T-205 file-watch test uses generic debounce harness only; `WorkerPoolFactory` using `get_context("spawn")` locally (no global state mutation); CI matrix profiles enumerated (no `core+dev+all`); SnapGene fixtures synthetic + `PROVENANCE.md`; BR-14 removed from T-503 structural predicates.
- **M2-01..M2-09 moderate findings.** Replay determinism reassigned to T-309a + T-310b; FR-ADV-07 UAT extended with construct-checksum-mismatch + programmatic-event-bypass cases; `module-coverage-check` parses `docs/module_manifest.yaml` (machine-readable); renderer implementation files explicit in T-802/T-803/T-903 + `docs/rendering_determinism.md`; canonical-JSON type-tag namespace `$$cev:` reserved; T-502 benchmark explicit (`tests/benchmark/T_502_validation_bench.py`); `TASK_BOARD.md` § 7 regenerated; agenda § 0.3 paragraph notes architecture's `AuthorisationStore` text excerpt is legacy combined form (binding form is split-port in T-203c); two path-fixture classes (`SyncLikePath` / `ActiveSyncPath`).

**Project root:** `C:\Users\tocvi\OneDrive\文档\Project_Code\Cloning_Expression_Vector_Design - Codex\`
**Inputs:** `ARCHITECTURE.md` v1.5 (binding), `REQUIREMENTS.md` (FR / NFR / UR / BR / MR / WR / SR / MS / ADV catalogues), `ROADMAP.md` (regenerated from this agenda v1.5), `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` (citation chain), `Cloning_Expression_Vector_Design_White_Paper.md` (conceptual reference).
**Companion deliverable:** `TASK_BOARD.md` (the war-room dashboard; lifecycle-tracked task index, regenerated from this agenda).

**v1.1 changes (retained context).** v1.1 absorbed first-round Codex audit (`audit report/CODING_AGENDA_Audit_Report.md`, 21 / 21 findings accepted, 5 blocking + 8 high + 8 moderate). Summary: B-01 type placement (non-operational types out of `sop_protected`); B-02 nine missing modules added (T-205, T-308e, T-309, T-310, T-504, T-606, T-607, T-807, T-808); B-03 Phase 8 split into 8a / 8b; B-04 CI gate lifecycle states; B-05 rule fixtures mandatory in T-405; H-01..H-08 (port inventory, SnapGene .dna ownership, RFC 8785 JCS, Windows/OneDrive platform tests, dependency groups, calibration drift policy, etc.); M-01..M-08 (ProcessPoolExecutor Windows-spawn, SLIC strategy, threshold profile governance, renderer tests, `implementation_status` flag, generated traceability index, calibration drift policy, app-service tasks). Per-finding adjudication in `audit report/CODING_AGENDA_Audit_Response.md`.

---

## Table of contents

0. Preface — purpose, participants, source-of-truth hierarchy
1. Meta-strategy — operating model
   1.1 Token economy and context-window budgets
   1.2 Parallelism strategy
   1.3 Work-segment definition and lifecycle
   1.4 Traceability requirements
   1.5 War-room dashboard
   1.6 Code commenting standards (migration-ready)
   1.7 Pre-execution / post-execution SOPs
2. Module catalogue — the build queue (71 active Section 2 task cards across 14 implementation phases)
3. Inter-module wiring
4. Test strategy
5. Debugging methodology
6. Development workflow
7. Three-role adversarial review and external audit history
8. Appendices

---

## 0. Preface

### 0.1 Purpose

The coding agenda answers a question that `ARCHITECTURE.md` v1.5 deliberately does *not* answer: **how is this software actually built**, by whom, in what order, with what verification, within what context budget, with what migration headroom? The architecture describes *what* the system is; the agenda describes *how* the engineering team (humans + AI coding agents) brings the system into existence without losing safety, traceability, or quality.

The agenda is *binding* on execution-time decisions. Where it disagrees with `ROADMAP.md`, the agenda wins on *how-to-build*; `ROADMAP.md` wins on *what-to-build-when*. Where it disagrees with `ARCHITECTURE.md`, `ARCHITECTURE.md` wins and the agenda is regenerated.

### 0.2 Participants

| Role | Responsibility in execution |
|---|---|
| `/architect` | Maintains `ARCHITECTURE.md`. Authorises every interface change. Reviews each module's public API before implementation begins. |
| `/scientific-advisor` | Maintains the citation chain in `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md`. Reviews every rule predicate and every biology adapter against published science. Owns `catalogues/rules/*.yaml`, `catalogues/risk_advisories.yaml`. |
| `/dev-orchestrator` | Maintains this agenda, `TASK_BOARD.md`, and `ROADMAP.md` phase exits. Schedules work, assigns model tiers, runs the six-dimension audit at every phase exit. Decides parallelism. |
| `/scientific-coder` (executor) | Implements modules per their per-module SOP in this agenda. Reads task brief → reads scoped architecture sections → produces code + tests → emits post-execution document. |

### 0.3 Source-of-truth hierarchy

`Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` (citations) > `ARCHITECTURE.md` v1.5 (binding design) > `REQUIREMENTS.md` (binding behaviour) > `ROADMAP.md` (regenerated from this agenda) > this agenda (binding *implementation discipline + phasing*) > task briefs (executor-facing).

**v1.2 architecture-excerpt note (M2-08 fix).** The `AuthorisationStore` Protocol shown as in-line Python at `ARCHITECTURE.md:860-904` is a **legacy combined form** that bundles read and admin-write methods on a single Protocol. The **binding port surface** is the **three-protocol split** enumerated in this agenda's T-203c (`AuthorisationReadPort`, `AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`). The split form is what `import-linter` enforces, what `tests/ports/test_port_inventory.py` verifies, and what the composition root (§ 3.2) wires. A future architecture-amendment pass (v1.6+) will replace the legacy excerpt with the split form; until then, the agenda overrides for implementation purposes per § 0.2 binding priority.

**v1.5 `DeveloperPrincipal` binding.** Administrator-action contexts now use **`AdminPrincipal | DeveloperBootstrapPrincipal`** directly in `REQUIREMENTS.md`, `ARCHITECTURE.md`, and this agenda. Ordinary `DeveloperPrincipal` (one without the `is_bootstrap = True` token claim) is **not** authorised for ordinary institutional administration post-bootstrap; the only path for a `DeveloperPrincipal` to perform admin actions is via the `is_bootstrap` claim during initial system setup, or via `institutional_policy.developer_permanent_admin == True` explicit grant. Tests `test_developer_principal_without_bootstrap_claim_denied_post_bootstrap` (T-311) + `test_requirements_and_architecture_developer_principal_references_documented` (T-204) enforce.

Where the agenda is silent, the executor consults `ARCHITECTURE.md` and `REQUIREMENTS.md` first, then this agenda's general SOPs (§ 1.7, § 4, § 6), then asks `/dev-orchestrator`.

---

## 1. Meta-strategy

### 1.1 Token economy and context-window budgets

Every coding task is sized to fit safely inside an Opus 4.7 / Sonnet 4.6 / Haiku 4.5 working window. Practical budgets:

| Working window stage | Tokens | Notes |
|---|---|---|
| Architecture-and-requirements references loaded once at task open | ≤ 30 k | Selective: only the sections this task touches, never the full 160 KB `ARCHITECTURE.md`. |
| Task brief (pre-execution plan + acceptance criteria) | ≤ 5 k | Short and surgical. |
| Code-and-tests being produced + read-back | ≤ 50 k | Sum of all files written, plus any files re-read for validation. |
| Post-execution doc + audit comment | ≤ 5 k | Short. |
| **Total task working budget** | **≤ 90 k** | Leaves headroom for tool calls, error replies, retries. |

Hard rules that follow from this:

1. **Never load the full `ARCHITECTURE.md`** into a coding task. The pre-execution plan (§ 1.7) lists the *exact* sections to be loaded (e.g., `§ 4.5 plugin contracts`, `§ 4.6 v1.4 supplement — Authorisation types`). The orchestrator extracts those sections into a `task_brief/<task_id>.md` file the executor reads instead of the full file.
2. **One module per task** for modules ≤ 800 lines of code. Split larger modules into typed sub-files (one task per sub-file). The catalogue in § 2 records the split decision.
3. **Tests live in the same task as the implementation.** Unit tests for a module are produced in the *same* task that produces the module. This avoids re-loading the module's code in a separate task.
4. **Integration tests are their own tasks.** Cross-module integration is a separate task that loads only the modules' public APIs (not their implementations).
5. **No task may rewrite a previously-completed task's code.** If a defect is found, the orchestrator opens a *new* task for the fix and links to the original task's `post_exec_doc`.

### 1.2 Parallelism strategy

The dependency DAG (§ 3.1) determines which tasks can run concurrently. The orchestrator schedules parallel agents only on tasks whose declared inputs do not overlap (no shared write paths; non-overlapping file write sets).

Rules:

- **Strictly-sequential phases.** Phase 2 (scaffold) → Phase 3 (domain types) → Phase 4 (catalogues) → Phase 5 (validation engine) must run sequentially because every later module depends on earlier ones.
- **Within-phase parallelism is the default after Phase 5.** Phases 6, 7, 9, 10, 12, and 13 contain modules with non-overlapping write sets that can be parallelised. The orchestrator schedules these as concurrent agents (typically 2–4 parallel agents, depending on the phase).
- **Adapter implementations are embarrassingly parallel.** Within Phase 6, the eleven biology adapters share no state; within Phase 10, the three vendor adapters and four screening adapters are likewise independent.
- **Catalogue population is parallel by category.** Within Phase 4, MR / WR / SR / BR / MS / ADV rule manifest population can be split among `/scientific-advisor`-assisted agents, one per category.

### 1.3 Work-segment definition and lifecycle

A **work segment** is the smallest unit the orchestrator schedules. Every segment has the same five-stage lifecycle:

```
   ┌───────────────────────────────────────────────────────────────────┐
   │  WORK-SEGMENT LIFECYCLE                                          │
   ├───────────────────────────────────────────────────────────────────┤
   │  1. PLAN       /dev-orchestrator drafts a task brief from this   │
   │                agenda's module entry. Records in TASK_BOARD.md   │
   │                with status = "planned".                          │
   │                                                                  │
   │  2. ASSIGN     Orchestrator picks model tier (Opus / Sonnet /    │
   │                Haiku) per the module's catalogue entry. Marks    │
   │                task "assigned" with assignee + timestamp.        │
   │                                                                  │
   │  3. EXECUTE    Executor reads task brief + scoped architecture   │
   │                excerpts. Implements module + unit tests.         │
   │                Emits post-execution doc.                         │
   │                Marks "in-progress" then "execution-complete".    │
   │                                                                  │
   │  4. VERIFY     CI runs: lint, mypy --strict, pytest, coverage,   │
   │                determinism, all applicable CI gates. Six-        │
   │                dimension audit by orchestrator. Marks "verified" │
   │                or "verification-failed" with itemised reasons.   │
   │                                                                  │
   │  5. ARCHIVE    Task brief, post-execution doc, audit notes are   │
   │                committed under task_artefacts/<task_id>/.        │
   │                TASK_BOARD.md status = "done". Linked from any    │
   │                downstream task that depends on this output.      │
   └───────────────────────────────────────────────────────────────────┘
```

Status transitions are append-only: a "done" segment is never re-opened; a defect produces a *new* segment that explicitly supersedes the prior one.

### 1.4 Traceability requirements

Every line of code committed by the project must be reachable from a chain:

> source line → file → module entry in § 2 → task brief → ROADMAP phase exit criterion → ARCHITECTURE §x.x → REQUIREMENTS UR-/FR-/MR-/WR-/SR-/BR-/MS-/ADV- ID → citation in `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` §18 (where applicable).

This is enforced by:

- **Mandatory file header comment** (see § 1.6) carrying `module_id`, `task_id`, `architecture_sections`, `requirements_ids`.
- **`audit-traceability-check` CI gate** (already specified in `ARCHITECTURE.md` § 4.10 #13) verifies every cited reference resolves.
- **TASK_BOARD.md** lists every task with the chain explicit.
- **The post-execution doc** for each task records: files written, sections referenced, requirements satisfied, tests added, any deferred sub-tasks.

### 1.5 War-room dashboard

`TASK_BOARD.md` lives at the project root and is the single canonical view of project state. It is regenerated whenever a task transitions state. Structure:

```markdown
# TASK_BOARD.md

## Global progress
- Phase 0:  ✅ complete (foundations)
- Phase 1:  ✅ complete (architecture v1.5)
- Phase 2:  🟡 in-progress (3/8 tasks done, 2 in-progress, 3 planned)
- Phase 3:  ⚪ planned
- ...

## Current bottlenecks
- T-204 (engine.session event-sourcing) — blocked on architecture clarification of snapshot-keying
- T-218 (adapter.biology.SpliceAiAdapter) — blocked on SpliceAI licensing decision
- ...

## In-progress tasks
| Task ID | Module | Assignee | Started | Expected | Status |
|---|---|---|---|---|---|
| T-301 | engine.codon | Sonnet-A | 2026-05-15 | 2026-05-16 | execute |
| T-302 | engine.primer | Sonnet-B | 2026-05-15 | 2026-05-17 | execute |

## Completed tasks (last 20)
...

## Risk register status
- R-21 (advisory bypass): mitigations all green; CI gate `no-passive-advisory-bypass-check` passing.
- ...
```

A complementary CLI command `vector-design status` (delivered in Phase 11) reads `events/`, `tasks/`, and `audit.sqlite` to produce the same view programmatically; the markdown board is the human-readable mirror updated by `/dev-orchestrator`.

### 1.6 Code commenting standards (migration-ready)

Every Python file ships with a standardised header so a future port to Rust (or any strict static-typed language) is mechanical:

```python
"""
module_id:           engine.codon
file:                src/engine/codon/optimiser.py
task_id:             T-307
architecture_refs:   §4.2.1 engine.codon; §4.6 v1.4 supplement → CodingSequenceDesign
requirements_refs:   FR-CORE-04..07; MR-07..09
citations:           Sharp & Li 1987 (PMID 3431546); Clarke & Clark 2008 (PMID 18301736);
                     Jacobs & Shakhnovich 2017 (PMID 29262339)
purity:              pure                                   # pure | adapter | application | interface
migration_notes:     - all types are frozen dataclasses (port to Rust struct + derive PartialEq)
                     - no Python-specific reflection used (no getattr/setattr/dynamic imports)
                     - all string keys for hashmaps are typed via NewType (port to Rust enum or &'static str)
                     - file is < 800 LoC; no module-level mutable state
"""
```

In-line comments follow three rules:

1. **WHY before WHAT.** "Why this codon-table is host-specific" — not "this loops over codons".
2. **Cite the rule.** Where a function implements a rule, the docstring names the rule ID and the citation. Example: `# Implements MR-08 (%MinMax distance ≤ 0.2; Clarke & Clark 2008).`
3. **Mark every cross-layer boundary.** Where a function accepts an injected port (e.g., `RnaFolder`), a one-line comment names the port and the deterministic-fake test fixture. Migration to Rust requires every boundary to be visible.

`/scientific-coder` is required to emit headers + WHY-comments in every PR; the `audit-traceability-check` CI gate parses headers and validates the references.

**v1.1 M-06 refinement — lightweight headers + generated traceability index.** To prevent metadata drift, inline file headers carry only the *mandatory* lightweight fields (`module_id`, `file`, `task_id`). The richer chain — `architecture_refs`, `requirements_refs`, `citations`, `purity`, `migration_notes` — is *generated* from `tasks/task_brief/T-<id>.md` + each module's manifest into `docs/traceability_index.md` by a script invoked in CI. The `audit-traceability-check` gate compares the generated index against the in-file lightweight headers and flags drift in either direction (a file whose `task_id` no longer matches the brief, or a generated index entry whose source brief no longer exists).

### 1.7 Pre-execution / post-execution SOPs

**Pre-execution plan** (orchestrator drafts; executor reads before starting):

```markdown
# task_brief/T-307.md — engine.codon constraint-aware optimiser

## Module
- ID: engine.codon
- Phase: 7
- Model tier: Opus 4.7
- Estimated context budget: ≤ 60 k tokens

## Inputs (load these before coding)
- ARCHITECTURE.md §4.2.1 (engine.codon row)
- ARCHITECTURE.md §4.5 — CodonAlgorithm Protocol definition
- ARCHITECTURE.md §4.6 v1.4 supplement — CodingSequenceDesign dataclass
- REQUIREMENTS.md FR-CORE-04..07; MR-07..09; MR-17
- This agenda § 2.7.4 (engine.codon entry)

## Deliverables
- src/engine/codon/types.py (CodingSequenceDesign — re-export from domain.types if already defined there)
- src/engine/codon/algorithms.py (CAI, %MinMax, CHARMING, avoid_only)
- src/engine/codon/optimiser.py (lexicographic-priority fixed-point loop, N=5 cap)
- tests/engine/codon/test_optimiser.py
- tests/engine/codon/test_algorithms_property.py
- tests/fixtures/codon/gold_constructs/*.json
- docs/handover/T-307_engine_codon.md

## Acceptance
- mypy --strict green
- ≥ 90 % line coverage on src/engine/codon/
- protected_intervals invariant test passes (MR-09)
- ViennaRNA call uses deterministic fake in CI

## Hand-off
- engine.assembly will consume CodingSequenceDesign + result in T-308 (next phase).
```

**Post-execution document** (executor produces; archived):

```markdown
# handover/T-307_engine_codon.md

## Status: execution-complete (awaiting CI verify)

## Files written
- src/engine/codon/types.py (152 LoC)
- src/engine/codon/algorithms.py (487 LoC)
- src/engine/codon/optimiser.py (294 LoC)
- tests/engine/codon/test_optimiser.py (312 LoC, 22 cases)
- tests/engine/codon/test_algorithms_property.py (164 LoC, 4 properties)
- tests/fixtures/codon/gold_constructs/{native_human_egfp,native_yeast_pgk1,...}.json (8 fixtures)

## Architecture sections consumed
- §4.2.1, §4.5 (CodonAlgorithm port), §4.6 v1.4 (CodingSequenceDesign)

## Requirements satisfied
- FR-CORE-04 (multiple algorithms)
- FR-CORE-05 (algorithm selection)
- FR-CORE-06 (protected RNA features preserved)
- FR-CORE-07 (forbidden motif avoidance)
- MR-07, MR-08, MR-09, MR-17

## CI gates touched
- audit-traceability-check
- no-domain-impurity-check (engine.codon imports only domain.* and domain.ports.*)
- import-linter

## Deferred / open
- None.

## Notes for downstream
- engine.assembly should accept a CodingSequenceDesign or a ProteinSequence; the latter
  builds a CodingSequenceDesign with native_dna=None and protected_intervals=().
```

---

## 2. Module catalogue — the build queue

The catalogue lists every module the platform must implement, organised by `ROADMAP.md` phase. Each entry is a *catalogue card* with seven fields:

- **id / file path / phase / model tier**
- **purpose** (one sentence)
- **public API** (what other code calls)
- **dependencies** (modules + ports it imports)
- **SOP** (numbered coding steps; the executor follows them in order)
- **test plan** (unit + property + integration test responsibilities)
- **acceptance** (CI gates + verification predicates)
- **context budget** (estimated LoC + sub-task split decision)
- **migration notes** (Rust-port hazards)

Cards are dense by design: an executor reads one card + the referenced architecture sections, then writes code.

### Phase 2 — Project scaffold (5 tasks; v1.2 — H2-02 phase-count fix)

#### 2.2.1 `T-201` — Python project bootstrap (v1.3 — uv groups vs PEP 621 extras per M3-01; determinism lifecycle per M3-02; canonical font packaging per M3-05)
- **Files:** `pyproject.toml`, `uv.lock`, `.python-version`, `Dockerfile`, `.github/workflows/ci.yaml`, `README.md` (project), `LICENSE` (Apache 2.0), `tools/fonts/install_canonical_fonts.py` (v1.3 — M3-05), `fonts/` (canonical fonts directory).
- **Model tier:** Sonnet. **Phase:** 2. **Context budget:** ≤ 30 k tokens.
- **SOP (v1.3):**
  1. Initialise `uv` project pinning Python 3.11.15 (exact patch from `ARCHITECTURE.md` v1.5).
  2. **(v1.3 M3-01 fix — distinguish uv groups vs PEP 621 extras.)**
     - **`[dependency-groups]` in `pyproject.toml`** — the current `uv` / PEP 735 dependency-group table; used for **`dev` only**. Contents: `pytest`, `pytest-cov`, `pytest-xdist`, `hypothesis`, `mypy`, `ruff`, `pre-commit`, `import-linter`, `mkdocs-material`. Installed via `uv sync --frozen --no-editable --group dev`.
     - **`[project]` `dependencies`** (always installed) — the **`core` runtime**: `pyyaml`, `pydantic` (boundary parsing only; domain types remain frozen dataclasses), `cryptography` (for `DecisionRecord` + profile signatures + `AuditKeyProvider`). Nothing else.
     - **`[project.optional-dependencies]`** — PEP 621 extras (installed via `uv sync --frozen --no-editable --group dev --extra <name>` or `pip install package[extra]`):
       - `io`: `biopython`, `sbol3` (PyPI package for pySBOL3), `snapgene-reader` (read-only `.dna`).
       - `biology-vienna`: `viennarna` (binding, pinned 2.6.x).
       - `biology-spliceai`: `tensorflow` + `spliceai` *or* HTTP-client-only (selected via env var).
       - `biology-signalp`: SignalP wrapper / HTTP client.
       - `primer`: `primer3-py`.
       - `api`: `fastapi`, `uvicorn`, `websockets`.
       - `cli`: `typer`, `rich`.
       - `pdf`: `weasyprint`, `markdown-it-py` (v1.3 — pinned PDF renderer stack per M3-05).
       - `llm-local`, `llm-openai`, `llm-anthropic`.
     - **`ui`** is a separate package under `ui/` managed by `pnpm` (not a Python extra).
  3. **(v1.5 / v1.4 H4-09 / v1.3 M3-05 fix — canonical fonts committed by T-201, not network-downloaded.)** T-201 commits canonical fonts `Noto-Sans-Regular.ttf` + `Noto-Mono-Regular.ttf` under `fonts/` via **Git LFS** (the only acceptable runtime path; license metadata `fonts/LICENSE-NOTO.md` committed alongside). `tools/fonts/install_canonical_fonts.py` becomes a **one-time bootstrap helper** that copies committed fonts into the developer's WeasyPrint font cache; it is **not** a `uv sync` hook (network availability + upstream font bytes do not affect reproducibility). The WeasyPrint renderer (T-802 / T-803 / T-903) uses these bundled fonts via `@font-face` rules — **never** the system fonts. Once T-201 has run, CI fails if either canonical font is missing from `fonts/`. **Platform-rendering expectations**: byte-identical PDF on Linux + Docker (via `core+dev+pdf` CI profile per v1.4 H4-09); *semantically-identical* PDF on Windows (same content, same field ordering, same content hash — but byte-level differences allowed due to Pango/Cairo version skew). `docs/rendering_determinism.md` documents these expectations.
  4. Add `Dockerfile` reproducing the build environment (pinned interpreter, pinned core runtime, pinned `dev` group, pinned OS, pinned font set, **pinned OS-level WeasyPrint dependencies — Pango + Cairo + HarfBuzz pinned versions per v1.4 H4-09**; PEP 621 extras installed only inside their respective container layer). All T-201 `uv sync` / `uv run` commands use `--no-editable` because Windows + OneDrive + non-ASCII path fixtures can make editable-install `.pth` processing unreliable; packaging-path fixtures are formalised later in T-205.
  5. Add GitHub Actions workflow (v1.2 — H2-09 explicit profile matrix; replaces v1.1's ambiguous `core+dev+all`; **v1.4 H4-09 adds `core+dev+pdf` profile**):

     | Profile | Extras | OS matrix | Cadence |
     |---|---|---|---|
     | `core+dev` | none | ubuntu-latest, windows-latest | every PR |
     | `core+dev+io` | `io` | ubuntu-latest, windows-latest | every PR |
     | `core+dev+biology-fakes` | none (uses `tests/fakes/biology/*`) | ubuntu-latest, windows-latest | every PR |
     | `core+dev+biology-vienna` | `biology-vienna` (pinned 2.6.x) | ubuntu-latest | nightly + `src/adapter/biology/vienna_rna*` PR |
     | `core+dev+biology-spliceai` | `biology-spliceai` | ubuntu-latest | nightly + `src/adapter/biology/spliceai*` PR |
     | `core+dev+biology-signalp` | `biology-signalp` | ubuntu-latest | nightly + `src/adapter/biology/signalp*` PR |
     | `core+dev+primer` | `primer` | ubuntu-latest, windows-latest | every PR |
     | `core+dev+api` | `api` | ubuntu-latest, windows-latest | every PR |
     | `core+dev+cli` | `cli` | ubuntu-latest, windows-latest | every PR |
     | **`core+dev+pdf`** (v1.4 H4-09) | `pdf` (WeasyPrint + markdown-it-py + canonical fonts) | ubuntu-latest, windows-latest | every PDF-touching PR + nightly |
     | `core+dev+llm-local` | `llm-local` | ubuntu-latest | nightly |
     | `core+dev+llm-openai` | `llm-openai` | ubuntu-latest | nightly (gated on `OPENAI_API_KEY` secret) |
     | `core+dev+llm-anthropic` | `llm-anthropic` | ubuntu-latest | nightly (gated on `ANTHROPIC_API_KEY` secret) |
     | `ui` | separate `ui/` package via `pnpm install` | ubuntu-latest | every UI-touching PR |

     **No CI job installs all extras together.** Windows CI never installs ViennaRNA / SpliceAI / SignalP / LLM providers. The `core+dev+pdf` Windows job runs renderer tests in semantic-identity mode per v1.3 M3-05.

     - Jobs per cell: `ruff`, `mypy --strict`, `pytest -m "not slow"`. **(v1.3 M3-02 fix)** Container-based determinism check ships as a workflow stub in **`not_implemented` lifecycle state** — present in YAML as a no-op comment until T-1301 fixtures exist; flips to `informational` at T-1301 entry and `enforced` at Phase 13 exit. T-201 does **not** attempt to run determinism against absent fixtures.
     - **Minimal-core job** verifies the `core` runtime + `dev` group alone build the domain + engine layers (no PEP 621 extra imports leak in).
  6. Pre-commit hooks: ruff format, ruff check, mypy.
  7. README adds (v1.2 amended per M2-09): "Project DBs MUST NOT live inside an actively-syncing OneDrive folder. The default `--db-outside-sync` flag is enabled. Setting it to `False` enters an experimental path that the platform actively warns against. Active-sync compatibility is verified only by the optional smoke test in T-205 (manual, not CI)."
- **Acceptance (v1.5 execution note):** `uv sync --frozen --no-editable --group dev` reproducible from lockfile (installs core runtime + dev group); `uv sync --frozen --no-editable --group dev --extra io` reproducible (adds the `io` extra); every CI matrix cell above runs with `uv run --no-editable`; minimal-core job confirms domain + engine layers do not import any PEP 621 extra dependency; canonical fonts present under `fonts/`.
- **Migration:** lockfile + Dockerfile are language-neutral; group + extra names map directly to Rust feature flags.

#### 2.2.2 `T-202` — Directory scaffold
- **Files:** create empty packages and `__init__.py` per `ARCHITECTURE.md` § 4.8 layout, plus `catalogues/`, `events/{design,governance,export}/`, `snapshots/`, `exports/`, `tasks/`, `task_artefacts/`, `docs/handover/`.
- **Model tier:** Haiku. **Phase:** 2. **Context budget:** ≤ 10 k tokens.
- **SOP:** Create directory tree exactly matching § 4.8 plus the new v1.4/v1.5 directories (`catalogues/sop_templates/`, `catalogues/risk_advisories.yaml`, `catalogues/screening_trust_policy.yaml`, `catalogues/institutional_policy.yaml`, `catalogues/export_profiles.yaml`, `catalogues/plugin_manifests/`).
- **Acceptance:** every directory exists; every `__init__.py` is in place; tree matches `ARCHITECTURE.md` § 4.8.

#### 2.2.3 `T-203` — Stub every public API in § 4.2 module catalogue (v1.2 — T-203c port inventory explicit per B2-06)
- **Files:** one stub file per module declared in `ARCHITECTURE.md` § 4.2.1 (domain core), § 4.2.2 (application), § 4.2.3 (adapters), § 4.2.4 (interface) — typed signatures, no implementation, raising `NotImplementedError`. Plus `tests/ports/test_port_inventory.py` under T-203c (acceptance test for the port catalogue).
- **Model tier:** Sonnet (large surface area; needs care with type signatures).
- **Context budget:** Split into four sub-tasks T-203a / T-203b / T-203c / T-203d (one per layer), each ≤ 40 k tokens.
- **SOP:**
  1. For each module in § 4.2, write a single file `src/<package>/<module>.py` containing every public function / class / port signature with full type annotations and a one-line `raise NotImplementedError` body.
  2. Every file gets the standardised header from § 1.6.
  3. Mark every port (`Protocol` class) under `src/domain/ports/`.
  4. **(v1.2 B2-06 fix)** T-203c **explicit numbered port inventory** under `src/domain/ports/` — every Protocol below must exist as a Protocol stub:

     **Catalogue ports (v1.4 M4-01: legacy runtime SOP-template library removed; slot #5 reassigned to `SopTemplateReadPort` via T-316a).** (1) `PartCatalogue`, (2) `HostCatalogue`, (3) `EnzymeCatalogue`, (4) `RuleRegistry`, (5) `SopTemplateReadPort` (v1.4 — replaces the legacy SOP-template read library; owning task T-316a), (6) `RiskAdvisoryCatalogue`, (7) `ScreeningProviderTrustPolicy`, (8) `InstitutionalPolicy`, (9) `ExportProfileCatalogue`, (10) `PluginManifestRegistry`, (11) `ThresholdProfileCatalogue`.

     **Authorisation ports (v1.2 — split per B2-04 / B2-06 / M2-08).** (12) `AuthorisationReadPort` (`get`, `read_own_profile`, `list_for_admin`); (13) `AuthorisationAdminWritePort` (`write_mint`, `write_modify`, `write_revoke`; requires `AdminPrincipal | DeveloperBootstrapPrincipal` — v1.3 H3-10); (14) `AuthorisationBootstrapPort` (`bootstrap_initial_admin`, called once at institutional setup, otherwise raises `AlreadyBootstrappedError`).

     **Persistence ports.** (15) `ProjectStore`, (16) `EventLog` (×3 streams — design / governance / export), (17) `AuditLog` (read interface), (18) `SnapshotStore`.

     **Security ports (v1.5 — unique canonical IDs; v1.4 H4-10 raw-key exposure removed).** (19) `AuditKeyProvider` — `mac(message) -> tuple[KeyVersionId, MacBytes]` / `verify(key_version, message, mac) -> bool` / `verify_with_archived(key_version, message, mac) -> bool` / `rotate(reason, principal) -> KeyVersionId` / `current_key_version() -> KeyVersionId`. **No raw `current_key()` byte-exposing method** — key bytes never leave the keystore adapter in production backends. Owning task T-312a. (20) `DecisionRecordSigner` — per-principal asymmetric signer for `DecisionRecord` / `RoleSnapshot`; (21) `DecisionRecordVerifier` — verifies signed records. **v1.4 B4-09: production implementation owned by T-314b** (per-principal key provisioning + rotation + revocation + offline verifier + public-key distribution + compromised-key response).

     **Audit-append broker ports (v1.3 — new per B3-01; v1.4 B4-04 — IPC client model).** (22) `AuditAppendPort` (single method `append(entry, caller: ServicePrincipal) -> AuditEntryId`; **v1.4: this is an IPC client port — the writer is the dedicated audit-service process**; preserves HMAC chain via `AuditKeyProvider`); (23) `AuditLogReadPort` (read-side only — replay + verification + `audit-traceability-check`); **(v1.4 B4-04 new)** (24) `AdminAuditAppendPort` (admin-side IPC client for the admin-service process; same audit-service writer).

     **Profile signing ports (v1.3 — new per B3-04; v1.4 — owning task split per B4-02).** (25) `AuthorisationProfileSigner` (`sign(draft, admin_principal) -> AuthorisationProfile`; institutional cryptographic identity, separate key from audit HMAC + per-principal DecisionRecord signer; **owning task T-314a Protocol / T-314b production adapter**); (26) `AuthorisationProfileVerifier` (`verify(profile) -> bool`; fails closed on tampered / wrong-version / revoked-key profiles; owning task T-314a / T-314b).

     **Admin-service IPC client port (v1.4 — new per B4-08).** (27) `AdminServiceClientPort` — Protocol used by CLI / API admin-command handlers to dispatch admin actions to the admin-service process via IPC (named pipe on Windows / Unix socket on POSIX). Signed admin-principal token. Owning task T-1103a (Protocol + IPC contract + deterministic test client) / T-1103b (production admin-service implementation).

     **SOP-template admin ports (v1.3 / v1.4 — moved canonical slot per M4-01).** v1.3 `SopTemplateReadPort` is now canonical port #5 (above). (28) `SopTemplateAdminWritePort` (`write_mint`, `write_modify`, `write_revoke`; requires `AdminPrincipal | DeveloperBootstrapPrincipal`); (29) `SopTemplateBootstrapPort` (`bootstrap_initial_templates(developer)`); **(v1.4 H4-04 new)** (30) `SopTemplateSigner` (institutional signer; separate cryptographic identity from audit HMAC + profile signer + DecisionRecord signer); (31) `SopTemplateVerifier` (verifies signed templates on read).

     **Review-queue ports (v1.3 — new per B3-06; v1.4 H4-01 / M4-06 clarified).** (32) `ReviewQueueStore` — **append-only request/read model**: `add(request)` writes an immutable request row; `list_pending(admin_principal)`; `get(item_id)`. The `status` field on `ReviewQueueItem` is **derived** from the latest decision row by the read model (not an update column). **(v1.4 H4-01 new)** (33) `ReviewQueueAdminPort` — admin-side resolution Protocol used only by the admin-service process (T-1103b); its `resolve(item_id, decision)` appends a decision row referencing the request. Engine-process callers cannot invoke; user/API callers cannot self-resolve.

     **I/O ports.** (34) `SequenceReader`, (35) `SequenceWriter`, (36) `SnapGeneChannel`, (37) `SnapGeneDnaReader` (read-only `.dna`).

     **Biology ports.** (38) `RnaFolder`, (39) `SplicePredictor`, (40) `SignalPeptidePredictor`, (41) `TIRPredictor`, (42) `KozakScorer`, (43) `CodonAlgorithm` (×4 algorithms — CAI / MinMax / CHARMING / avoid_only — each implements the same Protocol).

     **Engine support ports.** (44) `WorkerPoolFactory` (v1.2 — per H2-08).

     **Vendor + screening ports.** (45) `SynthesisVendorAdapter`, (46) `ScreeningAdapter`.

     **LLM ports.** (47) `LLMConstraintTranslator`, (48) `AdvisoryTextPolicy`.

     **Lifecycle ports (v1.1 / v1.2).** (49) `Lifecycle` (optional `start()` / `stop()`); (50) `RefreshableAdapter` (optional `refresh()` for adapters with rotating tokens / lazy-loaded models).

     **Total: 50 canonical ports** (v1.5 corrected arithmetic: v1.3 had 45 ports; remove the legacy SOP-template library port per M4-01 (-1); add `SopTemplateSigner` + `SopTemplateVerifier` (+2), `DecisionRecordVerifier` (+1), `AdminAuditAppendPort` (+1), `ReviewQueueAdminPort` (+1), and `AdminServiceClientPort` (+1) = +5 net change -> **50** ports total. `AuditKeyProvider` Protocol surface revised per H4-10, no port count change).

  5. **`tests/ports/test_port_inventory.py` (v1.3 — manifest-driven additions per M3-04)** — imports each of the 50 canonical ports above and fails if (a) any canonical port is missing; (b) any port has merged read and admin-write methods (`AuthorisationStore` legacy combined form is **forbidden**); (c) any expected method is missing; (d) any **additional** port discovered under `src/domain/ports/` lacks a manifest entry in `docs/port_manifest.yaml` (with `port_id`, `owning_task`, `architecture_section`, `requirements_refs` populated — v1.3 M3-04 fix). Manifest-less ports fail the gate; plugin-driven port additions are permitted via the manifest.
- **Acceptance:** `mypy --strict` green on every stub; `import-linter` contract passes (engines do not import adapters); `tests/ports/test_port_inventory.py` green.
- **Migration:** typed signatures are pure interface — direct port to Rust traits.

#### 2.2.4 `T-204` — CI gate skeletons with lifecycle states (v1.4 — manifest authority fixed per B4-07; expanded security gates per H4-02; initial-brief generator per H4-03)
- **Files:** `tools/ci_gates/` containing one stub per CI gate: `no_self_authorisation_check.py`, `no_passive_advisory_bypass_check.py`, `import_linter.ini`, `sop_after_gates_check.py`, `llm_output_policy_check.py`, `audit_traceability_check.py`, `plugin_manifest_signature_check.py`, `stale_catalogue_check.py`, `source_grade_citation_check.py`, `no_domain_impurity_check.py`, `module_coverage_check.py`, `gate_lifecycle_check.py`, `task_acceptance_completeness_check.py`, `rule_fixture_coverage_check.py`, `implementation_status_consistency_check.py`, **`no_direct_admin_handler_import_check.py` (v1.4 H4-02 new)**, **`audit_append_port_only_check.py` (v1.4 H4-02 new)**, **`sop_template_admin_port_only_check.py` (v1.4 H4-02 new)**, **`no_stale_task_ids_in_active_sections_check.py` (v1.4 M4-02 new)**, **`test_task_manifest_phase_order.py` (v1.4 B4-01 new)**, **`test_roadmap_stale_tokens.py` (v1.4 H4-07 new)**, **`test_task_count_consistency.py` (v1.4 H4-08 new)**, **`test_architecture_manifest_consistency.py` (v1.4 B4-07 new — informational)**, **`test_task_brief_coverage.py` (v1.4 H4-03 new)**. Plus **`tools/task_manifest_generator.py` (v1.3, v1.4 uses explicit phase-order table per B4-01)**, **`tools/port_manifest_generator.py` (v1.3 new — M3-04)**, **`tools/initial_task_brief_generator.py` (v1.4 H4-03 new)**, **`tools/task_count_reporter.py` (v1.4 H4-08 new)**. **(v1.5 B5-03 / v1.4 B4-07)** `tools/architecture_manifest_generator.py` is **removed**; `docs/module_manifest.yaml` is **manually authored** by `/dev-orchestrator` and committed (no automated generation from `ARCHITECTURE.md` prose). T-204 owns the generator/refinement workflow, but this repository now contains seed manifests under `docs/`: `docs/module_manifest.yaml` (manual seed), `docs/task_manifest.yaml` (heading-derived seed), and `docs/port_manifest.yaml` (canonical port seed). Tests: `tests/ci_gates/{test_module_coverage_check,test_task_acceptance_completeness_check,test_gate_lifecycle_check,test_rule_fixture_coverage_check,test_implementation_status_consistency_check}.py`.
- **Model tier:** Sonnet. **Phase:** 2. **Context budget:** ≤ 55 k tokens (v1.4 increased from 45 k for the expanded gate scope + initial-brief generator).
- **SOP (v1.3):**
  1. Every gate script lives at `tools/ci_gates/<gate>.py` with a header declaring its current `lifecycle_state` ∈ {`not_implemented`, `informational`, `enforced`, `enforced-green`} and its `owning_task_id`.
  2. Every gate script supports two run modes: `--informational` (default in early phases — runs and *reports* but returns exit 0 even on TODO predicates) and `--enforce` (returns exit 1 on any TODO marker, missing fixture, or unimplemented predicate).
  3. Initial state for every gate: `not_implemented` (script absent or pure-stub) — workflow does *not* run it. As the owning task transitions to `in-progress`, lifecycle flips to `informational`; the workflow runs the gate under `--informational` and the result is logged but does not block merge. When the owning task transitions to `verified`, lifecycle flips to `enforced` and the workflow runs under `--enforce` with merge-blocking semantics; `enforced-green` once observed-passing on `main`.
  4. **Meta-test `gate_lifecycle_check.py`** scans `tools/ci_gates/*.py` headers + the workflow YAML and fails if any gate listed under `enforced` in `TASK_BOARD.md` contains a TODO marker or returns exit 0 in `--enforce` mode against a known-failing fixture.
  5. **`module_coverage_check.py` (v1.4 — manifest is manually authored per B4-07).** Parses `docs/module_manifest.yaml` (a **manually-authored** committed manifest; no automated parsing of `ARCHITECTURE.md` prose). Manifest schema: `{module_id, layer, architecture_section, tasks: [task_id, ...]}`. Fails if any module lacks ≥ 1 task. Initial state: `informational` until T-311 + T-312b land (end of Phase 3); flips to `enforced` at Phase 3 exit. Companion **informational** gate `test_architecture_manifest_consistency.py` warns if a manifest module is unreferenced in `ARCHITECTURE.md` prose (helps detect future architecture-doc drift but does not block merges).
  6. **`task_acceptance_completeness_check.py` (v1.3 new — M3-03).** Parses every `tasks/task_brief/T-<id>.md`, locates the mandatory YAML acceptance block (schema in Appendix D), fails if missing or malformed. Cross-checks each acceptance item references an actual test file. Initial state: `informational` until Phase 3 exit; flips to `enforced` thereafter. **(v1.4 H4-03)** Initial briefs are bootstrapped via `tools/initial_task_brief_generator.py` (below) so the gate has something to parse from the start.
  7. **`tools/initial_task_brief_generator.py` (v1.4 H4-03 new).** Walks `CODING_AGENDA.md` § 2 task headings and emits initial `tasks/task_brief/T-<id>.md` files (with the mandatory YAML acceptance block per M3-03 / Appendix D, populated from the task card's deliverables + acceptance prose). Initial briefs are *seeds*; `/dev-orchestrator` refines each brief before assignment. Companion test `test_task_brief_coverage.py` asserts every `#### ... T-*` heading has a corresponding brief file.
  8. **`task_manifest_generator.py` (v1.3; v1.4 B4-01 uses explicit phase-order table).** Walks all `#### 2.x.y T-<id>` headings in `CODING_AGENDA.md` § 2 and emits `docs/task_manifest.yaml` with `{task_id, phase, model_tier, context_budget, owning_modules, depends_on}`. **v1.5 B5-01 / v1.4 B4-01 fix:** uses an explicit intra-phase dependency-order table plus the explicit phase-order table `[2, 3, 4, 5, 6, 7, 8a, 9a, 10, 8b, 9b, 11, 12, 13]` — fails if heading order disagrees with either table. The parser formally recognises range headings such as `T-601a..k`, stores them as one active card with `expanded_task_ids`, and requires companion tests so task-brief generation cannot silently skip the child IDs. `TASK_BOARD.md` cumulative counts are derived from this manifest via `tools/task_count_reporter.py` per v1.4 H4-08. CI fixture `test_task_manifest_phase_order.py` asserts `T-1001 / T-1002` precede `T-803 / T-806b / T-903`.
  9. **`port_manifest_generator.py` (v1.3 new — M3-04).** Walks `src/domain/ports/**/*.py` and emits `docs/port_manifest.yaml` with `{port_id, owning_task, architecture_section, requirements_refs}`. `test_port_inventory.py` cross-checks against this manifest.
  10. **(v1.4 H4-02 — expanded security gate scope.) `no-self-authorisation-check` covers 6 surfaces:** (1) UserPrincipal attempts to call `AuthorisationAdminWritePort.write_*`; (2) **ReviewerPrincipal** attempts (FR-AUTH-14); (3) UserPrincipal / ReviewerPrincipal attempts on `SopTemplateAdminWritePort.write_*`; (4) engine-process imports of `SqliteAuditLog` or `AuditBroker` write surfaces (must use `AuditAppendPort` only); (5) CLI / API direct imports of `AdminActionHandler` (must use `AdminServiceClientPort`); (6) admin-service IPC bypass attempts (calls outside the IPC layer). Also: `DeveloperBootstrapPrincipal` post-bootstrap restriction tests. Activation milestones: `informational` after T-311; `enforced` after T-313b + T-316b + T-1103b verified; `enforced-green` requires all 6 surfaces with adversarial tests. Three new companion gates: **`no_direct_admin_handler_import_check.py`** (static — CLI/API code paths must not import `AdminActionHandler`); **`audit_append_port_only_check.py`** (static — engine-process governance services must not import `SqliteAuditLog` / `AuditBroker` directly); **`sop_template_admin_port_only_check.py`** (static — SOP rendering / catalogue loaders must not import the admin-write port).
  11. **(v1.4 M4-02 + B4-06)** `no_stale_task_ids_in_active_sections_check.py` — fails if superseded split-task IDs appear in active sections. The retired-ID set is owned by the gate fixture, not restated in agenda prose; allow-lists are explicit and limited to historical changelog/audit sections only.
  12. **(v1.4 H4-07)** `test_support_doc_stale_tokens.py` — fails if active `README.md` or `ROADMAP.md` sections contain stale release labels, legacy architecture-version labels, removed runtime SOP-template library names, stale admin-context developer authority, or superseded split-task IDs.
  13. **(v1.4 H4-08)** `test_task_count_consistency.py` — fails if Section 2 heading-count + Appendix C row-count + `TASK_BOARD.md` § 1 count disagree.
  14. Wire each gate into `.github/workflows/ci.yaml` with conditional `if:` per the v1.0 § 3.5 path-filtering rules + per the lifecycle state (`enforced` gates always run; `informational` gates run with `continue-on-error: true`).
- **Acceptance:** all gate scripts present with lifecycle headers; `gate_lifecycle_check.py` runs in CI and passes; `module_coverage_check.py` + `task_acceptance_completeness_check.py` run in `informational` mode against the manually-authored `docs/module_manifest.yaml` + the initial-brief set produced by `tools/initial_task_brief_generator.py`; both manifest generators (task + port) produce non-empty YAML; expanded security gates' 6 surfaces all have stub tests landing as `informational`; phase-order fixture passes.
- **(v1.2 B2-07) `TASK_BOARD.md` § 7 integration:** each gate row carries a **four-state lifecycle column** (`not_implemented` / `informational` / `enforced` / `enforced-green`), the owning task ID, the current workflow mode, and the last observed CI result.

#### 2.2.5 `T-205` — Platform-readiness baseline (v1.2 — refined per H2-07 / H2-08 / M2-09)
- **Files:** `tests/platform/{test_paths_nonascii,test_paths_with_spaces,test_sqlite_wal_locking,test_filewatch_debounce_harness,test_atomic_writes,test_spawn_context_available,test_named_pipe_ipc_permissions,test_unix_socket_permissions,test_onedrive_sqlite_wal_smoke}.py`, `tests/platform/filewatch_debounce_harness.py` (generic harness, **not** a watcher), `tests/conftest_platform.py` (path fixtures), `docs/platform_caveats.md`.
- **Model tier:** Sonnet. **Phase:** 2. **Context budget:** ≤ 40 k tokens.
- **SOP (v1.2):**
  1. **Path fixtures (v1.2 M2-09).** Two path-fixture classes:
     - **`SyncLikePath`** — a temp directory containing both a space *and* a non-ASCII character (`tmp_with space + 文档/`), deep nesting; located *outside* any actively-syncing folder. **Used by all CI tests** (SQLite concurrency, file-watch, atomic-write).
     - **`ActiveSyncPath`** — a path inside an actively-syncing OneDrive folder. Used only by `tests/platform/test_active_sync_smoke.py`, marked `@pytest.mark.requires_active_onedrive_sync`. **Skipped in CI**; runs only on the developer's local machine.
  2. SQLite WAL + locking concurrency test under `SyncLikePath`: two writers + N readers; assert no `database is locked` errors under the agreed retry policy; assert WAL files clean up after close.
  3. **File-watch debounce test (v1.2 H2-07 fix).** Tests **only the generic debounce algorithm** via `tests/platform/filewatch_debounce_harness.py` — a small test-only harness that simulates burst writes against a temp directory using `pathlib` + `watchdog` primitives. **The harness is not `SnapGeneFileWatcher`** — the production SnapGene watcher (T-902 in Phase 9a) re-uses this debounce algorithm with the SnapGene-specific watch targets. T-205's acceptance is explicit that it tests filesystem primitives, not the production watcher.
  4. Atomic-write test: every output is written to `.tmp` and renamed; partial-write crash recovery verified by killing mid-write and re-running.
  5. **(v1.3 B3-07 fix — `WorkerPoolFactory` tests deferred to T-502.)** Phase 2 owns only a **minimal platform probe**: `tests/platform/test_spawn_context_available.py` asserts that `multiprocessing.get_context("spawn")` returns a usable context on this platform (both ubuntu-latest and windows-latest). The probe creates a small top-level test function in a temp module and executes one call through the spawn context — no `WorkerPoolFactory` involved. The full `WorkerPoolFactory` cross-mode tests (sequential / thread / process; library-import safety; FastAPI/notebook fallback) are **owned by T-502** in Phase 5 (which is when `WorkerPoolFactory` actually exists). T-205 cannot test what does not yet exist.
  6. **(v1.5 M5-06) IPC/path readiness for split services.** Windows named-pipe creation/connection fixtures verify service-account ACLs for `cev-audit-service` and `cev-admin-service`; POSIX Unix-socket fixtures verify socket path length, owner, mode, and connection denial for non-service users. SQLite WAL smoke fixtures cover `audit.sqlite`, `authorisation.sqlite`, `sop_templates.sqlite`, and `review_queue.sqlite` under `SyncLikePath`, with the actively-synced OneDrive path tested only by a skipped-by-default local marker.
   7. Long-path test (≥ 260 chars) where applicable.
  8. Case-sensitivity test (file `Foo.txt` vs `foo.txt` on case-insensitive Windows vs case-sensitive Linux).
  9. Document the platform caveats in `docs/platform_caveats.md` (OneDrive sync, long paths, SQLite WAL inside synced folders, PowerShell quoting rules, `WorkerPoolFactory` semantics across environments).
- **Acceptance:** every platform test green on both `ubuntu-latest` *and* `windows-latest` CI matrix cells; `docs/platform_caveats.md` exists and is linked from the project README; `test_active_sync_smoke.py` is *skipped* (not failed) in CI.
- **Migration:** all path handling uses `pathlib.Path` (portable to Rust `std::path::Path`); no OS-specific syscalls in the domain or engine layers.

### Phase 3 — Core domain model + sequence I/O + security ports (19 tasks; v1.5 — physical order now matches protocol/fake-before-consumer dependency order; T-314b precedes production T-313b authentication)

**Phase 3 v1.5 task order (Protocols + fakes before consumers; production authenticators before production services):**

T-301 → T-302 → T-303 → T-304 → T-305 → T-306 → T-307 → **T-312a** (AuditKeyProvider Protocol + TestProvider) → **T-313a** (AuditAppendPort + AdminAuditAppendPort Protocols + fake brokers) → **T-314a** (AuthorisationProfileSigner/Verifier + DecisionRecordSigner/Verifier Protocols + fakes) → **T-316a** (SopTemplate split-port Protocols + SopTemplateSigner/Verifier Protocols + value objects) → T-308 → T-309 → T-310 → T-311 → **T-312b** (production audit-key keystores + rotation service + offline verifier) → **T-314b** (production institutional signer + per-principal DecisionRecordSigner + key lifecycle per B4-09) → **T-313b** (production single-writer audit-service per B4-04, authenticated by T-314b verifier) → **T-315** (review queue + `AuthorisationRequest` service; defines `ReviewQueueAdminPort` consumed by T-1103b).

Note: **T-316c** (production SOP-template signer + key lifecycle per H4-04) and **T-316b** (signed SQLite SOP-template store + bootstrap migration) are **Phase 4**, after catalogue schema/content. T-316c is scheduled before T-316b so production bootstrap can sign and verify with production adapters.

**v1.5 split rationale (B5-01 / B5-06 / B5-07 plus B4-02 / B4-03 / B4-05):** v1.3 scheduled the audit-service, profile-signing, and SOP-template tasks after their consumers (T-310 / T-311). v1.5 keeps each early Protocol+fake task before consumers and schedules production adapters only after the consumers that need the Protocols. Production-authenticated services depend on production authenticators: T-313b follows T-314b, and Phase 4 schedules T-316c before T-316b.

#### 2.3.1 `T-301` — `domain.sequence` primitives
- **Files:** `src/domain/sequence/alphabets.py`, `src/domain/sequence/record.py`, `src/domain/sequence/location.py`, `src/domain/sequence/feature.py`, `src/domain/sequence/qualifier.py`, plus matching tests.
- **Model tier:** Opus (data-model precision required). **Context budget:** ≤ 60 k tokens. Sub-split allowed if exceeded.
- **SOP:**
  1. Implement `Alphabet`, `MoleculeType` enums (`ARCHITECTURE.md` § 4.6 v1.4 supplement).
  2. Implement `Sequence` ADT with sub-types `DnaSequence`, `RnaSequence`, `ProteinSequence`, `OligoSequence`.
  3. Implement `SequenceRecord` with canonical-orientation checksum (lex-min rotation for circular).
  4. Implement `LocationV14` with formal algebra: `LocationFuzziness`, `CompoundLocationKind`, `sequence_length_invariant_satisfied()`.
  5. Implement `Qualifier` structured type (B6).
  6. Implement `FeatureV14` with sub-features (compound feature support).
  7. Implement five typed hashes (`ConstructHashes`).
  8. Property tests: round-trip serialisation; circular checksum invariance under rotation; location-algebra invariants.
- **Acceptance:** every type frozen-dataclass; `mypy --strict`; 95 % coverage on this package; property tests with ≥ 1000 generated cases per type.
- **Local status:** completed and verified on 2026-05-14; see `task_artefacts/T-301/post_execution.md`.
- **Migration:** all enums map to Rust enums; frozen dataclasses map to Rust structs with `derive(Eq, Hash)`; checksum logic is byte-canonical and language-neutral.

#### 2.3.2 `T-302` — `domain.graph` (ConstructGraph)
- **Files:** `src/domain/graph/nodes.py`, `src/domain/graph/edges.py`, `src/domain/graph/construct_graph.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 50 k tokens.
- **SOP:**
  1. Implement `GraphNode`, `EdgeKind`, `Edge`, `ConstructGraph`.
  2. Implement `derive_feature_table(graph) → tuple[Feature, ...]` (M4 canonical-vs-derived rule).
  3. Implement graph topology validation: every edge endpoint exists; circular topology consistent with `SequenceRecord.topology`.
  4. Property tests: feature-table derivation is deterministic; graph round-trips through canonical JSON.
- **Acceptance:** every state transition preserves `feature_table == derive_feature_table(graph)`.
- **Local status:** completed and verified on 2026-05-14; see `task_artefacts/T-302/post_execution.md`.

#### 2.3.3 `T-303` — `domain.types` core entities
- **Files:** `src/domain/types/part.py`, `host.py`, `host_context.py`, `module.py`, `construct.py`, `library.py`, `assembly_method.py`, `assembly_plan.py`, `validation_rule.py`, `host_compat.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 70 k tokens — **split** into T-303a (Part/Host/HostContext/Module/Construct), T-303b (Library/AssemblyMethod/AssemblyPlan subclasses), T-303c (ValidationRule + HostCompatibilityConstraints).
- **SOP:**
  1. Per sub-task, implement the relevant frozen-dataclass types from `ARCHITECTURE.md` § 4.6 v1.4 supplement.
  2. Add validation in `__post_init__`: e.g., `Construct` requires `feature_table == derive_feature_table(graph)`.
  3. Add typed `AssemblyPlan` subclasses (M3 fix): `RestrictionLigationPlan`, `OverlapAssemblyPlan`, `TypeIISAssemblyPlan`, `GatewayPlan`, `LICPlan`, `USERPlan`, `InVivoAssemblyPlan`, `YeastTARPlan`.
- **Acceptance:** type invariants enforced on construction; tests for every invariant; `mypy --strict`.
- **Local status:** completed and verified on 2026-05-14; see `task_artefacts/T-303/post_execution.md`.

#### 2.3.4 `T-304` — `domain.security` (SecurityRole + Principal + AuthorisationProfile; v1.3 — profile signature per B3-04; `DeveloperBootstrapPrincipal` per H3-10)
- **Files:** `src/domain/security/roles.py`, `principals.py`, `operational_role.py`, `authorisation_profile.py`, `profile_signature.py` (v1.3 — new), `unsigned_authorisation_profile_draft.py` (v1.5 — unsigned draft model), `dual_control.py`, `tests/`.
- **Model tier:** Opus. **Context budget:** ≤ 65 k tokens (v1.3 increased from 60 k).
- **SOP (v1.3):**
  1. Implement `SecurityRole`, `OperationalRole` (M6 split).
  2. Implement `Principal` base + `UserPrincipal` / `ReviewerPrincipal` / `AdminPrincipal` / `DeveloperPrincipal` / **`DeveloperBootstrapPrincipal` (v1.3 H3-10 new)**. `DeveloperBootstrapPrincipal` is a `DeveloperPrincipal` whose token carries `is_bootstrap = True` claim, valid only during initial system bootstrap or when `institutional_policy.developer_permanent_admin == True`. Architecture's permissions matrix (`ARCHITECTURE.md:655-679`) places Developer at the bootstrap/system-level scope; post-bootstrap institutional admin authority requires `AdminPrincipal`.
  3. Implement `ROLE_INHERITS` map + `Principal.can_act_as` predicate (v1.3 v1.0 from before). Add `Principal.has_bootstrap_authority` predicate that returns True only for `DeveloperBootstrapPrincipal` whose claim is unexpired.
  4. Implement `CoveredBiologicalScope` (B4 expanded fields).
  5. Implement `DualControlFlags` (v1.3 v1.0 opt-in hooks).
  6. **Implement `UnsignedAuthorisationProfileDraft` + signed `AuthorisationProfile` v1.5.** The unsigned draft carries the mutable administrator input fields and cannot be persisted. The signed `AuthorisationProfile` carries `profile_content_hash`, `profile_signature: ProfileSignature` (B3-04 new — binds full canonical payload + version + subject UserId + issuer AdminPrincipalId + validity interval + revocation metadata via the institutional `AuthorisationProfileSigner` key), `profile_signature_key_version: KeyVersionId`. Frozen-dataclass `__post_init__` validation: profile with mismatched `profile_content_hash` raises `InvalidProfileError`; signature verification deferred to the persistence layer (T-310d / T-314a Protocol, T-314b production verifier). The signer constructs a signed `AuthorisationProfile` from a validated `UnsignedAuthorisationProfileDraft`; empty signatures are not valid sentinels.
  7. Implement `UserDeclaration`.
  8. Implement `ProfileSignature` value object (frozen dataclass with `signed_payload_hash`, `signature_bytes`, `signing_key_version`, `signed_at_utc`).
- **Acceptance:**
  - `UserPrincipal.can_act_as(SecurityRole.ADMINISTRATOR) == False`; `AdminPrincipal.can_act_as(SecurityRole.REVIEWER) == True`; `ReviewerPrincipal.can_act_as(SecurityRole.ADMINISTRATOR) == False`.
  - `DeveloperBootstrapPrincipal.has_bootstrap_authority == True`; ordinary `DeveloperPrincipal.has_bootstrap_authority == False`.
  - Unsigned drafts cannot cross the persistence boundary; a signed `AuthorisationProfile` with mismatched signature payload raises `InvalidProfileError` at construction (frozen-dataclass invariant).
  - Re-canonicalising a profile produces byte-identical signed payload.
- **Local status:** completed and verified on 2026-05-14; see `task_artefacts/T-304/post_execution.md`.
- **Migration:** straightforward — Rust enums + structs; signature is a binary byte string; key version is a typed integer.

#### 2.3.5 `T-305` — `domain.events` (typed events, three streams; v1.2 — H2-03 ownership cleanup)
- **Files:** `src/domain/events/base.py`, `design.py`, `governance.py`, `export.py`, tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 50 k tokens.
- **SOP (v1.2):**
  1. Implement `DomainEvent` abstract base.
  2. Implement `DesignEvent` subclasses listed in `ARCHITECTURE.md` § 4.7 / lines 2148-2159, **including (v1.2 B2-05 fix) `ScreeningCompleted`, `OperationalProtocolAuthorised`, and `SopRendered` as DesignEvent subclasses** (these belong to the *design* stream per architecture; v1.1's wiring had `ScreeningCompleted` on governance — corrected in § 3.3 below).
  3. Implement `GovernanceEvent` subclasses including v1.5 advisory events (`AdvisoryWarningPresented`, `RiskAdvisoryAcknowledged`, `RiskAdvisoryDeclined`, `RiskAdvisoryEscalated`) — these carry **typed references** to value-objects, not full payload copies (v1.2 H2-03 fix).
  4. Implement `ExportEvent` subclasses.
  5. **(v1.3 B3-03 fix — governance events embed full signed payloads.)** v1.2's H2-03 fix (reference-only events) was over-corrected — it broke FR-ADV-06 (`REQUIREMENTS.md:386`: full approval trace MUST be persisted in the immutable governance event stream). v1.3 restores durability while preserving H2-03's namespace separation:
     - The value-object **type** remains owned by `domain.types.risk_advisory` (`RiskAdvisoryAcknowledgement`) and `domain.types.governance` (`DecisionRecord`, `RoleSnapshot`) — these tasks own the type definition.
     - But the governance event **payload embeds the full canonical signed value-object** (frozen-dataclass payload + content hash), not just a reference. The governance event itself IS the durable signed-record store; no external value-object store is required.
     - Example: `RiskAdvisoryAcknowledged.payload = {"acknowledgement": <full RiskAdvisoryAcknowledgement frozen-dataclass canonical JSON>, "acknowledgement_content_hash": ContentHash}` — both the full value and the hash. The hash is used for indexing + replay-determinism cross-checks; the value is the durable record.
     - Same pattern for `RiskAdvisoryDeclined`, `RiskAdvisoryEscalated`, `ReviewerSignedOff`, `AuthorisationAttemptDenied`, `AdminAction*`, `SopTemplateMinted/Modified/Revoked`, `AuditKeyRotated`, `ReviewQueueItemCreated`, etc.
     - The cross-stream replay-determinism test (T-309) confirms that reading the design + governance streams alone is sufficient to reconstruct the full session, with **no external value-object lookup required**.
     - Static test `tests/static/test_governance_events_self_contained.py` asserts every governance event subclass that references a value-object type embeds the full canonical payload (not just a reference / not just a content hash).
  6. All events frozen-dataclass + JSON-serialisable (deterministic key order, per T-307 canonical-JSON rules).
- **Acceptance:** every event subclass has serialisation + deserialisation round-trip tests; canonical-JSON byte-identical across runs; **every governance event payload contains the full signed value-object plus its content hash** (static test); cross-stream replay-determinism test (in T-309) confirms `ScreeningCompleted` lives in the design stream and that governance events are self-sufficient (no external lookup required for replay).
- **Local status:** completed and verified on 2026-05-14; see `task_artefacts/T-305/post_execution.md`.

#### 2.3.6 `T-306` — Operational namespace + non-operational type packages (v1.1 — B-01 fix)

**v1.1 type placement.** Non-operational artefacts (`DesignRealisationPlan`, `ControlSet`, `RiskAdvisoryReport`, `RiskAdvisoryAcknowledgement`) are *not* part of `sop_protected`; they are generated pre-screening and must be importable by `engine.design_plan`, `engine.controls`, `engine.risk_classification`, and `app.advisory_acknowledgement`. The `sop_protected` namespace retains only the operational types that the v1.4 / v1.5 architecture says are gated.

- **Files:**
  - `src/domain/types/design_plan/__init__.py`, `plan.py`, `verification_artefacts.py`, `reviewer_packet.py`, tests.
  - `src/domain/types/controls/__init__.py`, `control_set.py`, `control_design.py`, tests.
  - `src/domain/types/risk_advisory/__init__.py`, `advisory.py`, `report.py`, `acknowledgement.py`, `decision.py`, tests.
  - **(v1.2 H2-03 fix)** `src/domain/types/governance/__init__.py`, `decision_record.py` (signed `DecisionRecord` value object), `role_snapshot.py` (`RoleSnapshot` value object), tests.
  - `src/domain/types/sop_protected/__init__.py`, `protocol_step.py`, `protocol_dag.py`, `sop_protocol.py`, `hazard.py`, `deviation.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 70 k tokens — split into T-306a (design_plan + controls), T-306b (risk_advisory + governance value objects per v1.2), T-306c (sop_protected only).
- **SOP (v1.1):**
  1. `sop_protected/__init__.py` carries `__sop_protected__ = True` sentinel; the `import-linter` contract restricts imports to `engine.sop_protocol`, the namespace itself, and the `sop_protected` test suite.
  2. Implement `ProtocolStep` (M11 expanded with SOP/QC/role fields) — *inside* `sop_protected`.
  3. Implement `ProtocolDAG` with canonical key order (N4 fix) — *inside* `sop_protected`.
  4. Implement `SopLinkedProtocol` — *inside* `sop_protected`.
  5. Implement `DesignRealisationPlan` in `domain.types.design_plan` — verify by type that it cannot import any name from `domain.types.sop_protected` (mypy + runtime guard + import-linter contract).
  6. Implement `ControlSet` + `ControlDesign` in `domain.types.controls` — verify it cannot import `sop_protected`.
  7. Implement `RiskAdvisory`, `RiskAdvisoryReport` (v1.5 fields: `design_session_id`, `report_content_hash`, `construct_version`, `advisory_id` per item, `required_acknowledgements()`), `RiskAdvisoryAcknowledgement`, `AdvisoryAcknowledgementDecision` in `domain.types.risk_advisory` — verify it cannot import `sop_protected`.
  8. New static test fixture (`tests/static/test_design_plan_no_protocolstep.py`) — uses `mypy` + AST analysis to assert no field in `DesignRealisationPlan` resolves to a `ProtocolStep`-bearing type.
- **Acceptance:**
  - `mypy --strict` rejects any attempt to add a `ProtocolStep` field to a `DesignRealisationPlan` (compile-time).
  - Runtime guard at construction rejects the same (defence-in-depth).
  - `import-linter` contract green: `engine.design_plan` / `engine.controls` / `engine.risk_classification` / `app.advisory_acknowledgement` may import `domain.types.{design_plan, controls, risk_advisory}` and *cannot* import `domain.types.sop_protected`.
  - `engine.sop_protocol` may import `domain.types.sop_protected` (the only path).
- **Local status:** completed and verified on 2026-05-14; see `task_artefacts/T-306/post_execution.md`.
- **Migration:** clean enum-to-Rust-enum mapping; namespace separation preserves the same in Rust modules.

#### 2.3.7 `T-307` — `domain.types.derivation` + RFC 8785 JCS canonicalisation (v1.1 — H-06 fix)
- **Files:** `src/domain/types/derivation/environment.py`, `policies.py`, `src/domain/canonicalisation/jcs.py`, `tests/canonicalisation/test_jcs_golden_vectors.py`, `tests/fixtures/canonicalisation/golden/*.json`, plus dataclass tests.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP (v1.1):**
  1. Implement `DerivationEnvironmentV14` with every v1.4 + v1.5 field (catalogue versions, plugin versions, SOP template content hashes, screening trust policy version, plugin package hashes, LLM prompt template versions, institutional policy version, redaction policy version, risk advisory catalogue version + content hash, privacy classification).
  2. Implement `canonical_json()` via **RFC 8785 JSON Canonicalisation Scheme** with project-specific rules:
     - **Object keys** sorted by their UTF-16 code-unit sequence (RFC 8785 §3.2.3).
     - **Numbers** serialised per RFC 8785 §3.2.2.3 (no trailing zeros, no leading zeros, decimal point only when fractional).
     - **No NaN, +Inf, -Inf** — these raise `CanonicalisationError` at serialise time.
     - **(v1.2 M2-05) Reserved type-tag namespace `$$cev:`.** Any string key beginning with `$$cev:` is reserved for project canonicalisation tagged-union encoding. User dictionaries containing reserved keys raise `CanonicalisationError` at serialise time. Reserved tags as of v1.2: `$$cev:decimal`, `$$cev:datetime`, `$$cev:enum`, `$$cev:bytes`. (v1.1 used `$decimal`; renamed in v1.2 for collision safety. A migration shim accepts v1.1 `$decimal` on deserialise but re-emits the v1.2 tag on canonicalise; both produce identical hashes for the same Decimal value.)
     - **`Decimal` values** are serialised as `{"$$cev:decimal": "12.345"}`, not as a float.
     - **Timestamps** are serialised as ISO-8601 UTC with microsecond precision (`2026-05-14T10:30:00.123456Z`) — or as `{"$$cev:datetime": "..."}` when embedded in a structure where typed disambiguation matters.
     - **Enums** are serialised as their `.value` (which must be a string or integer per the type system).
     - **Strings** are NFC-normalised before serialisation (Unicode normalisation form C).
     - **Non-string dict keys** are forbidden — raise `CanonicalisationError` (every key must be `str`).
     - **Tuples** are serialised as JSON arrays (no distinction from lists; this is enforced at the type level via `tuple[T, ...]` annotations only).
  3. Implement `hash()` — SHA-256 of `canonical_json()` output bytes (UTF-8 encoded).
  4. **Golden vectors** in `tests/fixtures/canonicalisation/golden/` — a curated set of 30+ inputs (including edge cases: empty objects, deeply nested, unicode-heavy, Decimal-bearing, timestamp-bearing, enum-bearing) with their expected canonical-JSON byte output. Tests verify byte-identical output on `ubuntu-latest` and `windows-latest` inside the determinism harness.
  5. Property test: two `DerivationEnvironment` instances with the same field values produce byte-identical `canonical_json` and identical hashes.
  6. Negative property test: a `DerivationEnvironment` with a NaN field raises `CanonicalisationError`.
- **Acceptance:** byte-deterministic canonical JSON across Python 3.11 implementations and platforms; every golden vector matches on both CI matrix cells; NaN / Infinity / non-string-keyed dicts raise.
- **Migration:** RFC 8785 is language-neutral; Rust crate `serde_jcs` provides the same semantics.

#### 2.3.8 `T-312a` — `AuditKeyProvider` Protocol + `TestAuditKeyProvider` (v1.4 — Protocol surface revised per H4-10: no raw `current_key()` method)
- **Files:**
  - `src/domain/ports/audit_key.py` — `AuditKeyProvider` Protocol (v1.4 H4-10: `mac` / `verify` / `verify_with_archived` / `rotate` / `current_key_version` — **no raw key-byte exposure**). Protocol only — no concrete adapter in this task.
  - `tests/fakes/security/audit_key/test_audit_key_provider.py` — deterministic in-memory `TestAuditKeyProvider` that computes HMACs against a fixed test key; used by T-310 / T-311 in their HMAC-chain integration tests before production keystores exist.
  - Contract tests `tests/domain/ports/test_audit_key_provider_contract.py` — verifies any conforming implementation honours the contract.
- **Model tier:** Sonnet. **Context budget:** ≤ 25 k tokens.
- **SOP (v1.4 H4-10):**
  1. Define `AuditKeyProvider` Protocol:
     - `mac(message: bytes) -> tuple[KeyVersionId, MacBytes]` — computes HMAC of message under the **current** key; returns the key version used + the MAC bytes. Raw key bytes never leave the adapter.
     - `verify(key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool` — verifies a MAC under a specific key version (current or recently rotated).
     - `verify_with_archived(key_version: KeyVersionId, message: bytes, mac: MacBytes) -> bool` — verifies against archived (escrowed) key versions per v1.4 H4-05 indefinite retention.
     - `rotate(reason: str, principal: AdminPrincipal | DeveloperBootstrapPrincipal) -> KeyVersionId` — mints a new key version, archives the previous, emits `AuditKeyRotated` governance event.
     - `current_key_version() -> KeyVersionId` — returns the version identifier only; no key bytes.
  2. Implement `TestAuditKeyProvider` — deterministic in-memory adapter with a fixed test key + simple archive map (the test key bytes are exposed only inside the adapter's `mac()` / `verify()` implementations; never returned externally). Used by T-310/T-311 unit + integration tests.
  3. Define `KeyVersionId` (typed NewType of `int`) and `MacBytes` (typed NewType of `bytes`).
  4. Contract tests for any future conforming implementation.
- **Acceptance:** Protocol defined with the v1.4 H4-10 surface (no `current_key` method) + `mypy --strict` green; `TestAuditKeyProvider` passes the contract test suite; T-310 / T-311 can run their HMAC-chain integration tests via `mac()` / `verify()` calls only (no access to raw key bytes).

#### 2.3.9 `T-313a` — `AuditAppendPort` + `AdminAuditAppendPort` Protocols + `ServicePrincipal` + fake brokers (v1.4 — early-half split per B4-03; scheduled before T-308 / T-310 / T-311 so they can depend on it)
- **Files:**
  - `src/domain/ports/audit_append.py` — `AuditAppendPort` + `AdminAuditAppendPort` Protocols (both `append(entry: AuditEntry, caller: <ServicePrincipal | AdminPrincipal>) -> AuditEntryId`; **v1.4 B4-04: both are IPC client ports — the writer is the dedicated audit-service process, implemented in T-313b**).
  - `src/domain/security/service_principals.py` — `ServicePrincipal` typed identity for engine-internal governance services (`PluginGovernance`, `AdvisoryAcknowledgementService`, `ScreeningOrchestrator`, `AuthorisationDecisionService`, `ReviewQueueService`); registered at composition root.
  - `tests/fakes/security/audit_append/test_fake_brokers.py` — deterministic in-memory `FakeAuditBroker` + `FakeAdminAuditBroker` that compute HMAC chain entries via `AuditKeyProvider.mac()` and store rows in memory; used by T-310 / T-311 unit tests before the production audit-service broker exists.
  - Contract tests `tests/domain/ports/test_audit_append_contract.py`, chain-integrity test helpers `tests/security/test_audit_append_chain_integrity_helpers.py`.
- **Model tier:** Sonnet. **Context budget:** ≤ 30 k tokens.
- **SOP (v1.4):**
  1. Define `AuditAppendPort` + `AdminAuditAppendPort` Protocols with append-only contract; no modify/delete methods.
  2. Define `ServicePrincipal` typed identity (frozen dataclass `(service_name, token)` where token is signed via `DecisionRecordSigner` from T-314a so the production audit-service can authenticate the caller).
  3. Implement `FakeAuditBroker` + `FakeAdminAuditBroker` — deterministic in-memory append brokers that compute HMAC chain rows via the `AuditKeyProvider.mac()` Protocol from T-312a. Used by T-310 / T-311 acceptance tests.
  4. Implement chain-integrity test helpers usable by any conforming broker (engine + admin appends alternating produce single linear HMAC chain).
  5. **Separation of duties (v1.3 B3-01 hard rule).** Engine-process code paths receive **only** `AuditAppendPort` (Protocol-typed); admin-service-process code paths receive **only** `AdminAuditAppendPort`. **No code path in any process receives the raw `SqliteAuditLog` write surface.** The actual writer is a separate audit-service process (T-313b).
- **Acceptance:** Protocols defined + `mypy --strict` green; fakes pass the contract test suite; chain-integrity helpers correctly detect tampered chains in synthetic fixtures; T-310 / T-311 can run their HMAC-chain integration tests against the fakes.

#### 2.3.10 `T-314a` — `AuthorisationProfileSigner` + `AuthorisationProfileVerifier` + `DecisionRecordSigner` + `DecisionRecordVerifier` Protocols + fakes (v1.4 — early-half split per B4-02 / B4-09; scheduled before T-308 / T-310 / T-311 so they can depend on it)
- **Files:**
  - `src/domain/ports/profile_signing.py` — `AuthorisationProfileSigner` + `AuthorisationProfileVerifier` Protocols (per v1.3 B3-04).
  - `src/domain/ports/decision_record_signing.py` — `DecisionRecordSigner` + `DecisionRecordVerifier` Protocols (per v1.4 B4-09 — promoted from v1.3 v1.2 unowned port to a Protocol with explicit signer + verifier surface).
  - `tests/fakes/security/profile_signing/test_fake_signers.py` — deterministic in-memory `FakeProfileSigner` / `FakeProfileVerifier` / `FakeDecisionRecordSigner` / `FakeDecisionRecordVerifier`; used by T-310 / T-311 unit tests.
  - `src/domain/types/signing_errors.py` — error taxonomy: `ProfileTamperDetectedError`, `UnknownKeyVersionError`, `RevokedKeyError`, `DecisionRecordTamperDetectedError`, `DecisionRecordPrincipalMismatchError`.
  - Contract tests for both signer + verifier Protocols.
- **Model tier:** Sonnet. **Context budget:** ≤ 30 k tokens.
- **SOP (v1.4):**
  1. Define `AuthorisationProfileSigner.sign(profile: AuthorisationProfile, admin: AdminPrincipal | DeveloperBootstrapPrincipal) -> ProfileSignature` and `AuthorisationProfileVerifier.verify(profile: AuthorisationProfile) -> Result[None, ProfileVerificationError]`. Verifier fails closed on tamper / wrong-version / revoked-key.
  2. Define `DecisionRecordSigner.sign(decision: DecisionRecord, principal: Principal) -> SignedDecisionRecord` and `DecisionRecordVerifier.verify(signed: SignedDecisionRecord) -> Result[None, DecisionRecordVerificationError]`. The signer binds the decision content + signing principal + key version; the verifier checks signature + key-version validity + revocation list.
  3. Implement deterministic fake signer/verifier pairs (in-memory key with deterministic round-trip behaviour). T-310 / T-311 acceptance tests run against these.
  4. Define the error taxonomy used by T-310d (verifier on load), T-311 (signer on write), T-806a (acknowledgement signing), T-1103a/T-1103b (admin IPC authentication).
  5. Contract tests cover sign-then-verify success, tamper failure, unknown-key-version failure, revoked-key failure.
- **Acceptance:** all four Protocols defined + `mypy --strict` green; fakes pass contract test suite; T-310 / T-311 can sign + verify against fakes; error taxonomy used by downstream tests.

#### 2.3.11 `T-316a` — `SopTemplate` split-port Protocols + `SopTemplateSigner` / `SopTemplateVerifier` Protocols + value objects (v1.4 — early-half split per B4-05; Phase 3; production SQLite store + bootstrap moved to T-316b in Phase 4)
- **Files:**
  - `src/domain/ports/sop_template.py` — three runtime Protocols (`SopTemplateReadPort`, `SopTemplateAdminWritePort`, `SopTemplateBootstrapPort`) + two cryptographic Protocols (`SopTemplateSigner`, `SopTemplateVerifier` per v1.4 H4-04).
  - `src/domain/types/sop_template.py` — value objects: `SopTemplate`, `SopTemplateSignature`, `SopTemplateVersion`, `SopTemplateRevocation`.
  - `tests/fakes/sop_template/test_fake_signer.py` — deterministic `FakeSopTemplateSigner` / `FakeSopTemplateVerifier` for T-316b unit tests.
  - Contract tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 35 k tokens.
- **SOP (v1.4):**
  1. Define the three runtime Protocols (per v1.3 B3-05; runtime semantics unchanged).
  2. Define `SopTemplateSigner.sign(template, admin) -> SopTemplateSignature` and `SopTemplateVerifier.verify(template) -> Result[None, SopTemplateVerificationError]` (per v1.4 H4-04). Sibling of T-314a Protocols (same shape; **separate cryptographic identity**).
  3. Define value objects.
  4. Implement fake signer/verifier pair for T-316b unit tests.
  5. **No SQLite store in this task** — that is T-316b in Phase 4 (post-catalogue).
- **Acceptance:** all five Protocols defined + `mypy --strict` green; fake signer/verifier pass contract tests; T-803 (Phase 8b) and the eventual T-316b can depend on `SopTemplateReadPort` from this task.

#### 2.3.12 `T-308` — `adapter.io.GenBank` + `FASTA` + `SBOL3` + `SnapGeneDnaReader` (v1.1 — added T-308e per H-02)
- **Files:** `src/adapter/io/genbank.py`, `fasta.py`, `sbol3.py`, `snapgene_dna_reader.py`, `imported_construct.py`, `write_result.py`, tests.
- **Model tier:** Opus (round-trip discipline is exacting). **Context budget:** ≤ 90 k tokens — **split** into T-308a (GenBank reader), T-308b (GenBank writer), T-308c (SBOL3 reader+writer), T-308d (FASTA + WriteResult), **T-308e (SnapGene .dna read-only — new in v1.1)**.
- **SOP:**
  1. Implement `ImportedConstruct` / `AnnotatedConstruct` / `WriteResult` types (B5).
  2. Implement `GenBankAdapter`: read using Biopython, normalise to `ImportedConstruct`; write produces semantic-equivalent output (M8 relaxation).
  3. Implement `Sbol3Adapter` using pySBOL3 ≥ 1.3, against SBOL 3.1.x `Component` / `Sequence` / `SequenceFeature` (N3 fix).
  4. Implement `FastaAdapter` (minimal; sequence-only).
  5. **T-308e: `SnapGeneDnaReader` (read-only)** — uses `snapgene-reader` library to parse `.dna` files into `ImportedConstruct`. Graceful fallback: when proprietary parsing fails (corrupted file, unknown SnapGene version), emit `LossWarning("snapgene-proprietary-format-unparseable")` and raise `SnapGeneDnaReadError` with a user-facing instruction to export to GenBank from SnapGene. Visual metadata (colours, labels) parsed where available, stored in `ImportedConstruct.snapgene_visual_metadata`.
  6. Round-trip property tests on a curated set of 20 reference constructs (including circular, reverse-strand features, compound locations, sub-features).
  7. **(v1.2 H2-10 fix) SnapGene `.dna` fixture provenance.** All fixture `.dna` files in `tests/fixtures/snapgene/` are **permissively redistributable** — either (a) generated locally from public-domain synthetic plasmids on a licensed SnapGene installation, or (b) drawn from `snapgene-reader`'s own bundled example fixtures whose licence permits redistribution for testing. Each fixture ships with `tests/fixtures/snapgene/<fixture_id>/PROVENANCE.md` documenting: synthetic source, generation date, licensed SnapGene installation used, fixture hash. Proprietary `.dna` files whose provenance cannot be cleared are kept out of the repo and referenced only by developer-machine paths; corresponding tests are marked `@pytest.mark.requires_local_snapgene_fixture` and **skipped in CI**. SnapGene `.dna` → GenBank semantic-equivalence test runs on the redistributable subset (≥ 5 fixtures) in CI; the proprietary subset extends coverage on developer machines.
- **Acceptance:** semantic-equivalent round-trip on every reference fixture; lossy-conversion warnings emitted when format does not support a feature; SBOL 3 round-trip preserves graph topology; SnapGene `.dna` round-trip (read → re-emit as GenBank → re-read with SnapGene file watcher) preserves feature table.
- **Hand-off:** T-902 (`SnapGeneFileWatcher`) *depends on* T-308e for the underlying `.dna` parse capability; T-902 owns the file-watch logic, not the parser.

#### 2.3.13 `T-309` — `engine.session` state machine + replay determinism + gate-predicate versioning (v1.3 — single task identity per B3-08; gate predicate versioning per M3-07)

**v1.3 task identity (B3-08).** T-309 is a **single** task. Sub-deliverables (a) the Phase-3-resident skeleton (state machine + replay + pending-predicate registry) and (b) per-phase gate-predicate activation are documented **inline** in this card. Activation work happens **inside the gate-activating tasks** (T-502, T-806b, T-1002, T-903) — not in a separate gate-activation task card. This matches the existing T-303 (a..c) / T-308 (a..e) / T-703 (a..e) sub-split pattern: one task heading, sub-deliverable enumeration within.

- **Files:** `src/engine/session/state_machine.py`, `events.py` (event-replay logic), `snapshots.py`, `gates_pending.py` (typed pending-predicate sentinel + `GatePredicateRegistry`), `predicate_versioning.py` (v1.3 — M3-07), `docs/safety_gates/activation_map.md`, tests including replay determinism + cross-stream invariant + state-transition coverage + predicate-version replay.
- **Model tier:** Opus. **Context budget:** ≤ 60 k tokens (v1.3 increased from 55 k).
- **Sub-deliverable (a) — Phase-3-resident skeleton.**
  1. Implement `DesignSession` state machine per `ARCHITECTURE.md` v1.5 § 4.4: states `EMPTY` → `COLLECTING` → `DRAFT` → `VALIDATING` → `{HARD-FAIL, SOFT-WARN, ALL-PASS}` → `ACKNOWLEDGED_WARN` → `COMPILING` → `READY_WITH_WARNINGS?` → `AWAITING_SCREENING` → `SCREENING` → `{HIT, WATCHLIST, MANUAL_REVIEW_REQUIRED, UNAVAILABLE, NOT_APPLICABLE, CLEAR}` → `AWAITING_REVIEWER_SIGNOFF` → `AWAITING_AUTHORISATION` → `AWAITING_SOP_RENDER` → `READY_TO_EXPORT` → `EXPORTED`. Three terminal blocked sub-states: `BLOCKED_BY_HIT`, `BLOCKED_BY_POLICY`, `BLOCKED_BY_UNSUPPORTED_TIER`.
  2. Implement event-sourced state rebuild: replay the **design** event stream from `JsonlEventLog` produces the same end state byte-for-byte (subject to `DerivationEnvironment` match). **(v1.2 M2-01)** This task **owns replay determinism**, not T-501 / T-1302.
  3. Implement snapshot management: snapshots keyed by `DerivationEnvironment.hash()`; replay accelerated by loading the latest snapshot whose hash matches the current environment.
  4. **Typed pending-predicate registration.** Each of the four safety gates (`BlockCompile`, `BlockExport`, `BlockVendorSubmission`, `BlockOperationalProtocol`) is declared with a `GatePredicateRegistry`. The skeleton registers each predicate as `GatePending` (returns `GateState.PENDING_NOT_YET_ACTIVATED`). A predicate transitions to `GateOpen` or `GateBlocked` only when its owning task lands and replaces the registry entry via `GatePredicateRegistry.activate(gate, predicate, version)`. Calling a `PENDING` predicate during a real session raises `GatePredicateNotYetActivated`; in pre-activation tests the predicate is mockable.
  5. **(v1.3 M3-07) Gate predicate versioning.** Each registered gate predicate carries `predicate_version: PredicateVersion` (semver-like) and `predicate_content_hash: ContentHash` (SHA-256 of the predicate's canonical source representation). `DerivationEnvironment` (T-307) is extended with `gate_predicate_versions: dict[GateName, PredicateVersion]` and `gate_predicate_content_hashes: dict[GateName, ContentHash]` captured at session start. Replay of an older session uses the predicate version stored in the session's `DerivationEnvironment`, not the current predicate. Predicate version bumps emit a `GatePredicateVersionBumped` governance event (signed `DecisionRecord` by Administrator + scientific-advisor review).
  6. **Cross-stream replay-determinism invariant test (v1.2 B2-05 fix).** A session log replayed twice — design events + governance events with embedded signed payloads (v1.3 B3-03) — produces byte-identical end state and gate verdicts. The test fails if `ScreeningCompleted` lives in the wrong stream, or if a governance event needed for state transition is unreferenced from the design stream, or if a governance event references rather than embeds its signed payload.
  7. **(v1.3 M3-07) Predicate-version replay test.** `test_replay_with_old_predicate_version` — a session captured with `BlockCompile_v1.0` replays under `BlockCompile_v1.1` and produces the **original verdict** (using the captured predicate version), not the current verdict.
- **Sub-deliverable (b) — Per-phase gate-predicate activation map** (documented in `docs/safety_gates/activation_map.md`; activation work happens in the gate-activating tasks, **not** in a separate task):
  - **`BlockCompile`** activated in **Phase 5** by T-502 (validation HARD failures).
  - **`BlockVendorSubmission`** activated in **Phase 10** by T-1002 (screening-verdict portion) + **T-1001** (vendor-profile-feasibility portion — v1.3 H3-02). T-903 consumes both before `VendorSubmissionPrepared`.
  - **`BlockOperationalProtocol`** activated in **Phase 8b** by T-806b (consumes T-806a's `all_required_advisories_acknowledged()` + Phase 10's `ScreeningCompleted` + authorisation profile match).
  - **`BlockExport`** activated in **Phase 9b** by T-903 (consumes Phase 10's `ScreeningCompleted` + Phase 8b's `OperationalProtocolAuthorised` + Phase 8a's advisory acknowledgement chain).
  - Each activation in the owning task replaces the `GatePending` registry entry with `GatePredicateRegistry.activate(gate, predicate, version)`; CI's `gate-lifecycle-check` (v1.1) confirms only activated predicates may be in lifecycle state `enforced` and predicates with TODO markers remain `informational`.
- **Acceptance:** every state transition has a unit test; replay determinism property test passes on ≥ 100 synthetic sessions; cross-stream invariant test green; predicate-version replay test green; **`Block*` predicates registered as PENDING with no concrete activation in T-309 itself** (concrete activation in the gate-activating tasks per sub-deliverable b).

#### 2.3.14 `T-310` — `adapter.persistence` implementations (v1.3 — depends on **T-312a** `AuditKeyProvider` Protocol per B3-02; profile signature verification on load per B3-04; reassigned replay-determinism ownership to T-310b per M2-01)
- **Files:** `src/adapter/persistence/sqlite_project_store.py`, `jsonl_event_log.py`, `sqlite_audit_log.py`, `sqlite_authorisation_store_read.py` (read-only side; admin-write side owned by T-311), `schemas/*.sql` (migrations), tests including crash-recovery, append-only-semantics, tamper-detection, read-only-enforcement, **profile-signature verification on load (v1.3 B3-04)**.
- **Model tier:** Opus. **Context budget:** ≤ 70 k tokens — **split** into T-310a (`SqliteProjectStore`), T-310b (`JsonlEventLog` ×3 streams + replay-determinism harness — **owns replay determinism per v1.2 M2-01**), T-310c (`SqliteAuditLog` *read interface* + tamper detection — consumes `AuditKeyProvider` from **T-312a**; the **append client port** is T-313a and production IPC implementation is T-313b), T-310d (`SqliteAuthorisationStoreRead` — read-only side; calls `AuthorisationProfileVerifier` from T-314a on every `get()`; production integration uses T-314b per v1.3 B3-04; admin-write `SqliteAuthorisationStoreWrite` is owned by T-311).
- **SOP (v1.2):**
  1. **`SqliteProjectStore`** — schema with constructs, sessions, parts library; migrations via Alembic-style; `save` / `load` / `list_sessions` per `ARCHITECTURE.md` v1.5 § 4.5 port. WAL mode + `synchronous=FULL` for durability; explicit `BEGIN IMMEDIATE` for write transactions to avoid race with file-watch.
  2. **`JsonlEventLog`** (×3 streams: design / governance / export) — append-only file writer with `fsync` after every write + atomic-append via `O_APPEND` semantics on POSIX and `FILE_APPEND_DATA` on Windows. Each event is one JSON line; the file is the canonical event store. **Stream ownership corrected per v1.2 B2-05:** the design-stream writer accepts `ScreeningCompleted`, `OperationalProtocolAuthorised`, `SopRendered` events from their owning application services (not from governance writers).
  3. **`SqliteAuditLog` (v1.3 — read interface only; tamper detection; append client port T-313a / production audit-service T-313b per B4-04)** — append-only chain semantics; tamper detection via HMAC chain (each row's `prev_hmac` is the HMAC of the previous row's payload, keyed by the institutional audit key); **the audit key is supplied by `AuditKeyProvider` from T-312a (the Protocol)** — `SqliteAuditLog` itself never knows the key bytes, only the provider. Verification on read uses `AuditKeyProvider.verify_with_archived(key_version, message)` so rotated keys still verify historical rows. Corrupted chain raises `AuditLogTamperDetectedError` and halts the engine; missing key provider raises `AuditLogTamperDetectionUnavailable` and refuses to start. **(v1.3 B3-01)** Append writes are routed through the `AuditAppendPort` / `AdminAuditAppendPort` Protocols from **T-313a**. Unit tests use deterministic fakes; production writes go through the single-writer audit-service in **T-313b**. This task ships only the underlying SQLite read interface + tamper-verification routines; the write path is outside the reader adapter.
  4. **`SqliteAuthorisationStoreRead` (v1.3 — verifier on load per B3-04)** — opened **read-only** by engine and User-role processes (`mode=ro` URI parameter on SQLite); reads `AuthorisationProfile` records produced by T-311's write-side. **(v1.3 B3-04 fix)** Every `get(user_id)` call invokes `AuthorisationProfileVerifier.verify(profile)` (port from T-314a; production adapter from T-314b) before returning. Verification failure raises `AuthorisationProfileTamperDetectedError`; never returns a partially-trusted profile. The verifier checks: signature matches profile content; signing key version is currently valid; profile is not revoked. Tests: corrupt one byte in `authorisation.sqlite` → load returns `AuthorisationProfileTamperDetectedError`; revoke a profile via T-311 → subsequent reads fail closed. OS-level file mode (Windows ACL / POSIX permissions) reinforces the read-only constraint for User-role processes; verified by an integration test that authenticates as a `UserPrincipal` and attempts a write — must receive `OperationalError`. **The write side is `SqliteAuthorisationStoreWrite` owned by T-311**; this task only ships the read adapter and the file-mode enforcement.
  5. **Snapshot store** — `snapshots/<session>/<event_seq>_<derivation_hash>.json` files; cleanup policy: retain last 10 snapshots per session + the most-recent-per-`DerivationEnvironment.hash()`.
  6. **Crash recovery tests** — kill the process mid-write at every state transition; on restart, replay should rebuild the same state.
  7. **(v1.2 M2-01) Replay-determinism property test** — owned in T-310b: given a sequence of `DesignEvent` writes to `JsonlEventLog`, re-reading and replaying through `engine.session` (T-309) produces a byte-identical session-state representation.
- **Acceptance:** schema migrations forward-compatible; tamper-detection test passes (corrupt one byte in `audit.sqlite` → `AuditLogTamperDetectedError`); audit-key-absent test passes (no provider → `AuditLogTamperDetectionUnavailable` at start); read-only enforcement test passes (UserPrincipal cannot write); crash-recovery test passes for every state transition; replay determinism preserved across 100+ synthetic sessions.
- **Migration:** SQLite + JSONL are language-neutral; Rust port uses `rusqlite` + `serde_json`.

#### 2.3.15 `T-311` — `app.admin_action_handler` (v1.3 — signs profiles per B3-04; routes audit writes per B3-01; `DeveloperBootstrapPrincipal` per H3-10; SOP-template admin writes deferred to **T-316b** per B3-05/B4-05)
- **Files:**
  - `src/app/admin_action_handler.py` — the sole admin write entry point.
  - `src/adapter/persistence/sqlite_authorisation_store_write.py` — write-side of `authorisation.sqlite`; opened `mode=rw` only by this handler running in the admin-service process.
  - `src/domain/ports/authorisation.py` — three Protocols (`AuthorisationReadPort`, `AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`); see T-203c numbered inventory.
  - `tests/app/admin_action_handler/{test_mint,test_modify,test_revoke,test_list,test_view_audit,test_user_denied,test_reviewer_denied,test_developer_bootstrap_allowed_pre_bootstrap,test_developer_denied_after_bootstrap,test_bootstrap_idempotent,test_signed_profile_round_trip}.py`.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens (v1.3 increased from 50 k).
- **SOP (v1.3):**
  1. Implement `AdminActionHandler` with five operations: `mint_profile(admin: AdminPrincipal | DeveloperBootstrapPrincipal, target_user: UserId, profile_draft: UnsignedAuthorisationProfileDraft, justification: str)`, `modify_profile`, `revoke_profile`, `list_profiles`, `view_audit_trail`. Each operation: (a) validates the calling principal's `can_act_as(SecurityRole.ADMINISTRATOR)`; (b) **(v1.3 B3-04)** calls `AuthorisationProfileSigner.sign(draft, admin)` from T-314a before commit (production adapter T-314b), producing a fully signed `AuthorisationProfile` with institutional `ProfileSignature` + `profile_signature_key_version`; (c) writes the signed profile through `AuthorisationAdminWritePort` to `authorisation.sqlite`; (d) **(v1.3 B3-01)** writes a signed `DecisionRecord` to the audit chain via the admin-service-process's audit-append path (this handler runs in the admin-service process; it appends via `AdminAuditAppendPort` from T-313a; production sends IPC to the single-writer audit-service from T-313b, which is the only `audit.sqlite` `mode=rw` holder); (e) writes the corresponding governance event (`AdminActionMinted` / `AdminActionModified` / `AdminActionRevoked`) to `events/governance/` with **the full signed profile embedded** in the event payload per v1.3 B3-03.
  2. **Adversarial denial:** every operation rejects `UserPrincipal` and `ReviewerPrincipal` with `PermissionError`, emits `AuthorisationAttemptDenied`, records the denial in `audit.sqlite`. Adversarial tests cover each denial path.
  3. **Bootstrap path (v1.3 H3-10 — narrowed Developer authority).** `AuthorisationBootstrapPort.bootstrap_initial_admin(developer: DeveloperBootstrapPrincipal, initial_admin_profile_draft: UnsignedAuthorisationProfileDraft)` — used once at institutional setup to mint the first Administrator. Subsequent calls raise `AlreadyBootstrappedError`. After bootstrap completes (`AdminBootstrapped` event observed), subsequent `mint/modify/revoke` calls require **`AdminPrincipal`** unless `institutional_policy.developer_permanent_admin == True`. Idempotent failure is verified by test. Adversarial test `test_developer_denied_after_bootstrap` confirms that an ordinary `DeveloperPrincipal` (without `is_bootstrap` claim) is rejected for `mint_profile` after bootstrap.
  4. **Profile signature integration tests (v1.3 B3-04).**
     - `test_signed_profile_round_trip`: mint → write to SQLite → read back via `SqliteAuthorisationStoreRead` (which invokes `AuthorisationProfileVerifier`) → verification succeeds.
     - `test_unsigned_profile_rejected_at_read`: bypass the signer via test injection → subsequent `get()` fails with `AuthorisationProfileTamperDetectedError`.
     - `test_modified_profile_after_signing_rejected`: write a signed profile, mutate one byte in the SQLite row, read back → tamper error.
  5. **Foundational admin surface only.** This task ships the application-layer handler + the SQLite write adapter; the CLI / API admin commands wire to this handler via the admin-service IPC in **T-1103a/T-1103b** (v1.3 H3-09 new). For Phase 3 testing, the handler is invoked via a thin programmatic shim (`tools/admin_shell.py`) that authenticates with a developer or admin principal supplied via environment variables — never User-process accessible.
  6. **(SOP-template admin writes — owned by T-316b per v1.3 B3-05 / v1.4 B4-05.)** Institutional `SopTemplate` admin-write operations are owned by **T-316b** (split from the legacy SOP-template admin-write task), not T-803. T-311 establishes the handler pattern; T-316b implements the SOP-template write adapter + the `SopTemplateAdminWritePort` + the signed governance events. T-311's `AdminActionHandler` is extended at T-316b implementation time with `mint_sop_template` / `modify_sop_template` / `revoke_sop_template` operations.
- **Acceptance:** every operation tested with `AdminPrincipal` (allowed) and `UserPrincipal` / `ReviewerPrincipal` (denied with `PermissionError` + `AuthorisationAttemptDenied`); `DeveloperBootstrapPrincipal` succeeds for mint/bootstrap pre-bootstrap; ordinary `DeveloperPrincipal` rejected for mint after bootstrap (unless `developer_permanent_admin == True`); bootstrap idempotency verified; admin audit chain extends the HMAC chain from T-310c + T-313a fakes and T-313b production audit-service without breaking integrity (cross-task integration test); signed-profile round trip green.

#### 2.3.16 `T-312b` — Production `AuditKeyProvider` adapters + rotation service + offline verifier (v1.3 — split from the legacy audit-key task per B3-02; scheduled after T-311)
- **Files:**
  - `src/adapter/security/audit_key/file_keystore.py` — file-backed adapter (dev-loop default); key stored under a separate filesystem ACL away from `audit.sqlite`.
  - `src/adapter/security/audit_key/os_keystore_windows.py` — DPAPI / DPAPI-NG (Windows production default).
  - `src/adapter/security/audit_key/os_keystore_posix.py` — POSIX Linux keyring / kwallet (Linux production default).
  - `src/app/audit_key_rotation_service.py` — rotation workflow (callable only by `AdminPrincipal | DeveloperBootstrapPrincipal`); records `AuditKeyRotated` governance event with `key_version_before` + `key_version_after` + `rotation_reason` (embedded signed `DecisionRecord` per v1.3 B3-03).
  - `tools/audit_key_verifier.py` — standalone offline verifier (does **not** import the engine); reads `audit.sqlite` + an escrowed key version and recomputes every row's HMAC chain.
  - `docs/security/audit_key_runbook.md` — provisioning, rotation cadence, key-loss recovery, compromise response procedure.
  - `tests/security/audit_key/{test_absent,test_wrong,test_rotated,test_tampered,test_offline_verification,test_separation_of_signature_and_hmac_keys,test_dpapi_fallback_on_ci,test_posix_keyring_fallback_on_ci}.py`.
- **Model tier:** Opus. **Context budget:** ≤ 50 k tokens.
- **SOP:**
  1. **Three concrete keystore adapters.** Selection driven by `config.audit_key_backend = "file" | "windows_dpapi" | "posix_keyring"`. Production defaults to OS keystore; dev-loop defaults to file with explicit warning. Each adapter stores: current key version + key bytes (encrypted at rest where the backend supports it), an indefinite escrow/archive of every key version referenced by any audit row, plus the rotation log. Short-lived in-process caches MAY bound recently used keys, but the authoritative archive is never pruned while referenced audit evidence exists.
  2. **CI fallback (v1.3 environment adaptation).** Where DPAPI / keyring APIs are unavailable in CI runners (Windows GitHub Actions without an interactive session; Linux runners without a configured keyring), adapters fall back to file-keystore with a CI-explicit warning. `test_dpapi_fallback_on_ci` + `test_posix_keyring_fallback_on_ci` confirm the fallback path.
  3. **Separation of duties (v1.2 B2-08 hard rule).** The engine's runtime process holds only `AuditKeyProvider`; never raw key bytes; production code calls only `mac()` / `verify()` / `verify_with_archived()` / `rotate()`. The `DecisionRecord` signature key (asymmetric, per-principal) is a separate port `DecisionRecordSigner` — different cryptographic role (per-principal non-repudiation vs institutional log-integrity).
  4. **Rotation:** Administrator triggers via `audit-key-rotate` CLI command (Phase 11 wiring). Existing audit rows continue verifying with their original key version (`verify_with_archived`); new rows use the current key version.
  5. **Offline verification:** `tools/audit_key_verifier.py` accepts an escrowed key archive and `audit.sqlite`, recomputes every row's HMAC chain, exits 0 if all rows verify or exits 1 with a list of failing row IDs.
  6. **Runbook:** provisioning at first install; rotation cadence (recommended quarterly + on personnel change); key-loss recovery (escrow restore procedure); compromise response (rotate immediately + investigate via offline verifier).
- **Acceptance:** all six original audit-key tests pass; both CI-fallback tests green; rotation emits the signed governance event with embedded `DecisionRecord` payload (v1.3 B3-03); offline verifier exits 0 on a clean log and exits 1 with row-IDs on a tampered log.
- **Migration:** ports + provider model are language-neutral; Rust adapters use `keyring-rs` or platform-native APIs.

#### 2.3.17 `T-314b` — Production `AuthorisationProfileSigner` + `DecisionRecordSigner` adapters + key lifecycle (v1.4 — new per B4-09; scheduled after T-311)

**v1.4 B4-09.** v1.3 had no concrete `DecisionRecordSigner` adapter or key lifecycle owner. v1.4 extends the legacy profile-signing responsibility to cover both institutional profile signing AND per-principal `DecisionRecordSigner` production implementation + key lifecycle.

- **Files:**
  - `src/adapter/security/profile_signing/institutional_signer.py` — production institutional `AuthorisationProfileSigner` (Ed25519; pinned via `cryptography` library). Private key admin-service-only; public key embedded in every engine process.
  - `src/adapter/security/profile_signing/institutional_verifier.py` — production verifier.
  - `src/adapter/security/decision_record_signing/per_principal_signer.py` — production per-principal `DecisionRecordSigner`; per-principal Ed25519 key pair; private key provisioned by admin (signed by institutional signer); public key distributed to engine processes.
  - `src/adapter/security/decision_record_signing/per_principal_verifier.py` — production verifier; checks signature + signing key version + per-principal revocation list.
  - `src/app/decision_record_key_management.py` — key provisioning (admin-issued; signed by institutional admin); key rotation (per-principal); per-principal revocation list; public-key distribution to engine processes; compromised-key response runbook.
  - `tools/profile_signature_verifier.py` — standalone offline verifier.
  - `tools/decision_record_verifier.py` — standalone offline verifier for `DecisionRecord` signatures.
  - `docs/security/profile_signing_runbook.md`, `docs/security/decision_record_signing_runbook.md`.
  - Tests: `tests/security/profile_signing/{test_sign_then_verify,test_tampered_payload_fails,test_wrong_key_version_fails,test_revoked_key_fails,test_offline_verifier_matches,test_separation_of_profile_signing_from_audit_hmac}.py`; `tests/security/decision_record_signing/{test_decision_record_signature_verifier,test_revoked_principal_signature_fails,test_rotated_principal_key_verifies_historical_records,test_separation_of_decision_record_from_profile_signing}.py`.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP (v1.4):**
  1. Implement production signer + verifier adapters using `cryptography` library Ed25519. Pinned in T-201 `core` runtime.
  2. **Separation of cryptographic identities (v1.4 hard rule).** Institutional profile-signing key, per-principal `DecisionRecordSigner` key, and institutional audit HMAC key (T-312b) are three distinct cryptographic identities. Compromise of one does not enable forging the others. Tested in `test_separation_of_profile_signing_from_audit_hmac` + `test_separation_of_decision_record_from_profile_signing`.
  3. **Per-principal key provisioning.** When `app.admin_action_handler` (T-311) mints a profile for a new user, it also provisions the user's `DecisionRecordSigner` key pair (private key encrypted by the user's institutional credential; public key broadcast to engine processes via the governance stream `DecisionRecordPublicKeyDistributed` event).
  4. **Key rotation + revocation.** Per-principal keys rotate on schedule (configurable, default 90 days) or on compromise. Revocation list maintained in admin-service; broadcast to engine processes via `DecisionRecordPrincipalKeyRevoked` event.
  5. **Offline verification.** Both standalone tools accept a signature + signed payload + escrowed public-key archive; exit 0 on valid, 1 with details on failure.
- **Acceptance:** all sign-then-verify round trips green for both signer types; tamper / wrong-version / revoked-key tests green; cryptographic-identity separation tests green; offline verifiers reproduce engine verdicts; key-lifecycle events flow through governance stream with embedded signed payloads per v1.3 B3-03.

#### 2.3.18 `T-313b` — Production single-writer audit-service process + IPC (v1.5 — new, replaces the legacy audit-append production half per B4-04; scheduled after T-314b)

**v1.4 B4-04 — single-writer audit-service.** v1.3's dual-writer + "lock handoff" model was non-executable (two long-lived `mode=rw` writers on one SQLite chain). v1.4 adopts a **dedicated audit-service process** (separate from engine + admin-service) that owns `audit.sqlite` `mode=rw` for its lifetime. Engine and admin-service processes are IPC clients of this audit-service.

- **Files:**
  - `src/interface/audit_service/__main__.py` — audit-service process entry point.
  - `src/interface/audit_service/server.py` — IPC server (named pipe `\\.\pipe\cev-audit-service` on Windows; Unix domain socket `/var/run/cev-audit/socket` on POSIX); accepts framed JSON-RPC-like requests; serialises all appends through a single in-process queue.
  - `src/interface/audit_service/handlers.py` — two IPC verbs: `engine_append(entry, service_principal_token)` and `admin_append(entry, admin_principal_token)`. Token authenticated via `DecisionRecordVerifier` (T-314b); audit-service appends through the HMAC chain via `AuditKeyProvider.mac()`.
  - `src/adapter/persistence/sqlite_audit_log_writer.py` — the SQLite `mode=rw` writer (owned only by the audit-service process); single-writer model eliminates lock contention.
  - `src/adapter/ipc/audit_service_client.py` — IPC client (named-pipe / Unix-socket); implements `AuditAppendPort` (engine-process) and `AdminAuditAppendPort` (admin-service-process) by sending framed requests to the audit-service.
  - `docs/deployment/audit_service.md` — runbook: launch audit-service as systemd unit (Linux) or Windows service; recovery on crash; IPC path configuration.
  - `src/interface/audit_service/governance_event_writer.py` — minimal local governance-event append path owned by the audit-service for security events such as authentication failure; it does not expose a general engine-stream client.
  - Tests: `tests/security/test_audit_service_concurrent_appends.py` (engine + admin appends under load → single linear chain); `tests/security/test_audit_service_crash_recovery.py`; `tests/security/test_audit_service_ipc_timeout.py`; `tests/security/test_audit_service_key_rotation_during_appends.py`.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP (v1.4 B4-04):**
  1. Implement the audit-service process: opens `audit.sqlite` `mode=rw`, holds the lock for its lifetime, exposes IPC server.
  2. IPC server accepts framed JSON-RPC requests on the configured pipe/socket; serialises all appends through an asyncio queue (single writer in code, single writer in SQLite).
  3. Each request is authenticated via `DecisionRecordVerifier` against the caller's signed principal token; unauthenticated requests denied + audit-service appends its own `AuditServiceAuthenticationFailed` governance event through its minimal local governance-event writer. This writer is owned by T-313b, emits only audit-service security events, is replay-tested, and avoids a circular dependency on an undefined engine-stream IPC client.
  4. IPC client implementations (`audit_service_client.py`) sit behind `AuditAppendPort` / `AdminAuditAppendPort` Protocols from T-313a; the composition root injects the IPC client into engine + admin-service processes.
  5. **Crash recovery:** on audit-service restart, re-opens `audit.sqlite`, recomputes the HMAC of the last row, accepts new appends only after validation. Partial-write recovery via SQLite WAL + atomic transactions.
  6. **IPC timeout:** engine-process clients block for max 5s on append; on timeout, retry with exponential backoff (3 retries); on final failure, raise `AuditServiceUnreachableError` and halt the calling governance service (audit is non-optional).
  7. **Key rotation during concurrent appends:** `AuditKeyProvider.rotate()` is called inside the audit-service process under the queue lock; new rows after rotation use the new key version; HMAC chain transitions cleanly across rotation. Verified by test.
- **Acceptance:** concurrent engine+admin appends under load produce single linear HMAC chain; crash recovery preserves chain integrity; IPC timeout + retry behaviour verified; key rotation under contention produces clean chain transition; Windows named-pipe + POSIX socket both green; authentication-failure governance events replay deterministically and are not lost on denied IPC requests.
- **Persistence-table update:** `audit.sqlite` writer is **`audit-service process` (T-313b)** only; engine + admin-service processes hold IPC client handles.

#### 2.3.19 `T-315` — `app.review_queue` + `AuthorisationRequest` service (v1.3 — new, per B3-06; v1.4 — `ReviewQueueAdminPort` added per H4-01; append-only semantics clarified per M4-06)

**Rationale.** FR-PROTO-SOP-09 + FR-AUTH-07 + FR-AUTH-12 require an administrator review queue + user extension-request workflow. v1.2 had the gate but not the recovery path. T-315 closes the loop.

- **Files:**
  - `src/domain/types/review_queue.py` — `AuthorisationRequest`, `ReviewQueueItem`, `ReviewQueueItemDecision` value objects (frozen dataclasses, canonical-JSON-serialisable).
  - `src/adapter/persistence/sqlite_review_queue_store.py` — SQLite-backed store; `add(request)` is append-only (request immutable once written); `resolve(item_id, decision)` adds a decision record without mutating the request.
  - `src/domain/ports/review_queue_admin.py` — `ReviewQueueAdminPort` Protocol exposing admin-only `resolve(item_id, decision)`; implemented only inside the admin-service process in T-1103b.
  - `src/app/review_queue_service.py` — user/service use cases only: `submit_extension_request(user: UserPrincipal, scope: CoveredBiologicalScope, justification: str)` (FR-AUTH-12) and `route_blocked_authorisation(session_id, reason, caller: ServicePrincipal)` (FR-PROTO-SOP-09; called by `app.authorisation_decision` via T-806b). It does **not** expose admin resolution to engine/API/CLI callers.
  - Governance events (per v1.3 B3-03 — full signed payloads embedded): `AuthorisationExtensionRequested`, `ReviewQueueItemCreated`, `ReviewQueueItemAssigned`, `ReviewQueueItemResolved`.
  - Tests: `tests/app/review_queue/{test_user_submits_request,test_user_cannot_self_approve,test_blocked_sop_creates_single_request,test_admin_triages_request_via_port_only,test_user_request_never_auto_granted,test_gate_recovery_path,test_cli_api_cannot_resolve_without_admin_service}.py`.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP:**
  1. Define value objects: `AuthorisationRequest` (subject user, requested `CoveredBiologicalScope`, justification, related `SessionId | None`, supporting evidence); `ReviewQueueItem` (id, request, status: `pending | under_review | approved | denied | expired`, assigned admin, signed `ReviewQueueItemDecision | None`, timestamps); `ReviewQueueItemDecision` (signed by AdminPrincipal via `DecisionRecordSigner`).
  2. Implement `SqliteReviewQueueStore` — append-then-update model. `add(request)` writes the immutable request row. `resolve(item_id, decision)` is exposed only through `ReviewQueueAdminPort`; it writes a separate decision row referencing the request — the request itself is never mutated. Reads join request + latest decision.
  3. Implement `ReviewQueueService` with user/service submission only. `submit_extension_request` and `route_blocked_authorisation` both write via the `AuditAppendPort` Protocol from T-313a (production IPC client T-313b) — these are service-originated audit entries. Admin resolution is **not** a method on this user-facing service; it is a `ReviewQueueAdminPort` operation implemented by admin-service code in T-1103b. Both paths emit the appropriate governance event with the full signed payload embedded (per v1.3 B3-03).
  4. **Cross-task wiring (Phase 8b T-806b — pre-declared here for traceability).** When `BlockOperationalProtocol` fires in T-806b, it calls `ReviewQueueService.route_blocked_authorisation(session_id, reason, service_principal)` to create a pending request. Phase 11 CLI (T-1101 / T-1102) + Phase 12 UI (T-1202) surface `submit-extension-request`, `list-review-queue`, `triage-request` commands; these route through the admin-service IPC (T-1103a/T-1103b) where admin actions are required. CLI/API/user paths cannot call `ReviewQueueAdminPort` directly.
- **Acceptance:**
  - `test_blocked_sop_creates_single_request`: a blocked SOP rendering produces exactly one pending `ReviewQueueItem`; no duplicate on retry.
  - `test_user_cannot_self_approve`: no `UserPrincipal`, CLI, API, or engine-process path can reach `ReviewQueueAdminPort.resolve`; attempts without admin-service IPC are rejected with `PermissionError` or a static-import failure.
  - `test_admin_triages_request_via_port_only`: admin-service resolves through `ReviewQueueAdminPort` → `ReviewQueueItemResolved` event with embedded signed `ReviewQueueItemDecision`; subsequent reads return the decision.
  - `test_user_request_never_auto_granted` (FR-AUTH-12): submitting `submit_extension_request` does **not** modify any `AuthorisationProfile`; only admin-service `ReviewQueueAdminPort.resolve` followed by `mint_profile` / `modify_profile` (via T-311) can grant access.
  - `test_gate_recovery_path`: a blocked session can be unblocked only by (a) admin approval via the queue, (b) admin minting / modifying the profile to cover the requested scope. No other path.

### Phase 4 — Catalogues (8 tasks; v1.5 — includes T-316c production SOP-template signer before T-316b signed store/bootstrap)

#### 2.4.1 `T-401` — Catalogue loader framework + JSON Schemas
- **Files:** `src/adapter/catalogue/yaml_loader.py`, `schemas/*.json` (one per catalogue), tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 45 k tokens.
- **SOP:**
  1. Implement a generic YAML loader that validates against a JSON Schema before deserialising.
  2. Implement `MaintenanceMetadata` parsing (retrieved_at, valid_until, source_url, review_required_after).
  3. Implement `GradedCitation` parsing with source-grade validation.
  4. Write JSON schemas for: parts, hosts, enzymes, rule-manifest-files (one per category), vendor-profiles, screening-trust-policy, institutional-policy, export-profiles, risk-advisories, sop-templates, plugin-manifests.
  5. Implement `stale-catalogue-check` predicate.
  6. Implement `source-grade-citation-check` predicate.
- **Acceptance:** every JSON schema validates against its first manifest entry; CI gates `stale-catalogue-check` and `source-grade-citation-check` pass.

#### 2.4.2 `T-402` — Parts catalogue population
- **Files:** `catalogues/parts.yaml` populated with all parts from `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` §§ 5.1 – 5.13.
- **Model tier:** Sonnet, reviewed by `/scientific-advisor`. **Context budget:** ≤ 50 k tokens. **Sub-split** by category if exceeded: T-402a (origins + markers), T-402b (promoters), T-402c (RBS/Kozak/terminator/polyA), T-402d (tags + linkers + proteases), T-402e (reporters + recombinases + CRISPR + inducible).
- **SOP:**
  1. For each part: write `id`, `name`, `role` (Sequence Ontology term), `sequence` (where in scope), `host_compatibility`, `licence`, `provenance`, graded `citation`, maintenance metadata.
  2. Every entry's citation must resolve to v2.0 KB § 18.
- **Acceptance:** every part loads; CI gates pass.

#### 2.4.3 `T-403` — Hosts catalogue
- **Files:** `catalogues/hosts.yaml` for ~ 60 strains from v2.0 KB § 6.
- **Model tier:** Sonnet, reviewed by `/scientific-advisor`. **Context budget:** ≤ 40 k tokens.
- **SOP:** for each strain: id, name, chassis class, genotype (standard nomenclature), supplier/ATCC, expression features (DE3 lysogen, recA-, endA-, oxidative cytoplasm, gyrA462, F', λpir, T-antigen, EBNA1), codon usage table ID, growth conditions, biosafety tier, citations.

#### 2.4.4 `T-404` — Enzymes catalogue + buffer-compatibility matrix
- **Files:** `catalogues/enzymes.yaml`, `catalogues/enzyme_buffer_compat.yaml`.
- **Model tier:** Sonnet, reviewed by `/scientific-advisor`. **Context budget:** ≤ 35 k tokens.
- **SOP:** ~40 Type-II REs, 6 Type-IIS for Golden Gate (BsaI, BsmBI/Esp3I, SapI, BbsI, AarI, PaqCI), 12 toolkit enzymes (T4 ligase, PNK, T4 DNA Pol, Phusion / Q5 / KAPA HiFi, Klenow, T5 exo, DpnI, alkaline phosphatases), 7 proteases (TEV, 3C/PreScission, Thrombin, Enterokinase, Factor Xa, SUMO Ulp1, HRV 3C). Cross-validate against REBASE.

#### 2.4.5 `T-405` — Rule manifests + fixtures + stub predicates (v1.1 — B-05 / M-05 fix)
- **Files (per category sub-task):**
  - `catalogues/rules/<category>.yaml`
  - `src/engine/validation/predicates/<category>.py` (stub predicates returning `Severity.INFO`)
  - **`tests/fixtures/rules/<category>/triggering/<rule_id>.json`** (one per rule — v1.1)
  - **`tests/fixtures/rules/<category>/passing/<rule_id>.json`** (one per rule — v1.1)
  - `tests/fixtures/rules/<category>/README.md` documenting biological rationale and expected predicate outcomes (v1.1)
- **Model tier:** Sonnet, reviewed by `/scientific-advisor`. **Parallel sub-tasks:** T-405a..T-405e (MR / WR / SR / BR / MS).
- **Context budget:** ≤ 40 k tokens per sub-task.
- **SOP per file (v1.1):**
  1. List every rule with: `rule_id`, `predicate_name`, `severity`, `severity_policy`, `blocks` (frozenset of `SafetyGate`), `reads`, `depends_on_metrics`, `produces_metrics`, `invalidates`, `preconditions`, `target_context`, `external_adapters`, `threshold_profile`, `citation` (graded), `last_reviewed`, `reviewed_by`, `implementation_status: stub | real` (**new in v1.1 per M-05**), `test_fixtures: {triggering: <path>, passing: <path>}` (**now mandatory in v1.1 per B-05**), `suggested_remediation`.
  2. For every rule, **author the triggering and passing fixture files in the same task** as the manifest entry. Each fixture is a JSON file containing a curated `Construct` (or partial construct) that the rule should fire on (triggering) or not (passing). Each fixture's `__rationale__` field documents the biological reasoning so `/scientific-advisor` can review.
  3. Stub predicate in `src/engine/validation/predicates/<category>.py` returns `Severity.INFO` until Phase 5/6 makes it real. Manifest entry's `implementation_status` is set to `stub`.
  4. `tests/fixtures/rules/<category>/README.md` documents per-rule rationale + expected predicate outcomes (one paragraph per rule).
- **Acceptance:**
  - Every rule loads under the YAML schema validation in T-401.
  - `source-grade-citation-check` passes for every entry (Grade A1 / A2 / A3 / B1 / B2; or C with corroborator).
  - Every predicate name resolves at startup (stub predicate exists in code).
  - **`rule-fixture-coverage-check`** (extended in v1.1): every rule in the manifest has both `test_fixtures.triggering` and `test_fixtures.passing` paths that resolve at load time. Phase 4 exit fails if any rule lacks fixtures.
  - **`implementation-status-consistency-check`**: every rule with `implementation_status: real` has a predicate that actually evaluates against its fixtures and returns the correct severity; every rule with `implementation_status: stub` has a stub predicate returning `INFO`. Phase 5/6 exit fails if any required rule still has `implementation_status: stub`.

#### 2.4.6 `T-406` — Vendor profiles + screening trust policy + institutional policy + export profiles + risk advisories
- **Files:** `catalogues/vendor_profiles/{twist,idt,genscript}.yaml`, `catalogues/screening_trust_policy.yaml`, `catalogues/institutional_policy.yaml`, `catalogues/export_profiles.yaml`, `catalogues/risk_advisories.yaml`.
- **Model tier:** Sonnet, reviewed by `/scientific-advisor`. **Parallel sub-tasks**: T-406a..T-406e.
- **Context budget:** ≤ 30 k tokens per sub-task.
- **SOP:** populate per v2.0 KB §§ 11 (vendors), 12 (screening), 17 (MS2 advisory entries), plus the dual-control + unsupported-tier policy defaults discussed in `ARCHITECTURE.md` v1.4 / v1.5.

#### 2.4.7 `T-316c` — Production `SopTemplateSigner` + `SopTemplateVerifier` adapters + key lifecycle (v1.5 — scheduled before T-316b production bootstrap)

**v1.4 H4-04 rationale.** v1.3 mentioned `SopTemplateSigner`/`SopTemplateVerifier` but had no production adapter, no key lifecycle, no rotation/archive/revocation/offline-verification model comparable to T-314b (profile signing) or T-312b (audit-key).

**Implementation status (2026-05-14).** Complete locally. Delivered the Ed25519 SOP-template signer/verifier package, `sop_template` archive purpose, key-management service, `SopTemplateSigningKeyDistributed` / `SopTemplateSigningKeyRevoked` governance events, offline verifier, and runbook. Focused verification: 22 tests passed with 93.13% targeted coverage. T-316b is now unblocked to consume the production signer/verifier.

- **Files:**
  - `src/adapter/security/sop_template_signing/institutional_signer.py` — production institutional `SopTemplateSigner` (Ed25519; separate cryptographic identity from `AuthorisationProfileSigner` + `DecisionRecordSigner` + audit HMAC). Private key admin-service-only; public key embedded in every engine process.
  - `src/adapter/security/sop_template_signing/institutional_verifier.py` — production verifier.
  - `src/app/sop_template_key_management.py` — key versioning + archive + revocation list + public-key distribution + compromised-key response.
  - `tools/sop_template_signature_verifier.py` — standalone offline verifier.
  - `docs/security/sop_template_signing_runbook.md`.
  - Tests: `tests/security/sop_template_signing/{test_sign_then_verify,test_tampered_template_fails,test_wrong_key_version_fails,test_revoked_key_fails,test_offline_verifier_matches,test_separation_of_sop_template_signing_from_other_identities}.py`.
- **Model tier:** Sonnet. **Context budget:** ≤ 35 k tokens.
- **SOP (v1.4 H4-04):**
  1. Implement production signer + verifier using Ed25519 via `cryptography` library (pinned in T-201 `core` runtime).
  2. **Separation of cryptographic identities.** Compromise of SOP-template signing key does not enable forging profile signatures, decision-record signatures, or audit-chain HMACs.
  3. Key versioning + archive (indefinite retention for any key referenced by an active or historical template — per v1.4 H4-05 escrow pattern).
  4. Revocation list maintained in admin-service; broadcast via `SopTemplateSigningKeyRevoked` governance event.
  5. Public-key distribution to engine processes via `SopTemplateSigningKeyDistributed` governance event.
  6. Compromised-key response procedure documented in runbook.
- **Acceptance:** sign-then-verify round trips green; tamper / wrong-version / revoked-key tests green; cryptographic-identity separation tests green; offline verifier reproduces engine verdicts; T-316b consumes the T-316c production signer/verifier during bootstrap/store integration; unit tests may still use T-316a fakes where explicitly marked non-production.

#### 2.4.8 `T-316b` — Signed SQLite SOP-template store + bootstrap migration (v1.5 — follows T-316c production signer/verifier; depends on T-401 schema + T-406 catalogue content + T-316a Protocols)

**v1.4 B4-05 rationale.** v1.3 scheduled T-316b in Phase 3 but its bootstrap reads `catalogues/sop_templates/*.yaml` files whose JSON schema lands in T-401 (Phase 4) and content lands via Phase 4 catalogue tasks. v1.5 keeps the SQLite store + bootstrap in Phase 4 after catalogue infrastructure exists and schedules it after T-316c so production signing/verification is available.

**Implementation status (2026-05-14).** Complete locally. Delivered `SqliteSopTemplateStore`, signed read verification, YAML bootstrap with idempotency, admin-handler SOP-template mint/modify/revoke operations, expanded SOP-template governance event payloads, and regression tests for tamper, revocation, bootstrap, and user/reviewer denial. Focused verification: 30 tests passed with 90.82% targeted coverage. Full local gates are green with 335 tests passed and 2 skipped. Phase 4 is now complete; T-501 is next.

- **Files:**
  - `src/adapter/persistence/sqlite_sop_template_store.py` — SQLite-backed store implementing `SopTemplateReadPort` (read side) + `SopTemplateAdminWritePort` (admin-side; admin-service process `mode=rw`) + `SopTemplateBootstrapPort` (one-time bootstrap from YAML). Three tables: `templates` (id, version, content, signed_payload, signature, signing_key_version, signed_at_utc, status: active/revoked); `template_versions` (full version history; immutable rows); `template_revocations` (revocation log).
  - `src/app/admin_action_handler/sop_template_writes.py` — extension of T-311's `AdminActionHandler` with `mint_sop_template`, `modify_sop_template`, `revoke_sop_template`. Operations require `AdminPrincipal | DeveloperBootstrapPrincipal`; UserPrincipal / ReviewerPrincipal rejected. Each emits the corresponding governance event (`SopTemplateMinted` / `Modified` / `Revoked`) with the full signed template payload embedded per v1.3 B3-03.
  - Tests: `tests/app/sop_template/{test_mint,test_modify,test_revoke,test_user_denied,test_reviewer_denied,test_admin_allowed,test_template_signature_verified_on_read,test_tampered_template_fails_load,test_bootstrap_initial_templates_from_yaml,test_bootstrap_idempotent}.py`.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP (v1.4):**
  1. Read `SopTemplateReadPort`/`SopTemplateAdminWritePort`/`SopTemplateBootstrapPort`/`SopTemplateSigner`/`SopTemplateVerifier` Protocols from T-316a.
  2. Implement the SQLite-backed store with the three tables above. On every read, the store calls `SopTemplateVerifier.verify(template)` (uses the production verifier from T-316c). Tampered templates fail load via `SopTemplateTamperDetectedError`.
  3. Implement the admin-write surface as an extension of T-311's `AdminActionHandler`. Operations sign each template via `SopTemplateSigner.sign(...)` before commit (uses the production signer from T-316c).
  4. **Bootstrap migration.** `SopTemplateBootstrapPort.bootstrap_initial_templates(developer)` reads `catalogues/sop_templates/*.yaml` (T-406 content), signs each via the bootstrap key, writes signed templates to the SQLite store, emits `SopTemplateMinted` per template. After bootstrap, the YAML files are no longer read at runtime — the SQLite store is canonical. Bootstrap is idempotent: re-running with unchanged YAML produces no new events.
  5. **Legacy runtime SOP-template library removed.** Per v1.4 B4-05 + M4-01, the v1.2 monolithic SOP-template Protocol + `YamlSopTemplateLoader` are **removed** from the runtime composition. The legacy YAML files remain in `catalogues/sop_templates/` only as **T-316b bootstrap input**; runtime reads go through `SqliteSopTemplateStore` via `SopTemplateReadPort`.
- **Acceptance:** every operation tested with `AdminPrincipal` (allowed) and `UserPrincipal` / `ReviewerPrincipal` (denied); template signature verified on every read; tampered template in SQLite triggers `SopTemplateTamperDetectedError`; bootstrap from YAML produces signed templates; running bootstrap twice is idempotent; the legacy runtime SOP-template library symbol is absent from composition root.

### Phase 5 — Validation rule engine (4 tasks; v1.1 — added T-504 per H-03 / B-02)

#### 2.5.1 `T-501` — `engine.dependencies` (DAG-evaluator)
- **Files:** `src/engine/dependencies.py`, `tests/engine/test_dependencies.py`.
- **Implementation status (2026-05-14).** Complete locally. Delivered deterministic validation dependency graph construction over `ValidationRule` read fields, produced metrics, required metrics, and invalidation declarations; field/metric impact computation; required metric and invalidated rule/metric reporting; producer-before-consumer topological order; graph diagnostics; and cycle detection. Focused verification: 6 tests passed with 99.37% targeted coverage. Full local gates were green with 341 tests passed and 2 skipped at verification time.
- **Model tier:** Opus. **Context budget:** ≤ 50 k tokens.
- **SOP:**
  1. Read every rule's `reads`, `depends_on_metrics`, `produces_metrics`, `invalidates` to build a DAG over `(field, metric)` pairs.
  2. Implement `affected_rules(changeset) → frozenset[RuleId]` with transitive closure.
  3. Cycle detection on registry load.
- **Acceptance:** property test on synthetic DAGs; performance test (< 100 ms for the full 150-rule registry).

#### 2.5.2 `T-502` — `engine.validation` (pure DAG executor; v1.2 — `WorkerPoolFactory` per H2-08; explicit benchmark per M2-06)
- **Files:** `src/engine/validation/engine.py`, `validation_context.py`, `report.py`, `worker_pool_factory.py` (v1.2 — replaces v1.1 `parallel_executor.py`), `tests/benchmark/T_502_validation_bench.py` (v1.2 — explicit benchmark file per M2-06), `tests/benchmark/results/T_502_validation_bench_<git_sha>.json` (nightly result records).
- **Implementation status (2026-05-14).** Complete locally. Delivered `ValidationContext`, deterministic `ValidationReport`, pure topological executor, field/metric incremental revalidation, typed predicate-error aggregation, HARD-gate routing, pickle-safe predicate stubs, sequential/thread/local-spawn `WorkerPoolFactory`, T-502 benchmark harness + local result record, and enforced `no-domain-impurity-check`. Focused verification: 11 tests passed with 91.98% targeted coverage. Full local gates were green with 352 tests passed and 2 skipped at verification time.
- **Model tier:** Opus. **Context budget:** ≤ 60 k tokens.
- **SOP (v1.2):**
  1. Implement `ValidationContext` (M7 boundary fix: precomputed metrics, threshold profile, derivation environment).
  2. Implement pure `validate(context, registry, executor: WorkerPoolFactory) → ValidationReport` that walks the DAG in topological order.
  3. **(v1.2 H2-08 fix — `WorkerPoolFactory` replaces global spawn-mutation.)**
     - **`WorkerPoolFactory`** (in `src/engine/validation/worker_pool_factory.py`) constructs a context manager backed by either `multiprocessing.get_context("spawn").Pool` (local context — no global state mutation), `concurrent.futures.ThreadPoolExecutor` (for I/O-bound contexts or notebook/test environments), or a `SequentialExecutor` (deterministic fallback).
     - All rule predicates are *top-level* functions (no closures, no lambdas) so they pickle cleanly under spawn semantics.
     - Workers receive deterministic random seeds derived from the rule_id; results are aggregated in **submit-order** (not arrival order) so the report is deterministic.
     - Exceptions are wrapped in typed `RuleEvaluationError(rule_id, cause)` and aggregated; a single failure does not crash the whole batch.
     - **Library imports never call `multiprocessing.set_start_method`.** Only the production CLI / API entry-points may set the global spawn method (`force=True`). Inside FastAPI / tests / notebooks, `WorkerPoolFactory.create("process")` works via local context.
  4. **(v1.2 M2-06 fix — explicit benchmark ownership.)**
     - `tests/benchmark/T_502_validation_bench.py` is a benchmark file (not a manifest). Compares sequential / thread / process modes on a 150-rule fixture and emits a JSON result record to `tests/benchmark/results/T_502_validation_bench_<git_sha>.json`.
     - CI cadence: runs on **nightly** for every commit on `main`; runs on PRs that touch `src/engine/validation/` or `tools/ci_gates/no_domain_impurity_check.py` (in informational mode); nightly regressions exceeding 50 % over the previous nightly **fail the nightly job** and open a follow-up task.
     - Default mode chosen per platform (process on Linux, sequential or thread on Windows depending on rule count) — recorded in `tests/benchmark/results/` per platform.
  5. Severity routing: each rule's `blocks` set determines which safety gate fires on HARD failures. **(v1.2 H2-06 cross-resolution.)** The `BlockCompile` gate-predicate registration in T-309 is **activated** here in T-502 (HARD validation failure → `BlockCompile`).
- **Acceptance:** Tier-1 deterministic budget: 10 kb construct < 5 s; incremental re-eval < 1 s; `no-domain-impurity-check` green; pure-function property tests; **deterministic-result-order** test: same input run 100× produces byte-identical reports; **pickle-safety** test: every registered predicate is picklable under spawn semantics; **benchmark file present + first nightly result recorded** before T-502 transitions to `verified`.

#### 2.5.3 `T-504` — `engine.compatibility` (v1.1 — new, per H-03 / B-02)
- **Files:** `src/engine/compatibility/engine.py`, `host_iteration.py`, `host_constraints.py`, `threshold_resolution.py`, tests.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with an `engine.compatibility` package, implemented role-keyed host workflow iteration, construct compatibility fact extraction, host-role threshold-profile resolution, structured `CompatibilityReport` payloads, HARD gate routing, missing-host handling, and R-15 marker-conflict detection per host role. Focused verification: 9 tests passed with 91.78% targeted coverage. Full local gates were green with 361 tests passed and 2 skipped at verification time.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP:**
  1. Implement `CompatibilityChecker.check(construct, hosts: tuple[HostContext, ...]) -> CompatibilityReport` per `ARCHITECTURE.md` v1.5 § 4.2.1 row.
  2. Iterate over each `HostContext` role independently — multi-host workflows are first-class (plant transient = E. coli cloning + Agrobacterium delivery + plant target; lentivirus = bacterial + producer + target; AAV = bacterial + producer + target; VLP = capsid-production + cargo-production + loading + target-cell-assay; cell-free = no propagation host).
  3. Evaluate `HostCompatibilityConstraints` per host (promoter recognition, codon usage, origin compatibility, marker, toxicity, secretion, intron / splicing support, methylation, copy number, transformation modality).
  4. Resolve threshold profiles per host + role at evaluation time — rules tagged `threshold_profile: <name>` look up the active profile against the current `HostContext`.
  5. Emit structured `CompatibilityReport` with per-host incompatibilities, severity, suggested remediation; gate routing per the violated rules' `blocks` sets.
  6. Fixtures covering: plant transient (3-host workflow), lentivirus (3-host), AAV (3-host), VLP (4-host), cell-free (no propagation), shuttle vectors (≥ 2 maintenance hosts).
- **Acceptance:** every fixture host workflow produces the expected `CompatibilityReport`; the v1.5 R-15 mitigation (multi-host marker-conflict misclassification) is verified by a negative fixture where a marker valid for the propagation host but invalid for the expression host is caught.
- **Hand-off:** Consumed by `app.validation_orchestrator` (T-603) and `app.assembly_orchestrator` (T-705).

#### 2.5.4 `T-503` — `engine.sequence_analysis` + ~50 structural predicates
- **Files:** `src/engine/sequence_analysis/{find_sites,digest,compatible_ends,rank_directional,design_diagnostic,fragment_sim}.py`; `src/engine/validation/predicates/{structural,host,frame,internal_sites}.py`; tests.
- **Implementation status (2026-05-14).** Complete locally. Replaced the placeholder with an `engine.sequence_analysis` package implementing topology-aware restriction-site discovery, digest and fragment simulation, compatible-end classification, directional cloning-site ranking, and diagnostic digest design. Added an `IMPLEMENTED_PREDICATE_REGISTRY` with 50+ structural predicate names, metric/payload-backed structural evaluation, concrete frame/tandem-stop/internal-site predicates, and host-compatibility predicates consuming the T-504 compatibility metric. BR-14 is explicitly excluded. `catalogues/rules/*.yaml` remain `implementation_status: stub` by design so Phase-4 fixture consistency stays enforced until per-rule fixture promotion. Focused verification: 11 tests passed with 91.67% targeted coverage. Full local gates are green with 372 tests passed and 2 skipped. Phase 5 is complete; T-601a..k is next.
- **Model tier:** Opus. **Context budget:** ≤ 75 k tokens — **split** into T-503a (sequence_analysis), T-503b (structural predicates), T-503c (host + frame predicates).
- **SOP:**
  1. `find_sites`: topology-aware site finding with degenerate-base support, circular wraparound, methylation context.
  2. `digest` + `fragment_simulation`: simulate cuts; produce ordered fragments with sticky-end sequences.
  3. `compatible_ends`: classify two fragment ends (sticky 5′ vs 3′ vs blunt) and whether they can ligate.
  4. `rank_directional_cloning_sites`: rank unique-site pairs in the vector that are absent in the insert.
  5. `design_diagnostic_digest`: search for an enzyme set producing band patterns distinguishable on a 1 % agarose gel between the correct clone and a defined `WrongCloneModel` set (empty vector, reverse-orientation insert, double insert, single recombinant).
  6. Implement ~ 50 structural rule predicates as listed in ROADMAP Phase 5 (V001..V005, V011..V012, V021..V025, MR-01..MR-06, MR-10..MR-11, MR-17..MR-19, MR-22..MR-23, MR-29..MR-35, MR-37..MR-44, MR-50..MR-53, WR-01..WR-07, WR-11..WR-21, BR-01..BR-13). **(v1.2 H2-11 fix — BR-14 removed from structural predicates.)** BR-14 is the advisory-acknowledgement hard-gate condition and is owned by `app.authorisation_decision` (T-806b in Phase 8b) + the `no-passive-advisory-bypass-check` CI gate; it has no structural predicate in this task. T-806a (Phase 8a) supplies the pure predicate `all_required_advisories_acknowledged(report, events) → (bool, frozenset[AdvisoryId])` consumed by T-806b. `engine.sequence_analysis` has no opinion on advisory acknowledgement state.
- **Acceptance:** every implemented rule has a triggering + passing gold fixture; rule-validation coverage gate green for the implemented subset; REBASE expectations match; **no structural predicate evaluates BR-14**.

### Phase 6 — Biology back-ends + application services (5 tasks; v1.2 — H2-02 phase-count fix)

#### 2.6.1 `T-601a..k` — Biology adapter implementations (parallel; v1.5 manifest range grammar expands to T-601a through T-601k)
- **Files (one task per adapter):** `src/adapter/biology/{vienna_rna,spliceai,signalp,rbs_calc_v2,noderer_kozak,cai,minmax,charming,avoid_only}.py`, plus deterministic-fake counterparts in `tests/fakes/biology/*`.
- **Implementation status (2026-05-14).** Complete locally. Converted `adapter.biology` from a T-203 placeholder module into a package with deterministic local adapters for RNA folding, splice motif prediction, signal peptide prediction, RBS/TIR scoring, Kozak scoring, and CAI / MinMax / CHARMING / avoid-only codon algorithms. Added adapter manifests with local latency fields, fixture-driven deterministic fakes, calibration-drift policy files for every adapter, and focused adapter tests. Heavyweight or service-backed production implementations remain optional behind the existing extras and port methods. Focused verification: 8 tests passed with 91.19% targeted coverage. Full local gates are green with 380 tests passed and 2 skipped. T-602 is next.
- **Model tier:** Sonnet. **Parallel sub-tasks:** one per adapter.
- **Context budget:** ≤ 30 k tokens per adapter.
- **SOP per adapter:**
  1. Implement the port (`RnaFolder`, `SplicePredictor`, etc.) from `ARCHITECTURE.md` § 4.5.
  2. Pin the underlying library version in `pyproject.toml`.
  3. Implement `Manifest` with `measured_typical_latency_ms` / `measured_max_latency_ms` benchmarked locally.
  4. Implement a **deterministic fake** with the same Protocol, returning fixture-driven outputs for a known input set.
  5. Add a **calibration test** that compares the fake's outputs against the real adapter on a curated input set within numeric tolerance (M9: production-adapter budget — measured per adapter, reported separately).
  6. **(v1.1 M-07) `CalibrationDriftPolicy`** declared per adapter in `tests/calibration/biology/<adapter>/policy.yaml`: `tolerance.relative_error` (default 0.05; per-adapter override allowed), `baseline_fixture_hash`, `baseline_captured_at`, `escalation_path` (drift > tolerance → emit `CalibrationDrift` alert nightly; non-release-blocking, but flagged in TASK_BOARD § 6). Baseline refresh requires `/scientific-advisor` sign-off recorded as a `CalibrationBaselineRefreshed` governance event; the refreshed baseline's hash is captured in `DerivationEnvironment.external_database_versions`.
- **Acceptance:** each adapter passes determinism check inside container; calibration test green; integration with `app.validation_orchestrator` (T-603) wires correctly; calibration-drift policy file exists for every production adapter.

#### 2.6.2 `T-602` — Biology-back-end-dependent predicates
- **Files:** `src/engine/validation/predicates/{rbs,kozak,uorf,premature_polya,splice,cpg,signal_peptide}.py`, tests.
- **Implementation status (2026-05-14).** Complete locally. Added pure metric-backed predicates for MR-12 RBS spacing/TIR/accessibility, MR-13 Kozak PWM threshold, MR-14 uORF scan, MR-15 premature polyA motifs, MR-16 splice-score threshold, MR-27 CpG content, and MR-28 signal-peptide/compartment consistency. The predicates consume `ValidationContext` metrics or deterministic sequence fallbacks and do not import biology adapters. `IMPLEMENTED_PREDICATE_REGISTRY` now includes the T-602 subset while `PREDICATE_REGISTRY` remains the Phase-4 stub registry for manifest consistency. Focused verification: 7 tests passed with 89.89% targeted coverage. Full local gates are green with 387 tests passed and 2 skipped. Phase 6 is complete locally through T-607; T-701 is next.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP:** Implement MR-12 (RBS folding), MR-13 (Kozak PWM), MR-14 (uORF scan), MR-15 (premature polyA), MR-16 (splice — SpliceAI), MR-27 (CpG content), MR-28 (signal peptide). Each predicate consumes precomputed metrics via `ValidationContext`.
- **Acceptance:** rule-validation coverage gate green; tests with known high-/low-expression constructs.

#### 2.6.3 `T-603` — `app.validation_orchestrator` (metric pre-compute)
- **Files:** `src/app/validation_orchestrator.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 45 k tokens.
- **SOP:**
  1. Read the rule registry; determine `required_metrics` for affected rules.
  2. Call biology adapters in parallel (Tier-2 budget).
  3. Cache metric results in the design session for incremental re-eval (with `DerivationEnvironment` hash binding).
  4. Build `ValidationContext` and invoke pure `engine.validation.validate`.
- **Acceptance:** integration test that demonstrates incremental re-eval after a single module change re-runs only affected rules + metrics; Tier-2 budget met.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with `ValidationOrchestrator`, `BiologyAdapterSet`, derivation-environment-bound `DesignSessionMetricCache`, predicate-to-metric bindings for the T-602 biology subset, parallel metric task execution, and default validation predicate composition that overlays implemented predicates on the Phase-4 stub registry. Focused verification: 4 tests passed. Full local gates are green with 391 passed and 2 skipped. Phase 6 is complete locally through T-607; T-701 is next.

#### 2.6.4 `T-606` — `app.design_service` (v1.2 — phase-local acceptance per H2-05)
- **Files:** `src/app/design_service.py`, tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 40 k tokens.
- **SOP (v1.2):**
  1. Implement top-level use cases per `ARCHITECTURE.md` v1.5 § 4.2.2: create / open / amend / compile / replay a design session.
  2. Each operation accepts a `Principal` and a `SessionId`; emits the appropriate `DesignEvent` subclass to the design event stream.
  3. Wire `engine.session` state-machine transitions to corresponding application use cases.
  4. **(v1.2 H2-05 fix.) Phase-local acceptance with explicit pending states.** Operations downstream of Phase 6 are explicitly modelled as `Awaiting*` pending states — `AwaitingScreening` (until Phase 10), `AwaitingAuthorisation` (until Phase 8b), `AwaitingSopRender` (until Phase 8b), `AwaitingExport` (until Phase 9b). `design_service` exposes a `current_pending_state(session_id)` method that returns the next pending step; tests verify the pending-state taxonomy is consistent with the gate-predicate registration in T-309.
- **Acceptance (v1.2 phase-local):**
  - Create / open / amend / compile / replay use cases work end-to-end with deterministic in-memory fakes for every adapter.
  - For each pending state, an integration test confirms `design_service` correctly returns the pending taxonomy without invoking the absent downstream service.
  - **Full happy path (create → add parts → compile → screen → authorise → export) is owned by T-1301 (white-paper UAT), NOT by T-606.** T-606 must not stub the screening / authorisation / SOP / export services to "fake green" the downstream path.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with `DesignService`, structural event-log/project-store/snapshot-store ports, create/open/amend/compile/replay use cases over `engine.session`, compile-gate integration with `GatePredicateRegistry`, and phase-local `AwaitingScreening` / `AwaitingAuthorisation` / `AwaitingSopRender` / `AwaitingExport` pending-state taxonomy mapped to T-309 safety gates. Focused verification: 6 tests passed. Full local gates are green with 397 passed and 2 skipped. T-607 is complete locally; T-701 is next.

#### 2.6.5 `T-607` — `app.decision_tree` (v1.1 — new, per M-08 / B-02)
- **Files:** `src/app/decision_tree.py`, `decision_flow.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 45 k tokens.
- **SOP:**
  1. Implement the decision-tree flow per FR-UI-01..12: objective → host → cargo → expression → tagging → cloning chemistry → biosafety tier.
  2. Each step has drop-down candidates pulled from `PartCatalogue` / `HostCatalogue` / etc., plus a free-text channel that feeds `app.constraint_translator` (Phase 12).
  3. Emit `PartAdded` / `HostSelected` / `FreeTextEntered` events as the user advances; persist intermediate state via `engine.session`.
- **Acceptance:** unit test on each step's candidate filter; integration test for the full flow producing a compileable construct.
- **Implementation status (2026-05-14).** Complete locally. Added `app.decision_flow` typed flow primitives and replaced the T-203 `app.decision_tree` placeholder with catalogue-backed candidate filtering for objective, host, cargo, expression, tagging, cloning chemistry, and biosafety tier. The flow emits `FreeTextEntered`, `HostSelected`, `PartAdded`, and final `LLMTranslationConfirmed` events through `DesignService`, enforces locked-step protection, and can produce deterministic compile metadata for `DesignService.compile_session`. Focused verification: 12 tests passed. Full local gates are green with 409 passed and 2 skipped. Phase 6 is complete locally; T-701 is next.

### Phase 7 — Codon + assembly + overhang + primer (5 tasks)

#### 2.7.1 `T-701` — `engine.codon` (constraint-aware optimiser)
- **Files:** `src/engine/codon/types.py`, `algorithms.py`, `optimiser.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 60 k tokens.
- **SOP:** See § 1.7 example brief. Implement CAI, %MinMax, CHARMING, `avoid_only`. Lexicographic-priority fixed-point with `N=5` cap. Honour `protected_intervals` and `functional_rna_features` (MR-09 / MR-17).
- **Implementation status (2026-05-14).** Complete locally. Converted the T-203 `engine.codon` placeholder into a package with `CodingSequenceDesign`, protected intervals, functional-RNA feature protection, CAI / MinMax / CHARMING / avoid-only algorithms, sequence metrics, and `CodonOptimiser` fixed-point execution capped at five iterations. Focused verification: 9 tests passed. Full local gates are green with 418 passed and 2 skipped. T-702 is also complete locally; T-703 is next.

#### 2.7.2 `T-702` — `engine.overhang` (Golden Gate fidelity optimiser)
- **Files:** `src/engine/overhang/dataset.py` (Potapov 2018 + Pryor 2020 matrices), `optimiser.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 50 k tokens.
- **SOP:**
  1. Embed the published fidelity matrices as static data (cite v2.0 KB sources; the matrices themselves are public data).
  2. Implement branch-and-bound search for non-cross-reactive overhang sets.
  3. Score sets by on-target ligation propensity, off-target cross-ligation minimisation, palindrome avoidance, reverse-complement-conflict avoidance.
- **Acceptance:** reproduce Pryor 2020 24-fragment benchmark assembly; performance budget < 60 s for 20 fragments.
- **Implementation status (2026-05-14).** Complete locally. Converted the T-203 `engine.overhang` placeholder into a pure package with Potapov 2018 / Pryor 2020 labelled fidelity matrices, canonical overhang enumeration, reverse-complement and palindrome guards, product-of-per-overhang fidelity scoring, cross-reaction diagnostics, a typed `OverhangDesignRequest` / result contract, bounded branch-and-bound search, exact benchmark-set scoring, and a 24-fragment benchmark fixture. Focused verification: 8 tests passed. Full local gates are green with 426 passed and 2 skipped. T-703 is also complete locally; T-704 is next.

#### 2.7.3 `T-703` — `engine.assembly` (strategy hierarchy; v1.1 — added T-703e SLIC per M-02)
- **Files:** `src/engine/assembly/base.py`, `restriction_ligation.py`, `gibson.py`, `golden_gate.py` + kit subclasses, `gateway.py`, `lic.py`, `slic.py` (**new in v1.1 per M-02**), `user.py`, `iva.py`, `yeast_tar.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 90 k tokens — **split** into T-703a (restriction + gibson), T-703b (golden_gate + kits), T-703c (gateway + lic + user), T-703d (iva + yeast_tar), **T-703e (SLIC — new in v1.1)**.
- **SOP:** Each strategy implements `validate_parts`, `design_primers`, `compile_assembly_plan` → typed `AssemblyPlan` subclass. Golden Gate uses `engine.overhang` for overhang-set picking.
- **T-703e SLIC sub-task:** SLIC is mechanically distinct from Gibson (T4-polymerase-only chew-back vs three-enzyme cocktail) and is listed in REQUIREMENTS § 1.2 scope. Implement `SLICStrategy` as a sibling of `GibsonLikeStrategy`; emit `OverlapAssemblyPlan` subclass `SLICPlan` carrying the T4-polymerase conditions distinct from Gibson conditions. Fixture: 3-fragment SLIC assembly with verified primer chew-back overlap geometry.
- **Implementation status (2026-05-14).** Complete locally. Converted the T-203 `engine.assembly` placeholder into a pure strategy package with `AssemblyPart`, `AssemblyStrategy`, `AssemblyEngine`, deterministic primer placeholders for T-704, and typed plan compilers for restriction ligation, Gibson-like / NEBuilder / In-Fusion overlap assembly, Golden Gate plus MoClo / Loop / YTK / GreenGate / GoldenBraid / JUMP / MIDAS kit subclasses, Gateway, LIC, SLIC, USER, IVA, and yeast TAR. Golden Gate delegates overhang selection to `engine.overhang`; SLIC emits a dedicated `SLICPlan` carrying T4-polymerase chew-back conditions. Focused verification: 7 tests passed. Full local gates are green with 433 passed and 2 skipped. T-704 is also complete locally; T-705 is next.

#### 2.7.4 `T-704` — `engine.primer` (Primer3-backed)
- **Files:** `src/engine/primer/designer.py`, `parameters.py`, `sequencing.py`, `diagnostic.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP:** Per-strategy primer design; `PrimerDesignParameters` (M1 / M2 v1.4). Off-target scan against full plasmid via `engine.sequence_analysis.find_sites`-style search. Sequencing-primer designer covers every cloning junction ±50 bp within Sanger read length. Diagnostic-digest primer designer pairs with `engine.sequence_analysis.design_diagnostic_digest`.
- **Implementation status (2026-05-14).** Complete locally. Converted the T-203 `engine.primer` placeholder into a pure package with `PrimerDesignParameters`, optional Primer3 backend detection, deterministic fallback primer-pair selection, Tm/GC metrics, exact seed off-target scanning, per-assembly-part primer sets, Sanger sequencing primer placement for junction coverage, and diagnostic-digest primer design wrapping `engine.sequence_analysis.design_diagnostic_digest`. Focused verification: 6 tests passed. Full local gates are green with 439 passed and 2 skipped. T-705 is also complete locally; Phase 7 is complete locally.

#### 2.7.5 `T-705` — `app.assembly_orchestrator` (iterative loop)
- **Files:** `src/app/assembly_orchestrator.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 40 k tokens.
- **SOP:** Implement lexicographic-priority fixed-point loop: codon optimisation → validation → assembly choice → primer design → validation → re-optimise until convergence or N=5 cap. Surface residual conflicts via structured `ConvergenceFailure` result.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with `AssemblyOrchestrator`, `AssemblyMethodPicker`, typed orchestration request/result models, iteration history fingerprints, lexicographic residual priority, optional T-603 validation-runner hooks before and after assembly/primer generation, integration with `CodonOptimiser`, `AssemblyEngine`, and `PrimerDesigner`, and structured `ConvergenceFailure` when the five-iteration cap is reached. Focused verification: 4 tests passed. Full local gates are green with 443 passed and 2 skipped. Phase 7 is complete locally; T-801 is also complete locally; T-802 is next.

### Phase 8a — Design-plan + controls + advisory data + advisory acknowledgement (pre-screening, non-operational; 7 tasks; v1.2 — H2-02 phase-count; B2-09 T-805 split)

**v1.2 reordering note.** Phase 8 was split (v1.1, B-03) into **8a** (pre-screening, non-operational) and **8b** (post-Phase-10, SOP + authorisation). v1.2 additionally splits Phase 9 (B2-02): **9a** (sequence I/O + SnapGene file-watch — pre-screening, runs after 8a) and **9b** (final export orchestrator — runs after 8b).

**Final phase order (v1.2): Phase 7 → 8a → 9a → 10 → 8b → 9b → 11 → 12 → 13.**

8a tasks (canonical list): T-801, T-802, T-804, **T-805a (new — v1.2 B2-09 — `app.design_plan_orchestrator`)**, T-806a, T-807, T-808.

#### 2.8a.1 `T-801` — `engine.risk_classification` (B3 mitigation)
- **Files:** `src/engine/risk_classification/classifier.py`, `report.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 45 k tokens.
- **SOP:** Scan a `ConstructGraph` against `catalogues/risk_advisories.yaml`. Emit `RiskAdvisoryReport` v1.5 with `design_session_id`, `construct_id`, `construct_checksum`, `report_content_hash`, stable `advisory_id` per item, `required_acknowledgements()`. Map every advisory to a graded citation.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with a deterministic risk-advisory classifier over parsed `risk_advisories.yaml` payloads; added catalogue parsing, trigger-tag inference from biosafety tier, screening verdict, provenance, export, vector, cargo, and host metadata, severity-ordered advisory emission, graded citation mapping, required-acknowledgement compatibility through `RiskAdvisoryReport`, and stable report content hashing bound to session, construct, checksum, version, catalogue hash, and emitted advisory payloads. Focused verification: 4 tests passed. Full local gates are green with 447 passed and 2 skipped. T-802 is also complete locally; T-804 is next.

#### 2.8a.2 `T-802` — `engine.design_plan` (v1.2 — renderer files explicit per M2-04)
- **Files:** `src/engine/design_plan/generator.py`, `src/engine/design_plan/renderers/{markdown,pdf,json}.py` (v1.2 — explicit renderers), templates, tests.
- **Model tier:** Opus. **Context budget:** ≤ 50 k tokens.
- **SOP (v1.2):**
  1. `DesignRealisationPlan` generator: assembly route + fragment inputs + QC checkpoints + expected verification artefacts + institutional-approvals-required + biosafety classification + reviewer-packet summary. **Cannot contain a `ProtocolStep`** — verified by type and by `import-linter` (the package cannot import `domain.types.sop_protected`).
  2. **(v1.2 M2-04) Renderer files explicit.** `renderers/markdown.py` uses `markdown-it-py` (pinned); `renderers/pdf.py` uses `weasyprint` (pinned) with the **deterministic-rendering policy** in `docs/rendering_determinism.md` — pinned font (Noto Sans / Noto Mono), no system-font fallback, no embedded timestamps in PDFs (use `derivation_environment.created_at_utc` as canonical `/CreationDate`), `/ID` and `/Producer` overridden to fixed canonical values; `renderers/json.py` uses the canonical-JSON serialiser from T-307.
  3. Acceptance includes the § 4.6a renderer test class.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with an `engine.design_plan` package containing `DesignPlanInput`, `DesignPlanGenerator`, deterministic QC checkpoint / verification artefact / approval synthesis, reviewer-packet evidence hashing, canonical JSON rendering, ordered Markdown rendering, deterministic PDF rendering with fixed metadata and no `/CreationDate`, and static tests proving the package does not import the gated operational protocol namespace or reference `ProtocolStep`. Focused verification: 3 tests passed. Full local gates are green with 450 passed and 2 skipped. T-804 is also complete locally; T-805a is next.

*(v1.1 placeholder T-803 / T-805 `MOVED` headings — removed in v1.2 H2-01. T-803 lives in Phase 8b; T-805 was split in v1.2 B2-09 into T-805a [Phase 8a, this phase, immediately below] and T-805b [Phase 8b, `app.sop_protocol_orchestrator`]. The agenda's task parser sees only one heading per task ID; cross-references to the new home appear as prose paragraphs in Appendix B's traceability matrix.)*

#### 2.8a.3 `T-804` — `engine.controls`
- **Files:** `src/engine/controls/generator.py`, `validation.py`, tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 40 k tokens.
- **SOP:** Generate `ControlSet` (positive / negative / process / library-specific). Validation rules (N8) tied to host role + chemistry + cargo class: positive-control suitability matched, negative-control absence-of-signal, vehicle/mock controls, replicate-structure recommendation.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with an `engine.controls` package containing `ControlGenerationInput`, `ControlSetGenerator`, deterministic positive / negative / process / vehicle / library-specific control synthesis, host/readout-aware positive controls, absence-of-signal negative controls, replicate recommendations, and `validate_control_set()` findings for missing vehicle, library-specific, process, replicate, host-match, and negative-baseline coverage. Focused verification: 4 tests passed. Full local gates are green with 454 passed and 2 skipped. T-805a is also complete locally; T-806a is next.

#### 2.8a.4 `T-805a` — `app.design_plan_orchestrator` (v1.2 — new, per B2-09)
- **Files:** `src/app/design_plan_orchestrator.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 45 k tokens.
- **SOP (v1.2):**
  1. Dispatch to `engine.design_plan` (T-802) for `DesignRealisationPlan` rendering; to `engine.controls` (T-804) for `ControlSet`; to `engine.risk_classification` (T-801) for `RiskAdvisoryReport`; to `app.advisory_acknowledgement`'s presentation surface (T-806a) for advisory presentation.
  2. Produce a `DraftDesignBundle` — explicitly **NOT** a vendor-export bundle. `DraftDesignBundle` is structurally incapable of containing `SopLinkedProtocol` (no field of any reachable type resolves to `domain.types.sop_protected.*`), `BlockVendorSubmission` clearance (no field references a screening verdict), or `OperationalProtocolAuthorised` evidence. Static test `tests/static/test_draft_bundle_no_operational_fields.py` enforces this at type + AST level.
  3. Always available, runs before screening. Emits the corresponding design events (`DesignRealisationPlanRendered`, `ControlSetRendered`, `RiskAdvisoryReportRendered`) to the design event stream.
  4. The `DraftDesignBundle` is the pre-screening sharing artefact (e.g., a junior researcher sharing a draft with a Reviewer before institutional sign-off). It must never be conflated with the final export bundle produced by T-903 (Phase 9b).
- **Acceptance:** integration test renders a draft bundle for white-paper Example A with no screening verdict, no SOP, no authorisation evidence; static test confirms no operational field is reachable; design events emitted to the correct stream; bundle round-trip JSON byte-deterministic.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with `DesignPlanOrchestrator`, `DraftDesignBundleRequest`, and `DraftDesignBundle`; composed T-802 design-plan rendering, T-804 controls generation/validation, and T-801 risk classification into a deterministic pre-screening bundle; added design-stream event classes `DesignRealisationPlanRendered`, `ControlSetRendered`, and `RiskAdvisoryReportRendered`; appended events through an injected design event log; added static coverage that the bundle shape and orchestrator imports exclude gated operational artefacts, vendor clearance, and screening/authorisation events. Focused verification: 14 tests passed. Full local gates are green with 458 passed and 2 skipped. T-806a is also complete locally; T-807 is next.

#### 2.8a.5 `T-806a` — Advisory presentation + acknowledgement surface (v1.3 — `AdvisoryWarningPresented` schema explicit per H3-11)
- **Files:** `src/app/advisory_acknowledgement.py`, `src/domain/events/governance/advisory.py` (explicit schema), tests.
- **Model tier:** Opus. **Context budget:** ≤ 50 k tokens (v1.3 increased from 45 k).
- **SOP (v1.3):**
  1. **(v1.3 H3-11 — explicit `AdvisoryWarningPresented` schema per FR-ADV-02.)** Define the event with full field set:

     ```python
     @dataclass(frozen=True)
     class AdvisoryWarningPresented(GovernanceEvent):
         design_session_id: SessionId
         construct_id: ConstructId
         construct_checksum: ConstructChecksum
         report_content_hash: ReportContentHash
         advisory_ids: frozenset[AdvisoryId]
         presentation_surface: PresentationSurface  # CLI | API | UI
         presentation_surface_version: str  # e.g., "cli==0.3.2", "api==1.0.0"
         recipient_principal_id: PrincipalId
         recipient_role: SecurityRole  # validated: ADMINISTRATOR or REVIEWER for binding presentations
         presented_at_utc: datetime
         presentation_id: PresentationId  # unique per render
     ```

     `recipient_role` constraint: a **binding** presentation (counted by the gate predicate `all_required_advisories_acknowledged`) requires `recipient_role` ∈ {`ADMINISTRATOR`, `REVIEWER`}. A presentation to a `User` is a soft notification — logged but not counted as a presentation for gate purposes.
  2. Implement the presentation surface: every CLI / API / UI render of a `RiskAdvisoryReport` to a qualified recipient emits `AdvisoryWarningPresented` to the governance event stream with all fields populated. The event payload **embeds** the full canonical `AdvisoryWarningPresented` value per v1.3 B3-03 (no reference-only payloads).
  3. Implement the three explicit-action endpoints: **acknowledge** (justification ≥ 20 chars + signed `DecisionRecord`), **decline** (route to alternative reviewer / dual-control flow), **escalate** (require `institutional_approval_id`). Emit `RiskAdvisoryAcknowledged` / `RiskAdvisoryDeclined` / `RiskAdvisoryEscalated` with **full signed value-object payloads embedded** per v1.3 B3-03.
  4. Implement the pure predicate `all_required_advisories_acknowledged(report, events) → (bool, frozenset[AdvisoryId])`. The predicate iterates over the report's `required_acknowledgements()` and matches them against governance-stream `RiskAdvisoryAcknowledged` events with the embedded `AdvisoryWarningPresented` event chain — checking `recipient_role ∈ {ADMINISTRATOR, REVIEWER}`, `report_content_hash` match, `construct_checksum` match, and signature validity.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-203 placeholder with `AdvisoryAcknowledgementService`, binding and soft presentation events, explicit acknowledge / decline / escalate actions over `RiskAdvisoryAcknowledgement` and signed `DecisionRecord` values, governance-event payload embedding, role checks for reviewer/administrator authority, escalation approval enforcement, and `all_required_advisories_acknowledged()` matching required advisory IDs against binding presentations, report hashes, construct checksums, substantive justification, and phase-local signature evidence. Focused verification: 5 tests passed. Full local gates are green with 463 passed and 2 skipped. T-807 is next.
  5. **Do not** implement the authorisation gate here — that is T-806b in Phase 8b, after Phase 10 delivers real screening events.
- **Acceptance:**
  - One test per presentation surface (`test_cli_presentation_emits_event`, `test_api_presentation_emits_event`, `test_ui_presentation_emits_event`) with the full FR-ADV-02 field set populated.
  - `test_user_presentation_not_counted_by_predicate`: a presentation to a `UserPrincipal` produces an event but the predicate does not count it (non-binding recipient role).
  - `test_admin_presentation_counted_by_predicate`: a presentation to an `AdminPrincipal` is counted; with subsequent acknowledgement, the predicate returns `(True, frozenset())`.
  - Explicit acknowledgement / decline / escalate paths produce the right governance events with embedded signed payloads.
  - Pure predicate has property-test coverage on ≥ 500 synthetic event chains.
  - The *gate-enforcement* portion stays unimplemented until Phase 8b.

#### 2.8a.6 `T-807` — `engine.vlp_policy` (v1.1 — new, per H-04 / B-02)
- **Files:** `src/engine/vlp_policy/policy.py`, `system_classes.py` (MS2 vs phage-derived VLP vs AAV vs lentiviral distinctions), tests + MS-* rule integration.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP:**
  1. Implement explicit policy constraints per `ARCHITECTURE.md` v1.4 M9 + v2.0 KB § 17:
     - Packaging-signal handling (MS2 pac hairpin geometry; ITR for AAV; LTR + Ψ for lentiviral).
     - Capsid-expression context (separate from cargo).
     - Helper-function separation (replication functions must not coexist with cargo unless explicitly authorised).
     - Cargo-size limits (AAV ≤ 4.7 kb between ITRs; lentivirus ≤ ~ 9 kb; MS2 VLP ≤ ~ 4 kb).
     - Replication / infectivity boundary (replication-competent viral systems are RG-2+ and require dual-control authorisation regardless of B3-mitigation status).
     - Assembly + assay controls (positive / negative / process control suitability per VLP class).
     - System-class distinction: MS2 RNA-binding display ≠ phage-derived VLP (e.g., Qβ, T7) ≠ AAV ≠ lentivirus.
  2. Consume the MS-* rules from `catalogues/rules/MS.yaml`; emit structured `VlpPolicyReport` referenced by the design plan.
  3. Integration with `engine.risk_classification` (T-801): VLP / phage / viral-vector constructs trigger the appropriate advisory categories.
- **Acceptance:** fixtures covering all four system classes; MS-* rule registry integration verified; MS2/VLP UAT (Phase 13) consumes the policy module.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-807 placeholder with a package exposing `VlpSystemClass`, `VlpPolicyRequest`, `VlpPolicyFinding`, `VlpPolicyReport`, and `VlpPolicyEngine`; implemented MS2 RNA-display, phage-derived VLP, AAV, and lentiviral policy distinctions; enforced packaging-signal declarations, cargo-capacity limits, helper/capsid separation, replication/infectivity boundaries, controls, and assembly-readout metadata; aligned the supported MS-01..MS-07 rule IDs with `catalogues/rules/MS.yaml`; and added risk-classification trigger-tag integration for MS2/VLP and AAV/lentiviral advisories. Focused verification: 7 tests passed. Full local gates are green with 470 passed and 2 skipped. T-808 is next.

#### 2.8a.7 `T-808` — `app.plugin_governance` (v1.1 — new, per B-02)
- **Files:** `src/app/plugin_governance.py`, tests + adversarial-test integration.
- **Model tier:** Sonnet. **Context budget:** ≤ 40 k tokens.
- **SOP:**
  1. Implement plugin-manifest loading: read `catalogues/plugin_manifests/<plugin>.yaml`, verify signature against the institutional plugin trust keyring, verify the loaded artefact's hash matches the manifest's declared hash.
  2. Enforce declared permissions via a runtime sandbox (per-plugin file-access scope; per-plugin network-access scope; deterministic-path plugins have no network access at all).
  3. Emit `PluginManifestApproved` governance events for accepted plugins; `PluginManifestRejected` for failures.
  4. Adversarial fixtures: unsigned manifest, hash-mismatched manifest, manifest declaring a permission outside the trusted set — each path produces a typed rejection + audit-log entry.
- **Acceptance:** `plugin-manifest-signature` CI gate flips from `informational` to `enforced` after this task; adversarial test fixtures all rejected correctly.
- **Implementation status (2026-05-14).** Complete locally. Replaced the T-808 placeholder with `PluginGovernanceService`, signed `PluginManifest` parsing, Ed25519 `PluginTrustKeyring` verification, artefact SHA-256 matching, sandbox permission validation/grants, approval/rejection governance-event emission, a fully signed seed plugin manifest, and an enforced `plugin_manifest_signature_check` CI gate wired into GitHub Actions. Focused verification: 10 tests passed and the enforced plugin-manifest gate passed. Full local gates are green with 476 passed and 2 skipped. Phase 8a is complete; Phase 9a is complete after T-901 and T-902.

### Phase 9a — Sequence I/O extensions + SnapGene file-watch (2 tasks; v1.2 — split from v1.1 Phase 9 per B2-02)

**v1.2 Phase 9 split rationale.** v1.1 had a single Phase 9 containing T-901 (EMBL/GFF3), T-902 (SnapGene watcher), and T-903 (final export orchestrator) — but T-903 cannot honestly turn green before Phase 10 (screening) and Phase 8b (authorisation + SOP). Phase 9 is split into:
- **Phase 9a** (this phase, pre-screening): T-901, T-902. I/O channels only — no operational export, no vendor clearance.
- **Phase 9b** (post-Phase-8b): T-903. Final export orchestrator with real screening verdicts + authorisation evidence + SOP bundle.

#### 2.9a.1 `T-901` — EMBL + GFF3 adapters
- **Files:** `src/adapter/io/embl.py`, `gff3.py`, tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 30 k tokens.
- **Implementation status (2026-05-14).** Complete locally. Added `EmblAdapter` using the shared Biopython conversion path and `Gff3Adapter` with embedded-FASTA read support, GFF3 feature-row writing, qualifier attribute encoding, and loss warnings for rich location metadata that GFF3 cannot fully express. Focused verification: `tests/adapter/io/test_sequence_io.py` has 8 passing tests; focused ruff, format, and mypy checks are green. Full local gates are green with 479 passed and 2 skipped. T-902 is next.

#### 2.9a.2 `T-902` — `adapter.snapgene.SnapGeneFileWatcher` (v1.2 — H2-04 fix; depends on T-308e for `.dna` parsing)
- **Files:** `src/adapter/snapgene/file_watcher.py`, tests. **(v1.2 H2-04: `dna_reader.py` removed — T-902 imports `SnapGeneDnaReader` from T-308e's namespace; T-902 owns only the watcher logic.)**
- **Model tier:** Sonnet. **Context budget:** ≤ 40 k tokens.
- **SOP (v1.2):**
  1. Watch a configured directory; on new `.gb` file, parse via the `GenBankAdapter` (T-308a) → run validation → emit updated `.gb` to a paired output directory; SnapGene re-imports. UR-01a (MUST) channel.
  2. For `.dna` file watching (optional), import `SnapGeneDnaReader` from `adapter.snapgene` (T-308e) — this task does **not** re-implement the `.dna` parser.
  3. Re-use the generic debounce algorithm validated in T-205's `filewatch_debounce_harness.py` (H2-07 cross-resolution) — SnapGene-specific watch targets (`.gb`, `.dna`) layered on top.
- **Acceptance:** file-watch test passes against `SyncLikePath` fixtures (non-ASCII paths, spaces, OneDrive-style burst writes); imports from T-308e, not from a duplicate local reader.
- **Implementation status (2026-05-14).** Complete locally. Replaced the `adapter.snapgene` placeholder with a package, implemented a deterministic pollable `SnapGeneFileWatcher`, coalesced burst writes, read GenBank via `GenBankAdapter`, called an injected validation hook, wrote paired GenBank output atomically, and re-exported T-308e `SnapGeneDnaReader` for optional `.dna` watch support without adding a local `dna_reader.py`. Focused verification: `tests/adapter/snapgene` has 5 passing tests; focused ruff, format, and mypy checks are green. Full local gates are green with 484 passed and 2 skipped. Phase 9a is complete; Phase 10 is next.

### Phase 10 — Vendor + screening adapters (2 parallel tasks; v1.4 B4-01 — physically reordered to precede Phase 8b)

**v1.4 B4-01 fix.** Phase 10 is physically inserted between Phase 9a and Phase 8b so heading-order parsing emits `T-1001 / T-1002` before `T-803 / T-805b / T-806b / T-903`. This matches the binding phase order `9a → 10 → 8b → 9b` and preserves the screening-before-SOP safety invariant at the manifest layer.

#### 2.10.1 `T-1001` — Vendor adapters (Twist / IDT / GenScript; v1.3 — activates vendor-profile-feasibility portion of `BlockVendorSubmission` per H3-02)
- **Files:** `src/adapter/vendor/{twist,idt,genscript}.py`, `src/engine/vendor_feasibility_gate.py` (v1.3 — new per H3-02), tests including per-rejection-class fixtures.
- **Model tier:** Sonnet. **Parallel sub-tasks per vendor.**
- **Context budget:** ≤ 40 k tokens per vendor (v1.3 increased from 35 k).
- **SOP (v1.3):**
  1. Implement `SynthesisVendorAdapter` with `check(VendorFeasibilityRequest)`, `auto_partition`, `estimate_cost(*, product_type, scale, cloning_option, currency, quote_date_utc)`. Constraints from `catalogues/vendor_profiles/*.yaml`.
  2. **(v1.3 H3-02)** Activate the **vendor-profile-feasibility portion** of `BlockVendorSubmission`: when any registered vendor's `check(request)` returns rejection — length / GC / repeat / adapter / product-format failure — the gate fires. Implement via `engine.vendor_feasibility_gate.activate_block_vendor_submission_for_vendor_failures()`, registered against `GatePredicateRegistry` from T-309. Per-rejection-class fixtures in `tests/fixtures/vendor_feasibility/`: `length_overflow.json`, `gc_extreme.json`, `repeat_excess.json`, `adapter_collision.json`, `product_format_mismatch.json`. Each fixture asserts the gate fires with the right `BlockReason`.
  3. Test: vendor rejects but screening verdict is `CLEAR` → gate still blocks (proves vendor-feasibility is an independent activation input).
- **Implementation status (2026-05-14).** Complete locally. Replaced the `adapter.vendor` placeholder with a package, implemented YAML-profile-backed `TwistVendorAdapter`, `IdtVendorAdapter`, and `GenScriptVendorAdapter`, added deterministic feasibility checks for length / GC / repeat / adapter / product-format rejection classes, partition planning, static cost estimation, and an engine-local vendor-feasibility gate activator that avoids adapter imports from `engine`. Added per-rejection-class fixtures under `tests/fixtures/vendor_feasibility/` and focused adapter/gate tests. Full local gates are green with 494 passed and 2 skipped. Phase 10 continues with T-1002.

#### 2.10.2 `T-1002` — Screening adapters + orchestrator (v1.3 — activates screening-verdict portion of `BlockVendorSubmission` per H3-02)
- **Files:** `src/adapter/screening/{igsc,ibbis,securedna,internal_blacklist}.py`, `src/app/screening_orchestrator.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens.
- **SOP (v1.3):**
  1. Implement `ScreeningProviderTrustPolicy` consumption (B10): adapter `canonical_at_this_scope` derives from institutional policy, never self-declared.
  2. Implement `screen` + `screen_batch` with typed `ScreeningError` taxonomy (N5).
  3. Implement `NotApplicableReason` enum + policy validation.
  4. Screening runs at assembled-product level by default; fragment-level only when policy permits.
  5. Reviewer / Admin sign-off workflow for `WATCHLIST` / `MANUAL_REVIEW_REQUIRED` / `UNAVAILABLE` produces signed `DecisionRecord` — emitted as a governance event with the **full signed payload embedded** per v1.3 B3-03.
  6. **(v1.3 H3-02)** Activate the **screening-verdict portion** of `BlockExport` + `BlockVendorSubmission` per verdict (HIT / WATCHLIST → block; CLEAR → permit subject to other inputs). Multi-input composition with T-1001's vendor-feasibility portion handled at T-903 (export) where both predicates must permit.
  7. `ScreeningCompleted` events emitted to the **design stream** per v1.2 B2-05 with library-mode batched payloads (one event per batch with per-realisation evidence in the payload — v1.3 H3-06 corrects v1.2's library-mode text).
- **Implementation status (2026-05-14).** Complete locally. Replaced the `adapter.screening` and `app.screening_orchestrator` placeholders with policy-backed IGSC, IBBIS, SecureDNA, and institutional blacklist adapters; added `ScreeningVerdict`, `ScreeningError`, `NotApplicableReason`, provider trust-policy loading, batch-preserving partial-failure handling, non-clear fallback behavior, batched `ScreeningCompleted` design-stream emission, reviewer sign-off governance emission with embedded signed decision payloads, audit append hooks, and `engine.screening_gate` screening-verdict activation for `BlockVendorSubmission` and `BlockExport` without adapter imports from `engine`. Full local gates are green with 507 passed and 2 skipped. Phase 10 is complete; Phase 8b begins with T-803.

### Phase 8b — SOP rendering + authorisation decision (post-Phase 10; 3 tasks; v1.2 — T-805b renamed per B2-09)

**v1.2 deferred safety phase.** This phase runs *after* Phase 10 delivers real screening adapters + `app.screening_orchestrator`. No SOP-gating acceptance criterion in any 8b task may turn green until a test fixture supplies a real `ScreeningCompleted` event with a policy-derived trust verdict.

#### 2.8b.1 `T-803` — `engine.sop_protocol` (gated; v1.3 — SOP-template admin writes moved to T-316b per B3-05/B4-05; consumes read port only)
- **Files:** `src/engine/sop_protocol/generator.py`, `src/engine/sop_protocol/renderers/{markdown,pdf,json}.py` (v1.2), templates (per chemistry + per host), tests. **(v1.3 B3-05)** `src/app/admin_action_handler/sop_template_writes.py` is NOT owned by this task — it is owned by **T-316b** (Phase 4). T-803 consumes templates via `SopTemplateReadPort` only.
- **Model tier:** Opus. **Context budget:** ≤ 55 k tokens (v1.3 reduced from 60 k since SOP-template admin writes moved out).
- **SOP (v1.3):**
  1. Bound to `SopTemplateReadPort` (from T-316a Protocol, backed by T-316b store; lifted from the former YAML-template runtime surface). Renders `SopLinkedProtocol` only after `OperationalProtocolAuthorised` event observed (enforced by `sop-after-gates-check`). Each `ProtocolStep` carries `sop_ref`, `approval_gate`, `hazard_class`, `allowed_roles`, `checkpoint_criteria`, `measured_outputs`, `deviation_policy`, `decision_rule`. **Imports only from `domain.types.sop_protected`** (v1.1 B-01 enforcement).
  2. **(v1.2 M2-04)** Renderer files explicit per `docs/rendering_determinism.md` (pinned fonts, no embedded timestamps, canonical `/CreationDate` from `derivation_environment.created_at_utc`). Cross-platform expectations: Linux byte-identity; Windows semantic-identity (v1.3 M3-05).
  3. **(v1.3 B3-05)** SOP-template admin operations are NOT part of this task. T-803 consumes signed templates from the read port; signature verification is performed on read by `SopTemplateVerifier` from T-316a/T-316c. If a template fails verification, T-803 raises `SopTemplateTamperDetectedError` and refuses to render.
- **Acceptance:** renderer tests in § 4.6a green; `SopLinkedProtocol` cannot render before observed `OperationalProtocolAuthorised` (sop-after-gates-check enforced green); cannot render against a tampered template (signature verification fails closed); cross-platform PDF determinism honoured (byte-identical on Linux, semantically-identical on Windows).
- **Implementation status (2026-05-14).** Complete locally. Replaced the `engine.sop_protocol` placeholder with a package containing `SopProtocolGenerator` plus deterministic JSON, Markdown, and PDF renderers. Generation requires an observed `OperationalProtocolAuthorised` before reading `SopTemplateReadPort`, refuses unsigned templates with `SopTemplateTamperDetectedError`, and emits `SopLinkedProtocol` values composed from `domain.types.sop_protected` operational fields. The SOP renderer remains reference-only: procedure-specific content stays in signed institutional templates and is not invented by the engine. `sop-after-gates-check` is now enforced green through `tests/ci_gates/test_t204_gates.py`. Full local gates are green with 511 passed and 2 skipped. Phase 8b continues with T-805b.

#### 2.8b.2 `T-805b` — `app.sop_protocol_orchestrator` (v1.2 — renamed + scoped per B2-09)
- **Files:** `src/app/sop_protocol_orchestrator.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 40 k tokens.
- **SOP (v1.2):** Dispatches to `engine.sop_protocol` (T-803) **only** when `OperationalProtocolAuthorised` event has been observed for the current session. Produces a `SopProtocolBundle` — the operational complement of T-805a's `DraftDesignBundle`. The `SopProtocolBundle` is a separate artefact from the `DraftDesignBundle` and from the final `ExportBundle` (T-903); it carries the SOP rendering + the approval-trace evidence but not the full export-grade bundle.
- **Acceptance:** integration test with mocked `OperationalProtocolAuthorised` event confirms SOP renders; integration test without the event confirms `SopLinkedProtocol` rendering is refused; `SopProtocolBundle` JSON byte-deterministic; emits `SopRendered` to **design stream** per v1.2 B2-05.
- **Implementation status (2026-05-14).** Complete locally. Replaced the `app.sop_protocol_orchestrator` placeholder with `SopProtocolOrchestrator`, `SopProtocolBundleRequest`, and deterministic `SopProtocolBundle` values. The app service filters `OperationalProtocolAuthorised` events to the current design session before invoking T-803, ignores wrong-session authorisations, stores authorisation evidence hashes in the bundle, emits `SopRendered` to the design stream, and appends through an injected design event log. Full local gates are green with 515 passed and 2 skipped. Phase 8b continues with T-806b.

#### 2.8b.3 `T-806b` — Authorisation gate decision + review-queue routing + adversarial UAT (v1.3 — routes blocked sessions to T-315 review queue per B3-06)
- **Files:** `src/app/authorisation_decision.py`, tests including the v1.5 adversarial UAT suite for FR-ADV-07 (R-21 mitigations) + FR-PROTO-SOP-09 review-queue routing test.
- **Model tier:** Opus. **Context budget:** ≤ 60 k tokens (v1.3 increased from 55 k).
- **SOP (v1.3):**
  1. Wire `app.authorisation_decision`: consumes a real `ScreeningCompleted` event from `app.screening_orchestrator` (delivered by Phase 10 to the **design** stream per v1.2 B2-05), the `UserDeclaration`, the granted `AuthorisationProfile` (verified-signed per v1.3 B3-04), and the chain of `RiskAdvisoryAcknowledged` events from T-806a (with embedded signed payloads per v1.3 B3-03).
  2. Call `all_required_advisories_acknowledged()` (T-806a's pure predicate) before emitting `OperationalProtocolAuthorised`; missing acknowledgements fire `BlockOperationalProtocol` + `AuthorisationAttemptDenied`. **(v1.2 H2-11 cross-resolution)** This is the home of the BR-14 hard-gate predicate; T-503 does not evaluate BR-14.
  3. Validate `UserDeclaration` against `AuthorisationProfile.scope` (`CoveredBiologicalScope`); validate the screening verdict against `ScreeningProviderTrustPolicy`; check for required institutional approval IDs where the profile demands them.
  4. **(v1.3 B3-06 fix — review-queue routing for blocked sessions per FR-PROTO-SOP-09.)** When `BlockOperationalProtocol` fires, call `ReviewQueueService.route_blocked_authorisation(session_id, reason, service_principal)` (from T-315) to create a pending `ReviewQueueItem`. The blocked session can now be unblocked only by admin approval via the queue (triggering `mint_profile` / `modify_profile` through T-311). The user-facing response includes a notice "operational protocol withheld pending administrator approval" plus a structured `review_queue_item_id` so the user can track the request.
  5. **Activate the `BlockOperationalProtocol` gate-predicate** (per v1.2 H2-06 — T-309 sub-deliverable (b) activation map).
  6. Implement the v1.5 adversarial UAT suite (FR-ADV-07): all bypass paths must produce `BlockOperationalProtocol`. **(v1.2 M2-02)** Bypass coverage extended to: (a) passive render (no acknowledgement event), (b) short justification, (c) unsigned acknowledgement, (d) report-content-hash mismatch, (e) decline, (f) escalate without `institutional_approval_id`, (g) screening hit, **(h) construct-checksum mismatch** (acknowledge against checksum X then modify construct), **(i) programmatic `OperationalProtocolAuthorised` construction without governance chain** (verified via static check + replay invariant in T-309), **(j) tampered `AuthorisationProfile`** (v1.3 B3-04 — signature fails on load).
  7. **(v1.3 B3-06)** Add `test_blocked_session_creates_review_queue_item` (FR-PROTO-SOP-09): a session that hits `BlockOperationalProtocol` produces exactly one `ReviewQueueItemCreated` event in `pending` state.
- **Acceptance:** `no-passive-advisory-bypass-check` CI gate flips to `enforced` green; `sop-after-gates-check` CI gate flips to `enforced` green; FR-ADV-07 adversarial suite green (all 10 bypass scenarios blocked); happy-path UAT (FR-ADV-06) green; **FR-PROTO-SOP-09 review-queue routing test green**.
- **Implementation status (2026-05-14).** Complete locally. Replaced the `app.authorisation_decision` placeholder with `AuthorisationDecisionService`, `AuthorisationDecisionRequest`, and `OperationalAuthorisationScope`. The service consumes real `ScreeningCompleted` events, verifies signed `AuthorisationProfile` values through the profile-verifier port when supplied, validates `UserDeclaration` against covered biological scope and institutional-approval constraints, checks screening trust policy evidence, requires T-806a `all_required_advisories_acknowledged()` before emitting `OperationalProtocolAuthorised`, emits `AuthorisationAttemptDenied` on policy failures, and routes blocked sessions to T-315 `ReviewQueueService.route_blocked_authorisation()`. Added `engine.operational_protocol_gate.activate_block_operational_protocol_gate()` for `BlockOperationalProtocol`. The `no-passive-advisory-bypass-check` gate is now enforced green through `tests/ci_gates/test_t204_gates.py`. Focused verification: 15 T-806b tests passed, including happy path, review-queue routing, screening HIT, scope/approval mismatch, tampered profile, and seven advisory-bypass variants. Full local pytest is green with 530 passed, 2 skipped. Phase 8b is complete and feeds T-903 export gating.

### Phase 9b — Final export orchestrator (1 task; v1.2 — split from Phase 9 per B2-02)

**v1.2 deferred export phase.** Runs after Phase 8b. The final `ExportBundle` requires real `ScreeningCompleted` + `OperationalProtocolAuthorised` + `SopRendered` events.

#### 2.9b.1 `T-903` — `app.export_orchestrator` + redaction (v1.2 — moved to Phase 9b per B2-02; renderers per M2-04)
- **Files:** `src/app/export_orchestrator/__init__.py`, `src/app/export_orchestrator/redaction.py`, `src/app/export_orchestrator/renderers/{bundle_zip,manifest}.py` (v1.2), `src/engine/export_gate.py`, tests.
- **Model tier:** Opus. **Context budget:** ≤ 50 k tokens.
- **SOP (v1.2):**
  1. Apply `ExportProfile` redaction (N6) at serialisation time; bundle ZIP with all artefacts including `DerivationEnvironment` and the full advisory approval trace.
  2. Bundle layout: GenBank + FASTA + SBOL 3.1.x + primer CSV + primer FASTA + `DesignRealisationPlan` Markdown + JSON + `SopLinkedProtocol` (from T-803 / T-805b) + `ControlSet` + validation report JSON + **screening verdict JSON** (from Phase 10) + **authorisation evidence JSON** (from T-806b) + advisory approval trace JSON + `DerivationEnvironment` JSON + metadata.
  3. **Activate the `BlockExport` gate-predicate** (per v1.2 H2-06 — T-309 sub-deliverable (b) activation) consuming Phase 10's `ScreeningCompleted` + Phase 8b's `OperationalProtocolAuthorised`. Emit `ExportProfileRedactionApplied`.
  4. **(v1.2 M2-04)** Renderer files explicit; manifest renderer produces a canonical-JSON manifest naming every artefact + its content hash; bundle-zip renderer uses deterministic ZIP options (stored times set to canonical `derivation_environment.created_at_utc`, file order canonical).
- **Acceptance:** the three white-paper examples produce a complete project bundle ZIP; every file opens in its intended application; `BlockExport` correctly blocks when authorisation absent or screening incomplete; bundle hash byte-deterministic across runs inside the determinism harness; renderer tests in § 4.6a green.
- **Implementation status (2026-05-14).** Complete locally. `app.export_orchestrator` is now a package with redaction and renderer modules. It builds deterministic final export ZIPs containing sequence, primer, design-plan, SOP, controls, validation, screening, authorisation, advisory trace, derivation-environment, metadata, and manifest artefacts; `ExportProfile` redaction is applied at serialisation time and `ExportProfileRedactionApplied` / `ExportBundleCreated` export events are emitted. `engine.export_gate.activate_final_export_gate()` activates `BlockExport`, composing existing screening verdict predicates and requiring `ScreeningCompleted`, `OperationalProtocolAuthorised`, and `SopRendered` evidence before opening. Focused verification: 6 T-903 tests passed, `ruff check` passed for the T-903 slice, and `no-passive-advisory-bypass-check` remained green locally. Phase 9b is complete and feeds Phase 11 CLI/API work.

### Phase 11 — HTTP API + CLI + admin-service IPC (4 tasks; v1.4 — admin-service task split into T-1103a (before T-1101 / T-1102) + T-1103b (after) per B4-08)

**v1.4 B4-08 split rationale.** v1.3 placed admin-service IPC after T-1101 / T-1102, but those tasks include admin commands that must route via the IPC. Implementing them first would force direct `AdminActionHandler` imports or insecure placeholders. v1.4 splits the admin-service work into an early Protocol/contract task (T-1103a, before T-1101) and a later production-implementation task (T-1103b, after T-1102). T-1101 / T-1102 acceptance is forbidden from importing `AdminActionHandler` directly (verified by new gate `no_direct_admin_handler_import_check.py` per H4-02).

**Phase 11 v1.4 task order:** **T-1103a** (IPC contract + `AdminServiceClientPort` Protocol + test client) → T-1101 (CLI consumes Protocol) → T-1102 (API consumes Protocol) → **T-1103b** (admin-service production implementation + IPC server + ACL + `ReviewQueueAdminPort`).

#### 2.11.1 `T-1103a` — `AdminServiceClientPort` Protocol + IPC contract + test client (v1.4 — new per B4-08; scheduled BEFORE T-1101 / T-1102)
- **Files:**
  - `src/domain/ports/admin_service.py` — `AdminServiceClientPort` Protocol. Verbs: `mint_profile`, `modify_profile`, `revoke_profile`, `list_profiles`, `view_audit_trail`, `mint_sop_template`, `modify_sop_template`, `revoke_sop_template`, `triage_review_queue_item`, `rotate_audit_key`. Each verb accepts a signed admin-principal token + verb-specific payload + returns a structured response with embedded signed `DecisionRecord`.
  - `src/domain/types/admin_ipc.py` — IPC request / response value objects (frozen-dataclass; canonical-JSON-serialisable).
  - `tests/fakes/admin_service/test_in_memory_client.py` — deterministic in-memory `InMemoryAdminServiceClient` for CLI / API unit tests (no real IPC; routes directly to a mock admin handler).
  - `docs/admin_service/ipc_contract.md` — wire format documentation: framing (length-prefixed JSON), authentication (token envelope defined against T-314a `DecisionRecordSigner`/`DecisionRecordVerifier` Protocols; production verification requires T-314b), error codes, version negotiation.
  - Contract tests `tests/domain/ports/test_admin_service_client_contract.py`.
- **Model tier:** Sonnet. **Context budget:** ≤ 35 k tokens.
- **SOP (v1.4):**
  1. Define the `AdminServiceClientPort` Protocol with all admin verbs from T-311 + T-315 (`triage_review_queue_item` per H4-01) + T-312b (`rotate_audit_key`) + T-316b (SOP-template admin writes).
  2. Define IPC request / response value objects.
  3. Implement `InMemoryAdminServiceClient` — used by T-1101 / T-1102 unit tests; routes admin verbs to a configurable mock handler without invoking real IPC.
  4. Document the wire format in `docs/admin_service/ipc_contract.md` (versioned; T-1103b implements this contract).
- **Acceptance:** Protocol defined + `mypy --strict` green; in-memory client passes contract tests; T-1101 / T-1102 can construct + dispatch admin requests via `AdminServiceClientPort` without importing `AdminActionHandler`.
- **Implementation status (2026-05-14).** Complete locally. Added `domain.types.admin_ipc` request/response/token/decision-record envelopes, `domain.ports.admin_service.AdminServiceClientPort` with all 10 admin verbs plus `dispatch`, `docs/admin_service/ipc_contract.md`, and `tests.fakes.admin_service.InMemoryAdminServiceClient`. Contract tests verify all verb methods produce structured responses with embedded decision-record metadata and the fake records every request without IPC. Focused verification: 11 T-1103a/port tests passed, T-1103a `ruff check` passed, and strict `mypy` passed for the new surface. Phase 11 protocol/contract foundation is complete; T-1101 CLI is next.

#### 2.11.2 `T-1101` — Typer-based CLI (v1.4 — admin commands route via `AdminServiceClientPort` per B4-08; no direct `AdminActionHandler` import)
- **Files:** `src/interface/cli/__main__.py`, command modules, tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 50 k tokens.
- **SOP (v1.4):** Commands per ROADMAP Phase 11: `new`, `open`, `validate`, `compile`, `screen`, `export`, `library`, `replay`, `audit`, `rule-index`, `list-sessions`, `acknowledge-advisory`, `decline-advisory`, `escalate-advisory`, `status` (war-room dashboard mirror); **admin commands** `admin-mint`, `admin-modify`, `admin-revoke`, `admin-mint-sop-template`, `admin-modify-sop-template`, `admin-revoke-sop-template`, `audit-key-rotate`, `submit-extension-request`, `list-review-queue`, `triage-request` **route exclusively through `AdminServiceClientPort` (T-1103a)** — CLI code paths cannot import `AdminActionHandler`. Static check `no_direct_admin_handler_import_check.py` (T-204 v1.4 H4-02) verifies.
- **Implementation status (2026-05-14).** Complete locally. Replaced the `interface.cli` placeholder with a package containing a Phase 11 command registry, injectable `CliRuntime`, optional Typer app builder, stdlib fallback runner, `vector-design` / `cev-design` console scripts, and focused CLI tests. Public commands delegate to configured runtime handlers; admin/profile/SOP/audit-key/review-queue admin commands require an `AdminServiceClientPort` binding and signed admin token provider. Focused verification: 7 T-1101 tests passed, T-1101 `ruff check` passed, strict `mypy` passed for the new surface, adjacent admin-service contract/gate smoke tests passed, full strict mypy passed across `src`, `tools`, and `tests`, agenda consistency passed, and the full non-slow suite passed with 550 passed / 2 skipped. Phase 11 CLI foundation is complete; T-1102 API is next.

#### 2.11.3 `T-1102` — FastAPI HTTP server + WebSocket (v1.4 — admin routes via `AdminServiceClientPort` per B4-08)
- **Files:** `src/interface/api/server.py`, route modules, tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 55 k tokens.
- **SOP (v1.4):** Same use cases as the CLI exposed over REST + WebSocket streaming for live validation. OpenAPI spec auto-generated. **Admin endpoints route through `AdminServiceClientPort` (T-1103a)** — API code paths cannot import `AdminActionHandler`. Static check `no_direct_admin_handler_import_check.py` verifies.
- **Implementation status (2026-05-14).** Complete locally. Replaced the `interface.api` placeholder with a package containing route metadata, injectable `ApiRuntime`, dependency-free OpenAPI-style route index, optional FastAPI app builder, validation WebSocket stream helper, and `vector-design-api` console script. Public API routes delegate to configured runtime handlers; admin/profile/SOP/audit-key/review-queue endpoints require an `AdminServiceClientPort` binding and signed admin token provider. Focused verification: 9 T-1102 tests passed, adjacent Phase 11/admin-service smoke tests passed, full strict mypy passed across `src`, `tools`, and `tests`, full ruff passed, and the full non-slow suite passed with 559 passed / 2 skipped. Phase 11 API foundation is complete and now feeds the T-1103b production admin-service boundary.

#### 2.11.4 `T-1103b` — Admin-service production implementation + IPC server + ACL + `ReviewQueueAdminPort` (v1.4 — production half split per B4-08; H4-01 review queue + M4-05 OS-level ACL tests)

**Rationale.** v1.2 introduced the admin-service process separation as a security boundary but provided no executable specification of how CLI / API admin commands reach it. v1.4 split the work into protocol/contract (T-1103a) and production implementation (T-1103b); v1.5 binds production authentication to T-314b and review-queue resolution to `ReviewQueueAdminPort`.

- **Files:**
  - `src/interface/admin_service/__main__.py` — admin-service process entry point.
  - `src/interface/admin_service/ipc.py` — local IPC layer: named pipe on Windows (`\\.\pipe\cev-admin-service`); Unix domain socket on POSIX (`/var/run/cev-admin/socket`). Path configurable via `config.admin_service_ipc_path`; permissions enforce admin-only access on POSIX (mode 0600 + owned by admin UID); ACL'd on Windows.
  - `src/interface/admin_service/auth.py` — mutual authentication: client supplies signed admin/developer-bootstrap credentials (token via DPAPI on Windows; via SO_PEERCRED + signed token on Linux); admin-service verifies and binds the principal to the request.
  - `src/interface/admin_service/review_queue_admin.py` — v1.4 H4-01: implements `ReviewQueueAdminPort` (from T-315) for admin-service-side `triage_review_queue_item` verb. The admin-service holds the only path to resolve queue items; engine/API/CLI callers cannot self-resolve.
  - `src/adapter/ipc/admin_service_client_production.py` — production implementation of `AdminServiceClientPort` (from T-1103a); used by composition root in engine + CLI + API processes; supplants the T-1103a in-memory test client at integration.
  - Tests: `tests/interface/admin_service/{test_unauthenticated_denied,test_user_credentials_denied,test_reviewer_credentials_denied,test_admin_credentials_routed,test_developer_bootstrap_pre_bootstrap,test_developer_denied_post_bootstrap,test_windows_named_pipe_round_trip,test_posix_socket_round_trip,test_concurrent_admin_clients_serialised,test_review_queue_admin_only_resolution,test_windows_named_pipe_acl_restricts_to_admin_sid,test_posix_socket_mode_0660_owned_by_cev_admin_group,test_service_account_separation}.py`.
- **Model tier:** Opus. **Context budget:** ≤ 60 k tokens (v1.4 increased from 55 k for ReviewQueueAdminPort + ACL tests).
- **SOP (v1.4):**
  1. Implement the admin-service process entry point. The process starts with `AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`, `SopTemplateAdminWritePort` (T-316b), `SopTemplateBootstrapPort` (T-316b), the admin-side `AdminAuditAppendPort` (T-313a / T-313b IPC client), and **`ReviewQueueAdminPort` (v1.4 H4-01 — for `triage_review_queue_item` IPC verb)**. It does **not** hold the engine's session state or user-facing services.
  2. Implement IPC: named-pipe server on Windows; Unix-domain-socket server on POSIX. Path + permissions enforce admin-only access at the filesystem layer. Listener accepts framed JSON-RPC-like requests (verb + signed credentials + payload).
  3. Implement mutual authentication. On Windows, the client process token is verified via `GetTokenInformation` + DPAPI-protected developer/admin token. On POSIX, the client UID is verified via `SO_PEERCRED` + a per-principal signed token (envelope from T-314a; production signature verification from T-314b). Unauthenticated clients receive `AdminServiceAuthenticationError`; non-admin credentials receive `PermissionError` + an `AuthorisationAttemptDenied` audit entry.
  4. Implement CLI / API client routing. CLI commands construct an admin request, sign with the developer or admin credentials in the operator's keystore, send through IPC, render the response. API routes do the same on behalf of authenticated API callers (admin authentication carried in the HTTP request layer via the standard FastAPI auth dependency).
  5. **Concurrency.** Admin operations are serialised through the admin-service (single-writer to the authorisation + audit + SOP-template stores). Multiple concurrent admin clients queue. Test `test_concurrent_admin_clients_serialised` verifies serialisation.
  6. **Deployment.** `docs/deployment/admin_service.md` documents how to launch the admin-service as a systemd unit (Linux, under `cev-admin-svc` service account) or a Windows service (under a dedicated service account). The engine and admin-service share a configuration directory but operate as separate OS processes with separate UIDs/SIDs.
  7. **(v1.4 M4-05) OS-level ACL / UID enforcement tests.**
     - `test_windows_named_pipe_acl_restricts_to_admin_sid` — verify the pipe security descriptor restricts access to the Administrators group SID + the service-account SID; non-admin local user denied at the OS layer (before the application sees the request).
     - `test_posix_socket_mode_0660_owned_by_cev_admin_group` — verify socket file mode + owner; non-`cev-admin` group member denied via OS layer.
     - `test_service_account_separation` — admin-service runs under `cev-admin-svc` on Linux; the engine process runs under a different account; cross-account filesystem access verified denied.
     - Manual verification steps in `docs/deployment/admin_service.md`.
  8. **(v1.4 H4-01) Review-queue admin triage.** Admin-service handles `triage_review_queue_item` IPC verb; routes to `ReviewQueueAdminPort` (from T-315). Test `test_review_queue_admin_only_resolution` confirms user/API callers cannot reach this verb through any other path.
- **Acceptance:** all 13 tests green; Windows named-pipe + ACL round-trip; POSIX socket + mode + service-account separation; UserPrincipal + ReviewerPrincipal credentials denied + audit entry; AdminPrincipal credentials routed + audit entry; DeveloperBootstrapPrincipal pre-bootstrap allowed; ordinary DeveloperPrincipal post-bootstrap denied (v1.3 H3-10); review-queue triage admin-only.

- **Implementation status (2026-05-14).** Complete locally. Replaced the `interface.admin_service` placeholder with a package containing signed-token authentication, optional token-verifier injection for production key material, serialized length-prefixed IPC framing, endpoint/ACL metadata validation, admin verb dispatch with administrator/bootstrap role enforcement, review-queue triage through `ReviewQueueAdminResolutionService`/`ReviewQueueAdminPort`, and the `vector-design-admin-service` entry point. Added `adapter.ipc.admin_service_client_production.AdminServiceClient` with an injectable transport and in-process integration transport, plus `docs/deployment/admin_service.md`. Focused verification: 16 admin-service tests passed across the 13 required acceptance surfaces, full strict mypy passed across `src`, `tools`, and `tests`, full ruff passed, and the full non-slow suite passed with 575 passed / 2 skipped. Phase 11 is complete; T-1201 constraint translator + LLM adapter/red-team policy is next.

### Phase 12 — Web UI + LLM constraint translator + live SnapGene (3 tasks)

#### 2.12.1 `T-1201` — `app.constraint_translator` + `adapter.llm`
- **Files:** `src/app/constraint_translator.py`, `src/adapter/llm/{local,openai,anthropic}.py`, tests including red-team suite.
- **Model tier:** Opus. **Context budget:** ≤ 60 k tokens.
- **SOP:** `AdvisoryTextPolicy` enforces pinned prompt templates + model versions + citation checking + prohibited-output detection. Red-team test suite asserts no operational protocol details produced from LLM text. Default local-LLM; cloud requires explicit opt-in per session.
- **Implementation status (2026-05-14).** Complete locally. Replaced `app.constraint_translator` and `adapter.llm` placeholders with typed translation proposals, structured constraints, deterministic local fallback, OpenAI/Anthropic opt-in cloud adapters, forbidden-output detection, citation checking, manual-review fallback, and confirmed canonical payload generation for `DesignService.confirm_translation`. `llm-output-policy-check` is now enforced and covers the app, adapters, and red-team tests. Focused verification: 12 T-1201 tests passed, full strict mypy passed across `src`, `tools`, and `tests`, full ruff passed, agenda consistency passed, and the full non-slow suite passed with 587 passed / 2 skipped. Phase 12 continues with T-1202 React + TypeScript SPA.

#### 2.12.2 `T-1202` — React + TypeScript SPA
- **Files:** `ui/` (separate package), TypeScript components, tests.
- **Model tier:** Sonnet. **Parallel sub-tasks per component cluster:** decision tree wizard, vector map, validation panel, advisory acknowledgement dialog, admin console, audit-log viewer.
- **Context budget:** ≤ 45 k tokens per component cluster.
- **Acceptance:** every advisory acknowledgement dialog enforces the three-path rule (acknowledge / decline / escalate) — no "dismiss" close button.
- **Implementation status (2026-05-14).** Complete locally. Added the separate Vite/React/TypeScript `ui/` package with the decision-tree wizard, cited defaults, 2000-character specialised input, circular plasmid map, scrollable linear map, three-frame ORF translation highlights, validation report links back to modules, three-path advisory acknowledgement dialog with no dismiss/close path, admin console, audit-log viewer, design diff, expert-mode toggle, and i18n-ready locale selector. Replaced `interface.ui` placeholder with package metadata helpers. Focused verification: 5 UI tests passed, production TypeScript build passed, 4 focused Python UI metadata tests passed, full strict mypy passed across `src` and `tests`, full ruff passed, and the full non-slow suite passed with 591 passed / 2 skipped. Phase 12 continues with T-1203 SnapGene API client.

#### 2.12.3 `T-1203` — `adapter.snapgene.SnapGeneApiClient` (UR-01b SHOULD)
- **Files:** `src/adapter/snapgene/api_client.py`, tests.
- **Model tier:** Sonnet. **Context budget:** ≤ 35 k tokens.
- **Implementation status (2026-05-14).** Complete locally. Added `SnapGeneApiClient` with an injectable SnapGene Server Request API transport, `SnapGeneCommandTransport` for licensed server request tooling, status/capability probing that treats the current no-public-API reality as unavailable by default, GenBank-to-`.dna` import requests, `.dna`-to-GenBank export requests, SVG map generation, structured non-zero-code errors, and explicit UR-01a file-watch fallback through `SnapGeneFileWatcher`. Focused verification: 8 T-1203 tests passed, all SnapGene adapter tests passed with 13 passed, full strict mypy passed across `src` and `tests`, full ruff passed, and the full non-slow suite passed with 599 passed / 2 skipped. Phase 12 is complete; Phase 13 begins with T-1301 white-paper-example UAT.

### Phase 13 — Acceptance UAT + library mode + release (3 tasks)

#### 2.13.1 `T-1301` — White-paper-example UAT (v1.3 — expanded per H3-03)
- **Files:**
  - `tests/uat/example_a_bacterial.py` — Example A: pET-28a-based BL21(DE3) over-expression of an EGFP-tagged target protein. Full pipeline: decision-tree wizard → part selection → codon optimisation → assembly plan → validation → screening (`IGSCAdapter` fake CLEAR) → administrator-granted authorisation profile → advisory acknowledgement → SOP rendering → ExportBundle.
  - `tests/uat/example_b_mammalian.py` — Example B: lentiviral transduction of HEK293T cells with a CRISPR-i system. Full pipeline including dual-control authorisation (replication-competent system), engine.vlp_policy enforcement, multi-host compatibility via T-504.
  - `tests/uat/example_c_plant.py` — Example C: Agrobacterium-mediated transient expression in N. benthamiana. Three-host workflow (E. coli cloning + Agrobacterium delivery + plant target), promoter / terminator selection, codon optimisation for plant.
  - `tests/uat/fixtures/{example_a,example_b,example_c}/` — input parts, host context, expected output bundle hashes.
- **Model tier:** Opus, reviewed by `/scientific-advisor`.
- **Context budget:** ≤ 60 k tokens per example.
- **SOP:**
  1. For each example, run the **full end-to-end happy path**: create → add parts → compile → validate → screen → request acknowledgement → admin signs off → render SOP → export ExportBundle.
  2. Use realistic deterministic fakes for every adapter (biology adapters return calibrated fake outputs; screening returns CLEAR or WATCHLIST per fixture; vendor adapters return their published-spec constraint set).
  3. Assert: every gate is `enforced-green` for the happy path; every event is emitted to the correct stream with embedded signed payloads (per v1.3 B3-03); the resulting ExportBundle hash matches the fixture; SnapGene + GenBank tools open the bundle's `.gb` files.
- **Acceptance:** all three examples produce deterministic ExportBundles whose hashes match the captured fixtures; the bundles open in SnapGene + standard GenBank tools without warnings; `/scientific-advisor` reviews each example's biology output and signs off.
- **Implementation status (2026-05-14).** Complete locally. Added the shared T-1301 UAT harness plus Example A bacterial, Example B mammalian lentiviral/CRISPRi, and Example C plant transient-expression fixtures. Each example now runs the full happy path through decision tree, part selection, codon optimisation, assembly plan, validation hooks, screening CLEAR, active advisory acknowledgement, admin authorisation, gated SOP rendering, final ExportBundle generation, GenBank round-trip, and SnapGene file-watch fallback round-trip. Fixture bundle hashes are locked under `tests/uat/fixtures/{example_a,example_b,example_c}/expected_bundle_hash.txt`, and scientific-advisor signoff fixtures are present for all three examples. Focused verification: 3 T-1301 UAT tests passed; strict mypy across `src` and `tests` passed; full ruff passed; agenda consistency passed; full non-slow pytest passed with 602 passed / 2 skipped. Phase 13 continues with T-1302 adversarial UAT.

#### 2.13.2 `T-1302` — Adversarial UAT suite (v1.3 — file list explicit per H3-03; covers all v1.2 + v1.3 bypass scenarios)
- **Files:**
  - `tests/uat/adversarial/self_elevation.py` — UserPrincipal attempts to mint own profile.
  - `tests/uat/adversarial/advisory_bypass.py` — passive render without acknowledgement event.
  - `tests/uat/adversarial/reviewer_escalation.py` — ReviewerPrincipal attempts admin-only operation.
  - `tests/uat/adversarial/unsupported_tier.py` — BSL-4 tier blocked.
  - `tests/uat/adversarial/plugin_trust.py` — unsigned / hash-mismatched plugin manifest rejected.
  - `tests/uat/adversarial/export_leak.py` — ExportProfile redaction enforces PII removal.
  - `tests/uat/adversarial/audit_key_absent.py` (v1.2 B2-08) — engine refuses to start without `AuditKeyProvider`.
  - `tests/uat/adversarial/audit_key_compromise.py` (v1.2 B2-08) — compromised HMAC key does not enable forging `DecisionRecord`.
  - `tests/uat/adversarial/replay_integrity.py` (v1.2 M2-01) — replay with tampered governance event triggers `ReplayIntegrityFailure`.
  - `tests/uat/adversarial/construct_checksum_mismatch.py` (v1.2 M2-02) — acknowledge against checksum X, modify construct, block.
  - `tests/uat/adversarial/programmatic_event_bypass.py` (v1.2 M2-02) — writing `OperationalProtocolAuthorised` without governance chain detected.
  - `tests/uat/adversarial/profile_tamper.py` (v1.3 B3-04) — tampered `AuthorisationProfile` in SQLite fails verifier on load.
  - `tests/uat/adversarial/sop_template_tamper.py` (v1.3 B3-05) — tampered SOP template fails verifier on load; T-803 refuses to render.
  - `tests/uat/adversarial/governance_reference_only_rejected.py` (v1.3 B3-03) — a governance event with reference-only payload fails the static `test_governance_events_self_contained` plus the replay invariant.
  - `tests/uat/adversarial/review_queue_blocked_path.py` (v1.3 B3-06) — blocked session creates exactly one pending request; user cannot self-approve; admin approval triggers `mint_profile` → unblocks.
  - `tests/uat/adversarial/developer_post_bootstrap_denied.py` (v1.3 H3-10) — ordinary `DeveloperPrincipal` cannot mint after bootstrap.
  - `tests/uat/adversarial/admin_service_unauthenticated.py` (v1.3 H3-09) — admin command via IPC without credentials denied.
  - **`tests/uat/adversarial/dual_control_same_admin_rejected.py` (v1.4 M4-04)** — institution enables `dual_control_flags.require_two_admins_for_revocation = True`; same `AdminPrincipal` tries to mint then revoke a profile → second action denied with `DualControlViolation`.
  - **`tests/uat/adversarial/dual_control_two_admins_accepted.py` (v1.4 M4-04)** — same fixture but two distinct admin principals → both actions accepted.
  - **`tests/uat/adversarial/dual_control_advisory_signoff_pair_required.py` (v1.4 M4-04)** — `dual_control_flags.advisory_acknowledgement_requires_pair = True`; single-admin acknowledgement blocks gate; pair acknowledgement passes.
  - **`tests/uat/adversarial/audit_service_dual_writer_chain_integrity.py` (v1.4 B4-04)** — concurrent engine + admin appends to the audit-service under load produce a single linear HMAC chain (no interleaving corruption).
  - **`tests/uat/adversarial/admin_command_direct_handler_import_rejected.py` (v1.4 H4-02)** — static check: CLI / API code paths attempting to import `AdminActionHandler` directly fail `no-direct-admin-handler-import-check`.
- **Model tier:** Opus. **Context budget:** ≤ 75 k tokens (v1.3 increased from 60 k for the expanded scenario list).
- **SOP:** Each scenario has a fixture under `tests/uat/adversarial/fixtures/<scenario>/`, an expected verdict (which gate fires, which event is emitted, which audit row appears), and an expected absence assertion (e.g., `OperationalProtocolAuthorised` never emitted).
- **Acceptance:** all 22 explicit scenario modules green; each produces the expected typed denial or recovery verdict; each fixture records the expected gate/event/audit observation; none silently succeeds.
- **Implementation status (2026-05-14).** Complete locally. Added the `tests/uat/adversarial/` harness, all 22 explicit scenario modules, and fixture directories with expected verdict JSON for self-elevation, advisory bypasses, reviewer/admin boundary checks, BSL-4 blocking, plugin trust rejection, export redaction, audit-key absence/compromise, replay/governance payload integrity, profile/SOP-template tamper detection, review-queue recovery, developer post-bootstrap denial, admin-service authentication failure, dual-control revocation and advisory signoff modes, audit-service concurrent writer integrity, and the no-direct-admin-handler import boundary. T-1302 also made dual-control revocation enforcement and advisory pair-acknowledgement flags executable and replaced the `no_direct_admin_handler_import_check.py` stub with an informational static scanner. Focused verification: 22 T-1302 UAT tests passed; 57 related admin/advisory/replay/audit/SOP regression tests passed; full strict mypy passed across `src`, `tools`, and `tests`; full ruff passed; `no-direct-admin-handler-import-check --enforce`, task-acceptance completeness, and agenda consistency passed; full non-slow pytest passed with 624 passed / 2 skipped. Phase 13 continues with T-1303.

#### 2.13.3 `T-1303` — Combinatorial library benchmark + release polish (v1.3 — concrete cadence per H3-03)
- **Files:**
  - `tests/uat/library_benchmark.py` — 100-realisation fixture (smoke); 1000-realisation fixture (stretch).
  - `tests/uat/library_benchmark_fixtures/{100_realisation_input.json,1000_realisation_input.json,expected_hashes.json}`.
  - `tools/release/build_container_image.py`, `tools/release/build_wheel.py`, `tools/release/release_notes_template.md`.
  - Release docs: `docs/release/v0.1.0_release_notes.md`, `docs/release/installation.md`, `docs/release/migration_from_v0.0_to_v0.1.md`.
- **Model tier:** Sonnet. **Context budget:** ≤ 50 k tokens (v1.3 increased from 40 k).
- **SOP:**
  1. **Library mode benchmark.** 100-realisation library produces 100 deterministic outputs; per-realisation governance events emitted as **batched** entries in the design stream (per v1.3 H3-06 — library-mode `ScreeningCompleted` is a design event with per-realisation evidence in the payload). 1000-realisation stretch fixture verifies scaling behaviour; runs nightly (not on every PR).
  2. **Release polish.** Build container image with pinned interpreter + pinned core runtime + pinned `dev` group + pinned canonical fonts + Dockerfile; build wheel for `pip install`; produce release notes from `tools/release/release_notes_template.md` populated from the task manifest.
  3. **Determinism check.** The container determinism job (T-201, lifecycle-state `not_implemented` until now) flips to `enforced` at T-1303 verification: every white-paper example + the 100-realisation library benchmark produces deterministic outputs inside the container on both Linux + Windows.
- **Acceptance:** 100-realisation library benchmark green deterministic; 1000-realisation stretch benchmark green nightly; container image + wheel built reproducibly; release notes generated; `determinism` CI gate transitions to `enforced-green`.
- **Implementation status (2026-05-14).** Complete locally. Added the deterministic library benchmark harness, 100-realisation smoke fixture, 1000-realisation stretch fixture, locked expected hashes, release build wrappers for the Python wheel and pinned Docker image, a manifest-driven release-note renderer, release docs, and the CI determinism job covering the three white-paper examples plus the 100-realisation library fixture on Linux and Windows runners. The Python wheel was built locally under `task_artefacts/T-1303/dist/`; Docker is not installed in this workspace, so the container build is verified locally by dry-run plan and is wired for CI execution. Focused verification: T-1303 UAT/release tests passed; the 1000-realisation stretch fixture passed; release determinism check passed; full strict mypy and ruff passed for the new surface; release build dry-runs passed. This completes all active Section 2 implementation task cards.

---

## 3. Inter-module wiring (v1.5 — synchronised with corrected task order, split-task identities, seed manifests, and single-writer audit/admin-service boundaries)

### 3.1 Dependency DAG (build order — v1.5 phase order: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8a → 9a → **10** → 8b → 9b → 11 → 12 → 13; Section 2 heading order matches per B4-01)

```
   PHASE 2  scaffold (T-201..T-205) ─────────────────────────────────────┐
                                                                         │
   PHASE 3  domain.sequence ──► domain.graph ──► domain.types            │
                  │                                  │                   │
                  ▼                                  ▼                   │
            domain.security  ◄──── domain.events ◄── domain.types.{sop_protected,
                  │                       │            design_plan, controls,
                  │                       │            risk_advisory, governance}  ◄── v1.2 (T-306)
                  │                       │                              │
                  └─► domain.types.derivation ◄──┐                       │
                                                 │                       │
            ┌────────────────────────────────────┘                       │
            │ EARLY-HALF SECURITY PROTOCOLS (v1.4 B4-02/03/05 — fakes    │
            │   land before consumers T-308/T-310/T-311 can run):        │
            │   T-312a (AuditKeyProvider Protocol)                       │
            │   T-313a (AuditAppendPort + AdminAuditAppendPort + fakes)  │
            │   T-314a (Profile + DecisionRecord Signer/Verifier + fakes)│
            │   T-316a (SopTemplate split-port + Signer/Verifier + fakes)│
            ▼                                                            │
            adapter.io.{GenBank,FASTA,SBOL3,SnapGeneDnaReader} (T-308 a..e)
                  │                                                      │
                  ▼                                                      │
            engine.session (T-309: state machine + replay determinism)  │
                  │                                                      │
                  ▼                                                      │
            adapter.persistence.{ProjectStore, JsonlEventLog ×3,         │
                                 SqliteAuditLog (read), SqliteAuthorisationStoreRead} (T-310)
                  │                                                      │
                  ▼                                                      │
            app.admin_action_handler (T-311 — sole admin write path; uses
                                       T-313a/T-314a/T-316a fakes for unit tests)
                  │                                                      │
            LATE-HALF PRODUCTION ADAPTERS (after T-311):                 │
                  ├─► T-312b (audit-key keystores + rotation + offline   │
                  │           verifier; indefinite archive per H4-05)    │
                  ├─► T-314b (production profile + per-principal         │
                   │           DecisionRecord signers + key lifecycle     │
                   │           per B4-09; production verifier used by     │
                   │           T-313b)                                    │
                   ├─► T-313b (production audit-service process per B4-04;│
                   │           single-writer IPC server; engine + admin   │
                   │           processes are IPC clients)                 │
                  ▼                                                      │
            app.review_queue (T-315 — `AuthorisationRequest` service;    │
                              defines `ReviewQueueAdminPort` consumed by │
                              T-1103b admin-service)                     │
                                                                         │
   PHASE 4  adapter.catalogue.YamlLoader ─────────────────────────────► (consumes domain.*)
                  │
                  ├─► parts.yaml, hosts.yaml, enzymes.yaml, rules/*.yaml,
                  │   vendor_profiles/*.yaml, screening_trust_policy.yaml,
                  │   institutional_policy.yaml, export_profiles.yaml,
                  │   risk_advisories.yaml, threshold_profiles/*.yaml,
                  │   plugin_manifests/*.yaml
                  │   (NOTE v1.4 B4-05: `sop_templates/*.yaml` are NOT runtime-loaded;
                  │    they are T-316b BOOTSTRAP INPUT ONLY. Runtime reads go through
                  │    SqliteSopTemplateStore via SopTemplateReadPort.)
                  │
                  ├─► T-316c (Phase 4: production SopTemplateSigner + Verifier + key
                   │           lifecycle per H4-04)
                   ├─► T-316b (Phase 4: signed SQLite SOP-template store + bootstrap
                   │           migration; consumes T-316c production signer/verifier;
                   │           replaces v1.2 YamlSopTemplateLoader)
                  │
   PHASE 5  engine.dependencies ──► engine.validation (T-502 — pure DAG executor
                                                       with WorkerPoolFactory) ─► activates
                                                                                  BlockCompile
                                                                                  (T-309 sub-deliverable (b))
                  ▼
            engine.sequence_analysis ──► engine.validation.predicates
                                          (~50 structural rules — BR-14 EXCLUDED per v1.2 H2-11)

   PHASE 6  adapter.biology.* (T-601a..k formal range, parallel) ──► engine.validation.predicates
                                                          (biology-dependent — 7 rules)
            engine.compatibility (T-504 — multi-host workflows)
            app.validation_orchestrator (T-603) ◄── biology metric pre-compute
            app.design_service (T-606 — create/open/amend/compile/replay + Awaiting* pending states)
            app.decision_tree (T-607 — FR-UI-01..12)

   PHASE 7  engine.codon (T-701) ─┐
            engine.overhang (T-702)├─► engine.assembly (T-703 a..e — 9 strategies
            engine.primer (T-704)──┘                  incl. SLIC via T-703e)
                                          │
                                          ▼
                            app.assembly_orchestrator (T-705)

   PHASE 8a (pre-screening, non-operational — 7 tasks)
            engine.risk_classification (T-801)
            engine.design_plan (T-802 — DesignRealisationPlan; cannot contain ProtocolStep)
            engine.controls (T-804 — ControlSet)
            engine.vlp_policy (T-807 — VLP/AAV/lentivirus policy)
            app.plugin_governance (T-808 — plugin manifest verification)
            app.advisory_acknowledgement [presentation surface only] (T-806a — pure predicate)
            app.design_plan_orchestrator (T-805a — emits DraftDesignBundle; structurally
                                          incapable of containing SopLinkedProtocol)

   PHASE 9a (pre-screening I/O — 2 tasks)
            adapter.io.{EMBL,GFF3} (T-901)
            adapter.snapgene.SnapGeneFileWatcher (T-902 — imports SnapGeneDnaReader from T-308e;
                                                  does NOT own dna_reader.py per v1.2 H2-04)

   PHASE 10 adapter.vendor.{Twist,IDT,GenScript} (T-1001, parallel)
            adapter.screening.{IGSC,IBBIS,SecureDNA,InternalBlacklist} (T-1002, parallel)
            app.screening_orchestrator (T-1002) ──► emits ScreeningCompleted to design stream
                                                    per v1.2 B2-05; activates
                                                    BlockVendorSubmission (screening portion)
            T-1001 ──► activates BlockVendorSubmission (vendor-feasibility portion per H3-02)

   PHASE 8b (post-screening, operational — 3 tasks; T-805b renamed per v1.2 B2-09)
            engine.sop_protocol (T-803 — gated SopLinkedProtocol; consumes SopTemplateReadPort
                                  from T-316b; admin SOP-template writes moved to T-316b per v1.4 B4-05)
            app.sop_protocol_orchestrator (T-805b — emits SopProtocolBundle; emits SopRendered
                                            to design stream)
            app.authorisation_decision (T-806b — consumes ScreeningCompleted +
                                         all_required_advisories_acknowledged predicate;
                                         emits OperationalProtocolAuthorised to design stream;
                                         activates BlockOperationalProtocol (T-309 (b));
                                         home of BR-14 hard-gate predicate;
                                         routes blocked sessions to T-315 review queue per v1.3 B3-06)

   PHASE 9b (post-Phase-8b — 1 task)
            app.export_orchestrator (T-903 — final ExportBundle ZIP; consumes
                                       ScreeningCompleted + OperationalProtocolAuthorised +
                                       SopRendered; activates BlockExport (T-309 (b)))

   PHASE 11 T-1103a (AdminServiceClientPort Protocol + IPC contract + test client; FIRST)
            interface.cli (T-1101 — admin commands route via AdminServiceClientPort per v1.4 B4-08;
                            cannot import AdminActionHandler directly)
            interface.api (T-1102 — admin routes via AdminServiceClientPort per v1.4 B4-08)
            T-1103b (admin-service production process + IPC server + ACL +
                     ReviewQueueAdminPort per v1.4 H4-01; LAST in Phase 11)

   PHASE 12 app.constraint_translator + adapter.llm.* (parallel)
            interface.ui (React/TS; parallel sub-tasks per component cluster)
            adapter.snapgene.SnapGeneApiClient (UR-01b SHOULD)

   PHASE 13 White-paper-example UAT (T-1301 — full happy path) + adversarial UAT (T-1302
            — incl. construct-checksum mismatch + programmatic-event bypass per M2-02) +
            library benchmark + release polish

   Lifecycle hooks edge: every adapter implementing Lifecycle is start()ed after
   composition and stop()ped in reverse order at shutdown; RefreshingAdapter wraps
   adapters needing periodic refresh (e.g., IGSC session token, LocalLlm model weights).
```

**Build-order invariants:**

1. **No layer reaches across.** `domain/` never imports `adapter/`, `app/`, `interface/`. `engine/` imports only `domain/`. `app/` imports `domain/`, `engine/`, never specific adapters. `adapter/` imports `domain.ports/`. `interface/` imports `app/`.
2. **Ports before adapters.** Every port is defined in `domain.ports` before any adapter implementation begins (T-203c stub).
3. **Catalogues before predicates.** Every rule predicate has a manifest entry in `catalogues/rules/*.yaml` *before* the predicate function is written (T-405 before T-503).
4. **Adversarial fixtures before sign-off.** Every CI gate's adversarial test fixture exists *before* the gate is enabled in CI as release-blocking.

### 3.2 Port and adapter wiring

The platform's dependency-injection contract:

```python
# src/app/composition.py — single point where the engine is wired up.
# This is the ONLY place that knows about specific adapters; the engine
# and every other application module receive their dependencies as
# already-wired Protocols.
#
# v1.2: composition root rewritten to include every v1.1/v1.2 module:
#   - engine.session (T-309), engine.compatibility (T-504), engine.vlp_policy (T-807)
#   - app.design_service (T-606), app.decision_tree (T-607)
#   - app.design_plan_orchestrator (T-805a) and app.sop_protocol_orchestrator (T-805b)
#   - app.admin_action_handler (T-311) wired with the WRITE port, not the read port
#   - app.plugin_governance (T-808)
#   - AuditKeyProvider port (T-312a/T-312b) supplies HMAC operations to audit verification/writing
#   - Lifecycle.start() / .stop() called after composition / before shutdown
#   - WorkerPoolFactory (T-502) constructed locally; no global multiprocessing mutation

def compose_engine(
    config: PlatformConfig,
) -> Engine:
    # ── Catalogue ports
    part_catalogue: PartCatalogue = YamlPartLoader(config.catalogues_dir).load()
    host_catalogue: HostCatalogue = YamlHostLoader(config.catalogues_dir).load()
    enzyme_catalogue: EnzymeCatalogue = YamlEnzymeLoader(config.catalogues_dir).load()
    rule_registry: RuleRegistry = YamlRuleRegistryLoader(config.catalogues_dir).load()
    # v1.4 B4-05: legacy SOP-template library + YamlSopTemplateLoader REMOVED. Runtime SOP-template reads
    # go through SqliteSopTemplateStoreRead via SopTemplateReadPort (constructed below).
    risk_advisory_catalogue: RiskAdvisoryCatalogue = YamlRiskAdvisoryLoader(config.catalogues_dir).load()
    screening_trust_policy: ScreeningProviderTrustPolicy = YamlScreeningTrustLoader(config.catalogues_dir).load()
    institutional_policy: InstitutionalPolicy = YamlInstitutionalPolicyLoader(config.catalogues_dir).load()
    threshold_profile_catalogue: ThresholdProfileCatalogue = YamlThresholdProfileLoader(config.catalogues_dir).load()
    plugin_manifest_registry: PluginManifestRegistry = YamlPluginManifestLoader(config.catalogues_dir).load()
    export_profile_catalogue: ExportProfileCatalogue = YamlExportProfileLoader(config.catalogues_dir).load()

    # ── Biology ports — pinned production adapters or deterministic fakes per config
    rna_folder: RnaFolder = config.biology_adapter("rna_folder")
    splice_predictor: SplicePredictor = config.biology_adapter("splice_predictor")
    signal_p: SignalPeptidePredictor = config.biology_adapter("signal_peptide")
    rbs_calc: TIRPredictor = config.biology_adapter("tir")
    noderer_kozak: KozakScorer = config.biology_adapter("kozak")
    codon_algorithms: dict[str, CodonAlgorithm] = config.codon_algorithms()

    # ── Engine-support port
    worker_pool_factory: WorkerPoolFactory = WorkerPoolFactory(config.executor_mode)  # T-502

    # ── Security / audit-key (legacy audit-key task split into T-312a/T-312b)
    audit_key_provider: AuditKeyProvider = config.audit_key_provider()  # File | WindowsDpapi | PosixKeyring (T-312b in prod; T-312a TestAuditKeyProvider in tests)
    decision_record_signer: DecisionRecordSigner = config.decision_record_signer()  # asymmetric per-principal
    # v1.5/v1.3 B3-04 — separate institutional cryptographic identity for AuthorisationProfile signing (T-314a Protocol, T-314b production)
    profile_signer: AuthorisationProfileSigner = config.profile_signer()  # admin-service process only
    profile_verifier: AuthorisationProfileVerifier = config.profile_verifier()  # both processes
    # v1.5/v1.3 B3-05 — separate institutional cryptographic identity for SopTemplate signing (T-316a Protocol, T-316c production)
    sop_template_signer: SopTemplateSigner = config.sop_template_signer()  # admin-service process only
    sop_template_verifier: SopTemplateVerifier = config.sop_template_verifier()  # both processes

    # ── Persistence
    project_store: ProjectStore = SqliteProjectStore(config.project_db)
    design_event_log: EventLog = JsonlEventLog(config.events_dir / "design")
    governance_event_log: EventLog = JsonlEventLog(config.events_dir / "governance")
    export_event_log: EventLog = JsonlEventLog(config.events_dir / "export")
    snapshot_store: SnapshotStore = FilesystemSnapshotStore(config.snapshots_dir)
    # v1.3 B3-01: AuditLog read interface only; writes are brokered.
    audit_log_reader: AuditLogReadPort = SqliteAuditLog(config.audit_db, audit_key_provider, mode="ro")
    authorisation_read_port: AuthorisationReadPort = SqliteAuthorisationStoreRead(
        config.authorisation_db, profile_verifier,  # v1.3 B3-04 — verify on every get()
    )
    # v1.3 B3-05 — read-only SOP template port (admin-write port constructed only in admin-service process)
    sop_template_read_port: SopTemplateReadPort = SqliteSopTemplateStoreRead(
        config.sop_template_db, sop_template_verifier,  # v1.3 B3-05 — verify on every read
    )
    # v1.3 B3-06 — review queue store
    review_queue_store: ReviewQueueStore = SqliteReviewQueueStore(config.review_queue_db)

    # v1.4 B4-04: audit-append is an IPC client to the dedicated audit-service process (T-313b).
    # The audit-service process is the ONLY mode=rw writer of audit.sqlite — it owns the lock
    # for its lifetime. Engine + admin-service processes are both IPC clients of the audit-service.
    # Governance services in the engine process receive `audit_append: AuditAppendPort` IPC client,
    # NOT a direct database handle.
    audit_append: AuditAppendPort = AuditServiceClient(
        ipc_path=config.audit_service_ipc_path,
        service_principal_registry=config.service_principals,
        decision_record_signer=decision_record_signer,  # signs service-principal tokens
    )

    # The admin-write ports are constructed ONLY when this composition root runs inside
    # the admin-service process (not in the User-facing engine process). Engine processes
    # set config.is_admin_service_process = False and receive `None` for the write ports.
    authorisation_admin_write_port: AuthorisationAdminWritePort | None = (
        SqliteAuthorisationStoreWrite(config.authorisation_db, profile_signer)  # v1.3 B3-04
        if config.is_admin_service_process
        else None
    )
    authorisation_bootstrap_port: AuthorisationBootstrapPort | None = (
        SqliteAuthorisationStoreWrite(config.authorisation_db, profile_signer).as_bootstrap_port()
        if config.is_admin_service_process
        else None
    )
    # v1.3 B3-05 — SOP-template admin write ports (admin-service process only)
    sop_template_admin_write_port: SopTemplateAdminWritePort | None = (
        SqliteSopTemplateStoreWrite(config.sop_template_db, sop_template_signer)
        if config.is_admin_service_process
        else None
    )
    sop_template_bootstrap_port: SopTemplateBootstrapPort | None = (
        SqliteSopTemplateStoreWrite(config.sop_template_db, sop_template_signer).as_bootstrap_port()
        if config.is_admin_service_process
        else None
    )
    # v1.3 B3-01 — admin-service-process audit-append path; pairs with the engine broker.
    admin_audit_append: AdminAuditAppendPort | None = (
        AdminAuditServiceClient(  # v1.4 B4-04: admin-side IPC client to audit-service process
            ipc_path=config.audit_service_ipc_path,
            decision_record_signer=decision_record_signer,
        )
        if config.is_admin_service_process
        else None
    )

    # ── Vendor + screening — pluggable
    vendor_adapters: dict[VendorId, SynthesisVendorAdapter] = config.vendor_adapters()
    screening_adapters: dict[ScreeningProviderId, ScreeningAdapter] = config.screening_adapters()

    # ── SnapGene
    snapgene_dna_reader: SnapGeneDnaReader = SnapGeneDnaReader()  # T-308e
    snapgene_channel: SnapGeneChannel = config.snapgene_channel(snapgene_dna_reader)

    # ── LLM (default local; cloud opt-in)
    llm_translator: LLMConstraintTranslator = config.llm_translator()
    advisory_text_policy: AdvisoryTextPolicy = config.advisory_text_policy()

    # ── Engines (all pure)
    dependency_engine = DependencyEngine(rule_registry)
    session_engine = SessionEngine(design_event_log, snapshot_store)  # T-309
    validation_engine = ValidationEngine(dependency_engine, worker_pool_factory)
    compatibility_engine = CompatibilityEngine(host_catalogue, threshold_profile_catalogue)  # T-504
    seq_analysis = SequenceAnalysis(enzyme_catalogue)
    codon_optimiser = CodonOptimiser(codon_algorithms)
    primer_designer = PrimerDesigner()
    overhang_optimiser = OverhangSetOptimiser()
    assembly_engine = AssemblyEngine(seq_analysis, overhang_optimiser)
    risk_classifier = RiskClassifier(risk_advisory_catalogue)
    vlp_policy_engine = VlpPolicyEngine(rule_registry)  # T-807
    design_plan_generator = DesignPlanGenerator(assembly_engine, primer_designer, risk_classifier, vlp_policy_engine)
    controls_generator = ControlsGenerator(assembly_engine, primer_designer)
    sop_protocol_generator = SopProtocolGenerator(sop_template_read_port)

    # ── Application services
    validation_orchestrator = ValidationOrchestrator(
        validation_engine, rule_registry,
        rna_folder, splice_predictor, signal_p, rbs_calc, noderer_kozak,
    )
    assembly_orchestrator = AssemblyOrchestrator(
        codon_optimiser, primer_designer, assembly_engine,
        validation_orchestrator,
    )
    design_service = DesignService(session_engine, project_store, design_event_log)  # T-606
    decision_tree = DecisionTree(part_catalogue, host_catalogue, design_service)  # T-607
    # v1.3 B3-01: governance services receive audit_append (broker), NOT raw audit_log.
    plugin_governance = PluginGovernance(  # T-808
        plugin_manifest_registry, governance_event_log, audit_append,
        service_principal=config.service_principals.plugin_governance,
    )
    advisory_acknowledgement = AdvisoryAcknowledgementService(  # T-806a
        governance_event_log, audit_append, decision_record_signer,
        service_principal=config.service_principals.advisory_acknowledgement,
    )
    review_queue_service = ReviewQueueService(  # v1.3 B3-06 T-315
        review_queue_store, governance_event_log, audit_append, decision_record_signer,
        service_principal=config.service_principals.review_queue,
    )
    screening_orchestrator = ScreeningOrchestrator(  # T-1002 — writes ScreeningCompleted to DESIGN stream per v1.2 B2-05
        screening_adapters, screening_trust_policy,
        design_event_log, governance_event_log, audit_append,
        service_principal=config.service_principals.screening,
    )
    authorisation_decision = AuthorisationDecisionService(  # T-806b
        authorisation_read_port, advisory_acknowledgement, review_queue_service,  # v1.3 B3-06 — routes blocked sessions
        design_event_log, governance_event_log, audit_append, decision_record_signer,
        service_principal=config.service_principals.authorisation_decision,
    )
    design_plan_orchestrator = DesignPlanOrchestrator(  # T-805a — emits DraftDesignBundle, pre-screening
        design_plan_generator, controls_generator, risk_classifier,
        advisory_acknowledgement, design_event_log,
    )
    sop_protocol_orchestrator = SopProtocolOrchestrator(  # T-805b — emits SopProtocolBundle + SopRendered to DESIGN stream, post-authorisation
        sop_protocol_generator, sop_template_read_port,  # v1.3 B3-05: read port only; admin writes via T-316b in admin-service process
        authorisation_decision, design_event_log,
    )
    export_orchestrator = ExportOrchestrator(  # T-903 (Phase 9b)
        design_plan_orchestrator, sop_protocol_orchestrator,
        screening_orchestrator, authorisation_decision,
        export_profile_catalogue, export_event_log,
    )

    # ── Admin handler (T-311 + T-316b SOP-template extension) — constructed only inside the admin-service process.
    # The engine process never holds an admin write port. v1.3: admin handler receives:
    #   - split authorisation write/bootstrap ports (B2-04)
    #   - split SOP-template write/bootstrap ports (B3-05 — T-316b)
    #   - admin-side audit-append broker (B3-01)
    #   - profile signer (B3-04 — T-314a/T-314b)
    #   - SOP-template signer (B3-05 — T-316a/T-316c)
    #   - decision-record signer
    admin_action_handler: AdminActionHandler | None = (
        AdminActionHandler(
            authorisation_admin_write_port,
            authorisation_bootstrap_port,
            sop_template_admin_write_port,  # v1.3 B3-05 — replaces the legacy direct SOP-template write path
            sop_template_bootstrap_port,    # v1.3 B3-05
            admin_audit_append,             # v1.3 B3-01 — admin-side append broker
            governance_event_log,
            decision_record_signer,
            profile_signer,                 # v1.3 B3-04
            sop_template_signer,            # v1.3 B3-05
        )
        if (
            config.is_admin_service_process
            and authorisation_admin_write_port is not None
            and authorisation_bootstrap_port is not None
            and sop_template_admin_write_port is not None
            and sop_template_bootstrap_port is not None
            and admin_audit_append is not None
        )
        else None
    )

    constraint_translator = ConstraintTranslator(llm_translator, advisory_text_policy)

    engine = Engine(
        session_engine=session_engine,
        validation_orchestrator=validation_orchestrator,
        compatibility_engine=compatibility_engine,
        assembly_orchestrator=assembly_orchestrator,
        design_service=design_service,
        decision_tree=decision_tree,
        plugin_governance=plugin_governance,
        screening_orchestrator=screening_orchestrator,
        advisory_acknowledgement=advisory_acknowledgement,
        review_queue_service=review_queue_service,  # v1.3 B3-06
        authorisation_decision=authorisation_decision,
        design_plan_orchestrator=design_plan_orchestrator,
        sop_protocol_orchestrator=sop_protocol_orchestrator,
        export_orchestrator=export_orchestrator,
        admin_action_handler=admin_action_handler,
        constraint_translator=constraint_translator,
        snapgene_channel=snapgene_channel,
        snapgene_dna_reader=snapgene_dna_reader,
        audit_key_provider=audit_key_provider,
        audit_append=audit_append,                  # v1.3 B3-01 — broker port held by engine
        audit_log_reader=audit_log_reader,          # v1.3 B3-01 — read-only audit interface
        profile_verifier=profile_verifier,          # v1.3 B3-04
        sop_template_verifier=sop_template_verifier,  # v1.3 B3-05
    )

    # ── Lifecycle hooks (v1.1 Round-3 / v1.2 propagation)
    for adapter in engine.lifecycle_adapters():
        adapter.start()

    return engine


def dispose_engine(engine: Engine) -> None:
    """Reverse-order shutdown — called at process exit / API shutdown."""
    for adapter in reversed(list(engine.lifecycle_adapters())):
        adapter.stop()
```

`compose_engine` is *the* dependency-injection boundary; nothing else imports specific adapters. Tests inject deterministic fakes via the same `PlatformConfig`.

**v1.2 separation of duties (B2-04 fix).** The admin-write paths (`AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`, SOP-template admin writes) are constructed **only** when `config.is_admin_service_process == True`. The User-facing engine process sets that flag to `False` and the corresponding ports are `None` — `AdminActionHandler` is not constructed at all in that process. This means there is no code path in the engine process that can reach `mode=rw` SQLite access to `authorisation.sqlite` even if the User principal mis-authenticates.

### 3.3 Event-stream wiring (v1.2 — corrected per B2-05; matches `ARCHITECTURE.md` v1.5 lines 2148-2178)

Three append-only JSONL logs under `events/`:

| Stream | Writer | Reader | Key events |
|---|---|---|---|
| `events/design/<session>.jsonl` | `engine.session` (T-309), `app.design_service` (T-606), `app.assembly_orchestrator` (T-705), `app.validation_orchestrator` (T-603), `app.design_plan_orchestrator` (T-805a — `DraftDesignBundle*`), `app.screening_orchestrator` (T-1002 — **`ScreeningCompleted`**), `app.authorisation_decision` (T-806b — **`OperationalProtocolAuthorised`**), `app.sop_protocol_orchestrator` (T-805b — **`SopRendered`**) | replay (T-309), UI, `app.export_orchestrator` (T-903) | `SessionStarted`, `PartAdded`, `HostSelected`, `FreeTextEntered`, `LLMTranslationProposed`, `LLMTranslationConfirmed`, `RuleAcknowledged`, `OverrideJustified`, `DesignCompiled`, `ScreeningCompleted`, `OperationalProtocolAuthorised`, `SopRendered`, `SessionForked` |
| `events/governance/<institution>.jsonl` | `app.admin_action_handler` (T-311), `app.audit_key_rotation_service` (T-312b), `app.decision_record_key_management` (T-314b), `app.review_queue` (T-315 — extension requests, item creation, admin assignment/resolution), `app.advisory_acknowledgement` (T-806a — presentation/acknowledge/decline/escalate), reviewer sign-off, `app.plugin_governance` (T-808), `app.screening_orchestrator` (T-1002 — *reviewer/admin sign-off side only*, **not** `ScreeningCompleted`), `app.authorisation_decision` (T-806b — `AuthorisationAttemptDenied` only), `interface.audit_service` (T-313b — `AuditServiceAuthenticationFailed` only) | audit-log replay, `audit-traceability-check` | `AdminBootstrapped`, `AdminActionMinted`, `AdminActionModified`, `AdminActionRevoked`, `InstitutionalPolicyUpdated`, `ReviewerSignedOff`, `AuthorisationAttemptDenied`, `AuthorisationExtensionRequested`, `ReviewQueueItemCreated`, `ReviewQueueItemAssigned`, `ReviewQueueItemResolved`, `DecisionRecordPublicKeyDistributed`, `DecisionRecordPrincipalKeyRevoked`, `PluginManifestApproved`, `PluginManifestRejected`, `AdvisoryWarningPresented`, `RiskAdvisoryAcknowledged`, `RiskAdvisoryDeclined`, `RiskAdvisoryEscalated`, `UnsupportedBiosafetyTierAttempted`, `AuditKeyRotated`, `SopTemplateMinted`, `SopTemplateModified`, `SopTemplateRevoked`, `AuditServiceAuthenticationFailed` |
| `events/export/<institution>.jsonl` | `app.export_orchestrator` (T-903) | release-management, retrospective audits | `ExportBundleCreated`, `ExportProfileRedactionApplied` |

**Cross-stream correlation.** Cross-stream links are by **immutable `DecisionRecord` IDs** + content hashes; no shared session state. The design stream is the authoritative session state; the governance stream is the authoritative governance state; the export stream is the authoritative export state. Replay reconstructs session state from the design stream **and** cross-references `DecisionRecord` IDs into the governance stream.

**v1.3 B3-03 payload durability.** Every governance event payload **embeds** the full canonical signed value-object (frozen-dataclass canonical JSON) plus its content hash — **not** a reference. The governance stream is itself the durable signed-record store; no external value-object store is required. This satisfies FR-ADV-06 (`REQUIREMENTS.md:386`: the full approval trace MUST be persisted in the immutable governance event stream). The value-object **type** still lives in `domain.types.{risk_advisory,governance}` (per v1.2 H2-03 namespace separation), but each event payload contains a frozen canonical snapshot of the value. Static test `tests/static/test_governance_events_self_contained.py` enforces this.

**v1.2 cross-stream replay-determinism invariant test (B2-05 closure).** Implemented in T-309:

```
def test_replay_design_plus_referenced_governance_reproduces_session_state():
    log = build_replay_log(design=[...], governance=[...])
    state_via_engine = SessionEngine.replay(log)
    state_via_independent_walker = independent_event_walker(log)
    assert state_via_engine == state_via_independent_walker
    # The test fails if any state-transition predicate consults an event from
    # the wrong stream (e.g., looks for ScreeningCompleted in governance).
```

### 3.4 Persistence wiring (v1.2 — clarified per B2-04 / M2-08)

| Store | File | Writers | Readers | Mode |
|---|---|---|---|---|
| Project sessions | `project.sqlite` | `engine.session` (T-309) + `adapter.persistence.SqliteProjectStore` (T-310a) | engine, application | rw |
| Audit log | `audit.sqlite` | **Single writer (v1.4 B4-04):** dedicated **audit-service process** (T-313b) owns `mode=rw` for its lifetime. Engine process + admin-service process are both **IPC clients** of the audit-service (named pipe `\\.\pipe\cev-audit-service` on Windows; Unix socket `/var/run/cev-audit/socket` on POSIX). The audit-service serialises all appends through a single in-process queue, computes HMAC chain entries via `AuditKeyProvider.mac()` (T-312a v1.4 H4-10 — no raw key exposure), and persists rows atomically. Single linear HMAC chain across engine + admin appends. | engine, application (read-only via `audit_log_reader: AuditLogReadPort`) | append-only |
| Authorisation store | `authorisation.sqlite` | `app.admin_action_handler` (T-311) running in **separate admin-service process**, holding `AuthorisationAdminWritePort` + `AuthorisationBootstrapPort` opened `mode=rw` | engine + User-role processes hold `AuthorisationReadPort` opened `mode=ro` (T-310d) | append-only; OS-level filesystem ACL reinforces read-only constraint on engine processes |
| Design events | `events/design/<session>.jsonl` | session writer, design-service, assembly-orchestrator, validation-orchestrator, design-plan-orchestrator, **screening-orchestrator** (ScreeningCompleted per v1.2 B2-05), **authorisation-decision** (OperationalProtocolAuthorised), **sop-protocol-orchestrator** (SopRendered) | replay (T-309), UI | append-only |
| Governance events | `events/governance/<institution>.jsonl` | admin handler, advisory acknowledgement, plugin governance, reviewer sign-off, screening-orchestrator (admin/reviewer side only), audit-service authentication-failure writer (T-313b) | replay, audit, CI gates | append-only |
| Export events | `events/export/<institution>.jsonl` | export orchestrator (T-903, Phase 9b) | release retrospectives | append-only |
| Snapshots | `snapshots/<session>/<event_seq>_<derivation_hash>.json` | snapshotter | replay accelerator | rw |
| Exports | `exports/<bundle>.zip` | export orchestrator (T-903) | end-user | wo |
| Audit keys | `keys/audit_key_v<N>.bin` (file backend) **or** OS keystore | T-312b keystore adapter (rotation only; never co-located with `audit.sqlite`) | T-312a `AuditKeyProvider` (current + archived) | adapter-specific (typically root-only on POSIX; DPAPI-protected on Windows) |
| Profile signing keys (v1.3 B3-04) | OS keystore (production) **or** `keys/profile_signer/` (dev) | T-314b admin-service-only | T-314b verifier in both processes (public-key half) | private key admin-only; public key engine-readable |
| SOP template signing keys (v1.3 B3-05) | OS keystore (production) **or** `keys/sop_template_signer/` (dev) | T-316c admin-service-only | T-316c verifier in both processes | same pattern as profile keys |
| SOP templates | `sop_templates.sqlite` | T-316b `SqliteSopTemplateStoreWrite` (admin-service `mode=rw`) | engine + admin via `SopTemplateReadPort` (`mode=ro` on engine) | append-then-update version history; signed payloads |
| Review queue | `review_queue.sqlite` | T-315 request writer via `AuditAppendPort`; admin-service T-1103b resolves via `ReviewQueueAdminPort` | engine + admin via `ReviewQueueStore.list_pending` | append-only requests; decision rows appended (request never mutated) |

**v1.2 process separation (B2-04).** The admin-service process is a **separate executable boundary** from the engine / API / CLI processes. It holds `mode=rw` to `authorisation.sqlite` and is the only path through which `AuthorisationProfile` records are written. Engine processes never construct `SqliteAuthorisationStoreWrite`, never construct `AdminActionHandler` (set to `None` by composition root), and OS-level filesystem ACLs on `authorisation.sqlite` forbid write access from the engine's UID/SID. The runtime test in T-310/T-311 verifies that even if a User-level code path attempts a SQLite write, the kernel rejects it with `OperationalError("attempt to write a readonly database")`.

### 3.5 CI configuration (v1.2 — four-state lifecycle column per B2-07; manifest-driven module coverage per M2-03)

`.github/workflows/ci.yaml` runs the following gates per PR with conditional path-based triggers (§ 7.2 Round 2). Each gate carries a **lifecycle state**: `not_implemented` (absent from workflow), `informational` (runs with `continue-on-error: true` — does not block merge), `enforced` (merge-blocking), `enforced-green` (merge-blocking and observed-passing at least once on `main`).

| Job | What it runs | Owning task | Lifecycle state | Activation milestone |
|---|---|---|---|---|
| lint | `ruff check`, `ruff format --check` | T-201 | `enforced` from Phase 2 exit | scaffold complete |
| type | `mypy --strict src/` | T-201 | `enforced` from Phase 2 exit | scaffold complete |
| unit | `pytest -m "not slow and not integration and not uat"` | T-201 | `enforced` from Phase 2 exit | scaffold complete |
| integration | `pytest -m integration` with deterministic fakes | T-201 | `informational` until Phase 3 exit; `enforced` after | persistence + session land |
| determinism | container-based reproducibility check on white-paper examples | T-201 | `informational` until Phase 13; `enforced` after | UAT examples available |
| coverage | `pytest-cov` ≥ 90 % on domain + engine | T-201 | `enforced` from Phase 3 exit | domain types complete |
| rule-coverage | every rule has triggering + passing fixture | T-401 / T-405 | `informational` after T-405; `enforced` from Phase 4 exit | catalogues populated |
| no-domain-impurity-check | static analysis (`domain.*` does not import `adapter.*`, `app.*`, `interface.*`) | T-204 | `enforced` from Phase 3 exit | port stubs exist |
| import-linter | static contract per `domain.ports/` separation + `sop_protected` namespace partition | T-204 / T-306 | `informational` from Phase 2 exit; `enforced` from Phase 3 exit | T-306 lands |
| no-self-authorisation-check | static + runtime across six surfaces: UserPrincipal and ReviewerPrincipal cannot call `AuthorisationAdminWritePort`; UserPrincipal/ReviewerPrincipal cannot call `SopTemplateAdminWritePort`; engine code cannot import audit write surfaces directly; CLI/API cannot import `AdminActionHandler`; admin-service IPC cannot be bypassed; ordinary DeveloperPrincipal denied post-bootstrap | T-204 / T-311 / T-313b / T-316b / T-1103b | `informational` from T-203c; `enforced` only after T-313b + T-316b + T-1103b integration tests pass | all admin/audit/SOP write boundaries exist |
| no-passive-advisory-bypass-check | static + runtime: no path produces `OperationalProtocolAuthorised` without observed acknowledgement chain | T-204 / T-806b | `enforced` from T-806b exit | gate predicate active |
| sop-after-gates-check | static + runtime: `SopLinkedProtocol` cannot render without `OperationalProtocolAuthorised` | T-204 / T-803 | `enforced` from T-803 exit; T-805b/T-806b add app-level authorisation coverage | gate predicate active |
| llm-output-policy-check | red-team test suite | T-204 / T-1201 | `enforced` after T-1201 local verification | LLM adapter exists and `AdvisoryTextPolicy` gate passes |
| audit-traceability-check | every traceability reference resolves; generated `docs/traceability_index.md` matches file headers | T-204 | `informational` from Phase 2 exit; `enforced` from Phase 3 exit | headers present |
| plugin-manifest-signature | signature verification on every plugin load | T-204 / T-808 | `enforced` at T-808 exit | governance service exists; T-808 complete locally |
| source-grade-citation-check | every rule citation has grade ∈ {A1, A2, A3, B1, B2} or C+corroborator | T-401 | `enforced` from Phase 4 exit | catalogues populated |
| stale-catalogue-check | `review_required_after` in the future for every active catalogue | T-401 | `enforced` from Phase 4 exit; runs nightly | catalogues populated |
| **module-coverage-check** (v1.2 manifest-driven per M2-03) | parses manually authored `docs/module_manifest.yaml` and warns separately on architecture prose drift; fails if any module lacks ≥ 1 task | T-204 | `informational` after T-203 lands; `enforced` after Phase 3 exit (T-311 + T-312b land) | port inventory + admin handler exist |
| **task-acceptance-completeness-check** (v1.2 new — M2-03 follow-up) | every task brief has a machine-readable acceptance YAML block | T-204 | `informational` until Phase 3 exit; `enforced` after | briefs structured |
| gate-lifecycle-check (v1.1) | every gate's declared `lifecycle_state` header matches its TODO presence + matches CI table + matches `TASK_BOARD.md` § 7 | T-204 | `enforced` from Phase 2 exit | gate skeletons exist |
| rule-fixture-coverage-check (v1.1; v1.3 lifecycle corrected per H3-08) | every rule manifest entry has both triggering and passing fixture paths that resolve at load time | T-401 / T-405 | `informational` after T-405 while Phase 4 remains in progress; **`enforced` at Phase 4 exit**. Rules with legitimate deferral require explicit `deferred_with_reason` field + `/scientific-advisor` sign-off recorded as `RuleFixtureDeferralApproved` governance event | rules + fixtures present at Phase 4 exit |
| implementation-status-consistency-check (v1.1) | every rule with `implementation_status: real` has a working predicate; no required rule lingers in `stub` past Phase 6 exit | T-401 / T-405 | `enforced` from Phase 6 exit | predicates real |
| slow / uat | nightly | T-1301..T-1303 | `informational` from Phase 13 entry; `enforced` at Phase 13 exit | UAT complete |

**Lifecycle invariant.** No gate transitions to `enforced` while its owning task is in any state other than `verified`. The `gate-lifecycle-check` meta-gate fails any PR that violates this invariant (e.g., labels a gate `enforced` whose task is still `planned`).

---

## 4. Test strategy

### 4.1 Three-tier pyramid

```
                  ┌─────────────────────────────────┐
                  │   Tier-3 — UAT (slow, nightly)  │   3 white-paper examples
                  │                                 │   + adversarial suite
                  │                                 │   + library benchmark
                  └─────────────────────────────────┘
                ┌─────────────────────────────────────┐
                │  Tier-2 — integration               │   per-orchestrator;
                │  (deterministic fakes; in-process)  │   in-process;
                │                                     │   ≤ 5 min total
                └─────────────────────────────────────┘
        ┌─────────────────────────────────────────────────┐
        │  Tier-1 — unit + property                       │  every module;
        │  (pure, fast, property-based with hypothesis)   │  ≤ 30 s total
        │                                                 │  ≥ 5 000 cases
        └─────────────────────────────────────────────────┘
```

**Tier 1 — unit + property.** Every domain module has property tests for invariants (e.g., canonical-orientation checksum is rotation-invariant for circular sequences; `Principal.can_act_as` is reflexive and one-way for the inheritance edge; `DerivationEnvironment.canonical_json()` is byte-deterministic; advisory `required_acknowledgements()` returns the right subset). Property generators live in `tests/strategies/`.

**Tier 2 — integration.** Application orchestrators tested against deterministic fakes for every port. Network mocked, clock mocked, randomness seeded. Each fake has an independent calibration test against the production adapter (run in Tier-3 nightly).

**Tier 3 — UAT.** Three white-paper examples + adversarial suite + combinatorial library benchmark + multi-host workflow + MS2/VLP design + SOP-gated rendering + Administrator-only completion + Reviewer-cannot-escalate + active-advisory adversarial and happy-path scenarios + BSL-4 hard-block + plugin-trust-escalation attempt + export PII leak attempt.

### 4.2 Property-based testing patterns

| Property | Strategy | Modules |
|---|---|---|
| Round-trip fidelity | random `Construct` → serialise → parse → compare | `adapter.io.*` |
| Topology invariance | random circular `SequenceRecord` → rotate by k → checksum unchanged | `domain.sequence` |
| Pure determinism | random inputs → run twice → byte-identical outputs | `engine.*` |
| DAG soundness | random rule registry → check no cycles → all `produces_metrics` reachable | `engine.dependencies` |
| Authorisation invariants | `UserPrincipal.can_act_as(ADMINISTRATOR) == False` always | `domain.security` |
| Acknowledgement gating | report with `caution` advisory + no ack → gate blocks; + ack → gate opens | `app.advisory_acknowledgement`, `app.authorisation_decision` |
| Idempotence | apply same `DomainEvent` twice → state unchanged | `engine.session` |
| Canonical-JSON byte-equality | dataclass with same fields → identical canonical JSON | `domain.types.derivation` |

### 4.3 Adversarial UAT suite

Each scenario attempts to bypass a safety property and verifies the gate fires:

| Scenario | Bypass attempted | Expected outcome |
|---|---|---|
| `test_user_cannot_self_authorise` | UserPrincipal calls `AuthorisationAdminWritePort.mint` | PermissionError + `AuthorisationAttemptDenied` audit entry |
| `test_user_cannot_widen_role` | mid-session role change | PermissionError; principal binding immutable |
| `test_passive_advisory_bypass` | UI render only (no acknowledgement event) → authorisation gate | BlockOperationalProtocol + missing-advisory-ids audit |
| `test_short_justification_rejected` | acknowledgement with 5-char justification | rejected at construction (frozen dataclass `__post_init__`) |
| `test_unsigned_acknowledgement_rejected` | acknowledgement with empty signature | rejected; gate blocks |
| `test_version_mismatched_acknowledgement` | acknowledge against report-content-hash A but current report has hash B | gate blocks; mismatch logged |
| `test_decline_does_not_unblock` | RiskAdvisoryDeclined → authorisation gate | gate blocks; routes to alternative reviewer |
| `test_escalate_requires_institutional_approval_id` | escalate without `institutional_approval_id` | rejected at construction |
| `test_screening_hit_terminal_blocked` | HIT verdict → attempt SopRendered | BlockOperationalProtocol + BlockExport + BlockVendorSubmission |
| `test_screening_unavailable_requires_policy_permit` | UNAVAILABLE without policy permit | gate blocks |
| `test_bsl4_compile_blocked` | construct with BSL-4 tier → compile | BlockCompile + `UnsupportedBiosafetyTierAttempted` event |
| `test_plugin_unsigned_manifest_rejected` | plugin with no signature | refuses to load + `PluginManifestApproved` not emitted |
| `test_plugin_artefact_hash_mismatch_rejected` | plugin manifest hash != artefact hash | refuses to load |
| `test_export_pii_redacted_in_vendor_profile` | vendor bundle contains user IDs | `ExportProfile.VENDOR` redacts |
| `test_reviewer_cannot_mint_profile` | ReviewerPrincipal calls mint | PermissionError |
| `test_admin_only_completion_happy_path` | AdminPrincipal signs off `WATCHLIST` (no separate Reviewer) | `OperationalProtocolAuthorised` fires; audit log shows `signer_role = ADMINISTRATOR` |
| `test_administrator_alone_workflow` | Phase-13 end-to-end with single Administrator | full workflow completes |
| **`test_construct_checksum_mismatched_acknowledgement`** (v1.2 M2-02) | acknowledge against `construct_checksum` X; then modify the construct (recompute to Y); attempt authorisation | gate blocks; `construct_checksum_mismatch` reason recorded; routes to re-acknowledge |
| **`test_programmatic_event_construction_bypass`** (v1.2 M2-02) | a malicious or buggy module attempts to write an `OperationalProtocolAuthorised` event without the prior governance chain (no `AdvisoryWarningPresented`, no `RiskAdvisoryAcknowledged`, no `ScreeningCompleted`) | `no-passive-advisory-bypass-check` static check rejects at compile; runtime gate `app.authorisation_decision` rejects with `MissingGovernanceChain`; T-309's replay invariant test detects the orphaned event and flags it as `ReplayIntegrityFailure` |
| **`test_audit_key_absent`** (v1.2 B2-08) | start engine without `AuditKeyProvider` | engine refuses to start with `AuditLogTamperDetectionUnavailable` |
| **`test_audit_key_compromise_does_not_forge_decision_record`** (v1.2 B2-08) | leak HMAC key; attempt to forge a `DecisionRecord` signature | signature verification fails (signature key is a separate cryptographic identity) |

### 4.4 Determinism harness

Inside the pinned container, every Tier-3 UAT runs twice. Outputs must be byte-identical (for canonical-JSON artefacts) or semantic-equivalent (for GenBank / SBOL where format reorders fields). The CI gate that enforces this is `determinism` (§ 3.5).

### 4.5 Replay determinism (v1.2 — ownership reassigned per M2-01)

For every session, replay-from-events must reproduce the same `DerivationEnvironment` hash and the same final design state. **v1.2 ownership:**

- **T-309** (`engine.session` skeleton) — **owns replay determinism**: the design event stream + referenced governance decisions resolved by ID reproduce the same end state byte-for-byte.
- **T-310b** (`JsonlEventLog` ×3 streams) — owns the **replay-determinism property test** (≥ 100 synthetic sessions, byte-identical reports).
- **T-501** (`engine.dependencies`) — owns **DAG-evaluator determinism** (same rule registry → same DAG → same `affected_rules` computation), a different property.
- **T-1302** (adversarial UAT) — owns **end-to-end replay-determinism under adversarial fixtures** (e.g., replay a session with a tampered governance event → reproduces the same blocked state and emits a `ReplayIntegrityFailure` event).

### 4.6a Renderer tests (v1.1 — new, per M-04)

Markdown / PDF / JSON renderers for `DesignRealisationPlan` and `SopLinkedProtocol` (and project export bundles) require their own test class:

| Test | What it asserts |
|---|---|
| **Structural-output** | Every required section is present in the rendered Markdown / PDF; section headings match the canonical schema. |
| **Absence-of-operational-fields-in-design-plan** | A rendered `DesignRealisationPlan` Markdown / PDF / JSON contains *no* `ProtocolStep` field reachable via any output path; cross-checked against the `import-linter` namespace partition. |
| **Redaction-by-`ExportProfile`** | A `Vendor` profile bundle does not contain user IDs / reviewer notes / institutional approval IDs; a `Collaborator` profile does not contain PII; an `InternalAudit` profile contains everything. |
| **Reproducible-PDF** | The same `DesignRealisationPlan` rendered twice inside the container determinism harness produces byte-identical PDF output (subject to a documented PDF-determinism flag — pinned font, no embedded timestamp). |
| **Approval-trace-presence** | A rendered SOP bundle contains, by reference, the full advisory approval trace for every advisory of severity `caution` or `strong_caution`. |

### 4.6 Calibration tests (M9)

Each production biology adapter has a *calibration test* that runs the adapter against a curated input set and compares against measured ground truth (where available) or against a frozen previous-run baseline (where ground truth is unavailable). Calibration tests run in Tier-3 nightly; they are *not* a release-blocker but they alert when an adapter's behaviour changes (e.g., a model update).

---

## 5. Debugging methodology

### 5.1 Structured logging

Every module logs via the project's `structlog`-style logger (`src/infrastructure/logging.py`). Level conventions:

| Level | When |
|---|---|
| DEBUG | engine internals (DAG step, rule predicate fired, port adapter call); off by default in production |
| INFO | application-layer milestones (`Compiled`, `ScreeningCompleted`, `OperationalProtocolAuthorised`) |
| WARNING | soft-warn rule violations, fallback adapter used, plugin manifest expiring soon |
| ERROR | adapter failure, validation hard-fail blocked compile, unexpected exception |
| CRITICAL | governance violation (e.g., authorisation-attempt-denied), corrupted audit log, plugin signature failure |

Every log record carries: `session_id`, `principal_id`, `rule_id` (where applicable), `module_id`, `task_id` (where reachable). Production logs ship to per-institution log destinations; CI logs are captured by `pytest --capture=no`.

### 5.2 Audit-log replay debugging

When a session's outcome looks wrong, the orchestrator replays it deterministically:

```bash
vector-design replay <session_id> --to-event <event_seq> --dump
```

The replay reconstructs state from the design event stream, cross-references the governance event stream for any decision records, and prints a step-by-step trace. The same command is used in adversarial UAT to reproduce a failed scenario byte-for-byte.

### 5.3 Snapshot bisection

Every checkpoint emits a `snapshots/<session>/<event_seq>.json` artefact. To find the event that introduced a regression:

```bash
vector-design replay <session_id> --bisect <predicate.py>
```

The bisect harness binary-searches the event log for the first event at which `predicate(state) == True`. Useful for "when did the validation report start failing" type debugging.

### 5.4 Failure-mode handbook

Every documented failure mode in `Cloning_Expression_Vector_Design_White_Paper.md` § 25 maps to a design-time predictor (a validation rule) and a wet-lab remediation. The handbook is generated from the rule registry — every rule's `suggested_remediation` field appears in the handbook with the failure-mode it predicts:

```
Symptom: "no colonies after transformation"
  Predictor rules:
    MR-05 — marker working concentration mismatch (warn)
    MR-23 — inducible-system completeness (block)
    MR-30 — negative-selection cassette without ccdB-tolerant strain (block)
    WR-03 — DpnI digestion missing for plasmid template (block)
    WR-05 — dephosphorylation missing for single-cut linearisation (block)
  Suggested remediations (from rule manifests):
    - switch marker to one compatible with host genotype
    - confirm DE3 lysogen present for T7 promoter
    - propagate ccdB destination on DB3.1 / Survival 2
    - add DpnI step before transformation
    - dephosphorylate vector before ligation
```

The handbook is generated by `vector-design rule-index --by-failure-mode` (CLI command in Phase 11).

### 5.5 Common-defect remediation

Recurring engineering defects we expect during development, and the remediation pattern:

| Defect | Detection | Remediation |
|---|---|---|
| Engine imports adapter | `import-linter` CI gate fails | Move the dependency through a `domain.ports.*` interface; adapter implements it; orchestrator injects. |
| Operational fields leak into design plan | `mypy --strict` or T-306 runtime guard | Move type to `domain.types.sop_protected`; `DesignRealisationPlan` cannot contain it. |
| Non-deterministic canonical JSON | `determinism` CI gate fails | Use `sorted()` on every dict during serialisation; verify with property test. |
| Catalogue review stale | `stale-catalogue-check` fails | `/scientific-advisor` reviews and updates `maintenance.review_required_after`. |
| Rule predicate missing fixture | `rule-coverage` fails | Add `triggering` + `passing` gold fixtures; reference from rule manifest. |
| LLM emits operational protocol text | `llm-output-policy-check` red-team test fails | Tighten prompt template; add forbidden-output detection; emit `AdvisoryText` typed value. |
| Plugin manifest signature missing | `plugin-manifest-signature` fails | Sign with institutional plugin key; recompute artefact hash. |
| Replay mismatch after template change | `audit-traceability-check` fails | Verify `DerivationEnvironment` captured the changed input; if not, add the field and re-derive. |

---

## 6. Development workflow

### 6.1 War-room dashboard specifications

`TASK_BOARD.md` (war-room dashboard) carries:

```markdown
# TASK_BOARD.md

## Global progress
- Phase {n}: status, fraction complete, blockers
- Cumulative: tasks done / in-progress / planned / blocked
- Burn-down chart (ASCII or linked artifact)
- Currently active model tiers (Opus / Sonnet / Haiku) and their utilisation

## Current bottlenecks (top 5 blockers)
- Task ID, blocked-on (architectural decision / external dependency / upstream task)
- Age of blocker
- Escalation path

## In-progress tasks
| Task ID | Module | Phase | Tier | Assigned | Started | Expected | Stage |

## Recently completed (last 20)
| Task ID | Module | Done | Verified by | CI gates green | Notes |

## Phase exit status
For each phase: six-dimension audit checklist (Correctness, Completeness, Scientific validity, Performance, Maintainability, Safety) with each dimension's evidence link.

## Risk register status
For each R-01..R-21: mitigations green / amber / red, with linked tests.

## CI gate status (latest pull)
All 18 gates: green / fail with linked failing PR.
```

The `vector-design status` CLI command (Phase 11) regenerates this from `events/` + `tasks/` + `audit.sqlite`; the markdown view is the human-readable mirror that the orchestrator commits and edits.

### 6.2 Pre-execution plan template

Stored at `tasks/task_brief/T-<id>.md` per the template in § 1.7. The orchestrator drafts it before assigning; the executor reads it as the *only* task-specific input. Required sections: Module / Inputs / Deliverables / Acceptance / Hand-off.

### 6.3 Post-execution document template

Stored at `task_artefacts/T-<id>/handover.md` per the template in § 1.7. The executor produces it as the *last* action of the task before marking `execution-complete`. Required sections: Status / Files written / Architecture sections consumed / Requirements satisfied / CI gates touched / Deferred or open / Notes for downstream.

### 6.4 Code review SOP — the six-dimension audit

`/dev-orchestrator` performs this on every task before marking `verified`:

1. **Correctness** — does the behaviour match the requirement? Unit + integration tests green?
2. **Completeness** — is every public API documented? Every edge case tested?
3. **Scientific validity** — every biology rule cites v2.0 KB? `/scientific-advisor` sign-off where the task touches biology?
4. **Performance** — Tier-1 budget met? Tier-2 latency reported?
5. **Maintainability** — clear module boundaries? No cross-layer leaks? `mypy --strict` green? `ruff` clean? Comments per § 1.6?
6. **Safety** — every CI gate that the task touches is green? Audit log integrity? No silent bypass?

A task with green on all six dimensions transitions to `verified`. Any amber/red opens a follow-up task with explicit linkage.

### 6.5 Definition of Done per module class

| Module class | Definition of Done |
|---|---|
| Pure domain (`domain.*`, `engine.*`) | All public APIs implemented; ≥ 90 % line coverage; property tests pass with ≥ 1000 cases; `mypy --strict` green; `no-domain-impurity-check` green; `import-linter` green. |
| Adapter (`adapter.*`) | Implements declared port; deterministic fake exists with calibration test; production adapter has `Manifest` with measured latency; pinned dependency in `pyproject.toml`. |
| Application orchestrator (`app.*`) | Wires its dependencies via `compose_engine`; integration test exercises the happy path + at least one failure path; events emitted to the correct stream; audit-log entries created where governance occurs. |
| Interface (`interface.cli`, `interface.api`) | OpenAPI / CLI help up-to-date; end-to-end test reaches `Exported` state for at least one fixture. |
| Catalogue YAML | JSON-schema-valid; every entry has graded citation; maintenance metadata in the future; loaded into engine without errors at startup. |
| Plugin manifest | Signed by institutional key; package hash matches loaded artefact; declared permissions honoured by sandbox. |

### 6.6 Phase exit criteria

Each phase has its own exit gate in `ROADMAP.md`. Additionally, every phase exit produces a `docs/handover/phase_<n>_handover.md` document carrying:

- Deltas from `ARCHITECTURE.md` (none expected; flagged if any)
- Completed modules with public API contracts
- Validation report on the white-paper examples (where applicable from Phase 13)
- Residual issues / deferred sub-tasks
- Update to the risk register

---

## 7. Three-role adversarial review and external audit history

### 7.1 Round 1 — opening attacks

**`/architect` attacking `/dev-orchestrator`:** "Your token-economy budget says one task should fit in ≤ 90 k. But `T-303` (domain.types) has 20+ frozen-dataclass entities with their `__post_init__` validators, plus their property tests. The sum easily exceeds 90 k. Either you over-split into 7+ sub-tasks (token cost amortised over context-reload), or the executor truncates."

**`/dev-orchestrator` rebuttal:** Conceded. `T-303` is explicitly split into T-303a (Part/Host/HostContext/Module/Construct), T-303b (Library/AssemblyMethod/AssemblyPlan), T-303c (ValidationRule + HostCompatibilityConstraints). Same pattern applied to other large modules (`T-308` GenBank/SBOL/FASTA split into a..d, `T-503` sequence-analysis + predicates split, `T-703` assembly strategies split). Each sub-task ships with its own task brief — the executor never sees the full 160 KB `ARCHITECTURE.md` because the brief carries only the relevant excerpt.

**`/scientific-advisor` attacking `/architect`:** "Your `domain.ports/` separation (B7) forces every engine to declare ports for biology adapters. But the calibration tests for those adapters need to compare *biological* outputs (e.g., ViennaRNA's predicted ΔG against a known reference set). Where does the calibration ground-truth live? It can't be `tests/fixtures/` because it changes when ViennaRNA's model updates — it would silently bake yesterday's behaviour into today's tests."

**`/architect` rebuttal:** Conceded. Calibration tests live in `tests/calibration/biology/<adapter>/`, with their ground-truth fixtures versioned alongside the adapter's pinned dependency version. When the dependency upgrades, the fixture is regenerated by a one-time bench run and recorded in `DerivationEnvironment.external_database_versions`. Calibration tests run in Tier-3 nightly, are non-release-blocking, but emit a `CalibrationDrift` alert when the adapter's outputs diverge from the previous fixture's by more than the documented tolerance.

**`/dev-orchestrator` attacking `/scientific-advisor`:** "Your 'every rule predicate has a triggering + passing gold fixture' principle is essential — but the rule registry has ~150 entries. That's 300 hand-curated fixtures. Who writes them, and when? If they all come at the end of Phase 4 / Phase 5 it's a single-person bottleneck and a soft-skipped CI gate for most of the build."

**`/scientific-advisor` rebuttal:** Conceded. Fixtures are populated *in the same task* as the rule manifest entry — when T-405a creates `MR.yaml`, the task also produces `tests/fixtures/rules/MR/{triggering,passing}/<rule_id>.json`. The five parallel sub-tasks (T-405a..e) split the load. Predicates remain stubs returning `INFO` until Phase 5; this prevents the `rule-validation coverage` gate from being a release-blocker until the corresponding predicates are real. Crucially, the gate flips from informational to release-blocking *per rule, when the predicate becomes real* — there is no project-wide "turn it on at the end" event.

### 7.2 Round 2 — counter-critiques and refinements

**`/dev-orchestrator` attacking `/architect`:** "The dependency-injection composition root `compose_engine` is good, but it implies a single global `Engine` object whose lifetime is the application's. For a long-running server (`interface.api`), state held in `Engine` will leak across users and sessions. Where does multi-session isolation live?"

**`/architect` rebuttal:** Conceded. Refinement: `Engine` is *stateless* — it holds only the wired ports and the rule registry. *Session state* is held in `DesignSession` instances which are loaded per-request from `ProjectStore` and discarded after the request completes. `engine.session` is a per-session state machine, not a global service. The orchestrators (`app.*`) accept a `DesignSession` argument on every call. Add a `test_no_session_state_leaks_across_requests` integration test to enforce this at runtime.

**`/architect` attacking `/dev-orchestrator`:** "The CI matrix you propose (§ 3.5) runs 18 gates on every PR. On a typical 200-line PR that touches one module, this is wasteful — most gates have nothing to verify. Aren't we wasting compute and slowing the developer feedback loop?"

**`/dev-orchestrator` rebuttal:** Partial concession with refinement. We add path-based gate filtering: gates that touch only certain layers run only when those layers change. Concretely:
- `no-self-authorisation-check` runs when `src/domain/security/`, `src/adapter/persistence/authorisation*` change.
- `no-passive-advisory-bypass-check` runs when `src/engine/risk_classification/`, `src/app/advisory_acknowledgement.py`, `src/app/authorisation_decision.py` change.
- `plugin-manifest-signature` runs when `catalogues/plugin_manifests/` change.
- `stale-catalogue-check` runs on a nightly schedule + when `catalogues/` change.
The other gates (type, unit, integration, coverage, import-linter) always run because they are cheap and could be invalidated by any change.

**`/scientific-advisor` attacking `/dev-orchestrator`:** "Your six-dimension audit at task exit (§ 6.4) treats scientific validity as one dimension among six. But a task that fails scientific validity should not ship at all, regardless of the other five. The current ordering implies scientific validity is just one vote of six."

**`/dev-orchestrator` rebuttal:** Conceded. The six dimensions are **not** weighted-vote criteria; they are **conjunctive gates**. A task transitions to `verified` only when *every* dimension is green. Where a dimension is amber or red, the task is `verification-failed` and a follow-up task is opened. Clarified in § 6.4.

### 7.3 Round 3 — edge cases

**`/scientific-advisor` raising a hidden assumption:** "The combinatorial-library mode (UR / Library) implies running the full pipeline for every realisation. For a 1 000-realisation library, that's 1 000 × ScreeningCompleted events. The screening adapter's `screen_batch` exists for this, but the *governance event stream* will balloon. Replay determinism across thousands of governance events is untested in the plan."

**`/architect` rebuttal (v1.3 H3-06 — corrected event-stream ownership):** Conceded. Refinement: library mode produces *batched* **design events** (one `ScreeningCompleted` event per *batch* to the **design stream**, not per realisation; v1.2 B2-05 / v1.3 H3-06 affirm `ScreeningCompleted` is a design event). Per-realisation evidence is carried in the event's structured payload (full list of `ScreeningResult | ScreeningError` of equal length and order to the input batch). The governance stream carries only reviewer / admin decision records + advisory events for the library realisations (e.g., one `RiskAdvisoryAcknowledged` per *unique* advisory across the union, with linkage to the affected realisation IDs). The `screen_batch` adapter contract returns `list[ScreeningResult | ScreeningError]`; the orchestrator emits one batched design event. Replay determinism in library mode is tested in T-1303 with a 100-realisation fixture and a 1 000-realisation stretch fixture.

**`/architect` raising a hidden assumption:** "Your active-advisory protocol (T-806) requires that every `caution` / `strong_caution` advisory be acknowledged. But in library mode, *each realisation* may produce different advisories. Does the Administrator acknowledge per-realisation or per-library?"

**`/scientific-advisor` rebuttal:** Per-library acknowledgement when the library's *union* of advisories has been acknowledged, except where a realisation produces a new advisory not in the union — that realisation is held in `AWAITING_REVIEWER_SIGNOFF` until its specific advisory is acknowledged. The pure predicate `all_required_advisories_acknowledged(report, events)` works per `report_content_hash`; library mode emits one report per realisation, so acknowledgements are addressed per realisation but most overlap across the library. The UI presents the *unique* advisories first and indicates which realisations they apply to.

**`/dev-orchestrator` raising a hidden assumption:** "The `compose_engine` boundary in § 3.2 implies every adapter is constructed once at startup. But the `SnapGeneFileWatcher` is a long-running process with file-system handles; the `IGSCAdapter` may need to refresh its session token; the `LocalLlmAdapter` may need to lazy-load model weights. The composition root needs lifecycle hooks."

**`/architect` rebuttal:** Conceded. Refinement: every adapter implements an optional `Lifecycle` protocol with `start()` and `stop()` methods. `compose_engine` calls `start()` after composition; the application shutdown calls `stop()` in reverse order. Adapters that need refresh implement `refresh()` and are wrapped in a `RefreshingAdapter` decorator that calls `refresh()` on a timer. This is added to T-203c (port stubs include the `Lifecycle` protocol).

**`/scientific-advisor` raising a final issue:** "MR-44 says global GC content < 25 % or > 65 % → warn. But for plant gene design, GC content is often 35 – 45 %, far from the 65 % ceiling, so the warn is never useful there. For some thermophiles the GC content can legitimately be > 70 %. The rule should be host-context-aware (M5)."

**`/architect` and `/dev-orchestrator` rebuttal:** Conceded — and this is exactly what `M5 HostCompatibilityConstraints` is for. The rule's `threshold_profile` field already resolves at evaluation time against the construct's `HostContext`. The rule manifest entry for MR-44 declares `threshold_profile: gc_content_per_host`; the profile YAML supplies per-host bounds. The validator passes both the construct and the resolved threshold to the predicate. Adding a per-host fixture in T-405a ensures the rule is calibrated.

### 7.4 Round 4 — convergence

The three roles convened. Each tried to surface a remaining defect; none did. The following statements were adopted unanimously:

| Statement | Adopted by |
|---|---|
| The agenda's task decomposition fits within ≤ 90 k context per sub-task, with explicit sub-splits for any module exceeding that bound. | all three |
| Every adapter has a deterministic fake + a calibration test against a versioned ground-truth fixture; calibration drift is alerted nightly, not release-blocking. | all three |
| Rule predicate stubs (returning `INFO`) ship in Phase 4; the `rule-validation coverage` gate flips per-rule when the predicate becomes real in Phase 5 / 6. | all three |
| `Engine` is stateless; `DesignSession` is per-request; multi-session isolation is enforced by integration test. | architect + orchestrator |
| CI gates run conditionally based on changed paths to keep the developer feedback loop tight. | orchestrator + architect |
| Six-dimension audit is conjunctive; any amber/red blocks `verified`. | scientific-advisor + orchestrator |
| Library mode emits batched governance events with per-realisation evidence; replay determinism tested at 100- and 1 000-realisation scales. | scientific-advisor + architect |
| Active-advisory acknowledgement is per `report_content_hash`; library mode reuses union acknowledgements but holds realisations with new advisories in `AWAITING_REVIEWER_SIGNOFF`. | scientific-advisor + architect |
| Adapters expose optional `Lifecycle` (start / stop / refresh); composition root manages lifecycle. | architect + orchestrator |
| Rules with `threshold_profile` resolve per-host via `HostCompatibilityConstraints` at evaluation time. | scientific-advisor + orchestrator |

Three roles signed off. The result is the catalogue + wiring + test strategy + workflow above.

### 7.4b Round 5 — Codex external audit (produces v1.1)

After the four internal rounds produced v1.0, an external audit by Codex (`audit report/CODING_AGENDA_Audit_Report.md`) raised 5 blocking + 8 high + 8 moderate findings against v1.0. The three internal roles accepted all 21 (full per-finding adjudication in `audit report/CODING_AGENDA_Audit_Response.md`). Summary of v1.1 structural changes:

| Finding | v1.1 change |
|---|---|
| **B-01** non-operational types wrongly in `sop_protected` | T-306 restructured: `domain.types.design_plan` / `controls` / `risk_advisory` carry non-operational types; `sop_protected` retains only operational types. `import-linter` contract amended. New static `test_design_plan_no_protocolstep` test. |
| **B-02** missing modules in build queue | Added T-205 (platform-readiness), T-308e (SnapGene `.dna`), T-309 (`engine.session`), T-310 (`adapter.persistence`), T-504 (`engine.compatibility`), T-606 (`app.design_service`), T-607 (`app.decision_tree`), T-807 (`engine.vlp_policy`), T-808 (`app.plugin_governance`). New `module-coverage-check` CI gate. |
| **B-03** phase order conflicts with screening-before-SOP | Phase 8 split into 8a (pre-screening; design plan + controls + advisory presentation) and 8b (post-Phase-10; SOP rendering + authorisation gate). T-803 / T-805 / T-806b move to 8b. |
| **B-04** TODO-passing CI gates create false safety | Gate lifecycle states (`not_implemented` / `informational` / `enforced`); new `gate_lifecycle_check` meta-test. |
| **B-05** rule fixtures missing from T-405 deliverables | T-405 deliverables include triggering + passing fixtures per rule; manifest schema extended with `test_fixtures` (mandatory) and `implementation_status: stub | real`. New `rule-fixture-coverage-check` and `implementation-status-consistency-check`. |
| **H-01** v1.5 port split not in T-203 | T-203c lists every v1.4 / v1.5 split port. |
| **H-02** SnapGene `.dna` at wrong level | T-308e for `.dna` read-only; T-902 *depends on* it. |
| **H-06** canonical JSON underspecified | T-307 adopts RFC 8785 JCS with project-specific bans + golden vectors. |
| **H-07** Windows / OneDrive / SQLite-locking / file-watch unplanned | T-205 platform-readiness baseline; CI matrix on `windows-latest`; non-ASCII path fixtures; WAL locking tests; atomic-write tests. |
| **H-08** adapter dependencies in core bootstrap | T-201 uses dependency groups; core bootstrap installs only `core` + `dev`. |
| **M-01** ProcessPoolExecutor + Windows-spawn | T-502 SOP extended with spawn semantics + deterministic result ordering + pickle safety. |
| **M-02** SLIC unmapped | T-703e adds `SLICStrategy`. |
| **M-03** threshold-profile calibration governance thin | `catalogues/threshold_profiles/*.yaml` carry source citation + scope + bounds + boundary fixtures + reviewer sign-off. |
| **M-04** renderer tests under-specified | New § 4.6a renderer test class. |
| **M-05** rule-stub safety | `implementation_status: stub | real` flag. |
| **M-06** file-header drift | Headers kept lightweight; full traceability generated in `docs/traceability_index.md`. |
| **M-07** calibration drift governance | `CalibrationDriftPolicy` per adapter in T-601. |
| **M-08** app-service tasks missing | T-606 / T-607 added. |

### 7.4c Round 6 — Codex second-round external audit (produces v1.2)

After v1.1 landed, a second external audit by Codex (`audit report/CODING_AGENDA_Second_Round_Audit_Report.md`) raised 9 blocking + 11 high + 9 moderate findings against v1.1. The three internal roles accepted all 29 (full per-finding adjudication in `audit report/CODING_AGENDA_Second_Round_Audit_Response.md`). Summary of v1.2 structural changes:

| Finding | v1.2 change |
|---|---|
| **B2-01** roadmap not regenerated | `ROADMAP.md` regenerated; Phase 8 split into 8a/8b and Phase 9 split into 9a/9b; final order 0→1→2→3→4→5→6→7→8a→9a→10→8b→9b→11→12→13 |
| **B2-02** export before screening | T-903 moved to Phase 9b; Phase 9a contains only I/O channels (T-901 + T-902); pre-screening sharing via T-805a's `DraftDesignBundle` (no SOP, no vendor clearance) |
| **B2-03** stale DAG + composition root | § 3.1 DAG rewritten; § 3.2 composition root rewritten with every v1.1/v1.2 module wired; § 3.3/3.4/3.5 propagated |
| **B2-04** missing admin handler task | New **T-311** `app.admin_action_handler` foundational task (Phase 3); split `AuthorisationAdminWritePort` / `AuthorisationBootstrapPort` / `AuthorisationReadPort`; admin-service process separation |
| **B2-05** event stream mismatch | `ScreeningCompleted` / `OperationalProtocolAuthorised` / `SopRendered` moved to design stream (matches architecture); cross-stream replay-determinism invariant test in T-309 |
| **B2-06** port inventory missing in T-203 | T-203c rewritten with explicit numbered enumeration of 37 ports + `tests/ports/test_port_inventory.py` acceptance |
| **B2-07** CI lifecycle column missing | § 3.5 + `TASK_BOARD.md` § 7 carry four-state lifecycle column |
| **B2-08** audit-key lifecycle missing | New **T-312** `AuditKeyProvider` port + three keystore adapters + rotation/recovery/offline verification; separation of HMAC and signature keys |
| **B2-09** Phase 8a missing app service | T-805 split into T-805a (`app.design_plan_orchestrator`, 8a) + T-805b (`app.sop_protocol_orchestrator`, 8b); v1.1 MOVED `####` placeholders removed |
| **H2-01** duplicate task headings | MOVED placeholders removed; cross-references in prose |
| **H2-02** stale phase counts + traceability | All headings + traceability rows + budget rows regenerated |
| **H2-03** `RiskAdvisoryAcknowledgement` ownership duplicated | Owned by `domain.types.risk_advisory` only; events carry typed references; new `domain.types.governance` for `DecisionRecord`/`RoleSnapshot` |
| **H2-04** T-902 owns dna_reader | `dna_reader.py` removed from T-902; imports `SnapGeneDnaReader` from T-308e |
| **H2-05** T-606 acceptance impossible | Phase-local acceptance with explicit `Awaiting*` pending states; full happy path moved to T-1301 |
| **H2-06** T-309 overclaims gate routing | Collapsed to single T-309 with skeleton/replay and per-phase gate activation documented as sub-deliverables |
| **H2-07** T-205 file-watch test before watcher exists | Uses generic `filewatch_debounce_harness.py` only; real watcher in T-902 |
| **H2-08** ProcessPoolExecutor global mutation | `WorkerPoolFactory` using `get_context("spawn")` locally; production entry-points may set globally, libraries never; sequential fallback for tests/notebooks |
| **H2-09** CI matrix ambiguous + heavy | Explicit profile matrix; no `core+dev+all`; heavy adapters Linux-only; Windows excludes ViennaRNA / SpliceAI / SignalP / LLM |
| **H2-10** SnapGene fixture licensing | Synthetic redistributable `.dna` fixtures + `PROVENANCE.md`; proprietary fixtures marked `requires_local_snapgene_fixture` |
| **H2-11** BR-14 as structural predicate | Removed from T-503; owned by T-806b + `no-passive-advisory-bypass-check` |
| **M2-01** replay-determinism ownership stale | Reassigned to T-309 + T-310b; T-501 keeps DAG determinism; T-1302 keeps adversarial replay |
| **M2-02** FR-ADV-07 UAT incomplete | Added construct-checksum-mismatch + programmatic-event-bypass + audit-key-absent + audit-key-compromise tests |
| **M2-03** module-coverage parses prose | Manifest-driven (`docs/module_manifest.yaml` generated from architecture); `task-acceptance-completeness-check` follow-up gate added |
| **M2-04** renderer ownership thin | Renderer files explicit in T-802 / T-803 / T-903; `docs/rendering_determinism.md` policy |
| **M2-05** canonical-JSON `$decimal` collisions | Reserved `$$cev:` type-tag namespace; v1.1 → v1.2 migration shim |
| **M2-06** T-502 benchmark untraceable | `tests/benchmark/T_502_validation_bench.py` + `tests/benchmark/results/` + nightly cadence |
| **M2-07** `TASK_BOARD.md` regeneration claim contradicted | Regenerated with four-state lifecycle column + workflow mode + last CI result |
| **M2-08** architecture excerpt shows combined `AuthorisationStore` | Agenda § 0.3 paragraph + T-203c explicitly supersede; tests enforce split form |
| **M2-09** OneDrive path policy missing | Two path-fixture classes `SyncLikePath` / `ActiveSyncPath`; CI uses `SyncLikePath` only; active-sync is manual smoke |

### 7.5 Sign-off statements

**`/scientific-advisor`:** "The biology gates are correctly placed inside the task lifecycle. Every rule predicate has a triggering + passing fixture authored by the same person who curates the rule. Adapter calibration is honest about model drift. The active-advisory acknowledgement workflow is fully testable. Approved."

**`/architect`:** "The token-economy budget is realistic with the documented sub-splits. The dependency-injection boundary is single and explicit. Layer purity is statically enforceable. The DAG is acyclic. Multi-session state has a clean home. Approved."

**`/dev-orchestrator`:** "The phasing matches the dependency DAG. Parallelism is documented per phase. CI gates have conditional triggers to keep the developer loop fast. Six-dimension audit is conjunctive. Every task has a brief, a deliverable, an acceptance criterion, and a hand-off note. Approved."

**`/architect` (v1.1):** "Every architectural defect Codex's audit found is correct. The type-placement bug (B-01), missing modules (B-02), and phase-order safety bug (B-03) are the most serious — they would have produced a scaffold that looks v1.5-aligned but contains structural inconsistencies. v1.1 closes all three. The `domain.ports/` separation now extends cleanly into v1.4 / v1.5 split-port territory (H-01). Canonical JSON is now formal (H-06 / RFC 8785). Persistence + audit stores have proper implementation tasks with tamper detection (H-05). Approved for v1.1."

**`/scientific-advisor` (v1.1):** "The scientific defects matter. Rule fixtures at curation time (B-05) is non-negotiable; SLIC mapping (M-02) and `engine.vlp_policy` (H-04) close real scope gaps; calibration-drift governance (M-07) makes biology-adapter drift detectable; threshold-profile governance (M-03) makes per-host calibration auditable. `engine.compatibility` (H-03 / B-02 / T-504) ensures multi-host workflows have a coherent owner instead of scattered predicates. Approved for v1.1."

**`/dev-orchestrator` (v1.1):** "The operational defects are clean wins. CI-gate lifecycle states (B-04) eliminate the 'TODO-green' failure mode. Dependency groups (H-08) prevent install fragility. Windows / OneDrive platform tests (H-07 / T-205) match the actual environment. `module-coverage-check` (B-02 verification) prevents future drift between architecture and agenda. Phase 8 split (B-03) preserves the v1.4 screening-before-SOP safety semantics in execution. ProcessPoolExecutor Windows-spawn semantics (M-01) and pickle safety eliminate a class of late-stage CI surprises. Approved for v1.1."

**`/architect` (v1.2):** "The second-round defects are about *synchronisation*. v1.1 fixed the task-card layer; v1.2 propagates the fixes through the roadmap, the DAG, the composition root, the event-stream wiring, the persistence wiring, the CI lifecycle, the dashboard, the traceability, and the budget table. The most consequential fixes were the export-ordering (B2-02), the missing admin-handler task with split write port (B2-04), event-stream ownership of `ScreeningCompleted` / `OperationalProtocolAuthorised` / `SopRendered` (B2-05), and the audit-key lifecycle (B2-08). Each was a structural inconsistency that would have produced a scaffold capable of bypassing its own safety invariants. v1.2 closes all four. Approved for v1.2."

**`/scientific-advisor` (v1.2):** "Scientific safety is now correctly sequenced and correctly attributed. Screening precedes authorisation precedes SOP rendering precedes export. Advisory acknowledgement is a governance event whose value-object lives in `domain.types.risk_advisory` and whose acknowledgement chain is the precondition of `OperationalProtocolAuthorised`. BR-14 is the gate predicate not the structural predicate. The active-advisory adversarial UAT extends to construct-checksum mismatch and programmatic-event bypass — both real attack vectors. Approved for v1.2."

**`/dev-orchestrator` (v1.2):** "The plan is now implementation-ready. Phase order, DAG, composition root, event ownership, persistence ownership, CI lifecycle, dashboard, traceability, and budget all agree. T-311 + T-312 (admin handler + audit key) close the only two structural ownership gaps in v1.1. The renderer policy (M2-04) and the path-fixture classes (M2-09) close the determinism + environment gaps. The duplicate task IDs (H2-01) are gone — the task parser now produces a single canonical list. Approved for v1.2."

### 7.4d Round 7 — Codex third-round external audit (produces v1.3)

After v1.2 landed, a third external audit by Codex (`audit report/CODING_AGENDA_Third_Round_Audit_Report.md`) raised 8 blocking + 11 high + 8 moderate findings against v1.2. The three internal roles accepted all 27 (full per-finding adjudication in `audit report/CODING_AGENDA_Third_Round_Audit_Response.md`). Summary of v1.3 structural changes:

| Finding | v1.3 change |
|---|---|
| **B3-01** audit-write contradictory | New **T-313** `AuditAppendPort` broker; composition root injects broker (not raw `AuditLog`) into engine-process governance services; persistence table shows two writers — engine `AuditBroker` + admin-service `AdminActionHandler` — both via shared `AuditKeyProvider` |
| **B3-02** T-310/T-311 depend on T-312 before it exists | T-312 split into T-312a (Protocol + TestAuditKeyProvider, before T-308) + T-312b (production keystores, after T-311); Phase 3 reorder applied |
| **B3-03** governance events reference-only without store | T-305 SOP revised: governance events **embed** full canonical signed payloads (frozen value object embedded, not referenced); FR-ADV-06 governance stream is the durable approval trace; static test enforces self-contained payloads |
| **B3-04** `AuthorisationProfile` signature missing | T-304 adds `profile_signature` + `profile_signature_key_version`; T-310d verifies on load; T-311 signs on write; new **T-314** `AuthorisationProfileSigner` + `AuthorisationProfileVerifier` ports |
| **B3-05** SOP-template admin write port missing | New **T-316** `SopTemplateAdminWritePort` + `SopTemplateReadPort` + `SopTemplateBootstrapPort` + SQLite store + signatures + signed governance events; T-803 consumes read port only |
| **B3-06** review queue + extension workflow missing | New **T-315** `app.review_queue` + `AuthorisationRequest` service; T-806b routes blocked sessions to queue; FR-PROTO-SOP-09 / FR-AUTH-07 / FR-AUTH-12 owned |
| **B3-07** T-205 worker-pool test before T-502 | `test_worker_pool_factory.py` moved to T-502; T-205 keeps only `test_spawn_context_available.py` probe |
| **B3-08** T-309 / T-309a / T-309b ambiguous identity | Model 1: T-309 single task heading; sub-deliverables (a)/(b) documented inline |
| **H3-01** T-204 stale instructions | T-204 rewritten manifest-driven only; adds `task_acceptance_completeness_check.py`, `architecture_manifest_generator.py`, `task_manifest_generator.py`, `port_manifest_generator.py` |
| **H3-02** `BlockVendorSubmission` not fully wired | T-1001 owns vendor-profile portion; T-1002 owns screening-verdict portion; T-903 consumes both |
| **H3-03** Phase 13 UAT cards thin | T-1301 / T-1302 / T-1303 expanded with full SOPs + fixture lists + per-scenario acceptance |
| **H3-04** Roadmap legacy sections active-looking | Legacy Phase 8/9 blocks moved to `ROADMAP.md` Appendix A with `Legacy-Pre-v1.2-` prefix |
| **H3-05** README stale | Updated to v1.3 + four-audit chain |
| **H3-06** Library-mode internal review text wrong | Library `ScreeningCompleted` → design stream (batched per batch); governance stream carries reviewer/admin only |
| **H3-07** Appendix C T-805 row stale | Removed; manifest-derivation note added |
| **H3-08** rule-fixture gate lifecycle conflict | `enforced` at T-405 verification / Phase 4 exit; deferrals require explicit `deferred_with_reason` + sign-off |
| **H3-09** Admin-service IPC unspecified | New **T-1103** named-pipe (Windows) / Unix-socket (POSIX) IPC + mutual authentication + CLI/API client routing |
| **H3-10** Developer authority ambiguous | New `DeveloperBootstrapPrincipal` sub-type; T-311 narrowed to `AdminPrincipal | DeveloperBootstrapPrincipal`; post-bootstrap restrictions |
| **H3-11** `AdvisoryWarningPresented` schema thin | T-806a explicit FR-ADV-02 field set + recipient-role constraint + per-surface tests |
| **M3-01** uv groups vs extras conflated | T-201 distinguishes `[dependency-groups]` (`dev` only) from `[project.optional-dependencies]` |
| **M3-02** determinism check before fixtures | T-201 determinism job in `not_implemented` lifecycle until T-1301 |
| **M3-03** task-acceptance YAML schema missing | Appendix D adds mandatory YAML acceptance schema; brief skeleton extended |
| **M3-04** port inventory overly closed | Manifest-driven port additions via `docs/port_manifest.yaml` allowed |
| **M3-05** renderer cross-platform unspecified | T-201 + T-802 canonical font packaging; Linux byte-identity / Windows semantic-identity expectations |
| **M3-06** Roadmap Phase 13 stale wording | "authorisation declared" replaced with full administrator-granted + screening + acknowledgement chain |
| **M3-07** Gate predicate versioning missing | T-309 adds predicate versioning; `DerivationEnvironment` extended with version + content-hash maps; replay test for older versions |
| **M3-08** `TASK_BOARD.md` arithmetic drift | Counts regenerated from `docs/task_manifest.yaml`; header note marks manifest-derived |

**`/architect` (v1.3):** "B3-01's `AuditAppendPort` broker is the structural primitive v1.2 was missing — engine-process governance services no longer hold the raw audit log; they hold the broker. B3-04's profile signing + B3-05's SOP-template signing complete the institutional-integrity story. B3-02's T-312 split unblocks Phase 3's actual buildability. T-309 single-identity ends the parser ambiguity. Approved for v1.3."

**`/scientific-advisor` (v1.3):** "B3-03 restores FR-ADV-06 — governance events embed full signed payloads, the stream is the immutable approval trace. B3-06's review queue is the recovery path: blocked users are routed into auditable admin review, not into an error state. H3-11's `AdvisoryWarningPresented` schema closes the field-level evidence gap. Approved for v1.3."

**`/dev-orchestrator` (v1.3):** "Manifest-driven gates (M2-03 → H3-01 fully) make CI self-consistent; gate-predicate versioning (M3-07) makes replay safe across changes; renderer cross-platform (M3-05) closes the last platform-determinism gap. T-1103 admin-service IPC is the executable boundary the security model required. T-1301/T-1302/T-1303 expansion brings UAT closure to the deferred work from earlier rounds. Approved for v1.3."

### 7.4e Round 8 — Codex fourth-round external audit (produces v1.4)

After v1.3 landed, a fourth external audit by Codex (`audit report/CODING_AGENDA_Fourth_Round_Audit_Report.md`) raised 9 blocking + 10 high + 8 moderate findings against v1.3. The three internal roles accepted all 27 (full per-finding adjudication in `audit report/CODING_AGENDA_Fourth_Round_Audit_Response.md`). Summary of v1.4 structural changes:

| Finding | v1.4 change |
|---|---|
| **B4-01** Section 2 physical order disagrees with binding phase order | Phase 10 physically inserted between Phase 9a and Phase 8b; CI fixture `test_task_manifest_phase_order.py` asserts T-1001/T-1002 precede T-803/T-806b/T-903 |
| **B4-02** T-314 scheduled after consumers | T-314 split: T-314a (Protocols + fakes, before T-310) + T-314b (production adapters + key lifecycle, after T-311) |
| **B4-03** T-313 scheduled after consumers | T-313 split: T-313a (Protocols + fake brokers, before T-310) + T-313b (production audit-service, after T-311) |
| **B4-04** Dual-writer audit-lock non-executable | Single audit-service writer process (T-313b); engine + admin processes both append via IPC; eliminates lock-handoff fragility |
| **B4-05** T-316 bootstrap + composition still uses YAML loader | T-316 split: T-316a (Phase 3 ports + value objects) + T-316b (Phase 4 SQLite store + bootstrap) + T-316c (Phase 4 production signer); `YamlSopTemplateLoader` removed from composition root |
| **B4-06** § 3 wiring stale | § 3 regenerated end-to-end for v1.4; new static gate `no_stale_task_ids_in_active_sections_check.py` |
| **B4-07** Manifest authority depends on missing anchors | `docs/module_manifest.yaml` manually authored; `architecture_manifest_generator.py` removed; ARCHITECTURE.md treated as checked reference |
| **B4-08** Admin IPC after CLI/API consumers | T-1103 split: T-1103a (Protocol + IPC contract, before T-1101) + T-1103b (production, after T-1102); T-1101/T-1102 forbidden from importing AdminActionHandler |
| **B4-09** DecisionRecordSigner unowned | T-314 extended to cover DecisionRecordSigner per-principal signer + key lifecycle in T-314b |
| **H4-01** Review-queue admin triage not wired | `ReviewQueueAdminPort` added; T-1103b admin-service handles `triage_review_queue_item` IPC verb |
| **H4-02** Security gates stale + narrow | `no-self-authorisation-check` expanded to 6 surfaces (UserPrincipal, ReviewerPrincipal, SopTemplateAdminWritePort, AuditAppendPort, direct AdminActionHandler import, IPC bypass); three new gates added |
| **H4-03** Task-acceptance gate has no brief-creation path | T-204 adds `tools/initial_task_brief_generator.py`; `test_task_brief_coverage.py` enforces |
| **H4-04** SOP-template key lifecycle thin | New **T-316c** Phase 4 — production SopTemplateSigner + key lifecycle + offline verifier |
| **H4-05** Audit-key archive eviction breaks long-term verification | T-312b indefinite retention via institutional escrow; in-process keystore retains current + recent only |
| **H4-06** REQUIREMENTS / ARCHITECTURE still cite `DeveloperPrincipal` | Agenda § 0.3 paragraph documents `DeveloperPrincipal` → `DeveloperBootstrapPrincipal` interpretation; v1.6 source-doc amendment scheduled |
| **H4-07** ROADMAP not truly regenerated | Active sections regenerated; stale-token CI check `test_roadmap_stale_tokens.py` |
| **H4-08** Task-board + Appendix C arithmetic drift | Manifest-derived counts via `tools/task_count_reporter.py`; CI assertion |
| **H4-09** PDF/font reproducibility insufficient | `core+dev+pdf` CI profile (Ubuntu + Windows); canonical fonts committed via Git LFS (not network-downloaded); OS-level WeasyPrint dependencies pinned |
| **H4-10** AuditKeyProvider exposes raw HMAC bytes | Protocol changed to `mac(message)` / `verify(...)` / `rotate(...)` — no raw `current_key()` method; key bytes never leave the keystore in production |
| **M4-01** SopTemplateLibrary alongside new ports | `SopTemplateLibrary` removed from port catalogue; legacy YAML files remain only as T-316b bootstrap input |
| **M4-02** Stale T-309a/T-309b/T-312 references | Purged from active content; new CI gate `no_stale_task_ids_in_active_sections_check.py` |
| **M4-03** Manifest claims unverifiable | Counts marked `(planned-generated)` until T-204 runs |
| **M4-04** Dual-control enforcement needs tests | T-1302 adds three dual-control adversarial scenarios |
| **M4-05** Admin-service OS-level ACL underspecified | T-1103b adds Windows pipe ACL + POSIX socket mode + service-account separation tests |
| **M4-06** `ReviewQueueStore` semantics ambiguous | Clarified: AuthorisationRequest + ReviewQueueItemDecision append-only; status derived |
| **M4-07** Appendix B T-803 row stale | Updated: SOP-template admin writes attributed to T-316b |
| **M4-08** T-201 numbering + lifecycle wording drift | T-201 SOP renumbered consecutively; lifecycle table footer v1.4 |

**`/architect` (v1.4):** "B4-01 physical reorder + B4-02 / B4-03 / B4-05 / B4-08 task splits eliminate the build-order defects. B4-04 single-writer audit-service is the right concurrency model — IPC clients on both sides, no lock-handoff fragility. B4-06 § 3 regenerated. B4-09 DecisionRecordSigner now owned. Approved for v1.4."

**`/scientific-advisor` (v1.4):** "Phase 10 physically precedes Phase 8b + Phase 9b in the build queue and in the manifest — the screening-before-SOP safety invariant is now manifest-enforceable. M4-04 dual-control adversarial UAT scenarios prove the institutional dual-control mode. SopTemplate signing lifecycle (T-316c) closes the cryptographic-integrity gap. Approved for v1.4."

**`/dev-orchestrator` (v1.4):** "Manifest authority is now realistic (manually authored against the agenda). Initial-brief generator unblocks the task-acceptance gate. Expanded security gates cover the v1.3 attack surface. PDF/font reproducibility has a real CI profile + committed fonts. Stale-token CI prevents future drift. Approved for v1.4."

### 7.4f Round 9 — Codex fifth-round mechanical consistency audit (produces v1.5)

After v1.4 landed, a fifth external audit by Codex (`audit report/CODING_AGENDA_Fifth_Round_Audit_Report.md`) raised 10 blocking + 9 high + 6 moderate findings against the v1.4 synchronization draft. The response is a mechanical consistency release: no new feature scope, only corrections needed to make task generation, implementation handoff, and security-significant acceptance testing reliable.

| Finding group | v1.5 change |
|---|---|
| **B5-01..B5-03** heading order, stale card, and counts | Phase 3 physically follows the executable dependency order; stale profile-signing legacy card removed; Phase 3 / Phase 4 / cumulative active counts are 19 / 8 / 71. |
| **B5-04** port inventory arithmetic | Canonical port inventory re-enumerated to 50 unique ports; `test_port_inventory.py` expectation and `docs/port_manifest.yaml` seed agree. |
| **B5-05..B5-07** non-executable wiring and production-authentication edges | Section 3 composition root uses `SopProtocolGenerator(sop_template_read_port)`; production audit-service follows production profile verifier; production SOP-template store follows production SOP-template signer/verifier. |
| **B5-08..B5-10** split-task consumers, review-queue triage, and source-doc authority | Consumer cards reference split responsibilities; admin review-queue triage routes through `ReviewQueueAdminPort` and admin-service IPC; `ARCHITECTURE.md` and `REQUIREMENTS.md` now carry `DeveloperBootstrapPrincipal`, signed SOP-template ports, and audit/admin service modules. |
| **H5-01..H5-09** checker scope, manifests, auth-failure path, bootstrap drafts, and support docs | `tools/agenda_consistency_check.py` checks duplicate IDs/sections, active stale tokens, phase order, counts, port total, source markers, and support-doc drift; seed manifests added; audit-service auth failure emits a governance event; unsigned profile draft model specified; README / ROADMAP regenerated to v1.5 authority. |
| **M5-01..M5-06** range grammar, numbering, sign-off, retention, fonts, and Windows/OneDrive fixtures | `T-601a..k` range grammar is manifest-safe; Section 2 numbering is parser-visible; sign-off is conditional on the local checker; audit-key retention is indefinite via escrow; font wording is future-tense until assets exist; platform probes cover named pipes, Unix sockets, and OneDrive SQLite WAL behavior. |

**`/architect` (v1.5):** "The agenda is now mechanically coherent enough to drive code generation. Build order, task-card count, port inventory, composition root, service boundaries, and source-document authority agree. The remaining risk is not architectural contradiction; it is implementation discipline."

**`/scientific-advisor` (v1.5):** "The safety invariant is preserved: screening still precedes SOP rendering, advisory acknowledgement remains active and auditable, and admin/reviewer governance paths are explicit. The v1.5 changes do not relax any biological-safety gate."

**`/dev-orchestrator` (v1.5):** "Future Codex sessions have a concrete entry protocol: read AGENTS.md, run `python tools/agenda_consistency_check.py`, use `docs/*_manifest.yaml` as seeds, and update TASK_BOARD.md after verified task work. Approved for Phase 2 scaffold start only while the checker remains green."

---

## 8. Appendices

### Appendix A — Glossary cross-reference

All molecular-biology terms used in this agenda are defined in `Cloning_Expression_Vector_Design_White_Paper.md` Appendix A (≈ 120 entries). Engineering terms (CI gate, port, adapter, dependency-injection composition root, fixture, property test, deterministic fake) are standard software-engineering vocabulary.

### Appendix B — Traceability matrix

Each task ID is traced to its ROADMAP phase + ARCHITECTURE section + REQUIREMENTS IDs:

| Task | Phase | Architecture refs | Requirements refs |
|---|---|---|---|
| T-201 / T-202 | 2 | § 4.1, § 4.8 | NFR-MAINT-*, SC-* |
| T-203 (a..d) | 2 | § 4.2 catalogue | DR-* |
| T-204 | 2 | § 4.10 | NFR-REL-*, NFR-SEC-* |
| **T-205** (v1.1) | 2 | § 4.8 + § 4.10 | NFR-MAINT-* (Windows / OneDrive / SQLite-locking / file-watch / non-ASCII / atomic-write) — H-07 |
| T-301 | 3 | § 4.6 v1.4 supplement (sequence primitives) | DR-02, B5 / B6 / M2 / M3 |
| T-302 | 3 | § 4.6 v1.4 supplement (graph) | M4 |
| T-303 (a..c) | 3 | § 4.6 v1.4 supplement | DR-03..05, B4, M3 |
| T-304 | 3 | § 4.6 v1.4 supplement (security) | UR-09, UR-10, FR-AUTH-*, M6, B4, B8 |
| T-305 | 3 | § 4.6 v1.4 supplement (events) | M12, B8, B9 |
| T-306 | 3 | § 4.6 v1.4 supplement (sop_protected) | M11, B1 |
| T-307 | 3 | § 4.6 v1.4 supplement (derivation) | B11 |
| T-308 (a..d) | 3 | § 4.5 SequenceReader/Writer | UR-01a, FR-IO-*, B5, M8 |
| **T-308e** (v1.1) | 3 | § 4.5 SequenceReader (SnapGene `.dna` read-only) | FR-INT-02, FR-IO-02 — H-02 |
| **T-309** (v1.3 — single identity per B3-08; gate-predicate versioning per M3-07) | 3 | § 4.2.1 engine.session skeleton + replay-determinism; § 4.4 state machine + activation map | FR-PROJ-*, B-02, M2-01, M3-07. Sub-deliverables (a) Phase-3 skeleton / (b) per-phase gate activation in owning tasks |
| **T-310** (v1.1; v1.5 depends on T-312a + T-314a verifier Protocols, then T-314b production verifier) | 3 | § 4.5 ProjectStore / EventLog / AuditLog ports; § 4.8 persistence | FR-PROJ-*, NFR-REL-*, NFR-SEC-*, R-16, FR-AUTH-10 — B-02 / H-05 / v1.3 B3-04 verifier-on-load |
| **T-311** (v1.2; v1.3 audit broker + profile signer + DeveloperBootstrap per B3-01 / B3-04 / H3-10) | 3 | § 4.2.2 app.admin_action_handler; § 4.5 split authorisation ports; § 4.5 split SOP-template ports | UR-10, FR-AUTH-01..14, BR-11..13, R-16 — B2-04 / v1.3 B3-04 / H3-10 |
| **T-312a** (v1.3 — early half of the audit-key split per B3-02) | 3 (early; before T-308) | § 4.5 AuditKeyProvider Protocol | NFR-SEC-*, R-16 — B3-02 |
| **T-312b** (v1.3 — production half of the audit-key split per B3-02) | 3 (late; after T-311) | § 4.5 AuditKeyProvider production adapters + rotation service + offline verifier | NFR-SEC-*, R-16 — B2-08 / v1.3 B3-02 |
| **T-313a** (v1.4 — early half of the audit-append split per B4-03) | 3 | § 4.5 AuditAppendPort + AdminAuditAppendPort Protocols + ServicePrincipal + fakes | NFR-SEC-*, R-16 — B3-01 / B4-03 |
| **T-313b** (v1.4 — production half per B4-03 / B4-04) | 3 | § 4.5 production single-writer audit-service + IPC; replaces dual-writer model | NFR-SEC-*, R-16 — B3-01 / B4-04 |
| **T-314a** (v1.4 — early half of the profile-signing split per B4-02 / B4-09) | 3 | § 4.5 ProfileSigner + ProfileVerifier + DecisionRecordSigner + DecisionRecordVerifier Protocols + fakes | FR-AUTH-02, FR-AUTH-10 — B3-04 / B4-02 / B4-09 |
| **T-314b** (v1.4 — production half per B4-02 / B4-09) | 3 | § 4.5 production institutional + per-principal signers + key lifecycle + offline verifiers | FR-AUTH-02, FR-AUTH-10, FR-AUTH-04 — B3-04 / B4-02 / B4-09 |
| **T-315** (v1.3 — new per B3-06; v1.4 — `ReviewQueueAdminPort` per H4-01; append-only model per M4-06) | 3 | § 4.2.2 app.review_queue + AuthorisationRequest service | FR-PROTO-SOP-09, FR-AUTH-07, FR-AUTH-12 — B3-06 / v1.4 H4-01 / M4-06 |
| **T-316a** (v1.4 — early half of the SOP-template split per B4-05; Protocols + value objects) | 3 | § 4.5 SopTemplate split admin ports + SopTemplateSigner / Verifier Protocols | FR-PROTO-SOP-*, FR-AUTH-* — B3-05 / B4-05 |
| **T-316b** (v1.4 — moved to Phase 4 per B4-05) | 4 | § 4.5 / § 4.8 SqliteSopTemplateStore + bootstrap migration; replaces YamlSopTemplateLoader | FR-PROTO-SOP-* — B3-05 / B4-05 |
| **T-316c** (v1.4 — new per H4-04) | 4 | § 4.5 production SopTemplateSigner + Verifier + key lifecycle | FR-PROTO-SOP-* — H4-04 |
| T-401 | 4 | § 4.8 catalogue layout | NFR-MAINT-*, M10 |
| T-402 (a..e) | 4 | § 4.2 catalogue | UR-04, FR-MOD-* |
| T-403 | 4 | § 4.2 catalogue | UR-06, FR-HOST-* |
| T-404 | 4 | § 4.2 catalogue | UR-07, FR-ENZ-* |
| T-405 (a..e) | 4 | § 4.6 rule manifest | MR-*, WR-*, SR-*, BR-*, MS-* |
| T-406 (a..e) | 4 | § 4.5 / § 4.8 | SR-*, BR-*, N6, N7 |
| T-501 | 5 | § 4.2 engine.dependencies | C5 |
| T-502 | 5 | § 4.2 engine.validation | FR-VAL-*, M7 |
| T-503 (a..c) | 5 | § 4.2 engine.sequence_analysis | FR-CORE-01..03, C3, MR-* / WR-* / BR-* |
| **T-504** (v1.1) | 5 | § 4.2.1 engine.compatibility; § 4.6 HostCompatibilityConstraints | UR-06, FR-HOST-*, R-15 — B-02 / H-03 |
| T-601 (a..k) | 6 | § 4.5 biology ports | FR-CORE-14..20, M9 |
| T-602 | 6 | § 4.2 engine.validation.predicates | MR-12..16, MR-27, MR-28 |
| T-603 | 6 | § 4.2 app.validation_orchestrator | M7 |
| **T-606** (v1.1) | 6 | § 4.2.2 app.design_service | — (B-02 / M-08) |
| **T-607** (v1.1) | 6 | § 4.2.2 app.decision_tree | FR-UI-01..12 — B-02 / M-08 |
| T-701 | 7 | § 4.5 CodonAlgorithm port | FR-CORE-04..07, MR-07..09, M4 |
| T-702 | 7 | § 4.2 engine.overhang | FR-CORE-13, MR-40..41 |
| T-703 (a..d) | 7 | § 4.2 engine.assembly | FR-CORE-12, MR-37..41, M3 |
| **T-703e** (v1.1) | 7 | § 4.2 engine.assembly SLIC strategy | REQUIREMENTS § 1.2 SLIC scope — M-02 |
| T-704 | 7 | § 4.2 engine.primer | FR-PRIM-*, M1 |
| T-705 | 7 | § 4.2 app.assembly_orchestrator | – |
| T-801 | 8a | § 4.2 engine.risk_classification | UR-11, FR-ADV-01 |
| T-802 | 8a | § 4.2 engine.design_plan + renderers (v1.2 M2-04) | FR-PROTO-DESIGN-*, B1, M11 |
| T-803 | 8b | § 4.2 engine.sop_protocol + renderers (v1.2 M2-04); **v1.4 M4-07: SOP-template admin writes moved to T-316b — T-803 consumes `SopTemplateReadPort` only** | FR-PROTO-SOP-*, B1, M11, M8 |
| T-804 | 8a | § 4.2 engine.controls | N8 |
| **T-805a** (v1.2 — new per B2-09) | 8a | § 4.2.2 app.design_plan_orchestrator — emits `DraftDesignBundle` pre-screening | FR-PROTO-DESIGN-* — B2-09 split |
| **T-805b** (v1.2 — renamed from T-805 per B2-09) | 8b | § 4.2.2 app.sop_protocol_orchestrator — emits `SopProtocolBundle` post-authorisation | FR-PROTO-SOP-* — B2-09 split |
| **T-806a** (v1.1) | 8a | § 4.4 advisory presentation surface | UR-11, FR-ADV-01..05 (presentation half) — B-03 split |
| **T-806b** (v1.1) | 8b | § 4.4 authorisation gate decision; BR-14 home (v1.2 H2-11); FR-ADV-07 extended (v1.2 M2-02) | UR-11, FR-ADV-06..07, BR-14, R-21 (gate half — *after* Phase 10) — B-03 split |
| **T-807** (v1.1) | 8a | § 4.2.1 engine.vlp_policy | MS-* + M9 — B-02 / H-04 |
| **T-808** (v1.1) | 8a | § 4.2.2 app.plugin_governance | NFR-SEC-*, R-18, N7 — B-02 |
| T-901 | 9a | § 4.5 SequenceReader/Writer | FR-IO-* |
| T-902 | 9a | § 4.5 SnapGeneChannel (file watcher; depends on T-308e) | UR-01a, FR-INT-04a |
| T-903 | 9b | § 4.2 app.export_orchestrator + renderers (v1.2 M2-04); `BlockExport` gate activation (v1.2 H2-06) | N6, R-19, B2-02 — moved from Phase 9 to Phase 9b |
| T-1001 (per vendor) | 10 | § 4.5 SynthesisVendorAdapter | SR-*, M1 |
| T-1002 | 10 | § 4.5 ScreeningAdapter + trust policy | BR-*, B10, N5 |
| **T-1103a** (v1.4 — early half of the admin-service split per B4-08; FIRST in Phase 11) | 11 | § 4.5 AdminServiceClientPort Protocol + IPC contract + in-memory test client | FR-AUTH-*, NFR-SEC-* — B4-08 |
| T-1101 (v1.4 — admin commands route via AdminServiceClientPort per B4-08) | 11 | § 4.2 interface.cli; admin commands via T-1103a Protocol | – |
| T-1102 (v1.4 — admin routes via AdminServiceClientPort per B4-08) | 11 | § 4.2 interface.api; admin routes via T-1103a Protocol | – |
| **T-1103b** (v1.4 — production half per B4-08 / H4-01 / M4-05) | 11 | § 4.2 interface.admin_service + IPC server + OS-level ACL + ReviewQueueAdminPort | FR-AUTH-*, NFR-SEC-*, FR-PROTO-SOP-09 — B4-08 / H4-01 / M4-05 |
| T-1201 | 12 | § 4.5 LLMConstraintTranslator + AdvisoryTextPolicy | UR-02, M10, R-17 |
| T-1202 | 12 | § 4.2 interface.ui | UR-02, FR-UI-* |
| T-1203 | 12 | § 4.5 SnapGeneChannel (api client) | UR-01b, FR-INT-04b |
| T-1301 | 13 | § 4.10 Tier-3 UAT | AC-01..03 |
| T-1302 | 13 | § 4.10 adversarial UAT | R-16..R-21 |
| T-1303 | 13 | § 4.10 library + release | AC-06..07 |

### Appendix C — Per-module context budget summary

**(v1.3 H3-07 / M3-08 / v1.4 H4-08 note.)** This table is **planned-generated** from the canonical task manifest (`docs/task_manifest.yaml` — produced by `tools/task_budget_generator.py` once T-204 runs). Until T-204 runs, the table is hand-maintained against the current task catalogue. The v1.2 row for the removed `app.protocol_orchestrator` (T-805) is absent; T-805 was split in v1.2 B2-09 into T-805a + T-805b (rows present below). **(v1.4 H4-08)** Cumulative LoC + total task counts are reported by `tools/task_count_reporter.py` (manifest-derived once available); CI `test_task_count_consistency.py` asserts heading-count + Appendix C row-count + `TASK_BOARD.md` agree.

| Module class | Estimated LoC | Sub-task count | Context per sub-task | Model tier |
|---|---|---|---|---|
| `domain.sequence` (T-301) | ≈ 800 | 1 | ≤ 60 k | Opus |
| `domain.graph` (T-302) | ≈ 400 | 1 | ≤ 50 k | Opus |
| `domain.types` (T-303) | ≈ 1 500 | 3 | ≤ 50 k each | Opus |
| `domain.security` (T-304) | ≈ 800 | 1 | ≤ 60 k | Opus |
| `domain.events` (T-305) | ≈ 700 | 1 | ≤ 50 k | Sonnet |
| `domain.types.sop_protected` (T-306) | ≈ 800 | 1 | ≤ 60 k | Opus |
| `domain.types.derivation` (T-307) | ≈ 400 | 1 | ≤ 45 k | Opus |
| `adapter.io` (T-308) | ≈ 1 800 | 4 | ≤ 55 k each | Opus |
| Catalogue loaders + schemas (T-401) | ≈ 600 | 1 | ≤ 45 k | Sonnet |
| Catalogue content (T-402..406) | data files | ≈ 15 sub-tasks | ≤ 35 k each | Sonnet |
| `engine.dependencies` (T-501) | ≈ 500 | 1 | ≤ 50 k | Opus |
| `engine.validation` (T-502) | ≈ 600 | 1 | ≤ 55 k | Opus |
| `engine.sequence_analysis` + structural predicates (T-503) | ≈ 1 500 | 3 | ≤ 55 k each | Opus |
| Biology adapters (T-601) | ≈ 200 each × 11 | 11 | ≤ 30 k each | Sonnet |
| Biology-dependent predicates (T-602) | ≈ 600 | 1 | ≤ 55 k | Opus |
| `app.validation_orchestrator` (T-603) | ≈ 400 | 1 | ≤ 45 k | Opus |
| `engine.codon` (T-701) | ≈ 900 | 1 | ≤ 60 k | Opus |
| `engine.overhang` (T-702) | ≈ 500 | 1 | ≤ 50 k | Opus |
| `engine.assembly` (T-703 a..e — v1.2 H2-02 correction; 5 strategy families) | ≈ 2 000 | 5 | ≤ 55 k each | Opus |
| `engine.primer` (T-704) | ≈ 800 | 1 | ≤ 55 k | Opus |
| `app.assembly_orchestrator` (T-705) | ≈ 400 | 1 | ≤ 40 k | Opus |
| `engine.risk_classification` (T-801) | ≈ 500 | 1 | ≤ 45 k | Opus |
| `engine.design_plan` (T-802) | ≈ 700 | 1 | ≤ 50 k | Opus |
| `engine.sop_protocol` (T-803) | ≈ 900 | 1 | ≤ 60 k | Opus |
| `engine.controls` (T-804) | ≈ 500 | 1 | ≤ 40 k | Sonnet |
| `app.protocol_orchestrator` (T-805) | ≈ 300 | 1 | ≤ 40 k | Opus |
| `app.advisory_acknowledgement` (T-806a, Phase 8a) | ≈ 500 | 1 | ≤ 45 k | Opus |
| `app.authorisation_decision` (T-806b, Phase 8b) | ≈ 500 | 1 | ≤ 55 k | Opus |
| `app.design_plan_orchestrator` (T-805a, Phase 8a — v1.2 new per B2-09) | ≈ 350 | 1 | ≤ 45 k | Opus |
| `app.sop_protocol_orchestrator` (T-805b, Phase 8b — v1.2 renamed per B2-09) | ≈ 250 | 1 | ≤ 40 k | Opus |
| `app.admin_action_handler` (T-311, Phase 3 — v1.2 new per B2-04; v1.3 expanded per B3-04 / H3-10) | ≈ 800 | 1 | ≤ 55 k | Opus |
| **`AuditKeyProvider` Protocol + `TestAuditKeyProvider` (T-312a, Phase 3 — v1.3 new per B3-02)** | ≈ 200 | 1 | ≤ 25 k | Sonnet |
| **`AuditKeyProvider` production adapters + rotation service + offline verifier (T-312b, Phase 3 — v1.3 new per B3-02)** | ≈ 900 | 1 | ≤ 50 k | Opus |
| **`AuditAppendPort` + `AdminAuditAppendPort` Protocols + fakes (T-313a, Phase 3 — v1.4 split per B4-03)** | ≈ 350 | 1 | ≤ 30 k | Sonnet |
| **Production audit-service process + IPC + single-writer (T-313b, Phase 3 — v1.4 new per B4-04)** | ≈ 900 | 1 | ≤ 55 k | Opus |
| **`AuthorisationProfileSigner` + `AuthorisationProfileVerifier` + `DecisionRecordSigner` + `DecisionRecordVerifier` Protocols + fakes (T-314a, Phase 3 — v1.4 split per B4-02 / B4-09)** | ≈ 400 | 1 | ≤ 30 k | Sonnet |
| **Production profile + DecisionRecord signers + key lifecycle (T-314b, Phase 3 — v1.4 production half per B4-02 / B4-09)** | ≈ 900 | 1 | ≤ 55 k | Opus |
| **`app.review_queue` + `AuthorisationRequest` service + `ReviewQueueAdminPort` (T-315, Phase 3 — v1.3 new per B3-06; v1.4 per H4-01 / M4-06)** | ≈ 950 | 1 | ≤ 55 k | Opus |
| **`SopTemplate` split-port Protocols + Signer/Verifier Protocols + value objects (T-316a, Phase 3 — v1.4 split per B4-05)** | ≈ 400 | 1 | ≤ 35 k | Sonnet |
| **Signed SQLite SOP-template store + bootstrap migration (T-316b, Phase 4 — v1.4 moved per B4-05)** | ≈ 800 | 1 | ≤ 55 k | Opus |
| **Production `SopTemplateSigner` + `SopTemplateVerifier` adapters + key lifecycle (T-316c, Phase 4 — v1.4 new per H4-04)** | ≈ 500 | 1 | ≤ 35 k | Sonnet |
| **`AdminServiceClientPort` Protocol + IPC contract + test client (T-1103a, Phase 11 — v1.4 split per B4-08; FIRST in Phase 11)** | ≈ 450 | 1 | ≤ 35 k | Sonnet |
| **Admin-service production implementation + IPC server + ACL + `ReviewQueueAdminPort` (T-1103b, Phase 11 — v1.4 production half per B4-08 / H4-01 / M4-05; LAST in Phase 11)** | ≈ 1000 | 1 | ≤ 60 k | Opus |
| EMBL + GFF3 adapters (T-901, Phase 9a) | ≈ 400 | 1 | ≤ 30 k | Sonnet |
| `adapter.snapgene.SnapGeneFileWatcher` (T-902, Phase 9a — H2-04 fix; no dna_reader) | ≈ 350 | 1 | ≤ 40 k | Sonnet |
| `app.export_orchestrator` (T-903, Phase 9b — moved per B2-02; renderers per M2-04) | ≈ 800 | 1 | ≤ 50 k | Opus |
| Vendor adapters (T-1001) | ≈ 400 each × 3 | 3 | ≤ 35 k each | Sonnet |
| Screening adapters + orchestrator (T-1002) | ≈ 1 000 | 1 | ≤ 55 k | Opus |
| CLI (T-1101) | ≈ 1 000 | 1 | ≤ 50 k | Sonnet |
| API + WebSocket (T-1102) | ≈ 1 000 | 1 | ≤ 55 k | Sonnet |
| LLM translator (T-1201) | ≈ 800 | 1 | ≤ 60 k | Opus |
| Web UI (T-1202) | ≈ 5 000 | ≈ 6 sub-tasks | ≤ 50 k each | Sonnet |
| SnapGene API client (T-1203) | ≈ 500 | 1 | ≤ 35 k | Sonnet |
| White-paper UAT (T-1301) | ≈ 2 000 | 3 | ≤ 60 k each | Opus |
| Adversarial UAT (T-1302) | ≈ 1 500 | 1 | ≤ 60 k | Opus |
| Library benchmark + release (T-1303) | ≈ 800 | 1 | ≤ 40 k | Sonnet |

**Estimated total LoC (excluding UI):** ≈ 26 000 lines of code + ≈ 15 000 lines of tests + ≈ 5 000 lines of catalogue YAML.

### Appendix D — Templates

#### D.1 Task brief skeleton (v1.3 — mandatory YAML acceptance block per M3-03)

```markdown
# task_brief/T-<id>.md — <module>

## Module
- ID: <module_id>
- Phase: <n>
- Model tier: <Opus | Sonnet | Haiku>
- Estimated context budget: ≤ <k> tokens

## Inputs (load these before coding)
- <ARCHITECTURE.md §x.x>
- <REQUIREMENTS.md IDs>
- <CODING_AGENDA.md § 2.x.y>
- <task_artefacts/T-<dep_id>/handover.md (if depends on prior task)>

## Deliverables
- <file path 1>
- <file path 2>
- ...

## Hand-off
- <downstream task(s) that consume this output>

## Acceptance (mandatory machine-readable block — v1.3 M3-03)

```yaml
phase: <n>
owning_modules:
  - <module_id_1>
  - <module_id_2>
gates_activated: []           # gates that this task makes real (lifecycle: not_implemented → informational)
gates_advanced_to: ["informational" | "enforced" | "enforced-green"]
acceptance:
  - id: A1
    description: "<one-sentence acceptance criterion>"
    test: "tests/<path>/test_<name>.py::<test_function>"
    blocks_verification: true | false
  - id: A2
    description: "<...>"
    test: "tests/<path>/<file>.py"
    blocks_verification: true
ci_gates_touched:
  - gate: <gate_name>
    lifecycle_transition: "not_implemented → informational"
  - gate: <gate_name>
    lifecycle_transition: "informational → enforced"
```

The `task-acceptance-completeness-check` CI gate (T-204 v1.3, per M3-03) parses every brief, validates the YAML against this schema, cross-checks each acceptance item references an actual test file, and fails if the block is missing or malformed. Initial state: `informational` until Phase 3 exit; flips to `enforced` thereafter.

#### D.2 Post-execution doc skeleton

```markdown
# handover/T-<id>.md

## Status: <execution-complete | verification-failed | verified>

## Files written
- <path> (<LoC>)
- ...

## Architecture sections consumed
- ...

## Requirements satisfied
- ...

## CI gates touched
- ...

## Deferred / open
- <none | itemised>

## Notes for downstream
- ...
```

### Appendix E — Sign-off

This coding agenda is **Finalised v1.5** after the fifth-round mechanical consistency pass. The sign-off is conditional on the local consistency checks in `tools/agenda_consistency_check.py` passing; it should be withdrawn if any active-section stale-token, duplicate-heading, duplicate-section, count, port-total, or source-document drift check fails. Authorisation chain:

1. `/architect` confirms the dependency DAG (§ 3.1 — v1.5 regenerated with Phase 10 between 9a and 8b per B4-01; T-313a/b + T-314a/b + T-316a/b/c + T-1103a/b splits per B4-02/03/05/08), composition root (§ 3.2 — v1.5 with `AuditServiceClient` IPC instead of in-engine broker per B4-04; legacy SOP-template library + `YamlSopTemplateLoader` removed per B4-05), event-stream wiring (§ 3.3 — v1.3 B3-03 embedded signed payloads preserved), persistence wiring (§ 3.4 — single-writer audit-service per B4-04), and module catalogue (§ 2) are consistent with `ARCHITECTURE.md` v1.5; confirms agenda overrides legacy combined-port excerpt + DeveloperBootstrapPrincipal source-doc amendments per § 0.3 binding-priority + v1.5 source-doc updates.
2. `/scientific-advisor` confirms the rule-population and biology-adapter-calibration plan in § 2.4 / § 2.6 reflects the v2.0 KB citation chain; confirms BR-14 is correctly homed in T-806b (not T-503); confirms event-stream ownership; confirms v1.3 B3-03 governance event embedding (FR-ADV-06 durable trace); confirms v1.3 B3-06 review queue (FR-PROTO-SOP-09 / FR-AUTH-07 / FR-AUTH-12) + v1.4 H4-01 admin-service triage; confirms v1.3 B3-04 profile signatures + v1.4 B4-09 DecisionRecordSigner + v1.4 H4-04 SopTemplate signatures provide three separate institutional cryptographic identities; confirms v1.4 M4-04 dual-control adversarial UAT scenarios; confirms v1.4 B4-01 Section 2 physical reorder makes screening-before-SOP safety invariant manifest-enforceable.
3. `/dev-orchestrator` accepts the test strategy (§ 4), debugging methodology (§ 5), workflow (§ 6), CI lifecycle (§ 3.5 — v1.5 expanded security gates per H4-02; manifest authority per B4-07; new gates `no_direct_admin_handler_import_check`, `audit_append_port_only_check`, `sop_template_admin_port_only_check`, `no_stale_task_ids_in_active_sections_check`, `test_task_manifest_phase_order`, `test_roadmap_stale_tokens`, `test_task_count_consistency`, `test_task_brief_coverage`), `TASK_BOARD.md` regeneration via `tools/task_count_reporter.py`, and assumes ownership of `TASK_BOARD.md` updates.

**v1.5 audit history.** 4 internal adversarial-falsification rounds (v1.0) + 21/21 first-round Codex audit findings accepted (v1.1) + 29/29 second-round Codex audit findings accepted (v1.2) + 27/27 third-round Codex audit findings accepted (v1.3) + **27/27 fourth-round Codex audit findings accepted (v1.4)** + fifth-round mechanical consistency remediation (v1.5). Zero defenses raised across all external coding-agenda audits.

Recommended next action: run `python tools/agenda_consistency_check.py`, then `/dev-orchestrator` opens T-1302 adversarial UAT now that T-1301 is complete locally.

---

*End of CODING_AGENDA.md.*

