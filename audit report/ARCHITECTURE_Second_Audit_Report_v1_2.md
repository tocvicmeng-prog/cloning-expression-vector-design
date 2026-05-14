# Architecture v1.3 Second Audit Report v1.2

Target file: `ARCHITECTURE.md`  
Response reviewed: `audit report/ARCHITECTURE_Audit_Response.md`  
Knowledge base baseline: `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` and project reference corpus in the same project folder  
Excluded file: `MS2_CP_Vector_Design_Handover_Package_v1_0.zip`  
Audit date: 2026-05-13

## Executive Verdict

`ARCHITECTURE.md` v1.3 is materially stronger than the earlier version. It now recognizes sequence/graph primitives, derivation environments, split design-vs-SOP outputs, screening result typing, reviewer/admin authorization, and more realistic state controls.

However, it is not yet implementation-ready as the authoritative architecture. The remaining defects are structural, not merely editorial. The most serious problems are:

1. The architecture claims a safety split between non-operational design plans and gated operational SOPs, but the requirements file still contains old full wet-lab protocol requirements and wet-lab execution acceptance criteria.
2. The pipeline can still generate a `SopLinkedProtocol` before sequence screening is complete.
3. The v1.3 administrator model weakens separation of duties and conflicts with dual sign-off expectations for high-risk workflows.
4. Sequence import/export contracts lose feature-table and construct-graph information, undermining GenBank/SBOL/SnapGene round-trip claims.
5. Authorization, screening, derivation, and audit models are not yet strong enough for regulated or institutionally governed molecular-biology workflows.

Recommendation: **conditional no-go** for implementation beyond scaffolding until a v1.4 or v1.3.1 architecture patch repairs the blocking issues below.

## Improvements Confirmed

The revised architecture correctly improves several previously weak areas:

- It separates `DesignRealisationPlan` from `SopLinkedProtocol`.
- It introduces typed sequence primitives, features, locations, insertion contexts, construct graphs, and derivation environments.
- It recognizes that validation should be pure and deterministic, with adapter-derived metrics computed outside the rule engine.
- It introduces first-class controls, assembly plans, screening outcomes, event types, and export/vendor gates.
- It adds administrator-controlled authorization profiles rather than allowing ordinary users to self-authorize operational SOPs.
- It narrows LLM use to advisory text and explicitly excludes sequence-level design authority.

These are substantial corrections. The audit below focuses on remaining faults.

## Blocking Findings

### B1. Requirements Still Contradict the Architecture's Safety Split

The architecture and audit response state that operational protocol generation has been split into:

- a non-operational `DesignRealisationPlan`, always available after compile; and
- a gated `SopLinkedProtocol`, available only after authorization, screening, and export controls.

The project requirements do not consistently reflect this split. Several requirements and acceptance criteria still call for a full, directly executable wet-lab protocol, including operational steps, reagent quantities, incubation conditions, transformation conditions, clone screening, expression induction, purification, cell staining, and wet-lab execution outcomes.

This creates a direct governance contradiction:

- The architecture says the system should not provide operational protocol details unless authorization gates pass.
- The requirements still require the system to generate and validate operational wet-lab protocols as a baseline output.

Impact:

- Implementers cannot know which document is binding.
- Test writers may encode unsafe or policy-inconsistent behavior.
- A product manager could truthfully claim the architecture prohibits an output while the requirements demand it.

Required correction:

- Update `REQUIREMENTS.md`, acceptance criteria, roadmap, and traceability appendices to use the same output split:
  - `DesignRealisationPlan`: non-operational, deterministic, safe-to-render design artifact.
  - `SopLinkedProtocol`: institution-specific operational protocol, rendered only after explicit authorization and all safety gates.
- Remove or reclassify acceptance criteria that require wet-lab execution success as a software release criterion.

### B2. SOP Generation Occurs Before Screening in the Data Flow

The inter-module data flow still shows compile producing:

- `engine.design_plan`
- `engine.controls`
- `engine.sop_protocol?`

before sequence screening occurs. Screening is shown after compile. This means the system may render or at least construct an operational SOP before the screening verdict is known.

That contradicts the stated safety model. Screening must be an upstream precondition for operational SOP rendering/export, not a downstream decoration.

Impact:

- A high-risk sequence could produce operational instructions before `HIT`, `WATCHLIST`, `UNAVAILABLE`, or `MANUAL_REVIEW_REQUIRED` gates apply.
- Even if export is later blocked, local logs, previews, caches, UI state, or plugin outputs may expose operational details.
- The state machine becomes ambiguous because `Compiled` can contain state that should not exist until after screening.

Required correction:

- Compile should produce only non-operational artifacts:
  - construct graph
  - validation report
  - design realization plan
  - controls plan
  - screening request package
- Screening and authorization must complete before `SopLinkedProtocol` is rendered.
- The event model should separate:
  - `DesignCompiled`
  - `ScreeningCompleted`
  - `OperationalProtocolAuthorized`
  - `SopRendered`
  - `Exported`

### B3. Administrator-Only Completion Undermines Dual Sign-Off and Separation of Duties

v1.3 states that an Administrator is a superset of Reviewer and that an institution may complete a workflow with Administrator alone. This is operationally convenient but unsafe as a general architecture rule.

The wider reference corpus still expects stronger governance for high-risk cases, including dual sign-off for replication-competent viral systems and higher biosafety workflows. The architecture does not enforce:

- two-person review;
- conflict-of-interest separation;
- separation between the person minting an authorization profile and the person signing off a watchlist/manual-review case;
- separate institutional biosafety officer or PI approval roles;
- policy-specific escalation for RG2+, viral vector, toxin, oncogene, or regulated cargo scenarios.

Impact:

- A single administrator can mint authority, sign off screening exceptions, render SOPs, and export bundles.
- This collapses authorization, review, and release into one actor.
- The architecture cannot credibly claim compliance readiness for higher-risk molecular-biology workflows.

Required correction:

- Keep `Administrator.can_act_as(Reviewer)` only for low-risk institutional deployments.
- Add policy-controlled dual-control requirements:
  - `requires_independent_reviewer`
  - `requires_biosafety_officer`
  - `requires_second_admin`
  - `requires_signed_institutional_approval`
- Disallow the same principal from both minting the relevant authorization profile and approving an exception unless policy explicitly permits it.

### B4. Authorization Coverage Is Biologically Under-Scoped

`AuthorisationProfile` covers role, host classes, biosafety tiers, assembly chemistries, downstream uses, and SOP libraries. This is not enough to authorize real molecular-biology work.

Missing authorization dimensions include:

- cargo risk classes, such as toxin, virulence factor, oncogene, cytokine, immune modulator, antibiotic resistance marker, selectable marker, reporter, and regulatory element;
- vector system classes, such as plasmid, integrating viral, non-integrating viral, transposon, phagemid, VLP, minicircle, BAC/YAC, or Agrobacterium binary vector;
- replication competence and helper-function status;
- insert size and copy-number constraints;
- host role, not just host class;
- screening verdict class and exception authority;
- target organism or cell-line restrictions;
- institutional protocol IDs and approval scope;
- jurisdictional or vendor-policy constraints;
- component lineage and provenance trust.

Impact:

- A user could be authorized for "mammalian cell culture" and "BSL2" but not actually authorized for a lentiviral oncogene construct, an AAV helper plasmid, a toxin fragment, or a construct with a restricted marker.
- SOP rendering may be authorized by overly broad categories.

Required correction:

- Add a `CoveredBiologicalScope` or equivalent policy object covering vector class, cargo class, host role, biosafety class, regulated sequence class, downstream use, and approval references.
- Make authorization decisions artifact-specific and traceable:
  - `authorisation_profile_id`
  - `profile_content_hash`
  - `institutional_approval_id`
  - `decision_id`
  - `decision_timestamp`
  - `decision_policy_version`

### B5. Sequence I/O Contracts Lose the Annotations Needed by the Architecture

The plugin contracts define:

- `SequenceReader.read(...) -> SequenceRecord`
- `SequenceWriter.write(record: SequenceRecord, format: SequenceFormat) -> bytes`

But `SequenceRecord` is essentially sequence plus metadata. It does not carry the full feature table, construct graph, SBOL component graph, primer annotations, topology-specific feature locations, SnapGene visual metadata, or structured qualifier information.

This contradicts the architecture's own goals:

- GenBank round-trip;
- SBOL round-trip;
- SnapGene round-trip;
- no silent annotation loss;
- construct graph and feature preservation;
- deterministic export.

Impact:

- The importer can parse annotations but has nowhere to put them.
- The exporter cannot reconstruct the original annotated file.
- The architecture cannot meet its own round-trip acceptance tests.

Required correction:

- Replace the I/O contracts with an annotated construct object:
  - `SequenceReader.read(...) -> ImportedConstruct`
  - `SequenceWriter.write(construct: AnnotatedConstruct, format: SequenceFormat) -> bytes`
- `ImportedConstruct` should include:
  - raw sequence;
  - topology;
  - feature table;
  - structured qualifiers;
  - source format metadata;
  - construct graph;
  - SBOL mapping;
  - warnings for lossy conversions.
- Byte-identical round-trip should not be required for GenBank/SBOL except where a format-specific canonical writer makes that realistic. Semantic equivalence should be the primary test.

### B6. The Feature Model Is Too Weak for GenBank, SBOL, and SnapGene

The architecture defines `Feature.qualifiers: dict[str, str]`. This is not sufficient.

Real feature annotations require:

- repeated qualifiers with the same key;
- ordered qualifiers;
- structured values;
- evidence fields;
- database cross-references;
- translations;
- codon-start metadata;
- notes from different namespaces;
- display colors and labels;
- ontology terms;
- fuzzy locations;
- joined locations;
- complemented locations;
- nested and compound features.

Impact:

- Important annotations will be flattened or overwritten.
- SBOL roles and GenBank qualifiers cannot be represented faithfully.
- SnapGene-style display information may be lost.

Required correction:

- Replace `dict[str, str]` with a structured qualifier model, for example:
  - `tuple[Qualifier, ...]`
  - `Qualifier(namespace, key, value, value_type, order, provenance)`
- Add explicit support for compound and fuzzy locations.

### B7. Domain Purity Is Still Violated by Adapter-Named Dependencies

The architecture says the domain core and engines should be pure and that validation should not depend directly on adapters. But module dependencies include entries such as:

- `engine.sequence_analysis` depending on `adapter.catalogue.EnzymeCatalogue`
- other engines depending on adapter-namespaced catalogue contracts

This mixes domain service logic with infrastructure naming. A catalogue port is acceptable; an adapter module dependency is not.

Impact:

- The architecture weakens testability and deterministic replay.
- It invites direct infrastructure imports into domain services.
- The "pure domain" claim becomes hard to enforce.

Required correction:

- Move port interfaces into `domain.ports` or `app.ports`.
- Make implementations live under `adapter.*`.
- Enforce with import-linter rules:
  - domain and engine modules may import `domain.*` and `domain.ports.*`;
  - domain and engine modules may not import `adapter.*`.

### B8. Authorization Store Type Model Is Inconsistent

The permissions matrix says a Developer can bootstrap or mint administrator authorization, while the `AuthorisationStore` write methods accept only `AdminPrincipal`.

The model also uses `DomainEvent.actor: UserId`, but admin and reviewer events are not ordinary user actions. `AdminActionMinted`, `AdminActionModified`, and `AdminActionRevoked` appear as domain events even though they are global governance events rather than session-bound design events.

Impact:

- The type signatures do not match the permissions model.
- Admin actions may be incorrectly tied to a design session.
- Developer bootstrap has no clear type-safe path.
- Event audit trails may confuse design provenance with governance administration.

Required correction:

- Separate principal identity from ordinary user identity:
  - `PrincipalId`
  - `UserPrincipal`
  - `ReviewerPrincipal`
  - `AdministratorPrincipal`
  - `DeveloperPrincipal`
- Split events:
  - design-session events;
  - governance/admin audit events.
- Split authorization ports:
  - `AuthorisationReadPort`
  - `AuthorisationAdminWritePort`
  - `AuthorisationBootstrapPort`

### B9. Reviewer/Admin Sign-Off Is Not Cryptographically or Semantically Bound

`ReviewerSignedOff` includes `signer_id` and `signer_role`, but the invariant is not strong enough. The event must prove that the signer actually held the role at the time of signing, under the correct policy and profile version.

Impact:

- A malformed or malicious event could claim `signer_role=Administrator` for a principal that does not have that role.
- Historical replay may be wrong after role revocation.
- The system cannot prove who was authorized to approve what at decision time.

Required correction:

- Add a signed decision record:
  - `principal_id`
  - `role_asserted`
  - `authorization_profile_id`
  - `profile_content_hash`
  - `policy_version`
  - `decision_scope_hash`
  - `signature`
  - `timestamp`
  - `key_id`
- Store role snapshots or immutable profile versions for replay.

### B10. Screening Trust Model Is Too Weak

`ScreeningAdapter.canonical: bool` lets an adapter claim canonical status. Trust should not be self-declared by a plugin.

Also, `NOT_APPLICABLE` can become a loophole unless policy defines when screening is genuinely not applicable. The knowledge base recognizes thresholds and screening contexts, but the architecture must still screen full assembled constructs and must not let short-fragment exemptions hide assembled risk.

Impact:

- A plugin can present itself as canonical without registry approval.
- Screening can be skipped through adapter or sequence-scope ambiguity.
- Vendor screening, internal screening, and advisory screening may be conflated.

Required correction:

- Move adapter trust into an institution-controlled registry:
  - `ScreeningProviderTrustPolicy`
  - `provider_id`
  - `provider_type`
  - `approved_use`
  - `canonical_for`
  - `policy_version`
- Require screening at the assembled-product level, not only at individual fragment level.
- Make `NOT_APPLICABLE` require a policy reason code and audit trail.

### B11. Derivation Environment Is Not Complete Enough for Deterministic Replay

`DerivationEnvironment` includes useful fields such as code version, rule set versions, catalogue snapshots, tool versions, external database versions, user overrides, and reviewer decisions. It still lacks several replay-critical items:

- authorization profile IDs and content hashes;
- SOP template content hashes, not just versions;
- screening provider trust policy version;
- screening query scope and threshold policy;
- exact assembled sequence submitted to screening;
- plugin package hashes;
- LLM prompt template versions and model identifiers if LLM text is included;
- institutional policy version;
- user declaration hash;
- export profile and redaction policy.

Impact:

- Two runs with the same visible inputs can produce different authorization or SOP results.
- Audit replay may fail after templates, plugins, or authorization profiles are updated.
- Exported bundles may not prove what policy state was used.

Required correction:

- Treat all governance, template, plugin, screening, and authorization inputs as derivation inputs.
- Add privacy classification so PII-bearing user overrides and reviewer notes are not blindly embedded in export bundles.

### B12. The State Machine Does Not Fully Specify Paths After Watchlist or Manual Review

The state machine introduces screening states and blocked states, but the transitions after reviewer/admin sign-off remain underspecified. It is unclear exactly how a `WATCHLIST`, `UNAVAILABLE`, or `MANUAL_REVIEW_REQUIRED` case moves to export, and which gates remain blocked after sign-off.

Impact:

- Implementations may diverge.
- Export may be allowed after inadequate sign-off.
- Manual-review cases could either dead-end or pass inconsistently.

Required correction:

- Define explicit transitions:
  - `ScreeningWatchlist -> AwaitingReview -> ReviewSignedOff -> ExportEligible`
  - `ScreeningUnavailable -> AwaitingReview -> ExportEligible` only if policy permits
  - `ManualReviewRequired -> AwaitingReview -> ExportEligible` only with required decision type
  - `ScreeningHit -> Blocked` with no ordinary override unless separately governed
- Bind each transition to an authorization policy.

## Major Findings

### M1. `SynthesisVendorAdapter.check` Is Still Under-Specified

The vendor check receives only a `Sequence`. Real vendor acceptance depends on:

- product type;
- synthesis vs cloning vs plasmid prep;
- scale;
- vector backbone;
- delivery format;
- host strain;
- hazardous sequence screening;
- IP/vendor restrictions;
- turnaround time;
- regional rules;
- customer account permissions.

The cost method was broadened, but `check(sequence)` remains too narrow.

Required correction:

- Replace with `check(request: VendorFeasibilityRequest)`.

### M2. `SequenceRecord.checksum` and Graph Hashing Are Ambiguous

The architecture says graph checksum binds nodes and edges, but the visible checksum definition is sequence-centric. Circular canonicalization by lexicographic minimum rotation is not enough for all biological use cases, especially where reverse-complement equivalence, feature orientation, and repeated sequences matter.

Required correction:

- Separate hashes:
  - `sequence_hash`
  - `topology_hash`
  - `annotation_hash`
  - `construct_graph_hash`
  - `export_bundle_hash`
- Define whether reverse complement is equivalent or distinct for each artifact type.

### M3. Location Semantics Are Incomplete

`Location` includes start, end, strand, circular wrap, and sub-locations. That is not enough for robust file exchange and sequence reasoning.

Missing details include:

- whether circular wrapped features have `end < start` or use split sub-locations;
- fuzzy bounds;
- between-base locations;
- join vs order;
- complement semantics for compound locations;
- remote locations;
- partial features;
- sequence-length invariant.

Required correction:

- Adopt a formal location algebra and map it explicitly to GenBank and SBOL.

### M4. Construct and Feature Duplication Is Not Governed

The model contains `Construct.feature_table` and also graph nodes/edges that can represent features. It is not clear which is authoritative or how divergence is prevented.

Required correction:

- Define one source of truth.
- If both are retained, define a synchronizing invariant and validation rule.

### M5. Host Compatibility Is Too Coarse

`Part.host_compatibility: HostClass` is too broad for real design. Compatibility depends on host role and context:

- propagation vs expression vs screening vs delivery;
- promoter recognition;
- codon usage;
- origin of replication;
- selectable marker;
- toxicity;
- secretion/localization;
- intron/splicing behavior;
- methylation sensitivity;
- copy number;
- transformation/transfection modality.

Required correction:

- Model compatibility as contextual constraints, not as a single host class field.

### M6. Role of Operation Is Conflated With Security Role

The architecture lets a user declare `role_of_operation: Role`, while `Role` is also used for security identities such as Administrator and Reviewer. This is risky and semantically confusing.

Impact:

- A normal user might appear to declare an administrator role.
- Operational role and authorization role become mixed in policy evaluation.

Required correction:

- Separate:
  - `SecurityRole`: Developer, Administrator, Reviewer, User.
  - `OperationalRole`: propagation, expression, producer, target, screening assay, storage, delivery.

### M7. BSL/Hazard Scope Is Not Fully Aligned

The architecture includes BSL1, BSL2, BSL2-plus, and BSL3 in several places. The knowledge base discusses broader biosafety concepts, and some earlier requirements mention specific supported tiers. The architecture needs an explicit non-support rule for out-of-scope tiers such as BSL4 rather than leaving the omission implicit.

Required correction:

- Add explicit unsupported-tier behavior:
  - hard block;
  - no SOP rendering;
  - no vendor submission;
  - audit event;
  - user-facing reason.

### M8. Roadmap Acceptance Criteria Still Overclaim Wet-Lab Validity

Some acceptance criteria still imply successful wet-lab execution or byte-identical format round-trip as a general requirement. Software architecture can validate consistency, traceability, and deterministic output, but it cannot guarantee wet-lab success without empirical validation.

Required correction:

- Replace wet-lab success acceptance criteria with:
  - expert review;
  - in silico checks;
  - dry-run execution by trained users;
  - optional validation studies outside ordinary CI.

### M9. MS2 and VLP Rules Remain Too High-Level

The architecture mentions MS2 specificity and safety rules, but the model does not yet specify enough constraints to prevent unsafe or biologically invalid VLP designs.

Potential gaps include:

- packaging signal handling;
- capsid expression context;
- helper-function separation;
- cargo-size limits;
- replication/infectivity boundaries;
- assembly controls;
- assay controls;
- distinction between RNA-binding display systems, bacteriophage-derived VLPs, and mammalian viral vectors.

Required correction:

- Add an MS2/VLP design policy module with explicit constraints, non-support boundaries, and required controls.

### M10. LLM Governance Is Incomplete

The architecture states that LLM suggestions are advisory only. That is necessary but incomplete.

Missing controls include:

- prompt template versioning;
- model/version tracking;
- citation checking;
- prohibited output detection for operational protocol details;
- red-team tests for unsafe sequence/protocol generation;
- deterministic fallback when LLM is unavailable;
- separation between LLM text and authoritative computed data.

Required correction:

- Add an `AdvisoryTextPolicy` and test suite.
- Treat all LLM output as untrusted content until passed through policy filters.

### M11. `ProtocolStep` Still Carries Operational Parameters

The domain model still includes `ProtocolStep` with fields such as quantities, temperature, and duration. This is acceptable only inside gated SOP artifacts. It is not safe if reused by design-plan artifacts or exposed through ordinary compile events.

Required correction:

- Place operational protocol types in a gated SOP namespace.
- Ensure `DesignRealisationPlan` cannot contain `ProtocolStep` or any operational fields by type.

### M12. Admin Audit and Event Sourcing Are Mixed

Admin profile changes are governance events, not ordinary construct design events. The architecture currently risks mixing them with session-based domain events.

Required correction:

- Use separate append-only streams:
  - design event stream;
  - governance audit stream;
  - export/vendor event stream.
- Link them by immutable decision IDs and content hashes.

### M13. The Response Document Overstates Resolution

The audit response claims broad acceptance and correction of prior issues. Some corrections are present in `ARCHITECTURE.md`, but several are not reflected in the requirements, roadmap, state machine, or contracts. The response also has internal tally inconsistency: it states one count near the top and a different total acceptance count later.

Required correction:

- Treat the response document as an intent log, not proof of implementation.
- Add a traceability table that maps each accepted finding to exact changed files, sections, and tests.

## Moderate Findings

### N1. Architecture Version Labels Are Inconsistent

The document status says v1.3, but some headings or footer text still refer to v1.1. This is not a scientific issue, but it weakens traceability.

Required correction:

- Normalize all version labels and footer text.

### N2. Architecture References Requirement IDs That Do Not Exist

The architecture appendix references split requirement IDs such as `UR-08a`, `UR-08b`, `FR-PROTO-DESIGN`, and `FR-PROTO-SOP`. Those IDs are not consistently present in the actual requirements file.

Required correction:

- Either add those IDs to `REQUIREMENTS.md` or remove them from architecture traceability.

### N3. SBOL Language Appears Mixed Across Versions

Some requirements still use terminology such as `ComponentDefinition`, which belongs to SBOL 2, while the architecture claims SBOL 3 support.

Required correction:

- Define the SBOL target version precisely.
- Maintain a migration map for SBOL 2 imports if required.

### N4. Protocol DAG Canonicalization Is Underdefined

The protocol DAG uses dictionary-like successor structures. Deterministic replay requires stable ordering, canonical node IDs, and cycle detection.

Required correction:

- Define canonical serialization and topological ordering rules.

### N5. `ScreeningError` Is Used but Not Modeled

The screening batch interface returns `ScreeningResult | ScreeningError`, but `ScreeningError` is not specified as a durable domain type.

Required correction:

- Define error categories:
  - transient provider failure;
  - invalid query;
  - unsupported sequence;
  - ambiguous result;
  - policy failure;
  - provider unavailable.

### N6. Export Redaction Policy Is Missing

Export bundles may include derivation environments, user overrides, reviewer decisions, and authorization decisions. Some of those may contain personal, institutional, or sensitive security information.

Required correction:

- Add export profiles:
  - internal audit bundle;
  - collaborator bundle;
  - vendor bundle;
  - publication/supplement bundle.
- Define redaction rules for each.

### N7. Plugin Security Is Under-Specified

The architecture relies heavily on plugins and adapters. It does not yet define sandboxing, signature verification, package pinning, permission scopes, or denial of network access for deterministic paths.

Required correction:

- Add plugin manifest signing and permission declarations.
- Hash plugin artifacts into `DerivationEnvironment`.

### N8. Scientific Controls Are Present but Not Yet Mechanistically Validated

Controls are first-class, but the architecture does not yet specify enough mechanistic validation:

- positive control suitability;
- negative control absence of signal;
- vehicle/mock controls;
- expression vs assembly controls;
- screening assay controls;
- host-specific compatibility;
- replicate structure.

Required correction:

- Add control validation rules tied to design intent and host role.

## Cross-Document Consistency Table

| Area | Architecture v1.3 claim | Current consistency problem | Severity |
|---|---|---:|---:|
| Protocol safety split | Non-operational design plan plus gated SOP | Requirements and acceptance criteria still demand full operational wet-lab protocol generation | Blocking |
| Screening order | Gates protect SOP/export/vendor actions | Data flow can produce `SopLinkedProtocol` before screening | Blocking |
| Admin capability | Admin may act as reviewer and complete workflow alone | Conflicts with dual sign-off and independent review expectations for high-risk cases | Blocking |
| Authorization scope | Profiles authorize SOP rendering | Scope lacks component/cargo/vector/regulatory dimensions | Blocking |
| Sequence I/O | GenBank/SBOL/SnapGene round-trip | I/O signatures only move `SequenceRecord`; annotations and graph are lost | Blocking |
| SBOL support | SBOL 3 target | Some requirements still use SBOL 2 terminology | Moderate |
| Determinism | Same input plus derivation environment gives identical output | Authorization, screening trust, plugin hashes, SOP hashes, and policy hashes are incomplete | Blocking |
| Audit response | Prior findings accepted | Not all accepted changes are reflected across all documents | Major |

## Scientific Authenticity Assessment

The architecture is scientifically more authentic than the prior version, but it still abstracts away several wet-lab realities that matter for correctness:

- Host context is not merely organism class; it is role-specific and workflow-specific.
- Sequence annotations are not optional metadata; they are essential for interpreting parts, CDSs, promoters, origins, markers, linkers, tags, and regulatory features.
- Screening applies to assembled products and workflow intent, not just isolated input fragments.
- Operational SOP authorization must account for cargo, vector system, biosafety, institutional approval, user role, and downstream use.
- Wet-lab success cannot be inferred from architecture correctness. It requires empirical validation, quality of materials, host state, assay conditions, and operator execution.

## Practical Implementability Assessment

The revised architecture is implementable as a software system only after contract repairs. The current version would cause implementation ambiguity in these areas:

- whether to follow architecture or requirements for protocol output;
- when to render operational SOPs;
- how to import/export annotated biological files without annotation loss;
- how to enforce authorization in code;
- how to replay authorization and screening decisions deterministically;
- how to test wet-lab claims in CI;
- how to prevent plugin or adapter trust escalation.

The implementation should not proceed by coding around these ambiguities. The architecture should be amended first.

## Methodological Incapacity and Knowledge Gaps

The main methodological gap is that the architecture sometimes treats governance, wet-lab feasibility, sequence screening, and file-format fidelity as ordinary software features. They need stronger formal models.

Specific gaps:

1. No formal policy model for institutional approvals, biosafety committees, regulated components, or jurisdictional restrictions.
2. No threat model for plugins, LLM output, vendor adapters, or authorization-profile manipulation.
3. No formal biological annotation model sufficient for GenBank, SBOL, and SnapGene equivalence.
4. No decision-theoretic model for screening uncertainty, provider failure, or manual review.
5. No empirical validation boundary separating software correctness from wet-lab success.
6. No key-management and signature lifecycle model for administrator and reviewer decisions.
7. No clear conflict-of-interest model for administrator-only workflows.
8. No complete provenance hash model for templates, plugins, authorization profiles, and screening policies.

## Required Corrections Before Implementation

The next architecture revision should make the following changes before full implementation:

1. Update `REQUIREMENTS.md` to match the design-plan/SOP split.
2. Move SOP rendering after screening and authorization in the pipeline.
3. Add dual-control policy support for high-risk workflows.
4. Expand authorization scope to include cargo, vector class, component risk, screening result, approval IDs, and downstream use.
5. Replace sequence I/O contracts with annotated construct I/O contracts.
6. Replace simple feature qualifiers with structured qualifiers and formal location algebra.
7. Split authorization read/write/bootstrap ports.
8. Split security roles from operational host/workflow roles.
9. Add signed, immutable authorization and review decision records.
10. Move adapter trust into institution-controlled registries.
11. Complete `DerivationEnvironment` with authorization, plugin, SOP, screening, and policy hashes.
12. Replace byte-identical GenBank/SBOL round-trip criteria with semantic equivalence unless canonical writer conditions are defined.
13. Add plugin, LLM, and export redaction threat models.
14. Normalize architecture version labels and requirement traceability.

## Final Audit Conclusion

`ARCHITECTURE.md` v1.3 is a strong recovery draft, but it is not yet a safe or coherent implementation contract. The largest unresolved problem is cross-document inconsistency: the architecture says one thing about gated operational biology, while the requirements and some roadmap criteria still demand direct wet-lab protocol generation and wet-lab execution outcomes.

The second largest problem is sequencing: operational SOP rendering must not occur until screening and authorization have completed. The third is governance: administrator convenience must not erase independent review where biological risk requires it.

Final decision: **do not treat v1.3 as final.** Use it as the basis for a targeted v1.4 patch focused on safety ordering, authorization scope, sequence annotation fidelity, and requirements traceability.
