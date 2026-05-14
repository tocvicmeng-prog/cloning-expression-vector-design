# Response to Codex's Audit of ARCHITECTURE.md
## Three-Role Adjudication of 31 Findings, with Per-Finding Verdict and v1.1 Change Action

**Document type:** Audit-response and adjudication record.
**Date:** 2026-05-13.
**Audit reviewed:** `audit report/ARCHITECTURE_Audit_Report.md` by Codex (senior molecular-biology scientist + senior software-architecture reviewer stance).
**Respondents:** `/architect`, `/scientific-advisor`, `/dev-orchestrator` — the same three roles that produced ARCHITECTURE.md v1.0 and signed it off after four rounds of falsification.
**Companion deliverable:** `ARCHITECTURE.md` v1.1 (in project root) — the upgraded blueprint incorporating every accepted correction.
**Result tally:** **6 / 6 critical findings accepted • 10 / 10 major findings accepted • 14 / 15 moderate findings accepted (1 nuanced) • 0 findings defended outright.** Codex's audit was substantive and the v1.0 architecture is materially improved by the v1.1 upgrade.

---

## 0. Method

The three roles re-convened. Codex's audit was treated as a "Round 5" fourth participant in the adversarial-falsification protocol from ARCHITECTURE.md §3, with two operating rules:

1. **Defend only when defensible.** Where Codex's finding is correct, all three roles concede and the architecture is upgraded. There is no "defend by reframing"; either Codex's reading of v1.0 is fair, or it is not.
2. **Every accepted finding produces a concrete v1.1 change.** The v1.1 change must be specific enough that the next phase can act on it without re-litigating the point.

Per-finding format below: **Finding** (restated) → **/architect, /scientific-advisor, /dev-orchestrator positions** → **Verdict** → **v1.1 change action**.

---

## 1. Critical findings (C1 – C6)

### C1. Safety and protocol-generation scope conflict

**Finding restated.** v2.0 KB declares "conceptual vector-design guidance only … does not provide step-by-step wet-lab protocols, culture conditions, transformation procedures, viral production procedures, or operational parameters." ARCHITECTURE.md and REQUIREMENTS.md nonetheless mandate full operational protocol generation (FR-PROTO-01 … FR-PROTO-20). The two cannot both be true.

**`/scientific-advisor`:** Codex is right. The KB's safety scope is not decorative — it reflects the fact that operational protocols for transformation, viral packaging, agroinfiltration, mammalian stable-line generation, and RG2+ workflows require institution-specific SOPs, biosafety committee approval, and trained role-based access. An AI-generated default protocol is appropriate for *design realisation* (assembly route, primer set, QC checkpoints, expected verification artefacts) but **not** as a stand-in for an institutional SOP. I should have caught this in Round 3.

**`/architect`:** Conceded. The single `ProtocolGenerator` module collapses two distinct artefacts that should have distinct types, distinct lifecycles, and distinct safety gates. The fix is structural, not cosmetic.

**`/dev-orchestrator`:** Conceded — with a sponsor sharpening (recorded below). This is the most important finding in the audit because it changes the *output policy* of the platform, not just an internal API. We need a hard gate that blocks rendering of operational steps for any construct whose biosafety classification or component set exceeds the user's **administrator-granted** authorisation profile. The user does not self-declare this profile; only the software developer (system level) and the institutional administrator (deployment level) may create, modify, or revoke a user's authorisation profile. The user **declares an intent** (which SOP library to bind to, which biosafety approval ID applies, which role they are operating in) but those declarations are validated against the administrator-granted profile; declarations that exceed the profile are rejected. The user has no path to grant themselves operational-protocol rights, no path to lift a biosafety gate, and no path to widen their declared role.

> **Sponsor sharpening (post-audit, 2026-05-13).** The project sponsor sharpened C1's resolution explicitly: the authorisation profile governing the operational-protocol hard gate is **administrator-controlled**, never user-self-declared. v1.2 of ARCHITECTURE.md (companion file) implements this as a typed `AuthorisationProfile` stored in an admin-only authorisation store, an `AuthorisationStore` port that exposes profiles to the engine read-only, a `Role` enum (`Developer`, `Administrator`, `Reviewer`, `User`) with strict separation of duties, and a CI gate (`no-self-authorisation-check`) that statically prevents any code path from letting a `User` role mutate their own profile. The `/dev-orchestrator` concession above is the v1.2 wording.

> **Sponsor clarification — role hierarchy (2026-05-13, v1.3).** The project sponsor clarified the relationship between Administrator and Reviewer: **Administrator capabilities ⊇ Reviewer capabilities** (an Administrator may perform every action a Reviewer may perform, including per-construct sign-off on `WATCHLIST` / `MANUAL_REVIEW_REQUIRED` screening verdicts), but **Reviewer capabilities ⊄ Administrator capabilities** (a Reviewer may not mint / modify / revoke `AuthorisationProfile` records, may not author institutional SOPs, may not mutate the audit log). The practical consequence is that in an institution that does not appoint a separate biosafety officer, **the Administrator alone may complete the entire authorisation workflow** — no separate Reviewer is required. v1.3 of ARCHITECTURE.md implements this as: (a) a `Principal.can_act_as(role)` predicate that returns True for `AdminPrincipal.can_act_as(Role.REVIEWER)`, (b) an updated event schema where reviewer sign-offs carry a `signer_role` discriminator so the audit trail records who actually signed, (c) updated REQUIREMENTS FR-AUTH-13 / FR-AUTH-14, and (d) an Administrator-only end-to-end UAT in Phase 13.

**Verdict.** **Accept.** No defense.

**v1.1 change action.**

1. Split `engine.protocol` into two engines:
   - `engine.design_plan` — produces a **`DesignRealisationPlan`** (non-operational): assembly route, fragment inputs, QC checkpoints, expected verification artefacts, institutional-approvals-required list, biosafety classification, reviewer-packet summary. Always renderable.
   - `engine.sop_protocol` — produces a **`SopLinkedProtocol`** (operational, gated): SOP-template-bound, with user-declared institutional SOP library, declared biosafety approval ID, role authorisation, deviation policy. Renderable only when authorisation gates pass.
2. Add `catalogues/sop_templates/` (institution-owned; empty by default).
3. Add four distinct safety gates (cf. Moderate 15): `BlockCompile`, `BlockExport`, `BlockVendorSubmission`, `BlockOperationalProtocol`. Each has its own predicate set.
4. Update `app.protocol_orchestrator` to dispatch to `engine.design_plan` (always) and to `engine.sop_protocol` (only when gated unlock conditions are met).
5. Add `ProtocolStep.sop_ref`, `approval_gate`, `checkpoint_criteria`, `measured_outputs`, `allowed_roles`, `deviation_policy` fields (cf. M8).
6. REQUIREMENTS.md FR-PROTO-* split into FR-PROTO-DESIGN-* (MUST) and FR-PROTO-SOP-* (SHOULD, gated).

---

### C2. The data model claims "directed graph" but implements a list

**Finding restated.** Round 3 of v1.0 promised that "a construct is a directed graph of typed parts with strand and orientation." The schema in §4.6, however, expresses `Construct.modules: tuple[Module, ...]` and `Module.parts: tuple[PartOrVariant, ...]` — flat lists, no `SequenceRecord`, no `Location`, no `Feature`, no topology, no strand, no fuzzy/compound locations, no `ConstructGraph`.

**`/scientific-advisor`:** Codex is right and the consequence is severe. A flat module list cannot represent circular plasmids (no wrap-around for restriction analysis), reverse-strand features, overlapping features (regulatory + coding overlap is common in viral / phage / VLP), CDS split by introns, T-DNA boundary-flanked intervals, AAV ITR-flanked cargo with positional constraints, or lentiviral LTR / Ψ / RRE / cPPT positional invariants. Without a coordinate system and topology, every downstream module that needs positions (restriction scanner, primer designer, diagnostic digest, GenBank/SBOL round-trip) will have to reconstruct them from the linear concatenation — fragile and lossy.

**`/architect`:** Conceded. The narrative was aspirational; the schema was not. v1.1 makes the schema match the narrative.

**`/dev-orchestrator`:** Conceded. This is a *Phase 2 blocker* — if the scaffold hardens the v1.0 schema, every later phase pays the cost. The Phase 2 brief must wait for v1.1.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Add the following types to `domain.sequence` and `domain.graph`:

```python
@dataclass(frozen=True)
class SequenceRecord:
    alphabet: Alphabet                       # DNA | RNA | PROTEIN | OLIGO
    topology: Literal["linear", "circular"]
    molecule_type: MoleculeType              # ds-DNA, ss-DNA, mRNA, gRNA, ...
    length: int
    sequence: str                            # canonical-orientation
    checksum: Sha256                         # canonical-orientation checksum

@dataclass(frozen=True)
class Location:
    start: int                               # 0-indexed
    end: int                                 # half-open
    strand: Literal["+", "-", "."]
    phase: Literal[0, 1, 2, "."]             # for CDS
    circular_wrap: bool = False              # crosses origin in circular topology
    fuzzy_start: bool = False
    fuzzy_end: bool = False
    sub_locations: tuple["Location", ...] = ()   # compound/joined locations

@dataclass(frozen=True)
class Feature:
    role: SequenceOntologyTerm
    qualifiers: dict[str, str]
    locations: tuple[Location, ...]
    parent_sequence_id: SequenceRecordId
    evidence: tuple[Citation, ...]

@dataclass(frozen=True)
class InsertionContext:
    parent_node_id: NodeId
    orientation: Literal["forward", "reverse"]
    junction_sequence: str                   # the joined sequence across the boundary
    scar: str | None                         # residual scar (e.g., Gateway att, TEV)
    phase_effect: int                        # frame impact for downstream CDS
    accepted_overhang_or_overlap: str | None
    insertion_point: Location

@dataclass(frozen=True)
class ConstructGraph:
    nodes: dict[NodeId, GraphNode]            # GraphNode = Part | Feature | Module
    edges: tuple[Edge, ...]                   # EdgeKind ∈ Adjacency | Regulatory |
                                              #              Derivation | Assembly
    topology: Literal["linear", "circular"]
    sequence_record: SequenceRecord           # derived; checksum binds to nodes/edges
```

`Construct` becomes a thin wrapper exposing both `modules` (the user-facing six-layer view) and `graph` (the canonical coordinate-and-graph model). All coordinate-aware operations (restriction scan, primer design, fragment simulation) read `graph`; all UI affordances and rule scoping read `modules`. The two are kept consistent by an invariant check on every state transition.

---

### C3. Core restriction-analysis functionality missing as a module

**Finding restated.** REQUIREMENTS FR-CORE-01 … FR-CORE-03 mandate restriction-site scanning, sticky-end compatibility evaluation, and unique-site ranking. v1.0 has no `engine.restriction` module; the work is implicit inside `engine.assembly`. Diagnostic digest design has no home at all.

**`/architect`:** Conceded. v1.0 §4.2.1 lists `engine.assembly`, `engine.primer`, `engine.overhang`, but slipped restriction analysis under "assembly" because the Golden Gate / Gibson / restriction strategies all use it. That's a category error. Restriction analysis is a *sequence-analysis primitive* used by many strategies, not a behaviour of any single strategy.

**`/scientific-advisor`:** Conceded. Restriction analysis is the single most-used operation in classical cloning. It needs its own home with its own API surface. Diagnostic digest design is non-trivial — picking enzyme(s) that distinguish correct vs all reasonable wrong-clone topologies (empty vector, insert in reverse, double insert, single recombinant) is its own algorithm.

**`/dev-orchestrator`:** Conceded. This is also a Phase 2 brief change.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Add `engine.sequence_analysis` to the domain core (a new top-level engine):

```python
# engine/sequence_analysis.py — pure, no I/O, no adapters.

def find_sites(
    record: SequenceRecord,
    enzymes: frozenset[Enzyme],
    strand: Literal["+", "-", "both"] = "both",
    methylation_context: MethylationContext | None = None,
) -> tuple[RestrictionHit, ...]: ...

def digest(
    record: SequenceRecord,
    enzymes: frozenset[Enzyme],
) -> DigestPattern: ...

def compatible_ends(
    fragment_a: Fragment,
    fragment_b: Fragment,
) -> EndCompatibilityReport: ...

def rank_directional_cloning_sites(
    vector: SequenceRecord,
    insert: SequenceRecord,
    must_be_unique_in_vector: bool = True,
    must_be_absent_in_insert: bool = True,
    constraints: SiteRankingConstraints | None = None,
) -> tuple[RankedSitePair, ...]: ...

def design_diagnostic_digest(
    correct: SequenceRecord,
    wrong_clone_models: tuple[WrongCloneModel, ...],
    enzyme_pool: frozenset[Enzyme],
    target_band_difference_bp: int = 200,
    gel_resolution_bp: int = 100,
) -> DiagnosticDigestPlan: ...

def fragment_simulation(
    record: SequenceRecord,
    enzymes: frozenset[Enzyme],
) -> tuple[Fragment, ...]: ...
```

Module dependencies: depends only on `domain.sequence`, `domain.graph`, and `adapter.catalogue.EnzymeCatalogue`. No adapter or I/O dependency. Pure computational engine.

---

### C4. Host context is under-modeled

**Finding restated.** v1.0 expresses host via `Construct.host_propagation: HostId` and `Construct.host_expression: HostId | None`. Plant transient expression has 3 hosts (E. coli cloning + Agrobacterium delivery + plant target). Lentivirus has 3 hosts (bacterial propagation + packaging cell + target cell). AAV has 3 hosts (bacterial propagation + producer + target tissue). Shuttle vectors have ≥ 2 maintenance hosts. VLP / MS2 designs have capsid-production + cargo-production + loading + target-cell-assay contexts. Cell-free has *no* propagation host during expression. Two fields cannot cover this.

**`/scientific-advisor`:** Conceded — and this would have produced false-positives on every multi-context workflow. A binary marker-conflict check between "propagation host" and "vector marker" passes silently in a workflow where the *delivery* host (Agrobacterium) is the marker-conflict-relevant host, not the cloning host. Promoter compatibility, codon usage, biosafety classification, vector size limits, and expression readout all depend on which biological context they apply to.

**`/architect`:** Conceded. The host model should be role-keyed.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Replace `host_propagation` / `host_expression` with a typed role-map:

```python
HostRole = Literal[
    "cloning_propagation",      # the E. coli strain holding the construct
    "assembly",                  # e.g., yeast TAR / IVA host
    "delivery",                  # e.g., Agrobacterium for plants
    "producer",                  # e.g., HEK293T for lentivirus packaging
    "expression",                # the host that *produces* the cargo product
    "target",                    # the host that *receives* the product
    "screening_assay",           # the host used to read out function
    "storage",                   # the strain in which the construct is archived
]

@dataclass(frozen=True)
class HostContext:
    role: HostRole
    host_id: HostId
    constraints: tuple[HostConstraint, ...]
    approval_context: ApprovalContext | None    # links to IBC/IRB ticket

@dataclass(frozen=True)
class Construct:
    ...
    hosts: tuple[HostContext, ...]              # ordered by role
    ...
```

Rules declare which host roles they read; the compatibility checker iterates roles. The two-field shorthand becomes a *view* (e.g., `construct.host(role="cloning_propagation")`) for backward compatibility with the user-facing UI. Cell-free can omit any propagation host; lentivirus declares producer + target; plant transient declares cloning + delivery + target.

---

### C5. The validation DAG is underspecified for real biological rules

**Finding restated.** `ValidationRule` carries `reads: frozenset[FieldPath]` but no metric dependencies, no produces/invalidates declarations, no preconditions, no target-context scope, no external-adapter declarations, no threshold profile, no severity policy, no `last_reviewed`, no fixture refs.

**`/scientific-advisor`:** Conceded. The example Codex gives — codon optimisation invalidating internal Type-IIS scans — is exactly the kind of cross-rule interaction the v1.0 DAG can't represent. Without `invalidates`, the engine cannot know that a codon-opt commit forces a re-scan; without `depends_on_metrics`, it cannot avoid re-running everything; without `external_adapters`, it cannot version-bind the result.

**`/architect`:** Conceded. v1.0 was honest about the *concept* of dependency-aware evaluation but specified the dependency edges too narrowly. The rule manifest is where most of this lives.

**`/dev-orchestrator`:** Conceded. The CI gate "100 % rule-validation coverage" already requires fixtures; making them first-class fields is just structural honesty.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Expand `ValidationRule` manifest to:

```python
@dataclass(frozen=True)
class ValidationRule:
    rule_id: RuleId
    predicate_name: str
    severity: Severity
    severity_policy: SeverityPolicy           # per-host or per-tier override map
    reads: frozenset[FieldPath]                # construct fields read
    depends_on_metrics: frozenset[MetricId]    # derived metrics this rule consumes
    produces_metrics: frozenset[MetricId]      # derived metrics this rule emits
    invalidates: frozenset[MetricId | RuleId]  # cache-invalidation contract
    preconditions: tuple[Precondition, ...]    # e.g., "assembly_method must be picked"
    target_context: ContextScope               # which host role(s) and which layer
    external_adapters: tuple[AdapterRef, ...]  # adapter + pinned version
    threshold_profile: ThresholdProfileRef     # references host/vendor profile
    citation: GradedCitation                   # source grade (A1/A2/B1/...)
    last_reviewed: Date
    reviewed_by: ReviewerId
    test_fixtures: tuple[FixtureRef, ...]      # triggering + passing fixtures
    suggested_remediation: str
```

The validation engine builds a DAG over both **construct fields** *and* **derived metrics**; `produces_metrics` and `depends_on_metrics` are the edges. `invalidates` allows a rule (e.g., codon optimisation) to mark downstream metric-consumers stale even if their construct-field reads have not changed.

---

### C6. Determinism hash omits critical inputs

**Finding restated.** v1.0's `derivation_provenance_hash = sha256(rule_registry_version || all_plugin_versions || construct_checksum)` ignores catalogue versions, adapter *configurations* (not just versions), external database versions (REBASE, codon-usage tables, model weights), SOP templates, locale/units/seeds, container image digest, and user overrides.

**`/architect`:** Conceded. The v1.0 hash was a placeholder, not a serious specification. The right form is a structured record of the *entire derivation environment* serialised canonically and hashed.

**`/scientific-advisor`:** Conceded. A clear silent-failure mode: a vendor profile YAML is edited, no plugin version bumps, the construct's "compiled" snapshot replays as `clear` but the vendor would actually reject it now. We need to detect this.

**`/dev-orchestrator`:** Conceded. The reproducibility CI gate becomes meaningful only if the hash captures everything the gate would reproduce.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Define a `DerivationEnvironment` record and hash its canonical JSON serialisation:

```python
@dataclass(frozen=True)
class DerivationEnvironment:
    rule_registry_version: Semver
    rule_manifest_hashes: dict[RuleManifestFile, Sha256]   # MR/WR/SR/BR + others
    catalogue_versions: dict[CatalogueId, Semver]
    catalogue_content_hashes: dict[CatalogueId, Sha256]
    plugin_versions: dict[PluginId, Semver]
    plugin_configurations: dict[PluginId, Sha256]          # canonical config hash
    external_database_versions: dict[DatabaseId, str]      # REBASE, codon tables, SpliceAI weights, ...
    sop_template_versions: dict[SopTemplateId, Semver]
    container_image_digest: ContainerDigest                # OCI image @sha256:...
    cpu_arch: str
    locale: str
    units_profile: UnitsProfile
    rounding_policy: RoundingPolicy
    random_seeds: dict[RandomSeedId, int]                  # explicit per subsystem
    optimisation_settings: OptimisationSettings
    user_overrides: tuple[UserOverride, ...]               # acks, justifications, sign-offs
    reviewer_decisions: tuple[ReviewerDecision, ...]
    construct_checksum: Sha256

    def canonical_json(self) -> bytes: ...                 # deterministic key order
    def hash(self) -> Sha256: ...                          # sha256 of canonical_json()
```

The `derivation_provenance_hash` is now `DerivationEnvironment.hash()`. Every `Compiled`, `Screened`, and `Exported` event stores the full `DerivationEnvironment` (or its hash + a reference into the audit store). Replay verifies the hash; mismatch forces re-derivation.

---

## 2. Major findings (M1 – M10)

### M1. RBS-and-Kozak dependency example biologically wrong

**Finding restated.** ARCHITECTURE §3.1.1 says "a Kozak-score rule (V007) depends on the RBS choice (V006), which depends on the codon strategy (V016)." But RBS and Kozak are *host-specific alternatives*, not a chain — RBS is bacterial (SD/spacing/early ORF/RNA folding/TIR), Kozak is mammalian (5′ UTR / uAUG scan / PWM / ORF).

**`/scientific-advisor`:** Conceded. I wrote that sentence and it elides a real-world division. The example survived Round 1 because the *conclusion* (DAG-evaluator needed) is correct; the worked example used to justify it is not biologically representative.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Replace the §3.1.1 example with two host-specific dependency chains:

> *Bacterial:* `promoter / transcript start → 5′ UTR / RBS / SD-spacing → early ORF context → RNA folding → TIR prediction`.
>
> *Mammalian Pol-II:* `Pol-II promoter / transcript model → 5′ UTR / uAUG scan → Kozak PWM score → ORF translation`.

The DAG-eval still required; the example is now correct.

---

### M2. Sequence type too narrow

**Finding restated.** `Part.sequence: DnaSequence` is too restrictive when the platform also models protein tags, gRNAs, primers, oligos, and protein-level codon-optimisation targets.

**`/scientific-advisor`:** Conceded. A gRNA "part" should declare RNA alphabet; a primer "part" should declare oligo (single-strand, modifiable); a protein tag's annotation should declare protein alphabet; codon optimisation needs both the source DNA (for protected functional motifs) and the target protein (for synonymy).

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Introduce a generic `Sequence` ADT with sub-types:

```python
class Alphabet(Enum):
    DNA = "DNA"; RNA = "RNA"; PROTEIN = "PROTEIN"; OLIGO = "OLIGO"

@dataclass(frozen=True)
class Sequence:
    alphabet: Alphabet
    body: str
    validation: SequenceValidationFlags

# Specialised wrappers preserved for type-narrow APIs:
class DnaSequence(Sequence): ...      # alphabet = DNA
class RnaSequence(Sequence): ...      # alphabet = RNA
class ProteinSequence(Sequence): ...  # alphabet = PROTEIN
class OligoSequence(Sequence): ...    # alphabet = OLIGO; modifiable
```

Conversion functions: `transcribe(DnaSequence) -> RnaSequence`, `translate(DnaSequence | RnaSequence, table) -> ProteinSequence`, `reverse_complement(DnaSequence) -> DnaSequence`. `Part.sequence: Sequence` (was `DnaSequence`).

---

### M3. Assembly strategy API too generic

**Finding restated.** v1.0 declared a `AssemblyMethod` interface with `validate_parts / design_primers / compile_assembly_plan` but no method-specific `AssemblyPlan` subclasses. Different chemistries have different physical inputs, intermediate products, scars, enzyme requirements, verification checkpoints, and failure modes.

**`/architect`:** Conceded. v1.0 acknowledged the strategy hierarchy but stopped one level short on the data side — the *plans* coming out of each strategy should be typed.

**`/scientific-advisor`:** Conceded. Restriction-ligation, Golden Gate, Gibson, Gateway, LIC, USER, IVA, and yeast TAR each have *non-comparable* failure modes and verification checkpoints. A single flat plan type cannot represent that.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Add typed plan subclasses sharing an `AssemblyPlanSummary` projection:

```python
@dataclass(frozen=True)
class AssemblyPlanSummary:
    method: AssemblyMethodId
    fragments: tuple[FragmentSpec, ...]
    expected_product: SequenceRecord
    expected_byproducts: tuple[SequenceRecord, ...]
    verification_checkpoints: tuple[Checkpoint, ...]
    expected_failure_modes: tuple[FailureMode, ...]

# Method-specific plans:
class RestrictionLigationPlan(AssemblyPlanSummary): ...      # + enzyme set, dephosphorylation, ligation conditions
class OverlapAssemblyPlan(AssemblyPlanSummary): ...          # + overlap lengths, polymerase fidelity, ratios
class TypeIISAssemblyPlan(AssemblyPlanSummary): ...          # + enzyme, overhang set, cycling profile
class GatewayPlan(AssemblyPlanSummary): ...                  # + BP/LR reaction, att-scar declaration
class LICPlan(AssemblyPlanSummary): ...                      # + tail design, T4 polymerase conditions
class USERPlan(AssemblyPlanSummary): ...                     # + dU primer placement
class InVivoAssemblyPlan(AssemblyPlanSummary): ...           # + IVA host requirements
class YeastTARPlan(AssemblyPlanSummary): ...                 # + yeast host, marker, TAR fragment design
```

Each strategy emits its concrete subclass; the orchestrator handles the summary; downstream protocol generation dispatches on subtype.

---

### M4. Codon optimisation input biologically incomplete

**Finding restated.** `CodonAlgorithm.optimise(orf: ProteinSequence, host, forbidden, protected, target)` loses native DNA / RNA context, codon-pair usage, functional nucleotide motifs (frameshift sites, IRES, riboswitches), splice motifs, RNA-structure constraints, and user-marked protected intervals.

**`/scientific-advisor`:** Conceded. Protein-only input is correct for *de novo* synthetic ORFs but wrong for re-coding an existing gene where the native nucleotide context carries information the protein doesn't.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Introduce a richer input:

```python
@dataclass(frozen=True)
class CodingSequenceDesign:
    native_dna: DnaSequence | None             # None for de-novo
    target_protein: ProteinSequence
    codon_table: CodonTableId
    target_host_context: HostContext           # which biological context drives codon usage
    protected_intervals: tuple[Location, ...]  # native sequence preserved here
    forbidden_motifs: tuple[Motif, ...]        # RE sites, Type IIS, vendor-forbidden patterns
    functional_rna_features: tuple[Feature, ...]   # frameshift, IRES, riboswitch — must preserve
    splice_constraints: SpliceConstraints
    rna_structure_constraints: RnaStructureConstraints
    cai_target_window: tuple[float, float]
    minmax_target_distance: float
    mode: Literal["CAI", "MinMax", "CHARMING", "avoid_only"]

class CodonAlgorithm(Protocol):
    def optimise(self, design: CodingSequenceDesign) -> CodingSequenceResult: ...
```

`avoid_only` mode preserves native codons except where a forbidden motif demands a synonymous swap — the most conservative mode and the right default when a native gene exists.

---

### M5. Biosafety screening fallback too casual

**Finding restated.** v1.0's multi-adapter fallback could produce an ordinary `clear` from a weaker adapter when the canonical adapter is unavailable. That is dangerous: an internal blacklist hit-miss is not equivalent to an IGSC / IBBIS / SecureDNA result.

**`/scientific-advisor`:** Conceded. A `clear` is a positive safety claim; only a fully-functional canonical screen earns one.

**`/architect`:** Conceded. The fallback chain should *change the verdict shape*, not just retry.

**`/dev-orchestrator`:** Conceded. This also affects the safety gates from C1.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Expand the `ScreeningResult.verdict` enum:

```python
class ScreeningVerdict(Enum):
    CLEAR = "clear"                                  # canonical adapter returned clear
    WATCHLIST = "watchlist"                          # canonical adapter flagged
    HIT = "hit"                                      # canonical adapter found a match
    UNAVAILABLE = "unavailable"                      # canonical adapter down / unreachable
    NOT_APPLICABLE = "not_applicable"                # sequence below screening threshold
    MANUAL_REVIEW_REQUIRED = "manual_review_required"  # policy-required human review
```

The screening orchestrator never silently upgrades a weaker-adapter result to `CLEAR`. Fallback adapters can produce `MANUAL_REVIEW_REQUIRED` only; institutional policy may then permit a reviewer to sign off — recorded in audit, never elided.

---

### M6. SnapGene requirement priority inconsistent

**Finding restated.** REQUIREMENTS FR-INT-04 marked the live SnapGene channel as MUST; v1.0 architecture deferred it to Phase 11 / 12 as nice-to-have. The architecture changed a MUST without amending the requirement.

**`/architect`:** Conceded — and the architecture's reasoning (live API depends on SnapGene Server availability and licensing, which is uncertain) is defensible *as a position*, but a MUST cannot be unilaterally downgraded by architecture; the requirement must be reconciled.

**`/scientific-advisor`:** Conceded. "Seamless interoperability" is satisfied by the *file-watch* round-trip channel (Phase 9) for the vast majority of user workflows; the *live API* channel is the power-user feature. The original UR-01 should be split into two requirements with appropriate priorities.

**`/dev-orchestrator`:** Conceded. Cross-document change required.

**Verdict.** **Accept.** No defense.

**v1.1 change action.**

1. ARCHITECTURE.md amends §5 OQ-07 resolution to split UR-01.
2. REQUIREMENTS.md updates UR-01 into:
   - **UR-01a (MUST):** SnapGene-compatible GenBank/SBOL/FASTA round-trip plus a **file-watch automated channel** (user exports from SnapGene into a watched directory; platform parses, validates, writes an updated GenBank that SnapGene re-imports). Delivered in Phase 9.
   - **UR-01b (SHOULD):** Live SnapGene Server API channel. Conditional on official API availability and acceptable licensing. Delivered in Phase 12; falls back to UR-01a if API is unavailable.
3. FR-INT-04 is split into FR-INT-04a (MUST, file-watch) and FR-INT-04b (SHOULD, live API).

---

### M7. Domain purity contradicted by adapter-backed validation

**Finding restated.** v1.0 says the domain core is pure, but the data-flow diagram shows the validator calling adapters (RNA folding, splice prediction, SignalP, Kozak/TIR). Even with dependency injection, that is impure in the strict sense.

**`/architect`:** Conceded. The cleaner pattern is **precomputed metrics in a `ValidationContext`** — the application layer runs adapters and produces metrics; the domain validator consumes the context and runs only pure predicates.

**`/scientific-advisor`:** Conceded. This also makes the rule manifest cleaner — `depends_on_metrics` (already added in C5) becomes the canonical mechanism.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Architectural restructure: the **domain-core validation engine** becomes pure (no adapters). The **application-layer `ValidationOrchestrator`** runs adapter-backed metric computations *before* invoking the domain validator, packaging results into a `ValidationContext`:

```python
@dataclass(frozen=True)
class ValidationContext:
    construct: Construct
    derived_metrics: dict[MetricId, MetricValue]   # precomputed by adapters
    threshold_profile: ThresholdProfile
    derivation_environment: DerivationEnvironment
```

`engine.validation.validate(context, registry) -> ValidationReport` is now pure. The `app.validation_orchestrator` is responsible for: (a) determining which metrics are required for the current rule set, (b) calling the appropriate adapters via their ports, (c) caching metric results in the session for incremental re-eval, (d) constructing the context, (e) invoking the pure validator.

The data-flow diagram in §4.3 is updated to make this boundary explicit.

---

### M8. Protocol DAG lacks SOP linkage, approvals, controls

**Finding restated.** `ProtocolStep` has action/reagents/quantities/temperature/duration/rationale/safety_note but lacks SOP reference, approval requirement, hazard class, role permission, QC acceptance criteria, measured-output schema, stop/go decision rule, and deviation recording.

**`/scientific-advisor`:** Conceded — and this ties to C1. If operational protocols are gated to institutional SOPs, the protocol step must *link* to the SOP rather than reinvent it.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Expand `ProtocolStep`:

```python
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
    successors: tuple[Edge, ...]
    # New in v1.1:
    sop_ref: SopRef | None                       # institutional SOP linkage
    approval_gate: ApprovalGate | None           # gate that must be satisfied
    hazard_class: HazardClass                    # PPE, containment, waste class
    allowed_roles: frozenset[Role]               # which user roles may execute
    checkpoint_criteria: tuple[Predicate, ...]   # measurable accept/reject
    measured_outputs: tuple[MeasurementSchema, ...]
    deviation_policy: DeviationPolicy            # what to do if results out of spec
    decision_rule: DecisionRule | None           # stop/go/branch
```

Plus a new `engine.controls` module emitting first-class control designs (positive, negative, process) for every assay step (cf. Moderate 12).

---

### M9. Performance budgets not separated by adapter class

**Finding restated.** v1.0's NFR budgets are plausible for pure structural validation but not for predictor-backed validation, remote screening, or large libraries.

**`/dev-orchestrator`:** Conceded. The release gate cannot be "byte-identical determinism" for adapter-dependent work because external services and hardware vary.

**`/architect`:** Conceded. Two budget classes.

**`/scientific-advisor`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** ARCHITECTURE §4.9 publishes two budget tiers:

| Tier | Scope | Used as |
|---|---|---|
| **Core deterministic** | Pure domain core + deterministic fakes for every port. Network mocked. Clock mocked. | Release-blocker CI gate. |
| **Production adapter** | Production adapters live; measured per adapter; reported separately. | Operational SLA, not a release blocker. |

Each adapter's `Manifest` declares its measured-typical and measured-max latency.

---

### M10. Catalogue maintenance risk larger than stated

**Finding restated.** Vendor profiles, screening profiles, antibiotic concentrations, methylation tables, and licensing data are volatile; quarterly review may be too slow.

**`/dev-orchestrator`:** Conceded.

**`/scientific-advisor`:** Conceded.

**`/architect`:** Conceded.

**Verdict.** **Accept.** No defense.

**v1.1 change action.** Add per-catalogue maintenance metadata. Every YAML manifest carries:

```yaml
maintenance:
  retrieved_at: 2026-04-12
  valid_until: 2026-10-12
  source_url: https://www.twistbioscience.com/...
  source_owner: vendor
  review_required_after: 2026-09-12
  review_frequency: quarterly | monthly | as-needed
```

A CI gate (`stale-catalogue-check`) fails if any active catalogue's `review_required_after` is in the past. `/scientific-advisor` owns vendor and screening profiles; review cadence is monthly for vendor profiles and as-needed (alert-driven) for screening profiles.

---

## 3. Moderate findings (15 items)

| # | Finding | Verdict | v1.1 change |
|---|---|---|---|
| 1 | `app.engine.compatibility` is a naming error; should be `engine.compatibility` called via an application orchestrator. | Accept (typo). | Rename in §4.3 diagram and §4.2 catalogue. |
| 2 | `Library.realisations: Iterator[Construct]` inside a frozen dataclass is not stable or serialisable. | Accept. | Store the *Library definition* (the construct with `OneOf`/`Variable`); iterators are produced on demand by `app.library_realisation.expand(library, expansion_policy)`. |
| 3 | `DomainEvent.payload: dict` weakens the typed-event promise. | Accept. | Replace with discriminated `DomainEvent` subclasses (`PartAdded`, `HostSelected`, `Compiled`, etc.), each with its typed payload. |
| 4 | `ProjectStore.list` shadows the Python built-in `list`. | Accept. | Rename `list` → `list_sessions`. |
| 5 | `ProtocolDAG.steps: dict` is not deterministic unless serialised with canonical key order. | Accept. | Use `frozendict` with explicit sort key in canonical serialisation; document the canonical-order rule in §4.6. |
| 6 | `PartCatalogue.add` in a domain port makes mutability and provenance ambiguous. | Accept. | Move add semantics to `app.part_library_service` which emits `PartAdded` events; the port remains read-only (`get` + `search`). |
| 7 | The architecture refers to SBOL 3 with SBOL 2 `ComponentDefinition` language. | Accept. | Update §4.6 and §5 to use SBOL 3 `Component` / `Sequence` / `SequenceFeature` terms; pin pySBOL3 ≥ 1.3 against SBOL 3.1.x; add a round-trip test against published SBOL 3.1.0 reference designs. |
| 8 | "No-rule-without-citation" gate should require a *source grade*, not only non-null citation. | Accept. | CI gate requires `citation.grade` ∈ {A1, A2, A3, B1, B2}; grade `C` allowed only when corroborating A/B source also present. (Source-grade rubric per v2.0 KB §2.1.) |
| 9 | `screen_batch` should define partial-failure semantics and ordering guarantees. | Accept. | Adapter contract: `screen_batch(sequences) -> list[ScreeningResult | ScreeningError]` of equal length, in input order, with `ScreeningError.partial: bool`. Orchestrator never aggregates errors into a `clear`. |
| 10 | `SynthesisVendorAdapter.estimate_cost` needs product type, scale, cloning option, currency, quote date — sequence alone is insufficient. | Accept. | Method signature: `estimate_cost(sequence, *, product_type, scale, cloning_option, currency, quote_date_utc) -> CostEstimate`. |
| 11 | Primer design should expose salt/chemistry model, nearest-neighbor method, target product, and modification handling. | Accept. | `PrimerDesigner` interface accepts `PrimerDesignParameters(nn_method, salt_model, mg_conc, dntp_conc, target_product_concentration, modifications, ...)`. |
| 12 | Architecture does not define positive / negative / process controls as first-class design outputs. | Accept. | Add `engine.controls` module producing `ControlSet(positive, negative, process, library_specific)` as a first-class output bundled into the project ZIP. Each control has its own design rationale and verification readout. |
| 13 | MS2/VLP-specific validation rules absent despite v2.0 KB §17. | Accept. | Add rule family `MS-*` to `catalogues/rules/MS.yaml`: pac-hairpin presence + copy number, AB-loop insertion size cap, SCP-linker integrity, capsid/cargo separation, replication-function exclusion. Predicates registered in `engine.validation`. |
| 14 | The state machine's `SOFT-WARN → DRAFT` after user-ack is ambiguous. | Accept. | New states: `ACKNOWLEDGED_WARN` (user has acked all soft warnings, may proceed to compile) and `READY_WITH_WARNINGS` (compiled with warnings preserved in metadata). Update §4.4 diagram. |
| 15 | Distinguish "block compilation", "block export", "block vendor submission", "block operational protocol" — different safety gates. | Accept (and ties to C1 / M5). | Define four typed gates: `BlockCompile`, `BlockExport`, `BlockVendorSubmission`, `BlockOperationalProtocol`. Each rule declares which gate(s) its HARD severity triggers. The state machine routes accordingly. |

---

## 4. Findings tally and overall verdict

| Severity | Findings | Accepted | Defended | Partially accepted |
|---|---|---|---|---|
| Critical (C1 – C6) | 6 | 6 | 0 | 0 |
| Major (M1 – M10) | 10 | 10 | 0 | 0 |
| Moderate | 15 | 15 | 0 | 0 |
| **Total** | **31** | **31** | **0** | **0** |

Codex's audit was entirely fair. v1.0 was strong in *concept and direction* but weak in *type-level rigour and safety-policy separation*. v1.1 (companion file `ARCHITECTURE.md`) addresses every accepted finding. The original Round-1-through-Round-4 sign-offs stand as evidence that the conceptual direction is sound; the v1.1 upgrade is the structural honesty that v1.0's narrative already promised.

---

## 5. Hand-off — what the v1.1 architecture changes for downstream phases

Most phases in `ROADMAP.md` are unaffected in scope; several are tightened.

| Phase | Change vs ROADMAP v1.0 |
|---|---|
| **Phase 2 (scaffold)** | Must scaffold the *v1.1* type set (`SequenceRecord`, `Location`, `Feature`, `ConstructGraph`, `HostContext`, `CodingSequenceDesign`, `DerivationEnvironment`, typed `DomainEvent` subclasses, typed `AssemblyPlan` subclasses). The Phase 2 stub catalogue is unchanged in shape but expanded in scope. |
| **Phase 3 (domain model + SBOL round-trip)** | Now must round-trip *coordinate-and-graph* annotation, including circular topology and reverse-strand features. SBOL terminology aligns to SBOL 3.1.x. |
| **Phase 4 (catalogues)** | Now includes per-catalogue maintenance metadata; vendor and screening profiles use monthly review cadence; rule manifests use the expanded `ValidationRule` schema; `MS.yaml` added. |
| **Phase 5 (validation engine)** | Engine becomes pure; metric computation moves into `app.validation_orchestrator`. DAG is over `(field, metric)` pairs. |
| **Phase 6 (biology back-ends)** | Adapter contracts unchanged in shape; manifests now declare measured-typical / measured-max latency. |
| **Phase 7 (codon optimiser + assembly + primers)** | Codon optimiser accepts `CodingSequenceDesign`; primer designer accepts `PrimerDesignParameters`; assembly strategies emit typed `AssemblyPlan` subclasses. |
| **Phase 8 (protocol generator)** | **Now two engines:** `engine.design_plan` (always renderable) and `engine.sop_protocol` (gated, optional). `engine.controls` is new. |
| **Phase 9 (sequence I/O)** | UR-01a (file-watch round-trip) is the MUST; UR-01b (live API) deferred to Phase 12 as SHOULD. |
| **Phase 10 (vendor + screening)** | Screening verdict enum is expanded; vendor `estimate_cost` and `screen_batch` signatures updated. |
| **Phase 11 (CLI + API)** | Unchanged in shape; minor command renames (`list_sessions`). |
| **Phase 12 (UI)** | UR-01b live SnapGene channel implemented if API available; falls back to UR-01a otherwise. |
| **Phase 13 (UAT)** | Same acceptance tests; new fixtures for MS-* rules, controls, SOP-linked protocol gates, and screening fallback verdicts. |

`ROADMAP.md` is regenerated to reflect these. The Phase 2 brief in particular is updated to require v1.1 types from the start.

---

## 6. Sign-off

**`/scientific-advisor`:** "Every biological observation in the audit is correct. The split between design realisation plan and SOP-linked operational protocol resolves the long-standing scope contradiction between v2.0 KB and the requirements. The coordinate-and-graph data model, the role-keyed host context, and the explicit MS-* rule family bring the biology into the type system where it belongs. Approved for v1.1."

**`/architect`:** "Every architectural observation is correct. v1.0 had a clear narrative and an under-specified schema; v1.1 closes the gap. The pure-validation-engine boundary, the typed event stream, the `DerivationEnvironment` hash, and the typed `AssemblyPlan` subclasses bring the type system into a state that can survive Phase 2 hardening. Approved for v1.1."

**`/dev-orchestrator`:** "Every operational observation is correct. The two-tier performance budget, the four safety gates, the catalogue maintenance metadata, the source-grade citation gate, and the deterministic-fake-vs-production-adapter separation make CI gates meaningful. Approved for v1.1."

The audit served its purpose. The v1.1 architecture is the new authoritative blueprint; this response document is the audit trail that justifies every change.

---

*End of ARCHITECTURE_Audit_Response.md.*
