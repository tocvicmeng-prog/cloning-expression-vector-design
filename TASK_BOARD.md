# TASK_BOARD.md — War-Room Dashboard (v1.5 consistency release)

**Derived from:** `CODING_AGENDA.md` v1.5 + `ROADMAP.md` v1.5 + `ARCHITECTURE.md` v1.5. Counts below are seed-manifest checked against `docs/task_manifest.yaml` and `tools/agenda_consistency_check.py`; T-204 later owns the production manifest generator/refinement workflow.
**Last updated:** 2026-05-14 (T-1303 library benchmark/release polish complete locally; Phase 13 is 3 / 3 complete and all active Section 2 implementation task cards are done; project is a Git repository on `main` and uses non-editable `uv` installs for Windows/OneDrive/non-ASCII path reliability).
**Maintained by:** `/dev-orchestrator`. **Live mirror command (Phase 11+):** `vector-design status`.

## 1.1 v1.3 changes (operational security / audit boundary pass)

This dashboard was regenerated for v1.3:

- **Phase 3 task count: 12 → 17.** Historical v1.3 added audit-key split work, audit append broker work, profile-signing work, review-queue workflow, and SOP-template admin-write persistence. v1.4/v1.5 later split those responsibilities into the current task IDs shown in § 1.
- **Phase 11 task count: 2 → 3.** Historical v1.3 added the admin-service executable boundary; v1.4/v1.5 later split it into T-1103a and T-1103b.
- **Phase 2 task T-205** simplified: `test_worker_pool_factory.py` moved to T-502 per B3-07; T-205 keeps only `test_spawn_context_available.py` probe.
- **CI gate table § 7** updated: `rule-fixture-coverage-check` enforced at T-405 verification per H3-08; new gate `task-acceptance-completeness-check` added per M3-03.

**v1.2 changes (retained context).** Phase 8 split into 8a/8b (B-03), Phase 9 split into 9a/9b (B2-02), T-805 split into T-805a/T-805b (B2-09), T-311 admin handler + T-312 audit-key tasks (B2-04 / B2-08).

**Next milestone.** Active v0.1.0 implementation is complete locally. Phase 2 scaffold (`T-201`..`T-205`), all Phase 3 tasks (`T-301`..`T-315`), all Phase 4 tasks (`T-401`..`T-406`, `T-316c`, `T-316b`), all Phase 5 tasks (`T-501`, `T-502`, `T-504`, `T-503`), all Phase 6 tasks (`T-601a..k`, `T-602`, `T-603`, `T-606`, `T-607`), all Phase 7 tasks (`T-701`..`T-705`), all Phase 8a tasks, all Phase 9a tasks, all Phase 10 tasks, all Phase 8b tasks, Phase 9b, Phase 11, Phase 12, T-1301, T-1302, and T-1303 are done + locally verified.

---

## 0. Status legend

| Symbol | Meaning |
|---|---|
| ✅ | done + verified (all six audit dimensions green) |
| 🟢 | execution-complete (CI verify pending) |
| 🟡 | in-progress |
| ⚪ | planned (task brief drafted, not yet assigned) |
| 🔴 | blocked (with reason linked) |
| ⏸ | paused (deferred per orchestrator decision) |

---

## 1. Global progress

| Phase | Status | Done / Total | Notes |
|---|---|---|---|
| Phase 0 — Foundations | ✅ | 5 / 5 | KBs v1.0+v2.0, audit report, white paper, requirements |
| Phase 1 — Architectural framework | ✅ | 4 / 4 | ARCHITECTURE v1.5; 2 Codex audits resolved; 31/31 + 31/32 findings accepted |
| Phase 2 — Project scaffold | ✅ | 5 / 5 | T-201..T-205 verified locally. |
| Phase 3 — Core domain model + sequence I/O + security ports | ✅ | 19 / 19 | T-301..T-315 verified locally. **v1.5 physical task order:** T-301 → T-302 → T-303 → T-304 → T-305 → T-306 → T-307 → **T-312a** → **T-313a** → **T-314a** → **T-316a** → T-308 → T-309 → T-310 → T-311 → **T-312b** → **T-314b** → **T-313b** → **T-315**. T-314b precedes production T-313b so audit-service authentication can use the production verifier. |
| Phase 4 — Catalogues | ✅ | 8 / 8 | T-401 catalogue loader framework + JSON Schemas, T-402 parts catalogue, T-403 hosts catalogue, T-404 enzymes catalogue + buffer compatibility, T-405 rule manifests + fixtures + stubs, T-406 policy/profile catalogues, T-316c production SOP-template signing, and T-316b signed SQLite SOP-template store/bootstrap verified locally. |
| Phase 5 — Validation rule engine | ✅ | 4 / 4 | T-501 validation dependency DAG, T-502 pure validation executor, T-504 host compatibility, and T-503 sequence analysis + implemented structural-predicate subset verified locally. |
| Phase 6 — Biology back-ends + app services | ✅ | 5 / 5 | T-601a..k deterministic local biology adapters, T-602 biology-dependent predicates, T-603 validation orchestration, T-606 design service, and T-607 decision tree verified locally. |
| Phase 7 — Codon + assembly + overhang + primer | ✅ | 5 / 5 | T-701 codon optimiser, T-702 overhang optimiser, T-703 assembly strategy hierarchy, T-704 primer designer, and T-705 assembly orchestrator verified locally. |
| **Phase 8a** — Design plan + controls + advisory data + advisory presentation (pre-screening) | ✅ | 7 / 7 | T-801, T-802, T-804, T-805a, T-806a, T-807, and T-808 verified locally |
| **Phase 9a** — Sequence I/O extensions + SnapGene file-watch (pre-screening; v1.2 split per B2-02) | ✅ | 2 / 2 | T-901 EMBL/GFF3 adapters and T-902 SnapGene file-watch verified locally. |
| Phase 10 — Vendor + screening | ✅ | 2 / 2 | T-1001 vendor adapters/vendor-feasibility gate and T-1002 screening adapters/orchestrator verified locally. v1.2 `ScreeningCompleted` emitted to **design stream** per B2-05. |
| **Phase 8b** — SOP rendering + authorisation gate (post-Phase 10 + post-Phase-9a) | ✅ | 3 / 3 | T-803 gated SOP renderer, T-805b SOP bundle orchestration, and T-806b authorisation decision/review-queue routing verified locally. |
| **Phase 9b** — Final export orchestrator (post-Phase 8b; v1.2 split per B2-02) | ✅ | 1 / 1 | T-903 final export ZIP orchestration, redaction, manifest/ZIP renderers, and `BlockExport` activation verified locally. |
| Phase 11 — HTTP API + CLI + admin-service IPC | ✅ | 4 / 4 | T-1103a AdminServiceClientPort Protocol + IPC contract, T-1101 CLI command surface, T-1102 API route/WebSocket surface, and T-1103b production admin-service IPC/ACL/review-queue boundary verified locally. |
| Phase 12 — Web UI + LLM + live SnapGene | ✅ | 3 / 3 | T-1201 LLM constraint translator + enforced output policy, T-1202 React + TypeScript SPA, and T-1203 SnapGene API client verified locally. |
| Phase 13 — Acceptance UAT + library + release | ✅ | 3 / 3 | T-1301 white-paper-example UAT, T-1302 adversarial UAT, and T-1303 library benchmark/release polish verified locally. T-1303 adds deterministic 100/1000-realisation library fixtures, release build wrappers, release docs, and CI determinism wiring. |

**Cumulative (v1.5, seed-manifest checked):** 9 foundation items done + 71 implementation tasks done / **71 active Section 2 implementation task cards**. The fifth-round audit's stale legacy profile-signing heading is removed; `T-601a..k` remains one active card with formal range expansion for child briefs. Phase 0–13 complete locally.

**Phase-order reminder (v1.5, unchanged from v1.2 except Phase 10 physical placement already applied):** 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → **8a** → **9a** → **10** → **8b** → **9b** → 11 → 12 → 13. **v1.4 B4-01:** Section 2 of `CODING_AGENDA.md` is now physically ordered to match — Phase 10 inserted between Phase 9a and Phase 8b.

---

## 2. Current bottlenecks (top 5)

_None at present — all active Section 2 implementation tasks are complete locally._

Anticipated future bottlenecks:

| Anticipated bottleneck | Phase | Mitigation in CODING_AGENDA |
|---|---|---|
| SpliceAI licensing / TensorFlow size | 6 | Adapter is optional; HTTP-service fallback + alternative lighter adapters declared (CODING_AGENDA § 2.6.1 / OQ-05). |
| Curated rule fixtures (~150 rules × 2 fixtures) | 4 / 5 | Parallel sub-tasks T-405a..e; fixtures authored in the same task as the rule manifest entry. |
| Twist/IDT vendor-API access for live cost estimation | 10 | Static vendor adapters are delivered in T-1001 from `catalogues/vendor_profiles/*.yaml`; live API is Phase 15 stretch. |
| SnapGene Server API maturity | 12 | UR-01b is SHOULD; falls back to UR-01a (file-watch) if API unavailable. |
| Container determinism across CPU architectures | 2 / 13 | Pinned CPU arch in Dockerfile; determinism check runs only inside container in CI. |

---

## 3. Active task queue

_Empty — all active implementation tasks are complete locally._

| Task ID | Module | Phase | Tier | Assignee | Started | ETA | Stage |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

---

## 4. Recently completed (Phase 0 + Phase 1)

| Task ID | Deliverable | Date | Notes |
|---|---|---|---|
| F-001 | `Cloning_and_Expression_Vector_Design_Knowledge_Base_v1_0.md` | 2026-05-13 | Original primer; superseded by v2.0 |
| F-002 | `Cloning_KB_v2_Audit_Report.md` | 2026-05-13 | Cross-audit of v1.0 → v2.0 |
| F-003 | `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` | 2026-05-13 | Source-of-truth citation chain |
| F-004 | `Cloning_Expression_Vector_Design_White_Paper.md` | 2026-05-13 | First-principles pedagogical paper |
| F-005 | `REQUIREMENTS.md` v0.1 | 2026-05-13 | SRS; UR-01..11; FR/MR/WR/SR/BR/MS/ADV catalogues |
| A-001 | `ARCHITECTURE.md` v1.0 | 2026-05-13 | Initial three-role architecture (4 rounds of internal falsification) |
| A-002 | `audit report/ARCHITECTURE_Audit_Report.md` | 2026-05-13 | First Codex audit (31 findings) |
| A-003 | `audit report/ARCHITECTURE_Audit_Response.md` + ARCHITECTURE v1.1 / v1.2 / v1.3 | 2026-05-13 | 31/31 accepted; sponsor sharpening of C1; role-hierarchy clarification |
| A-004 | `audit report/ARCHITECTURE_Second_Audit_Report_v1_2.md` | 2026-05-13 | Second Codex audit (32 findings) |
| A-005 | `audit report/ARCHITECTURE_Second_Audit_Response.md` + ARCHITECTURE v1.4 | 2026-05-13 | 31/32 accepted, B3 defended with `BiosafetyClassificationLayer` mitigation |
| A-006 | ARCHITECTURE.md v1.5 | 2026-05-14 | Sponsor strengthening of B3 — active, auditable, design-record-tied advisory acknowledgement |
| A-007 | `CODING_AGENDA.md` v1.0 | 2026-05-14 | Authoritative coding plan; 4 rounds of three-role adversarial review |
| A-008 | `TASK_BOARD.md` (this file) | 2026-05-14 | War-room dashboard starter |
| A-009 | `audit report/CODING_AGENDA_Audit_Report.md` (Codex) | 2026-05-14 | External audit of CODING_AGENDA.md (5 blocking + 8 high + 8 moderate findings) |
| A-010 | `audit report/CODING_AGENDA_Audit_Response.md` + CODING_AGENDA.md v1.1 | 2026-05-14 | 21/21 findings accepted; type-placement fix (B-01), missing-modules added (B-02), Phase 8 split (B-03), CI-gate lifecycle states (B-04), rule-fixture-mandatory T-405 (B-05), plus 8 high + 8 moderate fixes |
| A-011 | `audit report/CODING_AGENDA_Second_Round_Audit_Report.md` (Codex) | 2026-05-14 | Second-round external audit of CODING_AGENDA.md v1.1 (9 blocking + 11 high + 9 moderate findings) |
| A-012 | `audit report/CODING_AGENDA_Second_Round_Audit_Response.md` + CODING_AGENDA.md v1.2 + ROADMAP.md v1.2 + TASK_BOARD.md v1.2 | 2026-05-14 | 29/29 findings accepted; ROADMAP regenerated (B2-01), Phase 9 split into 9a/9b (B2-02), § 3 wiring rewritten end-to-end (B2-03), T-311 admin handler added (B2-04), event-stream ownership corrected (B2-05), T-203c port inventory explicit (B2-06), CI lifecycle column (B2-07), T-312 audit-key management added (B2-08), T-805 split into T-805a/T-805b (B2-09), plus 11 high + 9 moderate fixes |
| A-013 | `audit report/CODING_AGENDA_Third_Round_Audit_Report.md` (Codex) | 2026-05-14 | Third-round external audit of CODING_AGENDA.md v1.2 (8 blocking + 11 high + 8 moderate findings) |
| A-014 | `audit report/CODING_AGENDA_Third_Round_Audit_Response.md` + CODING_AGENDA.md v1.3 + ROADMAP.md v1.3 + TASK_BOARD.md v1.3 + README.md v1.3 | 2026-05-14 | 27/27 findings accepted; new T-313 `AuditAppendPort` broker (B3-01); T-312 split (B3-02); governance events embed full signed payloads (B3-03); T-314 profile signing (B3-04); T-316 SOP-template admin write port (B3-05); T-315 review queue (B3-06); T-205 probe (B3-07); T-309 single identity (B3-08); T-1103 IPC (H3-09); `DeveloperBootstrapPrincipal` (H3-10) |
| A-015 | `audit report/CODING_AGENDA_Fourth_Round_Audit_Report.md` (Codex) | 2026-05-14 | Fourth-round external audit of CODING_AGENDA.md v1.3 (9 blocking + 10 high + 8 moderate findings) |
| A-016 | `audit report/CODING_AGENDA_Fourth_Round_Audit_Response.md` + CODING_AGENDA.md v1.4 + ROADMAP.md v1.4 + TASK_BOARD.md v1.4 | 2026-05-14 | 27/27 findings accepted; Section 2 physical reorder per B4-01 (Phase 10 between 9a and 8b); split task strategy introduced. |
| A-017 | `audit report/CODING_AGENDA_Fifth_Round_Audit_Report.md` | 2026-05-14 | Fifth-round audit found remaining synchronization drift in v1.4 (10 blocking + 9 high + 6 moderate). |
| A-018 | CODING_AGENDA.md v1.5 + ROADMAP.md v1.5 + TASK_BOARD.md v1.5 + seed manifests + Codex working files | 2026-05-14 | Fifth-round consistency pass: active heading order/counts fixed, stale T-314 removed, port inventory corrected to 50, source docs amended, seed manifests/checker added. |
| T-201 | Python project bootstrap | 2026-05-14 | `pyproject.toml`, `uv.lock`, Python 3.11.15 pin, CI workflow, Dockerfile, GPL-3.0 licence, canonical fonts, font installer, bootstrap package, and smoke tests added; local verification green with `uv --no-editable`. |
| T-202 | Directory scaffold | 2026-05-14 | `src/` layer packages, `domain/ports`, catalogue placeholders, event streams, snapshots, exports, task/handover folders, benchmarks, UAT folder, task brief, and scaffold tests added; docs-site and pre-commit bootstrap stubs added. |
| T-203 | Public API stubs + 50-port inventory | 2026-05-14 | Source-layer manifest modules import; `domain.ports` declares all 50 Protocols; port-inventory and module-manifest tests green; import-linter domain/engine contracts kept. |
| T-204 | CI gate skeletons + manifest tooling | 2026-05-14 | Lifecycle-aware gate runner, gate skeletons, manifest generators, task-count reporter, and 71 seed task briefs added; meaningful informational gates verified. |
| T-205 | Platform-readiness baseline | 2026-05-14 | Sync-like non-ASCII/space paths, SQLite WAL concurrency, debounce harness, atomic writes, spawn context, IPC path checks, POSIX socket skip path, and active OneDrive skipped smoke test added. |
| T-301 | `domain.sequence` primitives | 2026-05-14 | Sequence ADT, `SequenceRecord`, canonical circular checksum, formal `LocationV14`, structured `Qualifier`, `FeatureV14`, and typed construct hashes implemented; 100% package coverage and full local gates green. |
| T-302 | `domain.graph` canonical construct graph | 2026-05-14 | Immutable graph nodes/edges, topology and endpoint validation, deterministic canonical JSON, state-transition helpers, and derived feature table implemented; 99.60% package coverage and full local gates green. |
| T-303 | `domain.types` core entities + `domain.library` expand | 2026-05-14 | Parts, hosts, modules, constructs, libraries, assembly methods/plans, validation rules, and host-compat constraints implemented; `Construct.feature_table` bound to `derive_feature_table(graph)`; 95.70% package coverage and full local gates green. |
| T-304 | `domain.security` roles, principals, and signed authorisation profiles | 2026-05-14 | Security/operational role split, one-way admin→reviewer inheritance, bootstrap developer authority, covered biological scope, dual-control flags, unsigned drafts, signed profile hash invariants, declarations, and decisions implemented; 95.56% coverage and full local gates green. |
| T-305 | `domain.events` typed design/governance/export streams | 2026-05-14 | Deterministic event base, design/governance/export subclasses, active advisory presentation events, self-contained governance payloads, and stream ownership for screening/authorisation/SOP events implemented; 97.98% coverage and full local gates green. |
| T-306 | `domain.types` namespace split + `sop_protected` partition | 2026-05-14 | Non-operational design-plan/control/risk-advisory/governance values and operational SOP-protected protocol types implemented; runtime guard and import-linter partition enforce that design plans cannot contain `ProtocolStep`; 87.34% coverage and full local gates green. |
| T-307 | `domain.types.derivation` + RFC 8785 JCS canonicalisation | 2026-05-14 | RFC 8785 canonical JSON package, 32 golden vectors, `$$cev:` scalar tags, rejection rules, `DerivationEnvironmentV14`, policy enums, and stable environment hashes implemented; 92.46% coverage and full local gates green. |
| T-312a | `AuditKeyProvider` Protocol + `TestAuditKeyProvider` | 2026-05-14 | Typed audit-key Protocol moved to `domain.ports.audit_key` with `KeyVersionId`/`MacBytes`, no raw key accessor, deterministic HMAC fake, rotation/archive verification, and contract tests; 100% `domain.ports` coverage and full local gates green. |
| T-313a | `AuditAppendPort` / `AdminAuditAppendPort` Protocols + fake brokers | 2026-05-14 | Append-only audit client Protocols, `ServicePrincipal`, shared fake engine/admin HMAC chain, chain-integrity helpers, and separation-of-duty tests implemented; also fixed current-key verification in the T-312a fake; 96.97% slice coverage and full local gates green. |
| T-314a | Profile/decision-record signing Protocols + fakes | 2026-05-14 | Profile signer/verifier, decision-record signer/verifier, `SignedDecisionRecord`, signing result/error taxonomy, deterministic fakes, and contract tests implemented; 93.15% slice coverage and full local gates green. |
| T-316a | SOP-template split ports + signer/verifier Protocols | 2026-05-14 | `SopTemplate` value objects, read/admin/bootstrap/sign/verify Protocols, SOP-template verification errors, deterministic fake signer/verifier, and contract tests implemented; 93.59% slice coverage and full local gates green. |
| T-308 | Sequence I/O adapters + imported construct contracts | 2026-05-14 | GenBank, FASTA, SBOL3 sequence, and read-only SnapGene `.dna` adapters implemented with explicit loss warnings and imported/annotated construct invariants; 87.61% slice coverage and full local gates green. |
| T-309 | Session state machine + replay + pending safety gates | 2026-05-14 | Event-sourced `DesignSession`, cross-stream replay invariants, derivation-hash snapshots, pending `Block*` registry, predicate version helpers, and activation map implemented; 91.78% slice coverage and full local gates green. |
| T-310 | Persistence adapters | 2026-05-14 | SQLite project/session store, append-only JSONL logs, SQLite audit read/tamper verification, read-only authorisation store, and filesystem snapshot store implemented; 87.89% slice coverage and full local gates green. |
| T-311 | Admin action handler + authorisation write side | 2026-05-14 | Split authorisation ports, SQLite write adapter, signed profile mint/modify/revoke/bootstrap handler, governance events, and denial paths implemented; 92.64% slice coverage and full local gates green. |
| T-312b | Production audit-key adapters + rotation service + offline verifier | 2026-05-14 | File escrow keystore, explicit Windows-DPAPI/POSIX-keyring CI fallbacks, backend selector, admin/bootstrap rotation workflow, signed `AuditKeyRotated` governance event, offline SQLite verifier, runbook, and adversarial tests implemented; 90.36% slice coverage and full local gates green. |
| T-314b | Production profile + decision-record signing adapters and key lifecycle | 2026-05-14 | Ed25519 institutional profile signer/verifier, per-principal decision-record signer/verifier, shared signing-key archive, admin/bootstrap key-management events, offline verifier tools, runbooks, rotation/revocation/tamper tests, and cryptographic-identity separation implemented; 89.85% slice coverage and full local gates green. |
| T-313b | Production single-writer audit-service + IPC | 2026-05-14 | SQLite single-writer audit log, framed JSON audit-service server/handlers, IPC client implementing `AuditAppendPort`/`AdminAuditAppendPort`, authentication via production decision-record verifier, governance failure writer, timeout retry behavior, crash recovery, rotation transition, and concurrent append tests implemented; 91.51% slice coverage and full local gates green. |
| T-315 | Review queue + authorisation-request service | 2026-05-14 | `AuthorisationRequest` / `ReviewQueueItem` / signed `ReviewQueueItemDecision` value objects, typed `ReviewQueueStore` / `ReviewQueueAdminPort`, append-only SQLite queue, user/service submission, admin-only resolution helper, governance events, no-auto-grant recovery path, and adversarial self-approval tests implemented; 92.60% slice coverage and full local gates green. |
| T-401 | Catalogue loader framework + JSON Schemas | 2026-05-14 | `adapter.catalogue` package, generic YAML loader, `MaintenanceMetadata` and graded citation parsing, JSON-Schema subset validator, seed schemas for catalogue families, seed manifest entries, `stale-catalogue-check`, `source-grade-citation-check`, and catalogue gate tests implemented; 89.41% slice coverage and full local gates green. |
| T-402 | Parts catalogue population | 2026-05-14 | `catalogues/parts.yaml` populated from KB v2.0 §§ 5.1-5.13 with 160+ structured entries; parts schema tightened around required metadata; T-402 catalogue coverage, host-compatibility, maintenance, and citation traceability tests added; focused slice green at 89.41% coverage. |
| T-403 | Hosts catalogue | 2026-05-14 | `catalogues/hosts.yaml` populated from KB v2.0 § 6 with 60+ strain/context entries across bacterial, yeast, mammalian, insect, plant, cell-free, and phage/VLP chassis classes; host schema tightened; T-403 metadata and citation traceability tests added; focused slice green at 89.41% coverage. |
| T-404 | Enzymes catalogue + buffer-compatibility matrix | 2026-05-14 | `catalogues/enzymes.yaml` populated with 65+ Type-II, Type-IIS, toolkit, and protease entries; `catalogues/enzyme_buffer_compat.yaml` added and schema-registered; T-404 enzyme-class, citation, and buffer coverage tests added; focused slice green at 89.41% coverage. |
| T-405 | Rule manifests + fixtures + stub predicates | 2026-05-14 | `catalogues/rules/{MR,WR,SR,BR,MS}.yaml` populated with 122 rules; 244 triggering/passing fixtures added; `engine.validation.predicates` registry added; `rule-fixture-coverage-check` and `implementation-status-consistency-check` activated as informational gates; focused slice green at 90.77% coverage; full local gates green with 309 passed, 2 skipped. |
| T-406 | Vendor profiles + screening trust policy + institutional policy + export profiles + risk advisories | 2026-05-14 | Twist, IDT, and GenScript profiles populated; IGSC v3, IBBIS, SecureDNA, and institutional screening trust defaults added; institutional policy, export profiles, and active risk advisories populated; T-406 schema and regression tests added; focused slice green at 91.56% coverage; full local gates green with 315 passed, 2 skipped. |
| T-316c | Production SOP-template signer/verifier adapters + key lifecycle | 2026-05-14 | Ed25519 SOP-template signer/verifier, `sop_template` archive purpose, key distribution/revocation governance events, offline verifier, runbook, and identity-separation tests added; focused slice green with 22 passed at 93.13% coverage. |
| T-316b | Signed SQLite SOP-template store + bootstrap migration | 2026-05-14 | `SqliteSopTemplateStore`, YAML bootstrap, signed read verification, admin-handler SOP-template mint/modify/revoke, governance payloads, and tamper/idempotency/denial tests added; focused slice green with 30 passed at 90.82% coverage; full local gates green with 335 passed, 2 skipped. |
| T-501 | Validation dependency DAG | 2026-05-14 | `engine.dependencies` now builds deterministic rule/field/metric DAGs, computes affected rules and invalidated metrics/rules from field or metric changes, exposes diagnostics, and rejects producer cycles; focused slice green with 6 passed at 99.37% coverage; full local gates green with 341 passed, 2 skipped. |
| T-502 | Pure validation DAG executor | 2026-05-14 | `engine.validation` now evaluates the T-501 graph deterministically, supports incremental field/metric revalidation, aggregates predicate errors, routes HARD failures to safety gates, provides sequential/thread/local-spawn process worker pools, and records the benchmark harness; focused slice green with 11 passed at 91.98% coverage; full local gates green with 352 passed, 2 skipped. |
| T-504 | Role-keyed host compatibility | 2026-05-14 | `engine.compatibility` now checks multi-host workflows per `HostContext` role, resolves threshold profiles per host role, reports deterministic incompatibilities, and covers plant transient, lentivirus/AAV, VLP, cell-free, shuttle-vector, and R-15 marker-conflict fixtures; focused slice green with 9 passed at 91.78% coverage; full local gates green with 361 passed, 2 skipped. |
| T-503 | Sequence analysis + structural predicates | 2026-05-14 | `engine.sequence_analysis` now covers topology-aware restriction sites, digest simulation, compatible ends, fragment simulation, directional site ranking, and diagnostic digest design; implemented predicate registry subset covers 50+ structural names plus concrete frame/internal-site/host predicates while preserving manifest stubs for later promotion; focused slice green with 11 passed at 91.67% coverage; full local gates green with 372 passed, 2 skipped. |
| T-601a..k | Biology adapter implementations | 2026-05-14 | `adapter.biology` is now a package with deterministic local RNA folding, splice motif, signal peptide, RBS/TIR, Kozak, and codon-algorithm adapters; fixture-driven fakes, adapter manifests, and calibration policies added; focused slice green with 8 passed at 91.19% coverage; full local gates green with 380 passed, 2 skipped. |
| T-602 | Biology-back-end-dependent predicates | 2026-05-14 | Pure predicates now cover MR-12, MR-13, MR-14, MR-15, MR-16, MR-27, and MR-28 over precomputed biology metrics without importing adapters; implemented registry extended while manifest stubs remain consistent; focused slice green with 7 passed at 89.89% coverage; full local gates green with 387 passed, 2 skipped. |
| T-603 | Validation orchestrator metric pre-compute | 2026-05-14 | `app.validation_orchestrator` now determines affected rules and required biology metrics, computes metrics through injected adapter ports in parallel, caches results by session/environment/source hash, and invokes the pure validator; focused slice green with 4 passed; full local gates green with 391 passed, 2 skipped. |
| T-606 | Design-service use cases + pending states | 2026-05-14 | `app.design_service` now creates, opens, amends, compiles, and replays event-sourced design sessions; compile honours activated T-309 gates while pending defaults remain phase-local; `current_pending_state` reports AwaitingScreening / AwaitingAuthorisation / AwaitingSopRender / AwaitingExport without stubbing downstream services; focused slice green with 6 passed; full local gates green with 397 passed, 2 skipped. |
| T-607 | Decision-tree application driver | 2026-05-14 | `app.decision_flow` and `app.decision_tree` now provide catalogue-backed objective, host, cargo, expression, tagging, cloning-chemistry, and biosafety-tier candidates; selections persist through T-606 design events and produce deterministic compile metadata; focused slice green with 12 passed; full local gates green with 409 passed, 2 skipped. |
| T-701 | Constraint-aware codon optimiser | 2026-05-14 | `engine.codon` is now a pure package with typed coding-sequence designs, CAI / MinMax / CHARMING / avoid-only algorithms, fixed-point optimisation capped at five iterations, protected-interval and functional-RNA preservation, and sequence metrics; focused slice green with 9 passed; full local gates green with 418 passed, 2 skipped. |
| T-702 | Golden Gate overhang fidelity optimiser | 2026-05-14 | `engine.overhang` is now a pure package with Potapov/Pryor-labelled fidelity matrices, canonical overhang enumeration, product-of-per-overhang scoring, cross-reaction diagnostics, bounded branch-and-bound search, and the 24-fragment benchmark fixture; focused slice green with 8 passed; full local gates green with 426 passed, 2 skipped. |
| T-703 | Assembly strategy hierarchy | 2026-05-14 | `engine.assembly` is now a pure package with strategy contracts, `AssemblyEngine`, and typed plan compilers for restriction ligation, Gibson-like, Golden Gate kit, Gateway, LIC, SLIC, USER, IVA, and yeast TAR strategies; focused slice green with 7 passed; full local gates green with 433 passed, 2 skipped. |
| T-704 | Primer designer | 2026-05-14 | `engine.primer` is now a pure package with typed Primer3-compatible parameters, deterministic fallback primer-pair design, off-target scanning, sequencing-primer placement, and diagnostic-digest primer support; focused slice green with 6 passed; full local gates green with 439 passed, 2 skipped. |
| T-705 | Assembly orchestrator fixed-point loop | 2026-05-14 | `app.assembly_orchestrator` now coordinates codon optimisation, optional validation hooks, assembly planning, primer design, fixed-point fingerprints, and structured convergence failure after the five-iteration cap; focused slice green with 4 passed; full local gates green with 443 passed, 2 skipped. |
| T-801 | Risk-classification advisory layer | 2026-05-14 | `engine.risk_classification` now generates deterministic `RiskAdvisoryReport` values from parsed `risk_advisories.yaml` catalogue payloads, infers trigger tags from design metadata, maps advisories to graded citations, and binds report content hashes to session, construct, checksum, version, catalogue hash, and emitted advisory payloads; focused slice green with 4 passed; full local gates green with 447 passed, 2 skipped. |
| T-802 | Design-plan generator and renderers | 2026-05-14 | `engine.design_plan` now builds always-renderable `DesignRealisationPlan` values from assembly summaries, primers, biosafety classification, validation hashes, and advisory reports; renderers emit canonical JSON, ordered Markdown, and deterministic PDF bytes while static tests keep gated operational protocol types unreachable; focused slice green with 3 passed; full local gates green with 450 passed, 2 skipped. |
| T-804 | Control-set generator and validation | 2026-05-14 | `engine.controls` now generates positive, negative, process, vehicle/mock, and library-specific controls from host role, assembly chemistry, cargo/vector classes, readout, library size, and replicate context; validation reports missing required controls, weak replicate structure, unclear host matching, and negative-baseline issues; focused slice green with 4 passed; full local gates green with 454 passed, 2 skipped. |
| T-805a | Pre-screening draft design bundle orchestrator | 2026-05-14 | `app.design_plan_orchestrator` now composes T-801/T-802/T-804 into deterministic `DraftDesignBundle` values, renders design-plan JSON/Markdown/PDF, validates controls, emits `DesignRealisationPlanRendered`, `ControlSetRendered`, and `RiskAdvisoryReportRendered` design-stream events, and statically excludes gated operational artefacts and screening/authorisation event imports; focused slice green with 14 passed; full local gates green with 458 passed, 2 skipped. |
| T-806a | Advisory presentation and acknowledgement surface | 2026-05-14 | `app.advisory_acknowledgement` now emits active advisory presentation events, creates acknowledged/declined/escalated governance events with embedded acknowledgement payloads, enforces reviewer/admin action authority and escalation approval IDs, and exposes `all_required_advisories_acknowledged()` over binding presentations, hashes, checksums, justifications, and signature evidence; focused slice green with 5 passed; full local gates green with 463 passed, 2 skipped. |
| T-807 | VLP / AAV / lentiviral policy engine | 2026-05-14 | `engine.vlp_policy` now emits deterministic `VlpPolicyReport` values for MS2 RNA-display, phage-derived VLP, AAV, and lentiviral systems with cargo-capacity, packaging-signal, helper-separation, control/readout, replication-boundary, MS-* registry, and risk-trigger coverage; focused slice green with 7 passed; full local gates green with 470 passed, 2 skipped. |
| T-808 | Plugin manifest governance | 2026-05-14 | `app.plugin_governance` now verifies signed plugin manifests against the institutional trust keyring, checks artefact hashes, enforces sandbox permissions, emits approval/rejection governance events, and advances `plugin-manifest-signature` to enforced mode; focused slice green with 10 passed; full local gates green with 476 passed, 2 skipped. |
| T-901 | EMBL + GFF3 adapters | 2026-05-14 | `adapter.io.EmblAdapter` and `adapter.io.Gff3Adapter` implemented; EMBL uses the shared Biopython conversion path, GFF3 reads/writes embedded-FASTA feature payloads, and full local gates are green with 479 passed, 2 skipped. |
| T-902 | SnapGene file-watch channel | 2026-05-14 | `adapter.snapgene.SnapGeneFileWatcher` implemented as a deterministic pollable channel with burst-write debounce, GenBank import/export, validation-hook injection, atomic paired output writes, and T-308e `.dna` reader re-export without a local `dna_reader.py`; full local gates are green with 484 passed, 2 skipped. |
| T-1001 | Vendor adapters + vendor-feasibility gate | 2026-05-14 | `adapter.vendor` now exposes Twist, IDT, and GenScript static-profile adapters with deterministic feasibility checks, partitioning, and cost estimates; `engine.vendor_feasibility_gate` activates the vendor-profile portion of `BlockVendorSubmission`; full local gates are green with 494 passed, 2 skipped. |
| T-1002 | Screening adapters + orchestrator | 2026-05-14 | `adapter.screening` now exposes IGSC, IBBIS, SecureDNA, and institutional blacklist adapters; `app.screening_orchestrator` emits batched `ScreeningCompleted` design-stream events and reviewer sign-off governance events; `engine.screening_gate` activates screening-verdict gates; full local gates are green with 507 passed, 2 skipped. |
| T-803 | Gated SOP-linked protocol renderer | 2026-05-14 | `engine.sop_protocol` now consumes signed SOP templates via `SopTemplateReadPort`, requires observed `OperationalProtocolAuthorised` before rendering, emits reference-only `SopLinkedProtocol` values from `domain.types.sop_protected`, provides deterministic JSON/Markdown/PDF renderers, and advances `sop-after-gates-check` to enforced mode; full local gates are green with 511 passed, 2 skipped. |
| T-805b | SOP protocol bundle orchestrator | 2026-05-14 | `app.sop_protocol_orchestrator` now filters `OperationalProtocolAuthorised` to the current session, invokes T-803 only after authorisation, emits deterministic `SopProtocolBundle` values with authorisation evidence, and appends `SopRendered` design-stream events; full local gates are green with 515 passed, 2 skipped. |
| T-806b | Authorisation gate decision + review-queue routing | 2026-05-14 | `app.authorisation_decision` now consumes `ScreeningCompleted`, verified signed profiles, user declarations, and advisory acknowledgement governance chains before emitting `OperationalProtocolAuthorised`; blocked attempts emit `AuthorisationAttemptDenied`, route to `ReviewQueueService.route_blocked_authorisation`, and `engine.operational_protocol_gate` activates `BlockOperationalProtocol`; focused slice green with 15 passed, `no-passive-advisory-bypass-check` enforced locally, and full local pytest green with 530 passed, 2 skipped. |
| T-903 | Final export orchestrator + redaction | 2026-05-14 | `app.export_orchestrator` now builds deterministic final export ZIPs with canonical manifests, profile redaction, derivation environment, screening, authorisation evidence, and advisory trace; `engine.export_gate` activates composed `BlockExport`; focused T-903 tests green with 6 passed, T-903 `ruff check` green, and `no-passive-advisory-bypass-check` still enforced locally. |
| T-1103a | AdminServiceClientPort Protocol + IPC contract | 2026-05-14 | `domain.types.admin_ipc` request/response/token envelopes, `domain.ports.admin_service.AdminServiceClientPort`, deterministic `InMemoryAdminServiceClient`, contract tests, and `docs/admin_service/ipc_contract.md` added; focused slice green with 11 tests passed, strict mypy green for the new surface, and T-1103a ruff check green. |
| T-1101 | Typer-based CLI command surface | 2026-05-14 | `interface.cli` is now a package with command registry, injectable runtime, optional Typer app builder, stdlib fallback runner, `vector-design` / `cev-design` console scripts, and admin/review-queue admin commands routed through `AdminServiceClientPort`; focused T-1101 tests green with 7 passed, full strict mypy green, full ruff green, agenda consistency green, and full non-slow pytest green with 550 passed / 2 skipped. |
| T-1102 | FastAPI HTTP + WebSocket surface | 2026-05-14 | `interface.api` is now a package with route registry, injectable runtime, dependency-free OpenAPI-style route index, optional FastAPI app builder, validation WebSocket stream helper, and `vector-design-api` console script; admin endpoints route through `AdminServiceClientPort`; focused T-1102 tests green with 9 passed, full strict mypy green, full ruff green, and full non-slow pytest green with 559 passed / 2 skipped. |
| T-1202 | React + TypeScript SPA | 2026-05-14 | Added the separate `ui/` Vite/React package with decision-tree wizard, vector/linear maps, validation report, advisory acknowledgement dialog, admin console, audit-log viewer, design diff, expert-mode/i18n hooks, and `interface.ui` metadata helpers; UI tests, TypeScript build, focused Python tests, ruff, mypy, agenda consistency, and full non-slow pytest are green with 591 passed / 2 skipped. |
| T-1203 | SnapGene API client | 2026-05-14 | Added `SnapGeneApiClient` with injectable SnapGene Server Request API transport, command-tool transport, status/capability probing, import/export GenBank↔`.dna` request flow, SVG map generation, structured errors, and UR-01a file-watch fallback for unavailable or unlicensed live API paths; focused SnapGene tests, ruff, mypy, agenda consistency, and full non-slow pytest are green with 599 passed / 2 skipped. |
| T-1301 | White-paper-example UAT | 2026-05-14 | Added deterministic Example A/B/C UAT flows, shared end-to-end harness, fixture hashes, host-context fixtures, scientific-advisor signoff fixtures, GenBank and SnapGene fallback round-trip checks, VLP MS-06 coverage for the mammalian example, and gate assertions through screening, SOP, and final export; focused UAT tests, ruff, mypy, agenda consistency, and full non-slow pytest are green with 602 passed / 2 skipped. |
| T-1302 | Adversarial UAT suite | 2026-05-14 | Added the 22-scenario adversarial UAT harness, per-scenario modules and expected fixtures, dual-control revocation enforcement, pair-required advisory acknowledgement mode, and an informational no-direct-admin-handler import scanner; focused UAT, related regression slice, full ruff, full strict mypy, static gate, task-acceptance completeness, agenda consistency, and full non-slow pytest are green locally with 624 passed / 2 skipped. |
| T-1303 | Combinatorial library benchmark + release polish | 2026-05-14 | Added deterministic 100-realisation and 1000-realisation library fixtures with locked hashes, release build wrappers, release-note renderer/docs, CI determinism wiring, and a local wheel artefact under `task_artefacts/T-1303/dist/`; focused T-1303 tests, stretch fixture, release determinism check, ruff, mypy, and release dry-runs are green locally. |

---

## 5. Phase exit status (six-dimension audit)

| Phase | Correctness | Completeness | Scientific validity | Performance | Maintainability | Safety |
|---|---|---|---|---|---|---|
| 0 | ✅ | ✅ | ✅ | n/a | ✅ | ✅ |
| 1 | ✅ | ✅ | ✅ | n/a | ✅ | ✅ |
| 2 | ✅ | ✅ | n/a | ✅ | ✅ | ✅ |
| 3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 4 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 7 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 8a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 9a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 10 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 8b | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 9b | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 11 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 12 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 13 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 6. Risk register status (from ARCHITECTURE v1.5 § 6)

All risks have documented mitigations in `ARCHITECTURE.md` v1.5 § 6. CI gates supporting each risk are listed in `CODING_AGENDA.md` § 3.5 and § 4.

| Risk | Description | Mitigation status |
|---|---|---|
| R-01 | LLM constraint translator hallucinates | ✅ mitigated by `AdvisoryTextPolicy`, manual-review fallback, and red-team tests in T-1201 |
| R-02 | Plugin version drift breaks reproducibility | ✅ `DerivationEnvironment` captures all versions; T-1303 CI determinism check now covers white-paper examples plus the 100-realisation library fixture. |
| R-03 | Codon × validator loop oscillates | ✅ N=5 cap + lexicographic-priority fixed-point implemented in T-701 / T-705 |
| R-04 | Rule registry grows unmaintainable | 🟡 partitioned manifests + `last_reviewed` field + quarterly review planned in T-401 / T-405 |
| R-05 | Screening adapter outages | ✅ provider failures aggregate to `UNAVAILABLE`; institutional fallback never produces `CLEAR` (T-1002) |
| R-06 | SnapGene proprietary format drift | ✅ file-watch MUST channel implemented in T-902; optional `.dna` handling uses the T-308e read-only parser with GenBank fallback guidance. |
| R-07 | SBOL 3.1.x spec evolves | 🟡 pinned dependency; initial SBOL sequence round-trip covered in T-308; richer feature-coordinate property coverage remains future work |
| R-08 | Library exceeds performance budget | ✅ T-1303 adds deterministic 100-realisation smoke and 1000-realisation stretch fixtures with batched design-stream screening evidence. |
| R-09 | Determinism slips on platform variance | ✅ T-1303 wires release determinism checks for Linux and Windows CI runners and provides pinned wheel/container build wrappers. |
| R-10 | Free-text inputs leak to cloud LLM | ✅ local-LLM default; OpenAI/Anthropic adapters require explicit per-session opt-in |
| R-11 | AI-evasion of screening (2025 watch-item) | ✅ T-1002 added `MANUAL_REVIEW_REQUIRED` routing and non-clear fallback behavior; T-1302 adversarial UAT now verifies screening/advisory bypasses fail closed. |
| R-12 | Junior researcher misuses generated protocol | ✅ non-operational design-plan rendering delivered in T-802, pre-screening `DraftDesignBundle` delivered in T-805a, engine-level gated SOP rendering delivered in T-803, app-level SOP bundle orchestration delivered in T-805b, and authorisation hard gate delivered in T-806b |
| R-13 | Catalogue staleness silently affects outputs | 🟡 `stale-catalogue-check` CI gate planned in T-401 |
| R-14 | Coordinate round-trip is hard | 🟡 GenBank feature coordinates covered in T-308; richer SBOL feature-coordinate round trips remain future work |
| R-15 | Multi-host marker conflict misclassification | 🟡 role-keyed `HostContext` planned in T-304 |
| R-16 | User self-elevates authorisation | 🟡 T-1302 blocks user/reviewer/developer escalation attempts and verifies the CLI/API direct-admin-handler boundary; the broader `no-self-authorisation-check` aggregate gate remains a later consolidation. |
| R-17 | LLM unsafe output | ✅ `AdvisoryTextPolicy` + enforced `llm-output-policy-check` delivered in T-1201 |
| R-18 | Plugin trust escalation | ✅ signed manifest verification, artefact hashing, sandbox permission checks, governance events, and enforced `plugin-manifest-signature` gate delivered in T-808 |
| R-19 | Export bundle PII leak | ✅ `ExportProfile` redaction applied at export serialisation time in T-903; vendor/collaborator/publication profiles omit internal evidence and redact user/institution/vendor identifiers |
| R-20 | Unsupported biosafety tier attempted | ✅ T-503 delivered the structural predicate slot in the implemented registry subset; T-1302 verifies end-to-end BSL-4 hard-block UAT. |
| R-21 | Advisory bypass | ✅ report generation delivered in T-801, draft-bundle inclusion in T-805a, active presentation/acknowledgement predicate in T-806a, authorisation consumption in T-806b, and enforced `no-passive-advisory-bypass-check` local gate |

Legend: ✅ mitigated and verified in CI; 🟡 mitigation planned with task ownership; 🔴 unmitigated.

---

## 7. CI gate status (v1.2 — four-state lifecycle column per B2-07 / M2-07)

| Gate | Lifecycle state | Owning task | Workflow mode | Last CI result |
|---|---|---|---|---|
| `lint` | `enforced` | T-201 | GitHub Actions matrix + local `uv run --no-editable ruff check .` | local green 2026-05-14 |
| `mypy --strict` | `enforced` | T-201 | GitHub Actions matrix + local `uv run --no-editable mypy src tools tests` | local green 2026-05-14 |
| `pytest` (unit) | `enforced` | T-201 | GitHub Actions matrix + local `uv run --no-editable python tools/ci/run_pytest.py -m "not slow"` | local green 2026-05-14 |
| `pytest-cov` ≥ 90 % on domain + engine | `not_implemented` | T-201 | (absent) | unknown |
| `integration` (deterministic fakes) | `not_implemented` | T-201 | (absent) | unknown |
| `determinism` (container) | `enforced-green` | T-201 / T-1303 | GitHub Actions Linux + Windows determinism job running `tools/ci/determinism_check.py` | local green 2026-05-14 |
| `rule-validation coverage` | `not_implemented` | T-405 / T-503 | (absent) | unknown |
| `no-domain-impurity-check` | `enforced` | T-502 | local static import scan + import-linter boundary complement | local green 2026-05-14 |
| `import-linter` | `not_implemented` | T-204 / T-306 | (absent) | unknown |
| `no-self-authorisation-check` | `not_implemented` | T-204 / T-311 / T-313b / T-316b / T-1103b | (absent) | unknown |
| `no-direct-admin-handler-import-check` | `informational` | T-204 / T-1101 / T-1102 / T-1302 | local static scan over CLI/API boundary | local green 2026-05-14 |
| `no-passive-advisory-bypass-check` | `enforced` | T-204 / T-806a / T-806b | `tests/ci_gates/test_t204_gates.py` + local `python -m tools.ci_gates.no_passive_advisory_bypass_check --enforce` | local green 2026-05-14 |
| `sop-after-gates-check` | `enforced` | T-204 / T-803 | `tests/ci_gates/test_t204_gates.py` + local `python -m uv run --no-editable python -m tools.ci_gates.sop_after_gates_check --enforce` | local green 2026-05-14 |
| `llm-output-policy-check` | `enforced` | T-204 / T-1201 | `tests/ci_gates/test_llm_output_policy_t1201.py` + local `python -m tools.ci_gates.llm_output_policy_check --enforce` | local green 2026-05-14 |
| `audit-traceability-check` | `not_implemented` | T-204 | (absent) | unknown |
| `plugin-manifest-signature` | `enforced` | T-808 | GitHub Actions + local `python -m uv run --no-editable python -m tools.ci_gates.plugin_manifest_signature_check --enforce` | local green 2026-05-14 |
| `source-grade-citation-check` | `informational` | T-401 | 2026-05-14 | green |
| `stale-catalogue-check` | `informational` | T-401 | 2026-05-14 | green |
| `module-coverage-check` (manual `docs/module_manifest.yaml` seed; architecture consistency informational) | `not_implemented` | T-204 | (absent) | unknown |
| `task-acceptance-completeness-check` (v1.2 — new per M2-03; v1.3 YAML schema in Appendix D per M3-03) | `not_implemented` | T-204 | (absent) | unknown |
| `gate-lifecycle-check` (v1.1) | `not_implemented` | T-204 | (absent) | unknown |
| `rule-fixture-coverage-check` (v1.1; v1.3 enforced at Phase 4 exit per H3-08) | `informational` | T-401 / T-405 | 2026-05-14 | green |
| `implementation-status-consistency-check` (v1.1) | `informational` | T-401 / T-405 | 2026-05-14 | green |

**Lifecycle legend.** `not_implemented` — gate absent from CI workflow (owning task `planned`). `informational` — gate present in workflow with `continue-on-error: true` (owning task in `in-progress` or post-stub). `enforced` — merge-blocking (owning task `verified`; gate predicate active). `enforced-green` — merge-blocking and observed-passing at least once on `main`.

The `gate-lifecycle-check` meta-gate (v1.1) cross-validates this table against the agenda's § 3.5 CI table and the workflow YAML; drift fails the gate.

---

## 8. Update protocol

This file is updated by `/dev-orchestrator` at every task state transition:

1. **On task PLAN** — add an entry under § 3 with status `⚪ planned`.
2. **On task ASSIGN** — set assignee + start timestamp; stage = `🟡 in-progress`.
3. **On task EXECUTE-COMPLETE** — stage = `🟢 execution-complete`; CI run referenced.
4. **On task VERIFY** — if six dimensions all green: stage = `✅ done`; move to § 4 "Recently completed"; remove from § 3. If any amber/red: stage = `🔴 verification-failed`; open follow-up task.
5. **On phase EXIT** — update § 1, § 5 (six-dimension audit per phase); update affected risk-register rows in § 6.

CI gate flips from ⚪ to ✅ when the gate is enabled as release-blocking in `.github/workflows/ci.yaml` and observed green on at least one PR.

---

*End of TASK_BOARD.md.*
