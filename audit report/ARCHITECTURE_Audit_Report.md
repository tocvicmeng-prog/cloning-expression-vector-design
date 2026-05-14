# Audit Report on ARCHITECTURE.md

**Target:** `ARCHITECTURE.md`  
**Project:** Universal Cloning and Expression Vector Design Platform  
**Audit date:** 2026-05-13  
**Auditor stance:** senior molecular-biology scientist plus senior software-architecture reviewer  
**Source corpus reviewed:** `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md`, `Cloning_Expression_Vector_Design_White_Paper.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `README.md`, `Cloning_KB_v2_Audit_Report.md`, and the historical `Cloning_and_Expression_Vector_Design_Knowledge_Base_v1_0.md`. The zip archive explicitly excluded by the user was not read.

---

## 1. Executive Verdict

`ARCHITECTURE.md` is scientifically well motivated and directionally strong. Its central decisions are appropriate for this domain: typed biological parts, host-aware compatibility, method-specific assembly strategies, SBOL/GenBank interoperability, provenance, sequence-screening hooks, and a dependency-aware validation engine. The document clearly absorbed the v2.0 knowledge base rather than treating vector design as generic sequence editing.

However, the architecture is **not yet implementation-ready as an authoritative final blueprint**. Several claims in the narrative are stronger than the concrete schema and module catalogue can support. The most important defects are:

1. The protocol-generation scope conflicts with the knowledge-base safety scope and with realistic institutional biosafety control.
2. The data model is too sequence-thin and graph-thin to support circular plasmids, reverse-strand features, multi-host workflows, SBOL 3 round-trip, viral/vector-border structures, and combinatorial libraries robustly.
3. Core molecular-cloning functions required by `REQUIREMENTS.md` do not have explicit architecture modules, especially restriction-site analysis, sticky-end compatibility, unique-site ranking, diagnostic digest design, and enzyme-buffer/methylation compatibility.
4. The validation DAG is conceptually correct but underspecified for rules that call external predictors, invalidate prior derived results, or depend on host/context-specific thresholds.
5. The host model is too simple for plant, viral-vector, VLP, shuttle-vector, and producer-cell workflows.
6. The provenance and determinism scheme omits several inputs that materially change outputs.

**Recommendation:** approve the conceptual direction, but require a corrective `ARCHITECTURE.md` v1.1 before Phase 2 becomes code. The highest-risk corrections should be made before scaffolding so the public APIs do not harden around an insufficient domain model.

---

## 2. What the Architecture Gets Right

### 2.1 Scientific authenticity

The architecture correctly uses the v2.0 KB hierarchy: propagation, assembly, expression control, cargo, termination/metadata, validation, and provenance. It preserves the key design rule from the knowledge base: select the vector architecture from objective, host, cargo, and safety tier before choosing assembly chemistry.

It also correctly treats these as first-class biological variables:

- Host and replicon compatibility.
- Promoter and host-class compatibility.
- RBS/Kozak and local 5-prime context.
- Codon optimization as a constrained biological design problem, not a cosmetic transformation.
- Golden Gate overhang choice as a data-driven optimization using Potapov/Pryor-style fidelity data.
- Screening and biosafety as a hook to external or institutional systems, not as an internal verdict invented by the design software.
- SBOL/GenBank/FASTA output and controlled-vocabulary feature annotation.

### 2.2 Technical direction

The modular monolith with ports-and-adapters is a good fit. It avoids premature distributed-system complexity while still isolating external predictors, synthesis vendors, file formats, screening services, and LLM translation. Python is also defensible for the first implementation because Biopython, primer3 bindings, pySBOL3-style tooling, ViennaRNA bindings, and scientific scripting are central to the project.

The architecture also makes several mature engineering choices:

- CLI/API/UI separation.
- Declarative catalogue files for review by domain experts.
- Event-sourced sessions with replay and snapshots.
- Deterministic fakes for integration tests.
- Rule-validation coverage using known-good and known-broken constructs.
- Explicit residual risk register.

These are strong foundations.

---

## 3. Critical Findings

### C1. Safety and protocol-generation scope conflict

**Finding:** The architecture accepts a full wet-lab `ProtocolGenerator` as a first-class output with steps, reagents, quantities, temperatures, durations, host extensions, and downstream workflows. This follows `REQUIREMENTS.md` and `ROADMAP.md`, but it conflicts with the safety scope declared in both knowledge-base versions, which explicitly limit the material to conceptual vector-design guidance and exclude step-by-step wet-lab protocols, transformation procedures, viral-production parameters, and operational dual-use guidance.

**Why this matters:** The project cannot simultaneously claim a non-operational safety scope and require the software to generate executable protocols for transformation, mammalian transfection, plant agroinfiltration, AAV/lentiviral workflows, and VLP/phage-adjacent designs. This is not just a documentation inconsistency. It affects product policy, institutional review, liability, role-based access, and the shape of the domain model.

**Practical risk:** A junior user may treat the generated protocol as an approved SOP. That is unsafe for constructs involving viral-vector elements, broad-host-range replicons, antimicrobial cargo, delivery systems, plant transformation, mammalian stable-line generation, or any Risk Group 2+ component.

**Required correction:** Split protocol output into two tiers:

- **Design realization plan:** non-operational assembly route, required inputs, QC checkpoints, expected verification artefacts, and institutional approvals needed.
- **Institutional SOP-linked protocol:** generated only when the user has a configured local SOP library, declared biosafety approval, role authorization, and institution-specific templates. The software should reference approved SOP IDs and fill design-specific fields rather than inventing wet-lab procedures from general defaults.

For regulated or higher-risk workflows, the platform should export a reviewer packet and block operational protocol rendering until human sign-off is recorded.

### C2. The data model claims "directed graph" but implements a list

**Finding:** The adversarial review correctly states that a construct should be a directed graph of typed parts with strand, orientation, optionality, and variants. The final schema, however, defines `Construct.modules: tuple[Module, ...]` and `Module.parts: tuple[PartOrVariant, ...]`. It does not explicitly model feature coordinates, strand, topology, circularity, joins, overlaps, reverse-complemented parts, multi-segment constructs, or regulatory interactions.

**Why this matters scientifically:** Real plasmids are circular, features can be on either strand, features can overlap, coding sequences can be split by introns, T-DNA is defined by borders, AAV cargo is defined by ITR-flanked intervals, lentiviral transfer plasmids have LTR/packaging/RRE/cPPT elements with positional constraints, and Gateway or Golden Gate junctions change translated scars. A flat module list cannot safely represent these cases.

**Why this matters technically:** GenBank and SBOL round-trip without annotation loss requires a location model. Restriction-site analysis requires coordinate systems and circular wraparound. Primer design requires binding orientation and strand. Diagnostic digest prediction requires topology and fragment calculation. Combinatorial-library realization requires stable positions for variants.

**Required correction:** Add explicit sequence and graph primitives before coding:

- `SequenceRecord`: alphabet, topology (`linear`/`circular`), molecule type, length, checksum, sequence bytes/string.
- `Location`: start, end, strand, phase, circular-wrap flag, fuzzy/compound locations where needed.
- `Feature`: role, qualifiers, locations, parent sequence, evidence/citation.
- `ConstructGraph`: nodes as parts/features/modules, edges as adjacency/regulatory/derivation/assembly relationships.
- `InsertionContext`: orientation, junction sequence, scar, phase effect, accepted overhang/overlap.

The module list can remain as a user-facing abstraction, but the canonical model must be coordinate- and graph-aware.

### C3. Core restriction-analysis functionality is missing as a module

**Finding:** `REQUIREMENTS.md` makes restriction-site scanning, sticky-end compatibility, unique-site ranking, enzyme methylation sensitivity, double-digest compatibility, and diagnostic digest design mandatory. `ARCHITECTURE.md` has `engine.assembly`, `engine.primer`, `engine.overhang`, and `adapter.catalogue`, but no explicit `engine.restriction`, `engine.digest`, or `engine.sequence_analysis`.

**Impact:** This will cause core cloning logic to leak into unrelated modules. Restriction analysis is not just catalogue lookup. It needs recognition-site parsing, degenerate-base support, cut-position calculation, strand-specific hits, methylation context, circular-sequence wraparound, fragment simulation, compatible-end grouping, band-size prediction, and diagnostic-digest ranking.

**Required correction:** Add a domain-core module such as:

`engine.sequence_analysis` or `engine.restriction`

Required APIs:

- `find_sites(sequence_record, enzyme_set) -> tuple[RestrictionHit, ...]`
- `digest(sequence_record, enzymes) -> DigestPattern`
- `compatible_ends(fragment_a, fragment_b) -> CompatibilityReport`
- `rank_directional_cloning_sites(vector, insert, constraints) -> tuple[SitePair, ...]`
- `design_diagnostic_digest(construct, wrong_clone_models) -> DiagnosticDigestPlan`

This module should depend on the enzyme catalogue but remain a pure computational engine.

### C4. Host context is under-modeled

**Finding:** `Construct` has `host_propagation` and optional `host_expression`. That is not enough for the workflows claimed by the architecture and requirements.

**Examples:**

- Plant transient expression has at least three contexts: E. coli cloning host, Agrobacterium delivery host, and plant target tissue.
- Lentiviral work has bacterial propagation host, packaging/producer cell, and target cell.
- AAV transfer vectors have bacterial propagation, producer system, and target tissue/cell.
- Shuttle vectors have at least two maintenance hosts and sometimes a transfer/delivery context.
- VLP/MS2 designs can separate capsid-production host, cargo-production host, loading context, and target-cell assay context.
- Cell-free systems have no propagation host during expression.

**Impact:** Promoter compatibility, selectable markers, codon usage, biosafety classification, vector size limits, expression readout, and protocol/QC steps all depend on context. Two host fields will produce false compatibility passes and false failures.

**Required correction:** Replace `host_propagation`/`host_expression` with a typed host-context map:

`HostContext(role={propagation, assembly, delivery, producer, expression, target, screening, storage}, host_id, constraints, approval_context)`

Rules should declare which host-context roles they read.

### C5. The validation DAG is underspecified for real biological rules

**Finding:** The rule registry declares `reads: frozenset[FieldPath]`, but real validation depends on more than read sets. Rules may require external adapter outputs, invalidate derived artefacts, write intermediate metrics, depend on thresholds from host/vendor profiles, or require a prior assembly-method choice.

**Examples:**

- Codon optimization can invalidate internal Type IIS scans and synthesisability checks.
- RBS/TIR prediction depends on transcript context, early ORF sequence, host model, and RNA-folding result.
- SpliceAI-style scans depend on mammalian transcript definition, intron/exon assumptions, and predictor version.
- Vendor checks depend on vendor profile date/version and product class.
- Screening depends on screening database/adaptor version and should not be treated as equivalent to local static validation.

**Required correction:** Rule manifests need these fields at minimum:

- `reads`
- `depends_on_metrics`
- `produces_metrics`
- `invalidates`
- `preconditions`
- `target_context`
- `external_adapters`
- `threshold_profile`
- `severity_policy`
- `citation`
- `last_reviewed`
- `test_fixtures`

The engine should compute a DAG over both construct fields and derived metrics, not fields alone.

### C6. Determinism hash omits critical inputs

**Finding:** The architecture proposes `sha256(rule_registry_version || all_plugin_versions || construct_checksum)` as the derivation-provenance hash. This is insufficient.

**Missing inputs include:**

- Catalogue versions for parts, hosts, enzymes, vendor profiles, and rule manifests.
- Adapter configuration, not just adapter version.
- External database versions for screening, REBASE-like enzyme data, codon-usage tables, SignalP/SpliceAI/ViennaRNA models, and overhang matrices.
- Protocol/SOP template versions.
- Locale, units profile, rounding policy, random seeds, and optimization settings.
- Container image digest and CPU/OS assumptions where byte-identical outputs are required.
- User overrides and reviewer decisions.

**Impact:** Replays can appear reproducible while silently changing outputs.

**Required correction:** Define a `DerivationEnvironment` record and hash its canonical JSON serialization. Include every data source, model, adapter, profile, template, configuration, and seed that can affect output.

---

## 4. Major Findings

### M1. RBS and Kozak dependency example is biologically wrong

The adversarial section says a Kozak-score rule depends on RBS choice. RBS and Kozak context are host-specific alternatives, not a dependency chain. In bacteria, RBS/TIR depends on Shine-Dalgarno spacing, transcript structure, start codon, early coding sequence, and host model. In mammalian Pol-II expression, Kozak score depends on the local start-codon context and 5-prime UTR/uAUG structure.

**Correction:** Rewrite the example as two separate host-specific dependency chains:

- Bacterial: promoter/transcript start -> 5-prime UTR/RBS -> early ORF -> RNA folding/TIR.
- Mammalian: promoter/transcript model -> 5-prime UTR/uAUG scan -> Kozak PWM -> ORF translation.

### M2. Sequence type is too narrow

`Part.sequence: DnaSequence` is too restrictive for a platform that models protein tags, translated products, gRNAs, RNA elements, primers, oligos, and protein-level codon optimization targets. The requirements explicitly say `Sequence` must carry DNA/RNA/protein alphabet information.

**Correction:** Introduce a generic `Sequence` or distinct `DnaSequence`, `RnaSequence`, `ProteinSequence`, and `OligoSequence` types with validation and conversion rules. Genetic parts can store DNA, but cargo targets, translations, adapter outputs, and annotations need richer alphabets.

### M3. Assembly strategy API is too generic

The shared interface `validate_parts`, `design_primers`, and `compile_assembly_plan` is a reasonable minimum, but the architecture does not define method-specific `AssemblyPlan` subclasses. That will be necessary because restriction-ligation, Golden Gate, Gibson-like assembly, Gateway, LIC, USER, IVA, and yeast TAR have different physical inputs, intermediate products, scars, enzyme requirements, verification checkpoints, and failure modes.

**Correction:** Add typed plan models:

- `RestrictionLigationPlan`
- `OverlapAssemblyPlan`
- `TypeIISAssemblyPlan`
- `GatewayPlan`
- `LICPlan`
- `USERPlan`
- `InVivoAssemblyPlan`
- `YeastTARPlan`

Each should produce a common `AssemblyPlanSummary` plus method-specific details.

### M4. Codon optimization input is biologically incomplete

`CodonAlgorithm.optimise(orf: ProteinSequence, host, forbidden, protected, target)` starts from protein sequence. This loses the native DNA/RNA context, codon-pair usage, functional nucleotide motifs, splice motifs, RNA-structure constraints, and user-marked protected intervals. The KB emphasizes that codon changes are not biologically silent.

**Correction:** Optimize a `CodingSequenceDesign` containing native DNA, translated protein target, codon table, protected intervals, target host, forbidden motifs, desired CAI/%MinMax/avoid-only mode, and transcript context. Use protein-only input only for de novo synthetic ORFs.

### M5. Biosafety screening fallback is too casual

The architecture lists multi-adapter fallback for screening outages. That is useful for resilience, but an internal blacklist or weaker fallback is not equivalent to an IGSC/IBBIS/SecureDNA-style screening result.

**Correction:** Model screening outcomes as:

- `clear`
- `watchlist`
- `hit`
- `unavailable`
- `not_applicable`
- `manual_review_required`

Fallback to a weaker adapter must not produce an ordinary `clear` unless an institutional policy explicitly allows it and a reviewer signs off.

### M6. SnapGene requirement priority is inconsistent

`REQUIREMENTS.md` marks live SnapGene integration as a MUST. `ARCHITECTURE.md` correctly splits file-format round-trip from live integration and treats the live channel as a later nicety. That is technically realistic, but it changes a MUST requirement without explicitly updating the requirement.

**Correction:** Amend requirements or architecture traceability:

- MUST: GenBank/SBOL/FASTA round-trip and SnapGene-compatible GenBank output.
- SHOULD or COULD: live SnapGene channel, depending on official API availability and licensing.

### M7. Domain purity is contradicted by adapter-backed validation

The architecture says the domain core is pure, but the data-flow diagram has validation calling adapters for RNA folding, splice prediction, SignalP, and Kozak/TIR scoring. Calling external tools can still be deterministic if injected carefully, but it is not pure in the strict sense.

**Correction:** Use one of these patterns:

- Keep the validator pure by passing a `ValidationContext` with precomputed metrics.
- Or define adapter-backed rules as application-layer evaluators and reserve the domain engine for pure dependency scheduling and result aggregation.

Either is acceptable, but the boundary must be explicit.

### M8. Protocol DAG lacks evidence, approvals, and SOP linkage

`ProtocolStep` contains action, reagents, quantities, temperatures, duration, rationale, and safety note. It lacks:

- SOP reference.
- Approval requirement.
- hazard class.
- role permission.
- QC acceptance criteria.
- measured-output schema.
- stop/go decision rule.
- deviation recording.

**Correction:** Add `sop_ref`, `approval_gate`, `checkpoint_criteria`, `measured_outputs`, `allowed_roles`, and `deviation_policy` to the protocol model if operational protocol rendering remains in scope.

### M9. Performance budgets are not separated by deterministic fake vs production adapters

The budgets are plausible for pure structural validation, but not reliably for heavy predictor-backed validation, remote screening, or large library workflows. For example, SpliceAI-class scans and batch screening depend on hardware and external service behavior.

**Correction:** Publish two budget classes:

- **Core deterministic budget:** no network, deterministic fakes or local cached predictors.
- **Production adapter budget:** measured per adapter and reported separately, not used as a universal release blocker.

### M10. Catalogue maintenance risk is larger than stated

The architecture correctly uses YAML catalogues, but the promised catalogue scope is large and volatile: parts, host strains, genotypes, antibiotic concentrations, vendor constraints, enzyme buffers, methylation sensitivity, screening frameworks, and licensing. Quarterly review may be insufficient for vendor and screening profiles.

**Correction:** Add per-catalogue review frequency and source-owner fields. Vendor profiles and screening profiles should carry `retrieved_at`, `valid_until`, `source_url`, and `review_required_after`.

---

## 5. Moderate Findings and Editorial Corrections

1. `app.engine.compatibility` in the data-flow diagram appears to be a naming error. It should likely be `engine.compatibility` called through an application orchestrator.
2. `Library.realisations: Iterator[Construct]` inside a frozen dataclass is not stable, replayable, or JSON-serializable. Store the library definition and generate iterators at runtime.
3. `DomainEvent.payload: dict` weakens the typed-event promise. Use typed event subclasses or discriminated payload schemas.
4. `ProjectStore.list` shadows the Python built-in `list`. Use `list_sessions` or `query`.
5. `ProtocolDAG.steps: dict` is not deterministic unless serialized with canonical key order.
6. `PartCatalogue.add` inside a port in the domain model makes mutability and provenance ambiguous. Adding parts should be an application service that emits events.
7. The architecture refers to SBOL 3 as if the SBOL 2 `ComponentDefinition` terminology is the only model. The implementation should verify against the pinned SBOL 3.1.x object model before coding.
8. The "No-rule-without-citation" gate should require a source grade, not only non-null citation.
9. `screen_batch` should define partial failure semantics and ordering guarantees.
10. `SynthesisVendorAdapter.estimate_cost` should accept a product type, scale, cloning option, currency, and quote date. Sequence alone is insufficient.
11. Primer design should expose salt/chemistry model, nearest-neighbor method, target product, and modification handling.
12. The architecture does not define positive, negative, and process controls as first-class design outputs, even though wet-lab realism requires them.
13. The architecture does not yet include MS2/VLP-specific validation rules despite the v2.0 KB appendix: pac-hairpin presence/copy number, AB-loop insertion limit, SCP linker integrity, capsid/cargo separation, and replication-function exclusion.
14. The current validation state machine moves from `SOFT-WARN` back to `DRAFT` after user acknowledgement, which is ambiguous. Acknowledged warnings should produce an auditable `ACKNOWLEDGED_WARN` or `READY_WITH_WARNINGS` state.
15. The architecture should distinguish "block compilation", "block export", "block vendor submission", and "block operational protocol". These are different safety gates.

---

## 6. Functional Alignment Matrix

| Function | Scientific alignment | Implementability | Wet-lab workflow alignment | Audit result |
|---|---|---|---|---|
| Decision-tree design | Good. Objective -> host -> cargo -> expression -> chemistry matches the KB. | Feasible. | Good if free-text constraints are structured and reviewed. | Accept with LLM safety controls. |
| Parts/modules catalogue | Good. Six-layer model is scientifically valid. | Feasible but needs richer schema. | Good if source/licence/provenance is enforced. | Revise schema before code. |
| Host-strain database | Good concept. | High maintenance burden. | Incomplete for multi-host workflows. | Replace two-host model with host contexts. |
| Restriction analysis | Required and scientifically central. | Under-architected. | Essential for practical cloning. | Add explicit engine module. |
| Assembly method picker | Good strategy direction. | Feasible with typed plan subclasses. | Good if method-specific checkpoints exist. | Strengthen APIs. |
| Golden Gate overhang optimizer | Scientifically authentic. | Feasible with pinned datasets. | Strong for libraries. | Accept with dataset versioning. |
| Codon optimizer | Correctly treated as constrained. | Feasible but input model is incomplete. | Good if protected regions are honored. | Redesign input type. |
| Validation engine | Correct concept. | Feasible but DAG metadata is too thin. | Strong if rules map to concrete remediations. | Expand rule manifest. |
| Primer designer | Scientifically necessary. | Feasible using primer3 plus custom checks. | Strong if off-target and sequencing coverage are included. | Accept, but add detailed API. |
| Protocol generator | Wet-lab realistic in intent. | Technically feasible. | Safety and governance conflict. | Split into design plan vs SOP-linked operational protocol. |
| Sequence I/O | Correct standards posture. | Feasible but annotation round-trip is hard. | Strong. | Add sequence/location model. |
| Screening hook | Correct principle. | Feasible with institutional adapters. | Essential. | Add unavailable/manual-review states and policy logic. |
| Event sourcing | Good for auditability. | Feasible. | Good for provenance. | Expand derivation-environment hash. |
| LLM constraint translator | Useful but risky. | Feasible. | Accept only with user confirmation and local-first default. | Add schema validation and confidentiality controls. |

---

## 7. Required Corrections Before Phase 2

These should be made before scaffolding public APIs:

1. Add canonical `SequenceRecord`, `Location`, `Feature`, and `ConstructGraph` types.
2. Replace `host_propagation` and `host_expression` with role-based `HostContext` entries.
3. Add `engine.restriction` or `engine.sequence_analysis` to the domain-core catalogue.
4. Split protocol generation into non-operational design realization plans and institution-approved SOP-linked protocols.
5. Expand `ValidationRule` manifest fields beyond `reads`.
6. Replace the derivation hash with a complete `DerivationEnvironment` hash.
7. Reconcile live SnapGene integration priority with `REQUIREMENTS.md`.
8. Make screening states include `unavailable` and `manual_review_required`.
9. Add typed event payloads.
10. Add method-specific `AssemblyPlan` subclasses.

---

## 8. Recommended v1.1 Architecture Shape

The current layering can remain. The recommended additions are:

```text
domain/
  sequence.py         SequenceRecord, Location, Feature, topology, checksum
  graph.py            ConstructGraph, module/part adjacency, interactions
  host_context.py     HostContext roles and compatibility scopes
  events.py           typed event subclasses

engine/
  sequence_analysis.py
  restriction.py
  digest.py
  validation.py
  dependencies.py
  assembly/
    base.py
    restriction_ligation.py
    overlap.py
    type_iis.py
    gateway.py
    lic.py
    user.py
    invivo.py
  protocol/
    design_plan.py
    sop_linked_protocol.py

catalogues/
  sop_templates/      local, institution-owned, optional
  screening_profiles/
  vendor_profiles/
```

This keeps the current architectural intent while making the biological representation concrete enough to implement.

---

## 9. Scientific Authenticity Assessment

**Overall:** high, with specific corrections required.

The architecture is grounded in the v2.0 KB and reflects mainstream molecular-biology practice. The major scientific concepts are authentic: host-specific promoters, RBS/Kozak differences, Type IIS domestication, overhang fidelity, codon optimization caution, WPRE safety, vector size limits, provenance, and external screening.

The main scientific weakness is not fabricated content. It is **over-compression of context**:

- Two host fields compress workflows that need multiple biological contexts.
- A part list compresses constructs that need graph and coordinate semantics.
- A single protocol type compresses design guidance, local SOPs, biosafety approvals, and bench execution.
- A single validation DAG over field reads compresses derived biological metrics and external model outputs.

These compressions will become bugs if implemented directly.

---

## 10. Technical Feasibility Assessment

**Feasible with corrections.** The project is ambitious but technically achievable as a modular monolith if development is phased as the roadmap proposes. The highest technical risks are not algorithmic novelty; they are data modeling, annotation round-trip fidelity, catalogue governance, and safety-state management.

Most algorithms have workable paths:

- Restriction scanning and digest simulation are straightforward once sequence topology is explicit.
- GenBank/FASTA I/O is feasible with Biopython-style tooling, but byte-identical round-trip should be relaxed to semantic equivalence where formats reorder or normalize fields.
- SBOL 3 round-trip is feasible but must be tested against the pinned SBOL object model.
- Golden Gate overhang optimization is feasible for stated sizes with published matrices and heuristics.
- Primer design is feasible using primer3-like backends plus plasmid off-target checks.
- Codon optimization is feasible, but only if objectives and protected intervals are explicitly modeled.
- Predictor-backed validation is feasible with pinned local adapters and deterministic fakes.

The current document should be treated as a strong v1.0 concept, not a stable API contract.

---

## 11. Wet-Lab Workflow Alignment

The architecture aligns well with real design-time molecular biology in these respects:

- It validates before ordering or cloning.
- It includes host/marker/promoter/origin compatibility.
- It expects sequencing primers and diagnostic digests.
- It includes QC checkpoints in the protocol DAG.
- It anticipates common failure modes such as empty vector, rearrangement, expression failure, and insolubility.

But it needs correction in these respects:

- It must not treat generated wet-lab steps as universally executable protocols.
- It must represent controls as first-class outputs.
- It must distinguish bacterial cloning, expression testing, delivery/producer systems, and target-cell assays.
- It must gate viral/vector, VLP/phage, plant transformation, and mammalian stable-line outputs through biosafety approval states.
- It must support "design packet for review" as a primary output, not only "bench protocol".

---

## 12. Final Recommendation

Do **not** start coding directly from the current `ARCHITECTURE.md` schema. First produce `ARCHITECTURE.md` v1.1 with the corrections listed in Section 7.

After those corrections, the project should proceed. The conceptual architecture is strong and scientifically serious. The remaining work is to make the domain model and safety model as rigorous as the narrative already claims.

**Go/no-go:** conditional go. Go after v1.1 fixes the data model, restriction-analysis module, multi-host contexts, protocol-safety split, validation-rule manifest, provenance hash, and SnapGene requirement reconciliation.

