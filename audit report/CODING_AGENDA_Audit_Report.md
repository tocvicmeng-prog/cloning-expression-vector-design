# CODING_AGENDA.md Audit Report

**Audit date:** 2026-05-14  
**Audited document:** `CODING_AGENDA.md` v1.0  
**Primary source of truth:** `ARCHITECTURE.md` v1.5  
**Supporting sources:** `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, `TASK_BOARD.md`  
**Auditor stance:** senior software architect, senior implementation engineer, software quality-control reviewer, and scientific-software reviewer.

---

## Executive Verdict

`CODING_AGENDA.md` is a strong strategic development plan, but it is not yet safe to execute as the authoritative build queue. It correctly absorbs many of the v1.4/v1.5 architectural safety decisions, especially administrator-controlled authorisation, active advisory acknowledgement, three event streams, deterministic fakes, and adversarial UAT. However, the agenda has several execution-blocking defects:

1. A type-placement error places non-operational outputs under `domain.types.sop_protected`, while later forbidding `engine.design_plan` from importing that namespace.
2. Several architecture-critical modules are referenced in wiring or requirements but have no implementation task.
3. The v1.4 screening-before-authorisation-before-SOP pipeline is not reflected in the phase order strongly enough to be implementable without stubs or false confidence.
4. CI gate skeletons are planned to pass with TODO predicates, which conflicts with the architecture's safety-gate intent.
5. Rule-fixture ownership is described in the adversarial review but not carried into the actual T-405 deliverables and acceptance criteria.

**Recommendation:** regenerate or patch `CODING_AGENDA.md` before starting Phase 2 implementation beyond trivial repository bootstrap. T-201 can proceed only after dependency policy is clarified; T-203 and later stubbing should not proceed until the missing modules and type locations are corrected.

---

## Audit Method

I reviewed `ARCHITECTURE.md` as binding, with particular attention to:

- Source-of-truth hierarchy and v1.4/v1.5 binding supplements.
- Top-level architecture, module catalogue, inter-module flow, state machine, four gates, data model, event streams, persistence, performance, testing, and residual risks.
- The v1.4/v1.5 changes: screening-before-SOP sequencing, `domain.ports`, split roles, `CoveredBiologicalScope`, `ScreeningProviderTrustPolicy`, `DecisionRecord`, three event streams, `domain.types.sop_protected`, active advisory acknowledgement, and `no-passive-advisory-bypass-check`.

I then cross-checked `CODING_AGENDA.md` against `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, and `TASK_BOARD.md`, focusing on:

- Scientific soundness and engineering rationality.
- Rigor and robustness of quality-control measures.
- Adaptability to the target programming environment: Python 3.11+, local-first project storage, Windows/PowerShell development, OneDrive project location, future React UI, and adapter-heavy scientific dependencies.

---

## Overall Assessment

| Dimension | Assessment |
|---|---|
| Scientific soundness | Strong intent, but incomplete execution coverage for `engine.vlp_policy`, host compatibility, rule fixtures, threshold calibration, and screening/SOP ordering. |
| Engineering rationality | Strong layering and task discipline, but the build queue omits core modules and contains a type namespace contradiction. |
| Quality-control rigor | Ambitious and mostly well-conceived, but weakened by TODO-passing CI gate skeletons and inconsistent rule-fixture deliverables. |
| Environment suitability | Python ecosystem choice is rational, but Windows/OneDrive path behavior, SQLite locking, optional dependency packaging, and file-watch semantics need explicit tasks and CI coverage. |
| Execution readiness | Not ready as-is. Needs targeted agenda patch before implementation. |

---

## Strengths

1. **Correct source-of-truth posture.** The agenda explicitly says `ARCHITECTURE.md` v1.5 wins over the agenda if they disagree, and task briefs should load only scoped architecture excerpts. That is the right governance model for a large AI-assisted codebase.

2. **Good safety philosophy.** The plan preserves the non-operational `DesignRealisationPlan` versus gated `SopLinkedProtocol` split, administrator-controlled authorisation, active risk-advisory acknowledgement, no passive warning bypass, and adversarial tests for self-elevation.

3. **Appropriate core architecture.** Modular monolith plus hexagonal ports/adapters is suitable for this project. Scientific back ends, screening, vendor checks, SnapGene, and LLM translation are correctly treated as ports.

4. **Good determinism posture.** The agenda emphasizes pinned dependencies, deterministic fakes, `DerivationEnvironment`, canonical JSON, replay, event sourcing, and property tests.

5. **Good development hygiene.** Task briefs, post-execution handovers, a task board, phase gates, and six-dimension audit gates are appropriate for a large, safety-sensitive scientific software effort.

6. **Good adversarial UAT intent.** The proposed adversarial UAT suite covers real misuse paths: self-authorisation, role widening, advisory bypass, screening HIT, unsupported tiers, plugin trust, and export redaction.

---

## Blocking Findings

### B-01 - Non-operational types are incorrectly placed in `sop_protected`

**Evidence**

- `ARCHITECTURE.md` says operational protocol types only live in `domain.types.sop_protected`; `DesignRealisationPlan` must not contain a `ProtocolStep` and `engine.design_plan` must not import `domain.types.sop_protected.*` (`ARCHITECTURE.md` around lines 100 and 2059-2064).
- `REQUIREMENTS.md` says `DesignRealisationPlan` is always renderable and non-operational, while only operational types belong in `domain.types.sop_protected` (`REQUIREMENTS.md` lines 300-328).
- `CODING_AGENDA.md` T-306 puts `design_realisation_plan.py`, `control_set.py`, and `risk_advisory.py` under `src/domain/types/sop_protected/` (`CODING_AGENDA.md` lines 401-412).
- `CODING_AGENDA.md` T-802 then says `engine.design_plan` cannot import `domain.types.sop_protected` (`CODING_AGENDA.md` line 584).

**Impact**

This makes the implementation internally impossible:

- `engine.design_plan` must generate `DesignRealisationPlan`, but the agenda places the type in a namespace it forbids `engine.design_plan` from importing.
- `ControlSet` and `RiskAdvisoryReport` are produced at compile time before SOP authorisation; placing them in `sop_protected` falsely classifies non-operational artefacts as operational.
- The import-linter gate would either fail correct code or force developers to weaken the safety rule.

**Required correction**

Move types as follows:

- `domain.types.design_plan`: `DesignRealisationPlan`, non-operational verification artefacts, reviewer packet summaries.
- `domain.types.controls`: `ControlSet`, `ControlDesign`.
- `domain.types.risk_advisory`: `RiskAdvisory`, `RiskAdvisoryReport`.
- `domain.types.sop_protected`: only `ProtocolStep`, `ProtocolDAG`, `SopLinkedProtocol`, and operational hazard/quantity/temperature/duration/deviation types.

Then update T-306, T-801, T-802, T-804, import-linter contracts, and the traceability table.

**Verification**

Add a static test that `engine.design_plan` imports only non-operational type packages, and a negative mypy/import-linter fixture proving `DesignRealisationPlan` cannot reference `ProtocolStep`.

---

### B-02 - The build queue omits architecture-critical modules

**Evidence**

`ARCHITECTURE.md` lists modules that are necessary for correctness:

- `engine.session` for design-session state machine, event sourcing, and snapshots (`ARCHITECTURE.md` line 289).
- `engine.compatibility` for role-keyed host/design compatibility (`ARCHITECTURE.md` line 282).
- `engine.vlp_policy` for MS2/VLP/phage-derived design policy (`ARCHITECTURE.md` line 287).
- `adapter.persistence` for `ProjectStore`, `EventLog`, and `AuditLog` (`ARCHITECTURE.md` line 326).

`CODING_AGENDA.md` references these concepts in wiring and tests but does not provide implementation cards:

- `engine.session` is listed as an event writer and replay target, but there is no T-card implementing it (`CODING_AGENDA.md` lines 884, 894, 968, 1186).
- `SqliteProjectStore`, `JsonlEventLog`, `SqliteAuditLog`, and `SqliteAuthorisationStore` are used in `compose_engine`, but no persistence implementation task exists (`CODING_AGENDA.md` lines 804-809, 894-900).
- `engine.compatibility` is required by architecture and requirements but has no task in the agenda.
- `engine.vlp_policy` is required by v1.4 M9, but the agenda only schedules `MS.yaml` and UAT coverage, not the policy engine.

**Impact**

The agenda's "module catalogue - build queue" is incomplete. Without these modules:

- The state machine and four gates have no executable owner.
- Replay determinism and snapshot bisection are underspecified.
- FR-HOST compatibility can regress into scattered predicates instead of a coherent host-role engine.
- MS2/VLP scientific policy is reduced to manifest entries without the policy module the architecture explicitly added.
- Persistence and audit integrity cannot be verified.

**Required correction**

Add explicit implementation cards before dependent phases:

- T-309: `engine.session` state machine, event replay, snapshotting, session transitions, gate states.
- T-310: `adapter.persistence` implementations: `SqliteProjectStore`, `JsonlEventLog`, `SqliteAuditLog`, `SqliteAuthorisationStore`.
- T-504: `engine.compatibility`, including role-keyed `HostContext` checks and host-threshold profile resolution.
- T-506 or T-804b: `engine.vlp_policy`, consuming `MS.yaml` and exercising VLP-specific constraints.
- T-604 or T-805b: `app.design_service` / session orchestration entry points.
- T-406f or T-807: `app.plugin_governance`, because it is part of the v1.4 plugin-trust mitigation.

**Verification**

Add a "module coverage check" CI gate: every module in `ARCHITECTURE.md` section 4.2 must map to at least one task card with files, tests, and acceptance criteria.

---

### B-03 - Phase order conflicts with screening-before-SOP architecture

**Evidence**

- `ARCHITECTURE.md` v1.4/v1.5 requires: compile produces no SOP; screening completes first; authorisation evaluates after screening; SOP renders only after `OperationalProtocolAuthorised` (`ARCHITECTURE.md` line 84 and state-machine section around lines 539-569).
- `REQUIREMENTS.md` FR-PROTO-SOP-01 requires acceptable screening verdict before SOP rendering (`REQUIREMENTS.md` line 319).
- `CODING_AGENDA.md` schedules `engine.sop_protocol`, `app.protocol_orchestrator`, `app.advisory_acknowledgement`, and `app.authorisation_decision` in Phase 8 (`CODING_AGENDA.md` lines 574-610).
- It schedules screening adapters and `app.screening_orchestrator` in Phase 10 (`CODING_AGENDA.md` lines 628-644).

**Impact**

Phase 8 cannot truthfully complete the SOP and authorisation flow because the screening result model, trust policy behavior, batch semantics, and sign-off flows are not implemented until Phase 10. This creates two bad implementation paths:

- Phase 8 implements authorisation with placeholder screening, then later rewrites gate logic.
- Phase 8 marks safety behavior "green" without a real `ScreeningCompleted` contract.

Either undermines the architecture's central v1.4 safety correction.

**Required correction**

Choose one of these corrections:

1. **Move minimum screening earlier.** Add a Phase 8 prerequisite task that implements `ScreeningResultV14`, `ScreeningError`, `ScreeningProviderTrustPolicy`, `ScreeningCompleted` events, and deterministic fake screening before `app.authorisation_decision`.
2. **Split Phase 8.** Phase 8 implements only `DesignRealisationPlan`, `ControlSet`, `RiskAdvisoryReport`, advisory acknowledgement data types, and SOP templates. Actual `app.authorisation_decision` and `engine.sop_protocol` move after T-1002.

The second option is cleaner if preserving the roadmap phase count matters less than preserving safety semantics.

**Verification**

No task may mark SOP-gating acceptance green until a test fixture supplies a real `ScreeningCompleted` event with policy-derived trust and a verdict branch.

---

### B-04 - CI gate skeletons that pass with TODOs create false safety

**Evidence**

- T-204 says each safety gate script parses repository state and returns exit code 0/1, but the stub returns 0 with a TODO (`CODING_AGENDA.md` lines 332-336).
- Architecture describes these gates as release-blocking safety controls, including `no-self-authorisation-check`, `sop-after-gates-check`, `llm-output-policy-check`, `plugin-manifest-signature`, and `no-passive-advisory-bypass-check` (`ARCHITECTURE.md` lines 2282-2298).
- The agenda also states every CI gate's adversarial fixture should exist before the gate is release-blocking (`CODING_AGENDA.md` line 770), which conflicts with TODO-passing gates wired into CI.

**Impact**

The dashboard can show "green" for gates that do not enforce anything. That is especially dangerous for:

- Self-authorisation prevention.
- Passive advisory bypass.
- SOP-after-gates reachability.
- Plugin signature enforcement.
- LLM operational-text filtering.

**Required correction**

Define gate lifecycle states:

- `not_implemented`: gate script absent or TODO present; not merge-blocking.
- `informational`: gate runs and reports, but cannot pass safety sign-off.
- `enforced`: gate has fixtures and real predicate; merge-blocking.

Stub scripts should return:

- Exit 0 only under `--informational` mode.
- Exit 1 under `--enforce` if any TODO predicate remains.

`TASK_BOARD.md` should distinguish "planned", "informational", and "enforced green".

**Verification**

Add a meta-test that fails if any merge-blocking CI job contains a TODO marker in `tools/ci_gates/`.

---

### B-05 - Rule-fixture ownership is not carried into the actual T-405 deliverables

**Evidence**

- Architecture requires 100 percent rule-validation coverage: every rule has triggering and passing fixtures (`ARCHITECTURE.md` line 2286).
- The agenda's adversarial review says fixtures are populated in the same task as the rule manifest entry, and the gate flips per rule when the predicate becomes real (`CODING_AGENDA.md` line 1180).
- But T-405's actual file list and acceptance criteria include only rule YAML files plus stub predicates; they do not list fixture files or require triggering/passing fixture presence (`CODING_AGENDA.md` lines 467-473).

**Impact**

The stated scientific quality-control strategy depends on fixtures, but the scheduled task does not require them. This can delay fixture work until Phase 5/6, creating a bottleneck and making scientific review harder because predicate semantics cannot be checked against concrete examples at rule-curation time.

**Required correction**

Update T-405 deliverables per category:

- `tests/fixtures/rules/<category>/triggering/<rule_id>.json`
- `tests/fixtures/rules/<category>/passing/<rule_id>.json`
- `tests/fixtures/rules/<category>/README.md` explaining biological rationale and expected predicate result.

Update rule manifest schema so each rule's `test_fixtures` paths must resolve at load time.

**Verification**

The Phase 4 gate should fail if any manifest rule lacks fixture references. The Phase 5/6 gate should fail if any real predicate lacks both passing and triggering assertions.

---

## High-Severity Findings

### H-01 - v1.4/v1.5 port split is not fully represented in task cards

**Evidence**

`CODING_AGENDA.md` wiring uses names such as `RiskAdvisoryCatalogue`, `InstitutionalPolicy`, `AuditLog`, `AuthorisationReadPort`, and `AuthorisationAdminWritePort` (`CODING_AGENDA.md` lines 791-809 and 977). The adversarial review also adds an optional `Lifecycle` protocol (`CODING_AGENDA.md` lines 1211-1213). These are not explicitly scheduled in T-203 or the Phase 3/4 type tasks.

**Impact**

Developers may stub older v1.1 `AuthorisationStore` or adapter contracts instead of the v1.4 split ports. This risks API churn and undermines import-linter boundaries.

**Correction**

T-203 should include an explicit v1.5 port inventory:

- `AuthorisationReadPort`
- `AuthorisationAdminWritePort`
- `AuthorisationBootstrapPort`
- `AuditLog`
- `RiskAdvisoryCatalogue`
- `InstitutionalPolicyCatalogue`
- `ExportProfileCatalogue`
- `PluginManifestRegistry`
- `Lifecycle`
- `RefreshingAdapter`

Each port should be traced to architecture lines and test fixtures.

---

### H-02 - SnapGene `.dna` input support is not scheduled at the right level

**Evidence**

- Architecture standards-first objective includes SnapGene `.dna` I/O (`ARCHITECTURE.md` line 79), and adapter I/O explicitly includes SnapGene `.dna` read-only (`ARCHITECTURE.md` line 319).
- `REQUIREMENTS.md` FR-INT-02 and FR-IO-02 require read-only `.dna` input (`REQUIREMENTS.md` lines 127 and 335).
- `ROADMAP.md` Phase 3 includes `SnapGeneDnaReader` under `adapter.io` (`ROADMAP.md` line 136).
- `CODING_AGENDA.md` T-308 implements GenBank, FASTA, and SBOL3 only; `dna_reader.py` appears later under T-902 SnapGene file watcher (`CODING_AGENDA.md` lines 424-433 and 618-621).

**Impact**

The agenda conflates file-format input support with SnapGene file-watch integration. `.dna` read-only parsing is a core I/O requirement, not only a Phase 9 watcher detail.

**Correction**

Add T-308e: `adapter.io.SnapGeneDnaReader`, with graceful fallback messaging when proprietary parsing is unavailable. T-902 should depend on it, not own it.

---

### H-03 - `engine.compatibility` absence weakens host-scientific validation

**Evidence**

- `ARCHITECTURE.md` requires `engine.compatibility` to iterate over role-keyed host contexts (`ARCHITECTURE.md` line 282).
- `REQUIREMENTS.md` UR-06 and FR-HOST require automatic compatibility evaluation and a machine-readable set of checks (`REQUIREMENTS.md` lines 109 and 245).
- `CODING_AGENDA.md` includes host catalogues and validation predicates, but no `engine.compatibility` implementation card.

**Impact**

Host compatibility could become a loose set of predicate fragments rather than a coherent role-keyed engine. This is scientifically risky for plant, viral, VLP, mammalian, and multi-host workflows.

**Correction**

Add a dedicated `engine.compatibility` task before validation predicates are finalized. It should own:

- Role-keyed iteration over `HostContext`.
- `HostCompatibilityConstraints` evaluation.
- Threshold profile resolution by host and role.
- Fixture coverage for plant transient, lentivirus, AAV, VLP, and cell-free cases.

---

### H-04 - `engine.vlp_policy` is required by architecture but missing from the agenda

**Evidence**

- `ARCHITECTURE.md` v1.4 adds `engine.vlp_policy` for MS2/VLP/phage-derived design policy (`ARCHITECTURE.md` line 287).
- `ROADMAP.md` highlights `engine.vlp_policy` as a v1.4 addition (`ROADMAP.md` line 69).
- `CODING_AGENDA.md` schedules `MS.yaml` and MS2/VLP UAT but no implementation task for `engine.vlp_policy`.

**Impact**

The project may have MS rules without the policy module that distinguishes MS2 RNA-binding display, phage-derived VLPs, AAV, and lentiviral vectors. That is a scientific/safety gap because these systems differ in packaging, helper functions, replication competence, and cargo constraints.

**Correction**

Add an `engine.vlp_policy` card, likely in Phase 5 or 8, with tests tied to `MS.yaml` and the MS2/VLP UAT. Do not rely on manifest-only coverage.

---

### H-05 - Persistence and audit stores are under-specified for implementation

**Evidence**

- Architecture persistence includes `project.sqlite`, separated design/governance/export JSONL logs, `audit.sqlite`, `authorisation.sqlite`, snapshots, catalogues, exports, and locking (`ARCHITECTURE.md` lines 2188-2247).
- `CODING_AGENDA.md` wiring uses these stores (`CODING_AGENDA.md` lines 804-809 and 894-900).
- No task implements SQLite schemas, migrations, append-only semantics, file locks, tamper detection, or snapshot storage.

**Impact**

Replay determinism, audit integrity, authorisation enforcement, and crash consistency cannot be validated. These are central to both scientific reproducibility and safety governance.

**Correction**

Add `adapter.persistence` tasks with:

- SQLite schema migrations.
- Append-only event writers with fsync/atomic append strategy.
- Audit-log tamper detection.
- Read-only enforcement tests for user/engine roles.
- Snapshot schema keyed by `DerivationEnvironment.hash()`.
- Crash-recovery tests.

---

### H-06 - Canonical JSON determinism is underspecified

**Evidence**

`CODING_AGENDA.md` T-307 says canonical JSON is "deterministic, recursive sort by key bytes" (`CODING_AGENDA.md` lines 419-421). Architecture relies on byte-identical replay and hashes throughout.

**Impact**

Sorting keys is not enough for robust cross-platform canonicalization. Edge cases include:

- Floating point normalization.
- `Decimal` versus float.
- NaN/Infinity rejection.
- Time zone and timestamp precision.
- Unicode normalization.
- Enum representation.
- Dict keys that are not strings.
- Tuple/list equivalence.

**Correction**

Adopt a formal canonicalization policy, ideally RFC 8785-style JSON Canonicalization Scheme, with project-specific bans on NaN/Infinity and explicit timestamp/decimal encoding. Add cross-platform golden vectors.

---

### H-07 - Target environment risks are not planned

**Evidence**

The project root and current working directory are under OneDrive and include a localized `文档` path. `REQUIREMENTS.md`, `ARCHITECTURE.md`, and `CODING_AGENDA.md` record the project root under `OneDrive\文档`. The agenda also uses SQLite, file watchers, path-based CI, and generated bundles.

**Impact**

Windows + OneDrive can affect:

- SQLite locks and WAL files.
- Atomic file replacement during sync.
- File-watch debounce behavior.
- Paths with spaces and non-ASCII characters.
- Long path handling.
- Case sensitivity differences.
- PowerShell command quoting.

These are not theoretical for this repo; they match the current working environment.

**Correction**

Add a platform-readiness task before or during T-201:

- CI matrix on `ubuntu-latest` and `windows-latest`.
- Tests under a temp path containing spaces and non-ASCII characters.
- SQLite WAL/locking tests.
- File-watch debounce and atomic-write tests.
- A documented recommendation that active project databases should not live inside a syncing folder unless the app enables a safe lock/backup mode.

---

### H-08 - External scientific dependencies should be optional adapter extras, not core bootstrap dependencies

**Evidence**

T-201 plans to add runtime dependencies including `viennarna`, `primer3-py`, `pysbol3`, `fastapi`, and others at bootstrap (`CODING_AGENDA.md` line 308). Later phases include heavier or licensing-sensitive adapters such as SpliceAI, SignalP, and cloud LLM adapters.

**Impact**

Putting adapter-heavy dependencies into the core environment increases install fragility, especially on Windows and CI. It also blurs the architecture's port/adapter boundary.

**Correction**

Use dependency groups/extras:

- `core`: domain, engine, YAML, pydantic boundary parsing.
- `io`: biopython, pysbol3, snapgene reader.
- `biology-vienna`: ViennaRNA.
- `biology-spliceai`: TensorFlow/SpliceAI or HTTP client only.
- `primer`: primer3-py.
- `api`: FastAPI/uvicorn.
- `ui`: separate package.
- `llm-openai`, `llm-anthropic`, `llm-local`.

T-201 should bootstrap minimal core plus dev dependencies; adapter tasks add their own extras.

---

## Medium-Severity Findings

### M-01 - `ProcessPoolExecutor` in validation needs determinism and Windows constraints

`CODING_AGENDA.md` T-502 requires `ProcessPoolExecutor` for independent rule branches (`CODING_AGENDA.md` line 498). On Windows, process spawning and pickling can be expensive and can reorder result arrival. The plan should require stable result ordering, deterministic exception aggregation, explicit worker seeding, and benchmarks comparing sequential/thread/process modes. It should also ensure functions are picklable and entry points are safe under Windows spawn semantics.

### M-02 - `SLIC` is in scope but not clearly mapped to an assembly strategy

`REQUIREMENTS.md` scope lists SLIC as a supported cloning chemistry (`REQUIREMENTS.md` line 71). The architecture and agenda list LIC, USER, IVA, Gibson-like, In-Fusion, and others, but do not explicitly map SLIC. Add either a SLIC strategy or a documented mapping to `GibsonLikeStrategy`/`LICStrategy` with tests.

### M-03 - Rule-threshold calibration needs stronger task-level acceptance

The adversarial review correctly notes host-context-aware threshold profiles, but most task cards do not require calibration review per threshold. For scientific soundness, each threshold profile should have:

- Source citation.
- Intended host/role scope.
- Default and allowed override range.
- Triggering/passing fixtures near boundary values.
- A reviewer sign-off field.

### M-04 - PDF/Markdown rendering is under-tested

Requirements expect design plans and SOP protocols in Markdown/PDF, but the agenda mostly focuses on data and gate tests. Add renderer tests that inspect output structure, omitted operational fields in design plans, redaction by export profile, and reproducible PDF generation.

### M-05 - Rule stubs returning `INFO` need stronger safeguards

Returning `INFO` from Phase 4 predicate stubs is useful for loadability, but dangerous if any stub survives into later phases. The registry should carry `implementation_status: stub | real`, and any non-stub phase exit should fail if a required rule still points to a stub predicate.

### M-06 - File header traceability may create metadata drift

The required header comments are useful, but placing task IDs and requirement refs in every Python file can become stale during follow-up tasks. Consider generating traceability from `pyproject` metadata, manifest files, or `task_artefacts`, while keeping lightweight module headers in source.

### M-07 - Calibration tests need lifecycle governance

The agenda says calibration drift is nightly and non-release-blocking. That is reasonable, but there must be an escalation policy: what drift magnitude blocks release, who approves baseline refresh, and how refreshed baselines are captured in `DerivationEnvironment.external_database_versions`.

### M-08 - Design-service and decision-tree application tasks are thin or missing

The architecture includes `app.design_service` and `app.decision_tree`. The agenda reaches CLI/API/UI phases without clear implementation ownership for the application use cases that create sessions, collect structured choices, and drive the decision tree. Add task cards before interface work.

---

## Quality-Control Review

### What is robust

- `mypy --strict`, `ruff`, property tests, deterministic fakes, import-linter, and adversarial UAT are appropriate.
- The six-dimension audit is conjunctive, not a weighted vote.
- The agenda explicitly includes replay determinism, snapshot bisection, and event log debugging.
- The active advisory bypass tests are well aligned with v1.5 requirements.

### What must be strengthened

1. CI gates must not pass as TODO stubs.
2. Every architecture module must map to an implementation task.
3. Every rule manifest must carry fixture references at creation time.
4. Phase 8 safety acceptance must depend on actual screening contracts or be deferred.
5. Persistence and audit stores need implementation tasks and crash/tamper tests.
6. Windows/OneDrive/file-watch/SQLite behavior needs explicit platform tests.
7. Canonical JSON must be formalized, not merely described as sorted dicts.

---

## Scientific Review

The agenda's biological scope is broad and mostly aligned with the requirements: bacterial, plant, mammalian, yeast, insect, cell-free, viral/vector systems, cloning chemistries, codon optimization, overhang optimization, primer design, host compatibility, screening, and controls.

The strongest scientific aspects are:

- Rule registry separated from predicate code.
- Source-grade citation gate.
- Host-role-aware model.
- Separate biology adapters with deterministic fakes.
- Calibration tests for adapter drift.
- Explicit controls and validation fixtures.
- Safety separation between design artefacts and operational SOPs.

The scientific weaknesses are:

- Missing `engine.compatibility` and `engine.vlp_policy` tasks.
- Rule fixtures not required by T-405 deliverables.
- Threshold profiles need explicit calibration governance.
- Screening-before-SOP sequencing is not enforceable until screening contracts are implemented.
- SLIC support is not clearly mapped.
- `.dna` read-only input is not scheduled as core I/O.

---

## Engineering Rationality Review

The architecture choice is sound: Python 3.11+ is rational for this domain because of Biopython, pySBOL, ViennaRNA, primer3, and scientific test tooling. A modular monolith is a good fit because the domain is complex but does not yet justify microservices.

However, the agenda should be made more executable:

- Add missing module tasks.
- Split operational/non-operational type packages correctly.
- Move or defer SOP authorisation until screening is implementable.
- Convert the composition root from illustrative pseudocode into an implementation-owned task with lifecycle management.
- Formalize dependency groups and adapter extras.
- Add platform matrix testing.

---

## Adaptability to Target Programming Environment

### Suitable aspects

- Python 3.11+ with `uv` and a lockfile is appropriate.
- `mypy --strict` and frozen dataclasses provide good migration headroom.
- Hexagonal ports make future Rust or service extraction feasible.
- React/TypeScript UI later is appropriate, as long as the CLI/API is tested first.
- SQLite is reasonable for local-first single-user v1.

### Gaps for the actual environment

The current project is on Windows under OneDrive. The agenda should add explicit handling for:

- Non-ASCII path segments.
- Spaces in paths.
- OneDrive sync conflicts.
- SQLite WAL and file-locking behavior.
- Long path support.
- File watcher stability and debouncing.
- Atomic output writes for SnapGene round-trip.
- Windows process-spawn behavior for `ProcessPoolExecutor`.

---

## Required Remediation Plan

Before implementation starts in earnest:

1. Patch T-306/T-801/T-802/T-804 to move non-operational types out of `sop_protected`.
2. Add missing task cards for `engine.session`, `adapter.persistence`, `engine.compatibility`, `engine.vlp_policy`, `app.design_service`, `app.decision_tree`, and `app.plugin_governance`.
3. Re-sequence or split Phase 8 so SOP authorisation depends on real screening contracts.
4. Change T-204 so TODO gates are not treated as passing release-blocking gates.
5. Update T-405 to require triggering and passing fixture files for every rule.
6. Add T-308e for SnapGene `.dna` read-only input.
7. Add canonical JSON formalization and cross-platform golden vectors.
8. Add Windows/OneDrive/SQLite/file-watch platform tests.
9. Add optional dependency groups for adapter-heavy packages.
10. Add a module-coverage CI check mapping architecture modules to agenda tasks.

---

## Go / No-Go

| Area | Decision |
|---|---|
| Start T-201 bootstrap | Conditional go after dependency-group policy is clarified. |
| Start T-202 directory scaffold | Conditional go after missing module directories are added. |
| Start T-203 public API stubs | No-go until v1.4/v1.5 type placement and port inventory are corrected. |
| Start T-204 CI skeletons | No-go as currently written; gate lifecycle states must be corrected first. |
| Start Phase 3+ implementation | No-go until blocking findings are resolved. |

---

## Final Assessment

`CODING_AGENDA.md` is close to a high-quality execution plan, but it currently mixes a very strong architectural safety model with a build queue that is incomplete and occasionally contradictory. The most urgent correction is not scientific content; it is implementation coherence: type namespaces, module coverage, screening/SOP phase ordering, and honest CI gate states.

Once the blocking findings are patched, the agenda will be well positioned for disciplined implementation. As written, it risks producing a scaffold that appears aligned with `ARCHITECTURE.md` v1.5 while encoding enough early inconsistencies to cause expensive rewrites in Phase 3 through Phase 8.

