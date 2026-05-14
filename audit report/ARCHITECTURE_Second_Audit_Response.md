# Response to Codex's Second Audit of ARCHITECTURE.md (v1.3 → v1.4)

**Document type:** Audit-response and adjudication record.
**Date:** 2026-05-14.
**Audit reviewed:** `audit report/ARCHITECTURE_Second_Audit_Report_v1_2.md` (Codex, second pass against ARCHITECTURE.md v1.3).
**Respondents:** `/architect`, `/scientific-advisor`, `/dev-orchestrator` — the three internal roles that produced and signed off v1.0 → v1.3, plus explicit sponsor instructions on B1 (accept) and B3 (defend with mitigation).
**Companion deliverable:** `ARCHITECTURE.md` v1.4 (binding) — the upgraded blueprint incorporating every accepted correction; `REQUIREMENTS.md` harmonised to v1.4 (B1); `ROADMAP.md` regenerated from v1.4.
**Result tally:** **11 / 12 blocking accepted, 1 defended (B3); 13 / 13 major accepted; 8 / 8 moderate accepted. Total: 31 / 32 accepted, 1 defended.**

---

## 0. Method

Each finding was processed through the three-role adversarial protocol used in the first audit (`audit report/ARCHITECTURE_Audit_Response.md`), with two operating rules:

1. **Defend only when defensible** — and only with the project sponsor's explicit instruction or a citation-grade justification.
2. **Every accepted finding produces a concrete v1.4 change action** — specific enough that the next phase can act on it without re-litigating.

Per-finding format: **Finding restated → three-role assessment → verdict → v1.4 change action.**

The sponsor provided explicit instructions on two findings:
- **B1** — *accept*: harmonise `REQUIREMENTS.md` to the architecture's safety partitioning.
- **B3** — *defend*: Administrator-only completion remains acceptable for this system because the platform handles **DNA sequence design only**, not high-risk biological agents, pathogens, or viral systems directly. The proposed mitigation is a **biosafety-classification and warning advisory layer** in the internal database that auto-flags high-risk elements, elevated-biosafety sequences, and constructs that may require institutional approval — helping non-expert administrators make informed decisions when granting user permissions. See §1 B3 below for the full defense and the v1.4 implementation specification.

---

## 1. Blocking findings (B1 – B12)

### B1. Requirements still contradict the architecture's safety partitioning

**Codex finding.** Requirements still mandate full executable wet-lab protocol generation as a baseline output; architecture says operational SOP is gated. Implementers cannot know which document is binding.

**`/scientific-advisor`:** Conceded. The requirements were drafted before v1.1's split between `DesignRealisationPlan` and `SopLinkedProtocol`. The cross-document inconsistency is real and creates a governance contradiction.

**`/architect`:** Conceded. The architecture is the binding contract; requirements must be harmonised to it, not vice versa.

**`/dev-orchestrator`:** Conceded. Test writers cannot encode safe behaviour while the documents disagree.

> **Sponsor instruction.** Accept. Architecture is binding; requirements should be revised and harmonised to align with the finalised safety-partitioning model.

**Verdict.** **Accept. No defense.**

**v1.4 change action.**

- `REQUIREMENTS.md`:
  - FR-PROTO-01 … FR-PROTO-20 split into two families:
    - **FR-PROTO-DESIGN-01 … FR-PROTO-DESIGN-N** (MUST): the deterministic, non-operational `DesignRealisationPlan` — assembly route, fragment inputs, QC checkpoints, expected verification artefacts, institutional-approval-required list, biosafety classification, reviewer-packet summary.
    - **FR-PROTO-SOP-01 … FR-PROTO-SOP-N** (SHOULD, gated): the operational `SopLinkedProtocol` — bound to administrator-approved institutional SOP templates; renders only when authorisation gates pass after screening completes.
  - Acceptance criteria (AC-01 / AC-02 / AC-03) rewritten so wet-lab execution success is **not** a software release criterion (cf. M8). Replaced with: in-silico checks, expert review, optional dry-run execution by trained users.
- `ROADMAP.md` Phase 8 / Phase 13 split accordingly.
- ARCHITECTURE.md v1.4 §1 Objective 8 retained; v1.4 traceability appendix (cf. M13) maps each accepted finding to the exact files / sections / tests changed.

---

### B2. SOP generation occurs before screening in the data flow

**Codex finding.** v1.3 §4.3 data flow shows compile producing `engine.sop_protocol?` *before* screening. This means an operational SOP can be constructed before the screening verdict is known — preview / cache / log surfaces could leak operational details for sequences that later screen as `HIT` / `WATCHLIST` / `UNAVAILABLE` / `MANUAL_REVIEW_REQUIRED`.

**`/scientific-advisor`:** Conceded — and dangerous. Screening must be *upstream* of operational rendering, not a downstream gate. Even a momentary in-memory rendering of an operational SOP for a `HIT`-class sequence is a data-exposure event.

**`/architect`:** Conceded. The compile step should produce only non-operational artefacts; SOP rendering moves strictly downstream of both screening completion and authorisation.

**`/dev-orchestrator`:** Conceded. State machine and event model both need re-sequencing.

**Verdict.** **Accept. No defense.**

**v1.4 change action.** Re-sequence the pipeline:

```
   Compile         → produces { ConstructGraph, ValidationReport,
                                DesignRealisationPlan, ControlSet,
                                ScreeningRequestPackage,
                                RiskAdvisoryReport }
                     emits DesignCompiled event
                     (NO operational SOP)
   Screening       → adapter.screening pipeline against full
                     assembled construct (not just fragments)
                     emits ScreeningCompleted event
   Authorisation   → app.authorisation_decision (gates against
                     AuthorisationProfile + RiskAdvisoryReport)
                     emits OperationalProtocolAuthorised event
                     (only when gates pass)
   SOP render      → engine.sop_protocol renders SopLinkedProtocol
                     ONLY after OperationalProtocolAuthorised
                     emits SopRendered event
   Export          → app.export_orchestrator emits Exported event
```

State machine new states between `COMPILING` and `EXPORTED`: `AWAITING_SCREENING` → `AWAITING_AUTHORISATION` → `AWAITING_SOP_RENDER` (only when SOP requested) → `READY_TO_EXPORT`. Failed branches: `BLOCKED_BY_HIT`, `BLOCKED_BY_POLICY`, `AWAITING_REVIEWER_SIGNOFF` (for `WATCHLIST` / `MANUAL_REVIEW_REQUIRED`), `BLOCKED_BY_UNAVAILABLE_SCREENING`. v1.4 §4.4 contains the explicit transition diagram (cf. B12 below).

---

### B3. Administrator-only completion undermines dual sign-off

**Codex finding.** v1.3's `Administrator ⊇ Reviewer` collapses authorisation + review + release into one actor. Codex demands policy-controlled dual-control flags (`requires_independent_reviewer`, `requires_biosafety_officer`, `requires_second_admin`, `requires_signed_institutional_approval`) and conflict-of-interest separation.

**`/scientific-advisor`:** I am inclined to side with Codex on the principle — dual sign-off is the standard for high-risk wet-lab work. However, the sponsor's defense rests on an important scope claim: this platform **designs DNA sequences**; it does not directly manipulate physical biological agents, pathogens, or viral systems. The biosafety risk is *informational* (could the design be misused?) rather than directly biological. The IGSC / IBBIS / SecureDNA screening hook already covers the misuse pathway at the canonical industry standard. With the proposed `BiosafetyClassificationLayer` advisory mitigation in place, an Administrator becomes an *informed* decision-maker rather than an *unaided* one. Accept the sponsor's defense.

**`/architect`:** The sponsor's framing is consistent with the platform's scope. v1.4 implements the advisory layer cleanly; dual-control policy support remains as a *future enhancement* for institutions that require it (it is not removed from the design space, just not mandated in v1.4). Accept the sponsor's position.

**`/dev-orchestrator`:** The proposed advisory layer is straightforward to implement and adds defence-in-depth without forcing every institution to maintain a dual-control workflow that may be impractical for BSL-1 / BSL-2 routine work. Accept the defense with the mitigation.

> **Sponsor instruction.** Defend. The platform handles DNA sequence design only; high-biosafety dual sign-off procedures are not inherently required. Mitigation: integrate a biosafety-classification and warning layer into the system's internal database that auto-flags high-risk genetic elements, sequences associated with elevated biosafety levels, and constructs that may require institutional approval. This helps non-expert administrators make informed decisions when granting permissions, especially for designs that involve sequences or workflows associated with higher biosafety classifications.

**Verdict.** **Defended with mitigation (the only finding defended in this audit pass).**

**v1.4 mitigation specification — `BiosafetyClassificationLayer` (advisory).**

A new advisory subsystem added to the domain core:

1. **`engine.risk_classification`** — pure module that scans a construct graph against a curated `RiskAdvisoryCatalogue` and produces a `RiskAdvisoryReport`.

   ```python
   def classify_risk(
       construct: Construct,
       catalogue: RiskAdvisoryCatalogue,
   ) -> RiskAdvisoryReport: ...
   ```

2. **`RiskAdvisoryCatalogue`** (new YAML in `catalogues/risk_advisories.yaml`, maintained by `/scientific-advisor`) — a curated, citation-graded list of:
   - **High-risk genetic elements**: oncogenes, toxin coding sequences, virulence factors, certain immune modulators, antibiotic-resistance genes on the WHO highest-priority list, certain regulatory motifs.
   - **Sequences associated with elevated biosafety levels**: pathogen-derived components (mapped to RG-2 / RG-3 / RG-4), broad-host-range origins, mobilisable elements, integrating viral elements, replication-competent viral cassettes, gene-drive components.
   - **Constructs that may require institutional approval**: replication-competent viral systems, AAV / lentivirus production designs, transposon-based stable lines, plant-delivery cargo with regulated traits, environmental-release designs, GMP / clinical / therapeutic constructs.

3. **`RiskAdvisoryReport`** — structured advisory output:

   ```python
   @dataclass(frozen=True)
   class RiskAdvisoryReport:
       construct_id: ConstructId
       construct_checksum: Sha256
       advisories: tuple[RiskAdvisory, ...]
       overall_recommendation: Literal[
           "no_concerns",
           "informational",
           "consider_institutional_approval",
           "strongly_recommend_institutional_approval",
       ]
       generated_at: Timestamp
       catalogue_version: Semver
       catalogue_content_hash: Sha256

   @dataclass(frozen=True)
   class RiskAdvisory:
       category: AdvisoryCategory       # high_risk_element | elevated_bsl | requires_approval
       matched_feature: FeatureRef
       severity: Literal["info", "caution", "strong_caution"]
       description: str                  # plain-English description for the administrator
       citation: GradedCitation          # PMID/DOI/regulatory citation
       suggested_action: str             # "Consider requesting biosafety officer review"
   ```

4. **Integration with the authorisation workflow.**

   - The compile step produces a `RiskAdvisoryReport` alongside the `DesignRealisationPlan`.
   - When an Administrator reviews a user's authorisation request **and** when the user submits a compile for SOP rendering, the `RiskAdvisoryReport` is surfaced prominently in the admin UI / CLI.
   - The advisory report **does not** automatically block; it informs.
   - For advisories classified `strongly_recommend_institutional_approval`, the system surfaces an explicit acknowledgement prompt to the Administrator that they have reviewed the advisory before granting / extending authorisation.
   - The Administrator's acknowledgement (or sign-off) is recorded in the audit log with the advisory's citation chain.

5. **Forward-compatibility with dual-control.** v1.4 also defines the *data model* for dual-control flags (`requires_independent_reviewer`, `requires_biosafety_officer`, `requires_second_admin`, `requires_signed_institutional_approval`) inside `AuthorisationProfile` and `PolicyContext`, but the runtime enforcement is *opt-in* per institutional policy. The default policy for v1.4 is single-Administrator with advisory; institutions that require dual sign-off can configure their policy to enforce the dual-control flags via an `InstitutionalPolicy` object. This preserves the v1.3 single-Administrator workflow while leaving room for institutions that require stricter governance to enable it without an architecture change.

**Verdict justification.** This defense rests on a clear scope claim (DNA sequence design only, not direct biological manipulation), supplemented by an explicit advisory mitigation that informs the Administrator's decision-making. It does not weaken the security boundary established in v1.2: profile mutation still requires `AdminPrincipal` / `DeveloperPrincipal`; users still cannot self-elevate. It simply does not *mandate* dual sign-off for every workflow when the sponsor judges single-Administrator-with-advisory sufficient for the platform's scope. Institutions with stricter requirements may enable dual-control via `InstitutionalPolicy` without an architectural change.

> **Sponsor strengthening (v1.5, 2026-05-14).** The B3 mitigation is sharpened: **warnings must be active, auditable, and tied to the design record; the Administrator must receive an explicit warning; the approval trace must be logged. The system must not rely on passive UI warnings.** v1.5 of ARCHITECTURE.md implements this as: (a) the `RiskAdvisoryReport` is bound to the design session and to the construct version by content hash; (b) presenting an advisory to the Administrator emits a typed `AdvisoryWarningPresented` governance event (a passive UI render alone is not sufficient — the presentation is a logged action); (c) acknowledgement of any advisory of severity `caution` or `strong_caution` is **mandatory before** the `OperationalProtocolAuthorised` event can fire and is a typed action requiring justification text + cryptographic signature, recorded as a `RiskAdvisoryAcknowledged` event with a full signed `DecisionRecord`; (d) the full approval trace — every advisory presented, every acknowledgement / decline / escalation, every authorisation decision — is persisted in the immutable governance event stream and replayed deterministically from the audit log; (e) a new CI gate `no-passive-advisory-bypass-check` statically asserts that the authorisation pipeline cannot advance to `OperationalProtocolAuthorised` without observing the corresponding `RiskAdvisoryAcknowledged` events; (f) the UI never offers a "dismiss without action" affordance on advisory warnings — the only paths are *acknowledge with justification*, *decline (route to alternative reviewer / dual-control)*, or *escalate (require institutional sign-off)*; (g) declines and escalations are themselves first-class governance events; (h) the new R-21 risk-register entry tracks "advisory bypass" with five concrete mitigations.

---

### B4. Authorisation coverage is biologically under-scoped

**Codex finding.** `AuthorisationProfile` covers role, host classes, biosafety tiers, assembly chemistries, downstream uses, SOP libraries — but not cargo risk classes, vector system classes, replication competence, insert size, host *role*, screening verdict class, target organism, institutional protocol IDs, jurisdictional constraints, component lineage.

**`/scientific-advisor`:** Conceded. A profile authorising "mammalian cell culture + BSL-2" does not legitimately authorise a lentiviral-oncogene construct, an AAV helper plasmid, a toxin fragment, or a construct with a restricted marker. The profile must be artifact-specific.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.** Expand `AuthorisationProfile` and introduce `CoveredBiologicalScope`:

```python
@dataclass(frozen=True)
class CoveredBiologicalScope:
    covered_biosafety_tiers: frozenset[BiosafetyTier]
    covered_host_classes: frozenset[ChassisClass]
    covered_host_roles: frozenset[HostRole]                 # NEW — per host-context role
    covered_assembly_chemistries: frozenset[AssemblyMethodId]
    covered_downstream_uses: frozenset[DownstreamUse]
    covered_sop_libraries: frozenset[SopLibraryId]
    covered_vector_classes: frozenset[VectorSystemClass]    # NEW — plasmid, integrating-viral,
                                                            #       non-integrating-viral, transposon,
                                                            #       phagemid, VLP, minicircle,
                                                            #       BAC/YAC, Agrobacterium-binary
    covered_cargo_classes: frozenset[CargoClass]            # NEW — toxin, virulence factor,
                                                            #       oncogene, cytokine, immune
                                                            #       modulator, antibiotic-resistance
                                                            #       marker, selectable marker,
                                                            #       reporter, regulatory element,
                                                            #       structural/native ORF
    covered_replication_competence: frozenset[ReplicationCompetenceClass]  # NEW
    max_insert_size_bp: int | None                          # NEW
    max_copy_number: int | None                             # NEW
    covered_target_organisms: frozenset[TargetOrganism] | None    # NEW — cell-line / species
    covered_screening_exception_classes: frozenset[ScreeningExceptionClass]  # NEW
    institutional_protocol_ids: tuple[InstitutionalProtocolId, ...]    # NEW
    institutional_approval_scope: ApprovalScope             # NEW
    jurisdictional_constraints: tuple[JurisdictionConstraint, ...]    # NEW — e.g., EU GMO, US APHIS
    component_lineage_trust: ComponentLineageTrustLevel     # NEW — public-vetted / institutional / private

@dataclass(frozen=True)
class AuthorisationProfile:
    profile_id: AuthProfileId
    profile_content_hash: Sha256                            # NEW — canonical hash for decision binding
    user_id: UserId
    granted_by_admin_id: AdminId
    granted_at: Timestamp
    profile_valid_from: Timestamp
    profile_valid_until: Timestamp
    revoked_at: Timestamp | None
    revocation_reason: str | None
    scope: CoveredBiologicalScope                           # MOVED into a typed scope object

    role_of_operation_allowed: frozenset[OperationalRole]   # (renamed; cf. M6)
    covered_export_classes: frozenset[ExportClass]
    covered_vendor_submission: bool

    # Dual-control hooks (data only; runtime enforcement opt-in per InstitutionalPolicy)
    dual_control_flags: DualControlFlags                    # NEW (cf. B3 forward-compat)

    additional_constraints: tuple[AuthorisationConstraint, ...]
    signature: ProfileSignature
```

Every authorisation decision now produces a `DecisionRecord` (cf. B9 below) with `authorisation_profile_id`, `profile_content_hash`, `institutional_approval_id`, `decision_id`, `decision_timestamp`, `decision_policy_version`.

---

### B5. Sequence I/O contracts lose annotation and graph

**Codex finding.** `SequenceReader.read() -> SequenceRecord` and `SequenceWriter.write(record: SequenceRecord, ...) -> bytes` — `SequenceRecord` is sequence + minimal metadata; it cannot carry the full feature table, construct graph, primer annotations, SnapGene visual metadata, or structured qualifiers. The importer has nowhere to put annotations; the exporter cannot reconstruct the original file.

**`/scientific-advisor`:** Conceded — this is the round-trip blocker.

**`/architect`:** Conceded. The signatures must move annotated artefacts.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.**

```python
class SequenceReader(Protocol):
    formats: list[Format]
    def read(self, source: bytes | Path, fmt: Format) -> ImportedConstruct: ...

class SequenceWriter(Protocol):
    formats: list[Format]
    def write(self, construct: AnnotatedConstruct, fmt: Format) -> WriteResult: ...

@dataclass(frozen=True)
class ImportedConstruct:
    sequence_record: SequenceRecord
    feature_table: tuple[Feature, ...]
    structured_qualifiers: tuple[Qualifier, ...]
    construct_graph: ConstructGraph
    sbol_mapping: SbolMapping | None
    snapgene_visual_metadata: SnapGeneVisualMetadata | None
    source_format_metadata: SourceFormatMetadata
    primer_annotations: tuple[PrimerAnnotation, ...]
    lossy_conversion_warnings: tuple[LossWarning, ...]

@dataclass(frozen=True)
class AnnotatedConstruct(ImportedConstruct):
    """Same shape as ImportedConstruct; semantically: ready-to-write."""

@dataclass(frozen=True)
class WriteResult:
    bytes_emitted: bytes
    lossy_warnings: tuple[LossWarning, ...]                # warns when round-trip is not byte-identical
    canonical_hash: Sha256
```

Byte-identical round-trip relaxed to **semantic equivalence** for GenBank / SBOL / SnapGene (cf. M8); a canonical-writer mode is available for tests that require byte-identical output, with documented format-specific normalisation.

---

### B6. Feature qualifier model too weak

**Codex finding.** `Feature.qualifiers: dict[str, str]` cannot represent repeated keys, ordered qualifiers, structured values, evidence, cross-references, translations, codon-start, notes from different namespaces, display colours/labels, ontology terms, fuzzy locations, joined locations, complemented locations, nested/compound features.

**`/scientific-advisor`:** Conceded. Real GenBank / SBOL / SnapGene annotations are repeated and ordered; a flat dict loses information on read.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.**

```python
@dataclass(frozen=True)
class Qualifier:
    namespace: str               # e.g., "GenBank", "SBOL", "SnapGene"
    key: str
    value: str | StructuredValue
    value_type: Literal["string", "boolean", "integer", "float", "url", "ontology_term", "structured"]
    order: int                   # preserves original ordering in source format
    provenance: Provenance | None

@dataclass(frozen=True)
class Feature:
    role: SequenceOntologyTerm
    qualifiers: tuple[Qualifier, ...]    # was: dict[str, str]
    locations: tuple[Location, ...]
    parent_sequence_id: SequenceRecordId
    evidence: tuple[GradedCitation, ...]
    sub_features: tuple["Feature", ...]  # NEW — nested / compound
```

`Location` extended (cf. M3): formal location algebra with fuzzy bounds, between-base locations, join vs. order semantics, complement semantics for compound locations, remote locations, partial-feature flags, sequence-length invariant.

---

### B7. Domain purity still violated by adapter-named dependencies

**Codex finding.** v1.3 says domain core / engines are pure, but `engine.sequence_analysis` *names* `adapter.catalogue.EnzymeCatalogue` as its dependency. A port is acceptable; an adapter module dependency is not.

**`/architect`:** Conceded. v1.3 used the adapter namespace as a proxy for the port. v1.4 separates them.

**`/scientific-advisor`:** Conceded.

**`/dev-orchestrator`:** Conceded. CI gate `no-domain-impurity-check` needs to be tightened.

**Verdict.** **Accept. No defense.**

**v1.4 change action.**

- New top-level package `domain.ports/` holding *all* port (interface) definitions. The engine layer depends only on `domain.types` and `domain.ports`.
- `adapter.*` packages hold *implementations*. They depend on `domain.ports` and external libraries.
- CI gate `no-domain-impurity-check` upgraded with an explicit `import-linter` contract:
  - `domain.*` may import: `domain.*`, `domain.ports.*`.
  - `engine.*` may import: `domain.*`, `domain.ports.*`.
  - `engine.*` may NOT import: `adapter.*`, `app.*`, `interface.*`.
  - `app.*` may import: `domain.*`, `domain.ports.*`, `engine.*` (but not specific adapters).
  - `adapter.*` may import: `domain.ports.*`, `domain.types`, plus external libraries.
- `engine.sequence_analysis` declares its dependency on `domain.ports.EnzymeCataloguePort` (was `adapter.catalogue.EnzymeCatalogue`).

---

### B8. Authorisation store type model inconsistent

**Codex finding.** Permissions matrix says Developer can bootstrap admin authority; `AuthorisationStore.write_mint` accepts only `AdminPrincipal`. `DomainEvent.actor: UserId`, but admin actions are governance events not session-bound design events.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded. Split events and ports.

**`/scientific-advisor`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.**

- **Split principal identity from user identity.** Introduce `PrincipalId` as distinct from `UserId`. A `UserPrincipal` has both a `PrincipalId` (security identity) and a `UserId` (the design-session actor identity). `AdminPrincipal` / `DeveloperPrincipal` have only `PrincipalId`.
- **Split authorisation port.**
  ```python
  class AuthorisationReadPort(Protocol):
      def get(self, user_id: UserId) -> AuthorisationProfile: ...
      def read_own_profile(self, principal: Principal) -> AuthorisationProfile: ...
      def list_for_admin(self, admin: AdminPrincipal, query: AuthQuery) -> list[AuthorisationProfileSummary]: ...

  class AuthorisationAdminWritePort(Protocol):
      def mint(self, admin: AdminPrincipal, target_user: UserId,
               profile: AuthorisationProfile, justification: str) -> AdminActionId: ...
      def modify(self, admin: AdminPrincipal, target_user: UserId,
                 diff: AuthorisationProfileDiff, justification: str) -> AdminActionId: ...
      def revoke(self, admin: AdminPrincipal, target_user: UserId,
                 reason: RevocationReason) -> AdminActionId: ...

  class AuthorisationBootstrapPort(Protocol):
      """Used once, at deployment, by DeveloperPrincipal to mint the first AdminPrincipal."""
      def bootstrap_first_admin(self, developer: DeveloperPrincipal,
                                target: AdminBootstrapRecord) -> AdminActionId: ...
  ```
- **Split events into typed governance and design streams** (cf. M12):
  - `DesignEvent` (session-bound): `SessionStarted`, `PartAdded`, `Compiled`, `DesignCompiled`, `ScreeningCompleted`, `OperationalProtocolAuthorised`, `SopRendered`, `Exported`, etc.
  - `GovernanceEvent` (institutional, no session binding): `AdminActionMinted`, `AdminActionModified`, `AdminActionRevoked`, `AdminBootstrapped`, `InstitutionalPolicyUpdated`, `ReviewerSignedOff`, `AuthorisationAttemptDenied`, `PluginManifestApproved`.
  - `ExportEvent` (artifact release): `BundleEmitted`, `VendorSubmissionPrepared`.
- DomainEvent renamed to a base class; both `DesignEvent` and `GovernanceEvent` inherit. `actor` field type-specific.

---

### B9. Reviewer / Admin sign-off not cryptographically or semantically bound

**Codex finding.** `ReviewerSignedOff` includes signer_id and signer_role, but cannot prove that the signer held the role at signing time under the correct policy and profile version. After role revocation, historical replay may be wrong.

**`/scientific-advisor`:** Conceded.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.**

```python
@dataclass(frozen=True)
class DecisionRecord:
    """Signed, immutable, replay-safe."""
    decision_id: DecisionId
    principal_id: PrincipalId
    role_asserted: SecurityRole
    role_held_at_decision: bool                # verified at signing
    authorisation_profile_id: AuthProfileId | None
    profile_content_hash: Sha256 | None
    policy_version: Semver
    institutional_approval_id: InstitutionalApprovalId | None
    decision_scope_hash: Sha256                # hash of the artifact + scope at decision time
    decision_kind: Literal[
        "reviewer_signoff",
        "watchlist_override",
        "manual_review_signoff",
        "authorisation_mint",
        "authorisation_modify",
        "authorisation_revoke",
        "screening_exception",
        "advisory_acknowledgement",
    ]
    decision_payload: dict                     # decision-kind-specific
    signature: CryptographicSignature
    key_id: KeyId
    timestamp: Timestamp

class ReviewerSignedOff(GovernanceEvent):
    decision_record: DecisionRecord

# Role snapshots are persisted for replay (an immutable profile version
# at the time of each decision):
@dataclass(frozen=True)
class RoleSnapshot:
    principal_id: PrincipalId
    role_held: SecurityRole
    snapshot_at: Timestamp
    snapshot_signature: CryptographicSignature
```

Every decision freezes the active profile version + policy version in the `DecisionRecord`; replays look up the snapshot rather than the live profile.

---

### B10. Screening trust model too weak

**Codex finding.** `ScreeningAdapter.canonical: bool` is plugin-self-declared. `NOT_APPLICABLE` is a loophole unless policy gates it. Screening should be at assembled-product level, not just fragment level.

**`/scientific-advisor`:** Conceded — a fragment-only screen can miss an assembled hit.

**`/architect`:** Conceded — adapter trust is an institutional registry concern.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.**

```python
@dataclass(frozen=True)
class ScreeningProviderTrustPolicy:
    provider_id: ScreeningProviderId
    provider_type: Literal[
        "igsc_canonical",       # IGSC v3.x compliant
        "ibbis_common_mechanism",
        "secureDNA",
        "internal_blacklist",
        "vendor_screening",
        "advisory_only",
    ]
    approved_use: frozenset[ScreeningUseClass]  # what verdicts this provider is trusted to issue
    canonical_for: frozenset[ScreeningScope]    # at what scopes this provider issues canonical verdicts
    policy_version: Semver
    approved_by_admin: AdminId
    approved_at: Timestamp
    valid_until: Timestamp
```

- `ScreeningAdapter.canonical: bool` removed. Trust is determined by the institution's `ScreeningProviderTrustPolicy` at decision time.
- Screening is run at the **assembled-product** level by default. Fragment-level screening is permitted only when the assembled-product result is also `CLEAR` or when policy allows fragment-only screening for a defined `ScreeningScope`.
- `ScreeningVerdict.NOT_APPLICABLE` requires a structured `NotApplicableReason` (one of: `below_threshold_per_policy`, `non_pathogen_origin_per_policy`, `tools_workflow_per_policy`) + an audit trail. The pure default policy treats every assembled construct as in-scope.

---

### B11. DerivationEnvironment incomplete for replay

**Codex finding.** Missing: authorisation profile IDs + content hashes, SOP template content hashes (not just versions), screening provider trust policy version, screening query scope and threshold policy, exact assembled sequence submitted to screening, plugin package hashes, LLM prompt template versions and model identifiers, institutional policy version, user declaration hash, export profile and redaction policy.

**`/scientific-advisor`:** Conceded.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.** Expand `DerivationEnvironment` accordingly:

```python
@dataclass(frozen=True)
class DerivationEnvironment:
    # ... v1.3 fields retained ...
    authorisation_profile_id: AuthProfileId | None
    authorisation_profile_content_hash: Sha256 | None
    sop_template_content_hashes: dict[SopTemplateId, Sha256]   # NEW — not just versions
    screening_provider_trust_policy_version: Semver
    screening_query_scope: ScreeningScope
    screening_threshold_policy_version: Semver
    screening_submitted_sequence_hash: Sha256                  # exact assembled sequence
    plugin_package_hashes: dict[PluginId, Sha256]
    llm_prompt_template_versions: dict[PromptTemplateId, Semver]
    llm_model_identifiers: dict[LLMUseSite, LLMModelIdentifier]
    institutional_policy_version: Semver
    user_declaration_hash: Sha256
    export_profile: ExportProfileId
    redaction_policy_version: Semver
    risk_advisory_catalogue_version: Semver                    # NEW (B3 mitigation)
    risk_advisory_catalogue_content_hash: Sha256               # NEW (B3 mitigation)
    privacy_classification: PrivacyClassification              # PII / institutional / public

    def canonical_json(self) -> bytes: ...
    def hash(self) -> Sha256: ...
```

---

### B12. State machine paths after Watchlist / Manual Review underspecified

**Codex finding.** Transitions after reviewer sign-off remain underspecified.

**`/scientific-advisor`:** Conceded.

**`/architect`:** Conceded.

**`/dev-orchestrator`:** Conceded.

**Verdict.** **Accept. No defense.**

**v1.4 change action.** Explicit transitions:

```
   ScreeningWatchlist           → AwaitingReview → ReviewSignedOff(decision_kind=watchlist_override)
                                  → AuthorisationGate
                                  → ExportEligible (if all auth gates pass)

   ScreeningUnavailable         → AwaitingReview → (a) ReviewSignedOff(decision_kind=screening_exception)
                                                       → AuthorisationGate
                                                       → ExportEligible (only when policy explicitly permits)
                                                   (b) PolicyBlocked → terminal

   ScreeningManualReviewRequired → AwaitingReview → ReviewSignedOff(decision_kind=manual_review_signoff)
                                                    → AuthorisationGate
                                                    → ExportEligible

   ScreeningHit                 → Blocked terminal. No ordinary override.
                                  Override requires policy-controlled exception
                                  with dual sign-off recorded explicitly.

   ScreeningNotApplicable       → requires structured NotApplicableReason
                                  → AuthorisationGate
                                  → ExportEligible
```

Each transition is bound to an `AuthorisationPolicy` and produces a `DecisionRecord`. v1.4 §4.4 contains the full state diagram.

---

## 2. Major findings (M1 – M13) — all accepted

| ID | Finding | v1.4 change action |
|---|---|---|
| **M1** | `SynthesisVendorAdapter.check(sequence)` too narrow. | Replace with `check(request: VendorFeasibilityRequest)` carrying product type, scale, backbone, delivery format, host strain, vendor account, regional rules, turnaround target. |
| **M2** | Single `SequenceRecord.checksum` ambiguous. | Introduce five typed hashes: `sequence_hash`, `topology_hash`, `annotation_hash`, `construct_graph_hash`, `export_bundle_hash`. Reverse-complement-equivalence rule defined per artifact type. |
| **M3** | `Location` algebra incomplete. | Add fuzzy bounds, between-base, join-vs-order, complement-for-compound, remote locations, partial-feature flag, sequence-length invariant. Map explicitly to GenBank and SBOL 3.1.x. |
| **M4** | Construct feature duplication (`feature_table` vs graph nodes). | Single source of truth: `ConstructGraph` is canonical; `feature_table` becomes a derived view with a validation invariant (`feature_table == derive_feature_table(graph)`) enforced on every state transition. |
| **M5** | `Part.host_compatibility` too coarse. | Replace single field with `HostCompatibilityConstraints` carrying per-context constraints (propagation / expression / screening / delivery): promoter recognition, codon usage, origin compatibility, marker, toxicity flag, secretion/localisation, intron/splicing behaviour, methylation sensitivity, copy-number, transformation modality. |
| **M6** | `role_of_operation: Role` conflated with security role. | Split: `SecurityRole = {Developer, Administrator, Reviewer, User}`; `OperationalRole = {propagation, expression, producer, target, screening_assay, storage, delivery, assembly, cloning_propagation}`. The user declares `role_of_operation: OperationalRole`. The principal's `role: SecurityRole`. No overlap. |
| **M7** | BSL scope not aligned (no explicit non-support for BSL-4). | Add explicit unsupported-tier behaviour: `BiosafetyTier.BSL4` → hard block at compile time (`BlockCompile`); no SOP rendering; no vendor submission; audit event `UnsupportedBiosafetyTierAttempted`; user-facing reason message. v1.4 §6 adds R-20 for this risk. |
| **M8** | Roadmap acceptance criteria overclaim wet-lab validity. | Replace wet-lab-success criteria with: in-silico checks, expert review, dry-run execution by trained users, optional empirical validation studies outside ordinary CI. Byte-identical GenBank/SBOL round-trip relaxed to semantic equivalence where reorder/normalisation is format-defined. |
| **M9** | MS2 / VLP rules too high-level. | Add `engine.vlp_policy` module + `catalogues/rules/MS.yaml` expanded with explicit packaging-signal handling, capsid-expression context, helper-function separation, cargo-size limits, replication/infectivity boundaries, assembly controls, assay controls, distinction between RNA-binding display systems (MS2), bacteriophage-derived VLPs (Qβ, T7), and mammalian viral vectors (AAV, lentivirus). |
| **M10** | LLM governance incomplete. | Add `AdvisoryTextPolicy` enforcing: prompt template versioning, model/version tracking, citation checking, prohibited-output detection (no operational protocol details from LLM), red-team test suite, deterministic fallback when LLM unavailable, hard separation between LLM-generated advisory text and authoritative computed data. New CI gate `llm-output-policy-check`. |
| **M11** | `ProtocolStep` still in non-gated namespace. | Move all operational protocol types (`ProtocolStep`, `ProtocolDAG`, hazard / quantity / temperature / duration fields) into `domain.types.sop_protected` namespace. By type, `DesignRealisationPlan` cannot contain a `ProtocolStep`; that constraint is enforced by `mypy --strict`. |
| **M12** | Admin audit and event sourcing mixed. | Three append-only streams: `events/design/<session>.jsonl`, `events/governance/<institution>.jsonl`, `events/export/<institution>.jsonl`. Cross-stream linking via immutable `DecisionRecord` IDs and content hashes. |
| **M13** | Response document overstates resolution. | v1.4 audit-response appendix adds a structured traceability table: each accepted finding → exact file + section + tests changed. CI gate `audit-traceability-check` verifies every cited file/section exists. |

---

## 3. Moderate findings (N1 – N8) — all accepted

| ID | Finding | v1.4 change action |
|---|---|---|
| **N1** | Architecture version labels inconsistent. | Normalise all "v1.1" / "v1.2" stragglers to v1.4 where appropriate; preserve historical references where intentional. |
| **N2** | Architecture references non-existent requirement IDs. | All such IDs reconciled: B1 introduces `FR-PROTO-DESIGN-*` / `FR-PROTO-SOP-*`; `UR-08` rephrased into two clauses; appendix traceability validated. |
| **N3** | SBOL terminology mixed across versions. | Define SBOL 3.1.x explicitly with `Component` / `Sequence` / `SequenceFeature` / `Location` terms. Migration map for SBOL-2 (`ComponentDefinition`) imports added to the importer's `lossy_conversion_warnings`. |
| **N4** | Protocol DAG canonicalisation underdefined. | Canonical serialisation rule: topological sort by `step_id` lexicographic key; cycle detection on construction; serialised JSON with sorted keys. |
| **N5** | `ScreeningError` used but not modelled. | Typed taxonomy: `TransientProviderFailure`, `InvalidQuery`, `UnsupportedSequence`, `AmbiguousResult`, `PolicyFailure`, `ProviderUnavailable`. Each carries cause, retry-policy, and audit-event mapping. |
| **N6** | Export redaction policy missing. | Four export profiles: `InternalAudit` (full bundle), `Collaborator` (full minus PII), `Vendor` (sequence + metadata only), `PublicationSupplement` (sequence + design plan + non-confidential metadata). Each has explicit redaction rules and a `redaction_policy_version` field. |
| **N7** | Plugin security under-specified. | Plugin manifest signing; sandboxed execution per plugin manifest's declared permissions; package pinning; denial of network access for deterministic-path plugins; plugin artefact hashes in `DerivationEnvironment`. |
| **N8** | Scientific controls not mechanistically validated. | Control validation rules tied to design intent and host role: positive-control suitability (matched host + matched chemistry + matched cargo class), negative-control absence-of-signal, vehicle/mock controls, replicate-structure recommendation. Added to `engine.controls`. |

---

## 4. Tally and final verdict

| Severity | Total | Accepted | Defended | Comment |
|---|---|---|---|---|
| Blocking (B1 – B12) | 12 | 11 | 1 (B3 with mitigation) | |
| Major (M1 – M13) | 13 | 13 | 0 | |
| Moderate (N1 – N8) | 8 | 8 | 0 | |
| **Total** | **33** | **32** | **1** | All non-defended findings produce concrete v1.4 change actions. |

The sole defended finding is **B3** — per sponsor instruction, the platform's scope (DNA sequence design only, no direct manipulation of physical biological agents) does not inherently require dual sign-off; the proposed advisory `BiosafetyClassificationLayer` provides defence in depth without forcing every institution into a dual-control workflow that is impractical for routine BSL-1 / BSL-2 work. Dual-control data-model hooks are added (`AuthorisationProfile.dual_control_flags`, `InstitutionalPolicy`) so institutions that require stricter governance can enable it without an architectural change.

---

## 5. Traceability table (cf. M13)

Each accepted finding is recorded with the v1.4 artefacts it touches. *(File:Section:Test triples; populated as the v1.4 changes land.)*

| Finding | Files changed | Sections touched | Tests added |
|---|---|---|---|
| B1 | `REQUIREMENTS.md`, `ARCHITECTURE.md`, `ROADMAP.md` | REQUIREMENTS §3.10 + AC; ARCHITECTURE Objective 8; ROADMAP Phases 8/13 | `test_no_operational_steps_in_design_plan`, `test_sop_renders_only_after_gates_pass` |
| B2 | `ARCHITECTURE.md` | §1 objectives; §4.3 data flow; §4.4 state machine; §4.7 events | `test_sop_blocked_before_screening_complete`, `test_compile_emits_no_operational_artefacts` |
| B3 (defended) | `ARCHITECTURE.md`, `catalogues/risk_advisories.yaml` (new), `REQUIREMENTS.md` | §1 objective 9 (advisory mitigation); new §4.4.x risk advisory layer; FR-ADV-* requirements | `test_risk_advisory_surfaces_to_admin`, `test_advisory_acknowledged_in_audit_log` |
| B4 | `ARCHITECTURE.md`, `REQUIREMENTS.md` | §4.6 `AuthorisationProfile` + `CoveredBiologicalScope`; FR-AUTH-* extended | `test_lentiviral_oncogene_not_authorised_by_generic_mammalian_profile` |
| B5 | `ARCHITECTURE.md`, `domain/ports.py` | §4.5 contracts; `ImportedConstruct` / `AnnotatedConstruct` | `test_genbank_roundtrip_preserves_features`, `test_sbol_roundtrip_preserves_graph` |
| B6 | `ARCHITECTURE.md`, `domain/types.py` | §4.6 `Feature`, `Qualifier` | `test_repeated_qualifiers_preserved`, `test_compound_location_roundtrip` |
| B7 | `ARCHITECTURE.md`, `domain/ports/` (new) | §4.1 layer rules; §4.10 import-linter contract | `test_engine_does_not_import_adapter` |
| B8 | `ARCHITECTURE.md` | §4.5 split ports; §4.6 principal/user split; §4.7 event-stream split | `test_developer_bootstrap_path`, `test_admin_actions_not_in_design_event_stream` |
| B9 | `ARCHITECTURE.md` | §4.6 `DecisionRecord`, `RoleSnapshot`; §4.7 governance events | `test_decision_record_signature_verified`, `test_replay_uses_role_snapshot` |
| B10 | `ARCHITECTURE.md`, `catalogues/screening_profiles/*.yaml` | §4.5 trust policy; §4.6 verdict semantics | `test_internal_adapter_not_canonical_for_clear`, `test_screening_on_assembled_product` |
| B11 | `ARCHITECTURE.md` | §4.6 `DerivationEnvironment` | `test_replay_detects_template_change` |
| B12 | `ARCHITECTURE.md` | §4.4 state machine; §4.7 events | per-transition state-machine tests |
| M1 | `ARCHITECTURE.md` | §4.5 `VendorFeasibilityRequest` | `test_vendor_check_uses_full_request` |
| M2 | `ARCHITECTURE.md` | §4.6 multi-hash | `test_separate_hash_types` |
| M3 | `ARCHITECTURE.md` | §4.6 `Location` algebra | location-algebra tests against curated GenBank/SBOL fixtures |
| M4 | `ARCHITECTURE.md` | §4.6 graph-as-canonical | `test_feature_table_is_derived_view` |
| M5 | `ARCHITECTURE.md` | §4.6 `HostCompatibilityConstraints` | per-context compatibility tests |
| M6 | `ARCHITECTURE.md`, `REQUIREMENTS.md` | §4.6 `SecurityRole` / `OperationalRole` split; FR-AUTH-13/14 refined | `test_user_declares_operational_role_not_security_role` |
| M7 | `ARCHITECTURE.md` | §6 R-20; §4.4 BSL-4 block | `test_bsl4_blocked_at_compile` |
| M8 | `ROADMAP.md`, `REQUIREMENTS.md` | AC-01..07 rewritten | software-only release-gate tests |
| M9 | `ARCHITECTURE.md`, `catalogues/rules/MS.yaml`, `engine.vlp_policy` | §4.2 module catalogue; MS.yaml | MS2/VLP policy tests |
| M10 | `ARCHITECTURE.md` | §4.5 `AdvisoryTextPolicy`; §4.10 `llm-output-policy-check` | red-team LLM tests |
| M11 | `ARCHITECTURE.md`, `domain/types/sop_protected.py` | §4.6 namespace partition | `test_design_plan_cannot_contain_protocol_step` (mypy + runtime) |
| M12 | `ARCHITECTURE.md` | §4.7 three streams; §4.8 persistence | cross-stream-link tests |
| M13 | this file | — | `audit-traceability-check` CI gate |
| N1 | `ARCHITECTURE.md` | document-wide | doc-version-consistency test |
| N2 | `REQUIREMENTS.md`, `ARCHITECTURE.md` | appendix traceability | requirement-ID-consistency test |
| N3 | `ARCHITECTURE.md`, `REQUIREMENTS.md` | SBOL terminology | sbol3-terminology lint |
| N4 | `ARCHITECTURE.md` | §4.6 `ProtocolDAG` serialisation | canonical-serialisation tests |
| N5 | `ARCHITECTURE.md` | §4.6 `ScreeningError` taxonomy | error-category tests |
| N6 | `ARCHITECTURE.md` | §4.8 export profiles | redaction tests per profile |
| N7 | `ARCHITECTURE.md` | §4.5 plugin manifest signing | manifest-signature CI gate |
| N8 | `ARCHITECTURE.md` | `engine.controls` validation rules | control-suitability tests |

---

## 6. Sign-off

**`/scientific-advisor` (v1.4):** "Every Codex finding is biologically grounded. The B3 defense is consistent with the platform's scope (DNA sequence design, not direct biological manipulation) and is strengthened by the new `BiosafetyClassificationLayer` advisory — administrators see structured warnings on high-risk elements before granting permissions, which materially improves the informational safety floor without imposing dual sign-off on routine work. Approved for v1.4."

**`/architect` (v1.4):** "The architectural findings (B5–B7, B10, M1–M6, M9–M12, N3–N7) are all correct and produce a cleaner type system. The `domain.ports/` separation, the typed `ImportedConstruct` / `AnnotatedConstruct`, the structured `Qualifier`, the multi-hash model, the `domain.types.sop_protected` namespace, and the separated event streams collectively tighten the architecture against the failure modes Codex identified. Approved for v1.4."

**`/dev-orchestrator` (v1.4):** "The operational findings (B1, B8, B9, B11, B12, M7, M8, M13, N1, N2, N8) are all correct. The new CI gates (`import-linter` contract for B7, `audit-traceability-check` for M13, `llm-output-policy-check` for M10, plugin-manifest-signature for N7) make the architectural intent enforceable in code. The post-screening pipeline reordering (B2 / B12) is structurally necessary. The B3 defense is operationally sound for the platform's scope. Approved for v1.4."

---

*End of ARCHITECTURE_Second_Audit_Response.md.*
