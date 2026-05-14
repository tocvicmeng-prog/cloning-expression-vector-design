# Third-Round CODING_AGENDA.md Audit — Three-Role Response

**Audit input:** `audit report/CODING_AGENDA_Third_Round_Audit_Report.md`.
**Subject:** `CODING_AGENDA.md` v1.2.
**Result:** **27 / 27 findings accepted (8 blocking + 11 high + 8 moderate); 0 defended.**
**Output:** `CODING_AGENDA.md` v1.3; `ROADMAP.md` updated; `TASK_BOARD.md` updated; `README.md` updated; memory pointer updated.
**Adjudicating roles:** `/architect`, `/scientific-advisor`, `/dev-orchestrator`.
**Date:** 2026-05-14.

## Executive summary

The auditor's verdict is correct. v1.2 closed v1.1's synchronisation gaps but introduced (or exposed) a second class of defects centred on **operational security boundaries**: audit-write ownership, signed-value-object durability, profile signatures, SOP-template write governance, and review-queue workflow. These are not phase-ordering defects (v1.2 fixed those); they are **interface and persistence defects** that would let an implementation satisfy the surface contracts while leaving the audit trail, profile integrity, or recovery workflow undefined.

The three roles convened, walked each finding against `ARCHITECTURE.md` v1.5, `REQUIREMENTS.md` (especially FR-AUTH-02/04/07/10/12, FR-ADV-02/06, FR-PROTO-SOP-09), and the v1.2 wiring, and accepted every finding without defence. v1.3 closes all 27 with a targeted security/audit-boundary pass.

| Severity | Total | Accepted | Defended |
|---:|---:|---:|---:|
| Blocking | 8 | 8 | 0 |
| High | 11 | 11 | 0 |
| Moderate | 8 | 8 | 0 |

## Adjudication method (continued from v1.1 / v1.2)

For each finding the three roles asked the same four questions as in the prior responses: factual correctness against the agenda; impact correctness against `ARCHITECTURE.md` v1.5 / `REQUIREMENTS.md`; defensibility within the current plan; smallest correction. Where 1 and 2 are yes and 3 is no, the finding is accepted.

## Blocking findings

### B3-01 — Audit-log write ownership contradictory. **Accepted.**

**Adjudication.** Verified at `CODING_AGENDA.md:1217-1224, 1279-1290` (composition root injects `audit_log` directly into PluginGovernance / AdvisoryAcknowledgementService / ScreeningOrchestrator / AuthorisationDecisionService) versus `CODING_AGENDA.md:1392-1394` (persistence table says writer is `app.admin_action_handler` only, engine reads in `mode=ro`). Both cannot be true. The auditor is correct: governance services need to append audit entries from inside the engine process, but the v1.2 persistence claim forbids that. The "every governance-event-writing application service appends its own audit row through the same handler" line is a contradiction since `admin_action_handler` is `None` in the engine process.

**v1.3 correction.** Introduce a dedicated **`AuditAppendPort`** broker pattern that separates audit-append authority from authorisation-store write authority:

- **New port** `domain.ports.audit_append.AuditAppendPort` with one method: `append(entry: AuditEntry, caller_principal: ServicePrincipal) -> AuditEntryId`. Append-only. Verifies caller is a registered `ServicePrincipal` (engine-internal identity for governance services); preserves HMAC chain integrity through `AuditKeyProvider`; rejects modification or deletion.
- **New task T-313 `Audit append broker`** (Phase 3) — owns `src/app/audit_broker.py` + `src/adapter/persistence/sqlite_audit_log_append.py`. The append broker runs **in the engine process**; the audit log is opened `mode=rw` for the broker's exclusive file handle (kernel-enforced single-writer through SQLite's WAL+exclusive lock); other code paths in the engine receive **only** `AuditAppendPort` (not the raw `AuditLog`). Verification reads still use `AuditLog` in `mode=ro` for read paths.
- **Updated composition root**: replaces every `audit_log: AuditLog` injection into application services with `audit_append: AuditAppendPort`. Read-only audit reads (replay, verification, `audit-traceability-check`) use `audit_log_reader: AuditLogReadPort` separately.
- **Persistence table updated** to show two writers — `AuditBroker` (engine process, append-only) and `app.admin_action_handler` (admin-service process, append-only) — both writing through the same HMAC chain via `AuditKeyProvider`.
- **Test** `tests/security/test_audit_append_broker_separation.py` confirms: (a) engine code paths cannot reach `AuthorisationAdminWritePort`; (b) engine code paths can append audit entries via `AuditAppendPort`; (c) the broker rejects entries from non-`ServicePrincipal` callers.

### B3-02 — T-310/T-311 depend on T-312 before T-312 exists. **Accepted.**

**Adjudication.** Verified at `CODING_AGENDA.md:590-601` (T-310 says "consumes `AuditKeyProvider` from T-312") and `CODING_AGENDA.md:612-617` (T-311 audit-chain integration test references the provider). T-312 appears later (`CODING_AGENDA.md:619-644`). Phase 3 as listed cannot be executed in T-301→T-310→T-311→T-312 order without circular dependency. The auditor is correct.

**v1.3 correction.** Split T-312 into:

- **T-312a `AuditKeyProvider` protocol + `TestAuditKeyProvider`** (Phase 3, **scheduled immediately after T-307 and before T-310**). Deliverables: `src/domain/ports/audit_key.py` (Protocol only — `current_key`, `key_version`, `verify_with_archived`, `rotate`); `tests/fakes/security/audit_key/test_audit_key_provider.py` (deterministic in-memory test provider returning a fixed key); contract tests verifying the protocol shape. T-310 / T-311 depend on T-312a only.
- **T-312b `AuditKeyProvider` production adapters + rotation service + offline verifier** (Phase 3, **scheduled after T-311**). Deliverables: `src/adapter/security/audit_key/{file_keystore,os_keystore_windows,os_keystore_posix}.py`, `src/app/audit_key_rotation_service.py`, `tools/audit_key_verifier.py`, `docs/security/audit_key_runbook.md`, all the integration tests (`test_absent`, `test_wrong`, `test_rotated`, `test_tampered`, `test_offline_verification`, `test_separation_of_signature_and_hmac_keys`).

Updated Phase 3 task order: T-301 → T-302 → T-303 → T-304 → T-305 → T-306 → T-307 → **T-312a** → T-308 → T-309 → T-310 → T-311 → **T-312b** → **T-313** → **T-314** → **T-315** → **T-316**.

### B3-03 — Governance events reference-only without durable value-object store. **Accepted.**

**Adjudication.** Verified at `CODING_AGENDA.md:493-500` (T-305 says governance events carry only typed references; full value object "resolved via the persistence layer at replay or audit time"). The agenda defines no `RiskAdvisoryAcknowledgementStore` / `DecisionRecordStore` / `RoleSnapshotStore`. This conflicts directly with `REQUIREMENTS.md:386` (FR-ADV-06: the full approval trace MUST be persisted in the immutable governance event stream) and `ARCHITECTURE.md:2161-2168` (`ReviewerSignedOff` carries the signed `DecisionRecord`). The v2 H2-03 "make events reference-only" fix was over-corrected: it solved ownership duplication but broke durability.

**v1.3 correction.** Revise H2-03's resolution: governance events **embed** the full canonical signed value object (frozen-dataclass payload), **not** a reference. The value-object **type** remains owned by `domain.types.risk_advisory` and `domain.types.governance` (preserving H2-03's namespace separation), but each governance event payload **contains** an immutable canonical snapshot of the value object's serialised form. Specifically:

- `RiskAdvisoryAcknowledged` event payload includes the full `RiskAdvisoryAcknowledgement` value object (canonical JSON form per T-307) and its content hash. The event itself is the durable record.
- `RiskAdvisoryDeclined` / `RiskAdvisoryEscalated` likewise embed the full decision payload.
- `ReviewerSignedOff` / `AuthorisationAttemptDenied` / `AdminAction*` likewise embed full `DecisionRecord` + `RoleSnapshot` payloads.
- T-305 SOP is rewritten to require **embedded payload + content hash**, not reference. The cross-stream replay-determinism test (T-309a) confirms that reading the design + governance streams alone is sufficient to reconstruct the full session, with **no external value-object lookup required**.
- Static test `tests/static/test_governance_events_self_contained.py` asserts every governance event subclass has a non-reference payload field for its value object.

This restores FR-ADV-06's immutable-approval-trace property: the governance JSONL file is the durable signed-record store. No additional value-object store is required.

### B3-04 — `AuthorisationProfile` institutional signature missing. **Accepted.**

**Adjudication.** Verified at `REQUIREMENTS.md:363` (FR-AUTH-02: profile MUST include institutional signature) and `REQUIREMENTS.md:371` (FR-AUTH-10: tampered profile MUST fail verification on load). T-304 at `CODING_AGENDA.md:473-484` only implements `profile_content_hash`, not signature. T-310/T-311 cover database read/write and HMAC audit chain but do not verify per-profile signatures on read or sign on write. FR-AUTH-10 has no owning task.

**v1.3 correction.** Add profile signature support distributed across T-304, T-310, T-311, and a new T-314:

- **T-304** adds two fields to `AuthorisationProfile`: `profile_signature: ProfileSignature` (binds full canonical payload + version + subject UserId + issuer AdminPrincipalId + validity interval + revocation metadata via the institutional `AuthorisationProfileSigner` key) and `profile_signature_key_version: KeyVersionId`. Unit tests confirm: (a) a profile with mismatched signature fails frozen-dataclass `__post_init__` validation; (b) re-canonicalisation produces byte-identical signed payload.
- **T-310d (read side)** — `SqliteAuthorisationStoreRead.get()` calls `AuthorisationProfileVerifier.verify(profile)` before returning. Verification failure raises `AuthorisationProfileTamperDetectedError`; never returns a partially-trusted profile. Test: corrupt one byte in `authorisation.sqlite` → load returns the tamper error.
- **T-311** — every admin write (`mint`, `modify`, `revoke`) calls `AuthorisationProfileSigner.sign(profile, admin_principal)` before commit. Test: writes from `AdminPrincipal` produce verified-loadable profiles; writes that bypass the signer (test injection) fail downstream verification.
- **NEW T-314 `AuthorisationProfile signing ports + adapters`** (Phase 3, after T-311). Deliverables: `src/domain/ports/profile_signing.py` (`AuthorisationProfileSigner` + `AuthorisationProfileVerifier` Protocols); `src/adapter/security/profile_signing/institutional_signer.py` (the production signer — separate cryptographic key from the audit HMAC key, separate from per-principal DecisionRecord signer); offline verifier tool; test fixtures for tamper, revoked-key, wrong-version, valid-cases.

### B3-05 — SOP-template admin writes have no write port. **Accepted.**

**Adjudication.** Verified at T-203 (lists `SopTemplateLibrary` as a single catalogue port), T-311 (defers SOP-template admin writes to T-803), T-803 in v1.2 (adds `src/app/admin_action_handler/sop_template_writes.py` but still consumes the single `SopTemplateLibrary` and the YAML loader). No `SopTemplateAdminWritePort` exists. The agenda's claim that `app.admin_action_handler` is the sole write path to institutional SOP templates is not implementable.

**v1.3 correction.** Add **NEW T-316 `SopTemplate admin write port + persistence model`** (Phase 3, after T-315). Deliverables:

- `src/domain/ports/sop_template.py` — three Protocols: `SopTemplateReadPort` (existing read shape, lifted from `SopTemplateLibrary`), `SopTemplateAdminWritePort` (`write_mint`, `write_modify`, `write_revoke`, all requiring `AdminPrincipal | DeveloperBootstrapPrincipal`), `SopTemplateBootstrapPort` (`bootstrap_initial_templates(developer)`).
- `src/adapter/persistence/sqlite_sop_template_store.py` — SQLite-backed store replacing the YAML-only loader. Migrations preserve existing YAML templates as the initial bootstrap. Each template carries a signature via `AuthorisationProfileSigner`-class infrastructure (institutional template signer key); tampered templates fail load via `SopTemplateTamperDetectedError`.
- `src/app/admin_action_handler/sop_template_writes.py` — moved out of T-803 into a dedicated handler module; emits `SopTemplateMinted` / `Modified` / `Revoked` governance events with embedded signed payloads (per B3-03).
- Schema, atomic-write path, version history, denial tests for User/Reviewer, and acceptance tests for read/write/revoke.

T-803 (Phase 8b) is updated: it **consumes** the `SopTemplateReadPort` (no longer the `SopTemplateLibrary` directly); the admin-write surface lives in T-316. T-203c port inventory adds the three new ports.

### B3-06 — Administrator review queue + user extension workflow missing. **Accepted.**

**Adjudication.** Verified at `REQUIREMENTS.md:327` (FR-PROTO-SOP-09: blocked SOP MUST emit a structured request to the administrator review queue), `REQUIREMENTS.md:368` (FR-AUTH-07: review-queue requirement), `REQUIREMENTS.md:373` (FR-AUTH-12: users submit extension requests to Administrator without auto-granting). v1.2 has no `app.review_queue`, no `AuthorisationRequest` type, no `ReviewQueueItemCreated` event. The agenda implements the gate (blocks) without the recovery path (queue + admin triage). FR-PROTO-SOP-09 and FR-AUTH-07/12 are unowned.

**v1.3 correction.** Add **NEW T-315 `app.review_queue` + authorisation request service** (Phase 3, after T-314). Deliverables:

- `src/domain/types/review_queue.py` — value objects `AuthorisationRequest` (subject user, requested scope, justification, related session, supporting evidence), `ReviewQueueItem` (id, request, status: `pending | under_review | approved | denied | expired`, assigned admin, decision record, timestamps), `ReviewQueueItemDecision` (signed by AdminPrincipal).
- `src/adapter/persistence/sqlite_review_queue_store.py` — SQLite-backed append-then-update store. `add(request)` is append-only (request immutable once written); `resolve(item_id, decision)` writes a new decision record but never mutates the request.
- `src/app/review_queue_service.py` — three use cases: `submit_extension_request(user_principal, scope, justification)` (FR-AUTH-12), `route_blocked_authorisation(session_id, reason)` (FR-PROTO-SOP-09 — called by `app.authorisation_decision` when gate blocks), `triage_queue(admin_principal, item_id, decision)` (admin reviews + approves/denies).
- Typed events: `AuthorisationExtensionRequested`, `ReviewQueueItemCreated`, `ReviewQueueItemAssigned`, `ReviewQueueItemResolved` (all governance events with embedded signed payloads per B3-03).
- Acceptance tests: (a) a blocked SOP rendering produces exactly one pending `ReviewQueueItem` in `submitted` state; (b) a user calling `submit_extension_request` cannot self-approve; (c) admin resolves request → `ReviewQueueItemResolved` + audit-log entry; (d) FR-AUTH-12: user request is never auto-granted; (e) the gate predicate's recovery path runs through the queue.

Cross-resolution: T-806b (Phase 8b) calls `review_queue.route_blocked_authorisation` when `BlockOperationalProtocol` fires; Phase 11 CLI / Phase 12 UI surface `submit-extension-request`, `list-review-queue`, `triage-request` commands routed via the admin-service IPC (H3-09).

### B3-07 — Phase 2 platform tests depend on Phase 5 implementation. **Accepted.**

**Adjudication.** Verified at `CODING_AGENDA.md:420-435` (T-205 has `test_worker_pool_factory.py` for `WorkerPoolFactory` semantics) and `CODING_AGENDA.md:715-731` (T-502 owns the actual `WorkerPoolFactory` implementation in Phase 5). Same defect class as v1.2's H2-07 (file-watch debounce) but with multiprocessing. T-205 acceptance requires the test to pass on both `ubuntu-latest` and `windows-latest` in Phase 2 — impossible without the factory.

**v1.3 correction.**

- **Remove `test_worker_pool_factory.py` from T-205.** T-205 in v1.3 tests only minimal platform probes: `multiprocessing.get_context("spawn").Pool` can be created with a single top-level test function in a temp module (no production factory involved); a one-line probe `tests/platform/test_spawn_context_available.py` confirms the spawn context is available on both OSes.
- **Move `test_worker_pool_factory.py` to T-502.** T-502's acceptance includes the cross-platform factory semantics test (sequential / thread / process modes on both OSes, library-import safety, FastAPI/notebook fallback path).
- T-205's amended SOP step 5 in v1.3 reads: "Probe — assert `multiprocessing.get_context('spawn')` returns a usable context on this platform; T-502 owns the production `WorkerPoolFactory` test."

### B3-08 — T-309 / T-309a / T-309b task-identity ambiguity. **Accepted.**

**Adjudication.** Verified at `CODING_AGENDA.md:566-587` (parent T-309 heading retained alongside T-309a / T-309b sub-headings). Three potential models for parsers + task-board generators; v1.2 ambiguously hints at all three. `TASK_BOARD.md` Phase 3 count says "12 tasks listing T-301..T-312" but the agenda has T-309 + T-309a + T-309b — three task headings for one canonical work item. Pseudo-task counting is a real risk for automated tooling (module-coverage gate, task-acceptance-completeness gate).

**v1.3 correction.** Choose **Model 1**: `T-309` is the **only** task identity. T-309a and T-309b are **sub-deliverables documented inside** the T-309 task card — not separate task IDs. This matches the existing v1.2 pattern for T-303 (sub-split a/b/c documented inside the card), T-308 (sub-split a..e), T-703 (sub-split a..e). T-309's task card lists:

- **T-309 (Phase 3)** — `engine.session` state machine + replay-determinism skeleton + typed pending-predicate registry. The task ships in Phase 3.
- **Sub-deliverable (a)** — the Phase-3-resident skeleton (state enum, event-sourced replay, snapshot format, GatePredicateRegistry initialised with `GatePending` sentinels).
- **Sub-deliverable (b)** — per-phase gate-predicate activation: the *registration replacement* happens inside T-502 (BlockCompile), T-806b (BlockOperationalProtocol), T-1002 (BlockVendorSubmission), T-903 (BlockExport). These activations are **owned by the gate-activating tasks**, not by a separate T-309b task. T-309 documents the activation map (`docs/safety_gates/activation_map.md`) and exposes the registry API; activation is a deliverable of the owning gate task, not a child of T-309.

Task headings `#### 2.3.9a` and `#### 2.3.9b` are removed; T-309 has a single `#### 2.3.9` heading with the sub-deliverable description inline.

## High findings

### H3-01 — T-204 stale module-coverage instructions + missing gate files. **Accepted.**

**v1.3 correction.** Rewrite T-204:

- File list adds `task_acceptance_completeness_check.py`, `tools/architecture_manifest_generator.py`, `docs/module_manifest.yaml` (generated), `tests/ci_gates/test_module_coverage_check.py`, `tests/ci_gates/test_task_acceptance_completeness_check.py`.
- SOP step 5 rewritten: `module_coverage_check.py` **only** parses `docs/module_manifest.yaml` (generated by `architecture_manifest_generator.py` from `ARCHITECTURE.md` § 4.2). No Markdown parsing. Manifest schema: `{module_id, layer, architecture_section, tasks: [task_id, ...]}`.
- SOP step 6 (new): `task_acceptance_completeness_check.py` parses each `tasks/task_brief/T-<id>.md`, looks for the mandatory YAML acceptance block (schema in Appendix D), fails if missing or malformed.
- Acceptance updated: both gates run in `informational` mode at T-204 verification; flip to `enforced` per the CI lifecycle table.

### H3-02 — `BlockVendorSubmission` not fully wired. **Accepted.**

**v1.3 correction.** Split the predicate inputs:

- **T-1001 (vendor adapters)** activates the vendor-profile feasibility portion of `BlockVendorSubmission`. When any registered vendor's `check(request)` returns rejection (length / GC / repeat / adapter / product-format failure), the gate fires. T-1001 ships fixtures for each rejection class.
- **T-1002 (screening)** activates the screening-verdict portion of `BlockVendorSubmission` (HIT / WATCHLIST → block).
- **T-903 (export)** consumes both predicates before emitting `VendorSubmissionPrepared`. Test: vendor rejects but screening clear → still blocked.
- T-309 documents the multi-input activation in the gate-activation map.

### H3-03 — Phase 13 UAT cards too thin. **Accepted.**

**v1.3 correction.** Expand T-1301, T-1302, T-1303 with full SOPs, fixtures, and acceptance:

- **T-1301** — three white-paper-example UAT files (`tests/uat/example_a_bacterial.py`, `tests/uat/example_b_mammalian.py`, `tests/uat/example_c_plant.py`). Each runs the full pipeline (create → add parts → compile → screen → authorise → export) end-to-end with realistic fakes. Acceptance: every example produces a deterministic ExportBundle that opens in SnapGene + GenBank tools.
- **T-1302** — adversarial UAT, file list explicit: `tests/uat/adversarial/{self_elevation,advisory_bypass,reviewer_escalation,unsupported_tier,plugin_trust,export_leak,audit_key_absent,audit_key_compromise,replay_integrity,construct_checksum_mismatch,programmatic_event_bypass,review_queue_blocked_path}.py`. Each scenario has a fixture + expected verdict + expected events.
- **T-1303** — combinatorial library benchmark + release-polish acceptance with concrete cadence: nightly, 100-realisation fixture + 1000-realisation stretch fixture; deterministic across runs.

### H3-04 — Roadmap legacy sections look active. **Accepted.**

**v1.3 correction.** Move the v1.1 `Phase 8 (LEGACY)` and `Phase 9 (LEGACY)` blocks out of the main phase sequence and into a new **Appendix A — Pre-v1.2 phase history** at the end of `ROADMAP.md`. Prefix all legacy headings with `Legacy-Pre-v1.2-` to make them parser-distinct.

### H3-05 — README stale (v1.1). **Accepted.**

**v1.3 correction.** Update `README.md` to reference CODING_AGENDA v1.3 (after the third-round audit), the four-audit chain, Phase 9a/9b split, T-311/T-312/T-313/T-314/T-315/T-316 tasks, and revised task count.

### H3-06 — Internal review text contradicts library-mode event ownership. **Accepted.**

**v1.3 correction.** Rewrite the § 7.3 Round-3 paragraph about library mode: batched `ScreeningCompleted` events are **design events** (one event per batch with per-realisation evidence in the payload). The governance stream carries only reviewer/admin decision records and advisory governance for the library realisations.

### H3-07 — Appendix C still lists T-805 budget row. **Accepted.**

**v1.3 correction.** Remove the `app.protocol_orchestrator` (T-805) row from Appendix C. Add a header note: "This table is generated from the canonical task manifest (`docs/task_manifest.yaml`) via `tools/task_budget_generator.py`. Manual edits are overwritten on regeneration."

### H3-08 — Rule-fixture gate lifecycle conflicts with Phase 4 exit. **Accepted.**

**v1.3 correction.** Update § 3.5 CI lifecycle:

- `rule-fixture-coverage-check` is `informational` while T-405 sub-tasks are in-progress (Phase 4 active), and **`enforced` at T-405 verification (= Phase 4 exit)**. Phase 4 exit cannot succeed if the gate is red. Rules that legitimately defer fixtures require explicit `deferred_with_reason: <reason>` field in the manifest + `/scientific-advisor` sign-off recorded as a `RuleFixtureDeferralApproved` governance event.

### H3-09 — Admin-service IPC/authentication has no implementation task. **Accepted.**

**v1.3 correction.** Add **NEW T-1103 `Admin-service executable boundary + IPC`** (Phase 11, after T-1102). Deliverables:

- `src/interface/admin_service/__main__.py` — admin-service process entry point.
- `src/interface/admin_service/ipc.py` — local IPC: named pipe on Windows (`\\.\pipe\cev-admin-service`); Unix domain socket on POSIX (`/var/run/cev-admin/socket`). Configurable path; permissions enforce admin-only.
- Mutual authentication: client supplies signed AdminPrincipal/DeveloperPrincipal credentials (via OS process token / DPAPI on Windows; via SO_PEERCRED on Linux); admin-service verifies and binds the principal to the request.
- CLI (`vector-design admin-mint` etc., Phase 11 T-1101) and API (Phase 11 T-1102) route admin commands through this IPC.
- Acceptance tests: (a) unauthenticated client → denied; (b) UserPrincipal credentials → denied + audit entry; (c) AdminPrincipal credentials → routed + audit entry; (d) Windows named-pipe + POSIX socket both green.

### H3-10 — Developer authority for ordinary mint/modify/revoke ambiguous. **Accepted.**

**v1.3 correction.** Introduce `DeveloperBootstrapPrincipal` as a distinct sub-type:

- T-304 in v1.3 adds two Principal sub-types: `DeveloperPrincipal` (developer in development mode, full access to all bootstrap + diagnostic operations) and `DeveloperBootstrapPrincipal` (a `DeveloperPrincipal` whose token explicitly carries an `is_bootstrap = True` claim, valid only during initial system bootstrap or when an institutional policy explicitly grants the role).
- T-311 mint/modify/revoke permissions: `AdminPrincipal | DeveloperBootstrapPrincipal` (not the broader `DeveloperPrincipal`). After bootstrap completes (one-time event marked `AdminBootstrapped`), subsequent mint/modify/revoke require `AdminPrincipal` unless `institutional_policy.developer_permanent_admin == True`.
- Tests: `test_developer_cannot_mint_after_bootstrap_unless_policy_grants`, `test_developer_bootstrap_principal_works_pre_bootstrap_only`.

### H3-11 — `AdvisoryWarningPresented` schema under-specified. **Accepted.**

**v1.3 correction.** Expand T-806a with the full FR-ADV-02 schema:

```python
@dataclass(frozen=True)
class AdvisoryWarningPresented(GovernanceEvent):
    design_session_id: SessionId
    construct_id: ConstructId
    construct_checksum: ConstructChecksum
    report_content_hash: ReportContentHash
    advisory_ids: frozenset[AdvisoryId]  # all advisories in the rendered report
    presentation_surface: PresentationSurface  # CLI | API | UI
    presentation_surface_version: str  # e.g., "cli==0.3.2"
    recipient_principal_id: PrincipalId
    recipient_role: SecurityRole  # must be ADMINISTRATOR or REVIEWER (validated)
    presented_at_utc: datetime
    presentation_id: PresentationId  # unique per render
```

`recipient_role` constraint: must be `SecurityRole.ADMINISTRATOR` or `SecurityRole.REVIEWER` for a *bindng* presentation (a presentation to a User is a soft notification; the gate only honours acknowledgements presented to an Administrator or Reviewer). Tests: one per surface (CLI, API, UI); one for each recipient-role rejection (non-admin/non-reviewer presentation does not count as a presentation for gate purposes).

## Moderate findings

### M3-01 — Dependency groups vs extras conflated. **Accepted.**

**v1.3 correction.** Specify in T-201:

- **uv "dependency groups"** (`[tool.uv.dependency-groups]`) — for `dev` (test/lint/type-check) only.
- **PEP 621 "optional dependencies"** (`[project.optional-dependencies]`) — for `io`, `biology-vienna`, `biology-spliceai`, `biology-signalp`, `primer`, `api`, `cli`, `llm-local`, `llm-openai`, `llm-anthropic`. These are installable via `uv sync --extra <name>` or `pip install package[extra]`.
- Acceptance command updated: `uv sync --group dev` (for dev) + `uv sync --extra io` (for an optional adapter set). CI matrix uses the corresponding `--extra` flags.

### M3-02 — T-201 determinism check before fixtures exist. **Accepted.**

**v1.3 correction.** In T-201, the determinism job is created in `not_implemented` lifecycle state — present in workflow YAML as a comment-only stub, executed as a no-op until T-1301 fixtures exist. Alignment recorded in § 3.5 CI lifecycle table.

### M3-03 — `task-acceptance-completeness-check` requires YAML but template has none. **Accepted.**

**v1.3 correction.** Append a mandatory YAML block to the task-brief skeleton in Appendix D. Schema:

```yaml
# tasks/task_brief/T-<id>.md (acceptance section)
acceptance:
  - id: A1
    description: "mypy --strict green on every stub"
    test: "tests/typing/test_mypy_strict_<task>.py"
    blocks_verification: true
  - id: A2
    description: "test_port_inventory.py green"
    test: "tests/ports/test_port_inventory.py"
    blocks_verification: true
phase: 2
owning_modules: [domain.ports, ...]
gates_activated: []
gates_advanced_to: ["informational"]
```

The new gate `task-acceptance-completeness-check` enforces this schema on every brief.

### M3-04 — Port inventory overly closed. **Accepted.**

**v1.3 correction.** Update T-203c `test_port_inventory.py`:

- Required ports listed in the canonical port catalogue (the 37 in T-203c) must all exist.
- *Additional* ports discovered under `src/domain/ports/` are permitted **iff** they have a manifest entry in `docs/port_manifest.yaml` with `port_id`, `owning_task`, `architecture_section`, `requirements_refs` populated.
- Manifest-less ports fail the gate.
- This permits plugin-introduced ports without freezing the agenda text as the only source of truth.

### M3-05 — Renderer determinism cross-platform unspecified. **Accepted.**

**v1.3 correction.** Expand T-201 + T-802:

- T-201 adds **font-packaging step**: `tools/fonts/install_canonical_fonts.py` downloads / installs Noto Sans + Noto Mono into the project under `fonts/` (bundled in CI; bundled in the Docker image; on developer machines, the install script runs as part of `uv sync`). The PDF renderer uses these bundled fonts via WeasyPrint's `@font-face` rules — never the system fonts.
- T-201 also pins **renderer native dependencies**: WeasyPrint's underlying Pango/Cairo versions (pinned via the Docker image on Linux; via `pyfribidi` + `cairocffi` wheels on Windows where available). Where native parity is impossible (Windows lacks a perfect WeasyPrint native stack), tests verify **semantic identity** (same content, same field ordering, same content hashes) rather than byte identity.
- T-802 adds tests for both byte-identity (Linux) and semantic-identity (Windows). `docs/rendering_determinism.md` documents the platform expectations.

### M3-06 — Roadmap Phase 13 stale "authorisation declared" wording. **Accepted.**

**v1.3 correction.** Replace `ROADMAP.md` Phase 13 text "only when authorisation declared" with "only when administrator-granted `AuthorisationProfile` is verified-and-current, an acceptable `ScreeningCompleted` verdict has been observed, and the required `RiskAdvisoryAcknowledged` chain is complete."

### M3-07 — `GatePredicateRegistry` lacks migration/versioning. **Accepted.**

**v1.3 correction.** Add to T-309 (skeleton):

- Each gate predicate carries a `predicate_version: PredicateVersion` (semver-like) and a `predicate_content_hash` derived from the predicate's source.
- `DerivationEnvironment` is extended with `gate_predicate_versions: dict[GateName, PredicateVersion]` and `gate_predicate_content_hashes: dict[GateName, ContentHash]`.
- Replay of an older session **uses the predicate version stored in the session's `DerivationEnvironment`**, not the current predicate. T-310b's replay tests include a `test_replay_with_old_predicate_version` fixture.
- Predicate version bumps are governance-controlled: changing a gate predicate emits a `GatePredicateVersionBumped` governance event (signed `DecisionRecord` by Administrator + scientific-advisor review).

### M3-08 — `TASK_BOARD.md` arithmetic drift. **Accepted.**

**v1.3 correction.** Regenerate `TASK_BOARD.md` cumulative count from the canonical task manifest (`docs/task_manifest.yaml`, generated by `tools/task_manifest_generator.py`). Add a header note: "Counts derived from `docs/task_manifest.yaml`; do not edit manually."

## Scientific soundness and engineering rationality — three-role concurrence

`/scientific-advisor`: "B3-03 and B3-06 are the most consequential for scientific safety. The H2-03 fix in v1.2 was over-corrected — making governance events reference-only broke the requirement that the governance stream is itself the immutable approval trace. v1.3's correction (embed full signed payloads) restores FR-ADV-06 without re-introducing the duplication problem (the value-object **type** remains owned by `domain.types.risk_advisory`; the event **payload** is a canonical snapshot of the value). B3-06's review queue is the safety-recovery path: the gate must block dangerous SOP rendering, but blocked users must be routed into auditable admin review, not into an error state. v1.3's T-315 closes the loop. B3-04 profile signatures + B3-05 SOP-template signed writes complete the institutional-integrity story."

`/architect`: "B3-01 is the structural defect that v1.2 hid behind 'admin-handler in admin-service process only'. The composition root was passing the raw `audit_log` to engine-process governance services — that contradicts the persistence claim. v1.3's `AuditAppendPort` broker pattern is the right architectural primitive: it separates audit-append authority from authorisation-store write authority. Engine processes hold `AuditAppendPort`; admin-service processes hold `AuthorisationAdminWritePort`. Both write the audit chain through the same `AuditKeyProvider`. B3-02's T-312 split + reordering fixes the Phase 3 cycle. T-309 identity model 1 (T-309 only, sub-deliverables inline) is the right answer — it matches the existing T-303/T-308/T-703 pattern."

`/dev-orchestrator`: "B3-07 is the same defect class as v1.2's H2-07 (test before owning task); B3-08 is the natural cleanup after splitting T-309. H3-01/H3-07/M3-08 are about generating from a canonical manifest rather than hand-editing — v1.3 introduces `docs/task_manifest.yaml` and `docs/port_manifest.yaml` to make these gates manifest-driven. H3-03's Phase 13 expansion is overdue — T-1301..T-1303 were sketches in v1.0 and have been accumulating delegated work; v1.3 makes them concrete."

## Summary table

| Finding | Severity | Verdict | v1.3 change action |
|---|---|---|---|
| B3-01 | Blocking | Accepted | New **T-313** `AuditAppendPort` broker; composition root injects broker into governance services (not raw `AuditLog`); persistence table shows two writers (engine-process broker + admin-service handler), both through the same HMAC chain |
| B3-02 | Blocking | Accepted | T-312 split into **T-312a** (protocol + test provider, Phase 3 early) + **T-312b** (production keystores, Phase 3 late); Phase 3 order: T-307 → T-312a → T-308 → T-309 → T-310 → T-311 → T-312b → T-313 → T-314 → T-315 → T-316 |
| B3-03 | Blocking | Accepted | T-305 revised: governance events **embed** full canonical signed payload (not references); FR-ADV-06 governance stream is the durable approval trace; static test asserts no reference-only governance event |
| B3-04 | Blocking | Accepted | T-304 adds `profile_signature` + `profile_signature_key_version`; T-310d verifies on load; T-311 signs on write; new **T-314** `AuthorisationProfileSigner` + `AuthorisationProfileVerifier` ports + adapters |
| B3-05 | Blocking | Accepted | New **T-316** `SopTemplateAdminWritePort` + `SopTemplateReadPort` + `SopTemplateBootstrapPort` + SQLite store with signatures + signed governance events; T-803 consumes read port only; admin writes through T-316 |
| B3-06 | Blocking | Accepted | New **T-315** `app.review_queue` + `AuthorisationRequest` service; FR-PROTO-SOP-09 + FR-AUTH-07/12 fulfilled; T-806b routes blocked sessions to the queue; Phase 11 surfaces commands via admin-service IPC |
| B3-07 | Blocking | Accepted | `test_worker_pool_factory.py` removed from T-205; moved to T-502; T-205 keeps only a minimal `test_spawn_context_available.py` probe |
| B3-08 | Blocking | Accepted | T-309 model 1: single task heading; sub-deliverables (a)/(b) documented inline; `#### 2.3.9a` / `#### 2.3.9b` headings removed |
| H3-01 | High | Accepted | T-204 rewritten manifest-driven only; adds `task_acceptance_completeness_check.py`, `architecture_manifest_generator.py`, `docs/module_manifest.yaml` (generated) |
| H3-02 | High | Accepted | `BlockVendorSubmission` split: T-1001 owns vendor-profile portion, T-1002 owns screening-verdict portion, T-903 consumes both |
| H3-03 | High | Accepted | T-1301/T-1302/T-1303 expanded with explicit SOP, fixture lists, acceptance criteria, traceability |
| H3-04 | High | Accepted | Legacy Phase 8/9 blocks moved to new `ROADMAP.md` Appendix A with `Legacy-Pre-v1.2-` prefix |
| H3-05 | High | Accepted | `README.md` updated to v1.3; four-audit chain + v1.3 task count |
| H3-06 | High | Accepted | § 7.3 library-mode Round-3 paragraph rewritten: batched `ScreeningCompleted` events are design events |
| H3-07 | High | Accepted | Appendix C row for T-805 removed; header note marks the table as generated from `docs/task_manifest.yaml` |
| H3-08 | High | Accepted | `rule-fixture-coverage-check` is `enforced` at T-405 verification / Phase 4 exit; deferrals require explicit `deferred_with_reason` + sign-off |
| H3-09 | High | Accepted | New **T-1103** admin-service executable boundary + IPC (named pipe / Unix socket) + mutual authentication |
| H3-10 | High | Accepted | New `DeveloperBootstrapPrincipal` sub-type; T-311 mint/modify/revoke uses `AdminPrincipal | DeveloperBootstrapPrincipal`; post-bootstrap restrictions tested |
| H3-11 | High | Accepted | T-806a `AdvisoryWarningPresented` schema explicit (FR-ADV-02 fields); recipient-role constraint validated |
| M3-01 | Moderate | Accepted | T-201 distinguishes `[tool.uv.dependency-groups]` (`dev` only) from `[project.optional-dependencies]` (all others); acceptance commands explicit |
| M3-02 | Moderate | Accepted | T-201 determinism job in `not_implemented` lifecycle until T-1301 fixtures exist |
| M3-03 | Moderate | Accepted | Appendix D adds mandatory YAML acceptance schema; brief skeleton extended |
| M3-04 | Moderate | Accepted | `test_port_inventory.py` allows manifest-driven port additions via `docs/port_manifest.yaml` |
| M3-05 | Moderate | Accepted | T-201 + T-802 add canonical-font packaging + native-renderer pinning; Linux byte-identity / Windows semantic-identity expectations |
| M3-06 | Moderate | Accepted | `ROADMAP.md` Phase 13 text replaces "authorisation declared" with full administrator-granted-profile-plus-screening-plus-acknowledgement chain |
| M3-07 | Moderate | Accepted | T-309 adds gate predicate versioning; `DerivationEnvironment` extended with version + content-hash maps; replay test for older predicate versions |
| M3-08 | Moderate | Accepted | `TASK_BOARD.md` regenerated from `docs/task_manifest.yaml`; header note says counts are manifest-derived |

**Sign-off:** Three roles unanimously approve v1.3.

`/architect`: "v1.3's `AuditAppendPort` broker, T-312 split, profile-signing ports, SOP-template admin ports, and review-queue service close the operational security boundary defects that v1.2 left. The single `T-309` identity restores task-counting determinism. Approved."

`/scientific-advisor`: "Governance events now embed signed payloads (the immutable approval trace). Profile signatures + SOP-template signatures + review queue + AdvisoryWarningPresented schema make the institutional-integrity story complete and auditable. Approved."

`/dev-orchestrator`: "Manifest-driven module coverage + task-acceptance YAML + port manifest + task manifest make the QC layer canonical. T-1103 admin-service IPC, T-1301..T-1303 expansion, README + ROADMAP synchronisation finalise the contributor-facing surface. The plan is implementation-ready. Approved."

---

*End of CODING_AGENDA_Third_Round_Audit_Response.md.*
