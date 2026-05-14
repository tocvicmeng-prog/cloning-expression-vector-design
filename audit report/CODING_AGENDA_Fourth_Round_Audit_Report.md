# Fourth-Round CODING_AGENDA.md Audit Report

**Subject:** `CODING_AGENDA.md` v1.3  
**Prior response reviewed:** `audit report/CODING_AGENDA_Third_Round_Audit_Response.md`  
**Supporting documents consulted:** `ARCHITECTURE.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, `TASK_BOARD.md`  
**Audit date:** 2026-05-14  
**Reviewer stance:** senior software architect, experienced coder, and software quality-control auditor applying adversarial falsification.

## Executive Verdict

`CODING_AGENDA.md` v1.3 is **not yet implementation-ready**.

The third-round response correctly identified many serious v1.2 weaknesses and introduced the right security primitives in concept: `AuditAppendPort`, profile signing, signed SOP-template storage, review queue, `DeveloperBootstrapPrincipal`, and admin-service IPC. However, the v1.3 propagation is incomplete. Several new tasks are scheduled **after** the tasks that consume them, the binding build queue still physically orders SOP/export work before screening work, the inter-module wiring section remains partly v1.2, and the manifest-driven QC story depends on architecture anchors and generated manifests that are not actually present.

This fourth-round audit found:

| Severity | Count | Result |
|---|---:|---|
| Blocking | 9 | Must be fixed before coding begins |
| High | 10 | Must be fixed before security/safety-significant tasks are implemented |
| Moderate | 8 | Should be fixed before Phase 2/3 verification |

The core failure mode is synchronisation drift: v1.3 changed individual task cards, but did not fully regenerate the build queue, DAG, composition root, CI lifecycle table, task-board arithmetic, roadmap, and machine-manifest assumptions.

## Audit Method

I checked the v1.3 agenda against the third-round response commitments, then falsified the plan along these axes:

- strict build order: can each task pass its stated acceptance criteria when executed in the declared order?
- safety sequencing: can SOP rendering or export become reachable before screening and authorisation evidence exist?
- security boundaries: do audit, authorisation, SOP-template, and admin-service write paths have executable separation of duties?
- QC gates: are manifest, task, port, and CI gate claims machine-realistic?
- target environment: do Windows, OneDrive, uv, PDF rendering, SQLite locking, and IPC assumptions have testable plans?
- scientific safety: does the plan preserve screening-before-SOP, advisory acknowledgement, review-queue recovery, and dual-control/administrator-only semantics without ambiguity?

I stopped after repeated passes over task order, wiring, manifests, security, supporting-doc drift, and UAT coverage produced no additional distinct defect classes beyond the findings below.

## Positive Confirmations

- The v1.3 direction is architecturally better than v1.2: audit append authority is separated in concept from authorisation-store write authority.
- Governance events embedding full signed payloads is the correct fix for durable approval traces.
- `T-312a` / `T-312b` is the right pattern for splitting a protocol/test provider from production key stores.
- `DeveloperBootstrapPrincipal` is a stronger design than unrestricted post-bootstrap `DeveloperPrincipal` authority.
- Phase 13 UAT coverage is much more concrete than earlier versions.

These positives do not remove the blocking defects below.

## Blocking Findings

### B4-01 - The binding build queue still orders Phase 8b/9b before Phase 10

**Evidence.**

- The agenda states the binding phase order is `... 9a -> 10 -> 8b -> 9b ...`.
- In the actual module catalogue, `Phase 9a` is followed by `Phase 8b` at `CODING_AGENDA.md:1093`, then `Phase 9b` at `CODING_AGENDA.md:1125`, and only then `Phase 10` at `CODING_AGENDA.md:1137`.
- `T-204` says `task_manifest_generator.py` walks all `#### 2.x.y T-<id>` headings in `CODING_AGENDA.md` section 2. A heading-order parser will therefore emit `T-803`, `T-805b`, `T-806b`, and `T-903` before `T-1001`/`T-1002`.

**Why this is blocking.** This reopens the central safety defect v1.2 was meant to close: SOP rendering and final export can appear in the generated build queue before screening adapters and `ScreeningCompleted` exist.

**Required correction.**

Physically reorder section 2 to `Phase 9a -> Phase 10 -> Phase 8b -> Phase 9b`, or make `task_manifest_generator.py` use an explicit phase-order table and fail if heading order disagrees. Add a CI fixture that asserts `T-1001/T-1002` precede `T-803/T-806b/T-903` in `docs/task_manifest.yaml`.

### B4-02 - `T-314` profile signing is scheduled after its consumers

**Evidence.**

- Phase 3 order puts `T-314` after `T-310` and `T-311` at `CODING_AGENDA.md:468`.
- `T-310d` calls `AuthorisationProfileVerifier` from `T-314` on every `get()` at `CODING_AGENDA.md:629` and `CODING_AGENDA.md:634`.
- `T-311` calls `AuthorisationProfileSigner.sign()` from `T-314` before commit at `CODING_AGENDA.md:649`.

**Why this is blocking.** `T-310` and `T-311` cannot pass their own acceptance tests before the signer/verifier protocols, fakes, adapters, and error taxonomy exist. The third-round response explicitly accepted B3-04, but placed the new task too late to satisfy its consumers.

**Required correction.**

Split `T-314` into an early protocol/fake task and a later production-keystore task, or move the whole `T-314` before `T-310`. At minimum, `AuthorisationProfileSigner`, `AuthorisationProfileVerifier`, deterministic test signer/verifier, and signature error types must exist before `T-310d` and `T-311`.

### B4-03 - `T-313` audit append broker is scheduled after its consumers

**Evidence.**

- Phase 3 order puts `T-313` after `T-310` and `T-311` at `CODING_AGENDA.md:468`.
- `T-310c` states append writes are routed through the `AuditAppendPort` broker owned by `T-313` at `CODING_AGENDA.md:633`.
- `T-311` writes audit entries through `AdminAuditAppendPort` paired with the engine broker `T-313` at `CODING_AGENDA.md:649`.
- `T-311` acceptance requires the admin audit chain to extend the HMAC chain from `T-310c + T-313` at `CODING_AGENDA.md:658`.

**Why this is blocking.** The admin handler cannot honestly verify audit writes before the audit append broker and admin-side append port exist.

**Required correction.**

Define `AuditAppendPort`, `AdminAuditAppendPort`, service-principal identity, deterministic fake append brokers, and chain-integrity test helpers before `T-311`. Production broker implementation can remain later only if `T-311` acceptance is explicitly phase-gated and cannot be marked verified until the broker is in place.

### B4-04 - The dual-writer audit-lock model is internally non-executable

**Evidence.**

- `T-313` says the engine `AuditBroker` opens `audit.sqlite` `mode=rw` and holds an exclusive file lock for the broker lifetime at `CODING_AGENDA.md:696` and `CODING_AGENDA.md:703`.
- The same task says engine and admin-service brokers cannot both run simultaneously and require a "small lock-handoff protocol" at `CODING_AGENDA.md:704`.
- The composition root constructs the engine `AuditBroker` unconditionally at `CODING_AGENDA.md:1461`.
- `T-1103` says the admin-service process starts with the admin-side `AuditAppendPort` opened at `CODING_AGENDA.md:1182`.

**Why this is blocking.** A long-lived engine exclusive writer and a long-lived admin-service writer cannot both own the same SQLite chain. The plan names "lock handoff" but gives no protocol, state machine, timeout behavior, failure recovery, or cross-process test. This can deadlock admin operations or force an unsafe bypass of the audit chain.

**Required correction.**

Choose one executable model:

- a single audit-service writer process with both engine and admin append requests sent over IPC;
- SQLite transaction-level serialization using short `BEGIN IMMEDIATE` append transactions, without a lifetime exclusive lock;
- a queue-based append broker that all processes use.

Then add crash, timeout, concurrent engine/admin append, and key-rotation tests that prove a single linear HMAC chain under contention.

### B4-05 - `T-316` SOP-template bootstrap is scheduled before its inputs exist, and runtime wiring still uses the YAML loader

**Evidence.**

- `T-316` is Phase 3 and its bootstrap reads `catalogues/sop_templates/*.yaml` at `CODING_AGENDA.md:770`.
- `T-401` writes the `sop-templates` JSON schema later in Phase 4 at `CODING_AGENDA.md:776`.
- Phase 4 is where catalogue loading and catalogue data population start. Phase 2 only creates directories.
- The composition root still constructs `sop_template_library: SopTemplateLibrary = YamlSopTemplateLoader(...).load()` at `CODING_AGENDA.md:1411`.
- It then constructs `SopProtocolGenerator(sop_template_library)` at `CODING_AGENDA.md:1522`, despite later also constructing `sop_template_read_port`.

**Why this is blocking.** `T-316` cannot pass "bootstrap from YAML produces signed templates" before schemas and actual templates exist. The runtime wiring also keeps the old YAML read surface alive after declaring SQLite signed templates canonical.

**Required correction.**

Split `T-316` into:

- early Phase 3 port stubs and value-object types only;
- post-Phase 4 signed SQLite store, migration/bootstrap, and template signature verification after schema/catalogue content exists.

Remove `SopTemplateLibrary` / `YamlSopTemplateLoader` from runtime composition once `SopTemplateReadPort` is canonical.

### B4-06 - Section 3 wiring remains v1.2 and contradicts the v1.3 task cards

**Evidence.**

- Section 3 is titled "v1.2" at `CODING_AGENDA.md:1259` and its DAG says "v1.2 phase order" at `CODING_AGENDA.md:1261`.
- It still references `T-309a`, `T-309b`, and `T-312` at `CODING_AGENDA.md:1280`, `CODING_AGENDA.md:1291`, `CODING_AGENDA.md:1303`, `CODING_AGENDA.md:1342`, `CODING_AGENDA.md:1352`, and `CODING_AGENDA.md:1358`.
- It still says `sop_templates/*.yaml` are admin-writable via `T-803` at `CODING_AGENDA.md:1299`.
- It says Phase 11 wires admin commands to `T-311 AdminActionHandler` at `CODING_AGENDA.md:1360`, contradicting `T-1103`.

**Why this is blocking.** Section 3 is the executable wiring blueprint. If it is stale, implementers can build the old security boundary while the task cards say something else.

**Required correction.**

Regenerate section 3 end-to-end for v1.3. Add a static doc gate that fails on stale references to `T-309a`, `T-309b`, unsplit `T-312`, `T-803` SOP-template admin writes, and direct CLI/API-to-`AdminActionHandler` wiring outside historical appendices.

### B4-07 - Manifest-driven module coverage cannot work against the current architecture text

**Evidence.**

- `T-204` says `architecture_manifest_generator.py` parses `ARCHITECTURE.md` section 4.2 by anchor markers `<!-- module: <id> -->` at `CODING_AGENDA.md:442`.
- No such anchors are present in `ARCHITECTURE.md`.
- `ARCHITECTURE.md` section 4.2 also does not list the v1.3 agenda additions as first-class modules/ports: `AuditAppendPort`, `AuthorisationProfileSigner`, `AuthorisationProfileVerifier`, `ReviewQueueStore`, `SopTemplateAdminWritePort`, signed SOP-template store, or `interface.admin_service`.

**Why this is blocking.** The Phase 2 `T-204` acceptance requires non-empty generated manifests and a module-coverage check. The stated parser input is absent, and the architecture source does not enumerate the new v1.3 work items it is supposed to cover.

**Required correction.**

Either add an explicit architecture-amendment task before `T-204` that inserts stable module anchors and v1.3 modules, or make `docs/module_manifest.yaml` manually authored from an authoritative manifest schema and treat `ARCHITECTURE.md` prose as a checked reference, not the parser source.

### B4-08 - Admin-service IPC is introduced after the CLI/API tasks that need it

**Evidence.**

- Phase 11 task order is `T-1101`, `T-1102`, then `T-1103`.
- `T-1101` includes admin commands (`admin-mint`, `admin-modify`, `admin-revoke`) at `CODING_AGENDA.md:1159`.
- `T-1102` says admin endpoints route through `T-1103` at `CODING_AGENDA.md:1164`.
- The DAG still says CLI wires admin commands directly to `T-311` at `CODING_AGENDA.md:1360`.

**Why this is blocking.** The executable security boundary is the admin-service IPC. Implementing CLI/API admin routes before the IPC exists encourages direct handler imports or insecure placeholders.

**Required correction.**

Move `T-1103` before admin command wiring, or split an early `AdminServiceClientPort` / IPC contract task before `T-1101`/`T-1102`. `T-1101` and `T-1102` acceptance should fail if they import or instantiate `AdminActionHandler` directly.

### B4-09 - `DecisionRecordSigner` implementation and key lifecycle are unowned

**Evidence.**

- `DecisionRecordSigner` is listed as a port at `CODING_AGENDA.md:404`.
- It is consumed by admin actions, review queue decisions, advisory acknowledgement, screening sign-off, and admin-service authentication.
- No task owns a concrete `DecisionRecordSigner` adapter, key store, rotation policy, public-key distribution, offline verifier, or compromised-key response.

**Why this is blocking.** v1.4/v1.5 safety relies on signed `DecisionRecord` and `RoleSnapshot`. Without a concrete signer and key lifecycle, signed governance events and admin IPC authentication are not implementable.

**Required correction.**

Add a dedicated signing task or extend `T-314` to cover per-principal `DecisionRecordSigner` implementation, key provisioning, key rotation, revocation, offline verification, role-snapshot binding, and adversarial tests.

## High Findings

### H4-01 - Review-queue admin triage is not wired into the admin-service boundary

`T-315` says `triage_queue` writes via `AdminActionHandler`, but the `AdminActionHandler` operations listed in `T-311` are profile lifecycle operations, and the admin handler constructor in section 3 does not receive `ReviewQueueStore` or `ReviewQueueService`. `T-1103` also does not list `ReviewQueueStore` among admin-service-owned resources.

**Correction:** define a `ReviewQueueAdminPort` or run `ReviewQueueService.triage_queue` inside the admin-service process. Inject it into `T-1103`, add IPC verbs, and test that user/API callers cannot resolve their own requests.

### H4-02 - Security CI gates are stale and too narrow for the v1.3 surface

The `no-self-authorisation-check` row at `CODING_AGENDA.md:1709` covers "no User-scope code path imports `AuthorisationAdminWritePort` write methods." It does not explicitly cover:

- Reviewer attempts, required by FR-AUTH-14;
- `SopTemplateAdminWritePort`;
- `AuditAppendPort` / `AdminAuditAppendPort`;
- direct CLI/API reachability to `AdminActionHandler`;
- admin-service IPC bypass;
- `DeveloperBootstrapPrincipal` post-bootstrap restrictions.

It is also marked enforced after `T-311`, although v1.3 adds security-critical surfaces in `T-313`, `T-316`, and `T-1103`.

**Correction:** expand the gate scope and split activation milestones by protected surface. The gate should not be `enforced-green` until admin IPC, audit append, SOP-template writes, and reviewer-denial tests are included.

### H4-03 - The task-acceptance gate has no owned path to create task briefs

`T-204` adds `task_acceptance_completeness_check.py`, which parses `tasks/task_brief/T-<id>.md`. Appendix D defines the skeleton. No task creates the initial task-brief set for the approximately 66 Phase 2-13 task headings before the gate is enforced after Phase 3.

**Correction:** make `T-204` generate initial task briefs from `CODING_AGENDA.md`, or make the gate parse agenda cards directly until task briefs exist. Add a manifest test comparing every `#### ... T-*` heading with a corresponding task brief.

### H4-04 - SOP-template signing key lifecycle is underspecified

`T-316` mentions `SopTemplateSigner` and `SopTemplateVerifier`, but the port inventory does not include signer/verifier ports, no file path owns them, and there is no rotation, archive, revocation, offline-verification, or public-key distribution model comparable to `T-314` and `T-312b`.

**Correction:** add explicit SOP-template signing ports, keystore adapters, key-versioning semantics, offline verifier, compromise response, and tests for wrong-key-version and revoked-key behavior.

### H4-05 - Audit-key archive retention can break long-term audit verification

`T-312b` stores an archive of `N` previous key versions with default `N=10`, while the offline verifier is expected to verify every row in the legal audit log. After more than 10 rotations, historical rows may no longer verify.

**Correction:** audit HMAC keys used for legal traceability need indefinite verification retention, escrowed archives, or immutable exported verification bundles. Do not use bounded key eviction for any key version referenced by an audit row.

### H4-06 - Requirements and architecture still conflict with `DeveloperBootstrapPrincipal`

The agenda narrows post-bootstrap authority to `DeveloperBootstrapPrincipal`, but `REQUIREMENTS.md` FR-AUTH-04/09 and BR-12 still refer to `DeveloperPrincipal`, and `ARCHITECTURE.md` still says code paths requiring admin may accept `DeveloperPrincipal` in several places.

**Correction:** update requirements and architecture wording or add a compatibility note that `DeveloperPrincipal` is valid only through `DeveloperBootstrapPrincipal` / `AuthorisationBootstrapPort` during initial setup. Tests should assert the refined semantics.

### H4-07 - `ROADMAP.md` is not truly regenerated to v1.3

Although the roadmap header claims v1.3 regeneration, active sections still cite `ARCHITECTURE.md v1.1`, `SopTemplateLibrary`, `DeveloperPrincipal`, and `T-309b`, including in Phase 2, Phase 8b, Phase 9b, and Phase 11 material.

**Correction:** regenerate the whole roadmap from the v1.3 agenda, not only the Phase 8/9 legacy appendices and Phase 13 wording. Add a stale-token check against active roadmap content.

### H4-08 - Task-board and Appendix C arithmetic still drift

Appendix C says the removed `app.protocol_orchestrator` (`T-805`) row has been removed, but the row remains. The actual section-2 task headings total 66 tasks from Phase 2 through Phase 13, while `TASK_BOARD.md` claims "9 done / 67 main tasks"; including Phase 0 and Phase 1 totals gives 75, not 67.

**Correction:** make task counts produced by a real script checked into the repo. Add a CI assertion that section-2 headings, Appendix C rows, and `TASK_BOARD.md` totals agree.

### H4-09 - PDF/font reproducibility is not robust enough for the target environment

`T-201` adds a `pdf` extra and canonical fonts, but the CI matrix has no `core+dev+pdf` job. It also allows fonts to be downloaded at `uv sync` time, which makes reproducibility depend on network availability and upstream font bytes.

**Correction:** add a `core+dev+pdf` CI job on Linux and Windows, pin OS-level WeasyPrint/Pango/Cairo dependencies, commit or content-address fonts with license metadata, and make network font download a separate audited bootstrap command.

### H4-10 - `AuditKeyProvider.current_key()` exposes raw HMAC key material to runtime code

`T-312a` defines `current_key() -> KeyMaterial`, and `T-313` says the broker appends through `AuditKeyProvider.current_key()`. This exposes raw institutional HMAC key bytes to Python application code.

**Correction:** prefer provider methods such as `mac(message)`, `verify(key_version, message, mac)`, and `rotate(...)` so key bytes remain inside the keystore adapter where possible. If raw bytes must be exposed for a dev backend, constrain that to test/file-keystore modes and document the production threat model.

## Moderate Findings

### M4-01 - `SopTemplateLibrary` remains a canonical catalogue port beside the new SOP-template ports

The port inventory still lists `SopTemplateLibrary` as catalogue port 5, while v1.3 adds `SopTemplateReadPort`, `SopTemplateAdminWritePort`, and `SopTemplateBootstrapPort`. Keeping both read surfaces makes it unclear which one is authoritative.

**Correction:** either deprecate `SopTemplateLibrary` explicitly as an alias to `SopTemplateReadPort`, or remove it from the canonical runtime port list.

### M4-02 - Stale task IDs remain outside historical context

The agenda still contains active references to `T-309a`, `T-309b`, and unsplit `T-312` in task cards, section 3, CI tables, traceability rows, and budget context. This undermines the B3-08 single-identity fix.

**Correction:** stale-token scan active content and allow old IDs only inside explicitly marked historical audit sections.

### M4-03 - Generated-manifest claims are not currently verifiable

The agenda and task board claim `docs/task_manifest.yaml`, `docs/module_manifest.yaml`, and `docs/port_manifest.yaml` are generated/committed sources of truth. In the current folder these files are absent. That may be acceptable before Phase 2 implementation, but it makes current "manifest-derived" arithmetic claims unverifiable.

**Correction:** distinguish planned generated files from already-generated authority. If `TASK_BOARD.md` claims manifest-derived counts, include the manifest now or remove the claim until `T-204` runs.

### M4-04 - Dual-control enforcement needs explicit test coverage

The architecture allows administrator-only completion, but also says institutions can enable dual-control flags. The agenda includes an administrator-only happy path and mentions dual-control in a few places, but it lacks explicit positive/negative tests proving `InstitutionalPolicy.dual_control_flags` forces separation when enabled.

**Correction:** add UAT fixtures where the same administrator is rejected under dual-control policy and a distinct reviewer/admin pair is required.

### M4-05 - Admin-service OS-level IPC authorization is underspecified

`T-1103` names Windows named pipes and POSIX sockets, but the test list emphasizes round trips and credential denial, not OS-level ACL/UID ownership enforcement under service accounts.

**Correction:** add tests or manual verification steps for Windows named-pipe ACLs, Linux socket file ownership/mode, service account separation, and non-admin local user denial.

### M4-06 - Review-queue persistence wording mixes append-only and update semantics

`ReviewQueueStore.resolve()` "adds a decision record but never mutates the request", yet statuses include `pending | under_review | approved | denied | expired`. The plan should clarify whether status is materialized state, derived from appended decision rows, or an update column.

**Correction:** model request rows immutable, decision/status rows append-only, and latest status as a derived read model. Test replay from append-only rows.

### M4-07 - Appendix B traceability still attributes SOP-template admin writes to T-803

The traceability row for `T-803` still says `engine.sop_protocol + renderers ... + SOP-template admin writes`, despite v1.3 moving those writes to `T-316`.

**Correction:** regenerate traceability rows after the T-316 split.

### M4-08 - Minor task-card numbering and lifecycle wording drift remains

Examples include `T-201` SOP numbering skipping from 4 to 6 and CI lifecycle rows still labeled v1.2 where v1.3 semantics now apply. These are not functional blockers alone, but they are symptoms of hand-edited plan drift.

**Correction:** run a markdown structural linter over ordered lists, phase headings, version labels, and lifecycle-state tables.

## Scientific Soundness Assessment

The scientific safety model remains conceptually strong: design plan before SOP, screening before operational protocol, active advisory acknowledgement, administrator-controlled authorisation profiles, and immutable governance/audit traces are the right primitives for this domain.

The current v1.3 plan is scientifically unsafe to execute as written because the build queue and manifest generator can still place `engine.sop_protocol`, `app.authorisation_decision`, and `app.export_orchestrator` before real screening tasks. This is not a cosmetic ordering error. It can produce a scaffold where operational outputs are implemented and tested against mocks before the safety evidence pipeline exists.

The second major scientific concern is policy enforcement: administrator-only completion is allowed by the requirements, but dual-control mode must be proven by tests for institutions that require it.

## Engineering Rationality Assessment

The broad modular-monolith / hexagonal architecture remains rational. The strongest engineering weakness is sequencing: new cryptographic and audit abstractions are appended after their consumers. That creates circular dependencies and encourages local fakes, direct imports, or bypass shims.

The audit append model needs a simpler executable concurrency design. A lifetime exclusive engine writer plus a separate admin writer with an unnamed lock handoff is too fragile for a legal audit trail.

## Quality-Control Assessment

The QC strategy is ambitious and appropriate in principle: manifest-driven coverage, lifecycle gates, import-linter, traceability, adversarial UAT, and platform tests. In v1.3, however, the QC system is not yet self-consistent:

- the architecture manifest parser depends on nonexistent anchors;
- task-board counts do not match task headings;
- task briefs are required but not generated;
- stale IDs remain in active sections;
- security gates have not been expanded to the new v1.3 attack surface.

The plan needs a "docs-as-code" cleanup pass before coding, otherwise QC gates will encode drift instead of preventing it.

## Target Environment Assessment

The plan correctly acknowledges Windows, OneDrive, non-ASCII paths, SQLite WAL, and spawn-based multiprocessing. That is a strong baseline for the user's likely environment.

Remaining environment risks:

- PDF rendering and canonical fonts are not covered by a dedicated CI profile.
- Font acquisition at `uv sync` time undermines reproducibility.
- Windows named-pipe ACL behavior and POSIX socket permissions need explicit service-account tests.
- SQLite audit locking needs cross-process tests that include engine and admin-service writers, not only concurrent admin clients.

## Required Remediation Order

1. Physically reorder section 2 so Phase 10 precedes Phase 8b and Phase 9b.
2. Move or split `T-313` and `T-314` so their protocols/fakes exist before `T-310` and `T-311`.
3. Redesign audit append concurrency into one executable writer/serialization model.
4. Split `T-316` into early ports and post-catalogue signed persistence/bootstrap.
5. Regenerate section 3, Appendix B/C, `TASK_BOARD.md`, and `ROADMAP.md` from one task manifest.
6. Fix `T-204` manifest generation by adding architecture anchors/modules or changing the manifest authority.
7. Add `DecisionRecordSigner` concrete implementation and key lifecycle ownership.
8. Expand security gates to Reviewer, SOP-template, audit append, and admin IPC bypasses.
9. Add target-environment tests for PDF/font reproducibility and IPC permissions.

## Final Status

v1.3 should be treated as a useful draft, not a coding-ready agenda. The third-round fixes are directionally correct, but their propagation is incomplete. A v1.4 agenda should be produced before Phase 2 starts, with the blocking findings above resolved and machine-verifiable checks added to prevent the same drift pattern from recurring.
