# Software Requirements Specification
## Universal Cloning and Expression Vector Design Software

**Document type:** Software Requirements Specification (SRS)
**Drafted by:** Scientific Advisor (Senior Molecular Biology scientist role)
**Date:** 2026-05-13
**Status:** Draft v0.1 — for architect / dev-orchestrator review and consolidation
**Project root:** `C:\Users\tocvi\OneDrive\文档\Project_Code\Cloning_Expression_Vector_Design\`
**Source-of-truth documents:** `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` (machine-actionable), `Cloning_Expression_Vector_Design_White_Paper.md` (conceptual), `ROADMAP.md` (phasing).

---

## 0. How to read this document

Every requirement has:

- a **unique ID** (e.g., `FR-INT-01`),
- a **priority** in the MoSCoW scheme: **MUST** (release-blocker), **SHOULD** (important, can slip one phase), **COULD** (nice-to-have), **WON'T** (explicitly out of scope this release),
- a **rationale** (why the requirement exists; usually a citation to v2.0 KB or to the white paper),
- a **verification method** (how acceptance will be tested: unit test, integration test, user-acceptance test, expert review).

A traceability matrix at the end (§ Appendix A) maps each requirement back to the knowledge-base section that justifies it.

Categories used:

| Prefix | Category |
|---|---|
| `UR` | User-stated requirements (8 explicit asks from the project sponsor) |
| `FR-INT` | Interoperability (SnapGene, file formats, SBOL, external tools) |
| `FR-UI` | User interface (decision tree, drop-downs, free-text, visual map) |
| `FR-CORE` | Core molecular-cloning computational functions |
| `FR-MOD` | Modular building-block assembly |
| `FR-PARAM` | Plasmid parameter selection |
| `FR-HOST` | Host-strain database and compatibility engine |
| `FR-ENZ` | Enzyme and toolkit enzyme database |
| `FR-VAL` | In-silico validation engine |
| `FR-PRIM` | Primer design module |
| `FR-PROTO` | Wet-lab protocol generator |
| `FR-IO` | Sequence input / output and standards |
| `FR-PROJ` | Project management, versioning, provenance |
| `MR` | Molecular-genetics rules (machine-checkable) |
| `WR` | Wet-lab workflow rules (machine-checkable) |
| `SR` | Synthesis vendor / third-party supplier constraints |
| `BR` | Biosafety and biosecurity rules |
| `NFR` | Non-functional requirements (performance, usability, reliability, etc.) |
| `SC` | System / architectural constraints |
| `DR` | Data model and schema requirements |
| `AC` | Acceptance criteria (per major functional area) |

---

## 1. Project purpose and scope

### 1.1 Purpose

Build a software platform that takes a user-stated biological objective (host, cargo, expression level, biosafety tier, downstream use) and produces:

1. A fully designed cloning or expression vector (annotated DNA sequence + feature map),
2. All required primer sequences,
3. The corresponding wet-lab assembly protocol,

all verified against a comprehensive set of molecular-genetics rules, wet-lab workflow constraints, supplier-specific synthesis constraints, and biosafety/biosecurity screening requirements.

The software must be **universal** in the sense that it supports the three principal eukaryotic and prokaryotic host classes — bacterial (*E. coli* and broad-host Gram-negative), plant (via *Agrobacterium*-mediated transformation), and mammalian — plus yeast, insect/baculovirus, and cell-free systems where these are needed.

### 1.2 Scope (in scope)

- Conceptual to physical: design a vector, generate primers, generate a wet-lab protocol.
- Hosts: *E. coli* (cloning + expression), yeast (*S. cerevisiae*, *Pichia*), mammalian (HEK293, CHO, iPSC, primary), plant (nuclear, via *Agrobacterium*), insect (baculovirus), cell-free (PURE, S30, TXTL).
- Cargo classes: protein-coding ORFs, gRNAs (CRISPR), structural RNAs, reporter cassettes, gene-therapy payloads (AAV / lentivirus).
- Cloning chemistries: restriction + ligation, Gibson / NEBuilder HiFi, Golden Gate / MoClo / Loop / YTK / GreenGate / GoldenBraid / JUMP / MIDAS, Gateway, LIC, SLIC, USER, IVA, yeast TAR.
- Validation: in-silico rule pipeline; biosafety screening hook.
- Interoperability: SnapGene round-trip, SBOL 3, GenBank, FASTA.
- Output: vector design, primer set, diagnostic strategy, wet-lab protocol.

### 1.3 Out of scope (won't, this release)

- Liquid-handling robot integration / wet-lab automation.
- Actual placement of synthesis orders with vendors (the software generates submission-ready files; the human user submits).
- Wet-lab data ingestion (sequencing trace QC, gel-image OCR).
- Patent / freedom-to-operate analysis (handed off to `/ip-auditor`).
- Direct support for cell-line genome editing campaigns beyond construct design (delivery, screening, clonal isolation: out of scope).
- LIMS / inventory management.

### 1.4 Stakeholders and personas

| Persona | Background | Primary use of the software |
|---|---|---|
| **The senior scientist (project lead)** | PhD-level molecular biologist, designs constructs daily | Power user: combines templates, overrides defaults, demands traceability. |
| **The junior researcher / technician** | Bachelor's or Master's, first independent cloning project | Guided user: relies on decision-tree wizard, follows generated protocol step-by-step. |
| **The bioinformatician** | Programming background, designs combinatorial libraries | API user: scripts the platform to generate large libraries; consumes JSON/SBOL outputs. |
| **The institutional biosafety officer (IBC)** | Reviews construct designs before approval | Reviewer: reads metadata, screening results, biosafety classification. |
| **The principal investigator / sponsor** | Approves projects, signs MTAs | Approves; consumes summary reports. |

---

## 2. User-stated requirements (the 8 explicit asks)

These are the requirements stated directly by the project sponsor. Every one becomes a **MUST**.

| ID | Statement | Detailed elaboration |
|---|---|---|
| **UR-01a** *(MUST — was UR-01 pre-v1.1 audit)* | The software must seamlessly interoperate with SnapGene at the file-format level via an automated round-trip channel. | User exports a GenBank file from SnapGene into a watched directory; the platform parses, runs validation, emits an updated GenBank that SnapGene re-imports. Achievable regardless of SnapGene Server API availability. See FR-INT-01, FR-INT-03, FR-INT-04a, FR-INT-06. |
| **UR-01b** *(SHOULD — split from UR-01 per ARCHITECTURE v1.1 audit response M6)* | The software should also provide a live SnapGene channel via the official SnapGene Server API when available. | Conditional on official SnapGene Server API maturity and acceptable licensing; falls back to UR-01a (file-watch) if unavailable. See FR-INT-04b. |
| **UR-02** | The software must provide a decision-tree-based design interface with structured drop-downs **and** a free-text field for rare / specialised requirements. | The decision tree walks the user through objective → host → cargo → expression level → assembly chemistry. Drop-downs cover canonical options; a free-text channel lets the user enter unusual constraints (e.g., a non-catalogued promoter, a strain-specific oddity, an internal IP-protected element). See FR-UI-01 … FR-UI-12. |
| **UR-03** | The software must implement core molecular-cloning computational functions: restriction-enzyme site analysis, restriction-site compatibility evaluation, and codon optimisation. | See FR-CORE-01 … FR-CORE-15. |
| **UR-04** | The design environment must function as a modular "building-block" assembly system: users select and arrange genetic elements (markers, promoters, terminators, origins of replication). | See FR-MOD-01 … FR-MOD-08. |
| **UR-05** | Users must be able to specify plasmid copy number (high-copy vs low-copy origin). | See FR-PARAM-01 … FR-PARAM-04. |
| **UR-06** | The software must include a comprehensive host-strain database with genotypes / phenotypes, and must automatically evaluate compatibility between design choices and the selected host strain; conflicts must trigger a clear warning. | See FR-HOST-01 … FR-HOST-12. |
| **UR-07** | The software must include a database of the most commonly used restriction enzymes and other toolkit enzymes required for vector construction. | See FR-ENZ-01 … FR-ENZ-10. |
| **UR-08** | After designing the vector, GOI, and primers, the software must automatically produce a detailed, step-by-step wet-lab protocol; accurate, executable, cloning-strategy-compatible, design-aligned, and clear enough for a junior researcher to follow without ambiguity. | See FR-PROTO-01 … FR-PROTO-15. |
| **UR-09** *(added per ARCHITECTURE v1.2 sponsor sharpening, 2026-05-13)* | The biosafety / operational-protocol **hard gate** must be **administrator-controlled**, not user-self-declared. Only the software developer (system level) and the institutional administrator (deployment level) may create, modify, or revoke a user's authorisation profile. The user **declares** an intent (which SOP library to bind to, which biosafety approval ID applies, which role-of-operation they are operating in) but those declarations are validated against the administrator-granted profile; declarations that exceed the profile are rejected. The user has no path to grant themselves operational-protocol rights, no path to lift a biosafety gate, and no path to widen their declared role. | See FR-AUTH-01 … FR-AUTH-12 below. |
| **UR-10** *(added per ARCHITECTURE v1.3 sponsor clarification on role hierarchy, 2026-05-13)* | The role hierarchy must be **asymmetric**: `Administrator` capabilities **⊇** `Reviewer` capabilities (an Administrator may perform every Reviewer action, including per-construct sign-off on `WATCHLIST` and `MANUAL_REVIEW_REQUIRED` screening verdicts); `Reviewer` capabilities **⊄** `Administrator` capabilities (a Reviewer may not mint / modify / revoke `AuthorisationProfile` records, may not author institutional SOPs, may not mutate the audit log). The practical consequence is that **an institution may complete the entire authorisation workflow with an Administrator alone**, without a separate Reviewer being appointed. The audit trail must record whether each sign-off was performed by a dedicated `Reviewer` or by an `Administrator` acting in reviewer capacity. | See FR-AUTH-13 / FR-AUTH-14 below. |
| **UR-11** *(added per ARCHITECTURE v1.5 sponsor strengthening of B3, 2026-05-14)* | Advisory warnings emitted by the `BiosafetyClassificationLayer` (B3 mitigation) **must be active, auditable, and tied to the design record**. The Administrator must receive an **explicit warning**, and the **approval trace must be logged**. The system **must not rely on passive UI warnings** — a banner that can be dismissed without action is forbidden. Every advisory of severity `caution` or `strong_caution` requires an explicit signed acknowledgement (justification text + cryptographic signature) before any operational-protocol authorisation can fire; declines and escalations are first-class governance events; the full chain (presentation → acknowledgement / decline / escalation → authorisation decision) is persisted in the immutable governance audit stream and replayable from the audit log. | See FR-ADV-01 … FR-ADV-07 and BR-14 below. |

The remainder of this document expands each `UR` into specific testable `FR`/`MR`/`WR`/`SR`/`BR`/`NFR` items, then adds the common-essential requirements that any responsible molecular-biology software must implement.

---

## 3. Functional requirements

### 3.1 Interoperability — SnapGene and external tools (FR-INT)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-INT-01 | MUST | The system MUST round-trip GenBank flat files (`.gb` / `.gbk`) produced by SnapGene without annotation loss. | Golden-file: open a SnapGene export, parse, re-emit, byte- or semantic-equivalent. |
| FR-INT-02 | MUST | The system MUST accept proprietary SnapGene `.dna` files as input (read-only is acceptable; via a third-party parser library if available — `snapgene-reader` Python package). If `.dna` parsing is impractical, the system MUST instruct the user to export to GenBank and then import. | Unit test + manual UAT with real SnapGene files. |
| FR-INT-03 | MUST | The system MUST emit GenBank files that open in SnapGene with all features visible, named, coloured, and correctly annotated with SnapGene-recognised feature types (`promoter`, `CDS`, `terminator`, `rep_origin`, `misc_feature`, `primer_bind`, `regulatory`, `mat_peptide`, `sig_peptide`, etc.). | Manual UAT in SnapGene. |
| FR-INT-04a *(MUST — refined from FR-INT-04 per v1.1 audit M6)* | MUST | The system MUST provide an automated **file-watch** integration channel with SnapGene: user exports a GenBank file from SnapGene into a watched directory; the platform parses, validates, runs the pipeline, and emits an updated GenBank that SnapGene re-imports. This channel does not depend on any SnapGene API and is therefore unconditionally achievable. | Integration test with a running SnapGene instance + watched directory. |
| FR-INT-04b *(SHOULD — split from FR-INT-04 per v1.1 audit M6)* | SHOULD | The system SHOULD additionally provide a **live SnapGene Server API** channel where designs and updates are pushed bidirectionally over the official API. Conditional on official API availability and acceptable licensing. Falls back to FR-INT-04a if unavailable. | Integration test with a SnapGene Server instance, when available. |
| FR-INT-05 | SHOULD | The system SHOULD also support **Benchling**, **ApE**, and **Geneious** export formats (GenBank is the common denominator). | Round-trip tests against each. |
| FR-INT-06 | MUST | Every designed primer MUST be emitted as a `primer_bind` feature on the parent vector and as a separate FASTA entry in the project bundle. | Unit test. |
| FR-INT-07 | MUST | The system MUST emit a complete project bundle (vector + primers + protocol + metadata) as a ZIP archive that any biologist can unzip and use without the software installed. | Unit + UAT. |
| FR-INT-08 | SHOULD | The system SHOULD expose a documented HTTP API (REST or gRPC) so external scripts and SnapGene plug-ins can drive the engine programmatically. | API contract tests. |
| FR-INT-09 | MUST | The system MUST serialise every design to **SBOL 3** (Synthetic Biology Open Language v3.x). | Round-trip: design → SBOL → re-import → equivalent. |
| FR-INT-10 | SHOULD | The system SHOULD support **iGEM Registry** part import (BioBrick / iGEM Distribution part numbers) and **Addgene** plasmid IDs as input identifiers; the system fetches the sequence (cached locally) and uses it as a part. | Integration test with at least 10 real IDs. |
| FR-INT-11 | COULD | The system COULD support **JBEI ICE** and **FreeGenes** API queries for parts. | Integration test. |
| FR-INT-12 | MUST | All features annotated by the system MUST use **Sequence Ontology** controlled-vocabulary terms in the SBOL serialisation. | Static validation against the SO release. |

### 3.2 Decision-tree design interface (FR-UI)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-UI-01 | MUST | The UI MUST provide a step-wise decision tree guiding the user through: (1) objective, (2) target host, (3) cargo type, (4) expression level / induction, (5) tagging strategy, (6) cloning chemistry, (7) biosafety tier. | UAT walk-through. |
| FR-UI-02 | MUST | Each step MUST present a drop-down with canonical options pulled from the parts catalogue (v2.0 KB § 5–6). | UI inspection. |
| FR-UI-03 | MUST | Each step MUST also offer a free-text input field labelled "Other / specialised — describe your requirement" with at least 2 000 characters of capacity. Free-text entries are persisted and surfaced to the validator and protocol generator. | UI inspection + persistence test. |
| FR-UI-04 | MUST | The UI MUST display, at every decision point, an explanatory tooltip drawn from the white paper that explains what the choice means and what the trade-offs are. | UAT. |
| FR-UI-05 | MUST | Every drop-down entry MUST be tagged with its citation (PMID / DOI / repository URL) drawn from v2.0 KB § 18 and viewable on demand. | UI inspection. |
| FR-UI-06 | MUST | The UI MUST provide a "Why this default?" affordance at every step that opens the citation in a side panel. | UAT. |
| FR-UI-07 | MUST | The UI MUST display a live vector map (circular plasmid view) that updates as choices are made. | UAT. |
| FR-UI-08 | MUST | The UI MUST display a live linear feature map of any selected region with zoom / scroll. | UAT. |
| FR-UI-09 | MUST | The UI MUST display the ORF translation in three frames for any selected region, with start / stop codons highlighted and in-frame fusions visualised. | UAT. |
| FR-UI-10 | MUST | The UI MUST allow the user to "lock" any module (origin, marker, promoter, RBS/Kozak, ORF, terminator/polyA) and re-run the decision tree from any subsequent step. | UAT. |
| FR-UI-11 | MUST | The UI MUST display the live validation report (FR-VAL) as it changes, with each warning / error linked back to the specific module that caused it. | UAT. |
| FR-UI-12 | SHOULD | The UI SHOULD support "design diff" — visual comparison of two construct versions side-by-side with annotated changes. | UAT. |
| FR-UI-13 | SHOULD | The UI SHOULD provide an "expert mode" that exposes all underlying numeric parameters; a "guided mode" that hides them and shows only recommendations. | UAT. |
| FR-UI-14 | COULD | The UI COULD provide multi-language support (English first; Simplified Chinese a strong candidate for v1.1). | UAT. |

### 3.3 Core molecular-cloning computational functions (FR-CORE)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-CORE-01 | MUST | The system MUST scan any input sequence for the recognition sites of all enzymes in the toolkit database (FR-ENZ) and return all hit positions with strand. | Unit tests against curated sequences with known sites. |
| FR-CORE-02 | MUST | The system MUST evaluate restriction-site **compatibility** between two fragments produced by digestion: (a) sticky ends match, (b) reading frame is preserved across the junction if the ORF spans the cut. | Unit tests. |
| FR-CORE-03 | MUST | The system MUST identify **unique** restriction sites in a given vector (sites present in the vector but absent from a candidate insert) and rank them by suitability for directional cloning. | Unit tests. |
| FR-CORE-04 | MUST | The system MUST perform **codon optimisation** of any input ORF against any selected host's codon-usage table. | Unit tests vs published CAI / %MinMax values for known optimised genes. |
| FR-CORE-05 | MUST | Codon optimisation MUST support multiple algorithm choices: **CAI maximisation** (Sharp & Li 1987), **%MinMax** (Clarke & Clark 2008), **CHARMING** (Jacobs & Shakhnovich 2017), and **avoid-only mode** (preserve native codons except where a forbidden motif must be removed). | Algorithm-selection tests. |
| FR-CORE-06 | MUST | Codon optimisation MUST preserve **annotated functional RNA elements** (frameshift signals, IRES, riboswitches, regulatory pause sites, miRNA target sites, splice silencers/enhancers) if the user marks them as protected. | Unit test: optimisation must not change a marked region's sequence. |
| FR-CORE-07 | MUST | Codon optimisation MUST automatically avoid creating recognition sites for any enzyme in the user's "forbidden enzyme list" (typically the cloning enzymes for the chosen chemistry). | Unit test: post-optimisation, no forbidden site is present. |
| FR-CORE-08 | MUST | The system MUST compute **CAI**, **GC content (global and 50-bp windowed)**, **homopolymer-run length**, **direct-repeat count and length**, **predicted mRNA folding ΔG** in user-specified regions (typically −30 to +30 nt around the start codon) for any sequence. | Unit tests vs reference implementations. |
| FR-CORE-09 | MUST | The system MUST run **ORF detection and three-frame translation** with selectable codon-translation tables (NCBI translation tables 1, 11, 4 at minimum). | Unit tests. |
| FR-CORE-10 | MUST | The system MUST translate the user's annotated ORF in its intended frame from the chosen start codon to the chosen stop codon and confirm there is no premature stop. | Unit test. |
| FR-CORE-11 | MUST | The system MUST translate every annotated **fusion junction** (N-tag–linker–ORF, ORF–linker–C-tag, protease-site–scar–ORF, attB1–scar–ORF, etc.) in the intended reading frame and confirm consistency. | Unit test against curated fusion patterns. |
| FR-CORE-12 | MUST | The system MUST compute the **sticky-end sequence** generated by every restriction-enzyme cut (5′ overhang, 3′ overhang, blunt). | Unit tests. |
| FR-CORE-13 | MUST | The system MUST compute **Golden Gate overhang fidelity** scores using the Potapov 2018 / Pryor 2020 published datasets and rank candidate overhang sets for any N-fragment assembly. | Unit tests against published Pryor 2020 assemblies. |
| FR-CORE-14 | MUST | The system MUST detect **secondary-structure hot spots** (hairpins) by ViennaRNA `RNAfold` in any nominated region and flag those with ΔG ≤ -10 kcal/mol if they overlap an RBS / Kozak / cloning junction. | Unit tests. |
| FR-CORE-15 | SHOULD | The system SHOULD predict bacterial **translation-initiation rate (TIR)** using the RBS Calculator v2 model (Reis & Salis 2020). | Test against published TIR/expression correlations. |
| FR-CORE-16 | SHOULD | The system SHOULD compute a **quantitative Kozak score** for mammalian start codons using the Noderer 2014 position-weight matrix. | Test against published high/low-expression Kozak contexts. |
| FR-CORE-17 | SHOULD | The system SHOULD scan for cryptic splice sites (SpliceAI or NetGene2) in any mammalian cargo. | Test against curated cases with known cryptic splices. |
| FR-CORE-18 | SHOULD | The system SHOULD scan for **upstream ORFs** (uAUGs) in mammalian 5′ UTRs with their Kozak scores. | Unit tests. |
| FR-CORE-19 | SHOULD | The system SHOULD scan for **premature polyadenylation signals** (AAUAAA and close variants) in 5′ UTR and within the ORF. | Unit tests. |
| FR-CORE-20 | SHOULD | The system SHOULD predict **signal-peptide cleavage** using SignalP (or equivalent) and confirm the predicted cleavage site is consistent with the declared compartment. | Test against curated signal-peptide examples. |

### 3.4 Modular building-block assembly (FR-MOD)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-MOD-01 | MUST | The system MUST organise every genetic element as a typed, versioned **Part** (per v2.0 KB § 15 schema) with role (Sequence Ontology term), sequence, annotations, parent, licence, provenance, and SHA-256 checksum. | Schema validation. |
| FR-MOD-02 | MUST | The system MUST allow the user to assemble a construct by *dragging* parts into the six-layer architecture slots (propagation / assembly interface / expression-control / cargo / termination / metadata). | UAT. |
| FR-MOD-03 | MUST | Each slot MUST enforce **part-class constraints** at drag time: a promoter cannot be dropped into the cargo slot; a polyA cannot be dropped into the bacterial-terminator slot for a bacterial design; etc. | Unit + UI tests. |
| FR-MOD-04 | MUST | The system MUST ship a **default part library** populated from the v2.0 KB parts catalogue (§ 5) — at least every part listed there. | Inventory check. |
| FR-MOD-05 | MUST | The user MUST be able to **add a custom part** via paste, FASTA upload, or accession-ID fetch; the part is then assigned a UUID and stored in the local library. | UAT. |
| FR-MOD-06 | MUST | The library MUST be searchable and filterable by host compatibility, strength, size, licence, source. | UAT. |
| FR-MOD-07 | MUST | When a part is replaced in a construct, the validator and the protocol generator MUST re-run automatically. | Integration test. |
| FR-MOD-08 | SHOULD | The library SHOULD support **collections** (named groups of parts, e.g., "MoClo YTK level-0 parts"). | UAT. |
| FR-MOD-09 | SHOULD | The library SHOULD support **provenance graphs** so the user can see which parts derive from which others. | UAT. |

### 3.5 Plasmid parameter selection (FR-PARAM)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-PARAM-01 | MUST | The user MUST be able to specify **copy number** as: very-high (≥ 300), high (≥ 100), medium (10–100), low (1–10), single-copy. The system maps the choice to compatible origins (FR-MOD-04, v2.0 KB § 5.1). | UI inspection + mapping test. |
| FR-PARAM-02 | MUST | The user MUST be able to specify **host range** (single-host vs broad-host) and the system MUST restrict origin choices accordingly. | Mapping test. |
| FR-PARAM-03 | MUST | The user MUST be able to specify **biosafety tier** (BSL-1 / BSL-2 / BSL-2+ / BSL-3) and downstream use (research / translational / environmental release / manufacturing); the system warns when chosen elements (e.g., antibiotic markers, viral elements, mobilisation elements) are inappropriate for that tier. | Rule test. |
| FR-PARAM-04 | MUST | The user MUST be able to specify **expression level target** (off / low / medium / high / tunable) and the system narrows promoter, RBS/Kozak, and copy-number choices accordingly. | Mapping test. |
| FR-PARAM-05 | MUST | The user MUST be able to specify **induction** (constitutive vs inducible) and, if inducible, the inducer (IPTG / arabinose / rhamnose / aTc / doxycycline / galactose / methanol / heat). The system enforces all-components-present (e.g., Tet-On requires both TRE and rtTA cassettes). | Rule test. |
| FR-PARAM-06 | MUST | The user MUST be able to specify **secretion / compartment** target (cytoplasm / periplasm / extracellular / nucleus / ER / mitochondrion / chloroplast / membrane); the system adds the appropriate signal peptide and downstream-folding considerations. | Rule test. |

### 3.6 Host-strain database (FR-HOST)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-HOST-01 | MUST | The system MUST ship a database covering at minimum: |
|  |  | **E. coli (cloning):** DH5α, DH10B, TOP10, XL1-Blue, JM109, MachT1R, NEB Stable, Stbl3, Stbl4, HB101, NEB 5α, ccdB Survival 2 / DB3.1 (gyrA462), Pir+ strains (BW19851, EC100D-pir+). |
|  |  | **E. coli (expression):** BL21(DE3), BL21 Star, BL21(DE3)pLysS, BL21(DE3)pLysE, Rosetta(DE3), Rosetta-gami, Origami 2(DE3), SHuffle T7, SHuffle T7 Express, C41(DE3), C43(DE3), Lemo21(DE3), Tuner(DE3), Arctic Express, KRX, T7 Express. |
|  |  | **Yeast:** BY4741, BY4742, W303, S288C, INVSc1, EBY100, GS115 (*Pichia*), X-33 (*Pichia*), KM71H, SMD1168. |
|  |  | **Mammalian:** HEK293, HEK293T, HEK293F, Expi293F, CHO-K1, CHO-DG44, CHO-S, CHO-GS-null, HeLa, COS-1, COS-7, Sp2/0, NS0, Jurkat, K562, U2OS, HepG2, iPSC lines, human ES lines. |
|  |  | **Insect:** Sf9, Sf21, High Five, Tnms42. |
|  |  | **Plant:** *N. benthamiana*, *A. thaliana* (Col-0, Ler), rice (Nipponbare), maize (B73), tobacco (BY-2 suspension). |
|  |  | **Agrobacterium:** GV3101, GV2260, EHA105, EHA101, LBA4404, AGL-1. |
|  |  | Schema check + content review. |
| FR-HOST-02 | MUST | Each strain entry MUST contain: official name, genotype (in standard nomenclature), supplier / source, ATCC or equivalent ID where applicable, chassis class (prokaryote / eukaryote / cell-free), endogenous features relevant to design (DE3 lysogen for T7 polymerase, *recA-* / *endA-* status, oxidative-cytoplasm modifications, *gyrA462* for ccdB tolerance, *F'* episome for blue-white screening, *λpir* status for R6K, presence of T-antigen for SV40 ori, etc.), and primary citations. | Schema validation. |
| FR-HOST-03 | MUST | The system MUST automatically check the user's design against the chosen host's genotype and raise warnings for the following incompatibilities: |
|  |  | (a) Selectable marker already present in host (e.g., kanR host + kan marker on vector). |
|  |  | (b) T7 promoter on cargo without T7 RNA polymerase in host (e.g., needs DE3 lysogen). |
|  |  | (c) Inducible-promoter component missing from host (e.g., Tet-On without rtTA in target). |
|  |  | (d) ccdB-containing vector without ccdB-tolerant strain. |
|  |  | (e) R6K origin without π-protein-positive host. |
|  |  | (f) SV40 ori without large T-antigen. |
|  |  | (g) EBV oriP without EBNA1. |
|  |  | (h) LTR-containing lentivirus transfer plasmid with non-Stbl3/Stbl4 amplification host. |
|  |  | (i) Long repeats or known recombination hotspots with non-*recA-* host. |
|  |  | (j) Disulfide-rich protein with reducing-cytoplasm host (suggest SHuffle / Origami). |
|  |  | (k) Membrane protein with standard host (suggest C41/C43 / Lemo21). |
|  |  | (l) Rare-codon-heavy ORF with non-Rosetta host (or suggest codon optimisation). |
|  |  | Rule-by-rule unit tests. |
| FR-HOST-04 | MUST | Each warning MUST be classified as **HARD** (block compilation), **SOFT** (require user acknowledgement), or **INFO** (informational only). | Rule schema. |
| FR-HOST-05 | MUST | Each warning MUST include: the offending design element, the host feature it conflicts with, the rationale (a sentence or two), the citation, and **a concrete suggested remediation** (e.g., "switch host to BL21(DE3) or remove the T7 promoter"). | UAT. |
| FR-HOST-06 | MUST | The user MUST be able to override any SOFT warning with a justification that is recorded in the construct's provenance. | UAT + audit log. |
| FR-HOST-07 | MUST | The system MUST recommend **suitable hosts** for any given construct based on its features (suggests SHuffle for disulfide-rich, BL21(DE3) for T7-driven, GV3101 for plant binary, etc.). | Rule test. |
| FR-HOST-08 | SHOULD | The system SHOULD store per-host **codon usage tables** and use them for FR-CORE-04. | Inventory check. |
| FR-HOST-09 | SHOULD | The system SHOULD store per-host **standard growth conditions** (temperature, medium, antibiotic concentrations, induction protocol) so the protocol generator (FR-PROTO) can populate them. | Inventory check. |
| FR-HOST-10 | COULD | The system COULD support **user-defined custom strains** (paste genotype, declare features). | UAT. |
| FR-HOST-11 | MUST | Compatibility checking MUST be re-run automatically every time a module is changed. | Integration test. |
| FR-HOST-12 | MUST | The full set of compatibility checks (FR-HOST-03) MUST be enumerated in machine-readable form in the rule registry (§ 4 MR), each linked to its v2.0 KB citation. | Static check on rule registry. |

### 3.7 Enzyme and toolkit database (FR-ENZ)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-ENZ-01 | MUST | The system MUST ship a database of **commonly used restriction enzymes** with: recognition sequence, cut position, overhang type (5′/3′/blunt), overhang length, methylation sensitivity (Dam, Dcm, CpG, EcoKI), star activity profile, optimal buffer, optimal temperature, heat-inactivation conditions, supplier reference (NEB cat #, Thermo cat #, etc.). | Schema + content check; cross-validate against REBASE. |
| FR-ENZ-02 | MUST | At minimum the system MUST include: EcoRI, BamHI, HindIII, XhoI, NotI, PstI, SalI, KpnI, SacI, XbaI, NcoI, NdeI, EcoRV, BglII, SphI, ApaI, NheI, SpeI, AscI, FseI, PacI, SwaI, MluI, PmeI, AvrII, ClaI, HpaI, SmaI/XmaI, NruI, ScaI, AfeI. | Inventory check. |
| FR-ENZ-03 | MUST | The system MUST include the **Type IIS enzymes** for Golden Gate: BsaI, BsaI-HFv2, BsmBI / Esp3I, BsmBI-v2, SapI / BspQI, BbsI / BpiI, AarI, PaqCI, BtgZI, BsmFI, FokI. | Inventory check. |
| FR-ENZ-04 | MUST | The system MUST include common **DNA-manipulating enzymes** in a separate "toolkit enzyme" table: T4 DNA ligase, T4 polynucleotide kinase (PNK), T4 DNA polymerase (LIC blunt), Taq DNA polymerase, Phusion / Q5 / KAPA HiFi (high-fidelity polymerases), Klenow fragment, Klenow exo-, T5 exonuclease, DNase I, RNase A/H, Exo I, alkaline phosphatase (CIP / rSAP / Antarctic), Bsu polymerase. | Inventory check. |
| FR-ENZ-05 | MUST | The system MUST include common **assembly enzyme mixes** as composite entries: NEBuilder HiFi Master Mix, NEB Gibson Assembly Master Mix, In-Fusion (Takara), CloneEZ (GenScript), Golden Gate Assembly Kit (BsaI-HFv2 + T4), HiFi DNA Assembly (NEB). | Inventory check. |
| FR-ENZ-06 | MUST | The system MUST include the **proteases** used for tag removal: TEV protease (ENLYFQ↓G/S), 3C / PreScission (LEVLFQ↓GP), Thrombin (LVPR↓GS), Enterokinase (DDDDK↓X), Factor Xa (IEGR↓), SUMO protease (Ulp1; cleaves SUMO-X to native X), HRV 3C. | Inventory check. |
| FR-ENZ-07 | MUST | The system MUST include common **enzyme buffers** as separate entries with components and storage conditions. | Inventory check. |
| FR-ENZ-08 | MUST | The enzyme database MUST be searchable by recognition sequence, overhang, host-strain methylation compatibility, vendor, and price tier. | UAT. |
| FR-ENZ-09 | MUST | The system MUST flag **double-digest buffer incompatibility** (two enzymes that do not share a single optimal buffer at high activity); for each pairing the system MUST recommend either a single buffer with reduced activity, sequential digestion, or a substitute enzyme. | Rule test against curated REBASE compatibility data. |
| FR-ENZ-10 | MUST | The system MUST flag **methylation incompatibility** (e.g., DpnI for digesting methylated template after PCR; methylation-blocked enzymes on Dam+/Dcm+ DNA). | Rule test. |
| FR-ENZ-11 | SHOULD | The system SHOULD include **competent-cell products** (One Shot TOP10, DH5α MAX Efficiency, etc.) with declared transformation efficiency so the protocol generator can specify expected colony yield. | Inventory check. |
| FR-ENZ-12 | SHOULD | The enzyme database SHOULD be user-extensible (add new enzymes with the required schema). | UAT. |

### 3.8 In-silico validation engine (FR-VAL)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-VAL-01 | MUST | The validator MUST execute **every** rule in the machine-readable rule registry (§ 4 MR, WR, SR, BR) against any candidate design. | Integration test. |
| FR-VAL-02 | MUST | Validation rules MUST be expressed as `(rule_id, predicate, severity, citation, suggested_remediation)` tuples. | Schema check. |
| FR-VAL-03 | MUST | The validator MUST classify every result as `pass`, `warn`, or `fail`, with `fail` blocking compilation and `warn` requiring user acknowledgement. | Rule semantics test. |
| FR-VAL-04 | MUST | The validator MUST produce a structured report: pass/warn/fail counts, list of issues, each issue with location, severity, citation, suggested fix. | Report-schema test. |
| FR-VAL-05 | MUST | The validation report MUST be exportable as Markdown, PDF, and JSON. | UAT. |
| FR-VAL-06 | MUST | The validator MUST be **incremental** — when one module changes, only rules affecting that module re-run, plus their dependents. | Performance test. |
| FR-VAL-07 | MUST | The validation rule set MUST be **versioned** and the version recorded in the construct's provenance. | Provenance schema check. |
| FR-VAL-08 | SHOULD | The validator SHOULD expose a **what-if** mode: "if I changed this module to X, what would the new validation report look like?" | UAT. |
| FR-VAL-09 | MUST | The validator MUST run all v2.0 KB § 9 rules V001 – V025 at minimum, plus the additional rules listed in § 4 of this document. | Static rule-count check. |
| FR-VAL-10 | MUST | The validator MUST never silently filter or drop a rule; every rule must produce at least an `INFO` entry in the report so that absence-of-result is visible. | Audit-trail test. |

### 3.9 Primer design module (FR-PRIM)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-PRIM-01 | MUST | For every assembly chemistry chosen, the system MUST generate the **complete primer set** needed to amplify all fragments. | Unit test. |
| FR-PRIM-02 | MUST | Primer design MUST respect: Tm in user-set range (default 55–65 °C, ΔTm between pair ≤ 3 °C), length 18–35 nt, 3′ end GC stability, no 3′-end mismatch with template, no internal hairpin ΔG ≤ −9 kcal/mol, no primer-dimer ΔG ≤ −9 kcal/mol, single binding site in template. | Unit tests. |
| FR-PRIM-03 | MUST | For Gibson / HiFi: primers MUST include 5′ homology-arm extensions of length appropriate to the fragment count (15–40 nt per v2.0 KB § 7.5). | Unit test. |
| FR-PRIM-04 | MUST | For Golden Gate: primers MUST include 5′ extensions carrying the chosen Type IIS recognition site and the user-defined 4-nt overhang; the system MUST run the Pryor 2020 / Potapov 2018 overhang-set optimiser to pick non-cross-reactive overhang sets. | Unit test against published assemblies. |
| FR-PRIM-05 | MUST | For LIC: primers MUST include 5′ tails compatible with the chosen LIC vector. | Unit test. |
| FR-PRIM-06 | MUST | For USER: primers MUST place a single uracil at the designed cleavage position. | Unit test. |
| FR-PRIM-07 | MUST | For restriction cloning: primers MUST include 5′ flanking restriction-enzyme sites with the appropriate "fishtail" extension (typically 3–6 extra bp 5′ of the site for efficient cleavage by terminal cleavers). | Unit test. |
| FR-PRIM-08 | MUST | Each generated primer MUST be emitted as: (a) a `primer_bind` annotation on the parent vector, (b) a FASTA entry, (c) a row in a primer table (name, sequence 5′→3′, length, Tm, GC%, scale, modifications). | Output-format check. |
| FR-PRIM-09 | MUST | The system MUST generate **sequencing primers** that cover every cloning junction with at least 50 bp upstream and 50 bp downstream within Sanger read length (~ 800 bp). | Unit test. |
| FR-PRIM-10 | MUST | The system MUST generate **diagnostic restriction digest** primer-and-enzyme combinations that produce a distinguishable banding pattern on a 1 % agarose gel for correct vs incorrect clones. | Unit test. |
| FR-PRIM-11 | SHOULD | The system SHOULD support **gradient PCR** suggestions when no single Tm is optimal for all primer pairs. | UAT. |
| FR-PRIM-12 | MUST | The primer design MUST scan its candidates against the **target plasmid sequence** for off-target binding and reject candidates with secondary binding sites. | Unit test. |

### 3.10 Protocol output — split into design plan and SOP-linked operational protocol (FR-PROTO-DESIGN / FR-PROTO-SOP) — harmonised per ARCHITECTURE v1.4 B1

**v1.4 B1 harmonisation note.** The pre-v1.4 FR-PROTO-01 … FR-PROTO-20 (which demanded a single fully-executable wet-lab protocol as baseline output) is **superseded** by the two-family split below, to align with ARCHITECTURE.md v1.4 Objective 8 and the `DesignRealisationPlan` / `SopLinkedProtocol` partition introduced in v1.1 and reordered in v1.4 B2. Pre-v1.4 IDs are deprecated; new tests reference the new IDs.

#### FR-PROTO-DESIGN-* — `DesignRealisationPlan` (always renderable, non-operational)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-PROTO-DESIGN-01 | MUST | After a successful compile (FR-VAL passes), the system MUST emit a **`DesignRealisationPlan`** — a non-operational design artefact specific to the chosen cloning chemistry and host. Always renderable; never gated. | UAT by junior researcher. |
| FR-PROTO-DESIGN-02 | MUST | The plan MUST include: assembly route (chemistry + ordered fragments + diagnostic plan), fragment inputs (primer set + synthesis-vendor submission file if applicable), QC checkpoints (gel verification points, colony-PCR plan, diagnostic-digest plan, sequencing-primer coverage plan), expected verification artefacts (gel band sizes, expected Sanger reads, expected diagnostic-digest pattern), institutional-approval-required list, biosafety classification, reviewer-packet summary. | Content audit. |
| FR-PROTO-DESIGN-03 | MUST | The plan MUST NOT contain operational reagent quantities, incubation times, temperatures, durations, transformation conditions, or any `ProtocolStep` data. (Enforced at type level: `DesignRealisationPlan` cannot by type contain a `ProtocolStep`; see ARCHITECTURE v1.4 M11 and the `domain.types.sop_protected` namespace separation.) | mypy --strict + runtime type guard. |
| FR-PROTO-DESIGN-04 | MUST | The plan MUST be tailored to the chosen assembly chemistry. Supported: restriction-ligation, Gibson / NEBuilder HiFi, Golden Gate / MoClo (YTK, Loop, GreenGate, GoldenBraid, JUMP, MIDAS), Gateway BP / LR, In-Fusion, LIC, USER. | UAT. |
| FR-PROTO-DESIGN-05 | MUST | The plan MUST include the **diagnostic-digest strategy** and **sequencing strategy** (Sanger primers + coverage map; long-read recommendation if construct > 8 kb or repeats > 100 bp). | Content audit. |
| FR-PROTO-DESIGN-06 | MUST | The plan MUST include a **`RiskAdvisoryReport`** generated by `engine.risk_classification` (ARCHITECTURE v1.4 B3 mitigation) flagging high-risk genetic elements, elevated-BSL sequences, and constructs that may require institutional approval. | UAT + content audit. |
| FR-PROTO-DESIGN-07 | MUST | The plan MUST be emitted in Markdown and PDF; SHOULD also be exportable as a structured JSON for downstream tooling. | Output-format check. |
| FR-PROTO-DESIGN-08 | MUST | The plan MUST include a **troubleshooting appendix** mapping common failure symptoms to design-time predictors. | UAT. |
| FR-PROTO-DESIGN-09 | SHOULD | The plan SHOULD include a **time-and-materials estimate** (total wall-clock days, hands-on hours, consumables cost estimate). | UAT. |
| FR-PROTO-DESIGN-10 | MUST | Every reagent referenced in the plan MUST resolve to an entry in the enzyme / toolkit database (FR-ENZ) or to an explicit vendor SKU. | Content cross-check. |

#### FR-PROTO-SOP-* — `SopLinkedProtocol` (gated; operational; institutional)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-PROTO-SOP-01 | SHOULD | The system SHOULD emit a **`SopLinkedProtocol`** — an operational protocol bound to administrator-approved institutional SOP templates — when, and only when, all the following gates pass: (a) screening has completed with an acceptable verdict (`CLEAR`, signed-off `WATCHLIST` / `MANUAL_REVIEW_REQUIRED`, policy-permitted `UNAVAILABLE`, justified `NOT_APPLICABLE`); (b) the user's `UserDeclaration` lies inside the granted `AuthorisationProfile.scope`; (c) the `RiskAdvisoryReport` has been acknowledged where required. | UAT — gate-pass test fixture; UAT — gate-fail test fixture. |
| FR-PROTO-SOP-02 | MUST | The `SopLinkedProtocol` MUST be bound to a specific institutional SOP template from `catalogues/sop_templates/`. The institutional SOP library is admin-controlled. The system MUST NOT invent operational steps in the absence of an institutional SOP template. | Content audit; absence-of-SOP test fixture. |
| FR-PROTO-SOP-03 | MUST | The protocol MUST be rendered strictly *after* the `OperationalProtocolAuthorised` governance event has been recorded; static + runtime `sop-after-gates-check` CI gate enforces this. | CI gate test; runtime integration test. |
| FR-PROTO-SOP-04 | MUST | The protocol MUST include the steps required by the chosen SOP template: PCR set-up, digest / ligate / assembly, transformation, colony picking, miniprep, diagnostic digest, sequencing, glycerol-stocking, mammalian transient transfection or stable-line generation, Agrobacterium transformation + agroinfiltration / floral dip, with reagent quantities, temperatures, durations, and rationales — **only** as authored by the institutional SOP template. | Template-binding test. |
| FR-PROTO-SOP-05 | MUST | Each step MUST carry `sop_ref` (link to the institutional SOP), `approval_gate` (which authorisation gate authorised this step), `hazard_class` (PPE / containment / waste class), `allowed_roles` (which user roles may execute), `checkpoint_criteria` (measurable accept/reject), `measured_outputs` (measurement schema), `deviation_policy` (what to do if out of spec), `decision_rule` (stop/go/branch). | Schema test. |
| FR-PROTO-SOP-06 | MUST | The protocol MUST include biosafety reminders matching the user's `AuthorisationProfile`-granted tier and the construct's `RiskAdvisoryReport`. | Content audit. |
| FR-PROTO-SOP-07 | MUST | The protocol MUST be a typed `ProtocolDAG` with `THEN / BRANCH / CHECKPOINT / PARALLEL` edges; canonical serialisation rule applied (topological by `step_id` lexicographic key; cycle detection on construction). | Canonical-serialisation test. |
| FR-PROTO-SOP-08 | MUST | The protocol MUST be emitted in Markdown and PDF; SHOULD also be exportable as structured JSON. | Output-format check. |
| FR-PROTO-SOP-09 | MUST | If no `SopLinkedProtocol` can be rendered (institution has no SOP library, user lacks authorisation, screening blocked, advisory unacknowledged), the system MUST present a clear "operational protocol withheld pending administrator approval" notice and route a structured request to the Administrator's review queue. The user MUST still receive the `DesignRealisationPlan`. | UAT — gate-fail walkthrough. |
| FR-PROTO-SOP-10 | MUST | All operational types (`ProtocolStep`, `ProtocolDAG`, hazard / quantity / temperature / duration fields) MUST be defined in `domain.types.sop_protected` and MUST NOT be importable from any non-SOP code path. | `import-linter` CI gate. |

### 3.11 Sequence I/O and standards (FR-IO)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-IO-01 | MUST | The system MUST read/write **GenBank**, **FASTA**, **SBOL 3** at minimum. | Round-trip tests. |
| FR-IO-02 | MUST | The system MUST read **SnapGene .dna** (read-only acceptable). | UAT. |
| FR-IO-03 | MUST | The system MUST emit GenBank files with full feature annotation, **/locus_tag**, **/note**, **/translation** for CDS features. | Format conformance. |
| FR-IO-04 | MUST | The system MUST emit a **construct bundle** (ZIP) containing: the GenBank file, the FASTA file, the SBOL-3 file, the primer table (CSV + FASTA), the protocol (Markdown + PDF), the validation report (Markdown + JSON), the metadata block, the screening verdict (JSON). | Bundle audit. |
| FR-IO-05 | MUST | The system MUST compute and embed a **canonical-orientation SHA-256 checksum** of the construct sequence (rotate circular sequence to start at lexicographic minimum; record strand). | Unit test: two different rotations of the same circular sequence produce identical checksum. |
| FR-IO-06 | SHOULD | The system SHOULD support import from / export to **EMBL** flat files. | Format conformance. |
| FR-IO-07 | SHOULD | The system SHOULD support **GFF3** export of feature tables for genome-context viewers. | Format conformance. |
| FR-IO-08 | MUST | All sequence I/O MUST be **idempotent**: parsing a file and re-emitting it MUST produce semantically equivalent output (and byte-identical where the format permits). | Round-trip property test. |

### 3.12 Project management and versioning (FR-PROJ)

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-PROJ-01 | MUST | Every construct MUST have a **UUID** assigned at creation. | Schema. |
| FR-PROJ-02 | MUST | Every construct MUST have **semver-style versioning** (`major.minor.patch`); minor on element change, patch on annotation/metadata change. | Versioning rule test. |
| FR-PROJ-03 | MUST | Every construct MUST record its **parent UUIDs** (the construct(s) it derives from). | Provenance schema. |
| FR-PROJ-04 | MUST | Every construct MUST record `created_by` (ORCID or institutional ID), `created_at` (ISO-8601), and a free-text design rationale. | Schema. |
| FR-PROJ-05 | MUST | The system MUST maintain a **changelog** per construct documenting every modification and the user / agent that performed it. | Audit-log test. |
| FR-PROJ-06 | MUST | Constructs MUST be queryable by feature (any annotated part), by host, by biosafety classification, by date, by user, by free-text. | UAT. |
| FR-PROJ-07 | MUST | The system MUST support **collections / folders** for organising related constructs. | UAT. |
| FR-PROJ-08 | MUST | The system MUST attach a **licence / MTA** tag (OpenMTA / UBMTA / institutional / custom) to every construct and every part. | Schema. |
| FR-PROJ-09 | SHOULD | The system SHOULD support **multi-user collaboration** (shared project workspace, per-user roles). | UAT. |
| FR-PROJ-10 | COULD | The system COULD support a **public-repository publishing flow** (Addgene-compatible deposit). | UAT. |

### 3.13 Administrator-controlled authorisation (FR-AUTH) — added per UR-09 / v1.2 sponsor sharpening

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-AUTH-01 | MUST | The system MUST distinguish four roles: `Developer`, `Administrator`, `Reviewer`, `User`. Every authenticated session carries a typed `Principal` whose `role` is bound at authentication time and cannot be widened during the session. | Unit test on principal binding; integration test that a `UserPrincipal` cannot transition to `AdminPrincipal` in-session. |
| FR-AUTH-02 | MUST | The system MUST maintain a typed `AuthorisationProfile` per user covering: covered biosafety tiers, covered host classes, covered assembly chemistries, covered downstream uses, covered SOP libraries, covered export classes, allowed roles-of-operation, vendor-submission permission, valid_from / valid_until / revocation metadata, institutional signature. | Schema validation; round-trip test. |
| FR-AUTH-03 | MUST | The `AuthorisationProfile` MUST be **read-only** to the user it concerns and to all engine code paths. The `User` role MUST have no callable that mutates any `AuthorisationProfile`. | Static CI gate `no-self-authorisation-check`; runtime `PermissionError` test under `UserPrincipal`. |
| FR-AUTH-04 | MUST | Authorisation lifecycle (mint, modify, revoke) MUST be performed **exclusively** by `AdminPrincipal` or `DeveloperBootstrapPrincipal` through the admin-service-protected `app.admin_action_handler`. | Runtime `PermissionError` test; static reachability analysis. |
| FR-AUTH-05 | MUST | Every authorisation lifecycle action MUST be recorded in the immutable audit log as a typed `AdminActionMinted` / `AdminActionModified` / `AdminActionRevoked` event with actor, subject, structured diff, timestamp, justification, and (in multi-user mode) cryptographic signature. | Audit-log integrity test; tamper-detection test. |
| FR-AUTH-06 | MUST | The `BlockOperationalProtocol` gate MUST validate the user's `UserDeclaration` against the granted `AuthorisationProfile` on every compile. Validations include: declared SOP library ∈ `covered_sop_libraries`; declared `role_of_operation` ∈ `role_of_operation_allowed`; construct biosafety tier ⊆ `covered_biosafety_tiers`; construct host classes ⊆ `covered_host_classes`; construct assembly chemistry ∈ `covered_assembly_chemistries`; current time ∈ `[valid_from, valid_until]`; `revoked_at IS NULL`. | Rule-by-rule unit test; integration test with curated allowed and disallowed declarations. |
| FR-AUTH-07 | MUST | A failed gate validation MUST: (a) block `engine.sop_protocol` rendering, (b) still render `engine.design_plan`, (c) produce a clear "operational protocol withheld pending administrator approval" notice for the user, (d) route a structured request to the Administrator's review queue. | UAT; review-queue integration test. |
| FR-AUTH-08 | MUST | An expired (`valid_until` passed) or revoked (`revoked_at IS NOT NULL`) profile MUST cause the gate to block immediately. Profile freshness MUST NOT be cached past `valid_until`. | Integration test with clock-jump fixture. |
| FR-AUTH-09 | MUST | The `AuthorisationStore` MUST be implemented as a separate SQLite database (`authorisation.sqlite`) opened **read-only** by the engine process and the user-role processes; writes go through the admin service process which authenticates `AdminPrincipal` or `DeveloperBootstrapPrincipal`. | File-mode test; OS-level permission test in the containerised release environment. |
| FR-AUTH-10 | MUST | Every `AuthorisationProfile` MUST carry an institutional signature. Tampered profiles MUST fail verification on load and force re-mint by an Administrator. | Signature-tamper unit test. |
| FR-AUTH-11 | MUST | The administrator UI / CLI MUST expose: (a) "list all users + their current profiles", (b) "mint a profile for a user", (c) "modify a user's profile (diff + justification)", (d) "revoke a user's profile (reason)", (e) "browse the audit log of all authorisation actions". Read-only access to the audit log MUST be available to `Reviewer` principals as well. | UAT; admin walkthrough. |
| FR-AUTH-12 | MUST | The `User` role MUST be able to: (a) read its own profile, (b) view the constraints that would gate its current design, (c) submit a request to the Administrator for an extension to its profile (creates a queue entry, never auto-grants). The user MUST NOT be able to author or edit institutional SOP templates. | UAT. |
| **FR-AUTH-13** *(v1.3 — Administrator ⊇ Reviewer)* | MUST | An `Administrator` MUST be able to perform every action a `Reviewer` may perform, including per-construct sign-off on `WATCHLIST` and `MANUAL_REVIEW_REQUIRED` screening verdicts. The implementation MUST expose this through a single `Principal.can_act_as(required_role)` predicate that returns `True` when `principal.role == Role.ADMINISTRATOR` and `required_role == Role.REVIEWER`. Every code path that previously required a `ReviewerPrincipal` MUST be updated to accept any `Principal` satisfying `can_act_as(Role.REVIEWER)`. **In an institution that does not appoint a separate Reviewer, the Administrator alone MUST be able to complete the entire authorisation workflow** end-to-end. The audit log MUST record the `signer_role` discriminator (`Role.REVIEWER` vs `Role.ADMINISTRATOR`) for every sign-off event so the trail is honest about who actually signed. | Unit test on `Principal.can_act_as`; runtime integration test where an `AdminPrincipal` signs off a `WATCHLIST` verdict and the audit log shows `signer_role = ADMINISTRATOR`; Phase-13 Administrator-only end-to-end UAT. |
| **FR-AUTH-14** *(v1.3 — Reviewer ⊄ Administrator)* | MUST | A `Reviewer` MUST NOT be able to perform any `Administrator` action. Specifically: `ReviewerPrincipal` MUST be rejected by `app.admin_action_handler.mint_profile / modify_profile / revoke_profile`, by `SopTemplateAdminWritePort.write_*`, and by any direct audit-log mutation entry point outside `AuditAppendPort` / `AdminAuditAppendPort` — all such rejections MUST raise `PermissionError` and emit `AuthorisationAttemptDenied` to the audit log. `Principal.can_act_as(Role.ADMINISTRATOR)` MUST return `False` for any `ReviewerPrincipal`. There is no inheritance edge from `Reviewer` to `Administrator`. | Static reachability analysis (`no-self-authorisation-check` CI gate extended to cover Reviewer paths); runtime test where a `ReviewerPrincipal` attempts each admin operation and receives `PermissionError`. |

### 3.14 Advisory acknowledgement (FR-ADV) — added per UR-11 / v1.5 sponsor strengthening of B3

| ID | Priority | Requirement | Verification |
|---|---|---|---|
| **FR-ADV-01** | MUST | The `RiskAdvisoryReport` produced by `engine.risk_classification` MUST carry `design_session_id`, `construct_id`, `construct_checksum`, `construct_version`, `report_content_hash`, plus a stable `advisory_id` for every `RiskAdvisory` it contains. The report MUST be persisted by reference in the design event stream and reconstructable deterministically from the audit log. | Schema validation; round-trip test; replay determinism test. |
| **FR-ADV-02** | MUST | When the system presents an advisory to a principal (Administrator or Reviewer-acting), it MUST emit a typed `AdvisoryWarningPresented` governance event recording the design session, the construct version, the report content hash, the IDs of the advisories presented, the presenting surface (CLI / API / UI / report-email), and the recipient principal ID. A UI render alone is NOT sufficient — every presentation is logged. | Integration test that asserts an `AdvisoryWarningPresented` event is emitted on every CLI / API / UI presentation surface. |
| **FR-ADV-03** | MUST | For every `RiskAdvisory` of severity `caution` or `strong_caution` in the report, an explicit signed `RiskAdvisoryAcknowledgement` MUST be recorded **before** the system may emit an `OperationalProtocolAuthorised` event for that construct version. The acknowledgement MUST include: justification text (≥ 20 characters), an `AdvisoryAcknowledgementDecision` (`ACKNOWLEDGED` / `DECLINED` / `ESCALATED`), the matching `report_content_hash` + `advisory_id` + `construct_checksum`, and a signed `DecisionRecord` (per FR-AUTH B9). | Schema test; gate-pass and gate-fail integration tests. |
| **FR-ADV-04** | MUST | The system MUST NOT offer a "dismiss without action" UI affordance on advisory warnings. The only paths available on a warning of severity `caution` or `strong_caution` are *acknowledge* (with justification), *decline* (which routes the construct to an alternative reviewer / dual-control flow per `InstitutionalPolicy`), or *escalate* (which requires an `institutional_approval_id` and is recorded as a `RiskAdvisoryEscalated` governance event). | UI inspection; UAT walkthrough; declined / escalated event-emission tests. |
| **FR-ADV-05** | MUST | The authorisation gate MUST consult `all_required_advisories_acknowledged(report, governance_events)` before emitting `OperationalProtocolAuthorised`. Missing acknowledgements MUST cause `BlockOperationalProtocol` to fire and an `AuthorisationAttemptDenied` audit entry to be written that lists the missing `advisory_id`s. | Static CI gate `no-passive-advisory-bypass-check`; adversarial runtime fixture that attempts the bypass and verifies rejection. |
| **FR-ADV-06** | MUST | The full **approval trace** (every `AdvisoryWarningPresented`, every `RiskAdvisoryAcknowledged` / `RiskAdvisoryDeclined` / `RiskAdvisoryEscalated`, every authorisation decision, with timestamps and signatures) MUST be: (a) persisted in the immutable governance event stream; (b) referenced by `report_content_hash` from the `DerivationEnvironment`; (c) included in every project export bundle (subject to the chosen `ExportProfile` redaction policy); (d) deterministically replayable from the audit log. | Audit-log integrity test; bundle-export content audit; replay-determinism test. |
| **FR-ADV-07** | MUST | An adversarial UAT suite MUST verify that every known bypass path is rejected: (a) UI render only (no acknowledgement event), (b) acknowledgement event with empty or under-length justification, (c) acknowledgement event with invalid / missing signature, (d) acknowledgement event whose `construct_checksum` does not match the current construct version, (e) acknowledgement event whose `report_content_hash` does not match the current report, (f) `RiskAdvisoryDeclined` or `RiskAdvisoryEscalated` event without the required follow-through, (g) attempt to construct an `OperationalProtocolAuthorised` event programmatically without observing the matching acknowledgement chain. Each path MUST be rejected with `BlockOperationalProtocol` + a typed audit entry. | Adversarial UAT suite under Phase 13. |

---

## 4. Domain constraint catalogues (machine-checkable rules)

This section enumerates the substantive scientific rules the validator must encode. Each rule has a unique ID, a stated predicate, a severity, a justifying citation, and (where useful) a suggested remediation.

### 4.1 Molecular-genetics rules (MR)

| ID | Predicate | Severity | Citation / rationale |
|---|---|---|---|
| MR-01 | Promoter ↔ host class compatibility (bacterial / eukaryotic Pol II / Pol III / phage). | HARD | v2.0 § 5.3, § 5.4. A CMV promoter does not transcribe in *E. coli*; a T7 promoter does not transcribe in a mammalian cell without exogenous T7 RNAP. |
| MR-02 | Origin ↔ host compatibility. | HARD | v2.0 § 5.1. pUC ori works in *E. coli* but not yeast; CEN/ARS works in *S. cerevisiae* but not bacteria. |
| MR-03 | Origin incompatibility groups: two plasmids in the same Inc group cannot co-exist stably. | SOFT | del Solar 1998 (PMC98921). Warn when a second plasmid is supplied with the same Inc group. |
| MR-04 | Selectable marker not already encoded in host genome (e.g., host kanR + plasmid kan = no selection). | HARD | v2.0 § 5.2. |
| MR-05 | Selectable marker working concentration appropriate for the chosen host. | SOFT | v2.0 § 5.2 (E. coli vs mammalian concentrations differ by orders of magnitude). |
| MR-06 | Copy number consistent with cargo toxicity and stability. | SOFT | v2.0 § 5.1. Warn when a high-copy ori is combined with a leaky-promoter + toxic-cargo configuration. |
| MR-07 | Codon optimisation: CAI in [0.7, 0.95] for the chosen host. | SOFT | Sharp & Li 1987; Mauro & Chappell 2014. Avoid overshoot (saturated CAI can disturb co-translational folding). |
| MR-08 | Codon optimisation: %MinMax distance from native ≤ 0.2. | SOFT | Clarke & Clark 2008. Preserve rare-codon pause structure where it affects folding. |
| MR-09 | Codon optimisation MUST preserve user-marked functional RNA regions (IRES, frameshift signal, riboswitch). | HARD | v2.0 § 6.5. |
| MR-10 | Reading frame: every annotated ORF starts with ATG (or GTG/TTG in *E. coli* when explicitly declared) and ends with TAA/TAG/TGA; no internal stops. | HARD | central dogma. |
| MR-11 | Stop codon strategy: tandem stop codons (TAA TAA) preferred for high-fidelity termination. | SOFT | Reduces readthrough; especially for C-terminal-tagged constructs. |
| MR-12 | Bacterial SD/RBS: Shine–Dalgarno-like motif (consensus AGGAGG) within 5–13 nt of the AUG; ΔG(−30..+30) > −10 kcal/mol. | SOFT | Salis 2009; Reis & Salis 2020. |
| MR-13 | Mammalian Kozak: PWM score above threshold (Noderer 2014). | SOFT | v2.0 § 5.6. |
| MR-14 | uORF scan: any AUG in the 5′ UTR with Kozak PWM ≥ threshold → flag. | SOFT | Kozak 1987. |
| MR-15 | Premature polyadenylation scan: AAUAAA or strong variant in 5′ UTR or within ORF → flag. | SOFT | – |
| MR-16 | Splice-site scan: SpliceAI score above threshold within ORF → flag (mammalian designs). | SOFT | Jaganathan 2019. |
| MR-17 | Terminator presence and strength: every transcription unit must end in a terminator (bacterial) or polyadenylation signal (eukaryotic). | HARD | v2.0 § 5.7. |
| MR-18 | Cargo size within host capacity: AAV ≤ 4.7 kb between ITRs; lentivirus ≤ ~9 kb between LTRs; baculovirus ≤ ~38 kb; *E. coli* high-copy ≤ ~30 kb; BAC ≤ ~300 kb. | HARD | v2.0 § 9 V022. |
| MR-19 | AAV ITR integrity: 145-nt ITR sequences identical to canonical AAV2 (or other declared serotype) on both flanks. | HARD | – |
| MR-20 | Plant T-DNA: LB and RB borders flank the cassette in correct orientation; nothing outside is part of the transfer. | HARD | v2.0 § 5.x (plant). |
| MR-21 | Lentiviral 3rd-gen SIN structure: Ψ, RRE, cPPT/CTS, internal promoter, WPRE3 (not wild-type WPRE), SIN-deleted 3′ LTR. | HARD | Dull 1998 PMID 9811723; Zanta-Boussif 2009 (WPRE3). |
| MR-22 | If wild-type WPRE detected → recommend WPRE3 (mut6) variant. | SOFT | Zanta-Boussif 2009; Schambach 2006. |
| MR-23 | Inducible-system completeness: Tet-On requires TRE + rtTA; T7lac requires DE3 lysogen + (optionally) pLysS; pBAD requires AraC. | HARD | v2.0 § 9. |
| MR-24 | Mobilisation-element scan: *oriT* / *mob* genes flagged unless the design is intentionally mobilisable and biosafety tier allows it. | SOFT | NIH Guidelines 2024. |
| MR-25 | Viral replication elements (gag/pol/env, complete viral ORFs, replication-competent sequences) excluded unless explicitly approved. | HARD | NIH Guidelines 2024. |
| MR-26 | Antibiotic-resistance marker risk for translational / *in-vivo* / environmental use: WHO highest-priority antibiotics flagged. | SOFT | WHO antibiotic priority list. |
| MR-27 | CpG content: in mammalian designs, very high CpG count → flag (silencing risk). | INFO | – |
| MR-28 | Signal peptide ↔ compartment consistency: predicted SignalP cleavage site matches declared compartment; KDEL/HDEL only on intended ER-resident proteins. | SOFT | v2.0 § 5.9. |
| MR-29 | Frame-preservation across every fusion junction (N-tag–linker, linker–ORF, ORF–linker, linker–C-tag, scar–residue boundaries for Gateway / TEV / SUMO / etc.). | HARD | basic translation. |
| MR-30 | Negative-selection cassettes (ccdB, sacB, MazF, tse2) flagged if host is not the appropriate tolerant strain. | HARD | v2.0 § 5.2, § 8.3. |
| MR-31 | Intron presence on a bacterial expression vector → flag (introns not processed in *E. coli*). | HARD | – |
| MR-32 | Multiple in-frame AUGs upstream of the intended start in a mammalian ORF → flag (ribosome will use the first one). | SOFT | Kozak 1986. |
| MR-33 | Synthetic poly(A) signal on a bacterial expression vector → flag (no effect, wastes space). | INFO | – |
| MR-34 | Hairpin near junctions: ΔG ≤ -9 kcal/mol within 30 nt of a cloning junction → flag (assembly failure risk). | SOFT | – |
| MR-35 | Two compatible-end restriction sites used in non-directional cloning → flag (high background of self-ligated empty vector). | SOFT | basic restriction biology. |
| MR-36 | Single-cut linearisation with non-phosphatased ends → flag (high background of religated empty vector). | SOFT | – |
| MR-37 | Gateway: attB1/attB2 reading frame compatibility verified. | HARD | Hartley 2000. |
| MR-38 | Gateway attB1 N-terminal scar contributes 8–10 aa; attB2 C-terminal (no-stop) contributes ~25 aa — these MUST appear in the final translated sequence and the user is informed. | INFO | v2.0 § 7.6. |
| MR-39 | Type IIS site domestication: internal Type IIS recognition sites of the chosen kit absent from every part destined for Golden Gate. | HARD | Weber 2011. |
| MR-40 | Golden Gate overhang fidelity: chosen overhang set ranked by Pryor 2020 / Potapov 2018 score above kit-recommended threshold. | SOFT | Pryor 2020 PMID 32877448. |
| MR-41 | Two-fragment Golden Gate "junction" between cohesive overhangs at every step MUST not contain palindromic self-complementary overhangs. | HARD | basic Type IIS biology. |
| MR-42 | Promoter–promoter / terminator–terminator double-up (two transcription units back-to-back) requires insulator or strong terminator between them. | SOFT | Davis 2011 (insulated promoters). |
| MR-43 | Direct repeats ≥ 100 bp → block (recombination risk); ≥ 20 bp → warn. | HARD / SOFT | NEB synthesis guidelines. |
| MR-44 | Homopolymer runs > 9 nt (A/T/G/C) → warn; > 14 nt → block. | SOFT / HARD | v2.0 § 11. |
| MR-45 | Global GC content < 25 % or > 65 % → warn. | SOFT | v2.0 § 11. |
| MR-46 | GC in any 50-bp window < 15 % or > 80 % → warn. | SOFT | v2.0 § 11. |
| MR-47 | Plant 35S promoter on a mammalian construct → flag (works only weakly in mammalian cells). | SOFT | host-class mismatch. |
| MR-48 | Bacterial signal peptide (pelB, OmpA, DsbA) on a mammalian construct → flag (does not target ER). | HARD | – |
| MR-49 | T7 terminator on a non-T7 transcription unit → flag (does not terminate σ⁷⁰-transcribed mRNA). | SOFT | – |
| MR-50 | CRISPR gRNA cassette under a Pol-II promoter without ribozyme / Csy4 flanks → flag (5′ cap and polyA disrupt gRNA function). | HARD | Tsai 2014; Nissim 2014. |
| MR-51 | U6 / H1 / 7SK promoters: spacer must begin with G (or append a G) for transcription initiation. | SOFT | – |
| MR-52 | Mammalian polyA signal absent on a Pol-II-driven mRNA cassette → flag. | HARD | – |
| MR-53 | Bacterial terminator absent on a Pol-II-driven transcription unit → flag. | HARD | – |
| MR-54 | Mismatch between marker concentration in protocol vs database default for the host → flag. | SOFT | – |

### 4.2 Wet-lab workflow rules (WR)

| ID | Predicate | Severity | Rationale |
|---|---|---|---|
| WR-01 | The chosen polymerase is high-fidelity (Phusion / Q5 / KAPA HiFi / PrimeSTAR) when the PCR product will be cloned; Taq is not used for cloning amplicons. | HARD | Taq introduces too many errors for downstream use. |
| WR-02 | PCR template type is declared (plasmid / genomic / cDNA / synthetic). | SOFT | Affects cycle count and DpnI step. |
| WR-03 | If template is plasmid, DpnI digestion of the PCR product is included before transformation to remove template carry-over. | HARD | Otherwise empty parental vector dominates the colony pool. |
| WR-04 | For restriction-ligation, vector and insert are gel-purified before ligation (or PCR-cleaned if both produce clean amplicons). | SOFT | Avoids carry-over of un-cut vector. |
| WR-05 | For single-cut linearised vectors, dephosphorylation (CIP / rSAP / Antarctic phosphatase) is included to suppress religation. | HARD | Self-religation is the dominant background. |
| WR-06 | For double-digest, both enzymes are buffer-compatible (or sequential digestion is specified). | HARD | FR-ENZ-09. |
| WR-07 | For methylation-sensitive enzymes, the host genotype is dam+ / dcm+ or dam− / dcm− as required by the enzyme. | HARD | v2.0 § 7.2. |
| WR-08 | For Gibson assembly, fragments are mixed at 1:1 molar ratio (or 1:3 vector:insert for 2-piece); total DNA 50–100 ng. | SOFT | NEBuilder optimisation guide. |
| WR-09 | For Golden Gate, BsaI/BsmBI/SapI/BbsI is paired with T4 DNA ligase in the same reaction (one-pot). | HARD | – |
| WR-10 | For Golden Gate, the cycling programme alternates 37 °C and 16 °C and ends with a heat-inactivation step (60–80 °C). | SOFT | Engler 2008. |
| WR-11 | For Gateway BP / LR, Proteinase K stop step is included before transformation. | HARD | – |
| WR-12 | Transformation step specifies competent-cell type (chemical vs electro) and matches it to expected transformation efficiency target (≥ 10⁸ cfu/µg for high-throughput Golden Gate libraries; ≥ 10⁶ acceptable for routine cloning). | SOFT | – |
| WR-13 | Selection plate antibiotic concentration matches the host × marker matrix (FR-HOST-09). | HARD | – |
| WR-14 | Colony screening includes both colony PCR (rapid) and diagnostic restriction digest (more reliable). | SOFT | Mismatched results highlight chimeric clones. |
| WR-15 | Sequencing strategy covers every junction with ≥ 50 bp upstream and ≥ 50 bp downstream within Sanger read length. | HARD | FR-PRIM-09. |
| WR-16 | Constructs > 8 kb or containing repeats > 100 bp are sequenced by long-read (Nanopore / PacBio whole plasmid). | SOFT | Sanger cannot bridge such constructs reliably. |
| WR-17 | Glycerol stocks are made at 15–25 % glycerol final and stored at −80 °C. | HARD | – |
| WR-18 | For lentiviral and AAV transfer plasmid amplification, use a recombination-deficient host (Stbl3, Stbl4, NEB Stable). | HARD | LTRs and ITRs recombine in standard hosts. |
| WR-19 | For BAC propagation, use DH10B / EPI300 (recA-) at 30 °C if instability is observed. | SOFT | – |
| WR-20 | For very large constructs, use electroporation rather than chemical transformation. | SOFT | Chemical transformation efficiency drops sharply > 15 kb. |
| WR-21 | For ccdB-bearing destination vectors, propagate in DB3.1 or ccdB Survival 2 *only*. | HARD | – |
| WR-22 | For toxic-protein expression, the inducer is added when OD₆₀₀ ≈ 0.5–0.8, then growth at 16–25 °C overnight for solubility. | SOFT | Francis & Page 2010. |
| WR-23 | For disulfide-containing proteins, use SHuffle / Origami or co-express DsbC. | SOFT | – |
| WR-24 | For mammalian transient transfection, plate cells at 60–80 % confluence the day before; DNA:PEI mass ratio 1:3, 1 µg DNA per 1 × 10⁶ cells (default; per cell line). | SOFT | – |
| WR-25 | For lentivirus packaging, use HEK293T at 70–90 % confluence; co-transfect transfer + psPAX2 + pMD2.G; collect supernatant 48–72 h post-transfection. | SOFT | Dull 1998. |
| WR-26 | For agroinfiltration, OD₆₀₀ of *Agrobacterium* in infiltration buffer is typically 0.3–0.8; co-infiltrate p19 silencing suppressor at 1:1. | SOFT | – |
| WR-27 | For Sanger sequencing, sequencing primers anneal 50–100 bp upstream of the region of interest. | SOFT | First ~ 30 bp of a Sanger trace are unreliable. |
| WR-28 | DNA quality for sequencing must be > 50 ng/µL and A260/A280 in [1.8, 2.0]. | SOFT | – |
| WR-29 | For chemical transformation, heat shock at 42 °C for 30–45 s, then 2-min ice, then SOC recovery. | SOFT | – |
| WR-30 | For electroporation, DNA in salt-free buffer; cuvette gap matches voltage setting (1 mm = 1.8 kV, 2 mm = 2.5 kV). | SOFT | – |

### 4.3 Synthesis vendor / third-party supplier constraints (SR)

These are profile-driven; the system maintains one profile per vendor and selects based on user choice. The values below are *defaults as of 2024–2026* (per v2.0 KB § 11).

| ID | Predicate | Severity | Vendor profile field |
|---|---|---|---|
| SR-01 | Total synthesis length within vendor-specific bounds. **Twist gene fragments: 300–5 000 bp.** **Twist clonal genes: 300–5 000 bp.** **IDT gBlocks: 125–3 000 bp.** **IDT gBlocks HiFi: ≤ 5 000 bp.** **GenScript standard gene: ≤ ~10 000 bp.** | HARD | `min_length`, `max_length`. |
| SR-02 | Global GC content within vendor bounds. **Twist: 25–65 %.** **IDT: 25–75 %.** **GenScript: 30–70 %.** | HARD | `min_gc`, `max_gc`. |
| SR-03 | Per-50-bp-window GC within bounds. **Twist Express: 35–65 %, GC delta ≤ 52 %.** | HARD | `windowed_gc_min`, `windowed_gc_max`, `gc_delta_max`. |
| SR-04 | Homopolymer runs: **Twist: hard ban on ≥ 14 bp**. **IDT: ≤ 10 nt A/T, ≤ 6 nt G/C.** | HARD | `max_homopolymer_AT`, `max_homopolymer_GC`. |
| SR-05 | Direct repeats: ≥ 20 bp flagged; ≥ 40 bp rejected (most vendors). | SOFT / HARD | `max_repeat`. |
| SR-06 | Inverted repeats / hairpins: strong hairpins (ΔG ≤ -20 kcal/mol on ViennaRNA) rejected. | SOFT | `hairpin_max_negDG`. |
| SR-07 | Vendor-mandated 5′ / 3′ adapter sequences for certain products (e.g., Twist eBlocks have universal flanking; IDT gBlocks have no fixed flanking; clonal genes have vendor-specific cloning-site flanks). The system MUST include or strip these flanks based on vendor profile and intended assembly chemistry. | HARD | `flanking_5p`, `flanking_3p`, `flanking_handling`. |
| SR-08 | Vendor-mandated restriction sites for cloning into the supplied vector (e.g., a vendor's "ready-to-clone" service requires EcoRV blunt ends or specific Type IIS sites for direct subcloning). | HARD | `mandatory_sites`. |
| SR-09 | Vendor-forbidden patterns (vendor blacklists, IP-protected sequences, known toxic motifs). | HARD | `forbidden_patterns[]`. |
| SR-10 | Sequence complexity / linguistic complexity (vendor ML-based scoring; for software, a low-complexity windowed filter approximation). | SOFT | `complexity_threshold`. |
| SR-11 | Cost / price-tier thresholds (length, complexity, turnaround). The system MUST estimate the cost tier and warn before order. | INFO | `pricing_tiers`. |
| SR-12 | Pre-cloned vs linear-fragment: the user MUST be informed whether the vendor delivers the fragment ligated into a plasmid, or as a linear PCR-amplifiable fragment. | INFO | `delivery_format`. |
| SR-13 | Synthesis-vendor-side sequence screening (IGSC v3.0 compliant). The user is informed that the vendor will screen and may reject. | INFO | `screening_protocol`. |
| SR-14 | Codon-level rescue: if a sequence fails vendor constraints, the system MUST attempt synonymous-codon rewriting within the ORF to fix the violation without changing the protein, then re-check. | SOFT | – |
| SR-15 | Vendor turnaround time displayed (Twist: ~ 2 weeks; IDT: 1–2 weeks; GenScript: 2–3 weeks). | INFO | `lead_time_days`. |
| SR-16 | Twist Express-tier vs standard-tier eligibility (Express requires stricter GC, fewer repeats, no exotic adapters). | INFO | `service_tier_eligibility`. |
| SR-17 | If the construct exceeds any vendor's clonal-gene maximum, the system MUST automatically partition it into orderable fragments and design the assembly route (Gibson or Golden Gate). | SOFT | – |

### 4.4 Biosafety / biosecurity rules (BR)

| ID | Predicate | Severity | Rationale |
|---|---|---|---|
| BR-01 | Every construct MUST be routed through a configured screening adaptor (IGSC v3.0 / IBBIS Common Mechanism / SecureDNA / institutional blacklist). | HARD | v2.0 § 12. |
| BR-02 | A `hit` result from the screening adaptor MUST block ordering and route the construct to a designated reviewer (institutional biosafety officer / IBC). | HARD | – |
| BR-03 | A `watchlist` result MUST require explicit reviewer sign-off, recorded in provenance, before ordering. | HARD | – |
| BR-04 | The screening verdict MUST be persisted in the construct's metadata with timestamp and adaptor version. | HARD | – |
| BR-05 | Constructs containing any sequence from a Select Agent / pathogen on the HHS / USDA Select Agent list MUST trigger an automatic block regardless of screening verdict. | HARD | NIH Guidelines 2024; HHS list. |
| BR-06 | Constructs intended for *in-vivo* use, environmental release, or clinical-grade manufacturing MUST also undergo a stricter NIH Guidelines section IIIA/IIIB classification pass. | HARD | NIH Guidelines 2024. |
| BR-07 | The user MUST declare biosafety tier at design time; the system MUST refuse to compile if tier is unset. | HARD | – |
| BR-08 | Replication-competent viral vectors MUST be explicitly justified, flagged, and require dual sign-off. | HARD | – |
| BR-09 | The user MUST declare whether the construct uses any Risk Group 2+ organism component; if yes, dual sign-off required. | HARD | WHO LBM 4th ed. |
| BR-10 | The full biosafety / screening trail MUST be exportable as an audit document for institutional review. | HARD | – |
| **BR-11** *(added v1.2)* | `engine.sop_protocol` MUST NOT render an operational wet-lab protocol unless the user's administrator-granted `AuthorisationProfile` covers (a) the construct's biosafety tier, (b) the construct's host classes, (c) the construct's assembly chemistry, (d) the construct's downstream-use class, *and* the user's `UserDeclaration` (SOP library, biosafety approval ID, role-of-operation) lies inside the granted profile. Self-declaration by a `User` role MUST NOT lift this gate. | HARD | UR-09; ARCHITECTURE v1.2 §4.4 authorisation model. |
| **BR-12** *(added v1.2)* | Authorisation-profile mutation MUST require `AdminPrincipal` or `DeveloperBootstrapPrincipal` credentials and MUST emit an `AdminActionMinted` / `Modified` / `Revoked` event to the immutable audit log. `User` and `Reviewer` roles MUST NOT mutate any `AuthorisationProfile`. | HARD | UR-09; ARCHITECTURE v1.2 §4.4. |
| **BR-13** *(added v1.2)* | Tampered or expired `AuthorisationProfile` records MUST be rejected by the engine on load; integrity is enforced by institutional signature. | HARD | UR-09; ARCHITECTURE v1.2 R-16. |
| **BR-14** *(added v1.5)* | The `BlockOperationalProtocol` gate MUST fire whenever the construct's `RiskAdvisoryReport` contains an advisory of severity `caution` or `strong_caution` that has not been **explicitly acknowledged** by a signed `RiskAdvisoryAcknowledgement` whose `report_content_hash` and `construct_checksum` match the current versions. Passive UI dismissal MUST NOT satisfy this requirement. Declines and escalations route the construct to alternative workflows but do NOT unblock authorisation on their own. | HARD | UR-11; ARCHITECTURE v1.5 §1 objective 9 + §4.4 advisory gate + R-21. |

---

## 5. Non-functional requirements (NFR)

### 5.1 Performance

| ID | Priority | Requirement | Target |
|---|---|---|---|
| NFR-PERF-01 | MUST | Single-construct validation (full rule pipeline) completes in < 10 s for a 10 kb construct on a 4-core workstation. | benchmarked. |
| NFR-PERF-02 | MUST | Codon optimisation of a 1 kb ORF completes in < 5 s. | benchmarked. |
| NFR-PERF-03 | MUST | Golden Gate overhang-set optimisation for ≤ 20 fragments completes in < 60 s. | benchmarked. |
| NFR-PERF-04 | SHOULD | Batch validation of 1 000 constructs (combinatorial library) completes in < 30 min. | benchmarked. |
| NFR-PERF-05 | MUST | Sequence I/O (GenBank read, SBOL write, FASTA write) at ≥ 10 MB/s for a single file. | benchmarked. |

### 5.2 Usability

| ID | Priority | Requirement |
|---|---|---|
| NFR-USAB-01 | MUST | A junior researcher with no prior software experience can complete the white-paper Example A (bacterial enzyme expression construct) end-to-end within 30 min on first use. |
| NFR-USAB-02 | MUST | Every error / warning message references the rule ID, includes a one-sentence explanation, and provides at least one suggested remediation. |
| NFR-USAB-03 | MUST | All UI text is consistent with the white paper's terminology; every technical term has an in-app tooltip. |
| NFR-USAB-04 | SHOULD | Keyboard shortcuts and accessibility (WCAG 2.1 AA) supported. |

### 5.3 Reliability and data integrity

| ID | Priority | Requirement |
|---|---|---|
| NFR-REL-01 | MUST | No design change is persisted without writing the new version's checksum and a changelog entry. |
| NFR-REL-02 | MUST | The system MUST support automatic local backups of the project database (at least daily). |
| NFR-REL-03 | MUST | Sequence I/O MUST never silently lose annotations on round-trip. |
| NFR-REL-04 | MUST | All operations that modify constructs MUST be atomic — a crash mid-operation does not leave the database in an inconsistent state. |
| NFR-REL-05 | MUST | The validation rule registry version MUST be persisted with every validation report. |

### 5.4 Security

| ID | Priority | Requirement |
|---|---|---|
| NFR-SEC-01 | MUST | Sequence data may be confidential (IP, unpublished). Local-first storage; no cloud upload without explicit user consent. |
| NFR-SEC-02 | MUST | The screening adaptor channel MUST use a privacy-preserving query mode where supported (e.g., SecureDNA blinded queries). |
| NFR-SEC-03 | MUST | Per-user authentication if multi-user; audit log of who changed what. |
| NFR-SEC-04 | SHOULD | Encryption at rest for project databases (configurable). |
| NFR-SEC-05 | MUST | No telemetry without explicit user opt-in. |

### 5.5 Maintainability and extensibility

| ID | Priority | Requirement |
|---|---|---|
| NFR-MAINT-01 | MUST | New validation rules MUST be addable via a declarative registry without recompiling the core. |
| NFR-MAINT-02 | MUST | New parts catalogue entries MUST be addable via a data file without code changes. |
| NFR-MAINT-03 | MUST | New host strains MUST be addable via a data file. |
| NFR-MAINT-04 | MUST | New synthesis-vendor profiles MUST be addable via a data file. |
| NFR-MAINT-05 | MUST | New screening adaptors MUST be addable as plug-ins implementing the screening-hook contract (v2.0 § 12). |
| NFR-MAINT-06 | SHOULD | The parts catalogue, host database, enzyme database, and rule registry MUST be human-readable (YAML / TOML / JSON) so domain experts can review and edit them without programmer involvement. |

### 5.6 Compliance and licensing

| ID | Priority | Requirement |
|---|---|---|
| NFR-COMPLY-01 | MUST | The software's own licence is declared (project decision; recommend permissive open-source for the engine, possibly dual-licensed for institutional use). |
| NFR-COMPLY-02 | MUST | Every part shipped in the default catalogue declares its source licence (OpenMTA / UBMTA / public domain / vendor-restricted / custom). |
| NFR-COMPLY-03 | MUST | Output constructs inherit the most restrictive licence of their constituent parts; the system reports the resulting licence on every export. |
| NFR-COMPLY-04 | MUST | The software MUST NOT ship sequences that the project does not have licence to distribute. |
| NFR-COMPLY-05 | MUST | Third-party dependencies (ViennaRNA, SpliceAI, SignalP, etc.) MUST be inventoried with their licences in a `THIRD_PARTY_LICENSES.md` file. |

---

## 6. System / architectural constraints (SC)

| ID | Priority | Requirement |
|---|---|---|
| SC-01 | MUST | The internal data model MUST align 1:1 with the SBOL 3 ComponentDefinition / Sequence / Range / Role hierarchy so round-trip serialisation is direct. |
| SC-02 | MUST | The validation rule registry MUST be a typed, declarative artefact — not embedded in business logic — so rules can be reviewed by domain experts. |
| SC-03 | MUST | Plug-in contracts (screening adaptor, synthesis-vendor adaptor, codon-optimisation algorithm, RNA-folding back-end, splice-site predictor) MUST be declared interfaces that can be swapped without changes to the core. |
| SC-04 | MUST | The system MUST be runnable as a standalone CLI (Phase 7 of ROADMAP) before any UI is built; the UI is a wrapper over a tested CLI / API. |
| SC-05 | MUST | All sequence operations MUST be deterministic given the same inputs and the same rule-registry version. |
| SC-06 | MUST | The system MUST be testable end-to-end on the three worked examples from the white paper (§ 26–28). |
| SC-07 | SHOULD | The system SHOULD be language-agnostic in its file formats so that future implementations (in Python, Rust, TypeScript, etc.) can interoperate. |

---

## 7. Data model requirements (DR)

| ID | Priority | Requirement |
|---|---|---|
| DR-01 | MUST | Every typed entity (Part, Module, Construct, Host, AssemblyMethod, ValidationRule, ScreeningResult, ProtocolStep) MUST have a UUID, version, checksum, provenance, licence. |
| DR-02 | MUST | The `Part` type MUST carry a Sequence Ontology role; the `Sequence` type MUST carry an alphabet (DNA / RNA / protein); the `Range` type MUST carry start, end, strand, orientation. |
| DR-03 | MUST | The `Construct` type MUST aggregate Modules and emit a derived `full_sequence` plus a `feature_table` plus an `sbol_record`. |
| DR-04 | MUST | The `Host` type MUST declare: chassis class, compatible origins, compatible markers, codon-usage table, growth conditions, biosafety tier, references. |
| DR-05 | MUST | The `AssemblyMethod` type MUST declare: name, requires (constraints), scarless?, typical-max-fragments, optional overhang-fidelity-matrix reference, references. |
| DR-06 | MUST | The `ValidationRule` type MUST declare: ID, predicate (callable or declarative DSL), severity, citation, suggested remediation. |
| DR-07 | MUST | The `ProtocolStep` type MUST declare: step number, action, reagents (with vendor SKUs), quantities (with units), temperature, time, rationale, optional safety note. |
| DR-08 | MUST | The `ScreeningResult` type MUST declare: verdict (clear/watchlist/hit), adaptor name, adaptor version, evidence (list of structured matches), timestamp. |
| DR-09 | MUST | A `DesignSession` type MUST aggregate Construct, candidate methods, validation report, screening results, history (provenance graph). |
| DR-10 | MUST | All identifiers (UUIDs, versions, accessions) MUST be stored as strings; types MUST be JSON-serialisable. |

---

## 8. Acceptance criteria (AC)

A release is acceptable when every "MUST" passes its verification method, every "SHOULD" has been triaged into either implemented or explicitly deferred, and the following end-to-end acceptance tests pass:

| ID | Test |
|---|---|
| AC-01 *(software-side; revised per v1.4 M8 / B1)* | The bacterial Example A (white paper § 26 — His6-TEV-EnzymeA in BL21(DE3) via Gibson assembly) can be designed in the UI, validated with zero hard failures, has a `DesignRealisationPlan` rendered, has a `RiskAdvisoryReport` rendered, exports to GenBank that opens in SnapGene with all features preserved, has a sequencing-primer plan covering every junction with ≥ 50 bp upstream / downstream, and (in a separate dry-run path) the gated `SopLinkedProtocol` renders only when the test fixture supplies an administrator-minted authorisation profile and an institutional SOP template. **Wet-lab execution success is not a software release criterion**; it is performed as an empirical validation outside ordinary CI. |
| AC-02 *(software-side; revised per v1.4 M8 / B1)* | The mammalian Example B (white paper § 27 — CMV::mCherry::bGH for HEK293T transient via Golden Gate) can be designed, validated, has its `DesignRealisationPlan` + `ControlSet` + `RiskAdvisoryReport` rendered, the gated `SopLinkedProtocol` renders only when authorisation gates pass after screening completes. **Empirical wet-lab fluorescence verification is outside CI scope**; the software's role is verified by in-silico checks, expert review, and a dry-run walkthrough by a trained user. |
| AC-03 *(software-side; revised per v1.4 M8 / B1)* | The plant Example C (white paper § 28 — pTest::uidA::nos in pCAMBIA-derived binary vector for *N. benthamiana* agroinfiltration) can be designed in a multi-host context (E. coli cloning + Agrobacterium delivery + *N. benthamiana* target), validated with the role-keyed `HostContext` per host, has its `DesignRealisationPlan` rendered, the gated `SopLinkedProtocol` renders only when gates pass. **Empirical blue-staining verification is outside CI scope**; expert review verifies the design plan, controls, and gating behaviour. |
| AC-04 | All 50+ MR rules, 30+ WR rules, 15+ SR rules, and 10+ BR rules execute against a known-broken construct test set and produce the expected violations. |
| AC-05 | SBOL 3 round-trip on a curated set of 20 reference constructs is byte- or semantic-equivalent. |
| AC-06 | A combinatorial library of 100 promoter–RBS–ORF Golden Gate assemblies designs in < 30 min and the Pryor / Potapov overhang scores meet the kit-recommended threshold. |
| AC-07 | A junior researcher (persona) completes Example A from cold start (no prior software experience) within 30 min on first use, with the generated protocol producing a sequence-verified clone. |

---

## 9. Phasing alignment (MoSCoW × ROADMAP)

The MoSCoW priorities map to ROADMAP phases as follows:

| Phase (per ROADMAP.md) | MoSCoW items completed |
|---|---|
| Phase 1 — System architecture (`/architect`) | SC-01 … SC-07; DR-01 … DR-10 (designed but not yet implemented). |
| Phase 2 — Parts library & data model | FR-MOD-*, FR-ENZ-*, FR-HOST-* (catalogue side; compatibility-engine side begins Phase 3). |
| Phase 3 — Validation rule engine | FR-VAL-*; MR-*, WR-* (most); BR-* skeleton. |
| Phase 4 — Assembly-method picker | FR-CORE-12, FR-CORE-13; FR-PRIM-*. |
| Phase 5 — Sequence I/O & standards | FR-IO-*; FR-INT-01, FR-INT-03, FR-INT-09. |
| Phase 6 — Synthesis-vendor adaptor & screening hook | SR-*, BR-*; FR-INT plugin glue. |
| Phase 7 — End-to-end CLI | FR-INT-08; AC-01 dry-run. |
| Phase 8 — UI (deferred) | FR-UI-*; FR-INT-04 (live SnapGene channel); AC-01 / AC-02 / AC-03 full. |
| Phase 9 — Plant + mammalian end-to-end demos | AC-02, AC-03. |

---

## 10. Open questions / pending decisions

These items require decisions from the project sponsor or the architect during Phase 1.

| ID | Question |
|---|---|
| OQ-01 | Implementation language for the core engine — Python (best ecosystem for sequence work: Biopython, pySBOL, ViennaRNA bindings) vs Rust (performance) vs TypeScript (UI synergy). |
| OQ-02 | UI technology — desktop (Tauri, Electron) vs web (React + WebAssembly engine) vs hybrid. |
| OQ-03 | Local-first single-user vs server-with-multi-user from day one. |
| OQ-04 | Licence for the engine itself — permissive open-source (MIT / Apache 2.0) vs source-available institutional. |
| OQ-05 | Choice of in-process splice-site predictor (SpliceAI requires TensorFlow; lighter alternatives are NetGene2, NNSplice; or an HTTP service). |
| OQ-06 | Choice of in-process RNA folding (ViennaRNA Python bindings vs HTTP service vs lightweight pure-Python implementation). |
| OQ-07 | How tightly to couple to SnapGene — official SnapGene Server API (if available; check licensing), file-system watch, or both. |
| OQ-08 | Should the system support direct order placement with synthesis vendors (some have APIs) or remain submission-file-only? |
| OQ-09 | Should the rule registry be a YAML/TOML data file (easier for domain experts) or a Python module (easier for predicates with logic)? |
| OQ-10 | Multi-language UI strategy: English-first with i18n hooks, or design for bilingual English / Simplified Chinese from day one? |

---

## Appendix A — Traceability matrix to v2.0 KB

For audit purposes. Each requirement is mapped to the v2.0 KB section that justifies it.

| Requirement family | v2.0 KB section |
|---|---|
| Six-layer architecture | § 4 |
| FR-MOD-01 … FR-MOD-09 | § 5 (parts catalogue) and § 15 (data schema) |
| FR-HOST-01 … FR-HOST-12 | § 6 (host catalogue) |
| FR-ENZ-01 … FR-ENZ-12 | § 5.8 (tags, linkers, proteases) + § 7.2 (Type IIS enzymes) |
| FR-CORE-04 … FR-CORE-07 | § 3.4 codon-optimisation references; v2.0 §9 V016/V017 |
| FR-CORE-13 (overhang fidelity) | § 7.3 (Potapov 2018 + Pryor 2020) |
| FR-VAL-09 + MR-01 … MR-54 | § 9 (V001 – V025) and § 16 (failure modes) |
| FR-INT-09 (SBOL 3) | § 10 (interoperability standards) |
| SR-01 … SR-17 | § 11 (DNA synthesis vendor constraints) |
| BR-01 … BR-10 | § 12 (biosafety framework) |
| FR-PROJ-08 (MTA) + DR-* | § 13 (provenance and metadata) |
| FR-PROTO-01 … FR-PROTO-20 | § 14 (parameterised templates) + white paper §§ 18–20 (wet-lab workflows) + § 24 (lab realisation) |
| AC-01 / AC-02 / AC-03 | white paper §§ 26 / 27 / 28 (worked examples) |

---

## Appendix B — Glossary cross-reference

For terms used in this document but not defined here, see the glossary in `Cloning_Expression_Vector_Design_White_Paper.md` Appendix A. Key cross-references: `Vector`, `Cargo`, `MCS`, `Type IIS`, `MoClo`, `att site`, `Kozak`, `Shine–Dalgarno`, `WPRE`, `T-DNA`, `T7 promoter`, `Gibson assembly`, `Golden Gate`, `SBOL`.

---

## Appendix C — Sign-off

This requirements document is **Draft v0.1**. Recommended review path:

1. **Project sponsor** confirms UR-01 … UR-08 are correctly captured and the expanded set captures the intent.
2. **`/architect`** uses this document plus the v2.0 KB to produce `docs/architecture.md` (ROADMAP Phase 1 exit criteria).
3. **`/scientific-advisor`** (this skill) verifies each MR / WR / SR / BR rule against the v2.0 KB citation chain.
4. **`/dev-orchestrator`** consumes the prioritised MoSCoW × ROADMAP table to assemble the module registry for Phases 2–7.

---

*End of Software Requirements Specification — v0.1.*
