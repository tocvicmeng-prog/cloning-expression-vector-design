# Fifth-Round CODING_AGENDA.md Audit Report

**Subject:** `CODING_AGENDA.md` v1.4  
**Prior response reviewed:** `audit report/CODING_AGENDA_Fourth_Round_Audit_Response.md`  
**Supporting documents consulted:** `ARCHITECTURE.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, `TASK_BOARD.md`  
**Audit date:** 2026-05-14  
**Reviewer stance:** senior software architect, experienced coder, and software quality-control auditor applying exhaustive adversarial falsification.

## Executive Verdict

`CODING_AGENDA.md` v1.4 is **not yet implementation-ready**.

The fourth-round response correctly identified the major v1.3 defect pattern: the new security and governance primitives were added as task cards but were not fully propagated into physical task order, wiring, CI gates, manifests, and supporting documents. v1.4 makes several good conceptual moves: single-writer audit service, protocol/fake split tasks, admin-service IPC split, `SopTemplateReadPort`, explicit `DecisionRecordVerifier`, and wider security gates.

However, the actual v1.4 document still contains blocking executable contradictions. The most serious problem is that the declared v1.4 task order at `CODING_AGENDA.md:491` was not physically applied to the Phase 3 task headings. Consumers still appear before the early protocol/fake tasks that they need. In addition, a stale unsplit `T-314` task card remains active, Phase 3/4 task counts are arithmetically wrong, the port inventory has duplicate numbering and an impossible total, and the composition root still calls an undefined `sop_template_library`.

This fifth-round audit found:

| Severity | Count | Result |
|---|---:|---|
| Blocking | 10 | Must be fixed before coding begins |
| High | 9 | Must be fixed before Phase 2/3 handoff or any security-significant implementation |
| Moderate | 6 | Should be fixed before claiming v1.5/v1.4.1 closure |

The dominant failure mode is still synchronisation drift. v1.4 describes the right architecture in summary prose, but the executable parts of the plan remain partly v1.3: headings, counts, task cards, Section 3 wiring, roadmap text, and CI gates disagree.

## Audit Method

I read the fourth-round response first, then falsified v1.4 against its accepted commitments. I checked:

- physical Section 2 heading order versus declared phase/task order;
- whether every task can pass its own acceptance criteria when executed in the physical order;
- whether split tasks (`T-313a/b`, `T-314a/b`, `T-316a/b/c`, `T-1103a/b`) are referenced consistently by consumers;
- whether Section 3 composition, persistence tables, and CI lifecycle tables are executable;
- whether task counts, port counts, task-board counts, and parser assumptions are machine-realistic;
- whether the security and scientific safety invariants still hold: screening before SOP/export, no self-authorisation, signed profile/template integrity, single audit writer, and replayable governance evidence;
- whether `ARCHITECTURE.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, and `TASK_BOARD.md` drift in ways likely to mislead implementation.

I stopped after repeated passes over task order, task cards, composition, manifests, source documents, task-board arithmetic, and security boundary claims produced no additional distinct defect classes beyond the findings below.

## Positive Confirmations

- v1.4's intent is directionally sound: protocol/fake tasks before consumers, production adapters later, and IPC boundaries for audit/admin writes are the right implementation strategy.
- Phase 10 is now physically before Phase 8b and Phase 9b, closing the previous screening-before-SOP heading-order defect.
- The single-writer audit-service model is more executable than v1.3's dual-writer audit-lock design.
- Expanding `AuditKeyProvider` to `mac()` / `verify()` instead of exposing raw key bytes is the right security move.
- Splitting admin-service IPC into `T-1103a` and `T-1103b` is the right way to let CLI/API code depend on a port instead of importing `AdminActionHandler`.

These positives do not remove the blocking defects below.

## Blocking Findings

### B5-01 - Phase 3 physical heading order still contradicts the declared v1.4 dependency order

**Evidence.**

- The declared v1.4 order says `T-312a -> T-313a -> T-314a -> T-316a -> T-308 -> T-309 -> T-310 -> T-311 -> ...` at `CODING_AGENDA.md:491`.
- The actual Phase 3 headings are still physically ordered as `T-301..T-307`, then `T-308` at `CODING_AGENDA.md:618`, `T-309` at `CODING_AGENDA.md:632`, `T-310` at `CODING_AGENDA.md:654`, and `T-311` at `CODING_AGENDA.md:668`.
- Only after those consumers do the early split tasks appear: `T-312a` at `CODING_AGENDA.md:687`, `T-313a` at `CODING_AGENDA.md:725`, `T-314a` at `CODING_AGENDA.md:764`, and `T-316a` at `CODING_AGENDA.md:848`.
- `TASK_BOARD.md:42` repeats the intended order, not the actual heading order.

**Why this is blocking.** A heading-order task manifest generator, task-board generator, or implementation agent walking Section 2 will still implement `T-310` and `T-311` before the protocol/fake tasks that their acceptance tests require. This is precisely the B4-02/B4-03/B4-05 defect class that v1.4 claims to fix.

**Required correction.**

Physically move `T-312a`, `T-313a`, `T-314a`, and `T-316a` above `T-308` in Phase 3, or make `tools/task_manifest_generator.py` use an explicit intra-phase dependency-order table and fail if the physical headings disagree. The safest correction is to do both.

### B5-02 - A stale unsplit `T-314` task card remains active in Phase 3

**Evidence.**

- v1.4 correctly adds `T-314a` at `CODING_AGENDA.md:764` and `T-314b` at `CODING_AGENDA.md:780`.
- A full unsplit v1.3 card remains active at `CODING_AGENDA.md:803`: `#### 2.3.15 T-314 - AuthorisationProfileSigner + AuthorisationProfileVerifier`.
- The stale card still owns production files also owned by `T-314b`: `institutional_signer.py`, `institutional_verifier.py`, `tools/profile_signature_verifier.py`, and security tests.
- It also has a duplicate section number: `2.3.15` is used by `T-313b` at `CODING_AGENDA.md:740` and again by stale `T-314` at `CODING_AGENDA.md:803`.

**Why this is blocking.** The stale card is a real `####` task heading. Any parser, brief generator, or implementer will treat it as an active task. It reintroduces the exact unowned/duplicate production-signer surface that the `T-314a`/`T-314b` split was meant to eliminate.

**Required correction.**

Delete the unsplit `T-314` card entirely from active Section 2. If historical context is needed, move a one-line note to the historical audit appendix, not as a `#### ... T-*` heading.

### B5-03 - Phase counts and cumulative task counts are wrong

**Evidence.**

- Phase 3 header claims "18 tasks" at `CODING_AGENDA.md:487`.
- The intended declared Phase 3 order at `CODING_AGENDA.md:491` contains 19 tasks: `T-301..T-307` (7), `T-312a/T-313a/T-314a/T-316a` (4), `T-308..T-311` (4), and `T-312b/T-313b/T-314b/T-315` (4).
- The actual Phase 3 headings contain 20 active headings because stale `T-314` is still present.
- Phase 4 header claims "6 tasks" at `CODING_AGENDA.md:865`, but the active headings include `T-401..T-406` plus `T-316b` and `T-316c`, for 8 tasks.
- A direct heading count of Section 2 produced 72 active `#### ... T-*` headings, while `TASK_BOARD.md:56` claims 71 main tasks and a net v1.4 delta of +4.
- The delta arithmetic is wrong. v1.3's four original tasks (`T-313`, `T-314`, `T-316`, `T-1103`) become nine split tasks (`T-313a/b`, `T-314a/b`, `T-316a/b/c`, `T-1103a/b`), a net +5, not +4.

**Why this is blocking.** The manifest and task-board counts are used as QC controls. If the counts are wrong before coding begins, the plan cannot reliably detect missing briefs, stale task cards, or incomplete phase exits.

**Required correction.**

After deleting stale `T-314`, set Phase 3 to 19 tasks, Phase 4 to 8 tasks, and cumulative planned tasks to 72 unless another active heading is intentionally removed. Regenerate `TASK_BOARD.md` from the same manifest source. Add a test that checks per-phase counts and total count against active headings, not hand-maintained summary prose.

### B5-04 - The port inventory has duplicate numbering, stale test expectations, and impossible arithmetic

**Evidence.**

- `T-203c` claims "Total: 49 canonical ports" at `CODING_AGENDA.md:443`.
- The arithmetic on the same line says v1.3 had 45 ports, removed one (`SopTemplateLibrary`), then added six: `SopTemplateSigner`, `SopTemplateVerifier`, `DecisionRecordVerifier`, `AdminAuditAppendPort`, `ReviewQueueAdminPort`, and `AdminServiceClientPort`. That is 45 - 1 + 6 = 50, not 49.
- Numbering collides:
  - `AuthorisationProfileSigner` is #23 and `AuthorisationProfileVerifier` is #24 at `CODING_AGENDA.md:423`.
  - `AdminServiceClientPort` is #24b at `CODING_AGENDA.md:425`.
  - `ReviewQueueStore` is #29 and `ReviewQueueAdminPort` is #30 at `CODING_AGENDA.md:429`.
  - `SequenceReader` and `SequenceWriter` are also #29 and #30 at `CODING_AGENDA.md:431`.
- The test description still says `tests/ports/test_port_inventory.py` imports "each of the 45 canonical ports above" at `CODING_AGENDA.md:445`.

**Why this is blocking.** `T-203` is the type-surface foundation for the entire build. A wrong canonical port inventory will cause either false negatives (missing ports not detected) or false positives (valid ports rejected). It also undermines `docs/port_manifest.yaml`, `test_port_inventory.py`, and downstream import-linter contracts.

**Required correction.**

Re-enumerate the port list with unique monotonic IDs. Decide whether the canonical total is 50 or whether one proposed port is intentionally not canonical. Update `test_port_inventory.py` expectations, `docs/port_manifest.yaml` schema examples, `TASK_BOARD.md`, and Appendix B from that single list.

### B5-05 - Section 3 composition root is still non-executable

**Evidence.**

- Section 3 claims it is v1.4-synchronised at `CODING_AGENDA.md:1420`.
- The composition header still says `engine.session (T-309a)` and `AuditKeyProvider port (T-312)` at `CODING_AGENDA.md:1586` and `CODING_AGENDA.md:1591`.
- The composition root says `SopTemplateLibrary + YamlSopTemplateLoader REMOVED` at `CODING_AGENDA.md:1603-1604`, and constructs `sop_template_read_port` at `CODING_AGENDA.md:1645`.
- It then calls `SopProtocolGenerator(sop_template_library)` at `CODING_AGENDA.md:1722`. `sop_template_library` is no longer defined.
- The same block still tags `SessionEngine` as `T-309a` at `CODING_AGENDA.md:1710`.
- The CI and persistence sections still reference `T-309a`, unsplit `T-314`, and unsplit `T-316` at `CODING_AGENDA.md:1854`, `CODING_AGENDA.md:1878`, `CODING_AGENDA.md:1887-1889`, and `CODING_AGENDA.md:1909-1917`.

**Why this is blocking.** Section 3 is the executable wiring blueprint. An undefined variable in the composition root is not documentation drift; it is a direct implementation defect. It will also cause implementers to pass the old template library into SOP generation, contradicting v1.4's `SopTemplateReadPort` design.

**Required correction.**

Regenerate Section 3 from the corrected manifest. Replace line `SopProtocolGenerator(sop_template_library)` with `SopProtocolGenerator(sop_template_read_port)` or an explicit constructor that consumes only `SopTemplateReadPort`. Purge active `T-309a`, unsplit `T-312`, unsplit `T-314`, and unsplit `T-316` references outside historical sections.

### B5-06 - `T-313b` depends on the production `DecisionRecordVerifier` before it is scheduled

**Evidence.**

- The declared Phase 3 order places `T-313b` before `T-314b` at `CODING_AGENDA.md:491`.
- `T-313b` handler files authenticate requests via `DecisionRecordVerifier (T-314b)` at `CODING_AGENDA.md:745`.
- `T-313b` SOP says every request is authenticated via `DecisionRecordVerifier` at `CODING_AGENDA.md:756`.
- `T-314b`, the production verifier and key lifecycle task, is not until `CODING_AGENDA.md:780`.

**Why this is blocking.** A production audit-service process cannot satisfy its authentication acceptance criteria before the production verifier and public-key distribution/revocation model exist. It can unit-test against `T-314a` fakes, but the `T-313b` acceptance criteria are production-service criteria: concurrent appends, crash recovery, IPC timeout, and key rotation under contention.

**Required correction.**

Move `T-314b` before `T-313b`, or split `T-313b` into an IPC/server skeleton against `T-314a` fakes and a later production-authentication integration task after `T-314b`.

### B5-07 - `T-316b` production signed store/bootstrap is scheduled before the production SOP-template signer/verifier

**Evidence.**

- `T-316b` is the signed SQLite SOP-template store and bootstrap migration at `CODING_AGENDA.md:923`.
- Its SOP requires every read to call `SopTemplateVerifier.verify(template)` and every write/bootstrap to sign templates with `SopTemplateSigner.sign(...)` at `CODING_AGENDA.md:933-935`.
- Its acceptance requires template signature verification on every read, tamper failure, and bootstrap from YAML producing signed templates at `CODING_AGENDA.md:938`.
- The production `SopTemplateSigner` and `SopTemplateVerifier` adapters are not implemented until `T-316c` at `CODING_AGENDA.md:940-959`.
- The text admits that `T-316b` ships against fakes until `T-316c` lands at `CODING_AGENDA.md:934-935` and `CODING_AGENDA.md:959`.

**Why this is blocking.** `T-316b` is labelled as the production signed store/bootstrap task, but its own acceptance cannot be fully satisfied with fake signers. A bootstrap migration that produces signed institutional templates must be verified against the production key lifecycle, archive, revocation, and offline verifier.

**Required correction.**

Move `T-316c` before the production-signing portions of `T-316b`, or split `T-316b` into (a) schema/store integration against protocol fakes and (b) production bootstrap/signature integration after `T-316c`.

### B5-08 - `T-310` and `T-311` still reference unsplit `T-313`, `T-314`, and `T-316`

**Evidence.**

- `T-310` still says its append broker is `T-313` and its verifier comes from `T-314` at `CODING_AGENDA.md:656`, `CODING_AGENDA.md:660`, and `CODING_AGENDA.md:661`.
- `T-311` still calls `AuthorisationProfileSigner.sign()` from `T-314` and writes via an `AdminAuditAppendPort` opened on `audit.sqlite mode=rw` paired with `T-313` at `CODING_AGENDA.md:676`.
- `T-311` still says SOP-template admin writes are owned by `T-316` at `CODING_AGENDA.md:684`.
- `T-803` still references `T-316 v1.3` at `CODING_AGENDA.md:1247-1250`.
- `T-903` still references `T-309b` activation at `CODING_AGENDA.md:1284`.

**Why this is blocking.** The split-task strategy only works if consumers depend on the correct early-half surfaces. The task cards that implement persistence, admin actions, SOP rendering, and export still teach implementers to consume obsolete task identities.

**Required correction.**

Rewrite consumer task cards:

- `T-310c` consumes `T-313a` protocols/fakes and later integrates with `T-313b`;
- `T-310d` consumes `T-314a` verifier protocol/fake and later integration-tests with `T-314b`;
- `T-311` consumes `T-313a`, `T-314a`, and later integration-tests with `T-313b`/`T-314b`;
- SOP-template writes are `T-316b`; SOP-template production key lifecycle is `T-316c`;
- gate activation references must use single `T-309`, not `T-309b`.

### B5-09 - Review-queue admin triage is still wired through `AdminActionHandler`, not `ReviewQueueAdminPort`

**Evidence.**

- v1.4 says `ReviewQueueAdminPort` was added per H4-01 at `CODING_AGENDA.md:16` and in the port inventory at `CODING_AGENDA.md:429`.
- `T-315` files do not include a `src/domain/ports/review_queue_admin.py` or equivalent explicit port implementation owner at `CODING_AGENDA.md:829-834`.
- `T-315` SOP still says `triage_queue` writes via the admin-service-process `AdminActionHandler (T-311)` at `CODING_AGENDA.md:839`.
- `T-1103b` later says it implements `ReviewQueueAdminPort` from `T-315` at `CODING_AGENDA.md:1327` and routes to it at `CODING_AGENDA.md:1343`.

**Why this is blocking.** The port is declared in the inventory but not coherently owned in the producing task. The actual review-queue task still routes resolution through the general admin handler rather than through the dedicated admin-service port. That leaves the H4-01 self-resolution/bypass closure only partially implemented.

**Required correction.**

Make `T-315` explicitly own `ReviewQueueAdminPort` and its concrete app-service boundary. `ReviewQueueService` should expose user/service submission paths only; admin resolution should be through `ReviewQueueAdminPort`, implemented by admin-service code in `T-1103b`. Update acceptance tests to prove CLI/API/user paths cannot reach resolution except through `AdminServiceClientPort -> admin-service -> ReviewQueueAdminPort`.

### B5-10 - Source-of-truth hierarchy is not coherent for `SopTemplateLibrary`, admin authority, and new service modules

**Evidence.**

- `ARCHITECTURE.md` remains the authoritative blueprint in `README.md:18`, and ROADMAP says architecture defines what is built at `ROADMAP.md:7`.
- `ARCHITECTURE.md` still lists `SopTemplateLibrary` as a port/dependency at `ARCHITECTURE.md:234`, `ARCHITECTURE.md:284`, `ARCHITECTURE.md:321`, `ARCHITECTURE.md:853`, `ARCHITECTURE.md:2407`, and `ARCHITECTURE.md:2445`.
- `REQUIREMENTS.md:375` still requires `ReviewerPrincipal` to be rejected by `SopTemplateLibrary.write_*`.
- `REQUIREMENTS.md:365`, `REQUIREMENTS.md:370`, and `REQUIREMENTS.md:528` still permit `DeveloperPrincipal` for admin mutations, while the agenda interprets these as `DeveloperBootstrapPrincipal`.
- `ARCHITECTURE.md` interface modules are only `interface.cli`, `interface.api`, and `interface.ui` at `ARCHITECTURE.md:332-334`; v1.4 adds `interface.audit_service` and `interface.admin_service` in the agenda without an architecture-module amendment.

**Why this is blocking.** v1.4 simultaneously says the agenda removes `SopTemplateLibrary` and that the architecture remains the authoritative source. It also introduces new interface modules not present in the architecture catalogue while claiming architecture consistency. Implementers and manifest authors cannot know whether the architecture or the agenda wins.

**Required correction.**

Add a formal v1.6 architecture/requirements amendment or a tightly scoped binding override section that lists each intentional divergence, its replacement surface, and its expiry. At minimum: replace `SopTemplateLibrary` with `SopTemplateReadPort`/`SopTemplateAdminWritePort`; replace admin `DeveloperPrincipal` authority with `DeveloperBootstrapPrincipal`; add `interface.audit_service` and `interface.admin_service` to the module catalogue; update requirements FR-AUTH-14 and BR-12.

## High Findings

### H5-01 - The stale-token CI gate scope is too narrow

**Evidence.**

- The fourth response promised stale active IDs would be purged, especially `T-309a`, `T-309b`, and unsplit `T-312`.
- Active content still contains `T-309a` at `CODING_AGENDA.md:1586`, `CODING_AGENDA.md:1710`, `CODING_AGENDA.md:1854`, `CODING_AGENDA.md:1862`, and `CODING_AGENDA.md:1878`.
- Active content still contains unsplit `T-312` at `CODING_AGENDA.md:1591` and `CODING_AGENDA.md:1623`.
- More importantly, the gate scope does not include stale unsplit `T-313`, `T-314`, `T-316`, and `T-1103` references, which are now the main drift source.

**Impact.** The proposed CI gate would miss the active stale task IDs that now matter most. It would also allow the stale `T-314` heading to survive.

**Required correction.** Expand `test_no_stale_task_ids_in_active_sections.py` to cover every superseded task ID after a split, including `T-313`, `T-314`, `T-316`, and `T-1103`, with explicit allow-lists for historical sections only.

### H5-02 - `TASK_BOARD.md` was not regenerated from a manifest and preserves stale v1.3/v1.4 arithmetic

**Evidence.**

- `TASK_BOARD.md:3` says counts are only planned-generated until `T-204`.
- `TASK_BOARD.md:42` claims Phase 3 has 18 tasks even though intended Phase 3 has 19 and actual headings have 20.
- `TASK_BOARD.md:43` claims Phase 4 has 6 tasks even though `T-316b` and `T-316c` are active Phase 4 headings.
- `TASK_BOARD.md:56` claims 71 main tasks and a net +4 delta, which conflicts with the active heading count and split arithmetic.
- `TASK_BOARD.md:11` still describes the retained v1.3 Phase 3 change as "12 -> 17", which no longer matches v1.4.

**Impact.** The war-room dashboard is a primary operational control. If it starts with wrong counts and stale status math, it will hide missing work rather than reveal it.

**Required correction.** Do not claim task counts are regenerated until `docs/task_manifest.yaml` exists. Add an interim machine check that parses `CODING_AGENDA.md` headings directly and fails if the board disagrees.

### H5-03 - `T-204` claims committed manifests that do not exist in the repository

**Evidence.**

- `T-204` says `docs/module_manifest.yaml` is manually authored and committed, and `docs/task_manifest.yaml` plus `docs/port_manifest.yaml` are committed under `docs/` at `CODING_AGENDA.md:450`.
- In the current workspace, `docs/module_manifest.yaml`, `docs/task_manifest.yaml`, and `docs/port_manifest.yaml` do not exist.
- Section 3 CI table still says module coverage parses a manifest "generated from ARCHITECTURE.md" at `CODING_AGENDA.md:1917`, contradicting the v1.4 B4-07 manual-manifest correction.

**Impact.** This weakens the entire docs-as-code QC layer. The plan depends on manifests, but the first manifestation of those manifests is deferred, hand-maintained, and internally contradictory.

**Required correction.** Either make manifest creation an explicit `T-204` deliverable with no claim that files are already committed, or commit initial seed manifests now. Update Section 3 CI table to manual `docs/module_manifest.yaml` plus informational architecture-consistency check.

### H5-04 - The audit-service authentication failure path is undefined and likely circular

**Evidence.**

- `T-313b` denies unauthenticated IPC requests and "emits its own `AuditServiceAuthenticationFailed` event to the governance stream (via the audit-service's own engine-stream IPC client)" at `CODING_AGENDA.md:756`.
- The event-stream table at `CODING_AGENDA.md:1855` does not list audit-service as a governance-stream writer.
- No task defines an "engine-stream IPC client" for the audit-service.

**Impact.** The audit service is supposed to be the hardened single writer for the audit chain, but its failure-event path is not owned by any port or process. A failed authentication attempt is security-significant; losing or misrouting it breaks auditability.

**Required correction.** Define a concrete governance-event append path for audit-service-originated security events. It should be a dedicated, minimal `GovernanceEventAppendPort` or an explicit local event writer owned by `T-313b`, with replay and failure-mode tests. Avoid relying on an undefined "engine-stream IPC client."

### H5-05 - Admin-service IPC authentication still points to old `T-314`

**Evidence.**

- `T-1103a` documents authentication as "signed admin-principal token via T-314 `DecisionRecordSigner`" at `CODING_AGENDA.md:1299`.
- v1.4 split `DecisionRecordSigner`/`DecisionRecordVerifier` into `T-314a` protocols/fakes and `T-314b` production adapters at `CODING_AGENDA.md:764` and `CODING_AGENDA.md:780`.

**Impact.** The IPC contract is a security boundary. Ambiguous authentication ownership here invites direct handler calls, fake-token use in production, or mismatch between CLI/API test clients and production admin-service verification.

**Required correction.** Specify that `T-1103a` defines the token envelope against `DecisionRecordSigner`/`DecisionRecordVerifier` protocols from `T-314a`, and `T-1103b` production authentication requires `T-314b`.

### H5-06 - `AuthorisationProfile` minting lacks an unsigned draft model

**Evidence.**

- `T-304` makes `AuthorisationProfile` carry `profile_signature` and `profile_signature_key_version` at `CODING_AGENDA.md:540`.
- `T-311` receives an `AuthorisationProfile` object as input and then calls `AuthorisationProfileSigner.sign(profile, admin)` before commit at `CODING_AGENDA.md:676`.
- The plan does not define an `UnsignedAuthorisationProfileDraft`, builder, or `replace(profile_signature=...)` flow.

**Impact.** If the canonical `AuthorisationProfile` type requires a signature, a caller cannot construct the object that the signer is supposed to sign. If it allows empty signatures, the type-level invariant is weaker than the plan claims.

**Required correction.** Introduce a distinct unsigned draft type, or make the signer construct a signed `AuthorisationProfile` from a validated draft. Update tests to assert unsigned profiles cannot cross the persistence boundary.

### H5-07 - Architecture/module coverage cannot validate new audit/admin service modules

**Evidence.**

- `T-313b` adds `src/interface/audit_service/...` at `CODING_AGENDA.md:743-747`.
- `T-1103b` adds `src/interface/admin_service/...` at `CODING_AGENDA.md:1322-1328`.
- `ARCHITECTURE.md` lists only `interface.cli`, `interface.api`, and `interface.ui` at `ARCHITECTURE.md:332-334`.
- `T-204` says architecture consistency is informational, while module coverage is based on a manual manifest at `CODING_AGENDA.md:450`.

**Impact.** New process-boundary modules are security-critical and should not be introduced only in the agenda. Without architecture anchors, import-linter contracts and module coverage can miss or misclassify them.

**Required correction.** Add `interface.audit_service` and `interface.admin_service` to the architecture module catalogue or explicitly document them as v1.4 agenda-owned modules with manifest entries and import-linter rules.

### H5-08 - `no-self-authorisation-check` remains stale in the authoritative CI table

**Evidence.**

- `T-204` expands `no-self-authorisation-check` to six surfaces at `CODING_AGENDA.md:462`.
- Section 3.5 still lists only "no User-scope code path imports `AuthorisationAdminWritePort` write methods" and activation after `T-311` at `CODING_AGENDA.md:1909`.

**Impact.** The task card and the CI table disagree. Implementers wiring CI from Section 3.5 will under-scope the gate and mark it enforced too early, before audit-service, SOP-template, and admin-service IPC protections exist.

**Required correction.** Update the Section 3.5 row to the six surfaces and enforce only after `T-313b`, `T-316b`, and `T-1103b` integration tests pass.

### H5-09 - README and ROADMAP still advertise stale v1.3/v1.2 content

**Evidence.**

- Fourth response output says `README.md` was updated, but `README.md:24` still describes `CODING_AGENDA.md` as "Finalised v1.3" and points to the third-round response.
- `ROADMAP.md:3-6` claims v1.4 regeneration, but active Phase 2/8 text still references `SopTemplateLibrary` and `DeveloperPrincipal` at `ROADMAP.md:106` and `ROADMAP.md:290`.
- `ROADMAP.md:576` and `ROADMAP.md:600` still say the binding content/end marker is derived from `CODING_AGENDA.md v1.3`.

**Impact.** Support documents are not just narrative here; they are used as implementation context by agents and human reviewers. Stale v1.3 text will propagate old surfaces back into code.

**Required correction.** Regenerate README and ROADMAP from the corrected agenda. Add a stale-token test for README and ROADMAP that includes `Finalised v1.3`, `CODING_AGENDA.md v1.3`, `SopTemplateLibrary`, `DeveloperPrincipal` in admin contexts, and superseded task IDs.

## Moderate Findings

### M5-01 - `T-601a..k` range notation is not manifest-safe

**Evidence.**

- Phase 6 has an active heading `T-601a..k` at `CODING_AGENDA.md:1018`.
- v1.4 relies on heading parsers and task-brief coverage for every `#### ... T-*` task.

**Impact.** A simple `T-[0-9]+[a-z]?` parser will not treat `T-601a..k` as eleven task IDs. Depending on implementation, it may produce one invalid ID, one partial ID, or skip the range. This can mask count errors, especially when stale headings also exist.

**Required correction.** Either expand `T-601a..k` into explicit headings or define a formal range grammar in `task_manifest_generator.py` and test it.

### M5-02 - Section numbering is no longer monotonic in Phase 3

**Evidence.**

- `T-313b` is `2.3.15` at `CODING_AGENDA.md:740`.
- `T-314a` is `2.3.16` at `CODING_AGENDA.md:764`.
- `T-314b` is `2.3.17` at `CODING_AGENDA.md:780`.
- Stale `T-314` reuses `2.3.15` at `CODING_AGENDA.md:803`.

**Impact.** Non-monotonic numbering is a symptom of stale task insertion and breaks stable references in briefs, review comments, and generated manifests.

**Required correction.** After deleting stale `T-314` and reordering Phase 3, renumber the phase from `2.3.1` through `2.3.19` in physical task order.

### M5-03 - v1.4 sign-off claims overstate the state of the actual document

**Evidence.**

- The sign-off says the dependency DAG, composition root, persistence wiring, and module catalogue are consistent at `CODING_AGENDA.md:2655`.
- Findings B5-01 through B5-10 show active contradictions in those exact sections.

**Impact.** Overstated sign-off makes later audits harder because implementers may treat unresolved synchronization work as already closed.

**Required correction.** Replace the v1.4 sign-off with a conditional status until all machine-checkable agenda consistency tests pass.

### M5-04 - Audit-key retention text still contains old bounded-archive language

**Evidence.**

- v1.4 H4-05 says audit-key archive retention is indefinite.
- `T-312b` still contains older wording in its SOP about an archive of N previous key versions in the output reviewed earlier around the `T-312b` task, while later text says escrow is indefinite.

**Impact.** Key-retention ambiguity can break long-term audit verification. For a legal audit chain, "N previous versions" and "all referenced versions indefinitely" are materially different.

**Required correction.** Remove bounded archive wording entirely or explicitly define it as only an in-process cache, never the authoritative archive.

### M5-05 - PDF/font reproducibility is planned but current repository state does not match "committed fonts" language

**Evidence.**

- `T-201` says canonical fonts are committed under `fonts/` and CI fails if missing at `CODING_AGENDA.md:367`.
- The current workspace has no `fonts/` directory.

**Impact.** This is not blocking before coding begins if `T-201` is the task that creates the directory, but the language "are committed" is misleading in a planning document that also claims v1.4 output completed.

**Required correction.** Change present-tense claims to `T-201 will commit...`, or commit the font placeholders/license metadata now if the agenda is meant to describe the current repo state.

### M5-06 - Windows/OneDrive target environment needs IPC/path fixtures for the new services

**Evidence.**

- The user workspace is under OneDrive, and earlier agenda versions correctly added OneDrive/path readiness.
- v1.4 adds Windows named pipes for audit-service and admin-service IPC at `CODING_AGENDA.md:745`, `CODING_AGENDA.md:1288-1328`, but the existing platform readiness task `T-205` is not expanded to probe named-pipe permissions, service account ACLs, socket path length, or OneDrive interaction for the new SQLite files and IPC clients.

**Impact.** The plan is mostly suitable for the target programming environment, but new v1.4 process boundaries add Windows-specific failure modes that are not yet covered by the platform probe.

**Required correction.** Extend `T-205` with Windows named-pipe creation/connection fixtures, service-account ACL checks, SQLite WAL behavior under OneDrive-synced paths, and POSIX socket path/permission equivalents.

## Cross-Cutting Quality-Control Assessment

The quality-control strategy is conceptually strong but not robust yet:

- Manifest-driven counts are claimed before seed manifests exist.
- Stale-token gates are too narrow and would miss the current stale unsplit tasks.
- Port inventory tests still reference 45 ports while the inventory claims 49 and arithmetic implies 50.
- Section 3 CI lifecycle rows do not match `T-204` task-card scope.
- Support-document stale-token checks do not include README and do not catch all active ROADMAP drift.

The plan needs a bootstrap consistency pass before implementation tasks begin. The pass should generate a single machine-readable task manifest, port manifest, and module manifest, then render `TASK_BOARD.md`, Appendix B/C, and brief coverage from those manifests.

## Scientific and Engineering Rationality Assessment

Scientifically, the plan still protects the most important high-level invariant: no operational SOP/export should precede screening, authorisation, and advisory acknowledgement. v1.4 fixed the phase-level Phase 10 placement. The remaining risk is not that the scientific intent is wrong; it is that stale implementation surfaces can accidentally bypass that intent.

The riskiest scientific/safety consequences are:

- stale `SopTemplateLibrary` references can revive user-controlled or YAML-runtime SOP paths;
- stale admin-write surfaces can bypass `AdminServiceClientPort`;
- a broken audit-service authentication failure path can lose security-relevant events;
- wrong task order can cause fakes to be treated as production boundaries or production services to be built before their authenticators.

Engineering-wise, the target architecture remains viable: Python 3.11+, uv, SQLite, JSONL events, ports/adapters, and deterministic tests are appropriate. The immediate weakness is not the technology selection; it is synchronization discipline across the plan's executable documents.

## Required Remediation Sequence

1. Delete stale `T-314`; physically reorder Phase 3 so early protocol/fake tasks precede consumers; renumber Phase 3.
2. Recompute all task counts: Phase 3, Phase 4, cumulative total, `TASK_BOARD.md`, Appendix B/C, and context-budget table.
3. Rebuild the port inventory with unique IDs and a correct total; update the test expectation from 45.
4. Regenerate Section 3 composition, event, persistence, and CI tables from the corrected task/port manifests.
5. Decide and document source-of-truth overrides for `SopTemplateLibrary`, `DeveloperPrincipal`, `interface.audit_service`, and `interface.admin_service`; preferably amend `ARCHITECTURE.md` and `REQUIREMENTS.md`.
6. Fix build-order edges: `T-314b` before production-authenticated `T-313b`, and `T-316c` before production-signed bootstrap portions of `T-316b`, or split those tasks further.
7. Make `ReviewQueueAdminPort` a real `T-315` deliverable and route admin triage only through admin-service IPC.
8. Expand stale-token and count-consistency CI gates to catch all split-task drift, range notation, duplicate task IDs, duplicate section numbers, and support-doc stale tokens.

## Final Verdict

v1.4 should be treated as a partial synchronization draft, not a coding-ready plan. Its architecture is moving in the right direction, but the active document still contains enough contradictions to make automated task generation, implementation handoff, and security-significant acceptance testing unreliable.

The next version should be a mechanical consistency release before new features are added: reorder headings, remove stale cards, regenerate manifests and counts, fix Section 3, and align README/ROADMAP/requirements/architecture with the new ports and process boundaries.
