# Software Architecture Framework
## Universal Cloning and Expression Vector Design Platform

**Document type:** Authoritative architectural blueprint for downstream development.
**Drafted by:** A three-role collaboration of `/architect`, `/scientific-advisor`, `/dev-orchestrator`. v1.1 also incorporates an external audit by Codex (senior molecular-biology + senior software-architecture reviewer stance), every accepted finding upgraded into this document.
**Date:** 2026-05-13.
**Status:** **Finalised v1.5** — supersedes v1.4 in full. v1.1 incorporated 31/31 first-audit Codex findings. v1.2 incorporates a sponsor sharpening of C1. v1.3 incorporates the role-hierarchy clarification (Administrator ⊇ Reviewer, Reviewer ⊄ Administrator). v1.4 incorporates 31 of 32 findings from the second Codex audit; B3 (administrator-only completion) is defended per sponsor instruction with a new advisory `BiosafetyClassificationLayer` mitigation. **v1.5 incorporates a sponsor strengthening of the B3 mitigation:** advisory warnings must be active, auditable, tied to the design record; the Administrator must receive an explicit warning; the approval trace must be logged; the system must not rely on passive UI warnings. Changes against v1.0 are documented in `audit report/ARCHITECTURE_Audit_Response.md` and `audit report/ARCHITECTURE_Second_Audit_Response.md`.
**Project root:** `C:\Users\tocvi\OneDrive\文档\Project_Code\Cloning_Expression_Vector_Design\`
**Input documents:** `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md`, `Cloning_Expression_Vector_Design_White_Paper.md`, `REQUIREMENTS.md`, `audit report/ARCHITECTURE_Audit_Report.md`, `audit report/ARCHITECTURE_Audit_Response.md`.

---

## Version history

| Version | Date | Summary |
|---|---|---|
| v1.0 | 2026-05-13 | Initial three-role architecture after 4 rounds of falsification. |
| v1.1 | 2026-05-13 | Audit-response upgrade. 31/31 Codex findings accepted; structural changes to data model (SequenceRecord / Location / Feature / ConstructGraph / HostContext), new `engine.sequence_analysis` module, protocol split into design-plan vs SOP-linked, expanded `ValidationRule` manifest, comprehensive `DerivationEnvironment` hash, screening verdict enum expanded, typed `AssemblyPlan` subclasses, typed `DomainEvent` subclasses, two-tier performance budgets, MS-* rule family, four safety gates, source-grade citation gate. |
| v1.2 | 2026-05-13 | Sponsor sharpening of C1's resolution. The authorisation profile governing the operational-protocol hard gate is **administrator-controlled, not user-self-declared**. New `Role` enum (`Developer` / `Administrator` / `Reviewer` / `User`); new typed `AuthorisationProfile` admin-only object; new `AuthorisationStore` port (read-only to the engine); new typed `AdminAction` events; new CI gate `no-self-authorisation-check`; new risk R-16 (user self-elevation). Authorisation lifecycle is recorded in the audit log under strict separation-of-duties. The user **declares an intent** (SOP library, biosafety approval ID, role-of-operation); the gate validates the declaration against the administrator-granted profile; declarations that exceed the profile are rejected. |
| v1.3 | 2026-05-13 | Sponsor clarification on role hierarchy. **`Administrator` capabilities ⊇ `Reviewer` capabilities** (Administrator may perform every Reviewer action including per-construct sign-off on `WATCHLIST` / `MANUAL_REVIEW_REQUIRED` screening verdicts); **`Reviewer` capabilities ⊄ `Administrator` capabilities` (Reviewer may not mint / modify / revoke `AuthorisationProfile` records, may not author institutional SOPs, may not mutate the audit log). Practical consequence: an institution that does not appoint a separate biosafety officer may complete the entire authorisation workflow with an Administrator alone. Implementation: `Principal.can_act_as(role)` predicate with explicit inheritance map; `ReviewerSignedOff` event carries a `signer_role` discriminator so the audit trail records whether a Reviewer or an Administrator-acting-as-Reviewer signed; new requirements FR-AUTH-13 / FR-AUTH-14; new Phase-13 Administrator-only UAT. |
| v1.4 | 2026-05-14 | Second Codex audit response — 31/32 findings accepted, 1 defended (B3 with mitigation). **Pipeline re-sequenced**: SOP rendering moves strictly downstream of screening + authorisation (B2). New advisory **`BiosafetyClassificationLayer`** (`engine.risk_classification` + `catalogues/risk_advisories.yaml`) auto-flags high-risk genetic elements, elevated-biosafety sequences, and constructs that may require institutional approval — surfaces structured warnings to Administrators when granting permissions (B3 mitigation). **`CoveredBiologicalScope`** expands `AuthorisationProfile` with cargo classes, vector system classes, replication competence, insert size, host role, target organism, institutional protocol IDs, jurisdictional constraints, component lineage trust (B4). **`ImportedConstruct` / `AnnotatedConstruct`** I/O contracts preserve full annotation + graph through GenBank / SBOL / SnapGene round-trip (B5). **Structured `Qualifier`** replaces `dict[str, str]` (B6). **`domain.ports/`** package separates port interfaces from adapter implementations; `import-linter` CI gate enforces (B7). **Split authorisation ports** (Read / AdminWrite / Bootstrap) and **split events** (design / governance / export streams) with separate append-only logs (B8, M12). **Signed `DecisionRecord` + `RoleSnapshot`** make sign-offs cryptographically and semantically bound (B9). **`ScreeningProviderTrustPolicy`** moves adapter trust into institution-controlled registry; screening at assembled-product level by default (B10). **Expanded `DerivationEnvironment`** with profile hashes, SOP template content hashes, screening trust policy version, plugin package hashes, LLM prompt template versions, institutional policy version, redaction policy (B11). **Explicit state-machine transitions** after `WATCHLIST` / `MANUAL_REVIEW_REQUIRED` / `UNAVAILABLE` (B12). **`VendorFeasibilityRequest`** (M1). **Five typed hashes** — sequence, topology, annotation, graph, export-bundle (M2). **Formal `Location` algebra** with fuzzy / between-base / join-vs-order / complement / remote / partial / length-invariant semantics (M3). **`ConstructGraph` is canonical**, `feature_table` is a derived view with synchronising invariant (M4). **`HostCompatibilityConstraints`** replaces single-field host compat (M5). **`SecurityRole` vs `OperationalRole` split** so user-declared role-of-operation cannot collide with security identity (M6). **BSL-4 hard block** at compile time; explicit unsupported-tier behaviour (M7). **Wet-lab-success acceptance criteria softened** to in-silico + expert review + dry-run by trained users (M8). **`engine.vlp_policy` + expanded `MS.yaml`** for MS2 / VLP design (M9). **`AdvisoryTextPolicy` + `llm-output-policy-check` CI gate** (M10). **`domain.types.sop_protected` namespace** — `DesignRealisationPlan` cannot by type contain a `ProtocolStep` (M11). **Traceability table in audit-response** with `audit-traceability-check` CI gate (M13). New CI gates: `import-linter`, `llm-output-policy-check`, `audit-traceability-check`, `plugin-manifest-signature`, `sop-after-gates-check`. New risks R-17 (LLM unsafe output), R-18 (plugin trust escalation), R-19 (export PII leak), R-20 (unsupported biosafety tier attempted). |
| **v1.5** | **2026-05-14** | Sponsor strengthening of the B3 mitigation. **Advisory warnings must be active, auditable, tied to the design record; the Administrator must receive an explicit warning; the approval trace must be logged. The system must not rely on passive UI warnings.** Implementation: `RiskAdvisoryReport` carries `design_session_id`, `construct_id`, `construct_checksum`, `report_content_hash`, `advisory_id` per item; presenting an advisory emits an `AdvisoryWarningPresented` governance event (a UI render alone is not sufficient); acknowledgement of any advisory of severity `caution` or `strong_caution` is **mandatory before** `OperationalProtocolAuthorised` can fire and is a typed action requiring justification text + cryptographic signature, recorded as a `RiskAdvisoryAcknowledged` event carrying a signed `DecisionRecord`; UI affords only *acknowledge with justification*, *decline (route to alternative reviewer / dual-control)*, or *escalate (institutional sign-off)* — no "dismiss without action". Declines and escalations are first-class `RiskAdvisoryDeclined` / `RiskAdvisoryEscalated` governance events. New CI gate `no-passive-advisory-bypass-check` statically asserts the authorisation pipeline cannot reach `OperationalProtocolAuthorised` without the matching acknowledgement events. New requirements UR-11, FR-ADV-01..07, BR-14. New risk R-21 (advisory bypass). |

---

## Table of contents

0. Preface — participants, method, source-of-truth hierarchy
1. Architectural objectives
2. Opening proposals (v1.0, retained for historical context)
3. Adversarial review
   3.1 Rounds 1–4 — internal falsification (v1.0)
   3.2 Round 5 — Codex external audit (v1.1)
4. Final architecture (v1.1)
   4.1 Top-level pattern
   4.2 Module catalogue
   4.3 Inter-module data flow
   4.4 Working logic — design pipeline state machine + four safety gates
   4.5 Plugin contracts
   4.6 Data model (canonical schema)
   4.7 Event sourcing and audit
   4.8 Persistence and storage
   4.9 Concurrency and performance — two-tier budgets
   4.10 Testing and verification strategy
5. Resolved open questions
6. Residual risk register
7. Sign-off
8. Appendices

---

## 0. Preface

### 0.1 Participants

| Role | Mandate |
|---|---|
| `/architect` | System structure, module boundaries, plugin contracts, persistence, concurrency, non-functional posture. |
| `/scientific-advisor` | Biological data flow, validation semantics, rule dependencies, host/cargo realities, plugin contracts that interface with biology. |
| `/dev-orchestrator` | Phasing, model-tier-per-module, milestone handover, test strategy, code-quality gates. |
| Codex (external auditor, v1.1 only) | Independent scientific + software-architecture review. |

### 0.2 Method

Each role first authored an opening proposal (§2). Four internal rounds of adversarial falsification produced v1.0 (§3.1). An external audit by Codex then produced 31 findings; all three internal roles accepted all 31 (§3.2 and `audit report/ARCHITECTURE_Audit_Response.md`); v1.1 incorporated every accepted change. The project sponsor sharpened C1's resolution (v1.2). A further sponsor clarification established the role-hierarchy semantics (v1.3). A **second Codex audit** then produced 32 additional findings (`audit report/ARCHITECTURE_Second_Audit_Report_v1_2.md`); the three internal roles accepted 31 and the sponsor defended 1 (B3, with a mitigating advisory `BiosafetyClassificationLayer`); per-finding adjudication is in `audit report/ARCHITECTURE_Second_Audit_Response.md`. v1.4 (current) implements every accepted change.

### 0.3 Source-of-truth hierarchy

For any disagreement on factual matter: **v2.0 KB > white paper > v1.0 primer**. Every architectural choice in this document either cites v2.0 KB by section, or cites a REQUIREMENTS.md item by ID, or is recorded explicitly as a design decision with its rationale.

---

## 1. Architectural objectives

Derived from `REQUIREMENTS.md`, with v1.1 refinements from the audit response:

1. **Universal across hosts.** Bacterial, plant, and mammalian first-class; yeast, insect, cell-free supported. **(v1.1)** Hosts are role-keyed (cloning_propagation, assembly, delivery, producer, expression, target, screening_assay, storage) so multi-host workflows (lentiviral packaging, AAV producer, plant *Agrobacterium*-mediated transient, VLP capsid/cargo split) are first-class.
2. **Universal across chemistries.** Restriction-ligation, Gibson / NEBuilder HiFi, Golden Gate (MoClo / Loop / YTK / GreenGate / GoldenBraid / JUMP / MIDAS), Gateway, LIC, USER, IVA, yeast TAR. Each is a distinct, swappable strategy emitting a typed plan subclass.
3. **Standards-first.** SBOL 3.1.x internally (terms: `Component` / `Sequence` / `SequenceFeature` / `Location`); GenBank, FASTA, SnapGene `.dna` as I/O formats.
4. **Rule registry separated from business logic.** Domain experts edit YAML; engineers register typed predicates; the startup loader validates that every rule manifest entry has a registered predicate and a graded citation.
5. **Plugin contracts for biology back-ends.** RNA folding, splice prediction, signal-peptide prediction, codon optimisation algorithms, screening adapters, synthesis-vendor profiles, SnapGene channel, LLM constraint translator — all plug-in interfaces.
6. **Determinism + provenance.** Same input + same `DerivationEnvironment` = bit-identical output. The `DerivationEnvironment` hash captures *all* inputs that materially change outputs (catalogue versions, adapter configurations, external database versions, SOP templates, locale, units, seeds, container image digest, user overrides, reviewer decisions). Every output bundle carries a complete event log and the DerivationEnvironment.
7. **CLI-first, API-then-UI.** No UI logic creeps into the core.
8. **Wet-lab realism, with safety separation, administrator-controlled gating, and screening-first sequencing. (v1.4)** Two outputs are emitted, not one: a **`DesignRealisationPlan`** (non-operational, always renderable, ready for institutional review) and — only when administrator-granted authorisation gates pass **and** screening has completed — a **`SopLinkedProtocol`** (operational, bound to administrator-approved institutional SOP templates, role-gated). **(v1.4 B2 reordering)** Compile produces *no operational artefact*; it produces only `ConstructGraph`, `ValidationReport`, `DesignRealisationPlan`, `ControlSet`, `RiskAdvisoryReport`, and a `ScreeningRequestPackage`. Screening must complete before the authorisation gate evaluates; the authorisation gate must pass before `engine.sop_protocol` renders. Operational steps for transformation, viral packaging, agroinfiltration, mammalian stable-line generation, and RG2+ workflows render only when **(a)** the user holds an `AuthorisationProfile` granted by an `Administrator` whose `CoveredBiologicalScope` covers the construct's biosafety tier, cargo classes, vector class, host roles, replication competence, insert size, target organism, and institutional approval scope; **(b)** the user has declared intent (SOP library / biosafety approval ID / `OperationalRole`) that lies inside the granted profile; **(c)** screening has returned a verdict ∈ {`CLEAR`, signed-off `WATCHLIST` / `MANUAL_REVIEW_REQUIRED`, policy-permitted `UNAVAILABLE`, justified `NOT_APPLICABLE`}. **The user never self-grants authorisation.** Authorisation lifecycle (grant / modify / revoke) is performed exclusively by `Administrator` (institutional level) or `Developer` (system level via the `AuthorisationBootstrapPort`).

9. **Advisory biosafety classification layer with active, auditable acknowledgement (v1.4 B3 mitigation, strengthened in v1.5).** A new advisory subsystem (`engine.risk_classification` + `catalogues/risk_advisories.yaml`) auto-flags high-risk genetic elements, sequences associated with elevated biosafety levels, and constructs that may require institutional approval. **(v1.5 sponsor strengthening)** The advisory layer is **active, auditable, and tied to the design record** — *never* a passive UI banner:
    - The `RiskAdvisoryReport` is bound to the design session (`design_session_id`), to the exact construct version (`construct_id` + `construct_checksum`), and to the advisory catalogue version + content hash; the report itself carries a `report_content_hash` so it can be replayed deterministically from the audit log.
    - Every individual `RiskAdvisory` carries a stable `advisory_id` within the report so the acknowledgement trail can address each one.
    - Presenting an advisory to the Administrator emits a typed **`AdvisoryWarningPresented`** governance event — a UI render alone is *not* sufficient. The presentation itself is a logged action with timestamp, principal ID, and the IDs of the advisories shown.
    - For any advisory of severity `caution` or `strong_caution`, an **explicit acknowledgement is mandatory before** the `OperationalProtocolAuthorised` event can fire. The acknowledgement is a typed action requiring justification text (≥ 20 characters) + cryptographic signature, recorded as a **`RiskAdvisoryAcknowledged`** governance event carrying a signed `DecisionRecord`.
    - The UI offers only three paths on an advisory warning: **acknowledge** (with justification), **decline** (which routes the construct to an alternative reviewer or dual-control flow), or **escalate** (requiring institutional sign-off). There is no "dismiss without action" affordance.
    - Declines and escalations are themselves first-class governance events (`RiskAdvisoryDeclined`, `RiskAdvisoryEscalated`) recorded in the same governance stream with full context.
    - The full **approval trace** — every advisory presented, every acknowledgement / decline / escalation, every authorisation decision — is persisted in the immutable governance event stream and replayable from the audit log. The trace is included by reference in every exported bundle and is part of the `DerivationEnvironment`.
    - A new CI gate **`no-passive-advisory-bypass-check`** statically asserts the authorisation pipeline cannot advance to `OperationalProtocolAuthorised` without observing the corresponding `RiskAdvisoryAcknowledged` events for every `caution` / `strong_caution` advisory in the report.
    - This is the documented mitigation under which the platform retains the v1.3 Administrator-only completion path: the scope of this platform is **DNA sequence design**, not direct manipulation of physical biological agents; the advisory layer (now active and auditable) plus the canonical IGSC / IBBIS / SecureDNA screening hook collectively cover the informational misuse pathway. Institutions that require stricter dual-control governance may enable `AuthorisationProfile.dual_control_flags` via `InstitutionalPolicy` without an architectural change.
10. **Biosafety as a canonical-screening hook, not a decision.** The platform routes to a configured external screening adaptor and records the verdict. Verdicts are: `clear` / `watchlist` / `hit` / `unavailable` / `not_applicable` / `manual_review_required`. **(v1.4 B10)** Adapter trust is determined by an institution-controlled `ScreeningProviderTrustPolicy`, not by adapter self-declaration. Screening runs at the **assembled-product** level by default; fragment-only screening only when policy explicitly permits it. Fallback adapters can produce at most `manual_review_required`; an internal blacklist never silently produces a `clear`.
11. **Combinatorial libraries are first-class.** `OneOf` and `Variable` parts; the same engine validates and generates plans for both single constructs and libraries. Library expansion is lazy, deterministic, and event-recorded.
12. **(v1.1) Domain-core purity.** The validation engine is pure. **(v1.4 B7)** *All* port interfaces live under `domain.ports/`; the engine layer never names `adapter.*`. The `import-linter` CI gate enforces the contract.
13. **(v1.1) First-class controls.** Positive, negative, and process controls are first-class design outputs bundled with the construct, not afterthoughts in the protocol. **(v1.4 N8)** Control validation rules tied to design intent and host role: positive-control suitability matched on host + chemistry + cargo class; negative-control absence-of-signal; vehicle / mock controls; replicate-structure recommendation.
14. **(v1.4 M11) Operational types live in a gated namespace.** All operational protocol types (`ProtocolStep`, `ProtocolDAG`, hazard / quantity / temperature / duration fields) are defined in `domain.types.sop_protected`. By type, a `DesignRealisationPlan` cannot contain a `ProtocolStep`; the constraint is checked by `mypy --strict` and a runtime guard.
15. **(v1.4 M6) Security role and operational role are disjoint.** `SecurityRole = {Developer, Administrator, Reviewer, User}` identifies principals; `OperationalRole = {propagation, expression, producer, target, screening_assay, storage, delivery, assembly, cloning_propagation}` describes how a User intends to *use* a construct. The user declares an `OperationalRole`; their principal carries a `SecurityRole`. No overlap.
16. **(v1.4 M7) Unsupported biosafety tiers are hard-blocked.** `BiosafetyTier.BSL4` (and any tier the platform declares unsupported) is rejected at compile time with `BlockCompile`; no SOP rendering; no vendor submission; explicit audit event `UnsupportedBiosafetyTierAttempted`; user-facing reason message.

---

## 2. Opening proposals (v1.0, retained for historical context)

(Preserved unchanged from v1.0 — these proposals seeded the falsification process. Round-4 outcomes superseded any contradicting elements.)

### 2.1 `/architect` — overall pattern and layering

Hexagonal architecture (ports & adapters) in a modular monolith. Pure domain core; orchestrating application layer; thin interface layer; pluggable infrastructure. Python 3.11.15 is the pinned implementation interpreter for the bootstrap; web UI later, SQLite per project + YAML catalogues. Plugin discovery via `entry_points` or manifest.

### 2.2 `/scientific-advisor` — biological data flow and domain model

Roles, not labels. Host class is a type parameter. Construct is a directed graph, not a list. Rule dependency graph. Iterative pipelines (codon × validator × assembly) with explicit convergence. First-class biology back-end ports.

### 2.3 `/dev-orchestrator` — phasing, testability, integration

Every module independently testable in isolation. Every output bundle reproducible. Event-sourced design session. Rule registry as a typed declarative artefact. CI gates. Model tier per module. Three-tier test pyramid.

---

## 3. Adversarial review

### 3.1 Rounds 1–4 — internal falsification (produced v1.0)

The internal falsification surfaced and resolved (in summary):

| Round | Defect → resolution |
|---|---|
| 1 | Validation engine treated as flat list → DAG evaluator with declared field reads. |
| 1 | Python determinism not free → pin everything, containerised release build. |
| 1 | Single `AssemblyMethod` signature = god-class → strategy hierarchy with 8 concrete subtypes. |
| 1 | Codon × validator loop oscillates → lexicographic-priority fixed-point with N = 5 cap. |
| 1 | Protocol regen on replay expensive → derived-snapshot caching with provenance hash. |
| 1 | 90 % line coverage insufficient for science → 100 % rule-validation coverage gate. |
| 3 | Combinatorial libraries invisible → `OneOf` / `Variable` / `Override` first-class. |
| 3 | Codon optimiser ignores chemistry forbidden motifs → optimiser accepts forbidden-motif set. |
| 3 | UR-01 SnapGene conflates round-trip with live UX → two-phase split (refined in Round 5). |
| 3 | UR-02 free-text would be placebo → LLM `ConstraintTranslator` with user-confirmed snapshot. |
| 3 | Wet-lab protocols not linear → DAG with `THEN / BRANCH / CHECKPOINT / PARALLEL` edges. |
| 4 | (no further defects) — three roles signed off v1.0. |

### 3.2 Round 5 — Codex external audit (produced v1.1)

Codex's audit (`audit report/ARCHITECTURE_Audit_Report.md`) raised 6 critical, 10 major, and 15 moderate findings. All three internal roles accepted all 31 findings (full per-finding adjudication in `audit report/ARCHITECTURE_Audit_Response.md`). Summary of v1.1 structural changes:

| Finding | v1.1 / v1.2 change |
|---|---|
| C1 — safety vs operational protocol scope | **v1.1**: Protocol split into `engine.design_plan` (always-renderable, non-operational) + `engine.sop_protocol` (gated to institutional SOP library); four safety gates. **v1.2 (sponsor sharpening)**: The authorisation profile governing the `BlockOperationalProtocol` gate is administrator-controlled, never user-self-declared. New `Role` / `Principal` hierarchy, `AuthorisationStore` port with read/write split, `AdminActionHandler` application service, `authorisation.sqlite` admin-only store, `no-self-authorisation-check` CI gate, R-16 risk mitigation set. User declares intent; admin grants the profile that the gate validates against. |
| C2 — "graph" claimed but list implemented | Add `SequenceRecord`, `Location`, `Feature`, `InsertionContext`, `ConstructGraph` to the canonical model. |
| C3 — restriction analysis has no module | Add `engine.sequence_analysis` with `find_sites`, `digest`, `compatible_ends`, `rank_directional_cloning_sites`, `design_diagnostic_digest`, `fragment_simulation`. |
| C4 — host context under-modeled | Replace `host_propagation` / `host_expression` with `hosts: tuple[HostContext, ...]` keyed by role. |
| C5 — validation rule manifest too thin | Expand to include `depends_on_metrics`, `produces_metrics`, `invalidates`, `preconditions`, `target_context`, `external_adapters`, `threshold_profile`, `severity_policy`, `last_reviewed`, `reviewed_by`, `test_fixtures`. |
| C6 — derivation hash incomplete | Replace with `DerivationEnvironment` record covering catalogue versions, adapter configurations, external database versions, SOP templates, locale, seeds, container digest, user overrides, reviewer decisions. |
| M1 — RBS / Kozak dependency example wrong | Replaced with two host-specific chains (bacterial vs mammalian). |
| M2 — sequence type too narrow | Add `Sequence` ADT with `DnaSequence` / `RnaSequence` / `ProteinSequence` / `OligoSequence` sub-types. |
| M3 — assembly plan generic | Add typed `AssemblyPlan` subclasses per chemistry. |
| M4 — codon optimisation input incomplete | Replace `ProteinSequence` input with `CodingSequenceDesign` carrying native DNA, target protein, codon table, protected intervals, target host context, forbidden motifs, functional RNA features, splice constraints, RNA-structure constraints. |
| M5 — screening fallback too casual | Verdict enum expanded; fallback never silently produces `clear`. |
| M6 — SnapGene priority inconsistent | UR-01 split into UR-01a (MUST, file-watch round-trip) and UR-01b (SHOULD, live API). |
| M7 — domain purity contradicted | Adapter-backed metrics moved to application layer; pure validator consumes `ValidationContext`. |
| M8 — protocol step lacks SOP / approval / QC fields | Expanded `ProtocolStep` with `sop_ref`, `approval_gate`, `hazard_class`, `allowed_roles`, `checkpoint_criteria`, `measured_outputs`, `deviation_policy`, `decision_rule`. |
| M9 — performance budgets not separated | Two budget tiers: Core deterministic (release gate) + Production adapter (operational SLA). |
| M10 — catalogue maintenance risk | Per-catalogue maintenance metadata (`retrieved_at`, `valid_until`, `source_url`, `review_required_after`); `stale-catalogue-check` CI gate. |
| Moderate 1–15 | Naming fix (`app.engine.compatibility` → `engine.compatibility`); Library iterator → expansion function; typed `DomainEvent` subclasses; `ProjectStore.list` → `list_sessions`; canonical key order for `ProtocolDAG.steps`; `PartCatalogue.add` moved to application service; SBOL 3 terminology corrected; source-grade citation gate; `screen_batch` partial-failure semantics; expanded `estimate_cost` signature; `PrimerDesignParameters`; `engine.controls` module; `MS-*` rule family; `ACKNOWLEDGED_WARN` / `READY_WITH_WARNINGS` states; four typed safety gates. |

---

## 4. Final architecture (v1.1)

### 4.1 Top-level pattern

A **modular monolith** with **hexagonal (ports & adapters)** layering. Four layers — Interface, Application, Domain Core, Infrastructure — with strictly downward dependencies. Domain core is **pure**; adapter-backed work happens in the application layer; metrics flow into the validator via a `ValidationContext`.

```
┌──────────────────────────────────────────────────────────────────┐
│                          INTERFACE LAYER                         │
│   CLI  │  HTTP / gRPC API  │  Web UI (Phase 12)                  │
└─────────────────────────────────┬────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────┐
│                       APPLICATION LAYER                          │
│   DesignSessionService                                           │
│   DecisionTreeOrchestrator       ConstraintTranslator (LLM)      │
│   ValidationOrchestrator         AssemblyOrchestrator            │
│       (metric pre-compute)       PrimerOrchestrator              │
│   ProtocolOrchestrator           ControlsOrchestrator (NEW)      │
│       (dispatches to design_plan and sop_protocol)               │
│   ExportOrchestrator             ScreeningOrchestrator           │
│   LibraryRealisationService      PartLibraryService (NEW)        │
│       (lazy expansion)               (writes via events)         │
└─────────────────────────────────┬────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────┐
│                          DOMAIN CORE (pure)                      │
│                                                                  │
│   Sequence primitives (NEW):                                     │
│     SequenceRecord • Location • Feature • InsertionContext •     │
│     ConstructGraph                                               │
│   Domain model:                                                  │
│     Part • Module • Construct • Library • Override •             │
│     HostContext (NEW) • AssemblyMethod (hierarchy) •             │
│     AssemblyPlan (typed subclasses, NEW) •                       │
│     ValidationRule (expanded manifest) •                         │
│     ProtocolStep (expanded with SOP/QC/role) •                   │
│     DesignRealisationPlan • SopLinkedProtocol (NEW) •            │
│     ControlSet (NEW) • ScreeningResult (expanded verdict) •      │
│     DomainEvent (typed subclasses) •                             │
│     DerivationEnvironment (NEW) • CodingSequenceDesign (NEW)     │
│                                                                  │
│   Engines (pure):                                                │
│     ValidationEngine (pure, consumes ValidationContext)          │
│     DependencyEngine (DAG over fields × metrics)                 │
│     CodonOptimiser (constraint-aware, CodingSequenceDesign in)   │
│     PrimerDesigner (PrimerDesignParameters in)                   │
│     AssemblyMethodPicker                                         │
│     OverhangSetOptimiser (Pryor / Potapov)                       │
│     CompatibilityChecker (role-keyed)                            │
│     SequenceAnalysis (NEW — restriction, digest, diagnostic)     │
│     DesignPlanGenerator (NEW)                                    │
│     SopProtocolGenerator (NEW, gated)                            │
│     ControlsGenerator (NEW)                                      │
│     LibraryExpander                                              │
│                                                                  │
│   Ports (interfaces):                                            │
│     RnaFolder • SplicePredictor • SignalPeptidePredictor •       │
│     CodonAlgorithm • KozakScorer • TIRPredictor •                │
│     ScreeningAdapter • SynthesisVendorAdapter •                  │
│     SequenceReader / SequenceWriter •                            │
│     SnapGeneChannel • LLMConstraintTranslator •                  │
│     PartCatalogue (read-only) • HostCatalogue • EnzymeCatalogue •│
│     RuleRegistry • SopTemplateReadPort •                    │
│     ProjectStore • EventLog • AuditLog                           │
└─────────────────────────────────┬────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────┐
│                     INFRASTRUCTURE / ADAPTERS                    │
│   IO:           GenBankAdapter • FastaAdapter • Sbol3Adapter •   │
│                 SnapGeneDnaReader • EmblAdapter • Gff3Adapter    │
│   Biology:      ViennaRnaAdapter • SpliceAiAdapter •             │
│                 SignalPAdapter • RbsCalcV2Adapter •              │
│                 NodererKozakAdapter • CAIAdapter •               │
│                 MinMaxAdapter • CharmingAdapter                  │
│   Catalogues:   YamlPartLoader • YamlHostLoader •                │
│                 YamlEnzymeLoader • YamlRuleRegistryLoader •      │
│                 SqliteSopTemplateStore (signed; bootstrapped from YAML) •                    │
│                 YamlVendorProfileLoader                          │
│   Vendors:      TwistAdapter • IDTAdapter • GenScriptAdapter     │
│   Screening:    IgscAdapter • IbbisAdapter •                     │
│                 SecureDnaAdapter • InternalBlacklistAdapter      │
│   SnapGene:     SnapGeneFileWatcher (UR-01a, MUST) •             │
│                 SnapGeneApiClient (UR-01b, SHOULD)               │
│   LLM:          OpenAiAdapter • AnthropicAdapter •               │
│                 LocalLlmAdapter                                  │
│   Persistence:  SqliteProjectStore • FileEventLog •              │
│                 SqliteAuditLog                                   │
│   External tools: Primer3Adapter • RebaseAdapter                 │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Module catalogue

Each module declares: purpose, public API, inputs, outputs, dependencies, model tier (`/dev-orchestrator` convention), REQUIREMENTS items it satisfies.

#### 4.2.1 Domain-core modules

| Module | Purpose | Depends on | Satisfies |
|---|---|---|---|
| **`domain.sequence`** | Sequence primitives: `SequenceRecord`, `Location`, `Feature`, `InsertionContext`. Topology-aware (linear / circular). | — | C2, M2 |
| **`domain.graph`** | `ConstructGraph` with nodes (parts / features / modules) and typed edges (Adjacency / Regulatory / Derivation / Assembly). | `domain.sequence` | C2 |
| **`domain.types`** | Core entities: `Part`, `Module`, `Construct`, `Library`, `Override`, `HostContext`, `Host`, `AssemblyMethod` (abstract), `AssemblyPlan` (typed subclasses), `ValidationRule`, `ProtocolStep`, `ProtocolDAG`, `DesignRealisationPlan`, `SopLinkedProtocol`, `ControlSet`, `ScreeningResult`, `DerivationEnvironment`, `CodingSequenceDesign`. Typed `DomainEvent` subclasses. SBOL-3.1.x-aligned. | `domain.sequence`, `domain.graph` | DR-*, C4, C5, C6, M2, M3, M4, M5, M8 |
| **`domain.library`** | Library expansion. | `domain.types` | UR-04 |
| **`engine.sequence_analysis`** (NEW) | Restriction analysis: site finding, digest simulation, end compatibility, unique-site ranking, diagnostic-digest design, fragment simulation. Topology-aware. | `domain.sequence`, `domain.graph`, `adapter.catalogue.EnzymeCatalogue` (read-only port) | C3, FR-CORE-01..03 |
| **`engine.validation`** | Pure DAG evaluator over `(construct fields × derived metrics)`. Consumes `ValidationContext`. Incremental re-eval. | `domain.types` | FR-VAL-*, MR-*, WR-*, BR-*, C5, M7 |
| **`engine.dependencies`** | Field-and-metric read DAG; affected-rule computation on changeset. | `domain.types` | C5 |
| **`engine.codon`** | Constraint-aware codon optimisation. Accepts `CodingSequenceDesign`. Lexicographic-priority fixed-point. | `domain.types`, `CodonAlgorithm` port | M4, FR-CORE-04..07 |
| **`engine.primer`** | Per-strategy primer design. Accepts `PrimerDesignParameters`. Off-target scan against full plasmid. | `domain.types`, `engine.sequence_analysis`, Primer3 port | FR-PRIM-* |
| **`engine.assembly`** | Strategy hierarchy emitting typed `AssemblyPlan` subclasses. | `domain.types`, `engine.sequence_analysis` | M3, MR-37..41 |
| **`engine.overhang`** | Golden Gate / Type IIS overhang optimiser (Pryor 2020 / Potapov 2018). | `domain.types`, overhang-fidelity dataset | FR-CORE-13 |
| **`engine.compatibility`** | Role-keyed host ↔ design compatibility. Iterates over `HostContext` roles; rules declare which host roles they read. | `domain.types`, HostCatalogue port | C4, FR-HOST-* |
| **`engine.design_plan`** (NEW) | `DesignRealisationPlan` generator: assembly route, required inputs, QC checkpoints, expected verification artefacts, institutional-approvals list, biosafety classification. Always renderable. | `domain.types`, `engine.assembly`, `engine.primer`, `engine.sequence_analysis` | C1 (design half), FR-PROTO-DESIGN-* |
| **`engine.sop_protocol`** (NEW) | `SopLinkedProtocol` generator: gated to institution-supplied SOP templates; renders only when authorisation gates pass. | `domain.types`, `engine.design_plan`, `SopTemplateReadPort` port | C1 (operational half), FR-PROTO-SOP-* |
| **`engine.controls`** (NEW) | First-class control designs (positive / negative / process / library-specific). v1.4 adds mechanistic validation rules tied to host role and chemistry (N8). | `domain.types`, `engine.assembly`, `engine.primer` | Moderate 12; N8 |
| **`engine.risk_classification`** (NEW, v1.4 B3) | Pure module that scans a `ConstructGraph` against `catalogues/risk_advisories.yaml` and emits a `RiskAdvisoryReport` with categorised advisories (high-risk element / elevated BSL / requires approval). Advisory only — does not block. | `domain.types_v1_4`, `domain.ports.RiskAdvisoryCatalogue` | B3 mitigation |
| **`engine.vlp_policy`** (NEW, v1.4 M9) | MS2 / VLP / phage-derived design policy. Constraints for packaging signal handling, capsid expression, helper-function separation, cargo size, replication / infectivity boundary, assembly and assay controls. Distinguishes RNA-binding display systems (MS2), phage-derived VLPs (Qβ, T7), and mammalian viral vectors (AAV, lentivirus). | `domain.types_v1_4`, `catalogues/rules/MS.yaml` | M9 |
| **`engine.sequence_analysis`** (REVISED v1.4 B7) | Same scope as v1.3; dependency renamed from `adapter.catalogue.EnzymeCatalogue` to `domain.ports.EnzymeCataloguePort`. | `domain.types_v1_4`, `domain.ports.EnzymeCataloguePort` | B7 |
| **`engine.session`** | Design-session state machine; event sourcing; typed events; snapshot management. | `domain.types`, EventLog port | FR-PROJ-*, DR-* |

#### 4.2.2 Application-layer modules

| Module | Purpose |
|---|---|
| `app.design_service` | Top-level use cases. |
| `app.decision_tree` | UI flow driver. |
| `app.constraint_translator` | LLM free-text → structured constraints; user confirmation; snapshot. |
| `app.validation_orchestrator` | **(v1.1)** Determines required metrics for the active rule set; calls biology adapters; builds `ValidationContext`; invokes pure validator; caches metrics for incremental re-eval. |
| `app.assembly_orchestrator` | Iterative codon × validator × assembly loop with lexicographic-priority fixed-point convergence. |
| `app.primer_orchestrator` | Wraps `engine.primer` with off-target scanning. |
| `app.protocol_orchestrator` | **(v1.1)** Dispatches to `engine.design_plan` (always) and `engine.sop_protocol` (only when gates pass). |
| `app.controls_orchestrator` (NEW) | Wraps `engine.controls` and bundles control sets into the project ZIP. |
| `app.screening_orchestrator` | Routes to `ScreeningAdapter`. Distinguishes `clear` / `watchlist` / `hit` / `unavailable` / `not_applicable` / `manual_review_required`; never silently upgrades fallback to `clear`. |
| `app.library_realisation` | Expands `Library` to lazy realisations; runs per-construct pipeline; global pool checks. |
| `app.export_orchestrator` | Bundles project ZIP. |
| `app.part_library_service` (NEW) | Writes to part library by emitting `PartAdded` events (replaces v1.0's mutable `PartCatalogue.add`). |
| **`app.admin_action_handler` (NEW in v1.2)** | The sole write-path to `AuthorisationStore`, SOP-template admin write/bootstrap ports, and authorisation-related audit-log entries. Authenticates `AdminPrincipal` or `DeveloperBootstrapPrincipal`; ordinary `DeveloperPrincipal` is bootstrap-only unless explicitly granted by institutional policy; rejects any caller with `SecurityRole.USER` or `SecurityRole.REVIEWER` with `PermissionError`. Emits `AdminActionMinted` / `AdminActionModified` / `AdminActionRevoked` to the **governance event stream** (v1.4 M12). |
| **`app.authorisation_decision` (NEW in v1.4, B2)** | Runs the authorisation gate *after* screening completes. Validates `UserDeclaration` against `AuthorisationProfile.scope` (`CoveredBiologicalScope`, B4); validates `ScreeningCompleted` verdict and any signed `DecisionRecord`(s); checks `RiskAdvisoryReport` acknowledgement where required (B3); emits `OperationalProtocolAuthorised` event on success, `AuthorisationAttemptDenied` on failure. |
| **`app.advisory_acknowledgement` (NEW in v1.4, B3)** | When `RiskAdvisoryReport.overall_recommendation == "strongly_recommend_institutional_approval"`, surfaces the advisory to the Administrator and records the Administrator's acknowledgement as `RiskAdvisoryAcknowledged` governance event with the advisory's citation chain. |
| **`app.export_orchestrator` (REVISED v1.4 N6)** | Applies the chosen `ExportProfile`'s `RedactionPolicy` at serialisation time; emits `ExportProfileRedactionApplied` event before the bundle ZIP is written. |
| **`app.plugin_governance` (NEW in v1.4, N7)** | Loads plugin manifests; verifies signatures against the institutional plugin trust keyring; verifies the loaded artefact's hash matches the manifest; enforces the manifest's declared permissions via the runtime sandbox; emits `PluginManifestApproved` governance event. |

#### 4.2.3 Adapter / infrastructure modules

(One row per adapter family.)

| Module family | Implements port |
|---|---|
| `adapter.io` | `SequenceReader`, `SequenceWriter` for GenBank / FASTA / SBOL 3.1.x / SnapGene `.dna` (read-only) / EMBL / GFF3. |
| `adapter.biology` | `RnaFolder` (ViennaRNA), `SplicePredictor` (SpliceAI / NetGene2 / NNSplice), `SignalPeptidePredictor` (SignalP), `KozakScorer` (Noderer PWM), `TIRPredictor` (RBS Calc v2), `CodonAlgorithm` (CAI / %MinMax / CHARMING / avoid_only). |
| `adapter.catalogue` | `PartCatalogue` (read-only), `HostCatalogue`, `EnzymeCatalogue`, `RuleRegistry`, vendor / screening profile loaders. SOP-template YAML files are bootstrap input only; runtime reads use signed `SopTemplateReadPort` backed by `SqliteSopTemplateStore`. |
| `adapter.vendor` | `SynthesisVendorAdapter` (Twist, IDT, GenScript) with `check`, `auto_partition`, `estimate_cost(*, product_type, scale, cloning_option, currency, quote_date_utc)`. |
| `adapter.screening` | `ScreeningAdapter` (IGSC v3, IBBIS Common Mechanism, SecureDNA, internal blacklist) with `screen` and `screen_batch` returning typed verdicts. |
| `adapter.snapgene` | `SnapGeneFileWatcher` (UR-01a, MUST, Phase 9); `SnapGeneApiClient` (UR-01b, SHOULD, Phase 12). |
| `adapter.llm` | `LLMConstraintTranslator` (local-first default; OpenAI / Anthropic with explicit opt-in). |
| `adapter.persistence` | `ProjectStore` (SQLite, `list_sessions` not `list`), `EventLog` (JSONL), `AuditLog` (SQLite, immutable). |

#### 4.2.4 Interface modules

| Module | Purpose |
|---|---|
| `interface.cli` | Typer-based CLI; commands 1:1 with application services. |
| `interface.api` | FastAPI HTTP server + WebSocket for streaming. |
| `interface.ui` (Phase 12) | React + TypeScript SPA. |
| `interface.audit_service` | Dedicated local audit-service process; owns the only `audit.sqlite` write handle and exposes append-only IPC to engine/admin processes. |
| `interface.admin_service` | Dedicated local admin-service process; owns admin mutation ports and exposes authenticated local IPC to CLI/API/UI admin clients. |

### 4.3 Inter-module data flow

```
   ╭──────────────────────────────────────────────────────────────╮
   │  USER (CLI / API / UI)                                       │
   ╰─────────────┬────────────────────────────────────────────────╯
                 │ NewDesignRequest
                 ▼
   ┌───────────────────────────┐
   │ app.design_service        │
   │  emits SessionStarted     │
   └─────────────┬─────────────┘
                 ▼
   ┌───────────────────────────┐
   │ app.decision_tree         │◄─── adapter.llm
   │  parts + hosts + free-text│     (free-text →
   │  events: PartAdded /      │      structured)
   │  HostSelected (per role!) │
   └─────────────┬─────────────┘
                 ▼ ConstructChanged event
   ┌──────────────────────────────────────────────────────────────┐
   │ app.validation_orchestrator                                  │
   │                                                              │
   │   1. determine required metrics for affected rules           │
   │   2. call biology adapters (RnaFolder, SpliceAI, SignalP,    │
   │       NodererKozak, RbsCalcV2) to compute metrics            │
   │   3. build ValidationContext (construct, metrics, thresholds,│
   │       DerivationEnvironment)                                 │
   │   4. invoke pure engine.validation                           │
   │   5. cache metrics in session for incremental re-eval        │
   └──────────────┬───────────────────────────────────────────────┘
                  │ ValidationReport
                  ▼
   ┌───────────────────────────┐
   │ engine.compatibility      │
   │  host-role-keyed checks   │
   └─────────────┬─────────────┘
                 │ CompatibilityReport
                 │
                 │ HARD-FAIL → BlockCompile
                 │ SOFT-WARN → wait for user ack → ACKNOWLEDGED_WARN
                 │ ALL-PASS → ready to compile
                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ Compile command (v1.4 B2 — produces NO operational artefact) │
   │   ┌─ assembly choice  ──┐                                    │
   │   ├─ codon optimisation │  lexicographic-priority fixed-     │
   │   ├─ primer design      │  point loop (N=5 max)              │
   │   ├─ sequence-analysis  │                                    │
   │   ├─ overhang optim. ───┘                                    │
   │   ▼                                                          │
   │  engine.design_plan         → DesignRealisationPlan (always) │
   │  engine.controls            → ControlSet                     │
   │  engine.risk_classification → RiskAdvisoryReport (v1.4 B3)   │
   │  ScreeningRequestPackage    (assembled construct + scope)    │
   │                                                              │
   │  emits DesignCompiled event                                  │
   │  (NO SopLinkedProtocol; NO operational fields)               │
   └─────────────┬────────────────────────────────────────────────┘
                 │ DesignCompiled
                 ▼
   ┌───────────────────────────┐
   │ app.screening_orchestrator│──► adapter.screening
   │  at ASSEMBLED-PRODUCT     │     (canonical-only per
   │  level (v1.4 B10)         │      ScreeningProviderTrustPolicy)
   │  emits ScreeningCompleted │     (IGSC / IBBIS / SecureDNA)
   │  with structured verdict  │
   └─────────────┬─────────────┘
                 │ ScreeningCompleted
                 │
                 │ hit → BlockExport + BlockVendor + Blocked (terminal)
                 │ watchlist → AwaitingReview → DecisionRecord(watchlist_override)
                 │ unavailable → AwaitingReview → DecisionRecord(screening_exception)
                 │                                   (policy-permit required)
                 │ manual_review_required → AwaitingReview → DecisionRecord(manual_review_signoff)
                 │ not_applicable → requires policy NotApplicableReason
                 │ clear → proceed
                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ app.authorisation_decision  (v1.4 B2 — gate AFTER screening) │
   │   - validates UserDeclaration against AuthorisationProfile   │
   │   - validates CoveredBiologicalScope coverage (B4)           │
   │   - validates ScreeningCompleted verdict + DecisionRecord(s) │
   │   - checks RiskAdvisoryReport acknowledgement                │
   │     (strongly_recommend_institutional_approval requires      │
   │     Administrator acknowledgement to advance)                │
   │   - emits OperationalProtocolAuthorised event                │
   │   - on failure: blocks; no operational artefact produced     │
   └─────────────┬────────────────────────────────────────────────┘
                 │ OperationalProtocolAuthorised
                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ engine.sop_protocol  (v1.4 — renders ONLY post-auth)         │
   │   - reads AnnotatedConstruct + AssemblyPlan + Authorisation- │
   │     Decision; produces SopLinkedProtocol bound to declared   │
   │     institutional SOP templates                              │
   │   - emits SopRendered event                                  │
   └─────────────┬────────────────────────────────────────────────┘
                 │ SopRendered
                 ▼
   ┌───────────────────────────┐
   │ app.export_orchestrator   │──► adapter.vendor
   │  applies ExportProfile    │     (check w/ VendorFeasibilityRequest;
   │   redaction (v1.4 N6):    │      M1)
   │   - InternalAudit         │
   │   - Collaborator          │
   │   - Vendor                │
   │   - PublicationSupplement │
   │  bundles ZIP:             │
   │   GenBank+FASTA+SBOL+     │
   │   primers+controls+       │
   │   design_plan+sop_prot+   │
   │   validation+screening+   │
   │   risk_advisory_report+   │
   │   DecisionRecord(s)+      │
   │   DerivationEnvironment   │
   │  emits Exported event     │
   └─────────────┬─────────────┘
                 ▼
   ╭───────────────────────────╮
   │  USER receives bundle     │
   ╰───────────────────────────╯
```

### 4.4 Working logic — state machine and four safety gates

```
   ╔══════════════════════════════════════════════════════════════╗
   ║  DESIGN SESSION STATE MACHINE (v1.4 — B2 / B12 reordering)   ║
   ║                                                              ║
   ║  Compile produces NO operational artefact. Screening runs    ║
   ║  before authorisation. SOP renders ONLY after authorisation. ║
   ║  Each gated transition produces a signed DecisionRecord.     ║
   ╚══════════════════════════════════════════════════════════════╝

      ┌─────────┐ start ┌─────────────┐ parts added ┌──────────┐
      │  EMPTY  │──────►│ COLLECTING  │────────────►│  DRAFT   │
      └─────────┘       └─────────────┘             └────┬─────┘
                                                         │ change
                                                         ▼
                                                  ┌────────────────┐
                                                  │  VALIDATING    │
                                                  │  (incremental) │
                                                  └───────┬────────┘
                                                          │
                                ┌─────────────────────────┼───────────────────┐
                                ▼                         ▼                   ▼
                          ┌───────────┐            ┌────────────┐       ┌──────────┐
                          │ HARD-FAIL │            │ SOFT-WARN  │       │ ALL-PASS │
                          └─────┬─────┘            └──────┬─────┘       └────┬─────┘
                                │ BlockCompile gate       │                  │
                                │ user must fix           │ user acks        │
                                ▼                         ▼                  │
                          ┌───────────┐         ┌──────────────────┐         │
                          │ ◄── DRAFT │         │ ACKNOWLEDGED_WARN│─────────┤
                          └───────────┘         └────────┬─────────┘         │
                                                         ▼                   │
                                                                  compile    │
                                                       ┌──────────────┐     │
                                                       │  COMPILING   │◄────┘
                                                       │   - codon    │
                                                       │   - primers  │
                                                       │   - assembly │
                                                       │   - controls │
                                                       │   - design   │
                                                       │     plan     │
                                                       └──────┬───────┘
                                                              ▼
                                                   ┌──────────────────────┐
                                                   │READY_WITH_WARNINGS?  │
                                                   │  - if soft warns     │
                                                   │    survived compile  │
                                                   └──────────┬───────────┘
                                                              ▼
                                                       ┌──────────────┐
                                                       │  SCREENING   │
                                                       └──────┬───────┘
                                                              │
                                        ┌─────────────────────┼──────────────────────┐
                                        ▼                     ▼                      ▼
                                  ┌──────────┐       ┌──────────────┐       ┌─────────────┐
                                  │   HIT    │       │  WATCHLIST   │       │    CLEAR    │
                                  │ BlockExp │       │ reviewer     │       │ export OK   │
                                  │ BlockVS  │       │ sign-off     │       │             │
                                  │ BlockOp  │       └──────┬───────┘       └──────┬──────┘
                                  └──────────┘              ▼                      │
                                                     ┌────────────┐                │
                                                     │ UNAVAILBLE │                │
                                                     │ or         │                │
                                                     │ MANUAL_REV │                │
                                                     │ → BlockVS  │                │
                                                     │ + reviewer │                │
                                                     └──────┬─────┘                │
                                                            ▼                      ▼
                                                       ┌─────────┐           ┌──────────┐
                                                       │ BLOCKED │           │ EXPORTED │
                                                       └─────────┘           └──────────┘
```

**v1.4 B2 / B12 extension to the state machine.** The diagram above retains the v1.3 happy-path topology for orientation, but the v1.4 reordering inserts two new states between `COMPILING` and `EXPORTED` and tightens every screening branch:

```
   COMPILING (v1.4)
      produces: ConstructGraph, ValidationReport, DesignRealisationPlan,
                ControlSet, RiskAdvisoryReport, ScreeningRequestPackage.
      DOES NOT produce SopLinkedProtocol. DOES NOT produce any
      operational ProtocolStep / ProtocolDAG.
      emits DesignCompiled event.
            │
            ▼
   AWAITING_SCREENING
            │ assembled-product screening request submitted
            ▼
   SCREENING  (verdict ∈ {CLEAR, WATCHLIST, HIT, UNAVAILABLE,
                           NOT_APPLICABLE, MANUAL_REVIEW_REQUIRED})
            │ emits ScreeningCompleted event
            │
            ├── HIT → BLOCKED (terminal; no ordinary override)
            ├── WATCHLIST              ┐
            ├── MANUAL_REVIEW_REQUIRED ┼─→ AWAITING_REVIEWER_SIGNOFF
            ├── UNAVAILABLE            ┘   (Reviewer or Administrator-
            │                              as-Reviewer issues a signed
            │                              DecisionRecord; UNAVAILABLE
            │                              requires explicit policy)
            │
            ├── NOT_APPLICABLE → requires policy NotApplicableReason
            │                    + audit-logged justification
            │
            ▼ (CLEAR or signed-off branches converge here)
   AWAITING_AUTHORISATION  (v1.4 B2)
      app.authorisation_decision validates:
        - UserDeclaration ⊆ AuthorisationProfile.scope (CoveredBiologicalScope, B4)
        - ScreeningCompleted verdict + DecisionRecord(s) acceptable
        - RiskAdvisoryReport acknowledgement where required (B3)
        - all four safety gates open
      emits OperationalProtocolAuthorised event (or returns to BLOCKED)
            │
            ▼ (only when SOP requested)
   AWAITING_SOP_RENDER
      engine.sop_protocol renders SopLinkedProtocol bound to
      declared institutional SOP templates.
      emits SopRendered event.
            │
            ▼
   READY_TO_EXPORT
      app.export_orchestrator applies ExportProfile redaction (N6),
      bundles ZIP.
      emits Exported event.
            │
            ▼
   EXPORTED
```

Three terminal blocked sub-states:

- `BLOCKED_BY_HIT` — screening returned `HIT`; no ordinary override; override requires policy-controlled exception with dual sign-off.
- `BLOCKED_BY_POLICY` — `AWAITING_AUTHORISATION` returned a policy failure (e.g., user lacks `CoveredBiologicalScope` for the cargo class; institutional approval ID absent for a `requires_signed_institutional_approval` profile).
- `BLOCKED_BY_UNSUPPORTED_TIER` — BSL-4 or any tier the platform declares unsupported (M7) — rejected at `COMPILING` with `BlockCompile` and `UnsupportedBiosafetyTierAttempted` audit event.

**Four typed safety gates** (replaces single "block compile" in v1.0):

| Gate | Trigger | What it blocks |
|---|---|---|
| `BlockCompile` | Any HARD validation rule fails. | Cannot proceed past VALIDATING → COMPILING. |
| `BlockExport` | `ScreeningVerdict.HIT` or unresolved `WATCHLIST` / `UNAVAILABLE` / `MANUAL_REVIEW_REQUIRED`. | Cannot emit project ZIP. |
| `BlockVendorSubmission` | Vendor profile rejects the sequence; or any screening verdict ≠ `CLEAR` and policy requires `CLEAR` for orders. | Cannot route to a synthesis vendor. |
| `BlockOperationalProtocol` | The user's **administrator-granted** `AuthorisationProfile` does not cover the construct's biosafety tier, component set, host class, or assembly chemistry; **or** the user's declared SOP library / biosafety approval ID / role-of-operation falls outside the granted profile; **or** the profile has expired / been revoked. | `engine.sop_protocol` does not render; `engine.design_plan` always renders. |

Each rule declares which gate(s) its HARD severity triggers. Each `ScreeningVerdict` maps to a gate set. The `app.export_orchestrator` consults all four gates before emitting the bundle.

#### Authorisation model — administrator-controlled gates (v1.2)

The `BlockOperationalProtocol` gate is the most consequential of the four because it gates *executable wet-lab output*. To prevent self-elevation, the architecture imposes a strict separation-of-duties model:

```
   ┌────────────────────────────────────────────────────────────────┐
   │  ROLES (strict separation of duties)                          │
   ├────────────────────────────────────────────────────────────────┤
   │  Developer                                                    │
   │    - implements the software                                  │
   │    - publishes new rule predicates, validation rules,         │
   │      catalogue entries, plugin adapters                       │
   │    - can bootstrap an Administrator role on a new install     │
   │    - cannot author institutional SOPs (that is the            │
   │      Administrator's domain at the deployment level)          │
   │                                                                │
   │  Administrator   (Administrator ⊇ Reviewer; v1.3)             │
   │    - deploys the software at an institution                   │
   │    - authors / approves the institutional SOP library         │
   │    - mints, modifies, and revokes AuthorisationProfile        │
   │      records for individual users                             │
   │    - signs the institutional biosafety policy                 │
   │    - MAY perform every Reviewer action: per-construct         │
   │      sign-off on WATCHLIST and MANUAL_REVIEW_REQUIRED         │
   │      screening verdicts (v1.3 — when no separate Reviewer     │
   │      is appointed, the Administrator alone completes the      │
   │      full workflow)                                           │
   │                                                                │
   │  Reviewer (institutional biosafety officer / IBC)             │
   │  (Reviewer ⊄ Administrator; capabilities do NOT inherit       │
   │   upward to the Administrator role; v1.3)                     │
   │    - signs off on WATCHLIST / MANUAL_REVIEW_REQUIRED          │
   │      screening verdicts on a per-construct basis              │
   │    - cannot mint, modify, or revoke authorisation profiles    │
   │    - cannot author SOPs (that is the Administrator's domain)  │
   │    - cannot mutate the audit log                              │
   │                                                                │
   │  User (designer)                                              │
   │    - designs constructs                                       │
   │    - declares intent (SOP-library binding, biosafety          │
   │      approval ID applicable, role-of-operation)               │
   │    - has read-only access to their own AuthorisationProfile   │
   │    - cannot mutate any AuthorisationProfile                   │
   │    - cannot author SOPs                                       │
   │    - cannot widen their own role                              │
   │    - cannot sign off on screening verdicts                    │
   └────────────────────────────────────────────────────────────────┘
```

**Permissions matrix (v1.3).** Asymmetric inheritance: Administrator inherits Reviewer; nothing else inherits anything else. Developer's relationship is unchanged — Developer is a system-level role for bootstrap and rule-registry updates and does not auto-inherit Reviewer's per-construct biosafety sign-off authority.

| Capability | Developer | Administrator | Reviewer | User |
|---|:---:|:---:|:---:|:---:|
| Update software / publish predicates / publish catalogue entries | ✓ | — | — | — |
| Bootstrap an Administrator role on a new install | ✓ | — | — | — |
| Mint / modify / revoke `AuthorisationProfile` records | ✓ (system bootstrap) | ✓ | ✗ | ✗ |
| Author / approve institutional SOP library | — | ✓ | ✗ | ✗ |
| Sign the institutional biosafety policy | — | ✓ | ✗ | ✗ |
| Sign off on `WATCHLIST` screening verdicts | — | ✓ (v1.3) | ✓ | ✗ |
| Sign off on `MANUAL_REVIEW_REQUIRED` screening verdicts | — | ✓ (v1.3) | ✓ | ✗ |
| Read own `AuthorisationProfile` | ✓ | ✓ | ✓ | ✓ |
| Read another user's `AuthorisationProfile` | ✓ | ✓ | ✗ | ✗ |
| Read the authorisation audit log | ✓ | ✓ | ✓ (read-only) | ✗ |
| Mutate the audit log | ✗ (audit log is immutable; only the system can append signed events) | ✗ | ✗ | ✗ |
| Design constructs and declare intent (SOP library, biosafety approval ID, role-of-operation) | ✓ | ✓ | ✓ | ✓ |

**Inheritance predicate.** `Principal.can_act_as(required_role)` returns `True` iff:

```
   principal.role == required_role
   OR (principal.role == Role.ADMINISTRATOR  AND  required_role == Role.REVIEWER)
```

Every code path that previously required a `ReviewerPrincipal` now accepts any `Principal` for which `can_act_as(Role.REVIEWER)` is True — i.e., a `ReviewerPrincipal` *or* an `AdminPrincipal`. Code paths that require `AdminPrincipal` (mint / modify / revoke profile; author SOP templates) accept *only* `AdminPrincipal` or `DeveloperBootstrapPrincipal` — `ReviewerPrincipal` and ordinary post-bootstrap `DeveloperPrincipal` are rejected with `PermissionError`. The inheritance map is one-directional by design; no further inheritance edges are added.

**Practical workflow under v1.3.** A small institution that does not appoint a separate biosafety officer assigns one person the `Administrator` role. That person:

1. Bootstraps the deployment.
2. Authors the institutional SOP library.
3. Mints `AuthorisationProfile` records for the institution's Users.
4. When a User's compile produces a `WATCHLIST` or `MANUAL_REVIEW_REQUIRED` screening verdict, the **same Administrator** reviews and signs off — no separate Reviewer is required.

The `ReviewerSignedOff` event carries a `signer_role: Role` discriminator so the audit log records whether the signer was an institutional `Reviewer` or an `Administrator` acting in reviewer capacity.

**Authorisation lifecycle.**

```
   Administrator opens admin console
              │
              ▼
   Administrator authors / amends AuthorisationProfile for User U:
       - covered biosafety tiers (e.g., BSL-1 only)
       - covered host classes (e.g., E. coli, S. cerevisiae)
       - covered assembly chemistries (e.g., restriction, Gibson)
       - covered SOP libraries (subset of institutional library)
       - profile_valid_from / profile_valid_until
       - revocation_reason (if revoked)
              │
              ▼
   AdminAction event is appended to the immutable audit log:
       - actor: Administrator UUID
       - subject: User UUID
       - change: structured diff of profile
       - timestamp
       - signed (multi-user mode)
              │
              ▼
   AuthorisationStore now serves the updated profile to the engine
              │
              ▼
   User U logs in and designs a construct.
   When User declares intent (e.g., "use SOP library OncologyBSL2-v3.1"),
   the BlockOperationalProtocol gate consults the AuthorisationStore:

     IF declared_intent ⊆ U.profile.granted_capabilities
        AND construct.biosafety_tier ⊆ U.profile.covered_tiers
        AND construct.assembly_chemistry ∈ U.profile.covered_chemistries
        AND construct.host_classes ⊆ U.profile.covered_host_classes
        AND now() ∈ [profile.valid_from, profile.valid_until]
        AND profile.revoked_at IS NULL
     THEN gate.open() → engine.sop_protocol renders
     ELSE gate.block() → engine.sop_protocol does NOT render;
                          engine.design_plan still renders
                          a clear "operational protocol withheld pending
                          administrator approval" notice routes to
                          the Administrator's review queue
```

**Strict invariants enforced by code:**

1. The `User` role has no callable that mutates an `AuthorisationProfile`.
2. The `AuthorisationStore` port exposes `get`, `list_for_admin`, `read_own_profile` to the engine; **writes are only callable from an `AdminAction` handler that itself requires Administrator or Developer credentials**.
3. The CI gate `no-self-authorisation-check` performs static analysis to assert that no `User`-scope code path imports the `AuthorisationStore.write_*` methods.
4. Every modification of an `AuthorisationProfile` produces an immutable `AdminAction` event recorded in the audit log with actor, subject, diff, timestamp, and signature.
5. An expired or revoked profile causes the gate to block immediately; profile freshness is checked on every compile, not cached past `profile.valid_until`.

### 4.5 Plugin contracts (v1.1 signatures)

```python
# domain/ports.py

class ScreeningAdapter(Protocol):
    name: str
    version: str
    canonical: bool                   # True only for IGSC / IBBIS / SecureDNA
    def screen(self, sequence: SequenceRecord, metadata: ConstructMetadata) -> ScreeningResult: ...
    def screen_batch(
        self,
        sequences: list[SequenceRecord],
        metadata: list[ConstructMetadata],
    ) -> list[ScreeningResult | ScreeningError]:
        """Returns a list of equal length, in input order. Partial failures
        produce ScreeningError(partial=True); the orchestrator NEVER aggregates
        errors into CLEAR."""


class SynthesisVendorAdapter(Protocol):
    name: str
    version: str
    profile: VendorProfile

    def check(self, sequence: SequenceRecord) -> VendorCheckReport: ...

    def auto_partition(
        self,
        sequence: SequenceRecord,
        prefer_chemistry: AssemblyMethodId | None,
    ) -> list[Fragment]: ...

    def estimate_cost(
        self,
        sequence: SequenceRecord,
        *,
        product_type: ProductType,          # gene-fragment / clonal-gene / oligo-pool / etc.
        scale: SynthesisScale,              # micro / standard / large / GMP
        cloning_option: CloningOption,      # linear-fragment / pre-cloned-vector / etc.
        currency: Currency,
        quote_date_utc: Date,
    ) -> CostEstimate: ...


class RnaFolder(Protocol):
    def fold(self, rna: RnaSequence, temperature_C: float = 37.0) -> FoldResult: ...


class SplicePredictor(Protocol):
    def predict(self, dna: DnaSequence, host_class: HostClass) -> SpliceReport: ...


class SignalPeptidePredictor(Protocol):
    def predict(self, protein: ProteinSequence, host_class: HostClass) -> SignalReport: ...


class KozakScorer(Protocol):
    def score(self, rna: RnaSequence, atg_pos: int) -> float: ...


class TIRPredictor(Protocol):
    def predict(self, rna: RnaSequence, atg_pos: int) -> TirResult: ...


class CodonAlgorithm(Protocol):
    name: str
    def optimise(self, design: CodingSequenceDesign) -> CodingSequenceResult: ...


class LLMConstraintTranslator(Protocol):
    name: str
    version: str
    def translate(
        self,
        free_text: str,
        design_context: DesignContext,
        constraint_schema: ConstraintSchema,
    ) -> list[StructuredConstraint]: ...


class SnapGeneChannel(Protocol):
    name: str
    version: str
    capabilities: SnapGeneCapabilitySet   # file_watch | live_api
    def push(self, construct: Construct) -> None: ...
    def pull(self) -> Construct | None: ...
    def watch(self, callback: Callable[[Construct], None]) -> Watcher: ...


class PartCatalogue(Protocol):
    """Read-only port. Mutations go through app.part_library_service."""
    def get(self, part_id: PartId) -> Part: ...
    def search(self, query: PartQuery) -> list[Part]: ...


class HostCatalogue(Protocol):
    def get(self, host_id: HostId) -> Host: ...
    def search(self, query: HostQuery) -> list[Host]: ...


class EnzymeCatalogue(Protocol):
    def get(self, enzyme_id: EnzymeId) -> Enzyme: ...
    def compatible_pairs(self, e1: EnzymeId, e2: EnzymeId) -> BufferCompatibility: ...


class RuleRegistry(Protocol):
    def get(self, rule_id: RuleId) -> ValidationRule: ...
    def all(self) -> tuple[ValidationRule, ...]: ...


class SopTemplateReadPort(Protocol):
    """Read-only runtime access to institution-owned, signed SOP templates.

    Implemented by the signed SQLite SOP-template store. Legacy YAML files are
    bootstrap input only and are not read at runtime.
    """
    def get(self, sop_id: SopId) -> SopTemplate: ...
    def search(self, query: SopQuery) -> list[SopTemplate]: ...


class SopTemplateAdminWritePort(Protocol):
    """Admin-service-only mutation surface for signed SOP templates."""
    def write_mint(self, template: SopTemplate, admin: AdminPrincipal | DeveloperBootstrapPrincipal) -> SopTemplateVersion: ...
    def write_modify(self, template: SopTemplate, admin: AdminPrincipal | DeveloperBootstrapPrincipal) -> SopTemplateVersion: ...
    def write_revoke(self, sop_id: SopId, admin: AdminPrincipal | DeveloperBootstrapPrincipal) -> SopTemplateRevocation: ...


class AuthorisationStore(Protocol):
    """Admin-controlled store of AuthorisationProfile records.

    Strict separation of duties:
      - read-only methods are callable from the engine and from User-role code.
      - write methods are callable ONLY from app.admin_action_handler,
        which itself requires Administrator or DeveloperBootstrap credentials
        and records every action in the immutable audit log.

    CI gate `no-self-authorisation-check` statically asserts that
    no User-scope code path imports write_*().
    """
    # Read-only — exposed to engine and User code paths
    def get(self, user_id: UserId) -> AuthorisationProfile: ...
    def read_own_profile(self, principal: Principal) -> AuthorisationProfile: ...
    def list_for_admin(
        self,
        admin_principal: AdminPrincipal,
        query: AuthQuery,
    ) -> list[AuthorisationProfileSummary]: ...

    # Write — Administrator / Developer credentials required;
    # MUST NOT be invoked from User-scope code paths.
    def write_mint(
        self,
        admin_principal: AdminPrincipal,
        target_user: UserId,
        profile: AuthorisationProfile,
        justification: str,
    ) -> AdminActionId: ...

    def write_modify(
        self,
        admin_principal: AdminPrincipal,
        target_user: UserId,
        diff: AuthorisationProfileDiff,
        justification: str,
    ) -> AdminActionId: ...

    def write_revoke(
        self,
        admin_principal: AdminPrincipal,
        target_user: UserId,
        reason: RevocationReason,
    ) -> AdminActionId: ...


class SequenceReader(Protocol):
    formats: list[Format]
    def read(self, source: bytes | Path, fmt: Format) -> SequenceRecord: ...


class SequenceWriter(Protocol):
    formats: list[Format]
    def write(self, record: SequenceRecord, fmt: Format) -> bytes: ...


class ProjectStore(Protocol):
    def save(self, session: DesignSession) -> None: ...
    def load(self, session_id: SessionId) -> DesignSession: ...
    def list_sessions(self, query: SessionQuery) -> list[SessionSummary]: ...


class EventLog(Protocol):
    def append(self, event: DomainEvent) -> None: ...
    def replay(self, session_id: SessionId) -> Iterator[DomainEvent]: ...


class PrimerDesigner(Protocol):
    def design(
        self,
        parts: tuple[Part, ...],
        vector: SequenceRecord,
        strategy: AssemblyMethod,
        parameters: PrimerDesignParameters,
    ) -> PrimerSet: ...


@dataclass(frozen=True)
class PrimerDesignParameters:
    target_tm_C: tuple[float, float] = (55.0, 65.0)
    max_tm_difference_C: float = 3.0
    length_range: tuple[int, int] = (18, 35)
    nn_method: Literal["SantaLucia1998", "Allawi1997", "Sugimoto1996"]
    salt_model: Literal["Owczarzy", "Schildkraut", "Wetmur"]
    monovalent_mM: float = 50.0
    divalent_mM: float = 1.5
    dntp_mM: float = 0.2
    target_oligo_uM: float = 0.25
    modifications: tuple[OligoModification, ...] = ()
    target_product: TargetProduct = TargetProduct.STANDARD
```

Every adapter ships a `Manifest`:

```python
@dataclass(frozen=True)
class Manifest:
    name: str
    version: str
    capabilities: frozenset[Capability]
    config_schema: JsonSchema
    config_hash: Sha256                          # canonical-hash of active config
    measured_typical_latency_ms: float           # M9 production-adapter budget
    measured_max_latency_ms: float
    citations: tuple[GradedCitation, ...]
```

### 4.6 Data model (canonical schema)

> **v1.4 reading order.** The v1.0–v1.3 schema below is *retained* for continuity and orientation. The v1.4 supplement at the **end of this section** carries the structural updates from the second Codex audit: `SecurityRole` vs `OperationalRole` split (M6), structured `Qualifier` (B6), formal `Location` algebra (M3), multi-hash model (M2), `ImportedConstruct` / `AnnotatedConstruct` (B5), `VendorFeasibilityRequest` (M1), `ScreeningProviderTrustPolicy` (B10), expanded `ScreeningResult` + typed `ScreeningError` (N5), signed `DecisionRecord` + `RoleSnapshot` (B9), `CoveredBiologicalScope` + expanded `AuthorisationProfile` (B4), expanded `DerivationEnvironment` (B11), `RiskAdvisoryReport` + `RiskAdvisory` (B3 mitigation), `HostCompatibilityConstraints` (M5), `domain.types.sop_protected` namespace (M11), `ExportProfile` (N6). Where types are shown twice (once in v1.0–v1.3 form, once in v1.4 form), the **v1.4 form is binding**.



```python
# domain/sequence.py

class Alphabet(Enum):
    DNA = "DNA"; RNA = "RNA"; PROTEIN = "PROTEIN"; OLIGO = "OLIGO"

class MoleculeType(Enum):
    DS_DNA = "ds-DNA"; SS_DNA = "ss-DNA"
    MRNA = "mRNA"; GRNA = "gRNA"; OTHER_RNA = "RNA"
    PROTEIN = "protein"
    OLIGO_PRIMER = "primer"; OLIGO_PROBE = "probe"

@dataclass(frozen=True)
class Sequence:
    alphabet: Alphabet
    body: str                             # canonical orientation; uppercase
    validation: SequenceValidationFlags

class DnaSequence(Sequence): ...
class RnaSequence(Sequence): ...
class ProteinSequence(Sequence): ...
class OligoSequence(Sequence): ...

@dataclass(frozen=True)
class SequenceRecord:
    id: SequenceRecordId
    alphabet: Alphabet
    topology: Literal["linear", "circular"]
    molecule_type: MoleculeType
    length: int
    sequence: str                         # canonical-orientation
    checksum: Sha256                      # of canonical sequence (lex-min rotation for circular)

@dataclass(frozen=True)
class Location:
    start: int                            # 0-indexed, inclusive
    end: int                              # half-open
    strand: Literal["+", "-", "."]
    phase: Literal[0, 1, 2, "."]
    circular_wrap: bool = False
    fuzzy_start: bool = False
    fuzzy_end: bool = False
    sub_locations: tuple["Location", ...] = ()

@dataclass(frozen=True)
class Feature:
    role: SequenceOntologyTerm
    qualifiers: dict[str, str]
    locations: tuple[Location, ...]
    parent_sequence_id: SequenceRecordId
    evidence: tuple[GradedCitation, ...]

@dataclass(frozen=True)
class InsertionContext:
    parent_node_id: NodeId
    orientation: Literal["forward", "reverse"]
    junction_sequence: str
    scar: str | None
    phase_effect: int
    accepted_overhang_or_overlap: str | None
    insertion_point: Location


# domain/graph.py

@dataclass(frozen=True)
class GraphNode:
    id: NodeId
    kind: Literal["part", "feature", "module"]
    payload: Part | Feature | Module

class EdgeKind(Enum):
    ADJACENCY = "adjacency"
    REGULATORY = "regulatory"
    DERIVATION = "derivation"
    ASSEMBLY = "assembly"

@dataclass(frozen=True)
class Edge:
    source: NodeId
    target: NodeId
    kind: EdgeKind
    annotations: dict[str, str]

@dataclass(frozen=True)
class ConstructGraph:
    nodes: dict[NodeId, GraphNode]
    edges: tuple[Edge, ...]
    topology: Literal["linear", "circular"]
    sequence_record: SequenceRecord       # derived; checksum binds nodes/edges


# domain/types.py

@dataclass(frozen=True)
class Part:
    id: PartId
    name: str
    role: SequenceOntologyTerm
    sequence: Sequence                    # generic; can be DNA, RNA, protein, oligo
    annotations: tuple[Feature, ...]
    parent: PartId | None
    licence: Licence
    provenance: Provenance
    checksum: Sha256
    host_compatibility: frozenset[HostClass]

@dataclass(frozen=True)
class HostContext:
    role: HostRole                        # cloning_propagation | assembly | delivery |
                                          # producer | expression | target |
                                          # screening_assay | storage
    host_id: HostId
    constraints: tuple[HostConstraint, ...]
    approval_context: ApprovalContext | None

@dataclass(frozen=True)
class Module:
    id: ModuleId
    layer: Literal[
        "propagation","assembly","expression","cargo","termination","metadata"
    ]
    slot_kind: SlotKind
    parts: tuple[PartOrVariant, ...]

PartOrVariant = Part | OneOf | Variable | Override

@dataclass(frozen=True)
class OneOf:
    candidates: tuple[Part, ...]

@dataclass(frozen=True)
class Variable:
    domain: VariableDomain
    constraints: tuple[VariableConstraint, ...]

@dataclass(frozen=True)
class Override:
    free_text: str
    structured: tuple[StructuredConstraint, ...]
    origin: Literal["user", "llm_translation"]
    confirmed_by: UserId
    confirmed_at: Timestamp

@dataclass(frozen=True)
class Construct:
    id: ConstructId
    version: Semver
    modules: tuple[Module, ...]               # user-facing six-layer view
    graph: ConstructGraph                     # canonical coordinate-and-graph model
    hosts: tuple[HostContext, ...]            # role-keyed host map
    biosafety_tier: BiosafetyTier
    downstream_use: DownstreamUse
    feature_table: tuple[Feature, ...]
    sbol_record: SbolRef | None               # SBOL 3.1.x Component
    checksum: Sha256
    provenance: Provenance

@dataclass(frozen=True)
class Library:
    """Library = a Construct definition with at least one OneOf / Variable.
    Iterators are produced on demand by app.library_realisation.expand()."""
    definition: Construct
    expansion_policy: ExpansionPolicy

@dataclass(frozen=True)
class Host:
    id: HostId
    name: str
    chassis: ChassisClass
    genotype: Genotype
    compatible_origins: frozenset[OriginId]
    compatible_markers: frozenset[MarkerId]
    expression_features: HostFeatureSet
    codon_usage_table: CodonUsageTable
    growth_conditions: GrowthConditions
    biosafety_tier: BiosafetyTier
    references: tuple[GradedCitation, ...]


# Assembly methods (strategy hierarchy)
class AssemblyMethod(ABC):
    id: AssemblyMethodId
    name: str
    scarless: bool
    typical_max_fragments: int
    capabilities: frozenset[Capability]
    references: tuple[GradedCitation, ...]

class RestrictionLigation(AssemblyMethod): ...
class GibsonLike(AssemblyMethod): ...
class TypeIISGoldenGate(AssemblyMethod): ...
class GatewayMethod(AssemblyMethod): ...
class LICMethod(AssemblyMethod): ...
class USERMethod(AssemblyMethod): ...
class IVAMethod(AssemblyMethod): ...
class YeastTAR(AssemblyMethod): ...


# Typed assembly plans (one per chemistry)
@dataclass(frozen=True)
class AssemblyPlanSummary:
    method: AssemblyMethodId
    fragments: tuple[FragmentSpec, ...]
    expected_product: SequenceRecord
    expected_byproducts: tuple[SequenceRecord, ...]
    verification_checkpoints: tuple[Checkpoint, ...]
    expected_failure_modes: tuple[FailureMode, ...]

class RestrictionLigationPlan(AssemblyPlanSummary):
    enzymes: frozenset[Enzyme]
    dephosphorylation: bool
    ligation_conditions: LigationConditions

class OverlapAssemblyPlan(AssemblyPlanSummary):
    overlap_lengths: tuple[int, ...]
    polymerase: Polymerase
    molar_ratio_table: tuple[FragmentRatio, ...]

class TypeIISAssemblyPlan(AssemblyPlanSummary):
    enzyme: TypeIISEnzyme
    overhang_set: OverhangSet
    cycling_profile: ThermocyclingProfile
    overhang_fidelity_score: float                  # Pryor 2020 / Potapov 2018

class GatewayPlan(AssemblyPlanSummary):
    reaction: Literal["BP", "LR"]
    attB_scars: tuple[AttScar, ...]
    enzyme_kit: GatewayKitId

class LICPlan(AssemblyPlanSummary):
    tail_design: tuple[LicTail, ...]
    t4_pol_conditions: T4PolConditions

class USERPlan(AssemblyPlanSummary):
    dU_positions: tuple[Position, ...]
    primer_extensions: tuple[PrimerExtension, ...]

class InVivoAssemblyPlan(AssemblyPlanSummary):
    host_strain: HostId
    recombination_arms: tuple[HomologyArm, ...]

class YeastTARPlan(AssemblyPlanSummary):
    yeast_host: HostId
    selection_marker: MarkerId
    tar_fragment_design: tuple[TarFragment, ...]


# Coding-sequence design (codon optimiser input)
@dataclass(frozen=True)
class CodingSequenceDesign:
    native_dna: DnaSequence | None
    target_protein: ProteinSequence
    codon_table: CodonTableId
    target_host_context: HostContext
    protected_intervals: tuple[Location, ...]
    forbidden_motifs: tuple[Motif, ...]
    functional_rna_features: tuple[Feature, ...]
    splice_constraints: SpliceConstraints
    rna_structure_constraints: RnaStructureConstraints
    cai_target_window: tuple[float, float]
    minmax_target_distance: float
    mode: Literal["CAI", "MinMax", "CHARMING", "avoid_only"]


# Validation rule (expanded manifest, v1.1)
class Severity(Enum):
    HARD = "HARD"; SOFT = "SOFT"; INFO = "INFO"

class SafetyGate(Enum):
    COMPILE = "BlockCompile"
    EXPORT = "BlockExport"
    VENDOR_SUBMISSION = "BlockVendorSubmission"
    OPERATIONAL_PROTOCOL = "BlockOperationalProtocol"


# Roles, principals, and authorisation (v1.2, hierarchy clarified v1.3)
class Role(Enum):
    DEVELOPER = "developer"               # system implementer
    ADMINISTRATOR = "administrator"        # institutional admin
    REVIEWER = "reviewer"                  # IBC / biosafety officer
    USER = "user"                          # designer

# Role-capability inheritance map (v1.3). One-directional by design.
# Administrator inherits Reviewer; nothing else inherits anything else.
ROLE_INHERITS: Mapping[Role, frozenset[Role]] = {
    Role.DEVELOPER:     frozenset(),
    Role.ADMINISTRATOR: frozenset({Role.REVIEWER}),
    Role.REVIEWER:      frozenset(),
    Role.USER:          frozenset(),
}

@dataclass(frozen=True)
class Principal:
    """Abstract principal. Engine code typed against this base accepts
    any role except where AdminPrincipal / DeveloperBootstrapPrincipal is required.

    `can_act_as` exposes the v1.3 inheritance semantics: an
    AdminPrincipal returns True for can_act_as(Role.REVIEWER).
    A ReviewerPrincipal does NOT return True for can_act_as(Role.ADMINISTRATOR).
    """
    id: PrincipalId
    role: Role
    institution: InstitutionId
    credentials_verified_at: Timestamp

    def can_act_as(self, required_role: Role) -> bool:
        return (
            self.role == required_role
            or required_role in ROLE_INHERITS[self.role]
        )

@dataclass(frozen=True)
class UserPrincipal(Principal): ...
@dataclass(frozen=True)
class ReviewerPrincipal(Principal): ...
@dataclass(frozen=True)
class AdminPrincipal(Principal): ...
@dataclass(frozen=True)
class DeveloperPrincipal(Principal): ...
@dataclass(frozen=True)
class DeveloperBootstrapPrincipal(DeveloperPrincipal):
    is_bootstrap: bool


@dataclass(frozen=True)
class AuthorisationProfile:
    """Admin-controlled. Mutations are recorded as AdminAction events.

    The User role has read-only access to its own profile via
    AuthorisationStore.read_own_profile() and cannot mutate it.
    """
    profile_id: AuthProfileId
    user_id: UserId
    granted_by_admin_id: AdminId
    granted_at: Timestamp
    profile_valid_from: Timestamp
    profile_valid_until: Timestamp
    revoked_at: Timestamp | None
    revocation_reason: str | None

    covered_biosafety_tiers: frozenset[BiosafetyTier]      # e.g., {BSL-1, BSL-2}
    covered_host_classes: frozenset[ChassisClass]          # e.g., {E. coli, S. cerevisiae}
    covered_assembly_chemistries: frozenset[AssemblyMethodId]
    covered_downstream_uses: frozenset[DownstreamUse]
    covered_sop_libraries: frozenset[SopLibraryId]
    covered_vendor_submission: bool                        # may the user trigger orders?
    covered_export_classes: frozenset[ExportClass]
    role_of_operation_allowed: frozenset[Role]             # roles the user may declare-of-operation

    additional_constraints: tuple[AuthorisationConstraint, ...]
    signature: ProfileSignature                            # institutional signature (multi-user mode)

@dataclass(frozen=True)
class AuthorisationDecision:
    """Output of the BlockOperationalProtocol gate check."""
    allowed: bool
    blocked_by: tuple[BlockReason, ...]                    # empty when allowed
    profile_id: AuthProfileId
    decision_at: Timestamp

@dataclass(frozen=True)
class UserDeclaration:
    """User-declared intent. Validated against the granted profile."""
    declared_at: Timestamp
    declared_by: UserId
    sop_library_id: SopLibraryId | None
    biosafety_approval_id: BiosafetyApprovalId | None
    role_of_operation: Role
    intended_export_class: ExportClass
    intended_vendor_submission: bool

# Admin actions are typed DomainEvent subclasses (cf. §4.7)
class AdminActionMinted(DomainEvent):
    target_user: UserId
    profile: AuthorisationProfile
    justification: str
class AdminActionModified(DomainEvent):
    target_user: UserId
    diff: AuthorisationProfileDiff
    justification: str
class AdminActionRevoked(DomainEvent):
    target_user: UserId
    reason: RevocationReason

@dataclass(frozen=True)
class GradedCitation:
    text: str
    pmid: str | None
    doi: str | None
    pmc: str | None
    url: str | None
    grade: Literal["A1", "A2", "A3", "B1", "B2", "C"]   # per v2.0 KB §2.1
    accessed: Date

@dataclass(frozen=True)
class ValidationRule:
    rule_id: RuleId
    predicate_name: str
    severity: Severity
    severity_policy: SeverityPolicy
    blocks: frozenset[SafetyGate]
    reads: frozenset[FieldPath]
    depends_on_metrics: frozenset[MetricId]
    produces_metrics: frozenset[MetricId]
    invalidates: frozenset[MetricId | RuleId]
    preconditions: tuple[Precondition, ...]
    target_context: ContextScope
    external_adapters: tuple[AdapterRef, ...]
    threshold_profile: ThresholdProfileRef
    citation: GradedCitation
    last_reviewed: Date
    reviewed_by: ReviewerId
    test_fixtures: tuple[FixtureRef, ...]
    suggested_remediation: str


# Validation context (passed to pure validator, v1.1)
@dataclass(frozen=True)
class ValidationContext:
    construct: Construct
    derived_metrics: dict[MetricId, MetricValue]
    threshold_profile: ThresholdProfile
    derivation_environment: DerivationEnvironment


# Protocol primitives (expanded for SOP gating, v1.1)
class HazardClass(Enum):
    BSL1 = "BSL-1"; BSL2 = "BSL-2"; BSL2_PLUS = "BSL-2+"; BSL3 = "BSL-3"
    CHEMICAL_LOW = "chem-low"; CHEMICAL_HIGH = "chem-high"

@dataclass(frozen=True)
class ProtocolStep:
    step_id: StepId
    action: ActionKind
    reagents: tuple[ReagentRef, ...]
    quantities: tuple[Quantity, ...]
    temperature_C: float | None
    duration: Duration | None
    rationale: str
    safety_note: str | None
    successors: tuple[ProtocolEdge, ...]            # THEN / BRANCH / CHECKPOINT / PARALLEL
    sop_ref: SopRef | None
    approval_gate: ApprovalGate | None
    hazard_class: HazardClass
    allowed_roles: frozenset[Role]
    checkpoint_criteria: tuple[Predicate, ...]
    measured_outputs: tuple[MeasurementSchema, ...]
    deviation_policy: DeviationPolicy
    decision_rule: DecisionRule | None

@dataclass(frozen=True)
class ProtocolDAG:
    root: StepId
    steps: dict[StepId, ProtocolStep]                # canonically key-sorted on serialise

@dataclass(frozen=True)
class DesignRealisationPlan:
    """Non-operational. Always renderable."""
    construct_id: ConstructId
    assembly_plan: AssemblyPlanSummary
    primer_set: PrimerSet
    qc_checkpoints: tuple[Checkpoint, ...]
    expected_verification_artefacts: tuple[VerificationArtefact, ...]
    institutional_approvals_required: tuple[ApprovalRequirement, ...]
    biosafety_classification: BiosafetyTier
    reviewer_packet_summary: str

@dataclass(frozen=True)
class SopLinkedProtocol:
    """Operational. Renders only when all four authorisation gates pass."""
    construct_id: ConstructId
    sop_library_id: SopLibraryId
    biosafety_approval_id: BiosafetyApprovalId
    user_role: Role
    protocol_dag: ProtocolDAG
    deviation_policy: DeviationPolicy

@dataclass(frozen=True)
class ControlSet:
    positive: tuple[ControlDesign, ...]
    negative: tuple[ControlDesign, ...]
    process: tuple[ControlDesign, ...]
    library_specific: tuple[ControlDesign, ...]


# Screening verdict (expanded, v1.1)
class ScreeningVerdict(Enum):
    CLEAR = "clear"
    WATCHLIST = "watchlist"
    HIT = "hit"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"

@dataclass(frozen=True)
class ScreeningResult:
    verdict: ScreeningVerdict
    adapter_name: str
    adapter_version: str
    adapter_canonical: bool
    evidence: tuple[ScreeningEvidence, ...]
    timestamp: Timestamp


# Typed domain events (v1.1: discriminated subclasses)
@dataclass(frozen=True)
class DomainEvent:
    event_id: EventId
    session_id: SessionId
    timestamp: Timestamp
    actor: UserId

class SessionStarted(DomainEvent): ...
class PartAdded(DomainEvent):
    part: Part
class HostSelected(DomainEvent):
    host_context: HostContext
class FreeTextEntered(DomainEvent):
    text: str
class LLMTranslationProposed(DomainEvent):
    structured: tuple[StructuredConstraint, ...]
class LLMTranslationConfirmed(DomainEvent):
    structured: tuple[StructuredConstraint, ...]
class RuleAcknowledged(DomainEvent):
    rule_id: RuleId
    justification: str
class OverrideJustified(DomainEvent):
    override: Override
class Compiled(DomainEvent):
    plan: AssemblyPlanSummary
    primers: PrimerSet
    design_plan: DesignRealisationPlan
    derivation_environment: DerivationEnvironment
class Screened(DomainEvent):
    result: ScreeningResult
class Exported(DomainEvent):
    bundle_path: Path
    bundle_hash: Sha256
class ReviewerSignedOff(DomainEvent):
    signer_id: PrincipalId             # was: reviewer; renamed v1.3
    signer_role: Role                  # v1.3 — discriminator: Role.REVIEWER or Role.ADMINISTRATOR
    decision: ReviewerDecision
    # Invariant (enforced at construction): signer_role ∈ {Role.REVIEWER, Role.ADMINISTRATOR}.
    # The audit log records *who actually signed*, so an Administrator signing in
    # reviewer capacity is distinguishable from a dedicated Reviewer signing.
class SessionForked(DomainEvent):
    new_session_id: SessionId
    lineage: tuple[SessionId, ...]


# Derivation environment (v1.1)
@dataclass(frozen=True)
class DerivationEnvironment:
    rule_registry_version: Semver
    rule_manifest_hashes: dict[str, Sha256]            # MR / WR / SR / BR / MS
    catalogue_versions: dict[CatalogueId, Semver]
    catalogue_content_hashes: dict[CatalogueId, Sha256]
    plugin_versions: dict[PluginId, Semver]
    plugin_configurations: dict[PluginId, Sha256]
    external_database_versions: dict[DatabaseId, str]   # REBASE, codon tables, SpliceAI weights ...
    sop_template_versions: dict[SopTemplateId, Semver]
    container_image_digest: ContainerDigest
    cpu_arch: str
    locale: str
    units_profile: UnitsProfile
    rounding_policy: RoundingPolicy
    random_seeds: dict[RandomSeedId, int]
    optimisation_settings: OptimisationSettings
    user_overrides: tuple[UserOverride, ...]
    reviewer_decisions: tuple[ReviewerDecision, ...]
    construct_checksum: Sha256

    def canonical_json(self) -> bytes:
        """Deterministic key order: every nested dict is sorted by key bytes."""
        ...

    def hash(self) -> Sha256:
        return sha256(self.canonical_json())


@dataclass(frozen=True)
class DesignSession:
    id: SessionId
    construct: Construct
    library: Library | None
    validation_context: ValidationContext | None
    validation_report: ValidationReport | None
    compatibility_report: CompatibilityReport | None
    assembly_plan: AssemblyPlanSummary | None
    primer_set: PrimerSet | None
    controls: ControlSet | None
    design_plan: DesignRealisationPlan | None
    sop_protocol: SopLinkedProtocol | None
    screening_results: tuple[ScreeningResult, ...]
    derivation_environment: DerivationEnvironment | None
    event_log_ref: EventLogRef
    history: ProvenanceGraph
```

---

#### 4.6.v1.4 — Supplement integrating the second Codex audit (binding)

The following types **supersede** the equivalent v1.0–v1.3 forms above. Where a v1.4 type has the same name as a v1.0–v1.3 type, the v1.4 form is binding.

```python
# domain/security_roles.py — SecurityRole and OperationalRole split (v1.4 M6)
class SecurityRole(Enum):
    """Security identity, bound at authentication, cannot be widened in-session."""
    DEVELOPER = "developer"
    ADMINISTRATOR = "administrator"
    REVIEWER = "reviewer"
    USER = "user"

class OperationalRole(Enum):
    """How a User intends to use a construct biologically. Disjoint from SecurityRole."""
    CLONING_PROPAGATION = "cloning_propagation"
    ASSEMBLY = "assembly"
    DELIVERY = "delivery"
    PRODUCER = "producer"
    EXPRESSION = "expression"
    TARGET = "target"
    SCREENING_ASSAY = "screening_assay"
    STORAGE = "storage"

# (v1.3's Role alias is retained as a deprecated synonym for SecurityRole;
#  new code should use SecurityRole. Mypy stub Role = SecurityRole.)


# domain/sequence_v1_4.py — formal location algebra (v1.4 M3)
class LocationFuzziness(Enum):
    EXACT = "exact"
    BEFORE = "before"          # before the indicated base, e.g., <42
    AFTER = "after"            # after the indicated base, e.g., >42
    BETWEEN = "between"        # between two bases, e.g., 42^43
    UNKNOWN = "unknown"

class CompoundLocationKind(Enum):
    JOIN = "join"              # parts that are biologically joined (CDS with introns)
    ORDER = "order"            # ordered list, no biological join asserted
    BOND = "bond"              # non-contiguous bond
    GAP = "gap"

@dataclass(frozen=True)
class LocationV14:
    start: int
    end: int
    strand: Literal["+", "-", "."]
    phase: Literal[0, 1, 2, "."]
    start_fuzziness: LocationFuzziness = LocationFuzziness.EXACT
    end_fuzziness: LocationFuzziness = LocationFuzziness.EXACT
    circular_wrap: bool = False
    between_base: bool = False
    sub_locations: tuple["LocationV14", ...] = ()
    sub_kind: CompoundLocationKind | None = None
    complement_compound: bool = False        # complement of join/order vs join of complements
    remote_accession: str | None = None      # for cross-record references
    partial_at_5p: bool = False
    partial_at_3p: bool = False

    def sequence_length_invariant_satisfied(self, parent_length: int) -> bool: ...


# domain/types_v1_4.py — structured Qualifier (v1.4 B6)
@dataclass(frozen=True)
class Qualifier:
    namespace: str                            # "GenBank" | "SBOL" | "SnapGene" | ...
    key: str
    value: str | StructuredValue
    value_type: Literal["string","boolean","integer","float","url","ontology_term","structured"]
    order: int                                # preserves original ordering
    provenance: Provenance | None = None

@dataclass(frozen=True)
class FeatureV14:
    role: SequenceOntologyTerm                # SBOL 3.1.x role
    qualifiers: tuple[Qualifier, ...]         # was dict[str, str]
    locations: tuple[LocationV14, ...]
    parent_sequence_id: SequenceRecordId
    evidence: tuple[GradedCitation, ...]
    sub_features: tuple["FeatureV14", ...] = ()


# Multi-hash model (v1.4 M2)
@dataclass(frozen=True)
class ConstructHashes:
    sequence_hash: Sha256              # canonical-orientation sequence only
    topology_hash: Sha256              # sequence + topology (linear/circular)
    annotation_hash: Sha256            # features + qualifiers + locations
    construct_graph_hash: Sha256       # nodes + edges + topology
    export_bundle_hash: Sha256         # full project bundle ZIP hash

class ReverseComplementEquivalence(Enum):
    EQUIVALENT = "equivalent"          # e.g., sequence_hash for symmetric assays
    DISTINCT = "distinct"              # e.g., annotation_hash, where strand matters


# Annotated I/O contracts (v1.4 B5)
@dataclass(frozen=True)
class ImportedConstruct:
    sequence_record: SequenceRecord
    feature_table: tuple[FeatureV14, ...]
    structured_qualifiers: tuple[Qualifier, ...]
    construct_graph: ConstructGraph
    sbol_mapping: SbolMapping | None
    snapgene_visual_metadata: SnapGeneVisualMetadata | None
    source_format_metadata: SourceFormatMetadata
    primer_annotations: tuple[PrimerAnnotation, ...]
    lossy_conversion_warnings: tuple[LossWarning, ...]
    hashes: ConstructHashes

@dataclass(frozen=True)
class AnnotatedConstruct(ImportedConstruct):
    """Ready-to-write artefact."""

@dataclass(frozen=True)
class WriteResult:
    bytes_emitted: bytes
    lossy_warnings: tuple[LossWarning, ...]
    canonical_hash: Sha256


# Vendor feasibility request (v1.4 M1)
@dataclass(frozen=True)
class VendorFeasibilityRequest:
    sequence: SequenceRecord
    product_type: ProductType                 # gene-fragment | clonal-gene | plasmid-prep | oligo-pool
    workflow: Literal["synthesis_only","cloning","plasmid_prep","oligo_pool"]
    scale: SynthesisScale
    vector_backbone_id: PartId | None
    delivery_format: DeliveryFormat            # linear | pre-cloned | aliquot
    target_host_strain_id: HostId | None
    hazardous_screening_required: bool
    ip_constraints: tuple[IPConstraint, ...]
    turnaround_target_days: int | None
    regional_rules: tuple[RegionalRule, ...]
    customer_account_id: CustomerAccountId


# Screening trust + structured error (v1.4 B10, N5)
@dataclass(frozen=True)
class ScreeningProviderTrustPolicy:
    provider_id: ScreeningProviderId
    provider_type: Literal[
        "igsc_canonical","ibbis_common_mechanism","secureDNA",
        "internal_blacklist","vendor_screening","advisory_only",
    ]
    approved_use: frozenset[ScreeningUseClass]
    canonical_for: frozenset[ScreeningScope]
    policy_version: Semver
    approved_by_admin: AdminId
    approved_at: Timestamp
    valid_until: Timestamp

class ScreeningErrorCategory(Enum):
    TRANSIENT_PROVIDER_FAILURE = "transient_provider_failure"
    INVALID_QUERY = "invalid_query"
    UNSUPPORTED_SEQUENCE = "unsupported_sequence"
    AMBIGUOUS_RESULT = "ambiguous_result"
    POLICY_FAILURE = "policy_failure"
    PROVIDER_UNAVAILABLE = "provider_unavailable"

@dataclass(frozen=True)
class ScreeningError:
    category: ScreeningErrorCategory
    provider_id: ScreeningProviderId
    detail: str
    retry_policy: RetryPolicy
    audit_event_mapping: AuditEventKind
    timestamp: Timestamp

class NotApplicableReason(Enum):
    BELOW_THRESHOLD_PER_POLICY = "below_threshold_per_policy"
    NON_PATHOGEN_ORIGIN_PER_POLICY = "non_pathogen_origin_per_policy"
    TOOLS_WORKFLOW_PER_POLICY = "tools_workflow_per_policy"

# v1.4 ScreeningResult — adapter.canonical removed; trust comes from policy
@dataclass(frozen=True)
class ScreeningResultV14:
    verdict: ScreeningVerdict
    provider_id: ScreeningProviderId
    provider_trust_policy_version: Semver
    canonical_at_this_scope: bool                # derived from ScreeningProviderTrustPolicy
    scope: ScreeningScope
    submitted_sequence_hash: Sha256              # exact assembled sequence
    not_applicable_reason: NotApplicableReason | None
    evidence: tuple[ScreeningEvidence, ...]
    timestamp: Timestamp


# Signed decision record + role snapshot (v1.4 B9)
@dataclass(frozen=True)
class DecisionRecord:
    decision_id: DecisionId
    principal_id: PrincipalId
    role_asserted: SecurityRole
    role_held_at_decision: bool                  # verified at signing
    authorisation_profile_id: AuthProfileId | None
    profile_content_hash: Sha256 | None
    policy_version: Semver
    institutional_approval_id: InstitutionalApprovalId | None
    decision_scope_hash: Sha256
    decision_kind: Literal[
        "reviewer_signoff","watchlist_override","manual_review_signoff",
        "authorisation_mint","authorisation_modify","authorisation_revoke",
        "screening_exception","advisory_acknowledgement","bootstrap_admin",
    ]
    decision_payload: dict
    signature: CryptographicSignature
    key_id: KeyId
    timestamp: Timestamp

@dataclass(frozen=True)
class RoleSnapshot:
    principal_id: PrincipalId
    role_held: SecurityRole
    snapshot_at: Timestamp
    snapshot_signature: CryptographicSignature


# Risk advisory layer — B3 mitigation (v1.4)
class AdvisoryCategory(Enum):
    HIGH_RISK_ELEMENT = "high_risk_element"
    ELEVATED_BSL = "elevated_bsl"
    REQUIRES_APPROVAL = "requires_approval"

@dataclass(frozen=True)
class RiskAdvisory:
    advisory_id: AdvisoryId                       # v1.5 — stable ID for acknowledgement-trail addressing
    category: AdvisoryCategory
    matched_feature: FeatureRef
    severity: Literal["info","caution","strong_caution"]
    description: str                              # plain-English for the administrator
    citation: GradedCitation
    suggested_action: str

# Acknowledgement requirements per severity (v1.5 strengthening):
#   info             → no acknowledgement required (informational only)
#   caution          → explicit acknowledgement with justification REQUIRED
#                       before OperationalProtocolAuthorised may fire
#   strong_caution   → as above, AND the advisory's overall_recommendation
#                       being "strongly_recommend_institutional_approval"
#                       requires either an institutional_approval_id or
#                       a documented decline / escalation

@dataclass(frozen=True)
class RiskAdvisoryReport:
    # v1.4 fields:
    construct_id: ConstructId
    construct_checksum: Sha256
    advisories: tuple[RiskAdvisory, ...]
    overall_recommendation: Literal[
        "no_concerns","informational",
        "consider_institutional_approval","strongly_recommend_institutional_approval",
    ]
    generated_at: Timestamp
    catalogue_version: Semver
    catalogue_content_hash: Sha256
    # v1.5 additions — bind report to design record + audit replay:
    design_session_id: SessionId
    report_content_hash: Sha256                   # canonical-JSON hash of the report itself
    construct_version: Semver                     # which Construct version produced this report

    def required_acknowledgements(self) -> frozenset[AdvisoryId]:
        """The set of advisory_id values whose explicit acknowledgement is
        REQUIRED before OperationalProtocolAuthorised may fire. Severity
        'caution' and 'strong_caution' advisories are mandatory."""
        return frozenset(
            a.advisory_id for a in self.advisories
            if a.severity in ("caution", "strong_caution")
        )


# Active acknowledgement workflow (v1.5 sponsor strengthening of B3)
# ----------------------------------------------------------------------
# Warnings must be ACTIVE, AUDITABLE, and TIED TO THE DESIGN RECORD.
# The Administrator must receive an EXPLICIT warning, and the FULL
# APPROVAL TRACE must be logged. Passive UI banners are insufficient.
# Every step in the acknowledgement chain is a typed governance event.

class AdvisoryAcknowledgementDecision(Enum):
    ACKNOWLEDGED = "acknowledged"      # Administrator accepts the advisory and proceeds
    DECLINED = "declined"              # Administrator refuses; routes to alternative reviewer
                                       # or dual-control flow per InstitutionalPolicy
    ESCALATED = "escalated"            # Requires institutional sign-off (PI / IBC / equivalent)

@dataclass(frozen=True)
class RiskAdvisoryAcknowledgement:
    """A typed, signed acknowledgement record. Binds an Administrator's
    decision to the exact advisory, the exact construct version, and the
    exact RiskAdvisoryReport that surfaced it. Stored as the payload of
    a RiskAdvisoryAcknowledged governance event."""
    acknowledgement_id: AcknowledgementId
    design_session_id: SessionId
    construct_id: ConstructId
    construct_checksum: Sha256
    report_content_hash: Sha256                   # ties to the exact report
    advisory_id: AdvisoryId                       # the specific advisory acknowledged
    decision: AdvisoryAcknowledgementDecision
    justification: str                            # minimum 20 characters; required
    institutional_approval_id: InstitutionalApprovalId | None  # required if escalated
    decision_record: DecisionRecord               # signed; B9
    timestamp: Timestamp

    def is_blocking(self) -> bool:
        """An acknowledgement counts toward unblocking authorisation only
        when decision == ACKNOWLEDGED. DECLINED routes to alternative flow;
        ESCALATED requires institutional_approval_id."""
        return self.decision != AdvisoryAcknowledgementDecision.ACKNOWLEDGED


# Governance events for the advisory acknowledgement chain (v1.5)
class AdvisoryWarningPresented(GovernanceEvent):
    """Emitted when the system presents an advisory to an Administrator.
    Logged regardless of whether the Administrator subsequently acts on it.
    A passive UI render is NOT sufficient — every presentation is logged."""
    design_session_id: SessionId
    construct_id: ConstructId
    construct_checksum: Sha256
    report_content_hash: Sha256
    advisory_ids_presented: tuple[AdvisoryId, ...]
    presented_to: AdminPrincipal | ReviewerPrincipal
    presentation_surface: Literal["cli","api","ui","report_email"]

class RiskAdvisoryAcknowledged(GovernanceEvent):
    """Administrator explicitly acknowledges an advisory with justification
    and signature. Required for any advisory of severity caution/strong_caution
    before OperationalProtocolAuthorised may fire."""
    acknowledgement: RiskAdvisoryAcknowledgement

class RiskAdvisoryDeclined(GovernanceEvent):
    """Administrator declines an advisory; the construct is routed to an
    alternative reviewer or dual-control flow per InstitutionalPolicy.
    The decline does NOT unblock OperationalProtocolAuthorised on its own."""
    acknowledgement: RiskAdvisoryAcknowledgement   # decision = DECLINED

class RiskAdvisoryEscalated(GovernanceEvent):
    """Administrator escalates the advisory for institutional sign-off
    (PI / IBC / equivalent). Requires an institutional_approval_id."""
    acknowledgement: RiskAdvisoryAcknowledgement   # decision = ESCALATED


# Gate predicate for v1.5: the authorisation gate consults this
# before emitting OperationalProtocolAuthorised.
def all_required_advisories_acknowledged(
    report: RiskAdvisoryReport,
    events: tuple[GovernanceEvent, ...],   # the governance event stream for this session
) -> tuple[bool, frozenset[AdvisoryId]]:
    """Returns (all_satisfied, set_of_missing_advisory_ids).
    An advisory is satisfied iff there exists a RiskAdvisoryAcknowledged
    event in the stream whose acknowledgement.advisory_id matches AND
    acknowledgement.decision == ACKNOWLEDGED AND signature verifies."""
    required = report.required_acknowledgements()
    satisfied = frozenset(
        e.acknowledgement.advisory_id
        for e in events
        if isinstance(e, RiskAdvisoryAcknowledged)
        and e.acknowledgement.report_content_hash == report.report_content_hash
        and e.acknowledgement.decision == AdvisoryAcknowledgementDecision.ACKNOWLEDGED
    )
    missing = required - satisfied
    return (len(missing) == 0, missing)


# CoveredBiologicalScope + expanded AuthorisationProfile (v1.4 B4)
class VectorSystemClass(Enum):
    PLASMID = "plasmid"
    INTEGRATING_VIRAL = "integrating_viral"
    NON_INTEGRATING_VIRAL = "non_integrating_viral"
    TRANSPOSON = "transposon"
    PHAGEMID = "phagemid"
    VLP = "vlp"
    MINICIRCLE = "minicircle"
    BAC_YAC = "bac_yac"
    AGROBACTERIUM_BINARY = "agrobacterium_binary"

class CargoClass(Enum):
    TOXIN = "toxin"
    VIRULENCE_FACTOR = "virulence_factor"
    ONCOGENE = "oncogene"
    CYTOKINE = "cytokine"
    IMMUNE_MODULATOR = "immune_modulator"
    ANTIBIOTIC_RESISTANCE = "antibiotic_resistance"
    SELECTABLE_MARKER = "selectable_marker"
    REPORTER = "reporter"
    REGULATORY_ELEMENT = "regulatory_element"
    STRUCTURAL_NATIVE = "structural_native"

class ReplicationCompetenceClass(Enum):
    NONE = "none"
    HELPER_DEPENDENT = "helper_dependent"
    SELF_REPLICATING = "self_replicating"

@dataclass(frozen=True)
class CoveredBiologicalScope:
    covered_biosafety_tiers: frozenset[BiosafetyTier]
    covered_host_classes: frozenset[ChassisClass]
    covered_host_roles: frozenset[OperationalRole]              # NEW
    covered_assembly_chemistries: frozenset[AssemblyMethodId]
    covered_downstream_uses: frozenset[DownstreamUse]
    covered_sop_libraries: frozenset[SopLibraryId]
    covered_vector_classes: frozenset[VectorSystemClass]        # NEW
    covered_cargo_classes: frozenset[CargoClass]                # NEW
    covered_replication_competence: frozenset[ReplicationCompetenceClass]  # NEW
    max_insert_size_bp: int | None                              # NEW
    max_copy_number: int | None                                 # NEW
    covered_target_organisms: frozenset[TargetOrganism] | None  # NEW
    covered_screening_exception_classes: frozenset[ScreeningExceptionClass]  # NEW
    institutional_protocol_ids: tuple[InstitutionalProtocolId, ...]
    institutional_approval_scope: ApprovalScope
    jurisdictional_constraints: tuple[JurisdictionConstraint, ...]
    component_lineage_trust: ComponentLineageTrustLevel

@dataclass(frozen=True)
class DualControlFlags:
    """Data-only hooks; runtime enforcement opt-in per InstitutionalPolicy.
    The B3 defense rests on these being optional for institutions whose
    workflow does not require dual sign-off; institutions that do require
    dual sign-off enable enforcement via InstitutionalPolicy."""
    requires_independent_reviewer: bool = False
    requires_biosafety_officer: bool = False
    requires_second_admin: bool = False
    requires_signed_institutional_approval: bool = False

@dataclass(frozen=True)
class AuthorisationProfileV14:
    profile_id: AuthProfileId
    profile_content_hash: Sha256                       # NEW for B9 decision binding
    user_id: UserId
    granted_by_admin_id: AdminId
    granted_at: Timestamp
    profile_valid_from: Timestamp
    profile_valid_until: Timestamp
    revoked_at: Timestamp | None
    revocation_reason: str | None
    scope: CoveredBiologicalScope
    role_of_operation_allowed: frozenset[OperationalRole]
    covered_export_classes: frozenset[ExportClass]
    covered_vendor_submission: bool
    dual_control_flags: DualControlFlags
    additional_constraints: tuple[AuthorisationConstraint, ...]
    signature: ProfileSignature


# HostCompatibilityConstraints (v1.4 M5)
@dataclass(frozen=True)
class HostCompatibilityConstraints:
    propagation: HostContextConstraint | None
    expression: HostContextConstraint | None
    screening: HostContextConstraint | None
    delivery: HostContextConstraint | None
    producer: HostContextConstraint | None
    target: HostContextConstraint | None

@dataclass(frozen=True)
class HostContextConstraint:
    promoter_recognition_required: frozenset[PromoterRecognitionClass] | None
    codon_usage_table: CodonTableId | None
    compatible_origins: frozenset[OriginId]
    compatible_markers: frozenset[MarkerId]
    toxicity_flag: bool
    secretion_required: bool
    intron_splicing_supported: bool
    methylation_sensitivity: MethylationSensitivity
    copy_number_constraint: tuple[int, int] | None
    transformation_modality: frozenset[TransformationModality]


# Export redaction profile (v1.4 N6)
class ExportProfile(Enum):
    INTERNAL_AUDIT = "internal_audit"             # full bundle including PII
    COLLABORATOR = "collaborator"                  # full bundle minus PII
    VENDOR = "vendor"                              # sequence + minimal metadata only
    PUBLICATION_SUPPLEMENT = "publication_supplement"   # sequence + design plan + non-confidential metadata

@dataclass(frozen=True)
class RedactionPolicy:
    profile: ExportProfile
    redact_user_overrides: bool
    redact_reviewer_notes: bool
    redact_institutional_approval_ids: bool
    redact_principal_ids: bool
    redact_authorisation_profile_details: bool
    redact_screening_evidence_detail: bool
    redact_llm_advisory_text: bool
    policy_version: Semver


# Operational-types-only namespace (v1.4 M11)
# domain/types/sop_protected.py — only imported from engine.sop_protocol,
# never from engine.design_plan or any User-facing layer.
__sop_protected__ = True   # marker; an import-linter contract enforces:
#   - engine.design_plan MUST NOT import domain.types.sop_protected.*
#   - DesignRealisationPlan dataclass MUST NOT contain a ProtocolStep field
#   - mypy --strict + a runtime guard enforce both invariants.


# Expanded DerivationEnvironment (v1.4 B11)
@dataclass(frozen=True)
class DerivationEnvironmentV14:
    # v1.2/v1.3 fields retained
    rule_registry_version: Semver
    rule_manifest_hashes: dict[str, Sha256]
    catalogue_versions: dict[CatalogueId, Semver]
    catalogue_content_hashes: dict[CatalogueId, Sha256]
    plugin_versions: dict[PluginId, Semver]
    plugin_configurations: dict[PluginId, Sha256]
    external_database_versions: dict[DatabaseId, str]
    sop_template_versions: dict[SopTemplateId, Semver]
    container_image_digest: ContainerDigest
    cpu_arch: str
    locale: str
    units_profile: UnitsProfile
    rounding_policy: RoundingPolicy
    random_seeds: dict[RandomSeedId, int]
    optimisation_settings: OptimisationSettings
    user_overrides: tuple[UserOverride, ...]
    reviewer_decisions: tuple[ReviewerDecision, ...]
    construct_checksum: Sha256

    # v1.4 additions (B11)
    authorisation_profile_id: AuthProfileId | None
    authorisation_profile_content_hash: Sha256 | None
    sop_template_content_hashes: dict[SopTemplateId, Sha256]
    screening_provider_trust_policy_version: Semver
    screening_query_scope: ScreeningScope
    screening_threshold_policy_version: Semver
    screening_submitted_sequence_hash: Sha256
    plugin_package_hashes: dict[PluginId, Sha256]
    llm_prompt_template_versions: dict[PromptTemplateId, Semver]
    llm_model_identifiers: dict[LLMUseSite, LLMModelIdentifier]
    institutional_policy_version: Semver
    user_declaration_hash: Sha256
    export_profile: ExportProfile
    redaction_policy_version: Semver
    risk_advisory_catalogue_version: Semver
    risk_advisory_catalogue_content_hash: Sha256
    privacy_classification: PrivacyClassification

    def canonical_json(self) -> bytes: ...
    def hash(self) -> Sha256: ...
```

**Canonical-vs-derived (v1.4 M4).** `ConstructGraph` is the single source of truth for features and locations. `Construct.feature_table` is a *derived view*; the invariant `feature_table == derive_feature_table(graph)` is enforced on every state transition. The graph is what is serialised to SBOL 3.1.x and round-tripped through GenBank.

**Reviewer / Admin sign-off (v1.4 B9).** Every `ReviewerSignedOff` event now carries a `DecisionRecord` instead of bare `signer_id` / `signer_role` fields. The decision record proves: the signer's role was held at decision time (verified at signing); the authorisation profile content hash; the policy version; the institutional approval ID; the cryptographic signature with key ID. Role snapshots are persisted so historical replay is correct after role revocation.

### 4.7 Event sourcing and audit

The event stream is **append-only**; events are immutable typed subclasses of `DomainEvent`; multi-user mode signs events with the project keypair.

```
   ┌────────────────────────────────────────────────────────────────┐
   │  Append-only typed DomainEvent stream per session             │
   │  ─────────────────────────────────────────                     │
   │  SessionStarted                                                │
   │  PartAdded                                                     │
   │  HostSelected                                                  │
   │  FreeTextEntered                                               │
   │  LLMTranslationProposed                                        │
   │  LLMTranslationConfirmed                                       │
   │  RuleAcknowledged                                              │
   │  OverrideJustified                                             │
   │  Compiled                  (carries DerivationEnvironment)     │
   │  Screened                  (carries ScreeningResult enum)      │
   │  Exported                  (carries bundle hash + path)        │
   │  ReviewerSignedOff                                             │
   │  SessionForked             (new UUID; lineage)                 │
   │  AdminActionMinted         (admin minted an AuthorisationProfile, v1.2)
   │  AdminActionModified       (admin modified a profile, v1.2)    │
   │  AdminActionRevoked        (admin revoked a profile, v1.2)     │
   └────────────────────────────────────────────────────────────────┘
```

**v1.4 — three separated append-only streams (B8, M12).** Governance, design, and export concerns are split into three distinct streams written by three distinct application services. Cross-stream correlation is via immutable `DecisionRecord` IDs and content hashes.

```
   events/design/<session_id>.jsonl        — DesignEvent subclasses:
        SessionStarted, PartAdded, HostSelected, FreeTextEntered,
        LLMTranslationProposed, LLMTranslationConfirmed,
        RuleAcknowledged, OverrideJustified,
        DesignCompiled (v1.4 B2 — replaces Compiled; carries
                         ConstructGraph + DesignRealisationPlan +
                         ControlSet + RiskAdvisoryReport +
                         ScreeningRequestPackage),
        ScreeningCompleted (v1.4),
        OperationalProtocolAuthorised (v1.4 B2),
        SopRendered (v1.4 B2),
        SessionForked

   events/governance/<institution_id>.jsonl — GovernanceEvent subclasses:
        AdminBootstrapped, AdminActionMinted, AdminActionModified,
        AdminActionRevoked, InstitutionalPolicyUpdated,
        ReviewerSignedOff (carries signed DecisionRecord, v1.4 B9),
        AuthorisationAttemptDenied, PluginManifestApproved,
        AdvisoryWarningPresented   (v1.5 — every presentation logged),
        RiskAdvisoryAcknowledged   (v1.4 B3 / v1.5 sharpened),
        RiskAdvisoryDeclined       (v1.5 — Admin declines; routes to
                                          alternative reviewer / dual-control),
        RiskAdvisoryEscalated      (v1.5 — Admin escalates to institutional
                                          sign-off; institutional_approval_id
                                          required),
        UnsupportedBiosafetyTierAttempted (v1.4 M7)

   events/export/<institution_id>.jsonl    — ExportEvent subclasses:
        BundleEmitted, VendorSubmissionPrepared,
        ExportProfileRedactionApplied (v1.4 N6)
```

The legacy `DomainEvent` becomes the abstract base; `DesignEvent`, `GovernanceEvent`, and `ExportEvent` inherit from it with stream-specific actor types. `AdminAction*` events are no longer mixed into design sessions; they belong to the governance stream and are not bound to a `SessionId`.

The audit log is separate from all three event streams and immutable. It records who confirmed what when — reviewer sign-offs, override justifications, screening verdict acknowledgements, biosafety approval IDs, advisory acknowledgements, **and every `AdminAction*` event affecting any `AuthorisationProfile`**. The audit log is the legal trail for who granted whom what authorisation. It is written via the `AdminActionHandler` application service, which requires Administrator or Developer credentials and rejects writes from any User-role caller.

### 4.8 Persistence and storage

```
   project_directory/
   ├── project.sqlite                        (sessions, constructs, parts library cache)
   ├── events/                                (v1.4 — three separated streams, B8/M12)
   │   ├── design/<session_id>.jsonl          (DesignEvent — session-bound)
   │   ├── governance/<institution_id>.jsonl  (GovernanceEvent — institutional)
   │   └── export/<institution_id>.jsonl      (ExportEvent — artifact release)
   ├── snapshots/
   │   └── <session_id>/<event_seq>.json     (periodic derived snapshots; keyed by DerivationEnvironment hash)
   ├── audit.sqlite                          (immutable sign-offs, overrides, screening verdicts,
   │                                          AdminAction events; written by AdminActionHandler;
   │                                          no User-role write path)
   ├── authorisation.sqlite                   (v1.2 — admin-controlled AuthorisationProfile store;
   │                                          read-only to engine and User code;
   │                                          writes only via AdminActionHandler under
   │                                          Administrator or Developer credentials)
   ├── catalogues/
   │   ├── parts.yaml
   │   ├── hosts.yaml
   │   ├── enzymes.yaml
   │   ├── rules/
   │   │   ├── MR.yaml
   │   │   ├── WR.yaml
   │   │   ├── SR.yaml
   │   │   ├── BR.yaml
   │   │   └── MS.yaml                       (NEW — MS2/VLP-specific rules)
   │   ├── vendor_profiles/
   │   │   ├── twist.yaml
   │   │   ├── idt.yaml
   │   │   └── genscript.yaml
   │   ├── screening_profiles/               (per-adapter configuration)
   │   ├── sop_templates/                    (NEW — institution-owned; empty by default)
   │   ├── risk_advisories.yaml              (v1.4 B3 — high-risk genetic
   │   │                                       elements, elevated-BSL sequences,
   │   │                                       constructs requiring institutional
   │   │                                       approval; advisory only)
   │   ├── screening_trust_policy.yaml       (v1.4 B10 — institution-controlled
   │   │                                       provider trust registry)
   │   ├── institutional_policy.yaml         (v1.4 — opt-in dual-control flags,
   │   │                                       NotApplicableReason policy,
   │   │                                       unsupported-tier list)
   │   ├── export_profiles.yaml              (v1.4 N6 — redaction policies)
   │   └── plugin_manifests/                 (v1.4 N7 — signed plugin manifests,
   │                                          package hashes pinned)
   ├── exports/
   │   └── <bundle_id>.zip
   └── .lockfile                             (pinned dependency manifest)
```

Every YAML manifest carries maintenance metadata:

```yaml
maintenance:
  retrieved_at: 2026-04-12
  valid_until: 2026-10-12
  source_url: https://...
  source_owner: vendor | scientific-advisor | community
  review_required_after: 2026-09-12
  review_frequency: monthly | quarterly | as-needed
```

A CI gate `stale-catalogue-check` fails if any active catalogue's `review_required_after` is in the past.

### 4.9 Concurrency and performance — two-tier budgets

**Tier 1 — Core deterministic** (release-blocker CI gate):

| Operation | Target |
|---|---|
| Validation of a 10 kb construct (core only, deterministic fakes) | < 10 s |
| Codon optimisation of a 1 kb ORF | < 5 s |
| Golden Gate overhang-set optimisation for ≤ 20 fragments | < 60 s |
| Batch validation of 1 000 library realisations (deterministic fakes) | < 30 min |
| Sequence I/O (read GenBank, write SBOL 3 / FASTA) | ≥ 10 MB/s |
| Bundle export of a 10 kb construct | < 5 s |

**Tier 2 — Production adapter** (operational SLA, *not* a release gate):

| Operation | Measured per adapter; reported separately |
|---|---|
| RNA folding on a 1 kb mRNA | typical via ViennaRnaAdapter |
| SpliceAI scan on a 5 kb cDNA | typical via SpliceAiAdapter |
| Screening verdict (single sequence) | typical per adapter, reported in Manifest |
| Batch screening of 100 sequences | typical per adapter, reported in Manifest |
| Vendor `check` on a 5 kb sequence | typical per profile |

Each adapter's `Manifest.measured_typical_latency_ms` / `measured_max_latency_ms` is treated as the SLA target.

### 4.10 Testing and verification strategy

**Three test tiers:**

1. Unit tests with property-based generation (`hypothesis`) on every domain function, every parser, every predicate.
2. Integration tests against deterministic fakes for every adapter. Network mocked; clock mocked; randomness seeded.
3. End-to-end UAT on the three white-paper examples + a 100-realisation Golden Gate library + a multi-host workflow (e.g., bacterial cloning + Agrobacterium delivery + *N. benthamiana* target) + an MS2/VLP design exercising MS-* rules + a gated SOP protocol-rendering exercise.

**Release-blocking CI gates:**

1. All tests pass.
2. ≥ 90 % line coverage on `domain.*` and `engine.*`.
3. 100 % rule-validation coverage: every rule has both triggering and passing fixtures.
4. Determinism check: each white-paper example's output is byte-identical to its golden file inside the pinned containerised environment.
5. **Source-grade citation gate**: every rule manifest entry has a `citation.grade` ∈ {A1, A2, A3, B1, B2}; grade `C` allowed only when a corroborating A/B-graded source is present.
6. SBOL 3.1.x round-trip property test passes.
7. **Stale-catalogue check**: no active catalogue has `review_required_after` in the past.
8. **No-domain-impurity check**: static analysis confirms the domain core does not import any adapter or I/O module.
9. **No-self-authorisation check (v1.2)**: static analysis confirms that no `User`-scope code path imports the `AuthorisationStore.write_mint` / `write_modify` / `write_revoke` methods, and no User-role API endpoint can reach the `AdminActionHandler`. Tested by adversarial reachability analysis (mypy + a curated set of "if a User reaches this, fail the build" assertions) plus runtime integration tests that authenticate as a `UserPrincipal` and confirm 403 / `PermissionError` on every authorisation-write entry point.
10. **Import-linter contract (v1.4 B7)**: explicit declarations: `domain.*` may import `domain.*` and `domain.ports.*`; `engine.*` may import `domain.*` and `domain.ports.*` only — *never* `adapter.*`, `app.*`, `interface.*`; `app.*` may import `domain.*`, `domain.ports.*`, `engine.*`; `adapter.*` may import `domain.ports.*`, `domain.types`, plus external libraries. CI gate fails if any disallowed import is introduced.
11. **`sop-after-gates-check` (v1.4 B2)**: static + runtime check that `engine.sop_protocol.render` is reachable *only* from `app.protocol_orchestrator` *after* an `OperationalProtocolAuthorised` event has been observed in the design event stream for the active session.
12. **`llm-output-policy-check` (v1.4 M10)**: every LLM use site is wired through `app.constraint_translator` (or another `AdvisoryTextPolicy`-bound use site); every prompt template is versioned and pinned; every output passes a red-team test suite that asserts no operational protocol details are produced from LLM text; deterministic fallback exists when LLM is unavailable.
13. **`audit-traceability-check` (v1.4 M13)**: every accepted audit finding listed in `audit report/ARCHITECTURE_Audit_Response.md` and `audit report/ARCHITECTURE_Second_Audit_Response.md` has a row in the traceability table that resolves to existing file + section + test references.
14. **`plugin-manifest-signature` (v1.4 N7)**: every plugin loaded at runtime has a signed manifest whose signature verifies against the institution's plugin trust keyring; the manifest's declared package hash matches the loaded artefact's hash; the manifest's declared permissions are honoured by a runtime sandbox.
15. **`no-passive-advisory-bypass-check` (v1.5 — B3 strengthening)**: static + runtime check that the authorisation pipeline cannot advance to `OperationalProtocolAuthorised` without observing, in the governance event stream for the active session, a `RiskAdvisoryAcknowledged` event (with `decision = ACKNOWLEDGED` and a signature that verifies) for every advisory of severity `caution` or `strong_caution` listed in the `RiskAdvisoryReport.required_acknowledgements()`. The static side asserts no code path can construct an `OperationalProtocolAuthorised` event without first calling `all_required_advisories_acknowledged()` and getting `(True, frozenset())`. The runtime side: an adversarial test fixture attempts to authorise a construct with a `strong_caution` advisory but no acknowledgement event, and the test must observe `BlockOperationalProtocol` with an `AuthorisationAttemptDenied` audit entry citing the missing advisory IDs. UI-render-only tests verify that an `AdvisoryWarningPresented` event alone does *not* unblock authorisation — only the explicit acknowledgement does.

**Six-dimension audit gates** per phase exit (Correctness / Completeness / Scientific validity / Performance / Maintainability / Safety).

---

## 5. Resolved open questions (v1.1)

The 10 open questions from REQUIREMENTS.md §10:

| OQ | Resolution |
|---|---|
| OQ-01 | Python 3.11.15 pinned for core bootstrap; future patch bumps require lockfile + CI update. |
| OQ-02 | Web UI (React + TypeScript), Phase 12. |
| OQ-03 | Local-first single-user for v1; server-multi-user is Phase 14. |
| OQ-04 | Apache 2.0 for the engine; parts catalogues per-source licence. |
| OQ-05 | SpliceAI default; HTTP-service and lighter adapters provided. |
| OQ-06 | ViennaRNA Python bindings, pinned. |
| **OQ-07 (v1.1)** | UR-01 split: **UR-01a (MUST)** GenBank/SBOL/FASTA round-trip + automated SnapGene **file-watch** channel (Phase 9). **UR-01b (SHOULD)** Live SnapGene Server API channel (Phase 12), conditional on official API availability and acceptable licensing; falls back to UR-01a if unavailable. |
| OQ-08 | No direct vendor ordering in v1; Phase 15 stretch. |
| OQ-09 | YAML manifest + typed Python predicates + source-graded citations. |
| OQ-10 | English-first with full i18n hooks; Simplified Chinese in Phase 12. |

---

## 6. Residual risk register (v1.1)

| ID | Risk | Mitigation |
|---|---|---|
| R-01 | LLM constraint translator hallucinates a constraint. | Mandatory user review; constraint recorded with `origin: llm_translation`; pinned LLM model + prompt. |
| R-02 | Plugin version drift breaks reproducibility. | `DerivationEnvironment` captures all adapter versions + configurations; CI gate verifies. |
| R-03 | Codon × validator loop oscillates. | Lexicographic-priority fixed-point with N = 5 cap and explicit surfacing on failure. |
| R-04 | Rule registry grows unmaintainable. | Per-rule `last_reviewed` + `reviewed_by`; quarterly review for MR/WR/BR/MS; monthly for SR; alert-driven for screening. |
| R-05 | Screening adapter outages. | Multi-adapter fallback never produces `clear`; produces `UNAVAILABLE` or `MANUAL_REVIEW_REQUIRED`. |
| R-06 | SnapGene proprietary format drift. | Maintained third-party `.dna` parser; fallback to user-export-GenBank workflow; UR-01a is the MUST. |
| R-07 | SBOL 3.1.x spec evolution. | Pin to SBOL 3.1.x; round-trip property tests catch regressions on upgrade. |
| R-08 | Combinatorial libraries exceed performance budget. | Library size cap (configurable; default 10 000); batch screening; vectorised overhang fidelity. |
| R-09 | Determinism slips on platform variance. | Containerised release build with pinned CPU arch; determinism check runs in container. |
| R-10 | Free-text inputs leak confidential IP to a cloud LLM. | Default LLM adapter is local-LLM; cloud adapters require per-session explicit opt-in. |
| R-11 | AI-evasion of screening (2025 watch-item). | Track IGSC v3.x; AI-generated codon recodings of known hits route to manual review. |
| R-12 | Junior researcher misuses a generated protocol. | **(v1.1)** Operational protocols only render through `engine.sop_protocol` when authorisation gates pass; otherwise only `DesignRealisationPlan` is emitted. Hazard class and allowed-role fields enforce this. |
| **R-13 (v1.1)** | Catalogue staleness silently affects outputs. | Per-catalogue `valid_until` + `review_required_after`; CI gate `stale-catalogue-check`; `DerivationEnvironment` includes catalogue content hashes. |
| **R-14 (v1.1)** | Coordinate-and-graph round-trip is hard. | SBOL 3.1.x round-trip property test; GenBank features include `circular_wrap`, fuzzy locations, compound locations. |
| **R-15 (v1.1)** | Multi-host workflow misclassifies a marker conflict. | `engine.compatibility` iterates over each `HostContext` role independently; rules declare which roles they read; fixture coverage includes plant transient (3 hosts), lentivirus (3 hosts), AAV (3 hosts), VLP (4 hosts), cell-free (no propagation host). |
| **R-16 (v1.2)** | User attempts to self-elevate authorisation — e.g., editing the on-disk authorisation database, swapping their declared `role_of_operation`, registering a private SOP library, or invoking an admin endpoint with crafted credentials to render an operational protocol they should not be able to render. | (a) **Static**: `no-self-authorisation-check` CI gate prevents any User-scope code path from importing `AuthorisationStore.write_*` or reaching `AdminActionHandler`. (b) **Runtime**: every authorisation-write entry point checks `principal.role ∈ {Developer, Administrator}`; mismatch raises `PermissionError` and emits an audit-log `AuthorisationAttemptDenied` event with full context. (c) **Persistence**: `authorisation.sqlite` is opened read-only by engine and User-role processes; writes go through a separate admin service process. (d) **Integrity**: every `AuthorisationProfile` carries an institutional signature; tampered profiles fail verification on load and force re-mint by an Administrator. (e) **Declaration validation**: every user `UserDeclaration` is validated against the granted profile on every compile, not cached past `profile.valid_until`. (f) **Audit**: every grant / modify / revoke is recorded with actor + subject + diff + timestamp + signature in the immutable audit log. |
| **R-17 (v1.4)** | LLM-backed `ConstraintTranslator` or any other LLM use site generates operational protocol text, fabricated citations, or sequence-level design assertions that the user mistakes for authoritative output. | (a) `AdvisoryTextPolicy` enforces typed prompt templates with pinned versions; every prompt + model identifier is recorded in `DerivationEnvironment`. (b) `llm-output-policy-check` CI gate runs a red-team test suite that asserts no operational protocol details are produced from LLM text. (c) LLM output is typed `AdvisoryText` — a separate type from any authoritative computed data; UI affordances render LLM output in a visually distinct surface with an explicit "advisory only — not authoritative" label. (d) Citation checking — every cited PMID / DOI in LLM output is resolved against an offline corpus; unresolvable citations are stripped and flagged. (e) Deterministic fallback: when the LLM adapter is unavailable, the constraint translator returns a clear "manual translation required" error rather than producing a guess. (f) LLM is never invoked from within engine code paths; only from `app.constraint_translator` and `app.advisory_text_renderer`. |
| **R-18 (v1.4)** | Plugin trust escalation — a malicious or compromised plugin claims canonical status, performs unauthorised file I/O, or exfiltrates sequence data. | (a) `plugin-manifest-signature` CI gate verifies every plugin's manifest is signed by the institution's plugin trust keyring. (b) Plugin artefact hashes are recorded in `DerivationEnvironment.plugin_package_hashes`; mismatch on load fails the run. (c) Runtime sandbox enforces declared permissions per manifest; deterministic-path plugins have no network access. (d) `ScreeningProviderTrustPolicy` (B10) supersedes adapter self-declared `canonical: bool`; institutional registry controls which providers are trusted for which scopes. (e) Plugin manifest approvals are recorded as `PluginManifestApproved` governance events. |
| **R-19 (v1.4)** | Export bundle leaks PII (user IDs, reviewer notes), institutional approval IDs, or sensitive screening evidence to a downstream recipient (vendor, collaborator, publication supplement). | (a) Four typed `ExportProfile` values — `InternalAudit`, `Collaborator`, `Vendor`, `PublicationSupplement` — each with explicit `RedactionPolicy` rules. (b) `redaction_policy_version` recorded in `DerivationEnvironment`. (c) Export orchestrator enforces redaction at serialisation time; emits `ExportProfileRedactionApplied` event with the applied rules. (d) Privacy classification (`PrivacyClassification`) tags every field; redaction rule per classification per profile. |
| **R-20 (v1.4)** | User attempts to design or render a construct for an unsupported biosafety tier (e.g., BSL-4). | (a) Compile-time hard block on unsupported tiers; raises `BlockCompile` and emits `UnsupportedBiosafetyTierAttempted` governance event with user-facing reason. (b) The unsupported-tier list is policy-controlled in `institutional_policy.yaml`. (c) Test fixtures verify BSL-4 attempt produces no operational artefact and no vendor submission. |
| **R-21 (v1.5)** | An Administrator (or any actor) silently bypasses the advisory layer — e.g., via a passive UI render that requires no explicit action, by ignoring a banner, by dismissing a warning without acknowledgement, or by reaching the authorisation pipeline through a path that skips `engine.risk_classification` or that constructs an `OperationalProtocolAuthorised` event without first observing the matching `RiskAdvisoryAcknowledged` events. | (a) **Active acknowledgement contract**: warnings are not UI banners. Every advisory of severity `caution` or `strong_caution` *requires* an explicit signed `RiskAdvisoryAcknowledgement` (justification ≥ 20 chars + cryptographic signature) before authorisation can proceed. (b) **Static**: `no-passive-advisory-bypass-check` CI gate proves no code path can construct `OperationalProtocolAuthorised` without first calling `all_required_advisories_acknowledged()` and getting `(True, frozenset())`. (c) **Runtime**: the authorisation orchestrator re-checks the governance event stream on every attempt and rejects with `BlockOperationalProtocol` + `AuthorisationAttemptDenied` audit entry if any required advisory is unacknowledged. (d) **UI**: presentation surfaces (CLI / API / UI) offer only three paths — *acknowledge*, *decline*, *escalate* — and never a "dismiss without action" affordance. (e) **Auditability**: every presentation emits an `AdvisoryWarningPresented` governance event; every acknowledgement / decline / escalation emits the corresponding typed governance event; the full approval trace is included by reference in `DerivationEnvironment` and in every exported bundle. (f) **Replay**: a deterministic replay must reproduce the exact approval trace from the audit log; mismatched traces fail the determinism CI gate. (g) **Adversarial test fixture**: a UAT scenario that attempts each known bypass path (UI render only, malformed acknowledgement, unsigned acknowledgement, acknowledgement for a different construct version, acknowledgement with empty justification) and verifies every one is rejected. |

---

## 7. Sign-off

**`/scientific-advisor` (v1.1):** "Codex's biological findings are correct in every case. The role-keyed host context, the coordinate-and-graph data model, the `engine.sequence_analysis` module, the `CodingSequenceDesign` input, the expanded screening verdict enum, the MS-* rule family, the source-grade citation gate, and the split between non-operational design realisation and gated SOP-linked operational protocols collectively bring the biology and the safety policy into the type system. Approved for v1.1."

**`/architect` (v1.1):** "Codex's architectural findings are correct in every case. The `SequenceRecord` / `Location` / `Feature` / `ConstructGraph` types, the comprehensive `DerivationEnvironment` hash, the pure-validator with `ValidationContext`, the typed `AssemblyPlan` subclasses, the typed `DomainEvent` subclasses, the four typed safety gates, the read-only `PartCatalogue` with `PartLibraryService` writing via events, and the per-catalogue maintenance metadata bring the architecture into a state that can survive Phase 2 hardening without retrofitting. Approved for v1.1."

**`/dev-orchestrator` (v1.1):** "Codex's operational findings are correct in every case. The two-tier performance budget separates release-blocker determinism from production-adapter SLA. The expanded `ValidationRule` manifest (with `depends_on_metrics`, `invalidates`, `external_adapters`, `last_reviewed`, `test_fixtures`) makes the rule engine governable. The `stale-catalogue-check` and `no-domain-impurity-check` CI gates make architectural intent enforceable. Approved for v1.1."

**`/dev-orchestrator` (v1.2):** "The sponsor's sharpening of C1 is correct and structurally necessary. v1.1 placed user-declared SOP/biosafety bindings at the heart of the operational-protocol gate, which would have allowed a determined user to self-elevate by writing their own SOP file or asserting an arbitrary biosafety approval ID. v1.2 separates the *granted profile* (admin-only, signed, audit-logged) from the *declared intent* (user-supplied, validated against the granted profile). The `Role` enum, the `Principal` hierarchy, the `AuthorisationStore` with split read-only and write-restricted methods, the `AdminActionHandler` application service, the `authorisation.sqlite` admin-only store, the `no-self-authorisation-check` static CI gate, the runtime PermissionError defence, and the new R-16 risk-register entry collectively eliminate the self-elevation pathway. The audit trail in `audit.sqlite` becomes the legal record of who granted whom what authorisation. Approved for v1.2."

**`/dev-orchestrator` (v1.3):** "The sponsor's role-hierarchy clarification is operationally well motivated. Many institutions do not appoint a separate biosafety officer for small labs; forcing a dedicated Reviewer role into the workflow would have created either an artificial bottleneck or a real-world workaround in which the same person logs in under two principals. The v1.3 model — `Administrator ⊇ Reviewer` via an explicit `Principal.can_act_as` predicate, with `Reviewer ⊄ Administrator` preserved so a Reviewer cannot escalate — collapses the artificial bottleneck while preserving the security boundary. The `signer_role` discriminator on `ReviewerSignedOff` keeps the audit trail honest (an Administrator signing in Reviewer capacity is distinguishable from a dedicated Reviewer). FR-AUTH-13 / FR-AUTH-14 codify the asymmetry. The Phase-13 Administrator-only end-to-end UAT verifies that the full workflow completes without a separate Reviewer present. Approved for v1.3."

**`/scientific-advisor` (v1.4):** "Codex's second audit is rigorous and almost entirely correct. The screening-before-SOP reordering (B2), the expanded `CoveredBiologicalScope` (B4), the annotated I/O contracts (B5), the structured `Qualifier` (B6), the formal `Location` algebra (M3), the canonical-graph-with-derived-feature-table rule (M4), the contextual `HostCompatibilityConstraints` (M5), the BSL-4 hard block (M7), the MS2/VLP design policy module (M9), the AdvisoryTextPolicy (M10), and the mechanistic control-validation rules (N8) all align the architecture with real molecular-biology practice. The B3 defense — keep Administrator-only completion plus advisory `BiosafetyClassificationLayer` — is consistent with the platform's scope (DNA sequence design, not direct biological manipulation) and is strengthened by the new advisory layer. Approved for v1.4."

**`/architect` (v1.4):** "The architectural findings produce a cleaner, more testable system. The `domain.ports/` separation with `import-linter` enforcement (B7) closes the long-standing domain-purity weakness. The split authorisation ports (Read / AdminWrite / Bootstrap; B8) and split events (design / governance / export; M12) eliminate the type-signature mismatches Codex identified. The signed `DecisionRecord` + `RoleSnapshot` (B9) makes sign-offs cryptographically verifiable and replay-safe. The five typed hashes (M2) and the expanded `DerivationEnvironment` (B11) make replay deterministic across template, plugin, and policy changes. The `domain.types.sop_protected` namespace (M11) guarantees at type level that a `DesignRealisationPlan` cannot contain an operational `ProtocolStep`. Approved for v1.4."

**`/dev-orchestrator` (v1.4):** "The operational findings are all correct. The new CI gates — `import-linter` (B7), `sop-after-gates-check` (B2), `llm-output-policy-check` (M10), `audit-traceability-check` (M13), `plugin-manifest-signature` (N7) — make the architectural intent enforceable in code, not merely documented. The pipeline reordering (B2 + B12) is structurally necessary; the three-stream event split (M12) eliminates the design-vs-governance event confusion. The wet-lab-success acceptance criteria softening (M8) places empirical validation outside ordinary CI, where it belongs. The B3 defense is operationally sound for the platform's scope; the data model still carries `DualControlFlags` so institutions that require stricter governance can enable it via `InstitutionalPolicy` without an architectural change. Approved for v1.4."

**`/scientific-advisor` (v1.5):** "The sponsor's B3 strengthening is the right correction. v1.4's mitigation said the right things conceptually but rested too heavily on the assumption that an Administrator would *see* the advisory and *act* on it. A passive banner can be ignored; a UI render alone leaves no audit trail and cannot be replayed. v1.5 makes the advisory layer a typed, signed, replayable governance protocol: every presentation is logged; every acknowledgement is a signed action with justification; the report is bound to the design record by content hash so the trace is unambiguous even when the construct is revised; the three available paths — acknowledge / decline / escalate — match the real institutional decision space without leaving room for a silent skip. The biology stays correctly framed (this platform designs DNA sequences; it does not manipulate physical biology), and the new acknowledgement protocol now matches the rigour of the v1.2 / v1.3 authorisation gating. Approved for v1.5."

**`/architect` (v1.5):** "The strengthening is structurally clean. `RiskAdvisoryReport` now binds to `design_session_id` + `construct_id` + `construct_checksum` + `report_content_hash` so it is unambiguously a part of the design record. `RiskAdvisoryAcknowledgement` reuses the existing signed `DecisionRecord` machinery (B9), so cryptographic verification, role-snapshot binding, and replay-safety are inherited rather than reinvented. The four new governance events (`AdvisoryWarningPresented`, `RiskAdvisoryAcknowledged`, `RiskAdvisoryDeclined`, `RiskAdvisoryEscalated`) fit cleanly into the existing three-stream split (M12). The gate predicate `all_required_advisories_acknowledged()` is a pure function over the governance stream — testable, replayable. The new CI gate `no-passive-advisory-bypass-check` is a natural complement to the v1.4 gates and reuses the same static-analysis machinery. Approved for v1.5."

**`/dev-orchestrator` (v1.5):** "The strengthening is operationally essential. v1.4's B3 mitigation would have failed a real audit because there was no enforceable contract that the Administrator's awareness translated to a logged, replayable approval action. v1.5 makes the contract typed and enforceable in code: the static CI gate proves the bypass is impossible; the runtime test fixtures verify every known bypass path (UI render only, malformed acknowledgement, unsigned, version-mismatched, empty justification) is rejected with `BlockOperationalProtocol`; the audit trail is a first-class artefact persisted in the governance event stream and replayable from the audit log. The new R-21 risk-register entry catalogues six concrete mitigations covering static, runtime, UI, auditability, replay, and adversarial-test surfaces. UR-11, FR-ADV-01..07, and BR-14 are added to REQUIREMENTS.md so the contract is binding at the requirements level too. Approved for v1.5."

---

## 8. Appendices

### Appendix A — Diagram index

| Diagram | Section |
|---|---|
| Layer stack | § 4.1 |
| End-to-end data flow | § 4.3 |
| Design-session state machine with four safety gates | § 4.4 |
| Typed event stream | § 4.7 |
| Project directory layout | § 4.8 |

### Appendix B — Traceability: REQUIREMENTS → ARCHITECTURE v1.5

| REQUIREMENTS family | Implemented by ARCHITECTURE v1.5 modules |
|---|---|
| UR-01a SnapGene file-watch round-trip (MUST) | `adapter.snapgene.SnapGeneFileWatcher` + `adapter.io` (GenBank round-trip) |
| UR-01b SnapGene live API (SHOULD) | `adapter.snapgene.SnapGeneApiClient` (Phase 12) |
| UR-02 Decision-tree UI + free-text | `app.decision_tree` + `app.constraint_translator` + `interface.ui` |
| UR-03 Core cloning functions | `engine.sequence_analysis` + `engine.assembly` + `engine.primer` + `engine.codon` + `engine.overhang` |
| UR-04 Modular block assembly | `domain.types` + `domain.library` + `domain.graph` + `adapter.catalogue` |
| UR-05 Plasmid copy-number selection | `engine.compatibility` + part `host_compatibility` field |
| UR-06 Host-strain database with multi-host compatibility | `adapter.catalogue.HostCatalogue` + `engine.compatibility` + `HostContext` role-map |
| UR-07 Enzyme database | `adapter.catalogue.EnzymeCatalogue` |
| UR-08a Wet-lab design realisation plan | `engine.design_plan` + `app.protocol_orchestrator` |
| UR-08b SOP-linked operational protocol | `engine.sop_protocol` (gated) + `app.protocol_orchestrator` |
| FR-CORE-* | `engine.*` family in § 4.2.1 |
| FR-VAL-* | `engine.validation` + `engine.dependencies` + `app.validation_orchestrator` (metric pre-compute) |
| FR-PRIM-* | `engine.primer` + `app.primer_orchestrator` + `PrimerDesignParameters` |
| FR-PROTO-DESIGN-* | `engine.design_plan` |
| FR-PROTO-SOP-* | `engine.sop_protocol` + `SopTemplateReadPort` / signed `SqliteSopTemplateStore` |
| FR-IO-* | `adapter.io` |
| FR-PROJ-* | `engine.session` + `adapter.persistence` |
| MR-* / WR-* / SR-* / BR-* / **MS-*** | `catalogues/rules/*.yaml` + registered predicates |
| NFR-PERF-* | § 4.9 two-tier budgets |
| NFR-USAB-* | `interface.ui` + in-app help drawn from white paper |
| NFR-REL-* | `engine.session` event sourcing + § 4.10 CI gates |
| NFR-SEC-* | local-first persistence + `adapter.screening` blinded queries |
| NFR-MAINT-* | adapter pattern + YAML catalogues + maintenance metadata |
| NFR-COMPLY-* | `domain.types.Licence` + `THIRD_PARTY_LICENSES.md` + source-graded citations |
| SC-* | § 4.1 + § 4.5 + § 4.6 |
| DR-* | § 4.6 (canonical schema) |
| AC-* | § 4.10 tier-3 UAT (extended with multi-host, MS-*, SOP-gated cases) |

### Appendix C — Hand-off briefs for the next phases (v1.5)

#### C.1 Phase 2 brief — Project scaffold

- Python 3.11.15 project with `uv` + lockfile; pinned interpreter.
- Directory layout per § 4.8 including `catalogues/sop_templates/` and `catalogues/rules/MS.yaml`.
- Stub packages with the public APIs of every module in § 4.2 — including the v1.5 scaffold modules (`engine.sequence_analysis`, `engine.design_plan`, `engine.sop_protocol`, `engine.controls`, `app.controls_orchestrator`, `app.part_library_service`).
- CI workflow: `ruff` + `mypy --strict` + `pytest` + `pytest-cov` + determinism harness (Docker / Podman with pinned interpreter and dependencies) + `stale-catalogue-check` skeleton + `no-domain-impurity-check` skeleton + `source-grade-citation-check` skeleton.
- `THIRD_PARTY_LICENSES.md` stub.
- Engine licence file (Apache 2.0).
- Skeleton docs site (mkdocs-material).

**Acceptance:** `uv build` succeeds; `uv sync --frozen --no-editable --group dev` succeeds; `mypy --strict` passes on stubs; `pytest` bootstrap smoke tests run cleanly; implemented CI gates run green.

#### C.2 Phase 3 brief — Core domain model + sequence I/O round-trip

- Implement `domain.sequence`, `domain.graph`, `domain.types` per § 4.6 — *including the new v1.1 types*.
- Implement `adapter.io` for GenBank, FASTA, SBOL 3.1.x with round-trip property tests **including circular topology, reverse-strand features, compound locations, and circular-wrap features**.
- Implement `engine.session` (typed-event sourcing) with SQLite persistence.

**Acceptance:** the bacterial Example A construct (white paper § 26) round-trips through GenBank and SBOL 3.1.x byte-identically; circular plasmid topology is preserved; reverse-strand features are preserved.

#### C.3 Phase 4 brief — Catalogues

- Implement `adapter.catalogue` (Part, Host, Enzyme, RuleRegistry) as YAML loaders; SOP-template YAML is bootstrap input for signed `SqliteSopTemplateStore`, not a runtime SOP-template library.
- Populate `catalogues/parts.yaml`, `hosts.yaml`, `enzymes.yaml`, `rules/MR.yaml`, `rules/WR.yaml`, `rules/SR.yaml`, `rules/BR.yaml`, **`rules/MS.yaml`** from v2.0 KB §§ 5–7 + § 17.
- Implement manifest validation at startup (every rule manifest entry has a registered predicate; every entry has a `citation.grade`).
- Implement `stale-catalogue-check` against the maintenance metadata.
- Vendor profile YAMLs include `maintenance` metadata.

**Acceptance:** every catalogue YAML validates; every rule manifest resolves to a registered predicate (stubs OK at this phase); the source-grade citation gate passes (every entry has a graded citation); `stale-catalogue-check` passes (all maintenance metadata is in the future).

---

*End of ARCHITECTURE.md v1.5 — Universal Cloning/Expression Vector Design Platform.*
