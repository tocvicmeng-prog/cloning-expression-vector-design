# Universal Cloning / Expression Vector Design Software — Roadmap (v1.5 consistency release)

**Prepared:** 2026-05-13 | **Last regenerated:** 2026-05-14 (CODING_AGENDA v1.5 fifth-round consistency release; active sections aligned to split task IDs, signed SOP-template ports, admin/audit service modules, and `DeveloperBootstrapPrincipal`).
**Derived from:** `ARCHITECTURE.md` **v1.5** + `CODING_AGENDA.md` **v1.5**. This file is regenerated whenever either changes; for *implementation-discipline + phasing decisions*, `CODING_AGENDA.md` v1.5 is the canonical source.
**Audit-response trail:** `audit report/ARCHITECTURE_Audit_Report.md` + Response (31/31); `ARCHITECTURE_Second_Audit_Report_v1_2.md` + Response (31/32 with B3 defence + v1.5 sponsor strengthening); `CODING_AGENDA_Audit_Report.md` + Response (21/21 → v1.1); `CODING_AGENDA_Second_Round_Audit_Report.md` + Response (29/29 → v1.2); `CODING_AGENDA_Third_Round_Audit_Report.md` + Response (27/27 → v1.3); `CODING_AGENDA_Fourth_Round_Audit_Report.md` + Response (27/27 → v1.4); **`CODING_AGENDA_Fifth_Round_Audit_Report.md` remediation (v1.5 consistency release)**.
**v1.5 phase order (binding, unchanged from v1.2 with Phase 10 physically placed before 8b):** 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → **8a** → **9a** → **10** → **8b** → **9b** → 11 → 12 → 13. Section 2 of `CODING_AGENDA.md` v1.5 physically orders Phase 10 between Phase 9a and Phase 8b (v1.4 B4-01, rechecked in v1.5) — heading-order parsers emit T-1001/T-1002 before T-803/T-806b/T-903. (Pre-v1.2 single Phase 8 / single Phase 9 are obsolete; legacy text moved to Appendix A — `Legacy-Pre-v1.2-Phase-8` / `Legacy-Pre-v1.2-Phase-9` — per v1.3 H3-04.)
**Source of authority:** `ARCHITECTURE.md` § 4.2 (module catalogue) defines *what* is built; `CODING_AGENDA.md` v1.5 defines *implementation phasing* (this roadmap regenerated from it); this file defines the *dependency-ordered phase view* for stakeholder reading. If `CODING_AGENDA.md` disagrees with this file on phasing, the agenda wins and this file is regenerated.
**Status:** Phase 0 + Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5 + Phase 6 complete locally, and Phase 7 is complete locally through T-701. T-701 delivered the pure `engine.codon` package with algorithm selection, fixed-point optimisation, protected-interval preservation, and codon metrics. T-702 `engine.overhang` is the next hand-off.
**Hand-off skills:** `/architect` (system design); `/dev-orchestrator` (multi-module implementation); `/scientific-coder` (per-module implementation); `/scientific-advisor` (ongoing KB and rule-registry maintenance); `/ip-auditor` (when commercialisation enters scope).

---

## How to read this roadmap

- Phases are **strictly ordered by dependency**: each phase relies on a public API delivered by an earlier phase.
- Every phase ends with **six-dimension audit gates** (Correctness / Completeness / Scientific validity / Performance / Maintainability / Safety) per ARCHITECTURE § 4.10.
- Every phase produces a **milestone handover document** (`docs/handover/<phase>_handover.md`).
- **Model tier per module** is recorded in the module registry per the dev-orchestrator convention.
- **v1.5 impact note:** Phase scopes are binding against ARCHITECTURE.md v1.5. Where earlier roadmap versions targeted v1.0/v1.1 types, those briefs are superseded. The dependency order is unchanged.

---

## Phase 0 — Foundations (✅ COMPLETE)

| Deliverable | File |
|---|---|
| v1.0 knowledge base (historical primer) | `Cloning_and_Expression_Vector_Design_Knowledge_Base_v1_0.md` |
| Cross-audit v1.0 → v2.0 | `Cloning_KB_v2_Audit_Report.md` |
| v2.0 software-grade knowledge base | `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` |
| First-principles white paper | `Cloning_Expression_Vector_Design_White_Paper.md` |
| Project root scaffolding | `README.md` |
| Software requirements specification | `REQUIREMENTS.md` |

---

## Phase 1 — Architectural framework (✅ COMPLETE)

| Deliverable | File |
|---|---|
| Initial three-role architectural blueprint (v1.0) | `ARCHITECTURE.md` v1.0 (superseded) |
| External audit by Codex | `audit report/ARCHITECTURE_Audit_Report.md` |
| Three-role audit response (31/31 findings accepted) | `audit report/ARCHITECTURE_Audit_Response.md` |
| Upgraded authoritative blueprint after Codex audit (v1.1) | `ARCHITECTURE.md` v1.1 (superseded) |
| Sponsor sharpening of C1 — administrator-controlled gate (v1.2) | `ARCHITECTURE.md` v1.2 (superseded) |
| Sponsor clarification — `Administrator ⊇ Reviewer`, `Reviewer ⊄ Administrator` (v1.3) | `ARCHITECTURE.md` v1.3 (superseded) |
| Second Codex external audit (32 findings) | `audit report/ARCHITECTURE_Second_Audit_Report_v1_2.md` |
| Three-role response to second audit (31/32 accepted, B3 defended with mitigation) | `audit report/ARCHITECTURE_Second_Audit_Response.md` |
| Upgraded authoritative blueprint after second audit (v1.4) | `ARCHITECTURE.md` v1.4 (superseded) |
| Sponsor strengthening of B3 — active, auditable, design-record-tied advisory acknowledgement (v1.5) | `ARCHITECTURE.md` v1.5 (current) |

**v1.1 substantive upgrades** (full per-finding adjudication in the audit-response file): coordinate-and-graph data model (`SequenceRecord` / `Location` / `Feature` / `ConstructGraph`); role-keyed `HostContext`; new `engine.sequence_analysis` module; split `engine.protocol` into `engine.design_plan` + `engine.sop_protocol`; new `engine.controls`; expanded `ValidationRule` manifest (`depends_on_metrics`, `produces_metrics`, `invalidates`, `preconditions`, `target_context`, `external_adapters`, `last_reviewed`, `test_fixtures`, graded citations); comprehensive `DerivationEnvironment` hash; pure validation engine with `ValidationContext`; typed `AssemblyPlan` subclasses; typed `DomainEvent` subclasses; expanded `ScreeningVerdict` enum; four typed safety gates (`BlockCompile` / `BlockExport` / `BlockVendorSubmission` / `BlockOperationalProtocol`); per-catalogue maintenance metadata; two-tier performance budgets; MS-* rule family; `CodingSequenceDesign` input; `PrimerDesignParameters`.

**v1.2 substantive upgrades** (sponsor sharpening of C1): the `BlockOperationalProtocol` gate's authorisation profile is administrator-controlled, not user-self-declared. Introduces: `Role` enum (`Developer` / `Administrator` / `Reviewer` / `User`); typed `Principal` hierarchy; admin-only `AuthorisationProfile`; new `AuthorisationStore` port with strict read/write split; new `app.admin_action_handler` application service (sole write path to authorisation data); typed `AdminActionMinted` / `Modified` / `Revoked` events; new `authorisation.sqlite` admin-only store; new CI gate `no-self-authorisation-check`; new risk R-16 (user self-elevation); new requirements FR-AUTH-01 .. FR-AUTH-12 and BR-11 / BR-12 / BR-13.

**v1.3 substantive upgrades** (sponsor clarification on role hierarchy): asymmetric inheritance — `Administrator ⊇ Reviewer`, `Reviewer ⊄ Administrator`. Introduces: `ROLE_INHERITS` map; `Principal.can_act_as(required_role)` predicate; `ReviewerSignedOff` event carries a `signer_role: Role` discriminator (so the audit trail distinguishes a dedicated Reviewer from an Administrator-acting-as-Reviewer); new requirements FR-AUTH-13 (Admin ⊇ Reviewer) and FR-AUTH-14 (Reviewer ⊄ Admin); new UR-10. Practical consequence: an institution that does not appoint a separate biosafety officer may complete the entire authorisation workflow with an Administrator alone — verified by a Phase-13 Administrator-only end-to-end UAT.

**v1.4 substantive upgrades** (second Codex audit; 31/32 accepted, B3 defended with advisory mitigation):

- **Pipeline reorder (B2, B12)**: SOP rendering moves strictly downstream of screening + authorisation. New states `AWAITING_SCREENING` → `AWAITING_REVIEWER_SIGNOFF` (for `WATCHLIST` / `MANUAL_REVIEW_REQUIRED` / `UNAVAILABLE`) → `AWAITING_AUTHORISATION` → `AWAITING_SOP_RENDER` → `READY_TO_EXPORT`. Compile produces NO operational artefact.
- **B3 mitigation — advisory `BiosafetyClassificationLayer`**: new `engine.risk_classification` + `catalogues/risk_advisories.yaml` auto-flags high-risk genetic elements, elevated-BSL sequences, constructs that may require institutional approval. Surfaces structured warnings to Administrators when granting permissions. Advisory only — does not autonomously block. Dual-control flags added as opt-in data-model hooks for institutions that require stricter governance.
- **Authorisation scope expansion (B4)**: `CoveredBiologicalScope` covers cargo classes, vector system classes, replication competence, insert size, host role, target organism, screening-exception class, institutional protocol IDs, jurisdictional constraints, component lineage trust.
- **Annotated I/O contracts (B5)**: `SequenceReader` / `Writer` move `ImportedConstruct` / `AnnotatedConstruct` with feature table, structured qualifiers, construct graph, SBOL mapping, SnapGene visual metadata, primer annotations, lossy-conversion warnings.
- **Structured `Qualifier` (B6)**: replaces `dict[str, str]` with `tuple[Qualifier, ...]`; supports repeated keys, ordering, structured values, namespaces.
- **`domain.ports/` separation (B7)**: all port interfaces under `domain.ports`; `import-linter` CI gate enforces engine cannot import `adapter.*`.
- **Split events + ports (B8, M12)**: three event streams — design / governance / export. Split authorisation ports — Read / AdminWrite / Bootstrap.
- **Signed `DecisionRecord` + `RoleSnapshot` (B9)**: sign-offs cryptographically and semantically bound; replay-safe.
- **`ScreeningProviderTrustPolicy` (B10)**: adapter trust moved to institutional registry; screening at assembled-product level by default.
- **Expanded `DerivationEnvironment` (B11)**: profile hashes, SOP template content hashes, screening trust policy version, plugin package hashes, LLM prompt template versions, institutional policy version, redaction policy.
- **B1 harmonisation**: `REQUIREMENTS.md` FR-PROTO split into FR-PROTO-DESIGN-* (MUST, non-operational) and FR-PROTO-SOP-* (SHOULD, gated). AC-01 / AC-02 / AC-03 softened — wet-lab success is not a CI gate.
- **Five typed hashes (M2)**, **formal location algebra (M3)**, **canonical graph + derived feature-table (M4)**, **contextual `HostCompatibilityConstraints` (M5)**, **`SecurityRole` vs `OperationalRole` split (M6)**, **BSL-4 hard block (M7)**, **MS2/VLP design policy + `engine.vlp_policy` (M9)**, **`AdvisoryTextPolicy` + `llm-output-policy-check` CI gate (M10)**, **`domain.types.sop_protected` namespace (M11)**, **traceability table + `audit-traceability-check` CI gate (M13)**.
- **Moderate**: version-label normalisation (N1), requirement-ID reconciliation (N2), SBOL 3.1.x terminology (N3), canonical protocol-DAG serialisation (N4), typed `ScreeningError` taxonomy (N5), four export profiles + redaction policies (N6), plugin manifest signing (N7), mechanistic control validation rules (N8).
- New CI gates: `import-linter`, `sop-after-gates-check`, `llm-output-policy-check`, `audit-traceability-check`, `plugin-manifest-signature`.
- New risks: R-17 (LLM unsafe output), R-18 (plugin trust escalation), R-19 (export PII leak), R-20 (unsupported biosafety tier).

**v1.5 substantive upgrade** (sponsor strengthening of the B3 mitigation): advisory warnings must be active, auditable, tied to the design record. Introduces:

- `RiskAdvisoryReport` carries `design_session_id`, `construct_id`, `construct_checksum`, `report_content_hash`, plus a stable `advisory_id` per item.
- `RiskAdvisoryAcknowledgement` typed signed record (justification ≥ 20 chars + cryptographic signature via the existing `DecisionRecord` machinery from B9).
- Four new governance events: `AdvisoryWarningPresented`, `RiskAdvisoryAcknowledged`, `RiskAdvisoryDeclined`, `RiskAdvisoryEscalated`.
- `all_required_advisories_acknowledged()` gate predicate; the authorisation gate consults it before emitting `OperationalProtocolAuthorised`.
- New CI gate `no-passive-advisory-bypass-check` proves the bypass is statically impossible.
- New requirements: **UR-11**, **FR-ADV-01 … FR-ADV-07**, **BR-14**.
- New risk **R-21** (advisory bypass) with six concrete mitigations.
- UI affords only three paths on `caution` / `strong_caution` warnings: *acknowledge with justification*, *decline (route to alternative reviewer / dual-control)*, *escalate (institutional sign-off)*. No "dismiss without action".
- The full approval trace (presentation → acknowledgement / decline / escalation → authorisation decision) is persisted in the immutable governance event stream and is part of the `DerivationEnvironment`. Replay must reproduce the trace.

---

## Phase 2 — Project scaffold (✅ COMPLETE LOCALLY)

**Owner:** `/dev-orchestrator`. **Model tier:** Sonnet (scaffolding) with Opus review.
**Inputs:** ARCHITECTURE.md v1.5 § 4.1, § 4.5, § 4.8, § 4.10, Appendix C.1; CODING_AGENDA.md v1.5 § 2.2.

### Deliverables

- Initialised Python 3.11.15 project with `uv` + lockfile. Pinned interpreter.
- Directory layout per ARCHITECTURE § 4.8: `domain/`, `engine/`, `app/`, `adapter/`, `interface/`, `tests/`, `docs/`, `catalogues/` (incl. `sop_templates/`, `rules/` with `MR.yaml` / `WR.yaml` / `SR.yaml` / `BR.yaml` / **`MS.yaml`**, `vendor_profiles/`, `screening_profiles/`), `events/`, `snapshots/`, `exports/`.
- Stub packages with the public APIs of every module in ARCHITECTURE § 4.2 — **including the v1.1 + v1.2 new modules**:
  - `domain.sequence`, `domain.graph`, `domain.types` (with v1.1 + v1.2 types — including `Role`, `Principal` hierarchy, `AuthorisationProfile`, `UserDeclaration`, `AuthorisationDecision`, `AdminAction*` events)
  - `engine.sequence_analysis`
  - `engine.design_plan`
  - `engine.sop_protocol`
  - `engine.controls`
  - `app.controls_orchestrator`
  - `app.part_library_service`
  - **`app.admin_action_handler`** (v1.5 — admin-service-only write path to `AuthorisationStore`, SOP-template admin write/bootstrap ports, and authorisation-related audit-log entries)
  - **`adapter.persistence.SqliteAuthorisationStore`** (v1.2 — opened read-only by engine; writes only via `app.admin_action_handler`)
- All stubs raise `NotImplementedError` with typed signatures.
- CI workflow: `ruff` lint, `mypy --strict` type check, `pytest` test run, `pytest-cov` coverage; determinism harness (Docker / Podman with pinned interpreter and pinned dependencies); skeletons for `stale-catalogue-check`, `no-domain-impurity-check`, `source-grade-citation-check`, **`no-self-authorisation-check`** (v1.2) CI gates.
- `THIRD_PARTY_LICENSES.md` stub.
- Engine licence file (Apache 2.0).
- `docs/` site (mkdocs-material) skeleton.
- Pre-commit hooks: format, lint, type-check.

### Exit criteria (six-dimension audit)

1. *Correctness*: scaffold builds; `uv build` succeeds; `uv sync --frozen --no-editable --group dev` succeeds.
2. *Completeness*: every module in ARCHITECTURE v1.5 § 4.2 has a stub with typed signatures; every plugin port has a Protocol declared.
3. *Scientific validity*: N/A at scaffold.
4. *Performance*: build < 30 s on a 4-core machine.
5. *Maintainability*: `mypy --strict` green; `ruff` clean; documentation pages generate.
6. *Safety*: licence files present; no secrets; pre-commit hooks installed.

---

## Phase 3 — Core domain model + sequence I/O round-trip

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Opus (domain types) + Sonnet (I/O adapters).
**Inputs:** ARCHITECTURE.md v1.5 § 4.6 (data model), § 4.5 (SequenceReader/Writer ports), Appendix C.2.

### Deliverables

- `domain.sequence` fully implemented per § 4.6: `Sequence` ADT and sub-types (`DnaSequence`, `RnaSequence`, `ProteinSequence`, `OligoSequence`), `SequenceRecord` (with topology and canonical-orientation checksum), `Location` (with `circular_wrap`, fuzzy bounds, compound sub-locations), `Feature` (with graded citation evidence), `InsertionContext`.
- `domain.graph` fully implemented: `GraphNode`, `Edge` (with `EdgeKind`), `ConstructGraph` (topology-aware).
- `domain.types` fully implemented: `Part`, `Module`, `Construct` (with `modules` + `graph` views), `Library`, `OneOf`, `Variable`, `Override`, `HostContext`, `Host`, `AssemblyMethod`, `AssemblyPlan` (typed subclasses), `ValidationRule` (expanded manifest with graded citation), `ProtocolStep` (with SOP/QC fields), `ProtocolDAG`, `DesignRealisationPlan`, `SopLinkedProtocol`, `ControlSet`, `ScreeningResult` (expanded verdict enum), `DerivationEnvironment` (with canonical JSON + hash), `CodingSequenceDesign`, typed `DomainEvent` subclasses.
- `domain.library`: `expand` function (replaces v1.0's iterator field).
- `adapter.io`: `GenBankAdapter`, `FastaAdapter`, `Sbol3Adapter` (pinned pySBOL3 ≥ 1.3 against SBOL 3.1.x using `Component` / `Sequence` / `SequenceFeature` terms), `SnapGeneDnaReader` (read-only).
- `engine.session` (typed-event sourcing) backed by SQLite + JSONL event log; snapshot management keyed by `DerivationEnvironment.hash()`.

### Exit criteria

1. *Correctness*: SBOL 3.1.x and GenBank round-trip property tests pass for arbitrary valid Constructs — **including circular topology, reverse-strand features, compound locations, and circular-wrap features**.
2. *Completeness*: every v1.1 type has a constructor with validation, an equality, and a stable hash; `DerivationEnvironment.canonical_json()` is byte-deterministic across platforms.
3. *Scientific validity*: white-paper Example A (§ 26) round-trips through GenBank and SBOL 3.1.x byte-identically; circular plasmid topology preserved; reverse-strand features preserved.
4. *Performance*: 10 MB GenBank file parses in < 1 s.
5. *Maintainability*: 90 % line coverage on `domain/` and `adapter/io/`; `mypy --strict` green; `no-domain-impurity-check` passes (domain imports nothing from `adapter/` or `app/`).
6. *Safety*: no plaintext credentials; canonical-orientation checksum is rotation-invariant for circular sequences.

---

## Phase 4 — Catalogues (parts, hosts, enzymes, rule registry, SOP templates)

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder` + `/scientific-advisor` (data review). **Model tier:** Sonnet (loaders) + Opus (catalogue content review).
**Inputs:** ARCHITECTURE.md v1.5 § 4.8 (YAML layout, maintenance metadata), § 4.5 (catalogue ports), Appendix C.3; v2.0 KB §§ 5, 6, 7, 17 (MS2/VLP), 18 (citations).

### Deliverables

- `adapter.catalogue.YamlPartLoader` (read-only).
- `adapter.catalogue.YamlHostLoader` (HostCatalogue).
- `adapter.catalogue.YamlEnzymeLoader` (EnzymeCatalogue with buffer-compatibility matrix).
- `adapter.catalogue.YamlRuleRegistryLoader` reading `catalogues/rules/MR.yaml`, `WR.yaml`, `SR.yaml`, `BR.yaml`, **`MS.yaml`**.
- `adapter.catalogue.YamlSopTemplateLoader` (empty by default; reads institution-owned templates).
- `adapter.catalogue.YamlVendorProfileLoader` (Twist / IDT / GenScript).
- `adapter.security.sop_template_signing` production Ed25519 signer/verifier, key archive purpose, offline verifier, and key lifecycle governance events for the signed SOP-template runtime that T-316b builds on.
- `adapter.persistence.SqliteSopTemplateStore` and `app.admin_action_handler` SOP-template mint/modify/revoke integration, with signed-template read verification and idempotent YAML bootstrap.
- JSON Schemas for each YAML category.
- Manifest validation at startup: (a) every rule's `predicate_name` is registered (with a stub returning `INFO` at this phase), (b) every rule has a graded `citation` ∈ {A1, A2, A3, B1, B2, C-with-corroborator}, (c) every catalogue has `maintenance` metadata, (d) every active catalogue's `review_required_after` is in the future.
- Initial population of catalogues from v2.0 KB:
  - ~ 14 origins; ~ 13 markers; ~ 12 bacterial + ~ 13 eukaryotic promoters; RBS / Kozak / terminator / polyA tables; ~ 30+ tags / linkers / proteases.
  - ~ 60+ host strains across all chassis classes.
  - ~ 40+ restriction enzymes + 6 Type IIS + toolkit enzymes + proteases.
  - 122 rule manifests across MR/WR/SR/BR/MS files (stubs returning `INFO`).
  - Twist / IDT / GenScript vendor profiles; IGSC v3 / IBBIS / SecureDNA screening trust policy; institutional policy defaults; export profiles; active risk advisories.
- `app.part_library_service` writes new parts by emitting `PartAdded` events.
- `stale-catalogue-check` CI gate operational.
- `source-grade-citation-check` CI gate operational.

### Exit criteria

1. *Correctness*: every catalogue YAML validates against its JSON Schema; every rule manifest's `predicate_name` is registered.
2. *Completeness*: every part / host / enzyme / rule from v2.0 KB §§ 5–7 and the MS2/VLP-specific rules from § 17 are present.
3. *Scientific validity*: `/scientific-advisor` reviews catalogues against v2.0 KB citation chain; every entry has a graded citation that resolves to v2.0 KB § 18 or a peer-reviewed source.
4. *Performance*: catalogue loading at startup < 2 s.
5. *Maintainability*: catalogues pass `git diff` review; rule-index CLI lists rules by status / citation / last-reviewed.
6. *Safety*: `source-grade-citation-check` and `stale-catalogue-check` both green.

---

## Phase 5 — Validation rule engine (pure DAG over fields × metrics) (✅ COMPLETE LOCALLY)

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Opus (engine) + Sonnet (predicates).
**Inputs:** ARCHITECTURE.md v1.5 § 4.2 (`engine.validation`, `engine.dependencies`), § 4.3 (data flow with `app.validation_orchestrator`), § 4.4 (state machine + safety gates).

### Deliverables

- `engine.dependencies`: DAG construction over `(field, metric)` pairs from rule manifests; affected-rule-and-metric computation on changeset.
- `engine.validation`: **pure** DAG evaluator. Consumes `ValidationContext` (precomputed metrics, threshold profile, derivation environment). HARD / SOFT / INFO severities and `blocks: frozenset[SafetyGate]` per rule. Incremental re-eval.
- `app.validation_orchestrator`: determines required metrics for affected rules, calls biology adapters (or uses cached metric values), packages `ValidationContext`, invokes the pure validator.
- Predicate registry framework with typed Python functions.
- Implemented structural-predicate registry subset with >= 50 predicate names: V001 – V005, V011 – V012, V021 – V025, MR-01 .. MR-06, MR-10, MR-11, MR-17 – MR-19, MR-22, MR-23, MR-29 – MR-35, MR-37 – MR-44, MR-50 – MR-53, WR-01 .. WR-07, WR-11 .. WR-21, BR-01 .. BR-13. Catalogue rule manifests remain `implementation_status: stub` until each rule's curated fixture promotion is explicitly performed; biology-back-end-dependent rules are deferred to Phase 6.
- `engine.sequence_analysis` (NEW — same phase) implementing C3: `find_sites`, `digest`, `compatible_ends`, `rank_directional_cloning_sites`, `design_diagnostic_digest`, `fragment_simulation` — all topology-aware.
- Four safety gates wired into the state machine.
- Validation report renderer (Markdown, JSON).
- Gold fixtures: ≥ 1 triggering + 1 passing construct per implemented rule.

### Exit criteria

1. *Correctness*: every implemented rule passes its (triggering, passing) gold-fixture pair; `engine.sequence_analysis` matches REBASE-derived expectations on a known-good test set.
2. *Completeness*: 100 % of implemented rules have both fixture types.
3. *Scientific validity*: `/scientific-advisor` reviews predicate implementations against v2.0 KB intent.
4. *Performance*: Tier-1 (deterministic-fake) validation of Example A (~ 6 kb) < 5 s; incremental re-eval after single-module change < 1 s.
5. *Maintainability*: 90 % line coverage on `engine/validation`, `engine/dependencies`, `engine/sequence_analysis`; `no-domain-impurity-check` passes.
6. *Safety*: rule overrides recorded in audit log; HARD failures trigger correct safety gate.

---

## Phase 6 — Biology back-end adapters + dependent rules

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Sonnet.
**Inputs:** ARCHITECTURE.md v1.5 § 4.5 (Biology ports), v2.0 KB § 5.5, § 5.6, § 5.7.

### Deliverables

- `adapter.biology.ViennaRnaAdapter` (RnaFolder; pinned ViennaRNA 2.6.x).
- `adapter.biology.SpliceAiAdapter` (SplicePredictor; TensorFlow); HTTP-service fallback adapter.
- `adapter.biology.SignalPAdapter` (SignalPeptidePredictor; SignalP 5.0b or 6.0).
- `adapter.biology.NodererKozakAdapter` (KozakScorer; PWM).
- `adapter.biology.RbsCalcV2Adapter` (TIRPredictor).
- `adapter.biology.CAIAdapter`, `MinMaxAdapter`, `CharmingAdapter`, `AvoidOnlyAdapter` (CodonAlgorithm implementations).
- Each adapter declares `Manifest` with `measured_typical_latency_ms` and `measured_max_latency_ms` (M9 Tier-2 budget).
- Biology-back-end-dependent rules added to the registry: MR-12 (RBS), MR-13 (Kozak), MR-14 (uORF), MR-15 (premature polyA), MR-16 (splice), MR-27 (CpG), MR-28 (signal peptide), V006, V007, V008, V009, V010, V018.
- Deterministic fakes for each adapter (used in upstream tests).

### Exit criteria

1. *Correctness*: every adapter passes its determinism check inside the containerised CI environment.
2. *Completeness*: every biology port has at least one production adapter and a deterministic fake.
3. *Scientific validity*: published high-/low-expression test constructs are correctly scored.
4. *Performance (Tier-2)*: RNA folding on a 1 kb mRNA < 200 ms; SpliceAI on a 5 kb cDNA < 5 s.
5. *Maintainability*: each adapter has a deterministic fake for unit tests in upstream modules.
6. *Safety*: no sequence is sent to external services without explicit user opt-in; adapter configuration hashes recorded in `DerivationEnvironment`.

---

## Phase 7 — Codon optimiser + assembly strategies + overhang optimiser + primer designer

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Opus (assembly + overhang) + Sonnet (primer designer).
**Inputs:** ARCHITECTURE.md v1.5 § 4.2 (`engine.codon`, `engine.assembly`, `engine.overhang`, `engine.primer`), v2.0 KB § 7, Pryor 2020 / Potapov 2018 overhang datasets.

### Deliverables

- `engine.codon` — constraint-aware optimiser accepting `CodingSequenceDesign`. Modes: `CAI` / `MinMax` / `CHARMING` / `avoid_only`. Lexicographic-priority fixed-point with N = 5 cap. Preserves user-marked protected intervals and functional RNA features.
- `engine.assembly` — strategy hierarchy emitting typed `AssemblyPlan` subclasses:
  - `RestrictionLigationStrategy` → `RestrictionLigationPlan`
  - `GibsonLikeStrategy` (NEBuilder HiFi / Gibson / In-Fusion) → `OverlapAssemblyPlan`
  - `TypeIISGoldenGateStrategy` (with concrete kit subclasses: MoClo / Loop / YTK / GreenGate / GoldenBraid / JUMP / MIDAS) → `TypeIISAssemblyPlan`
  - `GatewayStrategy` → `GatewayPlan`
  - `LICStrategy` → `LICPlan`
  - `USERStrategy` → `USERPlan`
  - `IVAStrategy` → `InVivoAssemblyPlan`
  - `YeastTARStrategy` → `YeastTARPlan`
- `engine.overhang` — Golden Gate overhang-set optimiser against Pryor 2020 / Potapov 2018 matrices; regression tests against the 24-fragment and 35-fragment Pryor 2020 benchmarks.
- `engine.primer` — per-strategy primer design accepting `PrimerDesignParameters` (nn_method, salt_model, monovalent_mM, divalent_mM, dntp_mM, target_oligo_uM, modifications, target_product). Sequencing primer designer; diagnostic restriction digest primer designer; off-target scan against full plasmid via `engine.sequence_analysis`.
- `app.assembly_orchestrator` — iterative codon × validator × assembly loop with lexicographic-priority fixed-point convergence (cap N = 5).
- `AssemblyMethodPicker` mapping (objective, host, cargo, library_size, fragment_count, scarless_required) → ranked methods.

### Exit criteria

1. *Correctness*: every strategy passes its golden-file assembly test; overhang optimiser reproduces Pryor 2020 24-fragment benchmark.
2. *Completeness*: every cloning chemistry in REQUIREMENTS § 2 has a working strategy producing the correct typed plan subclass.
3. *Scientific validity*: `/scientific-advisor` reviews strategy implementations against v2.0 KB § 7.
4. *Performance (Tier-1)*: codon optimisation of a 1 kb ORF < 5 s; overhang optimisation for 20 fragments < 60 s.
5. *Maintainability*: 90 % line coverage on `engine/codon`, `engine/assembly`, `engine/overhang`, `engine/primer`.
6. *Safety*: codon optimiser preserves user-marked protected intervals even when other constraints would drive their alteration.

---

## Phase 8 — (superseded by Phase 8a + Phase 8b per v1.2 B2-01; v1.3 H3-04 — legacy prose moved to Appendix A)

The pre-v1.2 Phase 8 (single phase containing design plan + SOP + admin + authorisation + advisory) is **superseded** by the v1.2 split. See **Phase 8a** (pre-screening, non-operational; below) and **Phase 8b** (post-Phase-10, post-Phase-9a, operational; further below). The two-phase split preserves the v1.4 screening-before-SOP safety invariant in execution.

**v1.3 H3-04 cleanup.** The legacy single-phase deliverables + exit-criteria prose has been moved out of the main phase sequence and into **Appendix A — Pre-v1.2 phase history** at the end of this file. Parsers + readers following the v1.3 phase order should never encounter active-looking legacy content in the binding flow.

### Legacy-Pre-v1.2-Phase-8 (placeholder — content in Appendix A)

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Opus (DAG + safety logic) + Sonnet (per-chemistry templates).
**Inputs:** ARCHITECTURE.md v1.5 § 4.2 (`engine.design_plan`, `engine.sop_protocol`, `engine.controls`), § 4.4 (safety gates), v2.0 KB § 14, REQUIREMENTS FR-PROTO-DESIGN-* + FR-PROTO-SOP-*.

### Deliverables

- `engine.design_plan` — `DesignRealisationPlan` generator: assembly route, required inputs, QC checkpoints, expected verification artefacts, institutional-approvals-required list, biosafety classification, reviewer-packet summary. **Always renderable.**
- `engine.sop_protocol` — `SopLinkedProtocol` generator: bound to **administrator-approved** institutional SOP templates; renders only when the user's `UserDeclaration` lies inside an administrator-granted `AuthorisationProfile` (BR-11; FR-AUTH-06 / FR-AUTH-07).
- **`app.admin_action_handler`** (v1.5) — the admin-service-only write path to `AuthorisationStore` and signed SOP-template admin ports. Authenticates `AdminPrincipal` or `DeveloperBootstrapPrincipal`; rejects `UserPrincipal`, `ReviewerPrincipal`, and ordinary post-bootstrap `DeveloperPrincipal` with `PermissionError`. Emits `AdminActionMinted` / `Modified` / `Revoked` events to the immutable audit log. Required CLI / admin-UI commands: `mint-profile`, `modify-profile`, `revoke-profile`, `list-profiles`, `view-auth-audit-log`.
- **`adapter.persistence.SqliteAuthorisationStore`** (v1.2) — backed by `authorisation.sqlite`. Opened **read-only** by engine and User-role processes; writes only via a separate admin-service process under Administrator or Developer credentials. Each `AuthorisationProfile` carries an institutional signature; tampered profiles fail load.
- **`BlockOperationalProtocol` gate** wiring: every compile checks `UserDeclaration` against `AuthorisationProfile`; freshness is verified on every compile (no caching past `valid_until`); failed gate blocks `engine.sop_protocol` but `engine.design_plan` still renders and a structured request is routed to the Administrator's review queue.
- **(v1.5) Active advisory acknowledgement workflow** — `engine.risk_classification` (B3 mitigation) emits a `RiskAdvisoryReport` bound to the design session and construct version by content hash; presentations emit `AdvisoryWarningPresented`; every `caution` / `strong_caution` advisory requires an explicit signed `RiskAdvisoryAcknowledgement` (justification ≥ 20 chars + signature via the v1.4 B9 `DecisionRecord`) before authorisation can proceed; `RiskAdvisoryDeclined` / `RiskAdvisoryEscalated` are first-class governance events; the gate predicate `all_required_advisories_acknowledged()` is consulted before `OperationalProtocolAuthorised` fires; the new CI gate `no-passive-advisory-bypass-check` proves the bypass is statically impossible. UI surfaces (CLI / API / web UI) offer only *acknowledge* / *decline* / *escalate* — no "dismiss without action".
- `engine.controls` — `ControlSet` generator: positive / negative / process / library-specific controls as first-class outputs.
- Protocol DAG renderers: Markdown (human reading), PDF (printable benchwork), JSON (downstream automation).
- Troubleshooting appendix generator: failure mode → design-time predictor → wet-lab remediation.
- Time-and-materials estimator.
- Per-chemistry templates with reagent / quantity / temperature / time / rationale / safety-note / SOP-ref / approval-gate / hazard-class / allowed-roles / checkpoint-criteria fields.

### Exit criteria

1. *Correctness*: `DesignRealisationPlan` for the three white-paper examples renders correctly; `SopLinkedProtocol` renders only when the user's `UserDeclaration` lies inside an admin-granted `AuthorisationProfile`; `ControlSet` includes positive + negative + process controls for every example.
2. *Completeness*: every assembly chemistry has both a design-plan template and an SOP-linked-protocol template; `app.admin_action_handler` exposes mint / modify / revoke / list / view-audit commands.
3. *Scientific validity*: junior-researcher persona dry-run of Example A's `DesignRealisationPlan` produces a clear assembly route + QC checkpoints; the gated `SopLinkedProtocol` is emitted only when the test fixture's user has an Administrator-minted profile covering Example A's tier / host / chemistry.
4. *Performance (Tier-1)*: `DesignRealisationPlan` generation < 2 s per construct; gate validation < 50 ms per compile.
5. *Maintainability*: protocol DAG is JSON-serialisable with canonical key order.
6. *Safety*: gated rendering of `SopLinkedProtocol` enforced; `BlockOperationalProtocol` gate fires when authorisation is incomplete, expired, revoked, or absent; `no-self-authorisation-check` static CI gate passes; runtime test confirms `UserPrincipal` cannot invoke any `AuthorisationStore.write_*` method nor reach `app.admin_action_handler` (PermissionError on every attempt).

---

## Phase 8a — Design plan + controls + advisory data + advisory acknowledgement (pre-screening; v1.2 binding)

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Opus.
**Inputs:** `CODING_AGENDA.md` v1.2 § 2.8a; `ARCHITECTURE.md` v1.5 § 4.2 (`engine.risk_classification`, `engine.design_plan`, `engine.controls`, `engine.vlp_policy`, `app.plugin_governance`, `app.design_plan_orchestrator`, `app.advisory_acknowledgement` presentation surface); v2.0 KB § 14, REQUIREMENTS FR-PROTO-DESIGN-* + UR-11 + FR-ADV-01..05.

### Deliverables

- `engine.risk_classification` (T-801) — `RiskAdvisoryReport` generator, v1.5 fields (`design_session_id`, `construct_checksum`, `report_content_hash`, stable `advisory_id`).
- `engine.design_plan` (T-802) — `DesignRealisationPlan` generator; cannot contain `ProtocolStep`; renderers per `docs/rendering_determinism.md`.
- `engine.controls` (T-804) — `ControlSet` generator.
- `engine.vlp_policy` (T-807) — VLP / AAV / lentivirus policy.
- `app.plugin_governance` (T-808) — plugin manifest verification.
- `app.advisory_acknowledgement` presentation surface (T-806a) — emits `AdvisoryWarningPresented` / `RiskAdvisoryAcknowledged` / `RiskAdvisoryDeclined` / `RiskAdvisoryEscalated`; pure predicate `all_required_advisories_acknowledged()`.
- `app.design_plan_orchestrator` (T-805a) — emits `DraftDesignBundle` (no SOP, no operational clearance); always-renderable pre-screening sharing artefact.

### Exit criteria

1. *Correctness*: `DraftDesignBundle` for the three white-paper examples renders correctly with no `SopLinkedProtocol` reachable.
2. *Completeness*: every assembly chemistry has a design-plan template; advisory presentation surface complete.
3. *Scientific validity*: junior-researcher persona dry-run of Example A's design plan; `/scientific-advisor` sign-off.
4. *Performance (Tier-1)*: `DesignRealisationPlan` generation < 2 s per construct.
5. *Maintainability*: 90% coverage on Phase 8a modules.
6. *Safety*: structural test confirms no operational field reachable in `DraftDesignBundle`; advisory acknowledgement events emit to governance stream; `no-passive-advisory-bypass-check` running in `informational` mode (flips to `enforced` at Phase 8b exit).

---

## Phase 9a — Sequence I/O extensions + SnapGene file-watch (pre-screening; v1.2 binding)

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Sonnet.
**Inputs:** `CODING_AGENDA.md` v1.2 § 2.9a; `ARCHITECTURE.md` v1.5 § 4.5 (`SequenceReader` / `SequenceWriter` / `SnapGeneChannel` / `SnapGeneDnaReader`), REQUIREMENTS UR-01a + FR-IO-*.

### Deliverables

- `adapter.io.EmblAdapter` + `adapter.io.Gff3Adapter` (T-901).
- `adapter.snapgene.SnapGeneFileWatcher` (T-902) — UR-01a MUST channel; imports `SnapGeneDnaReader` from T-308e's namespace (no local `dna_reader.py` per v1.2 H2-04).
- **No final export orchestrator in this phase** — T-903 lives in Phase 9b (v1.2 B2-02).

### Exit criteria

1. *Correctness*: SnapGene file-watch round-trip works on the three white-paper examples (read `.gb` from watched dir → validate → re-emit `.gb` that SnapGene re-imports).
2. *Completeness*: every UR-01a I/O channel implemented.
3. *Scientific validity*: SnapGene reads the platform-emitted GenBank with no annotation loss.
4. *Performance (Tier-1)*: file-watch round-trip latency < 2 s per file.
5. *Maintainability*: 90% coverage on `adapter.io` + `adapter.snapgene.SnapGeneFileWatcher`.
6. *Safety*: no operational artefact emitted from Phase 9a (final ExportBundle is Phase 9b).

---

## Phase 9 — (superseded by Phase 9a + Phase 9b per v1.2 B2-02; v1.3 H3-04 — legacy prose moved to Appendix A)

The pre-v1.2 Phase 9 (single phase containing I/O extensions + SnapGene watcher + final export orchestrator) is **superseded** by the v1.2 split. See **Phase 9a** (pre-screening I/O; above) and **Phase 9b** (post-Phase-8b final export orchestrator; further below). The split fixes the export-before-screening defect (B2-02).

**v1.3 H3-04 cleanup.** Legacy single-phase deliverables + exit-criteria prose moved to **Appendix A — Pre-v1.2 phase history**.

### Legacy-Pre-v1.2-Phase-9 (placeholder — content in Appendix A) — Sequence I/O extensions + project bundle export + SnapGene file-watch round-trip

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Sonnet.
**Inputs:** ARCHITECTURE.md v1.5 § 4.5 (SequenceReader / Writer ports), REQUIREMENTS UR-01a (MUST), FR-IO-*.

### Deliverables

- `adapter.io.EmblAdapter`, `adapter.io.Gff3Adapter`.
- `adapter.snapgene.SnapGeneFileWatcher` — the **UR-01a MUST** automated file-watch channel: user exports GenBank from SnapGene into a watched directory; the platform parses, validates, runs the pipeline, emits an updated GenBank that SnapGene re-imports.
- `app.export_orchestrator` emitting the project bundle ZIP: GenBank + FASTA + SBOL 3.1.x + primer CSV + primer FASTA + `DesignRealisationPlan` Markdown + Markdown + JSON + `SopLinkedProtocol` (if gated unlock) + `ControlSet` + validation report JSON + screening verdict JSON + `DerivationEnvironment` JSON + metadata.
- All four safety gates wired into export: `BlockExport`, `BlockVendorSubmission`.

### Exit criteria

1. *Correctness*: the three white-paper examples produce a complete project bundle ZIP whose every file opens in its intended application; SnapGene file-watch round-trip works end-to-end for all three examples.
2. *Completeness*: every output format in REQUIREMENTS FR-IO-* and UR-01a is implemented.
3. *Scientific validity*: SnapGene reads the platform-emitted GenBank for all three examples with no annotation loss.
4. *Performance (Tier-1)*: bundle export of a 10 kb construct < 5 s.
5. *Maintainability*: 90 % coverage on `adapter/io` and `app/export_orchestrator`.
6. *Safety*: bundle includes screening verdict + `DerivationEnvironment`; metadata includes biosafety classification.

---

## Phase 10 — Synthesis vendor adapters + screening hook with expanded verdicts

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Sonnet.
**Inputs:** ARCHITECTURE.md v1.5 § 4.5, § 4.4 (safety gates); REQUIREMENTS SR-*, BR-*; v2.0 KB §§ 11, 12.

### Deliverables

- `adapter.vendor.TwistAdapter`, `IDTAdapter`, `GenScriptAdapter`. `check`, `auto_partition`, `estimate_cost(*, product_type, scale, cloning_option, currency, quote_date_utc)`.
- `app.screening_orchestrator` + adapters: `adapter.screening.IgscAdapter` (IGSC v3.0), `IbbisAdapter` (Common Mechanism), `SecureDnaAdapter` (blinded queries), `InternalBlacklistAdapter` (canonical=False).
- `ScreeningVerdict` enum fully implemented: `CLEAR` / `WATCHLIST` / `HIT` / `UNAVAILABLE` / `NOT_APPLICABLE` / `MANUAL_REVIEW_REQUIRED`. Fallback adapters never produce `CLEAR`.
- `screen_batch` with typed partial-failure semantics: `list[ScreeningResult | ScreeningError]` of equal length, in input order. Orchestrator never aggregates errors into `CLEAR`.
- Reviewer sign-off workflow for `WATCHLIST` / `MANUAL_REVIEW_REQUIRED`. Automatic block for `HIT` and Select-Agent matches.
- Audit trail of every screening verdict in `audit.sqlite`.
- `BlockVendorSubmission` and `BlockExport` gates triggered correctly per verdict.

### Exit criteria

1. *Correctness*: every vendor constraint in v2.0 KB § 11 is enforced; verdict flows correct.
2. *Completeness*: three vendor profiles + four screening adapters.
3. *Scientific validity*: vendor checks match published vendor specifications; screening fallback never silently produces `CLEAR`.
4. *Performance (Tier-2)*: vendor check on a 5 kb sequence < 500 ms; batch screening of 100 sequences via IGSC HTTP adapter < 60 s.
5. *Maintainability*: vendor profiles are externally editable YAML with maintenance metadata; new adapters addable as plugins.
6. *Safety*: every screening verdict persisted with adapter version, configuration hash, timestamp; audit log immutable.

---

## Phase 8b — SOP rendering + authorisation gate (post-Phase 10; v1.2 binding)

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Opus.
**Inputs:** `CODING_AGENDA.md` v1.2 § 2.8b; `ARCHITECTURE.md` v1.5 § 4.2 (`engine.sop_protocol`, `app.sop_protocol_orchestrator`, `app.authorisation_decision`); REQUIREMENTS FR-PROTO-SOP-*, FR-AUTH-*, FR-ADV-06..07, BR-14, UR-11, R-21.

### Deliverables

- `engine.sop_protocol` (T-803) — gated `SopLinkedProtocol` generator; renderers per `docs/rendering_determinism.md`; SOP-template admin-write operations extending T-311's handler.
- `app.sop_protocol_orchestrator` (T-805b — renamed from T-805 per v1.2 B2-09) — emits `SopProtocolBundle` only after `OperationalProtocolAuthorised`; `SopRendered` to design stream.
- `app.authorisation_decision` (T-806b) — consumes `ScreeningCompleted` (design stream) + acknowledgement chain (governance stream); activates `BlockOperationalProtocol`; home of BR-14 hard-gate predicate (v1.2 H2-11); FR-ADV-07 adversarial UAT with all 9 bypass scenarios (v1.2 M2-02).

### Exit criteria

1. *Correctness*: `SopLinkedProtocol` renders only after observed `OperationalProtocolAuthorised`; `sop-after-gates-check` `enforced` green.
2. *Completeness*: every assembly chemistry has an SOP template; FR-ADV-07 adversarial suite covers all 9 bypass paths.
3. *Scientific validity*: gated SOP for the three white-paper examples is correct.
4. *Performance (Tier-1)*: gate validation < 50 ms per compile.
5. *Maintainability*: 90% coverage on Phase 8b modules.
6. *Safety*: `no-passive-advisory-bypass-check` `enforced` green; `BlockOperationalProtocol` predicate active (T-309 sub-deliverable (b) activation per v1.3 B3-08).

---

## Phase 9b — Final export orchestrator (post-Phase 8b; v1.2 binding)

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Opus.
**Inputs:** `CODING_AGENDA.md` v1.2 § 2.9b; REQUIREMENTS FR-PROTO-*, N6, R-19.

### Deliverables

- `app.export_orchestrator` (T-903) — final `ExportBundle` ZIP; consumes `ScreeningCompleted` + `OperationalProtocolAuthorised` + `SopRendered`; renderer files per `docs/rendering_determinism.md`; activates `BlockExport` predicate (T-309 sub-deliverable (b) activation per v1.3 B3-08).

### Exit criteria

1. *Correctness*: white-paper examples produce a complete project bundle ZIP; every file opens in its intended application.
2. *Completeness*: bundle includes screening verdict + authorisation evidence + SOP + advisory approval trace + `DerivationEnvironment`.
3. *Scientific validity*: SnapGene reads the platform-emitted GenBank.
4. *Performance (Tier-1)*: bundle export of a 10 kb construct < 5 s.
5. *Maintainability*: 90% coverage on `app.export_orchestrator`.
6. *Safety*: `BlockExport` correctly blocks when authorisation absent or screening incomplete; bundle hash byte-deterministic.

---

## Phase 11 — HTTP API + CLI

**Owner:** `/dev-orchestrator` coordinating `/scientific-coder`. **Model tier:** Sonnet.
**Inputs:** ARCHITECTURE.md v1.5 § 4.2 (`interface.cli`, `interface.api`, `interface.admin_service`, `interface.audit_service`); REQUIREMENTS FR-INT-08, FR-PROJ-*.

### Deliverables

- `interface.cli` — Typer-based CLI commands: `new`, `open`, `validate`, `compile`, `screen`, `export`, `library`, `replay`, `audit`, `rule-index`, `list-sessions`. Every command maps 1:1 to an application service.
- `interface.api` — FastAPI HTTP server exposing the same use cases over REST + WebSocket for streaming validation reports and live design updates.
- OpenAPI spec auto-generated and published.
- End-to-end CLI walk-through of white-paper Example A from cold start.

### Exit criteria

1. *Correctness*: every CLI command does what its `--help` says; OpenAPI spec validates.
2. *Completeness*: every application service reachable via CLI and API.
3. *Scientific validity*: Example A from cold start to project bundle ZIP via CLI in < 5 min.
4. *Performance (Tier-1)*: HTTP request latency for validation of a 10 kb construct < 3 s.
5. *Maintainability*: 90 % coverage on `interface/cli` and `interface/api`.
6. *Safety*: API does not expose secrets; auth configurable; opt-in telemetry only.

---

## Phase 12 — Web UI + decision tree + free-text translator + live SnapGene channel

**Owner:** `/dev-orchestrator` coordinating frontend specialist; `/scientific-advisor` reviews UI text. **Model tier:** Sonnet (UI components) + Opus (interaction logic).
**Inputs:** ARCHITECTURE.md v1.5 § 4.2 (`interface.ui`, `app.decision_tree`, `app.constraint_translator`, `adapter.llm`, `adapter.snapgene.SnapGeneApiClient`); REQUIREMENTS UR-01b (SHOULD), UR-02, FR-UI-*.

### Deliverables

- React + TypeScript SPA consuming the HTTP / WebSocket API.
- Decision-tree wizard implementing FR-UI-01 … FR-UI-12.
- `app.constraint_translator` + `adapter.llm` (local-LLM default; OpenAI / Anthropic with explicit opt-in): free-text → structured-constraint proposal → user confirmation → snapshot.
- `adapter.snapgene.SnapGeneApiClient` — **UR-01b SHOULD** live API channel if/when SnapGene Server API is available; falls back to UR-01a (file-watch) otherwise.
- i18n hooks; English-first; Simplified Chinese locale stub.
- In-app help drawn from the white paper (33 diagrams indexed).

### Exit criteria

1. *Correctness*: every UI affordance maps to a tested application-layer use case.
2. *Completeness*: every UR / FR-UI requirement implemented.
3. *Scientific validity*: junior researcher persona completes white-paper Example A in the UI in < 30 min on first use.
4. *Performance*: design map + validation panel update < 500 ms after a single-module change.
5. *Maintainability*: front-end has full type coverage; components storybook-tested.
6. *Safety*: free-text does not leave the user's machine without explicit opt-in; LLM adapter configurable; default local-LLM.

---

## Phase 13 — Acceptance UAT + combinatorial libraries + multi-host workflows + release polish

**Owner:** `/dev-orchestrator` + `/scientific-advisor` (validation). **Model tier:** Sonnet (test fixtures) + Opus (release sign-off).
**Inputs:** REQUIREMENTS AC-01 … AC-07; ARCHITECTURE.md v1.5 § 4.10.

### Deliverables

- End-to-end UAT on the three white-paper worked examples (Example A bacterial enzyme; Example B mammalian mCherry; Example C plant GUS), each executed by independent reviewers in a wet-lab dry-run, **including verification of**:
  - role-keyed host context for plant transient (E. coli cloning + Agrobacterium delivery + *N. benthamiana* target).
  - `DesignRealisationPlan` for each (always-rendered).
  - Gated `SopLinkedProtocol` for each (v1.3 M3-06 corrected wording: rendered only when an administrator-granted `AuthorisationProfile` is **verified-and-current**, an acceptable `ScreeningCompleted` verdict has been observed, and the required `RiskAdvisoryAcknowledged` chain is complete).
  - `ControlSet` for each (positive / negative / process controls).
- Combinatorial library benchmark: 100 promoter × RBS × ORF Golden Gate library designed in < 30 min; overhang scores meet kit threshold.
- MS2/VLP design exercising MS-* rule family (pac-hairpin presence, AB-loop insertion size cap, SCP linker integrity, capsid/cargo separation, replication-function exclusion).
- **Administrator-only end-to-end UAT (v1.3, FR-AUTH-13 / UR-10):** a fixture institution with no Reviewer appointed; the same `AdminPrincipal` (a) mints a User's `AuthorisationProfile`, (b) authors and approves an institutional SOP template, (c) the User compiles a construct that produces a `WATCHLIST` screening verdict, (d) the **same Administrator** signs off on the verdict, (e) the `ReviewerSignedOff` event in the audit log shows `signer_role = Role.ADMINISTRATOR`, (f) the project bundle exports successfully with full audit trail.
- **Reviewer-cannot-escalate UAT (v1.3, FR-AUTH-14):** a `ReviewerPrincipal` attempts each administrator action (mint / modify / revoke profile; author SOP; mutate audit log) and is rejected with `PermissionError`; every attempt is logged as `AuthorisationAttemptDenied`.
- **(v1.5) Active-advisory adversarial UAT (FR-ADV-07, BR-14, R-21):** every known bypass path is attempted and rejected — (a) UI render only (no acknowledgement event); (b) acknowledgement with empty / under-length justification; (c) acknowledgement with invalid / missing signature; (d) acknowledgement whose `construct_checksum` does not match; (e) acknowledgement whose `report_content_hash` does not match; (f) `RiskAdvisoryDeclined` / `RiskAdvisoryEscalated` without the required follow-through; (g) programmatic attempt to construct `OperationalProtocolAuthorised` without observing the acknowledgement chain. Every path produces `BlockOperationalProtocol` + typed audit entry citing the missing advisory IDs.
- **(v1.5) Active-advisory happy-path UAT:** a fixture construct triggers a `strong_caution` advisory; the Administrator explicitly acknowledges with a 60-character justification; the signed `RiskAdvisoryAcknowledged` event is recorded in the governance stream; `all_required_advisories_acknowledged()` returns `(True, frozenset())`; authorisation gate fires `OperationalProtocolAuthorised`; the SOP renders; the exported bundle contains the full approval trace (presentation + acknowledgement + decision record + signature) under the chosen `ExportProfile` redaction policy.
- Stress tests at NFR-PERF Tier-1 + Tier-2 budgets.
- Documentation site finalised: API reference, user guide, white-paper as in-app help, developer guide for adapter plugins, contributors guide for rule manifests and catalogue maintenance metadata.
- Release artefacts: container image, Python wheel, web-UI build, sample project bundles for the three examples.
- Release notes with migration notes.
- Public-facing repository with Apache 2.0 licence.

### Exit criteria

1. *Correctness*: every AC-01 … AC-07 passes.
2. *Completeness*: every MUST-priority FR / NFR / SC / DR delivered.
3. *Scientific validity*: full rule-validation coverage; every rule has both triggering and passing fixtures; **MS-\* family included**; independent expert review by a senior molecular biologist.
4. *Performance*: every NFR-PERF Tier-1 budget met inside the containerised release environment; Tier-2 budgets measured and reported per adapter.
5. *Maintainability*: documentation complete; release engineering documented; all CI gates green.
6. *Safety*: full screening chain verified against IGSC v3.0 test suite; `BlockExport` / `BlockVendorSubmission` / `BlockOperationalProtocol` gates verified end-to-end; **adversarial self-elevation test**: a UserPrincipal attempts (a) to call `AuthorisationStore.write_*` directly, (b) to reach `app.admin_action_handler` via every public API surface, (c) to swap `role_of_operation` mid-session, (d) to declare an SOP library outside the granted profile, (e) to declare a future-dated profile, (f) to tamper with `authorisation.sqlite` on disk and continue compiling — every attempt blocked with `PermissionError` and recorded as `AuthorisationAttemptDenied` in the audit log. Audit log integrity verified.

---

## Stretch / future phases (post-v1.0; planned but not committed)

- **Phase 14** — Multi-user collaborative server.
- **Phase 15** — Direct vendor ordering (Twist / IDT APIs) — conditional on vendor API maturity and explicit user opt-in.
- **Phase 16** — Genome-context features: integration site selection (AAVS1, CCR5, etc.); CRISPR HDR template designer.
- **Phase 17** — Public repository publishing (Addgene-compatible deposit pipeline).
- **Phase 18** — Liquid-handler integration: protocol-DAG export to OpenTrons / Hamilton / Tecan automation languages.

---

## Non-goals (explicitly out of scope)

- Wet-lab data ingestion (sequencing trace QC, gel-image OCR).
- Patent / freedom-to-operate analysis (handed off to `/ip-auditor`).
- Direct cell-line genome-editing campaign management.
- LIMS / inventory management.
- Bypass of institutional biosafety review.

---

## Risk register (inherited from ARCHITECTURE v1.5 § 6)

The 21 residual risks from ARCHITECTURE v1.5 § 6 remain active throughout development. R-13 (catalogue staleness), R-14 (coordinate round-trip), R-15 (multi-host marker conflict misclassification), R-16 (self-elevation), R-17 (LLM unsafe output), R-18 (plugin trust escalation), R-19 (export PII leak), R-20 (unsupported biosafety tier), and R-21 (advisory bypass) have explicit phase-owned mitigations.

---

## Regeneration policy

This document is **derived** from `ARCHITECTURE.md` v1.5 plus `CODING_AGENDA.md` v1.5. Any change to ARCHITECTURE.md requires regenerating `ROADMAP.md`. The regeneration process:

1. `/architect` updates `ARCHITECTURE.md` (with version bump).
2. `/architect` and `/dev-orchestrator` jointly regenerate `ROADMAP.md` from the updated architecture.
3. The diff between old and new ROADMAP.md is reviewed against in-flight work.
4. In-flight phases that change ownership / scope are re-handed-off with updated briefs.

---

*End of binding ROADMAP.md content (Phases 0..13 + Stretch + Non-goals + Risks + Regeneration policy) — derived from `ARCHITECTURE.md` v1.5 + `CODING_AGENDA.md` v1.5.*

---

## Appendix A — Pre-v1.2 phase history (legacy; v1.3 H3-04)

This appendix preserves the pre-v1.2 single-phase descriptions of Phase 8 (Design plan + SOP-linked protocol + controls) and Phase 9 (Sequence I/O extensions + project bundle export + SnapGene file-watch round-trip) as **historical reference**. **These descriptions are no longer binding.** The binding phases are Phase 8a / Phase 8b (per v1.2 B2-01) and Phase 9a / Phase 9b (per v1.2 B2-02).

Parsers + task-board generators following the current v1.5 phase order ignore this appendix. The headings below carry the `Legacy-Pre-v1.2-` prefix so they are parser-distinct from active phases.

### Legacy-Pre-v1.2-Phase-8 — Design plan + SOP-linked protocol + controls (v1.0..v1.1 era)

*Historical narrative only — superseded by Phase 8a + Phase 8b in the binding flow above.*

The pre-v1.2 Phase 8 was a single phase containing: design plan generator, SOP-linked protocol generator, controls generator, admin action handler, authorisation store, advisory acknowledgement workflow, and protocol orchestrator. Deliverables and exit criteria mirrored the v1.5 architecture but did **not** preserve the screening-before-SOP safety invariant (SOP rendering was scheduled before Phase 10 screening). The v1.2 B2-01 split corrected this by moving the SOP and authorisation work to Phase 8b after Phase 10.

### Legacy-Pre-v1.2-Phase-9 — Sequence I/O extensions + project bundle export + SnapGene file-watch round-trip (v1.0..v1.1 era)

*Historical narrative only — superseded by Phase 9a + Phase 9b in the binding flow above.*

The pre-v1.2 Phase 9 was a single phase containing: EMBL + GFF3 adapters, SnapGene file watcher, and the final export orchestrator. Deliverables mirrored the v1.5 architecture, but the final export orchestrator's exit criteria required `ScreeningCompleted` + `OperationalProtocolAuthorised` + `SopRendered` events that did not exist at the pre-v1.2 Phase 9 time (since Phase 10 screening was scheduled after). The v1.2 B2-02 split corrected this by moving the final export orchestrator (T-903) to Phase 9b after Phase 8b.

---

*End of ROADMAP.md v1.5 (regenerated from `ARCHITECTURE.md` v1.5 + `CODING_AGENDA.md` v1.5).*
