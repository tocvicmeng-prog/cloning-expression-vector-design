# Third-Round Audit of CODING_AGENDA.md v1.2

**Date:** 2026-05-14  
**Auditor stance:** senior software architect, experienced coder, software quality-control reviewer, adversarial falsification reviewer.  
**Primary file audited:** `CODING_AGENDA.md` v1.2.  
**Required prior input read:** `audit report/CODING_AGENDA_Second_Round_Audit_Response.md`.  
**Reference documents checked:** `ARCHITECTURE.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, and `TASK_BOARD.md`.

## Executive Verdict

`CODING_AGENDA.md` v1.2 is a substantial improvement over v1.1. The second-round fixes were mostly propagated through the agenda: Phase 9 is split into 9a/9b, the final export is moved after screening/authorisation/SOP rendering, T-311 and T-312 were added, T-805 was split into design-plan and SOP orchestrators, event ownership was corrected in the main wiring table, the CI lifecycle table is better, and the dashboard has a lifecycle column.

However, v1.2 is still **not implementation-ready**. The remaining defects are more subtle than v1.1's defects, but several are structurally important. The largest problems are:

- the audit-log write path is internally contradictory;
- T-310/T-311 use `AuditKeyProvider` before T-312 implements it;
- governance events were changed to reference-only payloads without a durable value-object store;
- `AuthorisationProfile` institutional signatures are not planned despite FR-AUTH-10;
- SOP-template admin writes have no write port or persistence model;
- the required administrator review queue and user profile-extension workflow are missing;
- Phase 2 still contains tests for a Phase 5 implementation (`WorkerPoolFactory`);
- task counting is ambiguous around `T-309`, `T-309a`, and `T-309b`.

Severity count:

| Severity | Count | Meaning |
|---|---:|---|
| Blocking | 8 | Must be corrected before Phase 2/3 implementation begins or the scaffold will encode incorrect security, audit, or task-lifecycle behavior. |
| High | 11 | Likely to cause major rework, false QC confidence, or failed acceptance if not fixed before the owning phase. |
| Moderate | 8 | Important cleanup to prevent drift, ambiguity, brittle CI, or poor environment portability. |

## Method

I applied a third-round falsification strategy:

1. Verified that every accepted item in `CODING_AGENDA_Second_Round_Audit_Response.md` is reflected in `CODING_AGENDA.md` v1.2.
2. Checked agenda behavior against `ARCHITECTURE.md` v1.5, especially event streams, audit persistence, authorisation boundaries, and safety gates.
3. Checked MUST/SHOULD obligations in `REQUIREMENTS.md`, especially FR-AUTH, FR-ADV, FR-PROTO-SOP, FR-IO, SR, and BR.
4. Checked `ROADMAP.md`, `TASK_BOARD.md`, and `README.md` for synchronization claims.
5. Parsed task headings and task IDs to identify duplicate, pseudo-task, and counting risks.
6. Re-ran the pass after identifying findings, looking for additional defects of the same class. No further distinct defect class was found beyond the findings below.

## Blocking Findings

### B3-01. Audit-log write ownership is internally contradictory

**Evidence:** In the composition root, `audit_log = SqliteAuditLog(config.audit_db, audit_key_provider)` is constructed unconditionally and passed directly to `PluginGovernance`, `AdvisoryAcknowledgementService`, `ScreeningOrchestrator`, and `AuthorisationDecisionService` (`CODING_AGENDA.md:1217-1224`, `CODING_AGENDA.md:1279-1290`). But the persistence table says the audit log writer is `app.admin_action_handler` running in the admin-service process, while the engine/application read it in read-only mode (`CODING_AGENDA.md:1392-1394`). The composition root also explicitly avoids constructing `AdminActionHandler` in the user-facing engine process (`CODING_AGENDA.md:1304-1322`, `CODING_AGENDA.md:1362`).

**Impact:** Governance services must write audit entries, but v1.2 gives them either direct audit-log access, which bypasses the claimed admin-handler-only write path, or read-only access, which makes their acceptance impossible. The plan says "every governance-event-writing application service appends its own audit row through the same handler" (`CODING_AGENDA.md:1393`), but that handler is absent in the engine process.

**Required correction:** Split audit writing from authorisation writing. Add a dedicated `AuditAppendPort` or audit broker service that permits append-only audit entries from authorised application services without giving them authorisation-store write access. Document which process owns it, how it authenticates service callers, and how it preserves append-only HMAC-chain integrity.

### B3-02. T-310 and T-311 depend on T-312 before T-312 exists

**Evidence:** T-310 is headed as depending on T-312 `AuditKeyProvider` (`CODING_AGENDA.md:590-601`) but T-312 is scheduled after T-310 (`CODING_AGENDA.md:619-644`). T-311 writes audit entries through `AuditLog` plus `AuditKeyProvider` (`CODING_AGENDA.md:612-617`) but also runs before T-312. T-312 then defines the actual `AuditKeyProvider` protocol and adapters (`CODING_AGENDA.md:619-628`).

**Impact:** The Phase 3 order is not executable. T-310 cannot pass HMAC tamper-detection or audit-key-absent acceptance before the key-provider contract and adapters exist. T-311 cannot pass its admin audit-chain integration test before the same provider exists.

**Required correction:** Move T-312 before T-310/T-311, or split T-312 into T-312a in Phase 2/early Phase 3 for the protocol plus test key provider, and T-312b for production keystore adapters. Then T-310/T-311 can depend on T-312a explicitly.

### B3-03. Governance events were made reference-only without a durable value-object store

**Evidence:** T-305 states that governance events carry only references to `RiskAdvisoryAcknowledgement`, `DecisionRecord`, and `RoleSnapshot`; full value objects are resolved via the persistence layer at replay or audit time (`CODING_AGENDA.md:493-500`). But no task defines a durable `RiskAdvisoryAcknowledgementStore`, `DecisionRecordStore`, or `RoleSnapshotStore`. T-806a emits `RiskAdvisoryAcknowledged` / `Declined` / `Escalated` events (`CODING_AGENDA.md:881-889`), and T-806b consumes the chain of `RiskAdvisoryAcknowledged` events (`CODING_AGENDA.md:955-964`), but the plan does not say where the full signed acknowledgement payload is persisted.

This conflicts with FR-ADV-06, which requires the full approval trace to be persisted in the immutable governance event stream (`REQUIREMENTS.md:386`), and with architecture text saying `ReviewerSignedOff` carries the signed `DecisionRecord` (`ARCHITECTURE.md:2161-2168`).

**Impact:** Replay and audit can encounter dangling references. A governance event stream that only contains references is not itself the immutable approval trace required by the requirements. The system can pass event round-trip tests while losing the signed material needed for legal/audit review.

**Required correction:** Either embed immutable canonical snapshots of the signed value objects in the governance events, or add an explicit content-addressed immutable value-object store with its own append-only integrity checks, event references, export inclusion rules, and replay tests. Do not allow plain database references without a tamper-evident payload path.

### B3-04. `AuthorisationProfile` institutional signature is missing from implementation ownership

**Evidence:** REQUIREMENTS FR-AUTH-02 requires each `AuthorisationProfile` to include an institutional signature, and FR-AUTH-10 requires tampered profiles to fail verification on load (`REQUIREMENTS.md:363`, `REQUIREMENTS.md:371`). T-304 only says to implement `AuthorisationProfile` with `profile_content_hash` (`CODING_AGENDA.md:473-484`). T-310/T-311 cover database read/write and audit-chain entries, but do not explicitly sign profiles or verify profile signatures on read/write (`CODING_AGENDA.md:590-617`).

**Impact:** A tampered `authorisation.sqlite` profile could be detected by filesystem/HMAC/audit checks in some scenarios, but the profile object itself lacks the required institutional signature invariant. FR-AUTH-10 would not have an owning task or unit test.

**Required correction:** Add profile signature fields and verification to T-304/T-310/T-311. The signature should bind the full canonical profile payload, profile version, subject user, issuer principal, validity interval, and revocation metadata. Add signature-tamper tests and ensure `AuthorisationReadPort.get()` fails closed when verification fails.

### B3-05. SOP-template admin writes have no write port, adapter, or persistence model

**Evidence:** T-203 lists `SopTemplateLibrary` only as a catalogue port, not a split read/write/admin port (`CODING_AGENDA.md:382`). T-311 defers SOP-template admin writes to T-803 (`CODING_AGENDA.md:616`). T-803 adds `src/app/admin_action_handler/sop_template_writes.py` but still consumes `SopTemplateLibrary`, which the composition root creates through `YamlSopTemplateLoader(...).load()` (`CODING_AGENDA.md:940-947`, `CODING_AGENDA.md:1194`, `CODING_AGENDA.md:1307-1311`). No `SopTemplateAdminWritePort`, schema, signature model, atomic write path, review workflow, or persistence table row exists.

**Impact:** The plan claims `app.admin_action_handler` is the sole write path to institutional SOP templates, but no safe write interface exists. A developer would either mutate YAML files ad hoc or overload the read-only loader, bypassing the same separation-of-duties discipline the authorisation store now has.

**Required correction:** Add split SOP-template ports: read, admin-write, and possibly bootstrap/import. Add a persistence adapter with signatures, version history, atomic writes, schema validation, audit events, and denial tests for User/Reviewer. T-803 should consume approved templates, not invent the write persistence model inside the SOP renderer task.

### B3-06. Required administrator review queue and user extension request workflow are missing

**Evidence:** FR-PROTO-SOP-09 requires a clear "operational protocol withheld pending administrator approval" notice and a structured request to the administrator review queue when SOP cannot render (`REQUIREMENTS.md:327`). FR-AUTH-07 repeats the review-queue requirement (`REQUIREMENTS.md:368`). FR-AUTH-12 requires users to submit extension requests to the Administrator without auto-granting (`REQUIREMENTS.md:373`). Searches of `CODING_AGENDA.md` show no `app.review_queue`, `AuthorisationRequest`, profile-extension request task, queue persistence, or admin triage workflow; the only "extension" language is SOP-template write deferral (`CODING_AGENDA.md:946`, `CODING_AGENDA.md:1310`, `CODING_AGENDA.md:1903`).

**Impact:** The gate can block, but the required recovery workflow is missing. This is a user-facing and safety-facing requirement: blocked users must be routed into an auditable admin review process rather than being left with only an error.

**Required correction:** Add an `app.review_queue` / `app.authorisation_request_service` task, queue persistence, typed events (`AuthorisationExtensionRequested`, `ReviewQueueItemCreated`, `ReviewQueueItemResolved`), CLI/API/UI surfaces, and tests that blocked SOP rendering creates exactly one pending request without granting access.

### B3-07. Phase 2 platform tests depend on a Phase 5 implementation

**Evidence:** T-205 tests `WorkerPoolFactory` semantics (`CODING_AGENDA.md:420-435`), but T-502 owns the actual `WorkerPoolFactory` implementation in Phase 5 (`CODING_AGENDA.md:715-731`). T-205 acceptance requires every platform test to be green on Ubuntu and Windows (`CODING_AGENDA.md:434`).

**Impact:** Phase 2 cannot pass as written unless T-205 implements a production component owned by T-502 or creates a throwaway duplicate. This repeats the earlier file-watch scheduling issue, but with multiprocessing infrastructure.

**Required correction:** Move `test_worker_pool_factory.py` to T-502, or make T-205 test only a minimal platform probe independent of the production factory. Phase 2 should establish environmental assumptions; Phase 5 should verify the actual validation-worker implementation.

### B3-08. Task identity and task counts are ambiguous around T-309/T-309a/T-309b

**Evidence:** The agenda has a parent heading `T-309`, plus sub-headings `T-309a` and `T-309b` (`CODING_AGENDA.md:566-587`). `TASK_BOARD.md` says Phase 3 has 12 tasks and lists `T-301..T-312`, while also saying T-309 split into T-309a and T-309b (`TASK_BOARD.md:39`). The cumulative line says v1.2 adds four main tasks but net +3 after removing T-805, and still reports 61 main tasks (`TASK_BOARD.md:53`). The parser-visible task headings total 61 unique IDs only if `T-309`, `T-309a`, and `T-309b` are all treated as separate task IDs.

**Impact:** The duplicate-heading problem was fixed, but a new pseudo-task-count problem was introduced. Automated task-board regeneration, context-budget assignment, module coverage, and phase exit counts can disagree about whether T-309 is a parent, an executable task, or three tasks.

**Required correction:** Pick one model:

- T-309 is the only task, with sub-deliverables T-309a/T-309b not written as task IDs; or
- T-309a and T-309b are real tasks, and T-309 is only prose without a task heading; or
- all three are real tasks with counts and acceptances updated accordingly.

## High Findings

### H3-01. T-204 still contains stale module-coverage instructions and omits new gate files

**Evidence:** T-204's file list does not include `task_acceptance_completeness_check.py` or `tools/architecture_manifest_generator.py` (`CODING_AGENDA.md:406-418`), even though the CI table adds `task-acceptance-completeness-check` (`CODING_AGENDA.md:1427-1429`). T-204 SOP item 5 still says `module_coverage_check.py` parses `ARCHITECTURE.md` and `CODING_AGENDA.md` prose and flips after T-310 (`CODING_AGENDA.md:414`), while the v1.2 acceptance says it parses `docs/module_manifest.yaml` instead (`CODING_AGENDA.md:416-417`).

**Impact:** The implementation brief for the gate is contradictory. A developer could implement the old Markdown parser and still appear to satisfy part of T-204. The new acceptance-completeness gate has no concrete file ownership.

**Required correction:** Rewrite T-204 files and SOP so the only accepted design is manifest-driven. Add explicit files for `task_acceptance_completeness_check.py`, `architecture_manifest_generator.py`, generated manifest schema, and tests for stale-manifest detection.

### H3-02. `BlockVendorSubmission` is not fully wired to vendor-profile rejection

**Evidence:** Architecture says `BlockVendorSubmission` fires when a vendor profile rejects the sequence or when screening is not acceptable for orders (`ARCHITECTURE.md:600-601`). T-309b says the predicate is activated in Phase 10 by T-1002 using screening verdict plus vendor policy (`CODING_AGENDA.md:581-587`). T-1001 implements vendor adapters (`CODING_AGENDA.md:982-985`), while T-1002 wires `BlockVendorSubmission` only per verdict (`CODING_AGENDA.md:987-996`).

**Impact:** Vendor feasibility failures can fall outside the gate activation owner. The system may block by screening verdict but still prepare vendor submissions for constructs that fail vendor length, GC, repeat, adapter, or product-format constraints.

**Required correction:** Split the predicate inputs explicitly: T-1001 activates vendor-profile feasibility portions; T-1002 activates screening-verdict portions; T-903 consumes both before `VendorSubmissionPrepared`. Add tests where vendor rejects but screening is clear.

### H3-03. Phase 13 UAT cards are too thin for the work moved into them

**Evidence:** T-606 moved full happy-path acceptance to T-1301 (`CODING_AGENDA.md:789-801`), and the adversarial suite now claims extra audit-key and replay scenarios (`CODING_AGENDA.md:1502-1505`). But Phase 13 task cards only list sparse file paths and no SOP or acceptance detail (`CODING_AGENDA.md:1026-1038`). T-1302's file list omits audit-key, replay-integrity, and governance-reference scenarios (`CODING_AGENDA.md:1032-1034`).

**Impact:** Critical end-to-end evidence is delegated to Phase 13 but not specified there. This creates a false sense that earlier tasks have moved risk downstream when the downstream task does not own it concretely.

**Required correction:** Expand T-1301/T-1302/T-1303 with explicit SOP, required fixtures, acceptance criteria, and traceability to every deferred full-path and adversarial scenario.

### H3-04. Roadmap legacy sections still contain active-looking stale deliverables and exit criteria

**Evidence:** `ROADMAP.md` marks old Phase 8 and Phase 9 sections as legacy, but retains full `### Deliverables` and `### Exit criteria` under those headings (`ROADMAP.md:275-305`, `ROADMAP.md:357-380`). Those legacy sections include pre-v1.2 export and SOP/auth wording.

**Impact:** Humans and scripts can still parse those sections as active. The roadmap now has both binding and legacy phase content in the main flow, which weakens the "regenerated" claim.

**Required correction:** Move legacy Phase 8 and Phase 9 text to an appendix outside the phase sequence, or remove it. If retained, mark every heading with a non-phase prefix that task parsers cannot mistake for an active phase.

### H3-05. README is stale and still advertises CODING_AGENDA v1.1

**Evidence:** `README.md` still describes `CODING_AGENDA.md` as "Finalised v1.1" and lists only the first-round agenda audit changes (`README.md:24`). It does not mention v1.2, T-311, T-312, Phase 9a/9b, T-805a/T-805b, or the second-round response.

**Impact:** README is contextual rather than binding, but it is the repository entry point. A contributor starting there will get the wrong phase model and task count.

**Required correction:** Update README to v1.2 and include the second-round audit response, Phase 9 split, new admin/audit-key tasks, and new task count.

### H3-06. Internal adversarial review text contradicts v1.2 event-stream ownership

**Evidence:** The main event-stream table now puts `ScreeningCompleted` in the design stream (`CODING_AGENDA.md:1364-1374`). But the retained internal review text still says library mode emits "batched governance events" and "one `ScreeningCompleted` event per batch" in the governance event stream (`CODING_AGENDA.md:1732-1734`).

**Impact:** The plan still contains two event-stream semantics for library mode. This matters because library screening can involve hundreds or thousands of results, and replay determinism depends on correct stream ownership.

**Required correction:** Rewrite the library-mode review text so batched `ScreeningCompleted` events are design events, with governance stream carrying only reviewer/admin decision records and advisory events.

### H3-07. Context-budget appendix still contains the removed `app.protocol_orchestrator` T-805

**Evidence:** Appendix C still lists `app.protocol_orchestrator` (T-805) (`CODING_AGENDA.md:1954`) even though v1.2 says T-805 was removed and split into T-805a/T-805b (`CODING_AGENDA.md:17`, `CODING_AGENDA.md:871-880`, `CODING_AGENDA.md:949-953`).

**Impact:** The budget table no longer matches the canonical task list. This can cause work assignment to an obsolete task and distort context-budget planning.

**Required correction:** Remove the T-805 row and ensure the budget table is generated from the same canonical task manifest as `TASK_BOARD.md`.

### H3-08. Rule-fixture gate lifecycle conflicts with Phase 4 exit criteria

**Evidence:** T-405 says Phase 4 exit fails if any rule lacks fixtures (`CODING_AGENDA.md:678-696`). The CI table says `rule-fixture-coverage-check` is informational from Phase 4 exit and enforced thereafter (`CODING_AGENDA.md:1430`).

**Impact:** The gate cannot be both informational at Phase 4 exit and the reason Phase 4 exit fails. This weakens scientific QC for rule curation.

**Required correction:** Make `rule-fixture-coverage-check` enforced at T-405 verification / Phase 4 exit. If some rules are intentionally deferred, require explicit `deferred_with_reason` metadata and scientific-advisor sign-off.

### H3-09. Admin-service process boundary lacks an implementation task for IPC/authentication

**Evidence:** v1.2 introduces a separate admin-service process (`CODING_AGENDA.md:1226-1238`, `CODING_AGENDA.md:1362`, `CODING_AGENDA.md:1402`). T-311 only provides a programmatic shim `tools/admin_shell.py` for Phase 3 testing (`CODING_AGENDA.md:615`). Phase 11 CLI/API task cards mention admin commands but do not specify how they communicate with or authenticate to the admin-service process (`CODING_AGENDA.md:998-1008`).

**Impact:** The separation-of-duties boundary is conceptually strong but not executable. Without IPC/authentication design, implementers may collapse admin and user paths back into one process to make CLI/API commands work.

**Required correction:** Add a task for admin-service executable boundary: local socket or named pipe, mutual authentication, principal binding, CLI/API routing, denial/audit tests, and deployment instructions.

### H3-10. Developer authority for regular mint/modify/revoke remains ambiguous

**Evidence:** T-311 allows `AdminPrincipal | DeveloperPrincipal` for `mint_profile`, `modify_profile`, and `revoke_profile` (`CODING_AGENDA.md:612-617`). Architecture's permissions matrix says Developer can mint/modify/revoke only as "system bootstrap" and does not auto-inherit Administrator (`ARCHITECTURE.md:655-679`). Requirements FR-AUTH-04 allows AdminPrincipal or DeveloperPrincipal, but the architecture narrows Developer semantics to bootstrap/system-level use.

**Impact:** Developer privilege can become broader than intended, especially if deployed in institutional mode. This is a governance risk, not just a type issue.

**Required correction:** Distinguish `DeveloperBootstrapPrincipal` or bootstrap-mode operations from ordinary institutional administration. Add tests proving Developer cannot modify/revoke ordinary profiles after bootstrap unless an explicit installation policy grants that capability.

### H3-11. `AdvisoryWarningPresented` is logged, but recipient/principal constraints are under-specified

**Evidence:** FR-ADV-02 requires presentation events to record design session, construct version, report hash, advisory IDs, presentation surface, and recipient principal ID (`REQUIREMENTS.md:382`). T-806a only says every CLI/API/UI render emits `AdvisoryWarningPresented` (`CODING_AGENDA.md:885-889`), without specifying the required fields, recipient-role validation, or tests for all surfaces.

**Impact:** The event can exist but lack the fields required to prove the administrator actually received the warning. This undercuts the v1.5 active-advisory mitigation.

**Required correction:** Expand T-806a with exact `AdvisoryWarningPresented` schema fields, recipient role constraints, and one test per presentation surface.

## Moderate Findings

### M3-01. T-201 still conflates dependency groups and extras

**Evidence:** T-201 calls optional dependency sets "dependency groups (uv extras)" (`CODING_AGENDA.md:328`) and uses `uv sync --only-group core --only-group dev` as acceptance (`CODING_AGENDA.md:363`). Groups and extras are distinct packaging concepts; the plan should not rely on ambiguous terminology.

**Impact:** Bootstrap implementation may encode the wrong pyproject structure, creating brittle install profiles.

**Required correction:** Specify the exact `pyproject.toml` sections and exact `uv` commands for groups versus optional extras. Validate the commands in T-201 on a minimal scaffold.

### M3-02. T-201 says every matrix cell runs a container determinism check before UAT fixtures exist

**Evidence:** T-201's CI matrix says jobs per cell include "container-based determinism check" (`CODING_AGENDA.md:359`). The CI lifecycle table says determinism is informational until Phase 13 and only enforced after UAT examples exist (`CODING_AGENDA.md:1414`).

**Impact:** The bootstrap task may attempt to run a determinism job with no examples or canonical artefacts.

**Required correction:** In T-201, create a no-op determinism scaffold or mark the determinism job absent/informational until fixtures exist. Align the T-201 acceptance with the lifecycle table.

### M3-03. `task-acceptance-completeness-check` requires YAML, but the task template has no YAML block

**Evidence:** The CI table says the new gate requires every task brief to have a machine-readable acceptance YAML block (`CODING_AGENDA.md:1428`). Appendix D's task brief skeleton contains only free-form Markdown sections and no YAML block (`CODING_AGENDA.md:1979-2008`).

**Impact:** The new gate will fail its own templates or force implementers to invent a local format.

**Required correction:** Add the exact YAML schema to Appendix D and to T-204 tests.

### M3-04. The port inventory is overly closed for a plugin-oriented architecture

**Evidence:** `tests/ports/test_port_inventory.py` fails if any port is added that is not listed in the agenda's catalogue (`CODING_AGENDA.md:402`). The architecture explicitly supports plugin contracts and future swappable adapters.

**Impact:** This is good for drift detection but poor for extensibility. A legitimate plugin-driven port addition will fail until the agenda is edited.

**Required correction:** Treat unlisted ports as a failure only if they lack a manifest entry, owner, and architecture/requirements reference. Do not make the agenda text the only possible source of truth for future ports.

### M3-05. Renderer determinism policy is named but not operationalized across platforms

**Evidence:** T-802/T-803/T-903 add renderer files and refer to `docs/rendering_determinism.md` (`CODING_AGENDA.md:856-863`, `CODING_AGENDA.md:940-947`, `CODING_AGENDA.md:970-978`). The plan mentions WeasyPrint and pinned fonts but does not assign font packaging, native-library availability, or Windows/Linux rendering parity tests to a bootstrap or renderer task.

**Impact:** PDF byte determinism is notoriously fragile. The plan can pass on Linux and fail on Windows due to font or native renderer differences.

**Required correction:** Add renderer environment setup to T-201/T-802, include font files or package installation, and define platform-specific expectations for byte-identical versus semantically identical PDFs.

### M3-06. Roadmap Phase 13 still uses stale "authorisation declared" wording

**Evidence:** Roadmap Phase 13 says gated SOP is rendered "only when authorisation declared" (`ROADMAP.md:507-511`). The correct architecture is administrator-minted authorisation plus screening plus advisory acknowledgement.

**Impact:** This is a wording defect, but it is in an acceptance UAT section and can lead to tests that validate declaration rather than grant verification.

**Required correction:** Replace "authorisation declared" with "administrator-granted authorisation profile, acceptable screening verdict, and required advisory acknowledgement chain observed."

### M3-07. `GatePredicateRegistry` activation lacks migration/versioning guidance

**Evidence:** T-309a registers all safety gates as pending, and T-309b activates predicates in later phases (`CODING_AGENDA.md:570-587`). There is no plan for how replay handles sessions created under earlier predicate versions or how predicate-version hashes enter `DerivationEnvironment`.

**Impact:** Replaying old sessions after a gate predicate changes can produce different blocked/allowed states without an explicit migration boundary.

**Required correction:** Version gate predicates, include predicate-version hashes in `DerivationEnvironment`, and add replay tests for old sessions under changed predicate versions.

### M3-08. TASK_BOARD still has minor arithmetic drift in cumulative counts

**Evidence:** `TASK_BOARD.md` says v1.2 adds four main tasks and also says net +3 after replacing T-805, while reporting 61 main tasks (`TASK_BOARD.md:53`). Because T-309 was also split into T-309a/T-309b while the parent remains visible, the arithmetic is not self-evident.

**Impact:** This is lower severity than B3-08, but it is another symptom that task counting is not machine-derived.

**Required correction:** Generate the cumulative count from a single task manifest and show the exact delta calculation.

## Scientific Soundness and Engineering Rationality Assessment

v1.2 gets the high-level scientific safety sequence right: screening before authorisation, authorisation before SOP, SOP before final export. It also correctly removes BR-14 from structural predicates and moves it into the authorisation gate.

The remaining scientific risks are workflow-completeness and auditability:

- blocked users are not routed through the required administrator review queue;
- advisory acknowledgement events may not contain the full immutable signed payload;
- SOP template approval and mutation are not represented as a first-class signed/admin-controlled store;
- `AuthorisationProfile` signatures are missing from the coding plan.

These are important because they determine whether a safety decision is auditable and replayable, not merely whether the right screen is shown.

## Quality-Control Robustness Assessment

The v1.2 QC plan is stronger than v1.1 but still has inconsistencies:

- task and phase counting are not fully canonical;
- T-204 mixes old Markdown-parsing instructions with new manifest-driven instructions;
- new gates are listed in CI but not in T-204's file deliverables;
- rule-fixture lifecycle state conflicts with Phase 4 exit requirements;
- Phase 13 UAT task cards are underspecified;
- README and retained roadmap legacy sections undermine contributor orientation.

## Target Environment Adaptability Assessment

The plan handles Windows/OneDrive better than v1.1, especially with `SyncLikePath` and `ActiveSyncPath`. But there are still adaptation gaps:

- WorkerPoolFactory tests are scheduled before the factory exists;
- renderer determinism needs native dependency and font packaging plans;
- uv group/extra syntax needs exact validation;
- admin-service IPC/authentication must be concrete on Windows, including named-pipe or local-socket behavior;
- audit-key providers need clear fallback behavior when DPAPI/keyring APIs are unavailable in CI.

## Recommended Correction Sequence

1. Fix the security/audit foundations first: audit append ownership, T-312 ordering, profile signatures, governance event payload persistence, and SOP-template write ports.
2. Add the missing admin review queue/profile-extension workflow.
3. Normalize the task manifest: resolve T-309/T-309a/T-309b identity, remove stale T-805 budget row, regenerate counts.
4. Rewrite T-204 so the manifest-driven gates and new task-acceptance gate have exact file ownership and no stale prose-parser instructions.
5. Expand Phase 13 UAT cards and align Roadmap/README.
6. Move Phase 2 tests that depend on later implementations to their owning tasks.

## Overall Conclusion

v1.2 fixes most v1.1 synchronization failures, but the new security and audit machinery is not yet coherent enough to start implementation. The plan now needs a targeted v1.3 pass focused less on phase ordering and more on operational security boundaries: audit append semantics, immutable governance payloads, signed authorisation profiles, SOP-template write governance, review queue workflows, and canonical task identity. Once those are corrected, the agenda will be much closer to implementation-ready.

