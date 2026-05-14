# Second-Round Audit of CODING_AGENDA.md v1.1

**Date:** 2026-05-14  
**Auditor stance:** senior software architect, experienced coder, software quality-control reviewer, scientific-software falsification reviewer.  
**Primary file audited:** `CODING_AGENDA.md` v1.1.  
**Required prior input read:** `audit report/CODING_AGENDA_Audit_Response.md`.  
**Reference documents checked:** `ARCHITECTURE.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, and `TASK_BOARD.md` where the agenda claims regeneration or lifecycle integration.

## Executive Verdict

`CODING_AGENDA.md` v1.1 is materially stronger than v1.0. It correctly accepts the prior audit's main direction: non-operational type placement was repaired, missing module task cards were added, SLIC and VLP policy received explicit coverage, rule fixtures were moved into catalogue work, Windows/OneDrive risk was recognized, and CI gate lifecycle states were introduced.

However, the plan is **not yet implementation-ready**. The second-round falsification found several structural defects where the v1.1 response was applied to individual task cards but not propagated through the roadmap, dependency DAG, composition root, event-stream contract, persistence wiring, CI tables, dashboard, and traceability appendices. The most serious residual issue is that export remains scheduled before real screening, authorisation, and SOP rendering, despite the architecture's central safety invariant that screening precedes authorisation, SOP rendering, and final export.

Severity count:

| Severity | Count | Meaning |
|---|---:|---|
| Blocking | 9 | Must be corrected before Phase 2/3 implementation starts, or the scaffold will encode the wrong architecture. |
| High | 11 | Likely to cause major rework, false QC confidence, or failed acceptance if not fixed before the owning phase. |
| Moderate | 9 | Important cleanup to prevent drift, ambiguity, or brittle implementation. |

## Method

I applied adversarial falsification in five passes:

1. **Response-to-agenda verification:** checked whether each accepted finding in `CODING_AGENDA_Audit_Response.md` has a concrete, coherent v1.1 change in `CODING_AGENDA.md`.
2. **Architecture consistency:** checked v1.1 against `ARCHITECTURE.md` v1.5, especially the state machine, safety gates, event streams, and port boundaries.
3. **Requirements consistency:** checked v1.1 against FR-PROTO-SOP, FR-IO, FR-AUTH, FR-ADV, DR-09, and acceptance tests.
4. **Build-order falsification:** walked the phase order and asked whether each acceptance criterion can actually be satisfied when scheduled.
5. **QC falsification:** checked whether CI gates, test plans, task IDs, and the regenerated dashboard would detect the defects they claim to detect.

After the final pass, I found no additional distinct defect classes beyond the findings below.

## Blocking Findings

### B2-01. The roadmap was not regenerated to match the binding v1.1 phase split

**Evidence:** The response says "`ROADMAP` regenerated accordingly" and Phase 8b runs after Phase 10 (`audit report/CODING_AGENDA_Audit_Response.md:83-88`). `CODING_AGENDA.md` states the new order as Phase 7 -> 8a -> 9 -> 10 -> 8b -> 11 (`CODING_AGENDA.md:727-731`). But `ROADMAP.md` still has a single Phase 8 containing design plan, SOP protocol, admin action handler, authorisation store, and advisory workflow (`ROADMAP.md:274-300`), followed by Phase 9 export (`ROADMAP.md:304-323`) and Phase 10 screening (`ROADMAP.md:327-349`).

**Impact:** The plan's own source-of-truth chain is inconsistent. A developer following `ROADMAP.md` will implement SOP/auth before screening, while a developer following `CODING_AGENDA.md` will defer those tasks. This invalidates phase-exit audits and makes "authoritative plan" status unsafe.

**Required correction:** Regenerate `ROADMAP.md` or explicitly demote it for implementation phasing. The roadmap must show 8a, Phase 10 screening, 8b, and final export in a coherent order.

### B2-02. Final export is still scheduled before screening, authorisation, and SOP rendering

**Evidence:** `CODING_AGENDA.md` schedules Phase 9 export before Phase 10 screening and Phase 8b SOP/authorisation (`CODING_AGENDA.md:731`, `CODING_AGENDA.md:816-830`, `CODING_AGENDA.md:832`). Architecture requires screening -> authorisation -> SOP -> export (`ARCHITECTURE.md:390-452`), and requirements say SOP emits only after acceptable screening and authorisation (`REQUIREMENTS.md:319-327`). Requirements also require the bundle to include a screening verdict (`REQUIREMENTS.md:337`).

**Impact:** T-903 cannot satisfy its own acceptance when it runs. At Phase 9, there is no real `ScreeningCompleted` event, no `OperationalProtocolAuthorised` event, no `SopLinkedProtocol`, and no final screening verdict. A Phase 9 export task would either ship an incomplete bundle or fake downstream state, both of which break the architecture's core safety invariant.

**Required correction:** Split Phase 9 into:

- Phase 9a: additional sequence I/O plus SnapGene file-watch channel.
- Phase 9b: final export orchestrator, after Phase 10 and Phase 8b.

Alternatively move T-903 entirely after Phase 8b. Add an explicit "draft/pre-screening design packet" if an early non-operational export is needed, and make it a separate artefact that cannot contain SOP or final vendor/export clearance.

### B2-03. The dependency DAG and composition root remain stale after the phase split

**Evidence:** The agenda's DAG still presents a single Phase 8 with `engine.sop_protocol`, `app.protocol_orchestrator`, and `app.authorisation_decision` before Phase 10 screening (`CODING_AGENDA.md:944-957`). It also still says `engine.assembly (8 strategies)` even though SLIC creates nine strategy families (`CODING_AGENDA.md:937-939`, `CODING_AGENDA.md:711-715`). The composition root constructs SOP, protocol orchestration, screening, admin handling, and export in one stale shape (`CODING_AGENDA.md:986-1077`), but it omits or fails to wire new v1.1 services such as `engine.session`, `engine.compatibility`, `engine.vlp_policy`, `app.design_service`, `app.decision_tree`, `app.plugin_governance`, lifecycle hooks, and a bootstrap/admin write port.

**Impact:** Section 3 is the implementation wiring contract. Because it contradicts the task cards, generated stubs and dependency injection will follow the wrong graph even if individual tasks are corrected. This is the kind of drift a module-coverage gate is supposed to catch, but the current plan would encode the drift before that gate becomes reliable.

**Required correction:** Rewrite `CODING_AGENDA.md` section 3 end-to-end. The DAG, composition root, event-stream table, persistence table, and CI table must all reflect 8a -> 10 -> 8b -> final export, plus every new v1.1 module.

### B2-04. `app.admin_action_handler` is architecture-critical but still has no concrete task card

**Evidence:** Architecture defines `app.admin_action_handler` as the sole write path to the authorisation store, SOP template library, and authorisation-related audit log (`ARCHITECTURE.md:307`, `ROADMAP.md:283`). `CODING_AGENDA.md` references it in T-310 (`CODING_AGENDA.md:530`) and the composition root (`CODING_AGENDA.md:1058`), but there is no `T-*` task card implementing `src/app/admin_action_handler.py`, no admin command acceptance, no bootstrap path, and no task-owned tests for mint/modify/revoke/list/view-audit.

The composition root worsens the issue by passing `authorisation_store: AuthorisationReadPort` into `AdminActionHandler` (`CODING_AGENDA.md:1013`, `CODING_AGENDA.md:1058`), which cannot be the write path the architecture requires.

**Impact:** The authorisation model is impossible to implement safely from the agenda. User self-authorisation cannot be ruled out if the only planned concrete store is read-only and the sole write application service is not owned by a task.

**Required correction:** Add a dedicated task, before any authorisation acceptance can go green, for:

- `src/app/admin_action_handler.py`
- `AuthorisationReadPort`, `AuthorisationAdminWritePort`, and `AuthorisationBootstrapPort`
- SOP template admin-write operations
- admin audit entries
- CLI/API/admin-surface hooks for mint/modify/revoke/list/view-audit
- adversarial tests for User and Reviewer denial

### B2-05. Event-stream wiring conflicts with the architecture's replay contract

**Evidence:** Architecture places `ScreeningCompleted`, `OperationalProtocolAuthorised`, and `SopRendered` in the design event stream (`ARCHITECTURE.md:2148-2159`), while governance stream carries admin, reviewer, plugin, and advisory governance events (`ARCHITECTURE.md:2161-2168`). `CODING_AGENDA.md` instead lists `app.screening_orchestrator` as a governance writer and omits it from the design stream (`CODING_AGENDA.md:1086-1090`). T-806b consumes a real `ScreeningCompleted` event from Phase 10 (`CODING_AGENDA.md:810`), but the event table tells implementers to write it to the wrong stream.

**Impact:** Replay determinism and authorisation gating will diverge. The session state machine rebuilds from design events, but screening verdicts needed for state transitions may be in governance logs. Export and authorisation can silently disagree about the session state.

**Required correction:** Make event ownership explicit:

- `ScreeningCompleted`, `OperationalProtocolAuthorised`, and `SopRendered` belong to the design/session stream if following architecture v1.5.
- Governance stream should carry reviewer/admin/advisory decision records and audit governance.
- Add a cross-stream correlation invariant test: replay design stream plus referenced governance decisions must reproduce the same session state and gate verdicts.

### B2-06. The promised v1.4/v1.5 port inventory fix is not actually present in T-203

**Evidence:** The audit response says H-01 was accepted and T-203c now explicitly lists every split port, plus `tests/ports/test_port_inventory.py` (`audit report/CODING_AGENDA_Audit_Response.md:143`). In the agenda, T-203 remains generic: "Mark every port (`Protocol` class) under `src/domain/ports/`" with no enumerated port inventory, no split authorisation ports, no lifecycle protocol, no refresh protocol, and no `test_port_inventory.py` acceptance (`CODING_AGENDA.md:348-357`).

**Impact:** This leaves the exact defect H-01 was meant to close. Without explicit port names and tests, scaffold generation can omit `AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`, `AuditLog`, catalogue policy ports, plugin registry ports, lifecycle hooks, or refresh hooks and still satisfy T-203 as written.

**Required correction:** Expand T-203c with an explicit inventory and architecture references. The acceptance must include a test that imports every required port and fails if any port is missing or merged into the wrong interface.

### B2-07. CI gate lifecycle is specified in T-204 but contradicted by CI and dashboard tables

**Evidence:** T-204 introduces lifecycle states and says `TASK_BOARD.md` gate rows carry a lifecycle column (`CODING_AGENDA.md:359-370`). But the CI table still marks nearly every gate as blocking "yes" (`CODING_AGENDA.md:1107-1134`) even for gates whose owning implementation occurs many phases later. `TASK_BOARD.md` has no lifecycle column in its gate table (`TASK_BOARD.md:149-163`) and says gates flip from planned to done only when release-blocking and green (`TASK_BOARD.md:177`).

**Impact:** The plan reintroduces the "TODO-green" failure mode in a different form. Either CI blocks early phases on unimplemented gates, or implementers disable the gates ad hoc, which defeats the lifecycle discipline.

**Required correction:** Replace the simple "Blocks merge" column with state-aware behavior:

- `not_implemented`: absent from workflow.
- `informational`: runs with `continue-on-error`.
- `enforced`: merge-blocking.
- `enforced-green`: merge-blocking and observed passing.

Mirror this exactly in `TASK_BOARD.md`.

### B2-08. Audit-log tamper detection lacks key-management design

**Evidence:** T-310 specifies an HMAC chain keyed by an "institutional audit key" (`CODING_AGENDA.md:529`) but no task owns key generation, storage, rotation, backup, access control, compromise response, or multi-user trust boundaries. Architecture requires signed `DecisionRecord` / `RoleSnapshot` and strict separation of duties (`ARCHITECTURE.md:21`, `ARCHITECTURE.md:84`), but the coding agenda gives the HMAC key no lifecycle.

**Impact:** HMAC tamper detection is only meaningful if the key is protected from the actor who can mutate the log. If the key is stored beside the database or broadly readable by the application process, an attacker can rewrite the log and recompute the chain. If the key is lost, audit verification fails irrecoverably. This is a security and governance hole, not an implementation detail.

**Required correction:** Add a security task for audit/key management:

- institutional audit key provisioning
- protected storage or OS keystore integration
- rotation and key versioning
- offline verification procedure
- separation between event signatures and log-integrity HMAC
- tests for key absence, wrong key, rotated key, and tampered row

### B2-09. Phase 8a lacks an application service for the always-renderable design plan

**Evidence:** T-805, the protocol orchestrator that dispatches to `engine.design_plan` always and SOP only when gates pass, is moved to Phase 8b (`CODING_AGENDA.md:752-754`, `CODING_AGENDA.md:801-804`). But `DesignRealisationPlan` is intended to be always renderable before screening (`ARCHITECTURE.md:84`, `ROADMAP.md:281`, `REQUIREMENTS.md:327`). T-903 also expects bundled design artefacts before Phase 8b exists (`CODING_AGENDA.md:827-830`).

**Impact:** The phase split fixed one safety issue but accidentally removed the application entry point for the safe half of the workflow. Implementers may call `engine.design_plan` directly from interfaces or export code, bypassing application-layer event logging and governance.

**Required correction:** Split T-805 into:

- `app.design_plan_orchestrator` in Phase 8a, dispatching design plan, controls, risk advisory, and non-operational notices.
- `app.sop_protocol_orchestrator` in Phase 8b, dispatching SOP only after authorisation.

Or make `app.protocol_orchestrator` a two-phase task with Phase 8a design-only acceptance and Phase 8b SOP acceptance.

## High Findings

### H2-01. Duplicate task headings for moved tasks will break task parsing and traceability

**Evidence:** T-803 and T-805 each appear twice as task headings: once as "MOVED" placeholders and once as real Phase 8b task cards (`CODING_AGENDA.md:743`, `CODING_AGENDA.md:796`, `CODING_AGENDA.md:752`, `CODING_AGENDA.md:801`).

**Impact:** Any task parser, dashboard generator, module-coverage check, or traceability audit scanning task headings can double-count or select the placeholder instead of the real task. This is especially problematic because v1.1 introduced automated coverage checks.

**Required correction:** Remove the duplicate task headings. Use prose notes without `####` task heading syntax, or mark the old positions as cross-reference paragraphs that do not contain a task ID.

### H2-02. Supporting metadata is stale in multiple places

**Evidence:** Phase 2 heading says "4 tasks" but contains T-201 through T-205 (`CODING_AGENDA.md:313-384`). Phase 6 heading says "3 tasks" but contains T-601, T-602, T-603, T-606, and T-607 (`CODING_AGENDA.md:647-693`). The traceability table still assigns T-803 and T-805 to Phase 8, not 8b (`CODING_AGENDA.md:1547-1555`). The context budget table still says `engine.assembly` T-703 has four splits, omitting T-703e SLIC (`CODING_AGENDA.md:1592`).

**Impact:** These are not cosmetic defects. The agenda relies on generated task indices, context budgets, and phase-exit arithmetic. Stale counts hide missing or duplicate work.

**Required correction:** Regenerate all phase counts, traceability rows, budget rows, and dashboard rows from the canonical task list after removing duplicate moved-task headings.

### H2-03. `RiskAdvisoryAcknowledgement` ownership is duplicated between events and domain types

**Evidence:** T-305 implements `RiskAdvisoryAcknowledgement` under domain events (`CODING_AGENDA.md:437-447`), while T-306 implements `RiskAdvisoryAcknowledgement` under `domain.types.risk_advisory` (`CODING_AGENDA.md:454-468`).

**Impact:** Developers can create two incompatible acknowledgement objects: one as an event payload and one as a domain value. That is dangerous because FR-ADV requires content-hash, construct-checksum, signature, and decision semantics to match exactly (`REQUIREMENTS.md:383-387`).

**Required correction:** Define the acknowledgement value object in `domain.types.risk_advisory`; governance events should carry that value object or a typed reference to it. `DecisionRecord` and `RoleSnapshot` ownership should also be stated once.

### H2-04. T-902 still owns `dna_reader.py` despite moving SnapGene parsing to T-308e

**Evidence:** T-308e states it owns the `.dna` read-only parser and T-902 owns file-watch logic only (`CODING_AGENDA.md:498-510`). But T-902 files include `dna_reader.py` (`CODING_AGENDA.md:822-825`).

**Impact:** This reintroduces the ownership conflict H-02 was meant to fix. Two parsers or adapter surfaces may emerge, one under `adapter.io` and one under `adapter.snapgene`.

**Required correction:** Remove `dna_reader.py` from T-902. T-902 should depend on `SnapGeneDnaReader` through a port or injected adapter.

### H2-05. T-606 acceptance requires future phases that do not exist yet

**Evidence:** T-606 is scheduled in Phase 6 but its acceptance requires the full happy path "create -> add parts -> compile -> screen -> authorise -> export" (`CODING_AGENDA.md:677-685`). Screening is Phase 10, authorisation is Phase 8b, export is T-903, and interfaces are later.

**Impact:** The task cannot honestly turn green in Phase 6. This encourages fake downstream stubs or broad integration tests that will churn later.

**Required correction:** Make T-606 acceptance phase-local: create/open/amend/compile/replay with deterministic fakes and explicit pending states for screening/export. Move full happy-path acceptance to Phase 13 or to a post-8b integration task.

### H2-06. T-309 overclaims full gate routing too early in the build

**Evidence:** T-309 implements the complete state machine and all four-gate routing in Phase 3 (`CODING_AGENDA.md:512-521`). But screening adapters, policy verdicts, advisory acknowledgement enforcement, SOP authorisation, and export policy are later phases.

**Impact:** A Phase 3 implementation will either stub safety-critical predicates or freeze early semantics before the real policy modules exist. That creates replay migration pain and false confidence.

**Required correction:** Split T-309:

- Phase 3: state enum, event-sourced replay skeleton, snapshot format, transition table with typed pending predicates.
- Later phases: activate concrete gate predicates when their owning modules land.

The CI lifecycle should reflect predicate maturity per gate.

### H2-07. T-205 tests file-watch debounce before a watcher contract exists

**Evidence:** T-205 schedules a OneDrive-style file-watch debounce test in Phase 2 (`CODING_AGENDA.md:372-384`), but the actual SnapGene file watcher is T-902 in Phase 9 (`CODING_AGENDA.md:822-825`).

**Impact:** The test is either impossible in Phase 2 or will create a throwaway watcher abstraction outside the planned module ownership.

**Required correction:** In T-205, test only generic filesystem primitives using a small test-only debounce harness, or move real watcher debounce acceptance to T-902. State the distinction explicitly.

### H2-08. ProcessPoolExecutor spawn policy is brittle for a library, API server, and Windows

**Evidence:** T-502 says to call `multiprocessing.set_start_method('spawn')` at engine initialisation and to refuse startup without a `__main__` guard (`CODING_AGENDA.md:611-618`). T-205 also requires global spawn semantics (`CODING_AGENDA.md:380`).

**Impact:** `set_start_method()` can only be called once per interpreter, and an importable library or API server may not control process startup. Refusing to initialise without a `__main__` guard is not a viable condition inside FastAPI, tests, or notebook-like contexts.

**Required correction:** Move multiprocessing policy to an executable boundary or worker pool factory. Use `multiprocessing.get_context("spawn")` locally instead of mutating global interpreter state. Keep validation deterministic under sequential fallback.

### H2-09. The dependency-group CI matrix is ambiguous and too heavy for the target environment

**Evidence:** T-201 declares optional groups including TensorFlow/SpliceAI, SignalP wrappers, LLM providers, and UI as a separate package (`CODING_AGENDA.md:322-331`) but the CI matrix includes `core+dev+all` on both Ubuntu and Windows (`CODING_AGENDA.md:333-336`).

**Impact:** `all` is not clearly defined, and if it means all optional dependencies it will pull heavy, licensed, network-sensitive, or platform-fragile components into Windows CI. That undermines the agenda's own target-environment adaptation goal.

**Required correction:** Define install profiles explicitly:

- `core+dev`
- `core+dev+io`
- `core+dev+biology-fakes`
- targeted adapter jobs, usually Linux-only unless the dependency is known Windows-safe
- UI job under its own package manager

### H2-10. SnapGene `.dna` fixtures may have licensing and reproducibility risk

**Evidence:** T-308e requires five reference `.dna` files (`CODING_AGENDA.md:506-509`). `.dna` is a proprietary binary format, and the agenda does not state fixture provenance, license, or how they are generated.

**Impact:** Tests may become non-redistributable, non-reproducible, or blocked in CI. This is especially risky for an open Apache-licensed scaffold.

**Required correction:** Use permissively redistributable synthetic fixtures, document fixture provenance, and keep any proprietary/manual acceptance separate from CI.

### H2-11. `BR-14` is treated as a structural validation predicate

**Evidence:** T-503 lists BR-14 among structural rule predicates (`CODING_AGENDA.md:635-645`). In requirements, BR-14 is the advisory acknowledgement hard gate: missing signed acknowledgement must fire `BlockOperationalProtocol` (`REQUIREMENTS.md:383-387`, `REQUIREMENTS.md:530`).

**Impact:** This mixes a governance/authorisation condition into sequence-analysis validation. The result could be a validation report pretending to evaluate a condition that only exists after risk advisory presentation and signed acknowledgement.

**Required correction:** Remove BR-14 from structural predicates. It belongs to `app.authorisation_decision` and `no-passive-advisory-bypass-check`, with a pure predicate supplied by T-806a.

## Moderate Findings

### M2-01. Replay determinism test ownership is stale

**Evidence:** T-309 and T-310 own event replay, snapshots, and persistence (`CODING_AGENDA.md:512-533`), but the test strategy says replay determinism is tested in T-501 and T-1302 (`CODING_AGENDA.md:1207-1210`).

**Impact:** The replay test may be implemented in the wrong module and miss persistence/session defects.

**Required correction:** Assign replay determinism to T-309/T-310, then reserve T-1302 for end-to-end replay under adversarial fixtures.

### M2-02. FR-ADV-07 adversarial cases are incomplete in the agenda's UAT table

**Evidence:** Requirements demand seven bypass paths, including construct-checksum mismatch and programmatic `OperationalProtocolAuthorised` construction without the acknowledgement chain (`REQUIREMENTS.md:387`). The agenda's adversarial table includes passive render, short justification, unsigned acknowledgement, report-hash mismatch, decline, escalate, and screening cases, but not construct-checksum mismatch or programmatic event construction (`CODING_AGENDA.md:1183-1201`).

**Impact:** A bypass could survive the UAT suite even though T-806b claims "all seven" are covered (`CODING_AGENDA.md:813-814`).

**Required correction:** Add explicit tests for construct-checksum mismatch and programmatic event construction without observed governance history.

### M2-03. Module coverage gate runs too late and parses narrative Markdown

**Evidence:** `module_coverage_check.py` parses `ARCHITECTURE.md` section 4.2 and `CODING_AGENDA.md` section 2, but remains informational until T-310 and only enforces after Phase 3 exit (`CODING_AGENDA.md:367`, `CODING_AGENDA.md:1130`).

**Impact:** Missing tasks in later phases can persist through scaffold and core domain work. Parsing prose Markdown is also brittle: duplicates, moved placeholders, code blocks, or historical architecture notes can create false positives/negatives.

**Required correction:** Enforce a lighter manifest check immediately after T-203 using a generated machine-readable module manifest. Keep the richer task-acceptance check informational until task metadata is complete.

### M2-04. PDF/rendering implementation ownership is under-specified

**Evidence:** Requirements demand SOP Markdown/PDF and optionally JSON (`REQUIREMENTS.md:326-327`). The agenda adds renderer tests (`CODING_AGENDA.md:1211-1221`), but T-803 and T-802 do not identify renderer libraries, output file ownership, font/timestamp controls, or renderer implementation files (`CODING_AGENDA.md:738-741`, `CODING_AGENDA.md:796-804`).

**Impact:** Renderer tests may exist without an owned renderer implementation plan. PDF determinism is particularly fragile unless the renderer, fonts, timestamps, and metadata handling are pinned.

**Required correction:** Add renderer implementation files and deterministic rendering policy to T-802/T-803/T-903, or add a separate renderer task.

### M2-05. Canonical JSON decimal wrapper needs reserved-key collision policy

**Evidence:** T-307 serialises Decimal as `{"$decimal": "12.345"}` (`CODING_AGENDA.md:481-486`) and forbids non-string dict keys but does not reserve `$decimal` or define collision behavior.

**Impact:** A legitimate user or catalogue object containing a `$decimal` key can be ambiguous with a typed Decimal wrapper. This weakens deterministic hashing and cross-language migration.

**Required correction:** Reserve a project type-tag namespace and reject user dictionaries containing reserved keys, or use a structured tagged-union encoding with explicit schema-level disambiguation.

### M2-06. T-502 benchmark ownership is not traceable

**Evidence:** T-502 references `T-502-bench` benchmark and records latency in each adapter manifest (`CODING_AGENDA.md:605-620`), but there is no task card or traceability row for the benchmark. Validation engine benchmarks are not adapter manifests.

**Impact:** Performance data may be inconsistently recorded and not re-run under CI/nightly policy.

**Required correction:** Make the benchmark a named test/benchmark file under T-502, record results in validation-engine performance metadata, and clarify whether it runs on PR, nightly, or release.

### M2-07. `TASK_BOARD.md` contradicts the response's regeneration claim

**Evidence:** The response says `TASK_BOARD.md` was regenerated with a gate lifecycle states column (`audit report/CODING_AGENDA_Audit_Response.md:184`). The actual dashboard gate table has only Gate, Status, and Owning task (`TASK_BOARD.md:149-163`).

**Impact:** The dashboard cannot function as the canonical lifecycle-tracked task index described by the agenda.

**Required correction:** Regenerate `TASK_BOARD.md` from the corrected agenda and include lifecycle state, owning task, current workflow mode, and last observed CI result for each gate.

### M2-08. Architecture source text still exposes split-port ambiguity

**Evidence:** `README.md` and architecture summaries say authorisation ports are split, but the architecture code excerpt still shows a combined `AuthorisationStore` with read and write methods (`ARCHITECTURE.md:860-904`). The response expects T-203 to define split ports anyway (`audit report/CODING_AGENDA_Audit_Response.md:143`).

**Impact:** Implementers may copy the combined protocol and then rely on static checks to distinguish read and write paths, which is weaker than separate interface types.

**Required correction:** Either update `ARCHITECTURE.md` to show the split protocols, or make `CODING_AGENDA.md` explicitly supersede the combined code excerpt with named split ports and tests.

### M2-09. Platform tests need a policy for OneDrive path location versus active sync exclusion

**Evidence:** T-201 warns that project DBs should not live inside actively syncing OneDrive and adds `--db-outside-sync` (`CODING_AGENDA.md:338`), while T-205 requires platform tests under paths with non-ASCII and spaces (`CODING_AGENDA.md:376-384`).

**Impact:** The plan recognizes the local environment but does not define how tests distinguish path compatibility from active-sync database safety. Running SQLite concurrency tests inside an active sync folder can create flaky failures that are environmental, not code defects.

**Required correction:** Add two path fixture classes: sync-like path naming without active sync for CI, and optional manual OneDrive active-sync smoke test marked non-blocking.

## Scientific Soundness and Engineering Rationality Assessment

Scientifically, v1.1 has the right safety posture in concept: design artefacts are separated from operational SOPs, screening is recognized as upstream of authorisation, VLP/MS policy has an owner, and active advisory acknowledgement is no longer passive UI text. The remaining scientific risk is mostly **ordering and ownership**, not domain intent. Export-before-screening, BR-14 as a structural predicate, event-stream mismatch, and missing admin handler ownership are the key defects that would undermine biosafety logic.

Engineering-wise, the plan still needs a full propagation pass. The task-card layer changed faster than the wiring layer. A robust agenda must keep these synchronized:

- Task catalogue
- Phase order
- Dependency DAG
- Composition root
- Event-stream ownership
- Persistence writers/readers
- CI gate lifecycle
- Dashboard state
- Traceability matrix
- Context-budget table

Currently those layers disagree.

## Quality-Control Robustness Assessment

The QC direction is strong but not yet rigorous enough. The lifecycle-state idea is correct, rule fixtures are a major improvement, and platform tests are appropriate for the target Windows/OneDrive environment. But the QC implementation plan still has defects:

- Lifecycle states are not reflected in the actual CI and dashboard tables.
- Module coverage runs too late and parses prose.
- Replay determinism is assigned to the wrong tasks.
- FR-ADV-07 UAT is missing two required bypass tests.
- HMAC tamper detection lacks key-management tests.
- Duplicate task IDs can defeat task-board generation and coverage checks.

## Target Environment Adaptability Assessment

The plan recognizes the target environment better than v1.0: Windows, paths with spaces/non-ASCII characters, long paths, SQLite WAL, OneDrive, and ProcessPool spawn semantics are all explicitly considered. The remaining environment risks are:

- `core+dev+all` CI is too broad for Windows and may install heavy or licensed adapters.
- Global multiprocessing start-method mutation is brittle.
- File watcher tests are scheduled before watcher ownership exists.
- SQLite tests need a clear active-sync policy.
- SnapGene binary fixtures need provenance and redistribution controls.

## Recommended Correction Sequence

1. **Reconcile source-of-truth phasing.** Update `ROADMAP.md`, `TASK_BOARD.md`, and `CODING_AGENDA.md` so they all agree on 8a -> 10 -> 8b -> final export, with Phase 9 split if needed.
2. **Rewrite agenda section 3.** Update dependency DAG, composition root, event-stream table, persistence table, and CI lifecycle table in one pass.
3. **Add missing task cards.** At minimum: `app.admin_action_handler`, split authorisation/bootstrap ports, audit key management, design-plan application orchestrator, deterministic renderers, and event-stream contract tests.
4. **Clean task identity.** Remove duplicate moved-task headings, fix phase counts, update traceability and context-budget tables.
5. **Fix impossible acceptance criteria.** Move full happy-path checks out of Phase 6 and split session/gate activation across the owning phases.
6. **Harden QC.** Implement lifecycle columns in `TASK_BOARD.md`, complete FR-ADV-07, move replay determinism to T-309/T-310, and make module coverage manifest-driven.

## Overall Conclusion

v1.1 is directionally correct but internally inconsistent. The previous audit's findings were accepted, but several fixes stopped at the task-card layer. Before coding starts, the agenda needs a synchronization pass across phasing, wiring, event ownership, CI lifecycle, task identity, and dashboard state. Without that pass, the project risks building a scaffold that looks aligned with `ARCHITECTURE.md` while violating the core safety sequence at runtime.

