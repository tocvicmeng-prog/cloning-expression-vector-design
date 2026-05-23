# Cloning & Expression Vector Design Toolkit — First Edition

**Subtitle:** User Guide for Designing, Validating, and Preparing Expression Vectors for Wet-Lab Execution

**Author / Copyright:** (c) 2026 General Molecular Expression Service Pty Ltd (GMExpression(R), GMES). All rights reserved.

**Trademark notice:** GMExpression(R) is a registered trademark of General Molecular Expression Service Pty Ltd.

**License:** GPL-3.0-only. The Toolkit's source code is distributed under the GNU General Public License v3.0; this manual is licensed for use with the Toolkit and may be redistributed under the same GPL-3.0 terms. Third-party catalogue records carry their own licences; see `THIRD_PARTY_LICENSES.md` and `docs/ml_corpus/manifest.yaml`.

**Software version covered:** Cloning & Expression Vector Design Toolkit v0.2.1 (post-collaborative-audit-fix; 148-record ML corpus; 23-marker catalogue; 35+-host catalogue; 51 ports; Phase 0-13 complete).

**Edition:** First Edition.

**Manual revision date:** 2026-05-23.

**Research Use Only (RUO):** This software produces advisory research artefacts that are intended for in-silico design, peer review, and pre-bench planning. It does not authorise wet-lab work, does not bypass institutional biosafety committees, does not bypass synthesis-vendor screening, and does not constitute medical or regulatory approval for any clinical, diagnostic, therapeutic, environmental, or commercial use. Users remain responsible for institutional biosafety review (IBC), vendor screening, material-transfer obligations, and local regulatory compliance.

**Read this first:** read § Foreword and § How to read this guide before any other section. If you are about to install the software, skip to Appendix A. If you are about to design a vector for the first time, follow Part 1 then Part 3.

---

## Foreword

This manual is the first complete written gathering of everything a working molecular biologist needs to know to operate the Cloning & Expression Vector Design Toolkit (the "Toolkit") in a research environment, take a real biological objective from a one-sentence intent to a synthesis-ready design bundle, and prepare for the wet-lab execution that follows. It is written for graduate students, postdoctoral researchers, research technicians, junior scientists in industry, and biologically literate engineers who are joining a project that uses the Toolkit and want to become competent users quickly.

The Toolkit was developed by General Molecular Expression Service Pty Ltd (GMExpression, GMES) to make the design step of expression-vector construction (i) traceable, (ii) auditable, (iii) safe to share with collaborators, and (iv) reproducible across machines, time, and reviewers. It does this by separating four concerns that are usually mixed in commercial vector-design software: (1) the **design intent** (what the user wants to make and why), (2) the **construct model** (the typed graph of features, sequences, and coordinates), (3) the **validation report** (the engine's structured opinion on whether the construct meets molecular, host, assembly, biosafety, and synthesis-vendor constraints), and (4) the **export bundle** (the human-readable, machine-readable, and SOP-linked artefacts that leave the Toolkit and go to the bench, the synthesis vendor, the institutional biosafety committee, the collaborator, or the archive).

The manual is also a teaching artefact. We assume you have completed an undergraduate molecular-biology course and have at least one wet-lab cloning attempt under your belt (successful or otherwise). We do not assume that you know SBOL, you know how a hexagonal-architecture port works, you know the precise difference between a Golden Gate Type IIS overhang and a Gibson-compatible homology arm, or you have read the relevant Sambrook chapter recently. Where the science matters for using the tool correctly, we re-explain it. Where the architecture matters for trusting the output, we re-explain that too. Where the IP / licensing posture matters for sharing your work or building a commercial product on top, we say so explicitly.

This is the first edition. It documents v0.2.1 of the Toolkit and the corresponding documentation set (`README.md`, `ARCHITECTURE.md` v1.5, `REQUIREMENTS.md` v0.2 with the Enrichment Amendment of 2026-05-23, the Knowledge Base v2.0, the White Paper, and the 2026-05-23 handover memos). Subsequent editions will track Toolkit releases; the front-matter version line and revision date are the canonical pointer.

If the Toolkit's behaviour and this manual disagree, the Toolkit's behaviour (driven by `ARCHITECTURE.md`, `REQUIREMENTS.md`, and the YAML catalogues) is authoritative for the runtime; this manual is authoritative for the intended user experience and the conceptual model. Discrepancies should be reported via the project issue tracker.

---

## How to read this guide

This guide is built in **six concentric layers**. Pick the one that matches your role and time budget. Reading the whole book takes a working week; doing the **30-minute starter path** is enough to make your first useful design.

| Layer | Reader | Time | Path |
|---|---|---|---|
| 1. Quick-start | You need a vector by Friday | 30 min | Read § Quick-start workflow chart; install per Appendix A; follow Part 3.2 (Decision Wizard) end-to-end; export per Part 3.8 |
| 2. First-time user | You will use the Toolkit weekly | 4 h | Read Parts 1, 2 (relevant subsection), 3 in full; skim 4; consult 5 and Appendix J as needed |
| 3. Junior researcher | You will run designs for the team | 1-2 d | Read Parts 1-5; read Appendices A-E; skim F; consult G-J as reference |
| 4. Senior scientist / PI | You sign off other people's designs | 1-2 d | Read Parts 1, 2 (full), 3.6-3.10, 4, 5, 6; read Appendix F (architecture); review Appendix M (IP/licensing) |
| 5. Software developer / integrator | You extend the Toolkit | 1 wk | Read Part 6.3-6.5; read all Appendices F, H, M; cross-read `ARCHITECTURE.md` § 4 and `REQUIREMENTS.md` § 3 in the project root |
| 6. Institutional biosafety officer (IBC) | You sit on a review committee | 4 h | Read § Foreword, Part 1, Part 3.6-3.10, Part 5, Appendix M, and § Safety Notice in the README |

Cross-references in this manual use the form `Part 3.6` (chapter-and-section) or `App. F.4` (appendix-and-section). Every claim that depends on a peer-reviewed source carries a PubMed identifier (PMID) or canonical URL. Every place where the Toolkit's behaviour is governed by a project document (`REQUIREMENTS.md`, `ARCHITECTURE.md`, `CODING_AGENDA.md`, `TASK_BOARD.md`) cites that document by section.

**Notational conventions** used throughout:

- `monospace` — file path, command line, code identifier, YAML key, schema field, file format.
- *italic* — emphasis, technical term at first use, species or gene name where house-style requires italics.
- **bold** — actionable instruction, severity label, decision point.
- `[brackets]` — placeholder you must replace; for example `[your-construct-id]`.
- `>` — block quote, usually a citation or a callout.
- `M`, `S`, `C`, `W` — MoSCoW priority (Must, Should, Could, Won't) inherited from REQUIREMENTS.md.
- `INFO`, `SOFT`, `HARD` — Toolkit validation severities (advisory, warning that needs acknowledgement, blocking).
- `MR`, `WR`, `SR`, `BR`, `MS` — Toolkit rule categories: Molecular Rule, Wet-lab Rule, Synthesis-vendor Rule, Biosafety Rule, MS2-Specific (and related VLP) rule.
- `PMID nnnnnnnn` — PubMed identifier (NCBI). Plug into `https://pubmed.ncbi.nlm.nih.gov/<pmid>/` to retrieve the paper.

If you are about to print this manual, the printable assembly is intentionally portrait-orientation, monospace-friendly, and grayscale-readable. All Mermaid diagrams have an ASCII fallback in the immediate text below the diagram; all colour cues in tables are duplicated as text labels.

---

## Quick-start workflow chart

This is the canonical end-to-end design path. Every other workflow in the manual is a specialisation of this chart. Read this chart first; then dive into Parts 1-3.

```mermaid
flowchart TB
    start([Project intent]) --> wiz[Decision Wizard<br/>host, cargo, objective, tier]
    wiz --> imp{Import<br/>existing<br/>sequence?}
    imp -- Yes --> snap[BR-16: SnapGene<br/>manual cross-check]
    snap --> graph[Construct graph<br/>features, coords, provenance]
    imp -- No --> graph
    graph --> val[Validation Engine<br/>MR, WR, SR, BR, MS]
    val --> sev{Any HARD<br/>violation?}
    sev -- Yes --> redesign[Redesign<br/>see Part 5.5]
    redesign --> wiz
    sev -- No --> soft{Any SOFT<br/>warning?}
    soft -- Yes --> ack[Acknowledge / Decline /<br/>Escalate with signed<br/>DecisionRecord]
    ack --> screen
    soft -- No --> screen[Biosecurity Screening<br/>IGSC / IBBIS / SecureDNA]
    screen --> verdict{Verdict?}
    verdict -- CLEAR --> auth[Authorisation Gate<br/>admin-controlled profile]
    verdict -- WATCHLIST / MANUAL_REVIEW --> sign[Reviewer sign-off]
    sign --> auth
    verdict -- HIT --> block[Block export<br/>route to IBC]
    auth --> design[DesignRealisationPlan<br/>always renderable]
    auth --> bundle[Export Bundle<br/>GenBank + SBOL3 + FASTA<br/>+ manifests]
    design --> bench[Bench Execution<br/>Part 4]
    bundle --> bench
    bench --> qc[QC + Verification<br/>Part 5]
    qc --> done([Validated vector])
```

**ASCII fallback** (if your viewer does not render Mermaid):

```
[Project intent]
      |
      v
[Decision Wizard] --> [Import existing? Y -> BR-16 SnapGene cross-check] --> [Construct Graph]
                                                                                 |
                                                                                 v
                                                                       [Validation Engine]
                                                                        MR + WR + SR + BR + MS
                                                                                 |
                                                              +------------------+------------------+
                                                              |                                     |
                                                       HARD violation                        no HARD violation
                                                              |                                     |
                                                              v                                     v
                                                       [Redesign --> Wizard]                [SOFT warning?]
                                                                                                    |
                                                                                            Y       |       N
                                                                                            |       |       |
                                                                                            v       |       v
                                                              [Acknowledge / Decline / Escalate]  [Screen]
                                                                                            |
                                                                                            v
                                                                                       [Screen]
                                                                                            |
                                                                              CLEAR / WATCHLIST / HIT
                                                                                            |
                                                                              +-------------+-------------+
                                                                              |             |             |
                                                                          CLEAR       WATCHLIST          HIT
                                                                              |        / MANUAL_REVIEW    |
                                                                              |             |             v
                                                                              |       [Sign-off]   [Block + IBC]
                                                                              +------+------+
                                                                                     |
                                                                                     v
                                                                          [Authorisation Gate]
                                                                          (admin profile match)
                                                                                     |
                                                                                     v
                                                                  +------------------+------------------+
                                                                  |                                     |
                                                          [DesignRealisationPlan]              [Export Bundle]
                                                          always renderable                    GenBank + SBOL3
                                                                  |                                     |
                                                                  +-----------+-----------+
                                                                              |
                                                                              v
                                                                       [Bench Execution]
                                                                              |
                                                                              v
                                                                          [QC + Verify]
                                                                              |
                                                                              v
                                                                       [Validated vector]
```

The diagram captures four key invariants of the Toolkit's design (see § Foreword above and Appendix F for the architectural reasoning):

1. The **Decision Wizard** is the only sanctioned entry point for design intent. Free-text overrides are captured and surfaced to the validator and protocol generator (REQUIREMENTS.md FR-UI-03).
2. **Validation is structured and gated.** Any HARD violation blocks the flow; any SOFT warning of severity `caution` or `strong_caution` requires an active, signed acknowledgement before export — passive "dismiss" affordances are forbidden by architecture (ARCHITECTURE.md § 1.9 / FR-ADV-01..07).
3. **Screening is canonical and verdict-typed.** The Toolkit never silently produces a `CLEAR` from an unavailable adapter (M5 / B10 in ARCHITECTURE.md); fallback adapters cap at `MANUAL_REVIEW_REQUIRED`.
4. **The DesignRealisationPlan is always renderable**, but the SOP-linked operational protocol is rendered only after authorisation gates pass and screening has returned a permitted verdict (ARCHITECTURE.md § 1.8).

---

## Table of Contents

**Front matter**
- Title page, copyright, RUO disclaimer, version, date
- Foreword
- How to read this guide
- Quick-start workflow chart
- Glossary (after Part 6; see Appendix K for the long-form definitions)

**Part 1 - Orientation**
- 1.1 What is a vector? (plasmid vs viral)
- 1.2 What is an expression vector? (cassette anatomy)
- 1.3 Why design vectors with software first
- 1.4 What this Toolkit does and does not do
- 1.5 Typical workflow

**Part 2 - Common wet-lab needs**
- 2.1 E. coli protein expression
- 2.2 S. cerevisiae expression
- 2.3 Pichia (K. phaffii) secretion
- 2.4 Mammalian transient expression
- 2.5 Mammalian stable expression
- 2.6 Viral vectors (lenti / AAV / adeno / retro)
- 2.7 Fluorescent-protein reporter design
- 2.8 Selectable markers per host
- 2.9 CRISPR / Cas9
- 2.10 Antibody vectors

**Part 3 - Toolkit walkthrough**
- 3.1 Install and launch
- 3.2 Decision Wizard step by step
- 3.3 Importing existing sequences
- 3.4 Vector Map
- 3.5 Compatibility Matrix
- 3.6 Validation Report
- 3.7 Advisory Actions
- 3.8 Exporting Design Bundles
- 3.9 Admin / Review Queue
- 3.10 Audit Trail

**Part 4 - Bench execution**
- 4.1 Gene synthesis ordering
- 4.2 Receiving and assembling
- 4.3 Transformation into E. coli
- 4.4 Transformation into expression host
- 4.5 Verifying expression
- 4.6 Scale-up and purification

**Part 5 - QC and troubleshooting**
- 5.1 Pre-bench QC and manual SnapGene cross-check (BR-16)
- 5.2 At-bench QC
- 5.3 Post-expression QC
- 5.4 Troubleshooting decision tree
- 5.5 When to redesign

**Part 6 - Collaborators and downstream**
- 6.1 SnapGene
- 6.2 Benchling, ApE, GeneStudio
- 6.3 Synthesis-vendor handoff
- 6.4 IBC reporting
- 6.5 IP for commercialisation

**Appendices**
- A. Installation and configuration
- B. Detailed input requirements
- C. Process steps reference card
- D. Essential input and process checklist
- E. FAQ
- F. Architecture and working principles
- G. Fundamental molecular genetics, biochemistry, cell biology, and physics principles
- H. Basic formulas and theorems
- I. Standard wet-lab protocols
- J. Troubleshooting table
- K. Glossary expansion
- L. References / further reading
- M. IP / licensing / patent notice

**Back matter**
- Standard scientific-advisor disclaimer
- Revision history
- Colophon

---

## Glossary (short form; long-form definitions in Appendix K)

Reading order: read this glossary as a one-page orientation before tackling Parts 1-2. Every term that appears multiple times in the manual is defined here at first use; rare terms are defined inline.

- **AAV** — Adeno-associated virus; small ssDNA parvovirus widely used as a non-integrating gene-therapy vector. Requires ITR sequences and a specific capsid serotype.
- **Addgene** — A non-profit plasmid repository (Cambridge, Massachusetts) that distributes plasmids and educational eBooks for academic researchers. The Toolkit's documentation cites Addgene eBooks under nominative-use principles only (see Appendix M).
- **Adapter (architecture)** — A concrete implementation of a `Port` (interface) in the hexagonal architecture; e.g., the `GenBankAdapter` implements the `SequenceWriter` port.
- **Advisory** — A structured, signed warning emitted by the `engine.risk_classification` module; severities are `info`, `caution`, and `strong_caution`. Cautions and strong cautions require an active `acknowledge`, `decline`, or `escalate` action before authorisation can proceed (ARCHITECTURE.md § 1.9, FR-ADV-01..07).
- **Agrobacterium-mediated transformation** — A horizontal gene transfer process in which *Agrobacterium tumefaciens* delivers a T-DNA region into a plant cell.
- **Antibiotic marker** — A gene whose product confers resistance to a selective antibiotic, enabling selection of transformed cells.
- **Antibody vector** — A vector engineered to express an antibody fragment (scFv, Fab) or full-length immunoglobulin (IgG).
- **Authorisation Profile** — An administrator-controlled object listing the scopes of operation (biosafety tiers, vector classes, cargo classes, host roles) a user may declare; the engine validates the user's declared intent against the profile (ARCHITECTURE.md v1.2 sponsor sharpening; UR-09).
- **Audit log** — An append-only event stream of all governance-relevant actions (advisory acknowledgements, authorisation decisions, sign-offs, exports) bound to cryptographic signatures and content hashes.
- **BamHI** — A Type II restriction enzyme that recognises GGATCC and cuts between the G and the second G to leave a 5' overhang GATCC.
- **BL21(DE3)** — *E. coli* strain carrying a chromosomal copy of the bacteriophage T7 RNA polymerase gene under lacUV5 control; the canonical host for pET vectors and IPTG-inducible T7 expression.
- **BLAST** — Basic Local Alignment Search Tool; an algorithm and toolkit from NCBI for comparing sequences.
- **BR-16** — Toolkit-specific biosafety rule that requires a **manual** SnapGene cross-check before any exported design is committed to synthesis. The Toolkit will not automate this check.
- **BSL-1/2/3/4** — Biosafety Level 1 through 4; risk-graded laboratory containment classifications. BSL-4 is hard-blocked at compile time by the Toolkit (ARCHITECTURE.md § 1 item 16; FR-AUTH; M7).
- **CAI** — Codon Adaptation Index; a measure (Sharp & Li 1987, PMID 3447015) of how well a CDS uses the codons that are abundant in a target host's tRNA pool.
- **Cargo** — The biologically active payload of a vector: a coding sequence, a guide RNA, a reporter, a regulatory element, a viral genome.
- **CAS9** — A CRISPR-associated endonuclease from *Streptococcus pyogenes* (SpCas9) widely used for genome editing.
- **Cassette** — A complete, functional transcription unit: promoter -> 5' UTR -> CDS / sgRNA / cargo -> 3' UTR -> terminator. The minimal unit of expression design.
- **CDS** — Coding sequence; the portion of a gene that encodes a protein, beginning with a start codon and ending with a stop codon.
- **CEN/ARS** — *Saccharomyces cerevisiae* centromere/autonomously-replicating-sequence vector backbone; low-copy, stable (Sikorski-Hieter 1989 pRS series, PMID 2659436).
- **CHO** — Chinese Hamster Ovary cell line; the industry-standard mammalian production host for recombinant proteins.
- **CMV promoter** — Human cytomegalovirus immediate-early promoter; a strong constitutive promoter widely used in mammalian expression.
- **Codon optimisation** — Replacing codons in a coding sequence with synonymous codons preferred by the target host; usually performed against a Codon Adaptation Index (CAI) target.
- **Compatible ends** — Two restriction-enzyme overhangs that can be ligated together because their single-stranded extensions are reverse-complements of each other.
- **Construct graph** — The Toolkit's canonical typed representation of a vector: a directed graph whose nodes are `Part`, `Feature`, or `Module` and whose edges are typed (Adjacency, Regulatory, Derivation, Assembly).
- **CRISPR** — Clustered Regularly Interspaced Short Palindromic Repeats; an RNA-guided sequence-specific endonuclease system adapted for genome editing.
- **DerivationEnvironment** — A typed record capturing every input that materially changes the Toolkit's output (catalogue versions, adapter configurations, external database versions, SOP templates, locale, seeds, container image digest, user overrides, reviewer decisions). Hashed into every export bundle to enforce reproducibility (ARCHITECTURE.md § 1 item 6; C6).
- **DesignRealisationPlan** — The non-operational, always-renderable design output that captures assembly route, required inputs, QC checkpoints, expected verification artefacts, biosafety classification, and institutional-approvals list (ARCHITECTURE.md § 4.2 `engine.design_plan`).
- **Detection / Decision Wizard** — The structured step-wise UI that walks the user through objective, host, cargo, expression level, tagging, cloning chemistry, and biosafety tier (REQUIREMENTS.md UR-02, FR-UI-01..12).
- **EF1alpha** — Human elongation factor 1-alpha promoter; a strong mammalian constitutive promoter with lower silencing tendency than CMV in certain cell types.
- **EmblAdapter / Gff3Adapter** — Toolkit infrastructure adapters that serialise/deserialise EMBL and GFF3 sequence formats.
- **Expression vector** — A vector that drives transcription and, in coding cassettes, translation of an inserted cargo in a target host.
- **FASTA** — Plain-text sequence format; one or more records each starting with a `>` header line followed by sequence lines.
- **Feature** — A coordinate-anchored annotation on a `SequenceRecord`: a CDS, promoter, terminator, origin, primer-binding site, restriction site, etc.
- **FlpIn / Flp recombinase** — A site-specific recombinase from *S. cerevisiae* 2-mu plasmid that recombines `FRT` sites; basis of the Flp-In stable-line system in mammalian cells.
- **Fork-Readiness Memo** — A GMExpression project document declaring whether the codebase is suitable for forking into a closed-source commercial line, with explicit IP, licensing, and contributor-agreement context.
- **G418** — Geneticin; an aminoglycoside antibiotic used as a mammalian selection agent. Selection by the `neo` (kanamycin / G418 resistance) gene.
- **GAL1 promoter** — *S. cerevisiae* galactose-inducible promoter; tight, strongly induced by galactose, fully repressed by glucose.
- **Gateway cloning** — A recombinase-based (lambda Int/IHF) cloning chemistry from Thermo Fisher / Invitrogen; uses `attB`, `attP`, `attL`, `attR` sites and `LR` / `BP` reactions.
- **GenBank** — The NCBI sequence file format (`.gb`, `.gbk`) and database; the Toolkit's primary interchange format with SnapGene.
- **Gibson assembly** — Isothermal assembly chemistry (Gibson 2009, PMID 19363495) using a 5' exonuclease + a polymerase + a thermostable ligase; joins fragments via 15-40 bp homology arms in a single reaction at 50 deg C.
- **Glycerol stock** — A frozen 25-50% glycerol suspension of a bacterial culture stored at -80 deg C for long-term archival.
- **Golden Gate assembly** — Type IIS restriction-enzyme-based (BsaI, BsmBI, SapI) one-pot cloning chemistry using cut-away enzyme recognition sites and designed 4-nt overhangs (Engler 2008, PMID 18948503; Pryor 2018, PMID 30153100).
- **HEK293** — Human embryonic kidney 293 cell line; widely used for mammalian transient transfection and AAV / lentivirus production.
- **Hexagonal architecture** — A software architectural style (Alistair Cockburn) in which the application core has no knowledge of external systems; all external interactions go through `Port` interfaces with concrete `Adapter` implementations.
- **HardGate / SoftGate** — Toolkit-specific gates in the design pipeline: HardGate blocks export; SoftGate emits an advisory that requires acknowledgement.
- **Hygromycin B** — An aminoglycoside antibiotic used as a selection agent in bacteria, yeast, and mammalian cells; selection by the `hph` gene.
- **IBC** — Institutional Biosafety Committee; the body that reviews and approves recombinant-DNA research at a research institution.
- **IGSC** — International Gene Synthesis Consortium; a self-regulating consortium of synthesis vendors that screens orders against a harmonised list of pathogens and toxins.
- **In-Fusion** — A homology-based cloning chemistry from Takara Bio; conceptually similar to Gibson but uses a proprietary 3' exonuclease.
- **Intron** — A non-coding region within a eukaryotic gene that is spliced out of the pre-mRNA.
- **IPTG** — Isopropyl beta-D-1-thiogalactopyranoside; a non-metabolisable lactose analogue that induces lac-operon expression by binding LacI.
- **IRES** — Internal Ribosome Entry Site; an RNA structure that recruits ribosomes independently of cap-dependent scanning.
- **ITR** — Inverted Terminal Repeat; the AAV genome's hairpin termini required for packaging.
- **K. phaffii / Pichia pastoris** — A methylotrophic yeast widely used for high-density secreted-protein production.
- **Kozak sequence** — The consensus context around eukaryotic start codons (gccRccATGG, R = purine; Kozak 1986, PMID 3839802); strong Kozak contexts improve translation initiation efficiency.
- **LacI / lacO** — Repressor protein / operator DNA element of the *E. coli* lac operon; basis of IPTG-inducible expression in pET, pUC, and pTrc vectors.
- **Lentivirus** — A genus of retroviruses (Lentivirus genus, Retroviridae family). Third-generation packaging splits genome, helper, and envelope across three or four plasmids (psPAX2 + pMD2.G + transfer + RT).
- **Library** — In the Toolkit, a combinatorial collection of constructs declared via `OneOf` / `Variable` / `Override` parts; expanded lazily and deterministically (FR-CORE; UR-04; v1.0 round-3 finding).
- **Ligation** — The enzymatic joining of two DNA ends by T4 DNA ligase (or analogous), restoring the phosphodiester backbone.
- **Manual SnapGene cross-check (BR-16)** — A mandatory manual procedure in which the user opens an exported design in SnapGene, visually inspects the feature map and sequence, and records the check in a `DecisionRecord`. The Toolkit will not bypass or automate this step.
- **Marker** — Selection or counter-selection element. In v0.2 the Toolkit moved markers from `parts.yaml::markers` into a standalone `catalogues/markers.yaml` (UR-13; FR-MARK-01..12); the v0.2 catalogue covers 23 markers including bacterial antibiotic, yeast auxotrophic and dominant, and mammalian markers.
- **MCS** — Multiple Cloning Site; a short polylinker containing multiple unique restriction sites for traditional cut-and-paste cloning.
- **Mermaid** — A text-based diagram language rendered by GitHub and many modern Markdown viewers; the Toolkit's manuals embed Mermaid diagrams with ASCII fallbacks.
- **Module** — A typed group of related parts treated as a single unit (e.g., a complete expression cassette).
- **mScarlet / mNeonGreen / mTurquoise2** — Modern monomeric fluorescent proteins (Bindels 2017 PMID 27869816 / Shaner 2013 PMID 23685885 / Goedhart 2012 PMID 22426491) preferred for live-cell imaging over earlier-generation FPs.
- **NEBuilder HiFi** — NEB's commercial implementation of Gibson assembly chemistry, optimised for high fidelity.
- **NotI, AscI, PacI, FseI** — "Rare-cutter" 8-bp restriction enzymes useful for cloning into large constructs.
- **ORF** — Open Reading Frame; a stretch of DNA from a start codon to a stop codon without intervening stops in the same frame.
- **Origin of replication (ori)** — A DNA element from which replication initiates; controls copy number and host range.
- **Part** — In the Toolkit, the smallest addressable design element: a promoter, RBS, CDS, terminator, ori, marker, or other annotated feature with sequence and metadata.
- **pET** — Plasmid for Expression of T7 transcripts; a family of *E. coli* expression vectors driving T7-polymerase-dependent transcription (Studier 1990, PMID 2199796).
- **PCR** — Polymerase Chain Reaction; exponential amplification of DNA by repeated cycles of denaturation, primer annealing, and primer extension by a thermostable polymerase.
- **pichia** — see K. phaffii.
- **PMID** — PubMed identifier; the unique numeric ID for a PubMed-indexed publication.
- **Port (architecture)** — An abstract interface in hexagonal architecture; the Toolkit declares 51 ports under `domain.ports/` (REQUIREMENTS.md § 11; ARCHITECTURE.md § 4.2 / B7).
- **Primer** — A short single-stranded oligonucleotide (typically 18-30 nt) that primes DNA synthesis by a polymerase.
- **psPAX2 / pMD2.G** — The standard helper plasmids for third-generation lentivirus packaging (Gag-Pol-Rev-Tat-encoding helper and VSV-G envelope, respectively).
- **pUC origin** — High-copy ColE1-derived origin (250-700 copies per cell in *E. coli*); the standard for cloning vectors.
- **pX330 / pX458 / lentiCRISPR v2** — Widely used CRISPR-Cas9 plasmids from the Zhang lab (Addgene IDs 42230, 48138, 52961) for sgRNA + Cas9 co-expression.
- **RBS** — Ribosome Binding Site; in bacteria, the Shine-Dalgarno sequence upstream of the start codon.
- **Reporter** — A gene whose product is easily measured (fluorescence, luminescence, enzymatic activity).
- **REbase** — REBASE; the canonical restriction enzyme database (Roberts et al., PMID 25378308).
- **Restriction enzyme** — An endonuclease that cleaves DNA at or near a specific recognition sequence. Type II enzymes cut within their recognition site; Type IIS enzymes cut at a defined distance outside it.
- **RUO** — Research Use Only.
- **Sambrook 4th ed.** — Sambrook & Russell, Molecular Cloning: A Laboratory Manual, 4th edition (Cold Spring Harbor Laboratory Press, 2001). The Toolkit's canonical reference for working concentrations and standard protocols.
- **SBOL3** — Synthetic Biology Open Language v3.1.x; the standards-based interchange format the Toolkit uses internally.
- **scFv** — Single-chain variable fragment; an engineered antibody fragment fusing the V_H and V_L domains via a flexible peptide linker.
- **Screening adapter** — A Toolkit port (`ScreeningAdapter`) with concrete adapters for IGSC, IBBIS, SecureDNA, and an internal blacklist. Returns a typed verdict `{CLEAR, WATCHLIST, HIT, UNAVAILABLE, NOT_APPLICABLE, MANUAL_REVIEW_REQUIRED}`.
- **SecureDNA** — A privacy-preserving screening system for short DNA orders (Kim et al., 2024).
- **Selection marker** — see Marker.
- **sgRNA** — Single guide RNA; the chimeric tracrRNA-crRNA used to direct Cas9 to a genomic site.
- **Shine-Dalgarno** — A purine-rich sequence upstream of bacterial start codons that base-pairs with 16S rRNA.
- **SnapGene** — A commercial molecular-biology desktop application (Insightful Science / Dotmatics); the Toolkit's primary interoperability target.
- **SOP** — Standard Operating Procedure; an institutionally-approved protocol template.
- **SopLinkedProtocol** — The Toolkit's operational protocol output, bound to an institutional SOP template and gated by authorisation (ARCHITECTURE.md § 4.2 `engine.sop_protocol`).
- **STR** — Short Tandem Repeat; a polymorphic genetic marker used for cell-line authentication.
- **T7 RNA polymerase** — A bacteriophage RNA polymerase that recognises a specific T7 promoter; used in pET / BL21(DE3) IPTG-inducible expression.
- **TEF1 promoter** — *S. cerevisiae* translation elongation factor 1-alpha promoter; strong, constitutive.
- **Terminator** — A DNA element that signals transcription termination.
- **Topology** — Linear vs circular; recorded on every `SequenceRecord` in the Toolkit.
- **Transformation** — Introduction of exogenous DNA into a recipient cell (bacterial heat-shock, electroporation, yeast LiAc, mammalian lipofection / electroporation).
- **Twist Bioscience / IDT / GenScript** — Major commercial gene synthesis vendors; the Toolkit emits vendor-screened submission-ready files for all three (FR-PROTO; REQUIREMENTS.md § 3.7).
- **URA3 / LEU2 / HIS3 / TRP1** — Classical yeast auxotrophic markers; *S. cerevisiae* requires uracil, leucine, histidine, or tryptophan synthesis genes for growth on selective media.
- **Vector** — A DNA molecule that can replicate in a host and accept inserted cargo.
- **VLP** — Virus-Like Particle; a non-infectious self-assembled protein particle that resembles a virus.
- **VSV-G** — Vesicular Stomatitis Virus G envelope glycoprotein; provides broad tropism in pseudotyped lentivirus.
- **YPD** — Yeast extract Peptone Dextrose; the standard rich medium for *S. cerevisiae*.

---

# Part 1 - Orientation

## 1.1 What is a vector?

A **vector** is a DNA molecule that can (a) replicate independently in a host cell, and (b) accept inserted cargo. The word covers two structurally distinct biological objects: **plasmids** (covalently closed circular dsDNA molecules that replicate as physical entities separate from the chromosome) and **viral vectors** (recombinant viral genomes that exploit a virus's natural delivery and replication machinery to introduce cargo into target cells).

### 1.1.1 Plasmid vectors

A plasmid is a topologically circular, double-stranded DNA molecule typically 2-20 kilobase pairs (kbp) in size that lives autonomously in a bacterial or yeast cell (and, in the case of "shuttle" vectors, can be propagated across hosts). Plasmids replicate from a defined **origin of replication (ori)** that recruits the host's replication machinery; the chosen ori determines (i) which hosts the plasmid can replicate in, (ii) approximately how many copies per cell will be maintained (the **copy number**), and (iii) which other plasmid families can coexist in the same cell (the **incompatibility group**, "Inc").

The minimum elements of a useful plasmid are:

1. An origin of replication, governing copy number and host range.
2. A selection marker, allowing transformed cells to be distinguished from untransformed.
3. A multiple cloning site (MCS) or other insertion point that lets the user introduce cargo.

A working expression vector adds:

4. A promoter (transcription start), often inducible.
5. A 5' untranslated region (5'UTR) with translation initiation context (Shine-Dalgarno in bacteria; Kozak in eukaryotes).
6. The cargo CDS (or sgRNA, structural RNA, reporter cassette).
7. A 3' UTR (typically a polyadenylation signal in eukaryotes).
8. A transcription terminator.

Plasmids are the workhorse of molecular cloning: they are easy to maintain (transform into *E. coli*, grow overnight, mini-prep), easy to characterise (sequence with universal primers), easy to share (lyophilise, ship, retransform), and easy to combine (cut-and-paste with restriction enzymes, or assemble by Gibson or Golden Gate). Every major cloning vector family is a plasmid: pUC, pBR322, pET, pBAD, pTrc, pCDF, pRSF, pACYC, pCDFDuet, pBR322 derivatives in *E. coli*; pRS and YEp series in yeast; pcDNA in mammalian; pPICZ in *Pichia*; pCAMBIA and the binary vectors in plant.

### 1.1.2 Viral vectors

A viral vector exploits the natural delivery machinery of a virus to introduce cargo DNA or RNA into a target cell. Modern viral vectors are deliberately **replication-incompetent**: the viral genes required for packaging and capsid assembly are split off the transfer vector onto separate helper plasmids; the recombinant virus produced from the transfer vector lacks the genes it would need to propagate further. This is a fundamental safety design — see Part 2.6 for the third-generation lentivirus example, and Part 4.4 for the bench procedures.

The viral vectors covered by the Toolkit are:

- **Adeno-associated virus (AAV)** — small (4.7 kb single-stranded DNA) parvovirus; non-integrating (mostly); requires ITR sequences and a packaging plasmid encoding Rep + Cap proteins. The Toolkit supports AAV serotype declaration and ITR-aware capacity calculations (see Part 2.6).
- **Lentivirus** — ~9 kb single-stranded RNA virus (HIV-1-derived); third-generation packaging splits Gag-Pol-Rev-Tat-encoding helper functions across plasmids (psPAX2 + pMD2.G) and uses a self-inactivating (SIN) LTR. Integrates into the host genome.
- **Adenovirus** — ~36 kb double-stranded DNA virus; non-integrating; high-capacity (cargo space up to ~8 kb in first-generation, ~37 kb in gutted "high-capacity").
- **Retrovirus (gammaretrovirus)** — ~8 kb single-stranded RNA virus; integrates into the host genome. Now largely superseded by lentivirus for most applications because lentivirus can transduce non-dividing cells.

Each viral vector class introduces extra design constraints (cargo size limit, helper plasmid choices, packaging cell line, biosafety tier elevation) that the Toolkit's compatibility and validation engines understand. See Part 2.6 for a worked example.

### 1.1.3 Why "vector" matters as a software concept

The Toolkit treats a vector as a **typed construct graph**, not a sequence string. This is a deliberate choice driven by adversarial review (ARCHITECTURE.md § 3.1 round 1, finding C2): a flat sequence loses the relationships among parts, cannot express combinatorial libraries cleanly, and forces every downstream engine to re-parse coordinates. The construct graph has:

- **Nodes** of types `Part`, `Feature`, or `Module`.
- **Edges** typed as `Adjacency` (physical order), `Regulatory` (e.g., promoter -> CDS), `Derivation` (e.g., this construct is built from these parent parts), and `Assembly` (e.g., this fragment is one of several assembled by Gibson).
- **Topology** declared on every `SequenceRecord` (linear or circular).
- **Provenance** carrying the parent part(s), the user override (if any), the catalogue version, and the timestamp.

You do not have to manipulate the construct graph by hand: the Decision Wizard builds it for you. But understanding that the Toolkit's internal model is a typed graph (and not a string) explains why importing a plain FASTA sequence requires you to either accept the engine's annotation heuristics or supply features explicitly — the engine cannot guess where the promoter "should" be from sequence alone.

## 1.2 What is an expression vector?

An **expression vector** is a vector engineered to make the host cell produce the cargo's gene product in usable quantities. The defining feature that distinguishes an expression vector from a plain cloning vector is the **expression cassette**: a contiguous, in-cis arrangement of regulatory elements that drives transcription and (for protein cargos) translation of the cargo.

### 1.2.1 Anatomy of a bacterial expression cassette

A canonical bacterial expression cassette (e.g., a pET cassette) has, in 5' -> 3' order on the sense strand:

```
[promoter] - [operator] - [5' UTR + RBS] - [start codon] - [(N-terminal tag)] - [CDS] - [(C-terminal tag)] - [stop codon] - [terminator]
```

- **Promoter** — recruits RNA polymerase. For pET, the T7 promoter is recognised by T7 RNA polymerase (which is itself encoded on the chromosome of BL21(DE3) under lacUV5 control). For pBAD, the araBAD promoter is recognised by sigma-70 host RNAP but requires AraC for activation in the presence of L-arabinose. For pTrc, the trc hybrid promoter combines the -35 of trpA and the -10 of lacUV5.
- **Operator** — a DNA-binding site for a repressor; in pET this is the lac operator (lacO), bound by LacI in the absence of IPTG.
- **5' UTR + RBS** — the Shine-Dalgarno sequence (typically AGGAGG, 6-8 nt upstream of the start codon) that base-pairs with 16S rRNA to position the ribosome.
- **Start codon** — usually ATG; in *E. coli* GTG and TTG also initiate at lower efficiency.
- **N-terminal tag** (optional) — a small affinity or solubility tag (His6, FLAG, SUMO, MBP, GST, TRX) fused in-frame upstream of the cargo CDS.
- **CDS** — the protein-coding sequence.
- **C-terminal tag** (optional) — an affinity tag (His6, FLAG, Strep-II, Myc) fused in-frame at the C-terminus.
- **Stop codon** — TAA, TAG, or TGA. TAA is most efficient in *E. coli*; the canonical pET design uses two-stop "TAA TAA" to suppress readthrough.
- **Terminator** — typically a rho-independent terminator (a stem-loop followed by a polyU tract).

### 1.2.2 Anatomy of a mammalian expression cassette

A canonical mammalian expression cassette (e.g., a pcDNA3 or CAG cassette) has:

```
[5' enhancer/promoter] - [intron (optional)] - [5' UTR + Kozak] - [start codon] - [(N-terminal tag)] - [CDS] - [(C-terminal tag)] - [stop codon] - [3' UTR + polyA signal] - [(WPRE optional)] - [polyA cleavage site]
```

- **Promoter** — CMV (human cytomegalovirus IE), EF1alpha (human elongation factor 1-alpha), CAG (CMV early enhancer + chicken beta-actin promoter + rabbit beta-globin intron), SV40 (Simian Virus 40), PGK (phosphoglycerate kinase), UBC (ubiquitin C). Strength order roughly CMV >= CAG > EF1alpha >= UBC > PGK > SV40, but the absolute ranking depends on the cell type and silencing context.
- **Intron** (optional but often beneficial in mammalian) — facilitates nuclear export and translation; rabbit beta-globin intron is common.
- **5' UTR + Kozak** — the Kozak consensus gccRccATGG (R = A or G) around the start codon; a strong Kozak context provides a +1 G (at +4) and a purine at -3 (Kozak 1986, PMID 3839802).
- **CDS + tags** — as in bacterial; common mammalian tags include FLAG, HA, Myc, His6, GFP, mCherry, BAP (BirA-acceptor peptide).
- **Stop codon** — TAA or TGA preferred over TAG in mammalian cells.
- **3' UTR + polyA signal** — bovine growth hormone polyA (bGH polyA) or SV40 late polyA are the standard short, efficient polyadenylation signals.
- **WPRE (optional)** — Woodchuck Hepatitis Virus Post-transcriptional Regulatory Element; boosts expression of transgenes in some lentiviral and AAV contexts.

### 1.2.3 Yeast and other hosts

Yeast cassettes follow the eukaryotic template but with yeast-specific promoters (GAL1 inducible, TEF1 constitutive, PGK1 constitutive, ADH1 constitutive) and terminators (CYC1, ADH1). Pichia uses AOX1 (methanol-inducible) and GAP (constitutive). Plant cassettes use CaMV 35S (constitutive), Ubi (constitutive), or tissue-specific promoters, with the NOS or 35S polyA terminator. Insect (baculovirus) uses polyhedrin or p10 very-late promoters.

### 1.2.4 Why cassette anatomy matters for design

Every element in a cassette is a node in the Toolkit's construct graph. The Decision Wizard asks you to specify the cassette element-by-element (or accept the catalogue defaults for the host you selected). The validation engine then checks that the chosen elements are mutually compatible: a T7 promoter without BL21(DE3) (or another T7-expressing host) is flagged; a Kozak context that lacks the +1 G is downgraded; a bacterial cassette without a Shine-Dalgarno is blocked; a mammalian cassette without a polyA signal is blocked.

## 1.3 Why design vectors with software first

Until ~2010, most cloning vector design happened on paper or in SnapGene (released 2009) or on whiteboards in lab meetings. Designs were iterated by manual annotation, manual primer design (Primer3 in a browser), manual restriction-site mapping, and manual visual inspection. Errors were absorbed at the bench: a primer that primed off-target, a Kozak context that lost the +1 G, an ori that turned out to be Inc-compatible with a contaminating plasmid in the host. Each error cost a week of bench time, a week of sequencing time, and one synthesis order.

Modern cloning is increasingly **synthesis-first**: instead of cutting and pasting from existing plasmids, the user orders a synthesised insert from Twist, IDT, or GenScript that arrives in 5-10 business days. Synthesis is fast and accurate, but it is also a one-shot event: an error caught after synthesis costs a re-order ($100-$500) and 5-10 days of delay. An error caught after assembly and transformation costs an additional ~$200 of reagents and 3-5 days. An error caught after expression costs the whole project a week and a culture run.

Software-first design — where the construct is fully specified, validated, and bundled before any DNA is synthesised — collapses the cost of iteration to milliseconds. The Toolkit makes this practical for four reasons:

1. **The Decision Wizard captures intent in a form the engine can validate.** Free-form notes do not check; structured fields (host, cargo type, biosafety tier, induction system, tag) do.
2. **The validation engine catches more than a human reviewer would.** The 51-port architecture lets the engine consult external databases (codon tables, restriction enzyme databases, host catalogues, marker catalogues, screening services) without forcing the user to know the URLs.
3. **The export bundle is reproducible.** Every export carries a `DerivationEnvironment` hash that captures the exact catalogue versions, adapter configurations, and user overrides used; re-running with the same hash produces a bit-identical output.
4. **The audit trail is institutional-grade.** Every advisory acknowledgement, every authorisation, every export is signed and logged. This is what makes the Toolkit suitable for use in regulated environments: an IBC can replay the design from its hash and audit log months later.

A useful mental model: traditional vector design is a craft (knowledge in the head of the cloner); Toolkit-mediated design is a manufacturing process (knowledge in catalogues and rules, applied uniformly across users and time). Both are needed; the Toolkit augments and audits the craft, not replaces it.

## 1.4 What this Toolkit does and does not do

### 1.4.1 What the Toolkit does

The Toolkit, in v0.2.1:

- Captures design intent through a **Decision Wizard** with cited defaults, free-text overrides, and lockable modules (UR-02; FR-UI-01..12).
- Represents designs as a **typed construct graph** with coordinate-aware features and provenance (C2; FR-MOD-01..08).
- **Validates** the design against:
  - Molecular rules (`MR-*` — promoter-host fit, Kozak strength, RBS suitability, marker-host links, copy-number incompatibility, restriction-site uniqueness, codon-context constraints).
  - Wet-lab rules (`WR-*` — assembly-chemistry compatibility, fragment-size limits, overhang fidelity, primer Tm consistency).
  - Synthesis-vendor rules (`SR-*` — vendor sequence prohibitions, repeat-content thresholds, GC-window constraints, length / cost thresholds).
  - Biosafety rules (`BR-*` — biosafety tier, high-risk-element flags, replication-competence, host-tier compatibility, BR-16 manual SnapGene cross-check).
  - MS2 / VLP-specific rules (`MS-*` — packaging-signal handling, capsid expression policy, helper-function separation).
- Routes advisory cases through **signed decision records**, role snapshots, review queues, and an immutable audit trail (UR-09..11; FR-AUTH-*; FR-ADV-*).
- Performs **biosecurity screening** through configured external adapters (IGSC, IBBIS, SecureDNA, internal blacklist) with a typed verdict that includes `MANUAL_REVIEW_REQUIRED` as a first-class outcome (BR-*; M5; B10).
- Generates a **DesignRealisationPlan** (non-operational, always renderable) and — only when authorisation gates pass — a **SopLinkedProtocol** (operational, gated to institutional SOPs).
- Supports **standards-based export** in GenBank, SBOL 3.1.x, FASTA, EMBL, and GFF3, plus SnapGene round-trip (FR-INT-01..12).
- Provides a **React + TypeScript** workspace UI with construct maps (circular and linear), compatibility matrix, validation report, advisory actions, admin queue, audit log, and design diff (Phase 12).
- Provides a **CLI and HTTP API** for headless workflows and automated pipelines.
- Maintains **manifests, event streams, deterministic renderers, release fixtures, and CI gates** to preserve traceability across forks, machines, and time.

### 1.4.2 What the Toolkit does not do

- It does **not** authorise wet-lab work. The DesignRealisationPlan is reviewable, not operational; the SopLinkedProtocol is operational only when an Administrator has granted a matching `AuthorisationProfile` (UR-09).
- It does **not** bypass institutional biosafety committees. The Toolkit's BiosafetyClassificationLayer flags candidate-IBC-relevant designs but the IBC's decision is binding (UR-11).
- It does **not** bypass synthesis-vendor screening. Vendor adapters expose `CLEAR / WATCHLIST / HIT / UNAVAILABLE / MANUAL_REVIEW_REQUIRED` verdicts; the user must escalate any `HIT`.
- It does **not** treat LLM text as authoritative scientific evidence. LLM-assisted constraint translation (UR-02 free-text channel) is captured as a `ConstraintTranslator` snapshot and routed through citation, policy, and review controls (M10 in ARCHITECTURE.md).
- It does **not** automatically scrape or fetch sequences from SnapGene. The SnapGene cross-check (BR-16) is **manual**, by a human in a browser, with the result recorded as a `DecisionRecord`.
- It does **not** perform freedom-to-operate (FTO) analysis. That belongs to the `/ip-auditor` skill and is out of scope for v0.2.1.
- It does **not** ingest wet-lab data (Sanger trace QC, gel-image OCR). Those workflows live downstream.
- It does **not** support BSL-4 work. BSL-4 is hard-blocked at compile time with an explicit reason message (M7).
- It does **not** authorise clinical, diagnostic, therapeutic, or environmental-release use. **Research Use Only.**

The Toolkit is the design and validation layer above the bench and below the synthesis vendor. It is sized for that role.

## 1.5 Typical workflow

The annotated workflow chart in § Quick-start shows the canonical path. Here is the same path described in working language, with the typical times and human decisions at each step.

1. **Define the intent** (10-30 min). Sit down with the Decision Wizard. Specify host, cargo, expression level, induction system, tag strategy, cloning chemistry, biosafety tier. Use the free-text fields for anything the dropdowns do not cover; the engine will surface those notes to the validator.

2. **Import or design parts** (10 min - 1 h). If you have an existing backbone or cargo sequence, import it (GenBank, FASTA, SBOL, SnapGene `.dna`). Cross-check in SnapGene (BR-16). Otherwise, pick parts from the catalogue and let the Wizard arrange them.

3. **Inspect the construct graph** (5-15 min). Open the Vector Map (circular and linear views). Confirm the order, orientation, and annotation of every feature. Open the Compatibility Matrix; confirm the host catalogue and marker catalogue have not flagged a conflict.

4. **Read the Validation Report** (10-30 min). Read every advisory in order. For each `caution` or `strong_caution`, decide whether to acknowledge (with a justification of >= 20 characters), decline (which routes to an alternative reviewer), or escalate (which requires institutional sign-off). Sign each decision; the DecisionRecord is committed to the audit log.

5. **Run screening** (1-5 min real time; 5 min - 24 h adapter time, depending on provider). The Toolkit submits the assembled construct to the configured screening adapter(s). The verdict comes back as `CLEAR`, `WATCHLIST`, `HIT`, `UNAVAILABLE`, `NOT_APPLICABLE`, or `MANUAL_REVIEW_REQUIRED`. A `HIT` blocks export; a `WATCHLIST` requires Reviewer / Administrator sign-off; a `CLEAR` advances.

6. **Authorisation gate** (1-2 min if your profile covers the construct; days or weeks if you need an Administrator to grant a new profile). The user declares intent (SOP library, biosafety approval ID, operational role); the engine validates the declaration against the Administrator-granted `AuthorisationProfile`. Declarations that exceed the profile are rejected with a clear reason.

7. **Render the DesignRealisationPlan and the export bundle** (1-2 min). The Toolkit assembles the GenBank, SBOL3, and FASTA outputs, the primer set, the assembly route, the QC checkpoints, the institutional-approvals list, the biosafety classification, and the DerivationEnvironment hash into a ZIP archive ready to share, archive, or submit to a synthesis vendor.

8. **Optional: render the SopLinkedProtocol** (if authorisation gate has passed). The operational protocol is bound to an institutional SOP template and is role-gated.

9. **Bench execution** (1-4 weeks depending on chemistry, scale, and host). Part 4 covers the bench procedures end-to-end.

10. **QC and verification** (1-2 weeks). Part 5 covers pre-bench QC, at-bench QC, post-expression QC, and the decision tree for when to redesign.

The total wall-clock time from intent to a synthesis-ordered construct in v0.2.1 is typically a working day for an experienced user. Most of that time is **reading the validation report carefully**, not waiting for the engine; the engine itself runs in < 2 seconds for typical single-construct designs, and the export-bundle generation in < 10 seconds (NFR performance budget in REQUIREMENTS.md).

---

# Part 2 - Common wet-lab needs

This part is a structured catalogue of the wet-lab applications the Toolkit was built to serve. For each application we present a five-block answer: **wet-lab goal**, **typical inputs you must provide**, **what the Toolkit will produce**, **bench action that follows**, and **common failure modes the Toolkit can or cannot catch**. Cross-references to the worked walkthrough in Part 3 and to the relevant standard protocols in Appendix I are included for every entry.

Each subsection ends with a short table summarising the canonical vector families, the recommended assembly chemistry, and the host strains the Toolkit knows about. The catalogues themselves are authoritative: if the Toolkit knows a strain or a vector that this manual omits, trust the catalogue and report the manual as out of date.

## 2.1 E. coli protein expression

### 2.1.1 Wet-lab goal

Produce a heterologous protein from a cargo coding sequence in *Escherichia coli*, in soluble form, at a scale sufficient for purification (typical micrograms to grams) and downstream use (biochemical assay, crystallography, antibody generation, enzyme characterisation, cell-free reaction component, immunisation antigen).

This is the most common cloning task in molecular biology. Roughly two-thirds of all recombinant proteins in research labs are produced first in *E. coli*. The host is fast (doubling time ~ 20 min), cheap (LB or 2xYT media, room-temperature shake flask), genetically simple (no introns, no significant post-translational modifications for most proteins), and well-characterised (decades of literature on every common vector).

### 2.1.2 Typical inputs

You must specify:

- The **target protein sequence** (either as an amino-acid sequence the Toolkit will codon-optimise, or as a native CDS the Toolkit will validate but not re-optimise).
- The **target host strain** — typically BL21(DE3) for T7-driven IPTG induction; BL21(DE3)pLysS for tighter pre-induction repression; Rosetta(DE3) or pRARE-containing strains for rare-codon supplementation; SHuffle or Origami for disulfide-bond formation; Lemo21(DE3) for tuneable T7 polymerase expression; C41(DE3) / C43(DE3) for toxic / membrane proteins; Arctic Express for cold-induction.
- The **promoter / induction system** — T7 (pET, IPTG); araBAD (pBAD, L-arabinose); trc (pTrc, IPTG); tac (pGEX, IPTG); rhaBAD (rhamnose); tet (anhydrotetracycline). The system determines the host requirements.
- The **expression strength target** — low (basal leak), medium (titrated IPTG), high (full IPTG induction).
- The **N- and C-terminal tag choices**, with linker preferences. Common tags: His6 (affinity), MBP (solubility + affinity), GST (solubility + affinity), SUMO (solubility + native N-terminus on cleavage), TRX (solubility), FLAG (epitope), Strep-II (affinity), TEV / PreScission protease site (cleavable linker).
- The **cloning chemistry**: restriction + ligation (NdeI / NcoI / XhoI / BamHI / HindIII into a pET MCS), Gibson, NEBuilder HiFi, Golden Gate (BsaI for MoClo-pET), In-Fusion, LIC (pET-LIC).
- The **biosafety tier** — usually RG1; elevate to RG2 if the cargo is from a Risk Group 2 organism or is a known toxin.

### 2.1.3 What the Toolkit produces

- A fully annotated GenBank file of the assembled expression vector.
- A SBOL3 record of the same construct.
- A FASTA file with the insert and primer set.
- A primer set with annealing temperatures, off-target scan against the full plasmid, and synthesis vendor recommendation.
- A codon-optimised insert (CAI >= 0.7 against *E. coli* K-12 by default; tunable via overrides).
- An assembly route specific to the chosen chemistry, with fragment specifications, expected Tm, and overhang fidelity scores (Pryor 2018 PMID 30153100 for Golden Gate).
- A list of QC checkpoints (diagnostic restriction digest, Sanger sequencing primers, colony PCR primers).
- A biosafety classification record (typically Risk Group 1 unless the cargo elevates it).
- A DesignRealisationPlan with the assembly route, required reagents, and expected verification artefacts.
- A DerivationEnvironment hash for reproducibility.

### 2.1.4 Bench action that follows

A typical Gibson-assembled pET-BL21(DE3) workflow (see Appendix I for protocols):

1. Order the synthesised insert from Twist / IDT / GenScript (5-10 business days).
2. Receive insert; resuspend in TE to a working concentration (typically 10 ng/uL).
3. PCR-amplify or restriction-digest the backbone to linearise it.
4. Set up the Gibson reaction (NEBuilder HiFi, 50 deg C, 15-60 min) with 1:2 backbone-to-insert molar ratio.
5. Transform 2 uL of the Gibson reaction into chemically competent DH5-alpha or NEB-5alpha (Appendix I § I.7).
6. Plate on LB + antibiotic; incubate 37 deg C overnight.
7. Pick 4-8 colonies; mini-prep each (Appendix I § I.1).
8. Verify by diagnostic restriction digest (Appendix I § I.2) and Sanger sequencing.
9. Re-transform the verified plasmid into BL21(DE3) (Appendix I § I.7).
10. Test small-scale expression (typically 5 mL LB + antibiotic; induce with 0.1-1 mM IPTG at OD600 ~ 0.6; grow 4 h at 37 deg C or overnight at 18 deg C).
11. Analyse soluble vs insoluble fractions by SDS-PAGE (Appendix I § I.14).
12. If expression is good, scale up; if poor, troubleshoot via the decision tree (Part 5.4 / Appendix J).

### 2.1.5 Common failure modes

| Failure mode | Will Toolkit catch? | How |
|---|---|---|
| Promoter-host mismatch (e.g., T7 promoter without DE3 host) | Yes | `MR-PROMOTER-HOST` advisory + Compatibility Matrix |
| Missing or weak Shine-Dalgarno | Yes | `MR-RBS-MISSING` / `MR-RBS-WEAK` advisory |
| In-frame stop codon in synthesised insert | Yes | `MR-INFRAME-STOP` advisory |
| Rare-codon clusters | Yes | `MR-CODON-RARE-CLUSTER` advisory (run codon optimiser) |
| Wrong selection marker for strain background | Yes | `MR-MARKER-MISMATCH` advisory (introduced in v0.2 with the markers catalogue) |
| Protein toxic to host | No (use C41 / C43 / pLysS) | Out of scope; flagged in the Validation Report Notes if a known-toxic CDS is detected |
| Insoluble inclusion bodies | No (use tagged construct, lower temperature, slower induction) | Out of scope; design-level advice in App. J row "Inclusion bodies" |
| Insert too large for synthesis vendor's single-fragment limit | Yes | `SR-LENGTH-OVER-VENDOR` advisory |
| Sequence with vendor-prohibited motif (e.g., long homopolymer) | Yes | `SR-VENDOR-PROHIBITED` advisory |
| Codon usage causes secondary RNA structure at RBS | Partial | `MR-RBS-OCCLUDED` advisory (uses RNA-folding adapter if available) |

### 2.1.6 Canonical reference table — E. coli protein expression

| Vector family | Promoter / inducer | Marker (per `markers.yaml`) | Recommended strain |
|---|---|---|---|
| pET-15b / 21a / 22b / 24a | T7 / IPTG | Amp (Carb) | BL21(DE3), Rosetta(DE3), Origami(DE3) |
| pET-28a/b/c | T7 / IPTG | Kan | BL21(DE3) |
| pET-30 | T7 / IPTG | Kan | BL21(DE3) |
| pBAD/HisA/B/C | araBAD / L-arabinose | Amp | TOP10, LMG194 |
| pTrc99A | trc / IPTG | Amp | DH5-alpha, JM109 |
| pGEX-4T-1 | tac / IPTG | Amp | BL21, BL21(DE3) |
| pMAL-c5x | tac / IPTG | Amp | NEB Express, BL21 |
| pCDFDuet-1 | T7 / IPTG | Spec | BL21(DE3) |
| pRSFDuet-1 | T7 / IPTG | Kan | BL21(DE3) |
| pACYCDuet-1 | T7 / IPTG | Cm | BL21(DE3) |
| pLysS / pLysE add-on | constitutive T7 lysozyme | Cm | BL21(DE3)pLysS |
| pRARE add-on | constitutive rare-tRNA cluster | Cm | Rosetta(DE3) |

References: Studier 1990 (PMID 2199796) for T7/pET; Guzman et al. 1995 (PMID 7768838) for pBAD/araBAD; Sambrook 4th ed. Appendix A1 for working concentrations; Beck et al. 1982 (PMID 6296021) for kanamycin mechanism. The Toolkit's `catalogues/markers.yaml` is the authoritative concentration record (see Part 3.5).

## 2.2 S. cerevisiae expression

### 2.2.1 Wet-lab goal

Express a heterologous protein in *Saccharomyces cerevisiae*. Yeast is preferred over *E. coli* when (a) the cargo requires eukaryotic post-translational modifications (N-glycosylation, disulfide bonds, certain phosphorylations), (b) the cargo is a membrane protein that needs eukaryotic membrane insertion machinery, (c) the cargo is an enzyme whose substrate is naturally eukaryotic, (d) the cargo is intended for downstream tests in a eukaryotic background. Yeast is also the standard host for two-hybrid (Y2H) screens, synthetic-biology pathway engineering, and metabolic engineering.

### 2.2.2 Typical inputs

- **Target protein** (amino-acid sequence or native CDS).
- **Vector backbone class**:
  - **2-mu (multi-copy)** for high-expression episomal work (YEp, pYES2, pESC, pRS42x series).
  - **CEN/ARS (low-copy)** for stable, single-copy episomal work (pRS41x series — pRS413/414/415/416/426 from Sikorski-Hieter 1989, PMID 2659436; Brachmann 1998, PMID 9483801).
  - **Integrating** (pRS40x) for chromosomal integration at the auxotrophic-marker locus.
- **Auxotrophic marker** — URA3, LEU2, HIS3, TRP1, MET15, LYS2. Choose a marker that complements an auxotrophy in the strain you will transform.
- **Dominant marker (alternative)** — KanMX (G418), HphMX (Hygromycin B), NatMX (clonNAT), BleMX (Zeocin) for prototrophic strains or industrial settings.
- **Promoter** — TEF1 (constitutive, strong), PGK1 (constitutive, medium-strong), ADH1 (constitutive, medium), GAL1 (galactose-induced, tight, very strong), CUP1 (copper-induced), MET25 (methionine-repressed). The Toolkit knows the strength and induction profile of each.
- **Terminator** — CYC1 (canonical), ADH1, TDH3.
- **Strain** — BY4741 (MATa his3 leu2 met15 ura3, the canonical EUROSCARF deletion-collection background; Brachmann 1998 PMID 9483801), BY4742 (MAT-alpha), W303 (his3 leu2 trp1 ura3 ade2 can1), CEN.PK (industrial background), INVSc1 (commercial expression strain), YPH499/500 (his3 leu2 lys2 trp1 ura3).
- **Tags** — typically C-terminal in yeast for in-vivo work; common: His6, FLAG, HA, GFP, mCherry, TAP-tag (Rigaut 1999), PrA/PrG for affinity, BAP/Avi for biotinylation.

### 2.2.3 What the Toolkit produces

- Annotated GenBank / SBOL3 / FASTA of the assembled vector.
- A primer set for amplifying the cargo, the backbone segments, and Sanger sequencing primers.
- A codon-optimised insert against *S. cerevisiae* (uses the codon usage from Sharp & Cowe 1991 by default).
- Assembly route (Gibson, Golden Gate-YTK, or restriction-ligation).
- QC checkpoints.
- A biosafety classification (RG1 for laboratory *S. cerevisiae* strains).
- Marker-host link advisories (the v0.2 `markers.yaml` catalogue has explicit `compatible_hosts` for every auxotrophic and dominant marker; the engine flags mismatches such as URA3 on a `ura3-Delta0` strain that is missing this auxotrophy).

### 2.2.4 Bench action that follows

A typical pRS415-GAL1::CARGO-CYC1term workflow into BY4741:

1. Order the synthesised insert (or PCR-amplify from a parent plasmid).
2. Assemble into pRS415 backbone by Gibson (50 deg C, 60 min) or by restriction-ligation (SacI / XbaI in pRS415 MCS).
3. Transform the assembly into chemically competent NEB-5alpha or DH5-alpha for amplification in *E. coli* (the pRS series carries pUC ori + Amp for *E. coli* maintenance).
4. Mini-prep; verify by restriction digest and Sanger.
5. Transform the verified pRS415-CARGO into BY4741 by the lithium acetate / PEG / heat-shock method (Appendix I § I.10; Gietz & Schiestl 2007 PMID 17401334).
6. Plate on SD -Leu (synthetic complete medium without leucine) at 30 deg C. Colonies typically appear in 2-3 days.
7. Pick colonies; verify integration / episomal carriage by colony PCR.
8. Test expression: grow in SD -Leu + 2% raffinose to mid-log (OD600 ~ 0.5); induce with 2% galactose; harvest at 4 h, 8 h, or 24 h depending on the cargo.
9. Lyse by glass-bead beating (or by enzymatic lyticase + freeze-thaw); SDS-PAGE / Western blot to confirm expression.

### 2.2.5 Common failure modes

| Failure mode | Will Toolkit catch? |
|---|---|
| Auxotrophic marker mismatch (e.g., URA3 on a ura+ strain) | Yes (v0.2 markers catalogue + `MR-MARKER-MISMATCH`) |
| GAL1 promoter used in CEN.PK (which has GAL1 fully functional) without acknowledging glucose repression | Partial (advisory note) |
| 2-mu and CEN backbones cross-loaded into the same strain (incompatibility) | Yes |
| Wrong yeast codon table for the strain background | Yes if the Wizard specified the strain; otherwise default S. cerevisiae K-table |
| Missing yeast Kozak (yeast prefers a different context from mammalian; Cigan 1988 PMID 3300555) | Partial — advisory |
| Insert too large for one synthesised fragment | Yes (`SR-LENGTH-OVER-VENDOR`) |
| Promoter contains rare *E. coli* codon clusters that affect amplification | No (out of scope for yeast cassette validation) |

### 2.2.6 Canonical reference table — S. cerevisiae

| Backbone family | Type | Marker | Strain example |
|---|---|---|---|
| pRS413 / 414 / 415 / 416 | CEN/ARS, low-copy | HIS3 / TRP1 / LEU2 / URA3 | BY4741, BY4742, W303 |
| pRS423 / 424 / 425 / 426 | 2-mu, high-copy | HIS3 / TRP1 / LEU2 / URA3 | BY4741, BY4742, W303 |
| YEp series | 2-mu, high-copy | various | various |
| YIp / pRS40x | integrating | various | various |
| pYES2 / pYES2.1 | 2-mu, GAL1-driven | URA3 | INVSc1 |
| pESC-His / -Leu / -Trp / -Ura | 2-mu, GAL1/GAL10 dual | various | INVSc1 |
| pYM / pAG | tagging cassette | KanMX / HphMX / NatMX | most (dominant) |

References: Sikorski & Hieter 1989 (PMID 2659436) for pRS41x/42x; Brachmann 1998 (PMID 9483801) for BY-series strains; Gietz & Schiestl 2007 (PMID 17401334) for LiAc transformation; Sambrook 4th ed. for media recipes.

## 2.3 Pichia (K. phaffii) secretion

### 2.3.1 Wet-lab goal

Produce a secreted, glycosylated protein from *Komagataella phaffii* (formerly *Pichia pastoris*) at high density. Pichia is the dominant industrial host for secreted recombinant proteins because it (a) grows to very high cell density (OD600 > 500 in bioreactors), (b) secretes folded protein efficiently via the alpha-mating-factor signal peptide, (c) glycosylates with shorter, more uniform N-glycans than *S. cerevisiae* (although still hypermannosylated relative to mammalian), and (d) has a tightly regulated, very strong methanol-inducible AOX1 promoter.

### 2.3.2 Typical inputs

- **Target protein** (CDS or amino-acid sequence).
- **Vector** — pPICZ (Zeocin, intracellular), pPICZ-alpha (Zeocin, alpha-mating-factor-fused for secretion), pPink-HC (high-copy histidine-complementation), pGAPZ (constitutive GAP promoter), pAOX1 family.
- **Signal peptide for secretion** — alpha-mating-factor (alpha-MF) from *S. cerevisiae* is the canonical Pichia secretion signal; native eukaryotic signal peptides also work; consider Kex2 / Ste13 cleavage sites in the linker.
- **Strain** — X-33 (wild-type Mut+, GS115 background variant), GS115 (his4-, Mut+ or Muts derivatives), KM71H (Muts, his4-), SMD1163 (pep4 prb1 proteinase-deficient; less proteolysis but slower growth), PichiaPink (ade2-, glycoengineered).
- **AOX1 phenotype** — Mut+ (methanol-utilisation, uses both AOX1 and AOX2; faster growth on methanol) vs Muts (slow; uses only AOX2; preferred for some scale-up cases).
- **Marker** — Zeocin (pPICZ); HIS4 complementation; or G418 (KanMX) in Pichia.
- **Tags** — usually C-terminal His6 with a Kex2 or PreScission cleavage site before the tag for secreted constructs.

### 2.3.3 What the Toolkit produces

- Annotated GenBank / SBOL3 with the AOX1 promoter, alpha-factor signal peptide (with explicit Kex2 / Ste13 boundary annotation), CDS, polyA / 3'-AOX1, and Zeocin selection module.
- Codon-optimised insert (Pichia-specific codon table; deviates from *S. cerevisiae*).
- Primer set including the linearisation primers for genome integration into the AOX1 locus.
- Assembly route. For pPICZ, the canonical workflow uses restriction-ligation (EcoRI / NotI / XbaI) into the MCS.
- QC checkpoints including post-integration colony PCR primers and AOX1 phenotype check.

### 2.3.4 Bench action that follows

1. Assemble pPICZ-alpha-CARGO in *E. coli* (TOP10 or DH5-alpha + Zeocin selection on low-salt LB).
2. Verify by digestion and Sanger.
3. Linearise the pPICZ vector with SacI or PmeI (cuts within AOX1 5' region; promotes single-crossover integration at the genomic AOX1 locus).
4. Transform 1-5 ug of linearised plasmid into electrocompetent Pichia by electroporation (Appendix I § I.11).
5. Select on YPDS + Zeocin (100-1000 ug/mL) for 3-5 days at 30 deg C.
6. Screen colonies for high-copy integrants by Zeocin-titration (re-plate on increasing Zeocin from 100 to 2000 ug/mL).
7. Screen for AOX1 phenotype (Mut+ vs Muts) by methanol vs glycerol plating.
8. Pilot expression: grow in BMGY (buffered glycerol-complex) to OD600 ~ 5; centrifuge; resuspend in BMMY (buffered methanol-complex); induce with 0.5-1% methanol every 24 h; harvest supernatant at 24, 48, 72, 96 h timepoints.
9. SDS-PAGE / Western on the supernatant; titre on the protein of interest.

### 2.3.5 Common failure modes

| Failure mode | Will Toolkit catch? |
|---|---|
| Wrong signal peptide (cytoplasmic CDS not secreted) | Yes (advisory if no signal peptide and a secreted-target hint set) |
| Kex2 site mis-engineered (clips off N-terminal residues) | Yes (annotation check) |
| Zeocin in high-salt media (Zeocin is inactivated by NaCl > ~5 g/L) | Partial (advisory note in catalogue entry) |
| Cytoplasmic protease degrades secreted product | No (use pep4/prb1 strain) |
| Hyperglycosylation reduces activity | No (glycoengineered strain or mammalian alternative) |
| Methanol toxicity in Mut+ strain | No |

### 2.3.6 Canonical reference table — Pichia

| Vector | Promoter | Marker | Notes |
|---|---|---|---|
| pPICZ A/B/C | AOX1 / methanol | Zeocin (low-salt LB) | intracellular |
| pPICZ-alpha A/B/C | AOX1 / methanol | Zeocin (low-salt LB) | alpha-factor secretion |
| pPink-HC | AOX1 / methanol | ADE2 complementation | high-copy in Pink strain |
| pGAPZ A/B/C | GAP / constitutive | Zeocin | continuous expression |
| pAO815 | AOX1 / methanol | HIS4 complementation | classical GS115 vehicle |

References: Cregg 2009 (PMID 19899091) for Pichia overview; Daly & Hearn 2005 (PMID 15549714) for expression strategy; Invitrogen / Thermo Fisher Pichia manuals (nominative use, not redistributed).

## 2.4 Mammalian transient expression

### 2.4.1 Wet-lab goal

Express a heterologous protein transiently in a mammalian cell line (HEK293, CHO, COS-7) for 24-96 hours. Transient expression is fast (no clonal selection), produces correctly post-translationally-modified mammalian protein, and is the standard small-scale production route for antibody Fabs, soluble receptor ectodomains, fluorescent fusion proteins for imaging, viral packaging functions, and pilot tests for downstream cell-line generation.

### 2.4.2 Typical inputs

- **Cargo** (CDS, fusion construct, or polycistronic ORF with IRES / 2A peptide).
- **Backbone** — pcDNA3.1 (CMV, Amp, Neo / Hygro / Zeo), pcDNA4 (CMV, Zeo), pcDNA5/FRT (FRT site for Flp-In stable lines), pCAGGS / pCAG (CAG promoter), pTwist-CMV (Twist standard mammalian backbone).
- **Promoter** — CMV (default), EF1alpha, CAG, SV40, PGK, UBC.
- **5' UTR + Kozak** — the Toolkit checks the Kozak context (gccRccATGG strict; gccAccATGG acceptable; Kozak 1986 PMID 3839802).
- **Tag** — C-terminal usually preferred for soluble proteins (His6, FLAG, HA, Myc); N-terminal signal peptides for secreted proteins; GFP fusions for imaging; HiBiT for luminescence.
- **Polyadenylation signal** — bGH polyA (default), SV40 late polyA.
- **Cell line** — HEK293 (or 293T for SV40-driven episomal replication), Expi293F (suspension for high-yield), HEK293F, CHO-K1, CHO-S, COS-7.

### 2.4.3 What the Toolkit produces

- Annotated GenBank / SBOL3 of the construct.
- Codon-optimised insert (human or mouse codon table; CAI >= 0.7 default).
- Kozak strength evaluation (a scalar 0.0-1.0 plus a categorical strong / acceptable / weak label).
- Polyadenylation signal annotation and consensus check (AATAAA).
- Splicing analysis: cryptic splice donors / acceptors flagged by SpliceAI adapter when configured.
- Primer set, assembly route.
- Biosafety classification (RG1 for HEK / CHO; elevated if the cargo is from a pathogen).

### 2.4.4 Bench action that follows

1. Assemble pcDNA3.1-CARGO in DH5-alpha + Amp.
2. Mini-prep, verify by digest and Sanger.
3. Midi-prep (to provide endotoxin-low DNA for transfection); 100-500 ug typical for a transfection campaign.
4. Seed HEK293 (or 293T) cells at 70-80% confluence in DMEM + 10% FBS in 6-well plates or T75 flasks.
5. Transfect by lipid-based (Lipofectamine 2000 / 3000, PEI) or by electroporation (Neon, Lonza) with 1-3 ug DNA per well in 6-well; 10-50 ug DNA per T75. (Appendix I § I.9.)
6. Change medium 4-6 h post-transfection.
7. Harvest cells at 24, 48, 72 h. Lyse for intracellular product; collect supernatant for secreted product.
8. SDS-PAGE / Western; or, for fluorescent fusions, image on a confocal microscope.

### 2.4.5 Common failure modes

| Failure mode | Will Toolkit catch? |
|---|---|
| Weak Kozak context | Yes (`MR-KOZAK-WEAK`) |
| Cryptic splice donor in coding sequence | Yes if SpliceAI adapter configured; otherwise advisory |
| Missing polyA signal | Yes (`MR-POLYA-MISSING`) |
| In-frame stop codon (e.g., readthrough TGA in a fusion) | Yes |
| Cargo encodes a known toxin without IBC approval | Yes (BiosafetyClassificationLayer advisory) |
| Transfection toxicity (lipofection-related) | No (bench-level optimisation) |
| Endotoxin in mini-prepped DNA | No (use midi-prep, endotoxin-removal column) |

### 2.4.6 Canonical reference table — mammalian transient

| Backbone | Promoter | Selection (for downstream) | Notes |
|---|---|---|---|
| pcDNA3.1(+) / (-) | CMV | Neo (G418), Amp (E. coli) | classical |
| pcDNA4 | CMV | Zeo (mammalian), Amp | |
| pcDNA5/FRT | CMV | Hygro / FRT integration | Flp-In stable system |
| pCAGGS / pCAG | CAG | none by default | strong in many lines |
| pCMV-Tag (Stratagene) | CMV | Neo or Hygro | epitope-tagging |
| pTwist-CMV / pTwist-Lenti-SFFV | CMV / SFFV | Amp / Puro | Twist standard |

References: Boshart 1985 (CMV) PMID 2999983; Niwa 1991 (CAG) PMID 1660837; Kozak 1986 PMID 3839802.

## 2.5 Mammalian stable expression

### 2.5.1 Wet-lab goal

Establish a clonal mammalian cell line that stably expresses the cargo from a chromosomally-integrated cassette, for repeated production runs, long-term studies, or cell-based assay reagents.

Two routes dominate practice: **random integration with antibiotic selection** (the cargo and a selection marker are co-transfected; antibiotic kills non-integrants; surviving colonies are clonally isolated) and **site-specific integration** via a pre-engineered docking site (Flp-In, PiggyBac, AttB / AttP using PhiC31, CRISPR-knock-in).

### 2.5.2 Typical inputs

- **Cargo** with mammalian expression cassette (as in § 2.4).
- **Mammalian selection marker** — Puromycin (puro), Blasticidin (blast), G418 / Neomycin (neo), Hygromycin (hygro), Zeocin (zeo). The v0.2 markers catalogue carries per-marker working concentrations for HEK293, CHO, HeLa with Sambrook 4th ed. references.
- **Integration strategy** — random, Flp-In, PiggyBac, AttB/AttP, CRISPR knock-in at AAVS1 or another safe-harbour locus.
- **Cell line** — HEK293, CHO-K1, CHO-S, CHO-DG44, HeLa, U2OS.

### 2.5.3 What the Toolkit produces

- Annotated construct with the chosen integration site (e.g., FRT site, PiggyBac ITRs, AAVS1 homology arms) and the selection cassette.
- Marker advisory if the chosen marker is not validated for the chosen cell line (the catalogue has explicit `compatible_hosts` lists).
- Cargo + selection cassette layout (IRES vs 2A peptide vs separate promoter).
- Primer set; assembly route; QC checkpoints.

### 2.5.4 Bench action that follows

For a Flp-In / pcDNA5-FRT stable line:

1. Establish a parental Flp-In host cell line (commercial; carries a single FRT site).
2. Co-transfect pcDNA5-FRT-CARGO + pOG44 (Flp recombinase expression plasmid) into the host line.
3. Select with Hygromycin B; pick clones; verify integration by PCR across the FRT/lacZ junction.

For random integration with G418:

1. Transfect pcDNA3.1-CARGO into HEK293.
2. After 48 h, replace medium with DMEM + 10% FBS + 600-800 ug/mL G418.
3. Replace medium every 3-4 days; resistant colonies appear in 10-21 days.
4. Pick 12-24 colonies; expand; screen by Western / FACS for cargo expression; freeze stocks.

### 2.5.5 Common failure modes

Most failure modes are bench-level (selection escape, mycoplasma, clonal drift) and are outside the Toolkit's design-level scope. The Toolkit catches marker-host mismatches (e.g., Zeocin in a cell line that lacks the right uptake; Hygromycin in a cell line that has innate resistance), missing polyA, weak Kozak, and (in v0.2) the marker concentration / medium incompatibilities recorded in `markers.yaml`.

## 2.6 Viral vectors (lentivirus / AAV / adenovirus / retrovirus)

### 2.6.1 Wet-lab goal

Deliver cargo to a target cell that is hard or impossible to transfect by chemical means: primary cells, post-mitotic neurons, intact tissue ex vivo, animal in vivo. Viral vectors exploit a virus's natural delivery and (sometimes) integration machinery while being engineered to be replication-incompetent.

### 2.6.2 Lentivirus (third-generation)

**Cargo size**: ~8 kb between the LTRs (cargo + WPRE).

**Plasmid set** (third-generation Self-Inactivating, SIN):

- **Transfer vector** carrying the cargo flanked by LTRs (5' LTR with hybrid promoter, 3' SIN LTR with deletion in U3); contains psi packaging signal, RRE, cPPT.
- **psPAX2** — packaging plasmid encoding Gag, Pol, Rev, Tat (under CMV).
- **pMD2.G** — envelope plasmid encoding VSV-G.

**Producer cell**: HEK293T (carries SV40 T antigen for episomal replication).

**Workflow**:

1. Triple-transfect HEK293T with transfer + psPAX2 + pMD2.G (typical molar ratio 4:3:1 or 2:1:1).
2. 48 h post-transfection, collect supernatant; filter (0.45 um); concentrate by ultracentrifugation (typically 25000 g, 90 min, 4 deg C) if needed.
3. Titrate functional virus on a target line (qPCR for integrated cargo, GFP FACS, or limited-dilution).
4. Transduce target cells; select with the cargo's antibiotic marker (Puro / Blast).

The Toolkit catches:

- Cargo size > ~8 kb (`WR-LENTI-CARGO-OVERSIZE`).
- Missing WPRE, missing cPPT, missing RRE.
- Cargo contains a polyA signal upstream of WPRE (truncates the genome).
- SIN LTR mis-annotated (loss of self-inactivation).
- Biosafety: replication-competence advisory if the cargo or modification could restore Tat / Rev functions.

### 2.6.3 AAV

**Cargo size**: ~4.7 kb between the ITRs (single-stranded; or ~2.3 kb for self-complementary AAV).

**Plasmid set**:

- **Transfer vector (pAAV-)** with cargo flanked by 5' and 3' ITRs.
- **pRep-Cap** for the chosen serotype (AAV2 Rep + AAV-serotype Cap; e.g., AAV-DJ for broad tropism, AAV9 for CNS / heart, AAV6 for muscle).
- **pHelper** providing Adenovirus E2A / E4 / VA RNA helper functions.

**Producer cell**: HEK293T.

The Toolkit checks ITR integrity (ITRs are critical and notoriously unstable; the engine flags the user when SnapGene cross-check is required), cargo-size budget against the chosen serotype's packaging limit, and presence of an AAV2 ITR pair (most production protocols use AAV2 ITRs regardless of capsid serotype).

### 2.6.4 Adenovirus

**Cargo size**: ~8 kb (first-generation), ~37 kb (gutted high-capacity).

Adenoviral vectors are used less in routine research because production is technically demanding (transfection of HEK293 or PER.C6 + plaque purification + amplification + CsCl gradient or chromatography), but they are valuable for short-term, high-titre expression. The Toolkit supports the AdEasy backbone family (He 1998 PMID 9482916).

### 2.6.5 Retrovirus (gammaretrovirus)

Largely superseded by lentivirus for most applications. Retroviruses transduce only dividing cells. The Toolkit supports the MMLV-based pBABE series and Phoenix-A / -E packaging cell lines.

### 2.6.6 Common failure modes (all viral)

- Cargo too large for the vector (Toolkit catches all four).
- LTR / ITR mis-annotation (Toolkit flags; manual SnapGene cross-check required).
- Replication-competence concern (Toolkit's BiosafetyClassificationLayer escalates).
- Helper-cell mismatch (Toolkit's advisory).
- Endotoxin in transfection-grade DNA (bench-level).
- Concentration / titre too low (bench-level).
- Off-target transduction in mixed cultures (experimental-design level).

## 2.7 Fluorescent-protein reporter design

### 2.7.1 Wet-lab goal

Visualise protein localisation, expression dynamics, protein-protein interaction (FRET / BiFC), or cell tracking using a genetically-encoded fluorescent protein (FP) fusion or co-expressed reporter.

### 2.7.2 Modern FP families the Toolkit knows

| FP | Excitation / Emission max (nm) | Notes |
|---|---|---|
| EGFP / EYFP | 488 / 507 (EGFP) | Classical; well-validated |
| mCherry | 587 / 610 | Bright red monomer (Shaner 2004 PMID 15558047) |
| mScarlet / mScarlet-I / mScarlet-H | 569 / 594 | Brightest red monomer (Bindels 2017 PMID 27869816) |
| mNeonGreen | 506 / 517 | Bright green-yellow (Shaner 2013 PMID 23685885) |
| mTurquoise2 | 434 / 474 | Brightest cyan (Goedhart 2012 PMID 22426491) |
| iRFP | 690 / 713 | NIR for deep tissue (Filonov 2011 PMID 21909076) |
| HaloTag / SNAP-tag | varies (ligand-dependent) | Self-labelling; not strictly FP |

### 2.7.3 Common design choices

- **N- vs C-terminal fusion**: N-terminal for proteins where the C-terminus is functional (e.g., GPCRs with C-terminal signalling); C-terminal otherwise.
- **Linker**: GGSGG or (GGGGS)2/3 are standard flexible linkers; rigid (EAAAK)n for rigid spacing.
- **Monomer vs dimer**: prefer monomers for fusions (mScarlet vs DsRed); dimers may oligomerise the fusion partner.
- **FRET pairs**: mTurquoise2 (donor) / mVenus or YPet (acceptor) is a high-dynamic-range FRET pair; EGFP / mCherry is a workable alternative for cyan-not-available setups.
- **Spectral channels**: for 4-channel imaging, pick mTurquoise2 + mNeonGreen + mCherry/mScarlet + iRFP.

### 2.7.4 What the Toolkit catches

- Frame-shift between cargo and FP.
- Stop codon between cargo and FP (truncates the fusion).
- Linker length / composition outside recommended ranges (advisory).
- Common spectral conflicts when multiple FPs are designed for the same construct.

## 2.8 Selectable markers per host (v0.2 markers catalogue)

The v0.2 markers catalogue (`catalogues/markers.yaml`, 23 markers) is the canonical concentration record. The Toolkit's `engine.compatibility` consults the markers catalogue via the new `MarkersCataloguePort` (REQUIREMENTS.md FR-MARK-12; ARCHITECTURE.md § 9.1).

### 2.8.1 Bacterial antibiotic markers

| Marker (gene) | Antibiotic | Working concentration (ug/mL in LB) | Notes |
|---|---|---|---|
| `bla` (Amp) | Ampicillin / Carbenicillin | 100 (Amp) / 50-100 (Carb) | Use Carb to suppress satellite colonies in long incubations |
| `neo` (Kan) | Kanamycin / Neomycin | 50 | |
| `cat` (Cm) | Chloramphenicol | 34 | Canonical pET-system pLysS / pRARE concentration |
| `tetA` (Tet) | Tetracycline | 12.5 | Light-sensitive; freshly prepared |
| `aadA` (Spec) | Spectinomycin | 100 | |
| `ble` (Zeo) | Zeocin / Bleomycin | 25 | Use low-salt LB (NaCl <= 5 g/L) |
| `aac(3)-IV` (Gen) | Gentamicin | 25 | Broad-host plant binaries |
| `hph` (Hyg) | Hygromycin B | 200 (bacterial) | Distinct from mammalian concentration (50-200) |
| `ermC` (Erm) | Erythromycin | 100-250 | Gram-positive (low *E. coli* utility) |

References: each row's citation is in `markers.yaml` and includes the canonical Sambrook 4th ed. Appendix A1 entry plus PMID-cited primary literature where available (e.g., Beck 1982 PMID 6296021 for kanamycin; Shaw 1975 PMID 1095 for chloramphenicol; Drocourt 1990 PMID 2370666 for Zeocin; Hollingshead 1985 PMID 2987812 for spectinomycin; Gritz & Davies 1983 PMID 6313438 for hygromycin).

### 2.8.2 Yeast auxotrophic markers

| Marker | Complements auxotrophy | Selection medium | Strain |
|---|---|---|---|
| URA3 | ura3 | SD -Ura | BY4741, W303 |
| LEU2 | leu2 | SD -Leu | BY4741, W303 |
| HIS3 | his3 | SD -His | BY4741, W303 |
| TRP1 | trp1 | SD -Trp | W303 (BY4741 is TRP1+) |
| MET15 / MET17 | met15 / met17 | SD -Met | BY4741, BY4742 |
| LYS2 | lys2 | SD -Lys | BY4742 |

URA3 has a counter-selection (5-FOA kills ura+ cells) commonly used for marker recycling.

### 2.8.3 Yeast dominant markers

| Marker | Antibiotic | Working concentration | Notes |
|---|---|---|---|
| KanMX | G418 | 200-400 ug/mL | Dominant; for prototrophic strains |
| HphMX | Hygromycin B | 200-300 ug/mL | Dominant |
| NatMX | clonNAT (Nourseothricin) | 100 ug/mL | Dominant |
| BleMX | Zeocin | 100-300 ug/mL | Dominant; low-salt medium |

### 2.8.4 Mammalian markers

| Marker | Antibiotic | Working concentration (cell-line typical) | Notes |
|---|---|---|---|
| `puro` | Puromycin | 1-10 ug/mL | Fast (3-5 d) selection; widely used |
| `bsd` | Blasticidin | 5-15 ug/mL | Cytoplasmic; quick |
| `neo` (G418) | G418 / Geneticin | 400-1000 ug/mL | Slow (10-21 d); same gene as bacterial Kan |
| `hph` | Hygromycin B | 50-500 ug/mL | Intermediate |
| `bleR` | Zeocin | 100-1000 ug/mL | Bifunctional; useful in dual selection |

All concentrations in this section are starting points; titrate against your cell line / strain background before relying on them. The `markers.yaml` catalogue carries `working_concentrations` blocks with `min / typical / max` and explicit `medium` and citation fields; the Toolkit emits these in advisories so the bench user does not have to look them up.

## 2.9 CRISPR / Cas9 design

### 2.9.1 Wet-lab goal

Make a targeted DNA double-strand break (DSB) at a defined genomic locus, then exploit endogenous repair (NHEJ for knockout, HDR for knock-in) to introduce the desired genetic change.

### 2.9.2 Typical inputs

- **Target genomic locus** (gene name + exon + coordinates) and the desired edit (knockout, point mutation, fluorescent-protein knock-in, tag insertion, conditional allele).
- **Cas variant** — SpCas9 (NGG PAM, 20-nt protospacer); SaCas9 (NNGRRT PAM, 20-22 nt); LbCas12a / Cpf1 (TTTV PAM, 23-25 nt, generates staggered cut); high-fidelity variants (eSpCas9, SpCas9-HF1, HiFi-Cas9).
- **sgRNA delivery vector** — pX330 (single sgRNA + SpCas9, no selection); pX458 (pX330 + GFP for FACS sorting); lentiCRISPR v2 (lenti, single sgRNA + SpCas9 + Puro); lentiGuide-Puro (sgRNA only; pair with lentiCas9-Blast).
- **HDR template** (for knock-in) — a dsDNA or ssODN with cargo flanked by homology arms (typically 500-1000 bp for dsDNA, 30-60 nt for ssODN; longer arms generally better for larger inserts).
- **Cell type and delivery** — transfection, electroporation, RNP delivery (purified Cas9 + sgRNA without DNA).

### 2.9.3 What the Toolkit produces

- The full assembled sgRNA + Cas9 construct (or RNP-formatted sgRNA design with synthesis spec).
- Off-target scan against the target genome (uses GuideScan, CRISPOR, or Cas-OFFinder adapter when configured).
- A PAM-context check (correct PAM for the chosen Cas variant).
- An HDR template with annotated homology arms, payload, silent PAM-disrupting mutations (so the edited locus does not re-cut), and diagnostic restriction sites.
- A genotyping primer set (T7E1 or amplicon-deep-sequencing).
- A biosafety classification advisory if the target is a known oncogene or tumour suppressor (CRISPR knock-in / knock-out of TP53, MYC, BRCA family typically routes to IBC).

### 2.9.4 Bench action that follows

For a knockout in HEK293:

1. Order the sgRNA insert as 24-nt complementary oligos with the BbsI / BsmBI overhangs for pX458.
2. Anneal the oligos; ligate into BbsI-digested pX458.
3. Transform; mini-prep; Sanger-verify the protospacer.
4. Transfect 1 ug pX458-sgRNA into HEK293 (Lipofectamine 3000 in 6-well).
5. After 48 h, FACS-sort GFP+ cells single-cell into 96-well.
6. Expand clones for 10-14 days; genotype by amplicon sequencing or T7E1 surveyor assay.
7. Validate the chosen knockout clone by Western or functional assay.

### 2.9.5 Common failure modes

| Failure mode | Will Toolkit catch? |
|---|---|
| Wrong PAM for chosen Cas | Yes (`MR-CAS-PAM-MISMATCH`) |
| sgRNA targets a non-unique sequence | Yes if off-target adapter configured |
| HDR arms too short for large insert | Yes (advisory) |
| HDR template will be cut by Cas9 (PAM not disrupted) | Yes (advisory) |
| Bystander edits in mixed populations | No (clonal isolation needed) |
| Off-target editing | Yes if off-target adapter configured (advisory) |
| Tumour-suppressor / oncogene edit lacks IBC review | Yes (BiosafetyClassificationLayer advisory) |

## 2.10 Antibody vectors

### 2.10.1 Wet-lab goal

Express an antibody fragment (scFv, Fab) or a full-length immunoglobulin (IgG) for research, diagnostics, or pre-clinical use.

### 2.10.2 Typical inputs

- **V_H and V_L amino-acid sequences** (or DNA).
- **Format** — scFv (V_H-linker-V_L or V_L-linker-V_H, classical (GGGGS)3 linker), Fab (heavy chain Fd + light chain on separate cassettes or paired by IRES), IgG (full heavy + light chain; typically as two cassettes co-transfected, or on a single bicistronic plasmid).
- **Constant region** — for IgG, the human IgG1, IgG2, IgG4 (or murine IgG2a) heavy chain constant region + kappa or lambda light constant.
- **Vector backbone** — pTwist-CMV / pcDNA3.4-TOPO / pcDNA3.1 / proprietary CHO expression backbones; pFUSE series (InvivoGen) is the standard for Fab / IgG academic work.
- **Production host** — Expi293F (transient HEK293), CHO-K1 / CHO-S (stable for commercial-scale).
- **Signal peptide** — secretory; commonly murine Ig heavy chain (V_H signal sequence) or human IL-2 signal peptide.

### 2.10.3 What the Toolkit produces

- Annotated GenBank / SBOL3 for each chain or the combined construct.
- Codon-optimised CDS for the chosen host (human / Chinese hamster).
- Validation of the heavy-light interchain disulfide context.
- Signal-peptide cleavage-site prediction (SignalP adapter when configured).
- Primer set, assembly route, QC checkpoints.

### 2.10.4 Bench action that follows

A typical Expi293F transient workflow:

1. Co-transfect Expi293F with HC and LC plasmids (1:1 molar ratio; 30 ug total DNA per 30 mL culture).
2. Add ExpiFectamine 293 reagent according to manufacturer protocol.
3. 24 h later, add ExpiFectamine 293 Enhancer 1 and Enhancer 2.
4. Harvest culture at 5-7 days; clarify by centrifugation and 0.22-um filtration.
5. Purify by Protein A or Protein G affinity chromatography; elute with low-pH glycine; neutralise immediately with Tris.
6. Buffer-exchange to PBS or storage buffer; quantify by A280; check by SDS-PAGE (reducing and non-reducing).
7. Functional QC (ELISA, BLI / SPR, flow cytometry on the target cell).

### 2.10.5 Common failure modes

- Heavy / light chain ratio off (Toolkit advisory).
- Signal peptide blocks secretion (Toolkit catches if cleavage prediction is configured).
- N-glycan heterogeneity in HEK vs CHO (out of scope).
- Aggregation in storage (bench-level; chromatographic optimisation).
- Endotoxin in DNA prep (bench-level).

---

# Part 3 - Toolkit walkthrough

This part walks you through the Toolkit as a user. We do not assume you have read the source code; we do assume you have installed the software per Appendix A and that you can open a terminal and a web browser. If you are reading this for the first time and have not installed yet, skip to Appendix A first, install, and come back.

The Toolkit exposes three user-facing surfaces:

1. **A React + TypeScript web UI** running locally at `http://127.0.0.1:5173/`. This is the primary surface for routine design work.
2. **A Python CLI** (`cevd ...`) for headless / scripted use, batch processing, and integration with continuous-integration systems.
3. **A REST HTTP API** (default port 8000) for programmatic access from external scripts, other tools, or pair-programming AI agents.

The architecture is identical across the three surfaces: the same application services, the same domain core, the same validation engine, the same export bundle. Anything you can do in the UI you can also do via CLI or API; this manual focuses on the UI because that is what most users will see first.

## 3.1 Install and launch

The full installation procedure is in Appendix A. The condensed version, for a Windows 11 machine with Python 3.11.15 and Node 20+ already installed:

```powershell
git clone https://github.com/GMExpression/cloning-expression-vector-design.git
cd cloning-expression-vector-design

# Python backend
uv sync                                  # installs Python deps into .venv
pre-commit install                       # enables the project's commit hooks

# UI dependencies
cd ui
npm install
cd ..

# Verify
$env:PYTHONPATH='src;.'
.\.venv\Scripts\python.exe tools\agenda_consistency_check.py
.\.venv\Scripts\python.exe tools\ci\run_pytest.py -m "not slow"
```

Once verified, launch the UI:

```powershell
cd ui
npm run dev -- --port 5173
```

Open `http://127.0.0.1:5173/` in a modern Chromium or Firefox browser. The UI loads the design summary surface; you are ready to begin.

For headless / CI use:

```powershell
.\.venv\Scripts\python.exe -m cevd design new --template pet28a-his-tag --cargo my_protein.fasta
```

The CLI exposes the same Decision Wizard prompts as the UI, but textually. The HTTP API is documented at `/docs` (OpenAPI / Swagger) once you start the backend with `uvicorn app.api.main:app --port 8000`.

## 3.2 Decision Wizard step by step

The Decision Wizard is the canonical entry point for new designs. Open the UI; click "New design" on the Design Summary panel. The Wizard walks through seven structured steps plus an open free-text input field at each step.

### 3.2.1 Step 1 - Objective

Pick one of:

- Recombinant protein expression
- Reporter / fluorescent fusion
- CRISPR knockout / knock-in
- Antibody (scFv / Fab / IgG)
- Viral packaging (lenti / AAV / adeno / retro)
- Combinatorial library
- Other / specialised (free-text)

The chosen objective constrains the downstream defaults. Selecting "Recombinant protein expression" pre-fills protein-friendly defaults (His6 tag suggestion, IPTG induction, BL21(DE3) host hint). Selecting "Other / specialised" leaves the defaults open and the engine consults the free-text channel.

### 3.2.2 Step 2 - Target host

Drop-down options grouped by class:

- Bacterial: *E. coli* (DH5-alpha, NEB-5alpha, TOP10, BL21, BL21(DE3), BL21(DE3)pLysS, Rosetta(DE3), SHuffle, Origami, C41(DE3), C43(DE3), Stbl3, JM109, MG1655, others — 35+ strains in v0.2)
- Yeast: *S. cerevisiae* (BY4741, BY4742, W303, INVSc1, YPH499/500, CEN.PK), *K. phaffii / Pichia* (X-33, GS115, KM71H, SMD1163, PichiaPink)
- Mammalian: HEK293 / 293T / 293F / Expi293F, CHO-K1 / CHO-S / CHO-DG44, HeLa, U2OS, COS-7, A549, MCF-7
- Insect: Sf9, Sf21, High Five
- Plant: *Agrobacterium tumefaciens* (LBA4404, GV3101) for delivery; *N. benthamiana*, *A. thaliana* for downstream
- Cell-free: PURE, S30, TXTL

The host catalogue (`catalogues/hosts.yaml`) is the authoritative record. Each strain entry has phenotype fields covering T7 lysogeny, lon / ompT protease status, trxB / gor redox status, rare-codon supplementation, plasmid-borne add-ons (pLysS / pLysE / pRARE), recombination phenotype, methylation phenotype, and the explicit list of compatible selection markers.

### 3.2.3 Step 3 - Cargo type

Drop-down options:

- Protein-coding ORF
- sgRNA (single)
- sgRNA library (multi-guide)
- Reporter (fluorescent / luciferase)
- Polycistronic (IRES / 2A)
- Structural / non-coding RNA
- Antibody fragment (scFv / Fab)
- Full-length antibody (IgG)
- Bacterial / archaeal native operon
- Gene-therapy cargo (AAV / lentivirus payload)
- Other / specialised

The cargo type drives downstream cassette construction. For a protein-coding ORF you will be asked for the source sequence and frame; for an sgRNA you will be asked for the protospacer; for a polycistronic cargo you will be asked for each ORF and the linker (IRES, P2A, T2A, F2A, E2A).

### 3.2.4 Step 4 - Expression level / induction

For bacterial:

- T7 / IPTG
- T7 / IPTG (tight, pLysS-controlled)
- araBAD / L-arabinose
- trc / IPTG
- tac / IPTG
- rhaBAD / L-rhamnose
- Tet-on / anhydrotetracycline
- Constitutive

For yeast (S. cerevisiae):

- GAL1 / galactose-induced
- TEF1 / constitutive (strong)
- PGK1 / constitutive (medium-strong)
- ADH1 / constitutive (medium)
- CUP1 / copper-induced
- MET25 / methionine-repressed

For mammalian:

- CMV / constitutive (strong; can silence in some lines)
- EF1alpha / constitutive (strong; less silencing)
- CAG / constitutive (broad)
- SV40 / constitutive (medium)
- PGK / constitutive (low-medium; reliable across types)
- UBC / constitutive (medium)
- Tet-on / doxycycline-induced
- TRE / Tet-responsive

The Wizard records both the selection and the strength target (low / medium / high) so the validation engine can flag induction-system / host mismatches (e.g., T7 promoter without a DE3 host raises `MR-PROMOTER-HOST` HARD).

### 3.2.5 Step 5 - Tagging strategy

Choose N-terminal tag, C-terminal tag, and linker.

N-terminal tags: His6, MBP, GST, SUMO, TRX, FLAG, HA, signal peptide for secretion (alpha-MF for yeast / Pichia, Ig heavy V_H signal for mammalian secreted, native signal for membrane proteins).

C-terminal tags: His6, FLAG, HA, Myc, Strep-II, AviTag (for BirA biotinylation), HaloTag, SNAP-tag, GFP / mCherry / mScarlet / mTurquoise2 / mNeonGreen, HiBiT, MoonTag.

Linkers: GGSGG (short flexible), (GGGGS)2/3 (long flexible), (EAAAK)n (rigid alpha-helix), PreScission / TEV / SUMO cleavage sites (cleavable).

The Wizard auto-suggests linker lengths per chosen tag combination; the validation engine flags fusion frame errors and in-frame stops.

### 3.2.6 Step 6 - Cloning chemistry

Options:

- Restriction + ligation (specify enzymes; the Toolkit auto-checks for unique sites)
- Gibson / NEBuilder HiFi (specify homology-arm length; default 25 bp)
- Golden Gate (specify Type IIS enzyme: BsaI / BsmBI / SapI; and the kit: MoClo, Loop, YTK, GreenGate, GoldenBraid, JUMP, MIDAS)
- Gateway (specify entry / destination vectors; LR vs BP reaction)
- LIC (Ligation-Independent Cloning)
- SLIC
- USER
- IVA (In-Vivo Assembly)
- TAR (Transformation-Associated Recombination, for yeast)
- In-Fusion (Takara)

The engine validates chemistry-vs-host (e.g., yeast TAR requires *S. cerevisiae* recA+ background), chemistry-vs-fragment-count (Gibson scales to ~5 fragments without efficiency loss; Golden Gate scales to ~15+ with proper overhang fidelity), and chemistry-vs-vendor (some vendors recommend Gibson-compatible 25-40 bp homology arms in synthesised fragments).

### 3.2.7 Step 7 - Biosafety tier

Pick:

- BSL-1 (RG1; basic precautions; most academic work)
- BSL-2 (RG2; biosafety cabinet, autoclaving, IBC review usually required)
- BSL-3 (RG3; certified facility, respirator, IBC + institutional sign-off mandatory)
- BSL-4 (RG4; hard-blocked at compile time by the Toolkit; explicit reason message; M7)

The Toolkit's `BiosafetyClassificationLayer` (ARCHITECTURE.md § 1 item 9, FR-ADV-*) cross-references your declared tier against the cargo's known classification (selectively, for cargo with known elevated-BSL status; the catalogue is intentionally conservative). If the engine believes your tier declaration may be too low (e.g., a cargo from a Risk Group 3 organism declared as BSL-1), it emits a `caution` or `strong_caution` advisory that requires active acknowledgement before authorisation.

### 3.2.8 The free-text channel (UR-02)

Every step has a free-text input labelled "Other / specialised - describe your requirement", capacity >= 2000 characters. Use this for:

- Strain-specific requirements ("BL21(DE3) with the lon::cat deletion described in PMID nnnnnnnn")
- Internal IP-protected parts ("our proprietary GS-tag from internal repo")
- Unusual physical constraints ("the cargo must be transcribed antisense to the genomic locus on integration")
- Citations to peer-reviewed work that is not yet in the Toolkit's catalogue
- Reviewer notes that must be visible to the validation engine

Free-text is persisted, indexed by step, surfaced to the validator (the `app.constraint_translator` LLM service translates it into structured constraints, then a user-confirmed snapshot is taken — M10 in ARCHITECTURE.md; the LLM's text is never authoritative without confirmation), and bundled into the export. This is the canonical channel for any requirement the Wizard's dropdowns do not cover.

### 3.2.9 Wizard completion

After Step 7 you see a confirmation summary. Review carefully. Click "Build construct" to commit the intent to a `DesignSession`. The Toolkit assembles the construct graph, runs all engines (compatibility, validation, sequence-analysis, controls, risk-classification), and presents the Construct Map plus the Validation Report.

## 3.3 Importing existing sequences

If you have an existing sequence to import (a parental backbone, a cargo, a tested cassette), use the Import surface rather than the Wizard. Supported formats:

- GenBank (`.gb`, `.gbk`)
- SBOL3 (`.xml`, `.ttl`)
- FASTA (`.fa`, `.fasta`)
- SnapGene `.dna` (read-only via `snapgene-reader` optional dependency)
- EMBL flat file
- GFF3 (annotation only; combine with FASTA for sequence)

### 3.3.1 GenBank import

The most common path:

1. Click Import > GenBank.
2. Drag your `.gb` file into the drop zone (or browse).
3. The parser extracts sequence + features + topology (LINEAR or CIRCULAR from the LOCUS line).
4. The Toolkit constructs a `SequenceRecord` and a derived `ConstructGraph`.
5. Verify the topology (the Toolkit cannot infer circular topology from sequence alone; it relies on the GenBank LOCUS field).

The engine emits an advisory if any feature uses a non-canonical type label that does not map cleanly to a Sequence Ontology term; you can either accept the engine's mapping or edit the feature manually.

### 3.3.2 SnapGene `.dna` import

If you have `snapgene-reader` installed in the optional `io` extra (`uv sync --extra io`), you can drag a `.dna` file directly. The parser extracts sequence, features, primers, and history. If the package is unavailable, the Toolkit instructs you to export to GenBank from SnapGene and re-import.

### 3.3.3 BR-16: the manual SnapGene cross-check

**This is mandatory.** Before any imported sequence proceeds to validation / export, you must perform a manual SnapGene cross-check (BR-16). The procedure:

1. Open the same source `.dna` file (or the GenBank export you just imported) directly in SnapGene on your machine.
2. Visually inspect the feature map: are all features present? Are their orientations correct? Are their boundaries the same?
3. Compare the sequence length, GC content, and topology between SnapGene and the Toolkit's display.
4. If all checks pass, click "BR-16 confirmed" in the Toolkit UI and provide a justification of >= 20 characters (e.g., "Cross-checked in SnapGene 7.2 on 2026-05-23; 11 features matched, length 5432 bp, GC 51.2%").
5. The Toolkit records the confirmation as a signed `DecisionRecord` bound to the `SequenceRecord` checksum, the SnapGene version (if you supplied it), and the timestamp.

If you skip BR-16, the design will be blocked at the authorisation gate with `BR-16-SNAPGENE-CROSSCHECK-MISSING`. There is no override that bypasses this; the rationale is that automated parsers do occasionally misinterpret unusual GenBank dialects, and a 30-second human cross-check eliminates the most common silent-corruption failure modes.

### 3.3.4 Importing a primer set

Primers can be imported as a FASTA file (one record per primer) or as a tab-separated file with columns `name`, `sequence`, `Tm_calc`, `purpose`. Primer features are attached to the appropriate `SequenceRecord` as `primer_bind` features (FR-INT-06) and are emitted into the export bundle.

## 3.4 Vector Map

The Vector Map surface provides two synchronised views of your construct:

- **Circular view**: features rendered as arcs on a circle; useful for plasmids; supports zoom and rotation.
- **Linear view**: features rendered as boxes on a line; useful for fragments, viral cargo, or any non-circular construct; supports zoom and pan.

Both views show:

- Feature names and types (colour-coded by Sequence Ontology category; legend in the lower-right corner).
- Feature directions (arrows for promoters, CDSs, terminators).
- Restriction sites (toggleable; defaults to a chosen "common" subset; can expand to "all known").
- Primer binding sites (toggleable).
- Annotation labels (auto-positioned to avoid overlap; manual nudging supported).

Click any feature to inspect its details (sequence, coordinates, type, qualifier list, provenance, source citation). Right-click to edit or remove (changes are versioned in the session event log).

### 3.4.1 Construct Architecture Table

Below the map is the Construct Architecture Table — a sortable, filterable list of every feature in the construct with columns: Order, Name, Type, Start, End, Length, Strand, Notes. Use this when you want a precise textual view rather than the visual map.

## 3.5 Compatibility Matrix

The Compatibility Matrix shows the cross-product of design choices against host / marker / chemistry / vendor catalogues, with each cell marked OK / WARN / BLOCK.

Rows: design elements (promoter, terminator, ori, marker, tag, chemistry, vendor).

Columns: host (selected strain), and any other contextual constraint (BSL tier, target organism).

Example: if you have selected BL21(DE3) as the host, a T7 promoter as the chosen promoter, and Amp as the marker, the matrix shows:

- T7 / BL21(DE3): OK (host carries the DE3 lysogen; T7 RNAP is induced by IPTG).
- T7 / DH5-alpha: BLOCK (no T7 RNAP in DH5-alpha).
- Amp / BL21(DE3): OK (host has no chromosomal beta-lactamase; bla gives selection).
- Amp / any low-salt-only strain: WARN if the medium is high-salt (advisory).
- Cargo-class / cell-line: OK / WARN / BLOCK per the BiosafetyClassificationLayer.

Hover over any cell for the rule reference (`MR-PROMOTER-HOST` / `MR-MARKER-MISMATCH` / `MS-PACKAGING-SIGNAL` etc.) and the citation. Click for the full rule documentation.

In v0.2, the markers catalogue (`catalogues/markers.yaml`) is now consulted for marker-host links (FR-MARK-12); the `MarkersCataloguePort` dependency was added to `engine.compatibility` and a dual-read shim against the legacy `parts.yaml::markers` block is in effect during the migration window.

## 3.6 Validation Report

The Validation Report is the single most important surface in the Toolkit. It is a structured list of findings, ordered by severity, with each finding carrying:

- A **rule ID** (e.g., `MR-PROMOTER-HOST`, `WR-FRAGMENT-OVERSIZE`, `SR-VENDOR-PROHIBITED`, `BR-16`, `MS-CAPSID-EXPRESSION`).
- A **rule category** (`MR` = Molecular Rule; `WR` = Wet-lab Rule; `SR` = Synthesis-vendor Rule; `BR` = Biosafety Rule; `MS` = MS2 / VLP rule).
- A **severity** (`INFO`, `SOFT`, `HARD`).
- A **citation** (PMID, knowledge-base section, or rule-manifest reference).
- A **scope** (the feature, region, or construct element the finding applies to).
- A **suggested remediation** (where applicable).
- A **last-reviewed** date (per the rule manifest's maintenance metadata).

### 3.6.1 Severity meanings

- **INFO**: informational; no action required. Surfaced for transparency. Example: "Codon usage CAI = 0.78 against E. coli K-12 codon table" — useful to know, but the value is already above the default threshold of 0.7.
- **SOFT**: warning; action may be required. Subdivided into:
  - `info` — not blocking; informational.
  - `caution` — requires acknowledgement before authorisation (FR-ADV-04). Example: "Promoter strength choice may exceed solubility threshold for this protein."
  - `strong_caution` — requires acknowledgement with stronger justification + cryptographic signature (FR-ADV-04). Example: "Cargo contains a sequence flagged by the BiosafetyClassificationLayer as potentially elevated-BSL; manual IBC review recommended."
- **HARD**: blocking; export is denied until the underlying issue is fixed. Example: "T7 promoter declared with non-DE3 host strain; replace promoter or change host."

### 3.6.2 Rule categories in detail

- **MR (Molecular Rule)** — biological correctness. Examples: in-frame stop codons; missing RBS / Kozak; ori-host mismatch; marker-strain mismatch; rare-codon clusters; restriction-site uniqueness; promoter-strength expectations; intron splice-site integrity.
- **WR (Wet-lab Rule)** — bench feasibility. Examples: Gibson homology-arm length; Golden Gate overhang fidelity (Pryor 2018 PMID 30153100); primer Tm divergence > 5 deg C; fragment count exceeds chemistry's reasonable scale; assembly enzymatic dependencies (e.g., NEB enzyme availability).
- **SR (Synthesis-vendor Rule)** — vendor constraints. Examples: insert length > vendor maximum single-fragment; vendor-prohibited motifs (long homopolymers, certain repeats, certain secondary-structure elements); GC content outside vendor window; sequence cost above project budget.
- **BR (Biosafety Rule)** — biosafety / biosecurity. Examples: BR-16 missing SnapGene cross-check; cargo flagged as elevated-BSL; screening verdict elevated; replication-competence advisory.
- **MS (MS2 / VLP rule)** — specific to MS2 / VLP / phage-derived design. Examples: packaging-signal handling; capsid-expression policy; helper-function separation; cargo-size budget against capsid; replication-competence / infectivity boundary.

### 3.6.3 Reading the report

Read from top (HARD) to bottom (INFO). Resolve all HARDs by editing the design (return to the Wizard, edit fields, re-build). Then read each SOFT in order:

- For `caution` items, decide acknowledge / decline / escalate.
- For `strong_caution` items, decide acknowledge with detailed justification / decline (which routes to an alternative reviewer) / escalate (which requires institutional sign-off).
- For `info` items, you do not need to act, but reviewing them gives you confidence in the build.

INFO items are useful when handing off to a reviewer: they show that the engine actually evaluated the construct, not that it stayed silent.

## 3.7 Advisory Actions

Every `caution` and `strong_caution` advisory requires an explicit action (FR-ADV-04, ARCHITECTURE.md § 1.9 / v1.5 sponsor strengthening). The three valid actions are:

1. **Acknowledge** — accept the advisory, supply a justification of >= 20 characters and a cryptographic signature (your local key, configured per Appendix A.6). The engine emits a `RiskAdvisoryAcknowledged` event into the governance event stream with the signed `DecisionRecord`.

2. **Decline** — route the construct to an alternative reviewer (a dual-control pattern). The engine emits `RiskAdvisoryDeclined`. The construct cannot advance to authorisation until the alternative reviewer acts.

3. **Escalate** — request institutional sign-off. The engine emits `RiskAdvisoryEscalated`. The construct is queued in the Review Queue (§ 3.9) until an Administrator (or Reviewer with the corresponding role) signs.

There is no "dismiss" or "ignore" affordance (UR-11; FR-ADV-01). A static CI gate `no-passive-advisory-bypass-check` asserts at build time that the authorisation pipeline cannot reach `OperationalProtocolAuthorised` without observing the corresponding acknowledgement events for every `caution` / `strong_caution` advisory.

### 3.7.1 Signing a DecisionRecord

The first time you act on an advisory in a session, the UI prompts you for your local signing key. Configure this per Appendix A.6 (key path defaults to `~/.cevd/keys/<user-id>.pem`; supports ED25519 or RSA-2048). The key signs the `DecisionRecord` content hash (which includes the advisory ID, the justification text, the timestamp, the actor's principal ID, and the construct's checksum). The signature is verifiable by anyone with the corresponding public key (which is in the export bundle's `keys/` directory).

This is not security theatre. It is what makes the audit log institutional-grade: at a future date, anyone reviewing the design can verify that the acknowledgements really did come from the named user, were made at the recorded time, and applied to the unmodified construct.

## 3.8 Exporting Design Bundles

Once validation is clear and authorisation has passed, click "Export bundle" on the Design Summary panel. The Toolkit produces a ZIP archive with the following structure:

```
my-construct-2026-05-23-abc123/
  README.md                       # bundle overview, version, DerivationEnvironment hash
  manifest.yaml                   # canonical machine-readable manifest
  sequences/
    construct.gb                  # primary GenBank (annotated, SnapGene-compatible)
    construct.sbol3.xml           # SBOL 3.1.x
    construct.fasta               # FASTA of full construct
    insert.fasta                  # FASTA of insert only (cargo)
    primers.fasta                 # primer set
  design/
    design_realisation_plan.md    # the DesignRealisationPlan (human-readable)
    construct_graph.json          # the typed construct graph
    compatibility_matrix.json     # the compatibility matrix as JSON
    validation_report.json        # the full validation report
    controls.json                 # the ControlSet
    risk_advisory_report.json     # the RiskAdvisoryReport
  audit/
    decision_records.jsonl        # signed DecisionRecords (advisory acknowledgements)
    governance_events.jsonl       # AdvisoryWarningPresented, RiskAdvisoryAcknowledged, etc.
    derivation_environment.json   # full DerivationEnvironment record
    derivation_environment.sha256 # the canonical bundle hash
  keys/
    <signers>.pub                 # public keys of every actor in this bundle
  vendor/
    twist_submission.tsv          # Twist-formatted synthesis order (if vendor adapter ran)
    idt_gblock_spec.tsv           # IDT gBlock spec
    genscript_form.tsv            # GenScript order form
  citations/
    citations.bib                 # BibTeX of every PMID / DOI cited in advisories
```

The bundle is self-contained. Anyone receiving it can:

- Open `construct.gb` in SnapGene, ApE, Benchling, or Geneious for visual inspection.
- Parse `construct.sbol3.xml` with any SBOL3-compliant tool.
- Read `design_realisation_plan.md` as a human-readable spec.
- Verify `derivation_environment.sha256` matches the contents of `derivation_environment.json` (reproducibility check).
- Verify every signature in `decision_records.jsonl` against the public keys in `keys/`.
- Re-run the same design in a fresh Toolkit installation given the same catalogue versions and inputs and obtain byte-identical outputs.

This last property is the central reproducibility guarantee (`ARCHITECTURE.md` § 1 item 6; C6). It is what makes the bundle suitable for audit, archive, and regulatory submission.

## 3.9 Admin / Review Queue

The Review Queue is the admin surface (`/admin/queue` in the UI) where Reviewers and Administrators see:

- All `RiskAdvisoryEscalated` cases waiting for institutional sign-off.
- All `WATCHLIST` / `MANUAL_REVIEW_REQUIRED` screening verdicts waiting for review.
- All declined advisories that have been routed to alternative reviewers.
- Pending `AuthorisationProfile` grant / modify / revoke requests.

Each queue entry shows the construct ID, the advisory or screening item, the actor who submitted it, the timestamp, and a "Review" button.

For Reviewers (and Administrators acting as Reviewers — see UR-10 / FR-AUTH-13/14), the action is to sign off (or decline) the item. The Toolkit records the `signer_role` on the resulting event so the audit trail captures whether a dedicated Reviewer or an Administrator-acting-as-Reviewer signed.

For Administrators, the queue also exposes:

- AuthorisationProfile grant / modify / revoke actions (REQUIREMENTS.md UR-09; FR-AUTH-01..12).
- SOP template registration (the SopTemplateReadPort is admin-write; users cannot register SOPs themselves).
- Risk advisory catalogue updates (admin-controlled; the `catalogues/risk_advisories.yaml` is editable but the Toolkit refuses to load an unsigned version).

## 3.10 Audit Trail

The Audit Trail surface (`/admin/audit` in the UI; or the `audit/governance_events.jsonl` file in every export bundle) is the canonical record of every governance-relevant action.

Each event is a typed `DomainEvent` subclass (ARCHITECTURE.md § 4.7) carrying:

- A timestamp (UTC, ISO 8601).
- A principal ID (the actor).
- A subject ID (the design session, construct, advisory, profile).
- A content hash.
- A cryptographic signature (where applicable).
- A typed payload (depends on event class).

Events are append-only. The Toolkit refuses to mutate or delete an event; only an Administrator can prune (and the prune itself becomes an event).

You can:

- **Browse** events by date, principal, subject, or type.
- **Replay** a design session from its event log (the Toolkit reconstructs the construct graph and validation report from the events).
- **Diff** two design sessions to see what changed.
- **Export** the event log as JSONL for external audit or archive.

The audit trail is what makes the Toolkit suitable for use in a regulated environment (REQUIREMENTS.md UR-09..11; ARCHITECTURE.md v1.5 sponsor strengthening). It is also the canonical reproducibility artefact: given the audit log and the `DerivationEnvironment`, the design can be reconstructed at any future date.

---

# Part 4 - Bench execution

This part covers the wet-lab procedures that follow a Toolkit design. We deliberately keep the descriptions condensed because Appendix I contains full step-by-step protocols for the most important procedures. The aim of this part is to give you the **decision logic** between Toolkit output and bench reality: what to order, who to order it from, when to PCR vs synthesise, when to use Gibson vs Golden Gate, how to triage a failed transformation, how to test a small expression batch before scaling.

If you have not used a wet lab before, do not start with this part. Pair with a senior researcher for your first few designs and use the published protocols (Sambrook 4th ed. is the canonical book; per-host protocols are linked below).

## 4.1 Gene synthesis ordering

Modern molecular cloning is increasingly synthesis-first. The Toolkit's export bundle includes pre-formatted submission files for the three major vendors (`vendor/twist_submission.tsv`, `vendor/idt_gblock_spec.tsv`, `vendor/genscript_form.tsv`). Decide the vendor based on:

| Vendor | Strengths | Limitations | Typical turnaround |
|---|---|---|---|
| **Twist Bioscience** | Cheapest per bp for medium-size synthesis; web ordering portal; cloning into pTwist backbones included; integrated screening | Repeat / GC limits; some sequence-complexity surcharges | 5-10 business days |
| **IDT (gBlocks, gBlock HiFi, Megamer)** | Fast small-fragment synthesis (gBlocks up to ~3 kb); ssODN for HDR / mutagenesis; primer ordering combined | Per-bp cost higher than Twist for larger inserts; clonal product as separate service | 3-7 business days for gBlocks; 7-10 for clonal |
| **GenScript** | Best for full plasmid synthesis + cloning + sequencing in one order; very long inserts (> 10 kb); codon-optimisation service included; subcloning service | Slower than gBlocks; pricier; portal less ergonomic | 10-20 business days |

### 4.1.1 Choosing what to synthesise vs PCR-amplify

| Situation | Recommend |
|---|---|
| Cargo < 2 kb, parental plasmid in hand | PCR-amplify with Gibson-compatible homology arms |
| Cargo > 2 kb, no parental plasmid | Synthesise (Twist clonal or gBlock if < 3 kb) |
| Codon-optimised version of native gene | Synthesise |
| Cargo with extensive mutagenesis (>5 sites) | Synthesise |
| Cargo with rare restriction sites or GC challenge | Use vendor with explicit complexity acceptance |
| Full plasmid replacement (whole backbone change) | GenScript clonal synthesis |
| sgRNA insert (24 nt + overhangs) | Order as paired oligos; anneal in-house |

### 4.1.2 Submitting the order

Open the vendor submission file from the export bundle and review every row. The Toolkit's vendor adapters incorporate the vendor's published screening / GC / repeat constraints (SR-* rules), but vendor policies change; double-check the most recent constraints on the vendor's website. After submission, the vendor's own screening runs again. Verdicts:

- **CLEAR** — order proceeds.
- **WATCHLIST / MANUAL_REVIEW** — vendor flags the order for human review; respond promptly to vendor questions; the Toolkit records your responses as `DecisionRecord` events in the bundle's audit log.
- **HIT** — vendor refuses to synthesise; you must escalate to your IBC, redesign the cargo, or both. The Toolkit will not produce an export bundle that lists `HIT` as resolved without an escalation record.

### 4.1.3 Receiving the synthesised DNA

- Verify the **tube label** matches the order.
- For Twist clonal: arrives as glycerol stock or plasmid DNA; transform per Appendix I § I.7; mini-prep; verify by digest and Sanger.
- For IDT gBlocks: arrives as ~250 ng or ~1 ug of linear dsDNA; resuspend in TE (10 mM Tris-HCl, 0.1 mM EDTA, pH 8.0) to a working concentration of 10-20 ng/uL.
- For GenScript clonal: arrives as plasmid DNA + sequencing trace; verify the trace matches your designed sequence (the Toolkit's `tools/verify_sanger.py` will compare a SnapGene-exported `.gb` to a Sanger `.ab1`).

## 4.2 Receiving and assembling

The Toolkit emits a chemistry-specific assembly route in the DesignRealisationPlan. The bench procedures map directly to the chosen chemistry.

### 4.2.1 Gibson / NEBuilder HiFi

Gibson assembly (Gibson 2009 PMID 19363495) is the workhorse for 2-5 fragment assembly with 25-40 bp homology arms.

Materials:

- NEBuilder HiFi DNA Assembly Master Mix (or DIY Gibson mix: 5x ISO buffer + T5 exonuclease + Phusion polymerase + Taq DNA ligase).
- Fragments at 50-100 ng / 0.5 pmol per reaction; backbone:insert at 1:2 molar ratio.
- Chemically competent DH5-alpha or NEB-5alpha.

Protocol (see Appendix I § I.5 for full):

1. Combine fragments in 10-15 uL total (PCR products in their reaction buffer are OK; for cleanest results, gel-purify).
2. Add NEBuilder HiFi master mix (1:1 v/v).
3. Incubate 50 deg C for 15 min (2-fragment) to 60 min (5-fragment).
4. Transform 2 uL into competent cells (Appendix I § I.7).
5. Plate; pick colonies; mini-prep; verify.

### 4.2.2 Golden Gate

Golden Gate (Engler 2008 PMID 18948503) uses a Type IIS enzyme (BsaI, BsmBI / Esp3I, SapI) plus T4 DNA ligase in a single tube. Designed 4-nt overhangs determine the order and orientation of fragments. Modern Golden Gate kits (MoClo, YTK, GreenGate, GoldenBraid, JUMP, MIDAS) provide standardised overhang sets and a parts library.

The Toolkit's `engine.overhang` (Pryor 2018 PMID 30153100 / Potapov 2018 PMID 30192978) selects overhang sets that maximise ligation fidelity for your fragment count.

Protocol (see Appendix I § I.6):

1. Combine 50-100 ng of each donor part + 50-100 ng of the destination vector.
2. Add BsaI-HF v2 (or BsmBI-v2) + T4 DNA ligase + 10x T4 buffer.
3. Cycle: 30 cycles of (37 deg C 2 min, 16 deg C 5 min); then 60 deg C 10 min (final ligation); then 80 deg C 5 min (enzyme heat-kill).
4. Transform 2 uL into competent cells.

The chemistry is particularly good for 5-15 fragment assembly with high efficiency when overhangs are chosen well; the Toolkit's overhang optimiser is integrated.

### 4.2.3 Restriction + ligation

The classical workhorse, still relevant when:

- You have a parental plasmid with the right MCS.
- You only need to swap one fragment.
- You want to avoid PCR (no polymerase-introduced errors).

Protocol (Appendix I § I.2 + I.4):

1. Digest backbone and insert with the chosen enzyme(s); gel-purify the desired bands.
2. Set up ligation with T4 DNA ligase at 16 deg C overnight; backbone:insert at 1:3 to 1:5 molar.
3. Transform 2-5 uL into competent cells.

For single-enzyme ligations, dephosphorylate the backbone (CIP or rSAP) to suppress self-ligation.

### 4.2.4 Gateway

Gateway (Hartley 2000 PMID 10721974) is a recombinase-based two-step system (BP reaction enters the cargo into a pDONR entry vector; LR reaction transfers from entry to a destination vector). Heavily used in large-scale ORF clone collections (the Human ORFeome).

The Toolkit's Gateway adapter emits the attB-flanked PCR primers, the entry vector spec, and the destination-vector spec. Bench protocols follow the manufacturer instructions.

### 4.2.5 LIC, SLIC, USER, IVA, In-Fusion

Variant chemistries the Toolkit supports. Each has its own vendor product:

- **LIC (Ligation-Independent Cloning)** — T4 polymerase creates single-stranded overhangs in the absence of dNTPs; anneal at room temperature; transform directly.
- **SLIC** — similar to LIC but uses RecA.
- **USER** — Uracil-Specific Excision Reagent; uracil-containing primers generate 3' overhangs after USER treatment.
- **IVA (In-Vivo Assembly)** — exploits *E. coli*'s native homologous recombination; transform PCR fragments with ~15 bp homology directly.
- **In-Fusion** — Takara's commercial Gibson analog using a proprietary 3' exonuclease.

## 4.3 Transformation into E. coli

After assembly, you transform the assembly mix into chemically-competent (or electrocompetent) *E. coli* for amplification.

### 4.3.1 Strain choice

| Strain | Use |
|---|---|
| DH5-alpha | Default cloning; high transformation efficiency; recA1 endA1 |
| NEB 5-alpha | DH5-alpha-equivalent; recommended for Gibson |
| TOP10 | Default for pCR / TOPO products; recA1 endA1 mcrA |
| Stbl3 / Stbl4 | For lentiviral / unstable LTR-containing constructs (recA13) |
| DH10B / DH10beta | High electroporation efficiency; for large libraries |
| XL10-Gold | For very large plasmids (up to ~50 kb); recA1 endA1 |

### 4.3.2 Heat-shock (chemically competent)

Appendix I § I.7 has the full protocol. Condensed:

1. Thaw 50 uL of competent cells on ice.
2. Add 1-5 uL of DNA (no more than 5% of cell volume).
3. Incubate on ice 20-30 min.
4. Heat-shock at 42 deg C for 30-45 s.
5. Return to ice for 2 min.
6. Add 950 uL of SOC; recover at 37 deg C with shaking for 1 h.
7. Plate 50-100 uL on selective LB-agar; incubate overnight at 37 deg C.

### 4.3.3 Electroporation

Higher efficiency (10^9-10^10 transformants per ug DNA vs 10^6-10^8 for chemical). Requires:

- Electrocompetent cells (commercial or in-house glycerol-washed).
- 1- or 2-mm gap cuvettes.
- Electroporator (Bio-Rad Gene Pulser, BTX, or similar).
- Salt-free DNA (Gibson reactions OK if diluted 10x; ligation mixes should be drop-dialysed first).

Conditions: 1.8 kV for 1-mm cuvettes; 2.5 kV for 2-mm. Time constant should be 4.5-5.5 ms. Add 950 uL SOC immediately; recover 37 deg C 1 h; plate.

## 4.4 Transformation into expression host

After verifying the plasmid in *E. coli*, transform into the expression host.

### 4.4.1 E. coli expression hosts

Re-transform the verified plasmid into BL21(DE3), Rosetta(DE3), Origami(DE3), SHuffle, etc. by the same heat-shock protocol. Selection plate must contain the construct's resistance marker; some expression strains have an additional chromosomal marker (e.g., pLysS in BL21(DE3)pLysS is Cm-resistant).

### 4.4.2 Yeast (S. cerevisiae LiAc)

Appendix I § I.10 has the full LiAc / PEG / heat-shock protocol (Gietz & Schiestl 2007 PMID 17401334). Condensed:

1. Grow 5 mL YPD overnight; subculture to OD600 ~0.5 in 50 mL YPD for ~4 h.
2. Pellet cells; wash with sterile water; wash with 100 mM LiAc.
3. Resuspend cells in 100 mM LiAc; aliquot ~50 uL per transformation.
4. To each aliquot add: 240 uL of 50% PEG-3350, 36 uL of 1 M LiAc, 50 uL of 2 mg/mL sheared salmon-sperm carrier DNA, 5-10 uL of plasmid DNA (~100-500 ng).
5. Vortex; incubate 30 deg C 30 min; heat-shock 42 deg C 25 min.
6. Pellet; resuspend in 100 uL water; plate on selective SD medium; incubate 30 deg C for 2-3 days.

### 4.4.3 Pichia electroporation

Appendix I § I.11. Linearise the pPICZ vector (SacI or PmeI; promotes single-crossover integration at the AOX1 locus). Transform 1-5 ug of linearised plasmid into 80 uL of electrocompetent Pichia (1.5 kV, 1-mm cuvette). Recover in 1 mL 1 M sorbitol at 30 deg C for 1-2 h. Plate on YPDS + Zeocin (100-1000 ug/mL); incubate 30 deg C for 3-5 days.

### 4.4.4 Mammalian (lipofection / electroporation)

Appendix I § I.9. For HEK293 transient (Lipofectamine 3000):

1. Seed cells at 70-80% confluence in DMEM + 10% FBS.
2. Per well of 6-well: dilute 2.5 ug DNA in 125 uL Opti-MEM; dilute 7.5 uL Lipofectamine 3000 in 125 uL Opti-MEM; combine; incubate 5-10 min at room temperature.
3. Add to cells; gently rock; incubate at 37 deg C.
4. Change medium at 4-6 h post-transfection.
5. Harvest at 24-72 h depending on cargo.

For electroporation (Neon, Lonza Nucleofector): follow the device's tissue-specific program; uses 1-5 ug DNA per 200,000 cells.

For viral packaging (lentivirus / AAV), transfect HEK293T with the three- or four-plasmid set as described in Part 2.6; collect supernatant at 48 h.

## 4.5 Verifying expression

### 4.5.1 Bacterial

After IPTG induction:

- Pellet 1 mL of culture; resuspend in SDS-PAGE loading buffer; run on SDS-PAGE; stain with Coomassie. A clearly enhanced band at the expected size in induced vs uninduced lane is the first sign of expression.
- For low-expression proteins, Western with anti-tag antibody (His6, FLAG) is more sensitive.
- Soluble vs insoluble: lyse cells by sonication or freeze-thaw + lysozyme; spin; run supernatant (soluble) and pellet (inclusion body) side by side.

### 4.5.2 Yeast and Pichia

- Glass-bead beating or lyticase + freeze-thaw to lyse.
- SDS-PAGE / Western (His6 tag detection is standard).
- For secreted protein, the supernatant goes directly to SDS-PAGE / Western.

### 4.5.3 Mammalian

- Lyse cells in RIPA or NP-40 lysis buffer with protease inhibitors.
- SDS-PAGE / Western with anti-tag antibody.
- For fluorescent fusions, image directly under a fluorescence microscope (no fixation needed for live cells).
- For secreted protein, collect supernatant; concentrate (Amicon spin column with appropriate MWCO); SDS-PAGE / Western.

### 4.5.4 Functional verification

Beyond Western: enzymatic activity assay (kinetic), binding assay (BLI / SPR / ITC / pulldown), cellular phenotype (knockout phenotype reversal, reporter readout, FACS).

## 4.6 Scale-up and purification

When small-scale expression is confirmed, scale up.

### 4.6.1 Bacterial scale-up

Typical: 0.5-2 L shake-flask culture in LB or 2xYT. Induce at OD600 ~0.6-0.8 with IPTG (0.1-1 mM). Express 4-6 h at 37 deg C for soluble well-expressed proteins; 16-24 h at 18 deg C for solubility-challenged proteins.

For larger scale or higher density, use bioreactor (1-10 L) with controlled aeration, pH, and temperature. Pichia and CHO are routinely run in bioreactors at 5-100 L scale for industrial production.

### 4.6.2 Purification by tag

Match tag to chromatography:

| Tag | Chromatography | Buffer |
|---|---|---|
| His6 | Ni-NTA / Ni-IDA / Co-NTA / Talon | Bind in 10-20 mM imidazole; elute in 250-500 mM imidazole |
| GST | Glutathione-agarose | Bind in PBS; elute in 10-30 mM reduced glutathione, 50 mM Tris pH 8.0 |
| MBP | Amylose-resin | Bind in MBP column buffer; elute in 10 mM maltose |
| FLAG | Anti-FLAG M2 affinity gel | Elute with 100-200 ug/mL FLAG peptide or low-pH glycine |
| Strep-II | Strep-Tactin resin | Elute with 2.5-10 mM desthiobiotin |
| HA | Anti-HA monoclonal resin | Elute with HA peptide or low-pH |
| Avi (biotinylated by BirA in vivo) | Streptavidin / monomeric avidin | Elute conditions vary |

After affinity capture: ion exchange or size-exclusion polishing to remove contaminants and aggregates.

### 4.6.3 Antibody / mammalian purification

For IgG / Fab, the canonical workflow is Protein A (for IgG1) or Protein G (broader specificity) affinity capture followed by SEC polishing. Elute Protein A with low-pH glycine (pH 2.7-3.0); neutralise immediately with 1 M Tris pH 9.0 to a final pH of 7.0-7.5.

For other secreted proteins, use the affinity tag (His6 or Strep-II) on the supernatant after Amicon concentration.

---

# Part 5 - QC and troubleshooting

This part covers quality-control checkpoints and troubleshooting workflows. The Toolkit's design discipline pushes most failure modes to design-time, but bench failures still happen. This part teaches you to triage them.

## 5.1 Pre-bench QC and manual SnapGene cross-check (BR-16)

Pre-bench QC is the single most cost-effective gate in the entire workflow. The Toolkit deliberately requires:

1. **Validation Report clear of HARDs**.
2. **All SOFTs acknowledged with signed DecisionRecords**.
3. **Manual SnapGene cross-check (BR-16)** of the final construct against the exported GenBank.

If any of the three is missing, the export bundle either does not generate or generates with an embedded "BR-16 unconfirmed" flag that downstream collaborators will see.

### 5.1.1 BR-16 procedure (repeated for emphasis)

1. Open the exported `construct.gb` in SnapGene.
2. Open the construct's original source in SnapGene (or your reference) side by side.
3. Compare:
   - Sequence length.
   - GC content.
   - Topology (circular vs linear).
   - Feature names, types, orientations, and coordinates.
   - Restriction site map.
   - Primer-binding sites.
4. Note any discrepancies. If the Toolkit's parser interpreted an unusual feature qualifier in an unexpected way, either edit the GenBank and re-import, or document the discrepancy in the BR-16 justification text.
5. Click "BR-16 confirmed"; supply a >= 20-char justification.

### 5.1.2 Sequence verification before ordering

For synthesised constructs, re-read the final designed sequence once more in SnapGene before clicking the vendor's "place order" button. Print it; eyeball it; check the start codon context, the linker, the stop codon, the polyA, and any restriction sites you mentioned. The 5 minutes you spend here saves a week downstream.

## 5.2 At-bench QC

### 5.2.1 Diagnostic restriction digest

After transformation, mini-prep, and before sequencing, run a diagnostic restriction digest. The Toolkit's export bundle includes the recommended digest in `design/design_realisation_plan.md`:

- Pick 2-3 enzymes that cut the construct in well-separated positions (e.g., one in the backbone and one in the insert).
- Predict the fragment sizes from the SnapGene map; record them in your notebook.
- Run a 1% agarose gel; compare observed to predicted.

A correct digest is your first strong evidence that the assembly worked.

### 5.2.2 Sanger sequencing

For cloning verification, Sanger-sequence the junctions and the full insert. Primers:

- Upstream of the 5' junction (e.g., T7 promoter primer for pET).
- Downstream of the 3' junction (e.g., T7 terminator primer).
- For inserts > 800 bp, internal walking primers every ~700 bp.

The Toolkit's primer designer (`engine.primer`) emits Sanger primers in the export bundle. Compare the trace `.ab1` files to the expected sequence; the Toolkit's `tools/verify_sanger.py` automates the comparison if you want it.

### 5.2.3 Colony PCR

Faster than mini-prep + digest for screening many colonies:

- Pick colony with a toothpick into 20 uL of PCR reaction with primers flanking the insert junction.
- Cycle: 95 deg C 5 min initial; 30 cycles of 95 / 55 / 72 deg C; 72 deg C 5 min final.
- Run on a 1% gel; correct insert shows a band of the expected size.

## 5.3 Post-expression QC

### 5.3.1 Expression-level QC

After SDS-PAGE / Western confirms expression, quantify yield:

- Coomassie band intensity vs BSA standards.
- BCA / Bradford / A280 on the soluble fraction after lysis.
- Anti-tag Western with serial dilutions vs a standard.

If yield is below your project's target, troubleshoot per Appendix J ("Low yield" row).

### 5.3.2 Functional QC

Demonstrate the cargo does what it should:

- Enzymatic activity (kinetic).
- Binding to its known partner (BLI, SPR, ITC, pulldown).
- Cell-based phenotype.

For antibody cargos, run an ELISA against the antigen of interest and measure the EC50.

### 5.3.3 Purity QC

For purified protein:

- SDS-PAGE under reducing and non-reducing conditions (looks for disulfide-linked species).
- SEC analytical run (looks for aggregation; typical target > 90% monomer).
- Endotoxin assay (LAL or recombinant Factor C) if downstream use is cell-based.
- Mass spectrometry (intact mass to confirm identity and modifications).

## 5.4 Troubleshooting decision tree

See Appendix J for the full table of ~ 40 symptoms / causes / diagnostics / fixes / Toolkit features to recheck.

The high-level decision tree:

```
[Bench failure observed]
        |
        v
+-------+-------+
| No colonies?  |--> Transformation efficiency
+---------------+   - DNA OK?
        |           - Cells OK?
        |           - Selection OK?
        |
+-------+-------+
| Wrong size?   |--> Restriction map mismatch
+---------------+   - Diagnostic digest agrees?
        |           - Re-run Sanger
        |
+-------+-------+
| No expression?|--> Promoter / RBS / Kozak / induction
+---------------+   - Strain has the right RNAP?
        |           - Induction conditions right?
        |           - Western with anti-tag?
        |
+-------+-------+
| Insoluble?    |--> Folding
+---------------+   - Lower temperature?
        |           - Solubility tag?
        |           - Refolding from inclusion?
        |
+-------+-------+
| Wrong activity?|--> Codon, tag, fusion frame
+---------------+   - Sanger confirms sequence?
                    - Tag interferes?
                    - Protease cleaved?
```

For each symptom, the corresponding Appendix J row lists which Toolkit feature to recheck (Validation Report rule, Compatibility Matrix cell, Vector Map feature). The pattern is: if the bench failure could have been caught at design-time, the Toolkit knows which rule covered it; rerun the validation with the rule explicitly enabled and confirm.

## 5.5 When to redesign

Redesigning is sometimes cheaper than troubleshooting. Indicators that suggest a redesign is the right move:

- Multiple rounds of mutagenesis have not rescued expression / activity.
- The cargo is fundamentally incompatible with the chosen host (e.g., a eukaryotic membrane protein in *E. coli*).
- The chosen vector backbone is no longer maintained / supported.
- The cargo is hitting fundamental vendor synthesis limits (length, repeat content).
- The host strain is exhibiting unstable behaviour (recombination of repeats, instability of selection marker).

When redesigning:

- Return to the Decision Wizard; re-open the existing session.
- Edit the relevant Wizard step.
- The engine re-runs validation; surfaces a design diff (`/admin/diff/<session-id>`) showing what changed.
- Capture the rationale in the DecisionRecord ("Redesigned because v1 expression was undetectable in BL21(DE3); switched to Lemo21(DE3) per Wagner 2008 PMID 18369191 to tune T7 polymerase expression").

---

# Part 6 - Collaborators and downstream

## 6.1 SnapGene (BR-16 NORMATIVE; manual cross-check)

SnapGene is the de-facto desktop standard for visualising and editing plasmid maps. The Toolkit's interoperability with SnapGene is **normative**: every design that proceeds to the bench must be cross-checked in SnapGene at least once (BR-16). The cross-check is **manual by a human in a browser**; the Toolkit will not automate, scrape, or otherwise programmatically extract content from SnapGene.

This posture is deliberate and is documented in the IP-audit memo (see Appendix M). SnapGene is a commercial product whose data, file format, and software are the property of Insightful Science / Dotmatics. The Toolkit's interoperability is via the open GenBank format (which both products read and write) and via a manual cross-check process. The Toolkit does not redistribute SnapGene content, does not include SnapGene-derived data in the export bundle, and does not embed SnapGene-trained models.

For the cross-check procedure see § 3.3.3 (BR-16 procedure).

## 6.2 Benchling, ApE, GeneStudio

These are alternative vector-editing tools that accept GenBank input. The Toolkit's export bundle is round-trip-compatible with all three. If your collaborator uses one of these tools, send them the `sequences/construct.gb` file from the bundle; they can open, view, and re-export. Visual layout (feature colours, label positions) varies by tool; the Toolkit's GenBank uses canonical SnapGene-recognised colours and feature types.

For Benchling specifically: Benchling supports GenBank import via the Notebook + Sequences workflow. Drag the `construct.gb` into a sequence record; Benchling auto-annotates from its public-sequence library; manually reconcile any conflicts.

For ApE (A Plasmid Editor): open the `.gb` file directly. ApE is open-source and free for academic use; useful for users who want a lightweight alternative to SnapGene.

For GeneStudio Pro: import via File > Import > GenBank.

## 6.3 Synthesis-vendor handoff

The export bundle's `vendor/` directory contains the pre-formatted submission files for Twist, IDT, and GenScript (see § 4.1.2). For each vendor:

- Open the vendor's web portal.
- Log in to your account; if you do not have one, register at the vendor's website (academic and commercial accounts have different pricing).
- For Twist: upload the `twist_submission.tsv` directly via the bulk-upload endpoint; review each row in the portal; place order.
- For IDT (gBlocks Gene Fragments): copy the sequence and order fields from `idt_gblock_spec.tsv` into the gBlocks order form; ensure the IDT cost screen accepts the sequence (some sequences exceed complexity limits and IDT will refuse).
- For GenScript: use the codon-optimisation + cloning service; upload the `genscript_form.tsv` as part of the project submission.

After submission, the vendor's screening runs again. Respond promptly to any vendor questions; document responses in your project notebook (or as DecisionRecords if you re-engage the Toolkit's audit log).

## 6.4 IBC reporting

The Institutional Biosafety Committee (IBC) is the body responsible for reviewing recombinant-DNA work at your institution. For BSL-2 and BSL-3 work, IBC review is mandatory; for BSL-1 work, IBC may require notification but not review.

The Toolkit's export bundle includes everything an IBC needs:

- The full annotated construct (`sequences/construct.gb`).
- The DesignRealisationPlan (`design/design_realisation_plan.md`) including the biosafety classification.
- The RiskAdvisoryReport (`design/risk_advisory_report.json`).
- The Validation Report (`design/validation_report.json`).
- The DerivationEnvironment hash (reproducibility).
- The signed DecisionRecords for every advisory acknowledgement.
- The screening verdict (CLEAR / WATCHLIST / etc.) from the configured screening adapter(s).

For most institutions you will need to also fill an IBC submission form (institution-specific). The Toolkit does not produce this form; consult your local IBC office.

## 6.5 IP for commercialisation (Fork-Readiness Memo)

If you plan to commercialise a product built on top of the Toolkit, read the Fork-Readiness Memo in `docs/fork-readiness/` and the IP audit memo (see Appendix M).

Key facts for commercialisation:

- The Toolkit is GPL-3.0-only; any software that links to or extends the Toolkit's core is itself GPL-3.0 (copyleft).
- The Toolkit's commercial fork posture is documented in the Fork-Readiness Memo; the Toolkit is GMExpression's property and the right to fork a commercial closed-source line rests with GMExpression.
- Catalogue data (markers, hosts, ports, parts) carries its own licensing; some records are CC-BY-SA, which restricts share-alike-bound use cases. The v0.2 corpus manifest maintains `partition: full` and `partition: sa_free` variants so a future commercial deployment can select the SA-free training partition (FR-ML-15; BR-15..17).
- Patent / FTO analysis is handled by the `/ip-auditor` skill, not the Toolkit; engage it before any commercial submission.

For any commercialisation conversation, the canonical starting point is the latest IP-audit memo (currently `docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit_v2.md`).

---

# Appendix A - Installation and configuration

This appendix gives the full installation procedure for Windows 11, the platform the Toolkit is primarily developed and tested on. Linux and macOS installation are analogous; the differences are footnoted.

## A.1 Prerequisites

- **Operating system**: Windows 11 Pro (10.0.26200 or newer); Windows 10 also works but is no longer the development target. Linux (Ubuntu 22.04+, Debian 12+, Fedora 39+) and macOS 14+ are supported.
- **Python**: version >= 3.11.15, < 3.12. The pinned version is 3.11.15. Newer Python 3.12 / 3.13 are not yet supported; the project's `pyproject.toml` enforces this.
- **uv**: the project's package and environment manager (https://github.com/astral-sh/uv). Install per the uv documentation; on Windows: `winget install --id Astral.Uv` or `pip install uv`.
- **Node.js**: version >= 20 LTS for the React UI.
- **git**: any recent version.
- **PowerShell** (Windows) or **bash** (Linux / macOS).
- **A modern web browser** (Chromium / Edge / Firefox / Safari).
- **Optional**: SnapGene desktop application for the BR-16 manual cross-check. SnapGene is licensed separately; users on academic accounts often have free access via institutional licence.

## A.2 Clone the repository

```powershell
cd C:\Users\<your-username>\Projects
git clone https://github.com/GMExpression/cloning-expression-vector-design.git
cd cloning-expression-vector-design
```

The project root path is referenced in many places (manifests, audit memos, the architecture document). If you place the repository at a different path, adjust the references accordingly. Note: the canonical project root in this manual is `C:\Users\tocvi\OneDrive\文档\Project_Code\Cloning_Expression_Vector_Design - Codex` because the maintainer's machine uses it; any other path is equivalent.

> **Windows / cp1252 pitfall**: the canonical project root contains the Unicode character 文档 (Chinese: "documents"). On Windows machines whose default console encoding is cp1252, printing an absolute Path object via `print(some_path)` triggers a `UnicodeEncodeError`. The Toolkit's CLI and tools never `print()` an absolute Path; they format the path as a UTF-8 string or use `repr()` first. If you are extending the codebase, follow the same convention.

## A.3 Python environment

```powershell
uv sync
```

This installs Python dependencies into `.venv/` per the lockfile `uv.lock`. To install optional extras (I / O adapters: snapgene-reader, biopython, sbol3):

```powershell
uv sync --extra io
```

To install all extras (for development):

```powershell
uv sync --extra dev --extra io --extra docs
```

## A.4 Pre-commit hooks

```powershell
pre-commit install
```

The project uses pre-commit hooks for formatting (ruff format), linting (ruff check), type checking (mypy --strict), import-linter, and a few project-specific gates (`no-self-authorisation-check`, `no-passive-advisory-bypass-check`, `audit-traceability-check`, `import-linter`, `stale-catalogue-check`, `sop-after-gates-check`, `llm-output-policy-check`, `plugin-manifest-signature`, `port-manifest-sync-check`).

## A.5 UI dependencies

```powershell
cd ui
npm install
cd ..
```

This installs the React + TypeScript + Vite UI dependencies into `ui/node_modules/`.

## A.6 Cryptographic key configuration

The Toolkit signs DecisionRecords with a per-user key. Generate one:

```powershell
mkdir $env:USERPROFILE\.cevd\keys -Force
openssl genpkey -algorithm Ed25519 -out $env:USERPROFILE\.cevd\keys\<user-id>.pem
openssl pkey -in $env:USERPROFILE\.cevd\keys\<user-id>.pem -pubout -out $env:USERPROFILE\.cevd\keys\<user-id>.pub
```

Replace `<user-id>` with your stable user ID (the same one you use in git commits). Configure the Toolkit to find the key:

```powershell
$env:CEVD_SIGNING_KEY="$env:USERPROFILE\.cevd\keys\<user-id>.pem"
```

The public key is uploaded into each export bundle's `keys/<user-id>.pub` automatically so collaborators can verify your signatures.

## A.7 Verification

Run the project's smoke tests:

```powershell
$env:PYTHONPATH='src;.'
.\.venv\Scripts\python.exe tools\agenda_consistency_check.py
.\.venv\Scripts\python.exe tools\ci\run_pytest.py -m "not slow"
```

For UI tests:

```powershell
cd ui
npm test
npm run build
```

A successful verification gives you green output from both the Python and UI test suites; the slow / integration tests are not required for a routine smoke check.

## A.8 Launch the UI

```powershell
cd ui
npm run dev -- --port 5173
```

Open `http://127.0.0.1:5173/`.

For headless / API mode:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --port 8000
```

OpenAPI documentation is at `http://127.0.0.1:8000/docs`.

## A.9 Catalogue refresh

Catalogue records (hosts, markers, parts, vendors, enzymes, screening, risk advisories) carry maintenance metadata with `retrieved_at`, `valid_until`, and `review_required_after` dates. A `stale-catalogue-check` CI gate fails if any catalogue is past its `review_required_after` date. Refresh catalogues by editing the YAML files; commits to a catalogue must come with an updated `retrieved_at` timestamp.

## A.10 Optional Docker image

A Dockerfile is provided in the repository root for containerised use:

```powershell
docker build -t cevd:v0.2.1 .
docker run --rm -p 5173:5173 -p 8000:8000 cevd:v0.2.1
```

The container includes the full Python + Node environment and runs both the UI and the API. Catalogue YAML files are baked in; for development, mount the repository as a volume.

---

# Appendix B - Detailed input requirements

This appendix enumerates the inputs required at each Wizard step, plus the import formats supported for existing sequences.

## B.1 Wizard Step 1 - Objective

Required:

- One of the enumerated objectives, or "Other / specialised" + a free-text description of >= 50 characters.

Optional:

- A project identifier (free-text, defaults to a UUID).
- A target date for synthesis / bench start.
- A reference to a parent project / collaborator.

## B.2 Wizard Step 2 - Target host

Required:

- One host strain from the catalogue, or "Other" + a free-text description with the strain genotype and any chromosomal markers.

Optional:

- Secondary host (for shuttle vectors).
- Host operating role (`cloning_propagation`, `expression`, `producer`, `target`, `assembly`, `delivery`, `screening_assay`, `storage`).
- Growth conditions (media, temperature, atmospheric requirements).

## B.3 Wizard Step 3 - Cargo type

Required:

- Cargo type (drop-down) and the cargo sequence (FASTA or GenBank import or paste).

For protein cargo:

- Amino-acid sequence (will be back-translated and codon-optimised) OR native CDS (validated but not re-optimised by default).
- Source organism (for codon-source context).
- Mutations / variants (list of point mutations relative to the canonical sequence).

For sgRNA cargo:

- The 20-nt (SpCas9) or 20-22-nt (SaCas9) or 23-25-nt (Cpf1) protospacer.
- The target genome (for off-target analysis).
- The PAM context (auto-inferred from the chosen Cas variant).

For polycistronic cargo:

- An ordered list of CDSs.
- The inter-ORF linker for each junction (IRES / P2A / T2A / F2A / E2A).

## B.4 Wizard Step 4 - Expression level / induction

Required:

- One promoter from the catalogue (host-appropriate), or "Other" + a free-text description.
- Expected strength: low / medium / high.

Optional:

- Induction conditions (IPTG concentration, arabinose %, galactose %, doxycycline concentration).
- Time-course (when to harvest after induction).

## B.5 Wizard Step 5 - Tagging strategy

Optional (any cargo may have zero, one, or two tags):

- N-terminal tag from the catalogue (His6 / MBP / GST / SUMO / TRX / FLAG / etc.) or "Other".
- N-terminal linker (e.g., GGSGG, (GGGGS)2/3, PreScission cleavage site).
- C-terminal tag from the catalogue.
- C-terminal linker.
- Stop-codon strategy (single TAA, double TAA TAA, TGA, TAG).

## B.6 Wizard Step 6 - Cloning chemistry

Required:

- One assembly chemistry from the enumerated list.

For Gibson:

- Homology-arm length (default 25 bp).
- Maximum acceptable fragment count.

For Golden Gate:

- Type IIS enzyme (BsaI / BsmBI / SapI).
- Toolkit / kit (MoClo, Loop, YTK, GreenGate, GoldenBraid, JUMP, MIDAS).
- Acceptance threshold for overhang fidelity (Pryor 2018 default).

For restriction + ligation:

- Enzyme list (the Toolkit will check uniqueness).
- Whether to dephosphorylate the backbone.

For Gateway:

- Entry / destination vector pair.
- Whether to perform BP, LR, or both.

## B.7 Wizard Step 7 - Biosafety tier

Required:

- BSL-1 / BSL-2 / BSL-3 / BSL-4 (the last is hard-blocked at compile time).
- Cargo organism source.

Optional:

- Pre-existing IBC approval reference / number.
- Operating institution.
- Operating jurisdictional constraints (US NIH Guidelines, EU EFSA, AU OGTR, etc.).

## B.8 Sequence-import formats

| Format | Extension | Notes |
|---|---|---|
| GenBank | `.gb`, `.gbk` | Primary; LOCUS line defines topology |
| SBOL3 | `.xml`, `.ttl` | SBOL 3.1.x with Sequence Ontology terms |
| FASTA | `.fa`, `.fasta` | Sequence only; combine with GFF3 for annotation |
| SnapGene `.dna` | `.dna` | Requires `snapgene-reader` optional dependency |
| EMBL flat file | `.embl`, `.emb` | Flat-file equivalent of GenBank |
| GFF3 | `.gff3`, `.gff` | Annotation only |

For files with multiple records (FASTA, multi-GenBank), the Toolkit prompts to select which record to import.

---

# Appendix C - Process steps reference card

This appendix is a one-page (well, several pages) reference card you can print and stick to the wall above your bench. It enumerates every Toolkit process step (engine + orchestrator) and what each one does to the construct.

## C.1 Engine modules (`src/engine/`)

| Module | Purpose | Inputs | Outputs |
|---|---|---|---|
| `engine.sequence_analysis` | Restriction analysis: site finding, digest simulation, end compatibility, unique-site ranking, diagnostic-digest design, fragment simulation. Topology-aware. | `SequenceRecord`, `EnzymeCatalogue` | site lists, digest fragments, diagnostic-digest design |
| `engine.validation` | Pure DAG evaluator over rules x metrics; consumes `ValidationContext`; incremental re-eval | `ConstructGraph`, `ValidationContext` | `ValidationReport` (typed findings) |
| `engine.dependencies` | Field-and-metric read DAG; affected-rule computation on changeset | `ConstructGraph` diff | rule re-eval set |
| `engine.codon` | Constraint-aware codon optimisation; lexicographic-priority fixed-point | `CodingSequenceDesign`, `CodonAlgorithm` port | optimised CDS + diagnostic report |
| `engine.primer` | Per-strategy primer design; off-target scan; Primer3 adapter | `PrimerDesignParameters` | primer set with Tm, off-target hits |
| `engine.assembly` | Strategy hierarchy emitting typed `AssemblyPlan` subclasses | `ConstructGraph`, chemistry choice | `AssemblyPlan` |
| `engine.overhang` | Golden Gate / Type IIS overhang optimiser (Pryor 2020 / Potapov 2018) | fragment list | overhang set with fidelity score |
| `engine.compatibility` | Role-keyed host x design compatibility; markers catalogue integration (v0.2) | `HostContext`, `Construct`, `MarkersCataloguePort` | `CompatibilityMatrix` |
| `engine.design_plan` | `DesignRealisationPlan` generator: assembly route, required inputs, QC checkpoints, expected verification artefacts, institutional-approvals list, biosafety classification. Always renderable. | upstream engines | `DesignRealisationPlan` |
| `engine.sop_protocol` | `SopLinkedProtocol` generator; gated to institution-supplied SOP templates; renders only when authorisation gates pass | `DesignRealisationPlan`, `SopTemplateReadPort`, `AuthorisationProfile` | `SopLinkedProtocol` |
| `engine.controls` | First-class control designs (positive / negative / process / library-specific) | `ConstructGraph`, host, chemistry | `ControlSet` |
| `engine.risk_classification` | Scans `ConstructGraph` against `risk_advisories.yaml`; emits `RiskAdvisoryReport` | `ConstructGraph`, `RiskAdvisoryCatalogue` | `RiskAdvisoryReport` |
| `engine.vlp_policy` | MS2 / VLP / phage-derived design policy | `ConstructGraph`, VLP rule set | `VlpPolicyReport` |
| `engine.session` | Design-session state machine; event sourcing; typed events; snapshot management | user actions | `DomainEvent` stream |

## C.2 Gates

| Gate | Trigger | Action |
|---|---|---|
| `screening_gate` | After validation, before authorisation | Run configured screening adapter(s); record verdict |
| `vendor_feasibility_gate` | Before export | Confirm vendor can synthesise (SR-* checks) |
| `operational_protocol_gate` | Before SopLinkedProtocol render | Confirm authorisation + screening + advisory acks |
| `export_gate` | Before bundle generation | Confirm all upstream gates passed |

## C.3 Application services (`src/app/`)

| Service | Purpose |
|---|---|
| `app.design_service` | Top-level use cases (new design, edit, validate, export) |
| `app.decision_tree` | UI flow driver for the Wizard |
| `app.constraint_translator` | LLM free-text -> structured constraints; user confirmation |
| `app.validation_orchestrator` | Determines required metrics; calls biology adapters; builds `ValidationContext`; invokes pure validator; caches metrics |
| `app.assembly_orchestrator` | Iterative codon x validator x assembly loop with lexicographic-priority fixed-point convergence |
| `app.primer_orchestrator` | Wraps `engine.primer` with off-target scanning |
| `app.protocol_orchestrator` | Dispatches to `engine.design_plan` (always) and `engine.sop_protocol` (gated) |
| `app.controls_orchestrator` | Wraps `engine.controls` |
| `app.export_orchestrator` | Builds the export bundle |
| `app.screening_orchestrator` | Runs the screening adapter(s); resolves multi-adapter verdicts |
| `app.library_realisation_service` | Lazy expansion of combinatorial libraries |
| `app.part_library_service` | Writes via events; reads from `PartCatalogue` port |

## C.4 51 ports

The Toolkit declares 51 ports under `domain.ports/` (REQUIREMENTS.md § 11; ARCHITECTURE.md § 4.2 / B7). The port manifest is at `docs/port_manifest.yaml`. Major categories:

- Sequence I/O: `SequenceReader`, `SequenceWriter`, `GenBankIO`, `Sbol3IO`, `FastaIO`, `SnapGeneReadPort`, `EmblIO`, `Gff3IO`.
- Biology adapters: `RnaFolder`, `SplicePredictor`, `SignalPeptidePredictor`, `CodonAlgorithm`, `KozakScorer`, `TIRPredictor`, `RbsCalcPort`.
- Catalogues: `PartCatalogue`, `HostCataloguePort`, `MarkersCataloguePort`, `EnzymeCataloguePort`, `RuleRegistryPort`, `VendorProfilePort`, `RiskAdvisoryCataloguePort`, `ScreeningProviderTrustPolicyPort`.
- Screening: `ScreeningAdapter`, `IgscPort`, `IbbisPort`, `SecureDnaPort`, `InternalBlacklistPort`.
- Vendor: `SynthesisVendorAdapter`, `TwistPort`, `IdtPort`, `GenScriptPort`.
- SnapGene: `SnapGeneChannel`, `SnapGeneFileWatchPort`, `SnapGeneApiPort`.
- LLM: `LLMConstraintTranslator`, `OpenAiPort`, `AnthropicPort`, `LocalLlmPort`.
- SOP: `SopTemplateReadPort`, `SopTemplateWriteAdminPort`.
- Authorisation: `AuthorisationReadPort`, `AuthorisationAdminWritePort`, `AuthorisationBootstrapPort`.
- Persistence: `ProjectStore`, `EventLogPort`, `AuditLogPort`, `DerivationEnvironmentPort`.
- External tools: `Primer3Port`, `RebasePort`.
- Plugin: `PluginManifestPort`, `PluginRegistryPort`.

A `port-manifest-sync-check` CI gate ensures the manifest stays in sync with the source.

---

# Appendix D - Essential input and process checklist

Print and tape to the wall. Use before declaring a design "ready for synthesis".

## D.1 Pre-design checklist

- [ ] Have you read Part 1 (Orientation)?
- [ ] Have you identified the correct subsection of Part 2 (E. coli protein, yeast, Pichia, mammalian, etc.) for your wet-lab goal?
- [ ] Do you have the cargo sequence? (FASTA / GenBank / paste / vendor catalogue ID)
- [ ] Do you know the target host strain? (BL21(DE3), BY4741, X-33, HEK293, etc.)
- [ ] Do you know the expression cassette elements you want? (promoter, RBS / Kozak, tag, terminator)
- [ ] Do you know the cloning chemistry you will use? (Gibson, Golden Gate, restriction, Gateway, etc.)
- [ ] Have you declared the biosafety tier?
- [ ] Have you confirmed the cargo is not on your institutional restricted list?

## D.2 Wizard checklist

- [ ] Step 1 - Objective set
- [ ] Step 2 - Host strain set (or "Other" with free-text)
- [ ] Step 3 - Cargo imported / pasted; type set
- [ ] Step 4 - Promoter / induction set; strength target set
- [ ] Step 5 - Tags set (or explicitly "none")
- [ ] Step 6 - Cloning chemistry set; parameters set
- [ ] Step 7 - Biosafety tier set
- [ ] Free-text fields filled where dropdowns are insufficient
- [ ] Wizard summary reviewed
- [ ] "Build construct" clicked

## D.3 Pre-export checklist

- [ ] Validation Report read in full
- [ ] All HARD findings resolved (return to Wizard if necessary)
- [ ] All `caution` and `strong_caution` findings acknowledged with signed DecisionRecords
- [ ] BR-16: manual SnapGene cross-check completed and recorded
- [ ] Screening verdict reviewed; HITs escalated; WATCHLISTs signed-off
- [ ] Authorisation gate passed (your AuthorisationProfile covers this construct)
- [ ] Vendor adapter ran successfully; vendor submission file reviewed
- [ ] Bundle generated; manifest reviewed
- [ ] DerivationEnvironment hash recorded

## D.4 Pre-bench checklist

- [ ] Bundle archived (institutional repository, lab notebook, project folder)
- [ ] Synthesis order placed (Twist / IDT / GenScript) or PCR plan ready
- [ ] Reagents on hand or ordered (assembly mix, competent cells, plates, antibiotics)
- [ ] Bench notebook entry started (date, design ID, bundle hash)
- [ ] IBC notification / approval in place if required

---

# Appendix E - FAQ (50+ questions)

This FAQ covers the most common questions from first-time users.

**E.1 Getting started**

- **Q1**: How long does the first design take? A: Plan 2-4 hours for your first design, including reading the relevant Wizard subsection of Part 2 and Part 3.
- **Q2**: Do I need to know SBOL? A: No. The Toolkit handles SBOL internally; you only see GenBank.
- **Q3**: Do I need to know hexagonal architecture? A: No. Appendix F explains it for the curious; you do not need it to use the Toolkit.
- **Q4**: Can I use the Toolkit without the UI? A: Yes; CLI and HTTP API expose the same functionality.
- **Q5**: Is the Toolkit free? A: GPL-3.0; free for academic and commercial use, with copyleft obligations on derivatives. See Appendix M.
- **Q6**: Can I run the Toolkit offline? A: Yes, after install; the catalogues are local, the screening adapters can be configured to local-only mode.

**E.2 Decision Wizard**

- **Q7**: What if my host strain is not in the catalogue? A: Use "Other" and supply the strain genotype as free-text; the engine downgrades some checks but proceeds.
- **Q8**: What if my cargo has a custom promoter not in the catalogue? A: Same as Q7; supply free-text; the engine annotates as `non_catalogued_promoter` and cannot run promoter-strength predictions.
- **Q9**: Can I have two tags on the same protein? A: Yes; N- and C-terminal can each have a tag; the engine flags potential interference.
- **Q10**: What's the difference between BL21(DE3) and Rosetta(DE3)? A: Rosetta(DE3) carries an additional pRARE plasmid with rare-codon tRNAs; use it when your cargo has rare-codon clusters.
- **Q11**: Why does the Wizard block BSL-4? A: M7 in the architecture; BSL-4 is hard-blocked at compile time. The Toolkit is not appropriate for BSL-4 work.

**E.3 Validation Report**

- **Q12**: What's the difference between SOFT-caution and SOFT-strong_caution? A: Both require acknowledgement; strong_caution requires more detailed justification.
- **Q13**: What if I disagree with an advisory? A: Use Decline (route to alternative reviewer) or Escalate (institutional sign-off). There is no Dismiss.
- **Q14**: Can I disable a rule? A: Administrators can disable rules in the rule registry; this is logged. Users cannot.
- **Q15**: What rules are in MR? A: Molecular: promoter-host, Kozak, RBS, ori-host, marker-strain, rare-codon, restriction-uniqueness, intron-splice.
- **Q16**: How many rules total? A: ~ 60 in v0.2.1 across MR/WR/SR/BR/MS, with new rules added per Knowledge-Base updates.

**E.4 Catalogues**

- **Q17**: How do I update a catalogue? A: Edit the YAML, bump the `retrieved_at` timestamp, commit. The `stale-catalogue-check` gate enforces freshness.
- **Q18**: Can I add a host strain? A: Yes; add to `hosts.yaml` per the schema in `schemas/hosts.schema.json`.
- **Q19**: Can I add a custom marker? A: Yes; add to `markers.yaml` per `schemas/markers.schema.json`.
- **Q20**: Where do the working concentrations come from? A: Sambrook 4th ed. Appendix A1 by default, with primary-literature citations where they diverge. See the citation block in each marker entry.

**E.5 Cloning chemistry**

- **Q21**: When should I use Gibson vs Golden Gate? A: Gibson for 2-5 fragments; Golden Gate for 5-15 with standardised overhangs and a designed kit.
- **Q22**: When should I use restriction + ligation? A: When you have a parental plasmid and a single fragment to swap.
- **Q23**: How long should Gibson homology arms be? A: 25 bp default; 20 minimum; 40-60 for problematic junctions.
- **Q24**: What's the Pryor overhang dataset? A: Pryor 2018 (PMID 30153100), a published ligation-fidelity dataset for Golden Gate overhang selection; integrated in `engine.overhang`.

**E.6 Synthesis**

- **Q25**: Which vendor is cheapest? A: For typical 1-2 kb cargo, Twist is usually cheapest; for short fragments, IDT gBlocks; for whole-plasmid synthesis, GenScript.
- **Q26**: What's the maximum gBlock size? A: ~ 3 kb as of 2026; check IDT's website for current limits.
- **Q27**: How long does synthesis take? A: 3-7 business days for gBlocks; 5-10 for Twist clonal; 10-20 for GenScript clonal.
- **Q28**: What happens if a vendor flags my sequence? A: WATCHLIST -> respond to vendor questions; HIT -> escalate to IBC; UNAVAILABLE -> try another vendor or redesign.

**E.7 Transformation and expression**

- **Q29**: Why are my transformations giving few colonies? A: See Appendix J row "No colonies" — common causes: bad DNA, bad cells, wrong selection.
- **Q30**: Why is my protein in inclusion bodies? A: Lower induction temperature (18 deg C), use a solubility tag (MBP / SUMO / TRX), use SHuffle / Origami if disulfide-related.
- **Q31**: Why is my mammalian expression low? A: Check Kozak (E12 in App. J), check codon usage, check promoter silencing in that line.
- **Q32**: How long should I express? A: Bacterial: 4 h at 37 deg C or 16-20 h at 18 deg C. Mammalian transient: 48-72 h. Pichia: 72-96 h.

**E.8 QC**

- **Q33**: When should I Sanger-sequence? A: Always, after first verification by diagnostic digest, before sending the plasmid to bench colleagues or vendors.
- **Q34**: Can I skip the diagnostic digest? A: Not recommended; the digest catches gross misassemblies before you commit to a Sanger order.
- **Q35**: Why do I need to do BR-16 every time? A: Because automated parsers occasionally misinterpret unusual GenBank dialects; a 30-second human cross-check eliminates the most common silent-corruption failure modes.

**E.9 Audit and reproducibility**

- **Q36**: How long are audit logs kept? A: Permanently in the project repository; the Toolkit never auto-deletes.
- **Q37**: Can someone reproduce my design from the bundle? A: Yes; the DerivationEnvironment hash and the event log together allow byte-identical reconstruction.
- **Q38**: Can I edit a past DecisionRecord? A: No; the log is append-only. Add a new record correcting the earlier one.

**E.10 Collaboration**

- **Q39**: How do I share a design with a collaborator? A: Send the export bundle ZIP. They open the GenBank in SnapGene / Benchling / ApE.
- **Q40**: Can my collaborator run validation on my design? A: Yes; they install the Toolkit, import the bundle, and run validation against their own catalogues.
- **Q41**: How do I send a design to the IBC? A: The bundle has everything the IBC needs; attach to your institution's IBC form.

**E.11 IP and licensing**

- **Q42**: Can I commercialise something built on the Toolkit? A: Yes, with GPL-3.0 obligations on derivative software. See Appendix M.
- **Q43**: Can I publish a paper using a Toolkit design? A: Yes; cite the Toolkit version and include the DerivationEnvironment hash in the supplementary methods.
- **Q44**: Can the Toolkit do patent / FTO analysis? A: No; that belongs to the `/ip-auditor` skill.

**E.12 Troubleshooting**

- **Q45**: The UI won't start. A: Verify Node 20+ and `npm install` succeeded; check port 5173 not in use.
- **Q46**: The Python tests fail with import errors. A: Verify `$env:PYTHONPATH='src;.'` and `uv sync` succeeded.
- **Q47**: I get a cp1252 UnicodeEncodeError. A: You probably printed an absolute Path to stdout on Windows; format with `str(path)` and explicit UTF-8.
- **Q48**: My BR-16 confirmation isn't sticking. A: Confirm your signing key path is set (`$env:CEVD_SIGNING_KEY`) and the key file exists.

**E.13 Misc**

- **Q49**: Can the Toolkit design primers from scratch? A: Yes; `engine.primer` integrates Primer3.
- **Q50**: Does the Toolkit support Cas12a / Cpf1? A: Yes; in CRISPR cargo type, select Cpf1 PAM.
- **Q51**: Does the Toolkit support base editors? A: Partial; ABE / CBE are supported via free-text cargo + the appropriate validation rules.
- **Q52**: Can I run the Toolkit on a Mac? A: Yes; macOS 14+ supported; same install procedure with bash instead of PowerShell.

---

# Appendix F - Architecture and working principles

This appendix is for the curious user, the software developer extending the Toolkit, and the institutional reviewer who wants to understand why the Toolkit's outputs are trustworthy. The full architecture document is `ARCHITECTURE.md` v1.5 (the binding document for the system); this appendix is a guided tour.

## F.1 Hexagonal layering (top-level pattern)

The Toolkit is a **modular monolith** with **hexagonal (ports and adapters)** layering. Four layers, dependencies pointing strictly downward:

```
INTERFACE LAYER  -- CLI, HTTP/gRPC API, React UI
        |
        v
APPLICATION LAYER  -- design service, orchestrators, constraint translator
        |
        v
DOMAIN CORE  (pure)  -- sequence primitives, construct graph, types, engines, ports
        |
        v
INFRASTRUCTURE / ADAPTERS  -- IO, biology, catalogues, vendors, screening, SnapGene, LLM, persistence
```

The **domain core is pure**: the validation engine, the codon optimiser, the primer designer, the assembly planner, and the controls generator have no knowledge of file formats, external APIs, or persistence. They consume typed inputs (`ConstructGraph`, `ValidationContext`, `CodingSequenceDesign`, `PrimerDesignParameters`) and produce typed outputs (`ValidationReport`, optimised CDS, primer set, `AssemblyPlan`, `ControlSet`).

External interactions flow through **ports** (interfaces declared under `domain.ports/`) implemented by **adapters** (concrete classes in `src/adapters/`). The `import-linter` CI gate enforces that the engine layer never names `adapter.*` (B7 in the architecture).

## F.2 The 10-step working cadence

The project operates on a documented 10-step cadence (see the user's MEMORY.md feedback file: `[CEV workflow discipline]` — Standing 10-step cadence for Cloning Expression Vector Design):

1. **Initial report** capturing the proposed change (markdown in `docs/handover/`).
2. **Architect analysis** (`/architect` skill).
3. **IP-auditor analysis** (`/ip-auditor` skill).
4. **User acceptance** of the three-skill briefing.
5. **REQUIREMENTS.md** update (Amendment block).
6. **Three-skill joint plan** (architect + scientific-coder + IP-auditor).
7. **ARCHITECTURE.md** update.
8. **CODING_AGENDA.md** update.
9. **TASK_BOARD.md** update.
10. **Implement** the tasks; CI gates; release.

Steps 5-10 are mechanical once steps 1-4 are accepted. The discipline ensures every change is reviewed by all three skills before code lands.

## F.3 51 ports

See Appendix C.4 for the full list. The port-manifest is at `docs/port_manifest.yaml`; the `port-manifest-sync-check` gate keeps it aligned with the source.

The 51-port count is a deliberate architectural statement: every external interaction is a port. There are no "convenience shortcuts" that bypass the port abstraction. The cost is verbosity (more files, more interfaces); the benefit is testability (every adapter can be swapped for a fake in tests) and reproducibility (the `DerivationEnvironment` captures the adapter configurations explicitly).

## F.4 CI gates

The Toolkit's CI runs a set of project-specific gates that are stricter than typical Python projects. The gate list as of v0.2.1:

- `ruff format --check`
- `ruff check`
- `mypy --strict`
- `pytest -m "not slow"` (unit + integration; ~ 95% line coverage; 100% rule-validation coverage gate)
- `pytest -m "slow"` (release-time)
- `import-linter` (B7 architecture purity)
- `no-self-authorisation-check` (UR-09 / C1 sponsor sharpening)
- `no-passive-advisory-bypass-check` (UR-11 / v1.5 sponsor strengthening)
- `audit-traceability-check` (M13)
- `stale-catalogue-check` (M10)
- `sop-after-gates-check` (B2 reordering)
- `llm-output-policy-check` (M10)
- `plugin-manifest-signature` (R-18 mitigation)
- `port-manifest-sync-check`
- `release-fixtures-deterministic` (release gate)
- `derivation-environment-hash-stable` (release gate)

The complete pre-release CI cycle is documented in `CODING_AGENDA.md` and `docs/release/`.

## F.5 Corpus subsystem (v0.2 Enrichment Amendment)

The v0.2 Enrichment Amendment added a curated **ML training corpus** under `docs/ml_corpus/` (sibling folder, intentionally not under `catalogues/`; isolated by an `import-linter` contract). Each record carries:

- Sequence licence block.
- Annotation licence block (separate from sequence).
- Source provenance (URL or repository identifier).
- Retrieval timestamp.
- SHA-256 checksum.
- A SnapGene manual cross-check record.

The corpus is split into partitions:

- `partition: full` — all 148 records.
- `partition: sa_free` — records without share-alike licensing constraints (suitable for closed-source commercial training).

CC-BY-SA-licensed records are routed to `docs/ml_corpus/records/cc-by-sa/`. SnapGene-derived records are **index-only with manual cross-check by a human in a browser** (BR-15..17); no automated extraction or redistribution.

This subsystem provides a future ML pipeline with audit-grade training data without compromising any party's licensing terms.

## F.6 Fork-Readiness

The Fork-Readiness Memo (`docs/fork-readiness/`) is a periodically-updated assessment of whether the codebase is suitable for forking into a closed-source commercial line. It covers:

- Licensing posture (GPL-3.0 implications on derivative software).
- Catalogue licensing (per-record CC-BY / CC-BY-SA / proprietary status).
- Contributor agreement state.
- Third-party dependencies and their licences (`THIRD_PARTY_LICENSES.md`).
- Trademark posture (GMExpression(R) is registered).

For any commercialisation conversation, the Fork-Readiness Memo plus the latest IP-audit memo are the canonical starting points.

---

# Appendix G - Fundamental molecular genetics, biochemistry, cell biology, and physics principles

This appendix recapitulates the fundamental science you must understand to make good use of the Toolkit's outputs. Each subsection states the principle, gives the mathematical or chemical formulation where one exists, and cites the canonical reference.

## G.1 The central dogma of molecular biology

DNA -> RNA -> protein (Crick 1958, 1970; transcription by RNA polymerase, translation by ribosome; reverse transcription possible in retroviruses). The Toolkit's cassette anatomy is a direct expression of the central dogma: a promoter recruits RNA polymerase to transcribe the gene to mRNA; for protein cargo, the mRNA's 5' UTR + RBS / Kozak recruits the ribosome; the ribosome translates the CDS into protein; the C-terminus emits when the ribosome encounters a stop codon; the 3' UTR + polyA signal terminates transcription and stabilises the message.

## G.2 DNA double-helix and Watson-Crick base pairing

dsDNA is two antiparallel strands wound in a right-handed helix; adenine pairs with thymine (A-T, two hydrogen bonds), guanine pairs with cytosine (G-C, three hydrogen bonds; Watson & Crick 1953). Cloning chemistries exploit this: Gibson exonuclease creates 3' overhangs that anneal across a homology arm; PCR primers anneal to a complementary template; Sanger sequencing reads the template via primer extension.

## G.3 Transcription

RNA polymerase recognises a promoter (the -10 and -35 hexamers in bacteria; the TATA box and Inr in eukaryotes), opens the DNA, synthesises an RNA copy of the template strand 5' -> 3'. Termination is rho-dependent or rho-independent (stem-loop + polyU) in bacteria; polyadenylation cleavage in eukaryotes. T7 RNA polymerase (bacteriophage T7, ~99 kDa, single-subunit) recognises a 17 bp consensus (TAATACGACTCACTATA) and transcribes processively at ~ 200-300 nt/s.

## G.4 Translation

Ribosome scans the mRNA 5' -> 3'; in bacteria, the Shine-Dalgarno sequence base-pairs with 16S rRNA to position the start codon; in eukaryotes, the cap-dependent scanning model (Kozak 1989 PMID 2657394) requires the 5' cap, scanning, and a strong context (gccRccATGG) for efficient initiation. Translation proceeds at ~ 20 amino acids per second; the ribosome dissociates at the stop codon.

## G.5 Codon usage and CAI

The genetic code is degenerate: most amino acids are encoded by 2-6 synonymous codons. Different organisms use synonymous codons at different frequencies, reflecting their tRNA pool. The **Codon Adaptation Index** (CAI; Sharp & Li 1987 PMID 3447015) measures how well a CDS uses the codons preferred by a target organism:

CAI = (Product over codons of w_i)^(1/L)

where w_i is the relative frequency of codon i in the target's "highly-expressed gene set" normalised to 1.0 for the most-used synonym, and L is the CDS length.

The Toolkit's codon optimiser targets CAI >= 0.7 by default; this is a heuristic balance between yield and avoiding excessive codon-uniformity artefacts.

## G.6 Restriction enzymes and the chemistry of cutting

Type II restriction enzymes recognise palindromic sequences (e.g., BamHI: GGATCC; EcoRI: GAATTC; HindIII: AAGCTT) and cut at a defined position. The mechanism involves catalytic Mg2+ (or Mn2+) and a hydrolytic cleavage of the phosphodiester backbone. Cut products carry either blunt ends, 5' overhangs, or 3' overhangs.

Type IIS enzymes (BsaI, BsmBI, SapI) recognise an asymmetric site and cut at a defined distance outside it; this asymmetry is exploited in Golden Gate to generate user-defined 4-nt overhangs.

REBASE (Roberts 2015 PMID 25378308) is the canonical restriction-enzyme database; the Toolkit's `EnzymeCataloguePort` reads from REBASE-derived records.

## G.7 Ligation chemistry

T4 DNA ligase joins two DNA ends by reforming the phosphodiester bond between a 3'-OH and a 5'-phosphate, consuming one ATP per bond. Sticky-end ligation is energetically favoured over blunt-end (~ 100-fold). Ligation efficiency depends on:

- End compatibility (matching overhangs).
- Concentration (typical 50-100 nM fragment ends; lower for blunt to disfavour intermolecular concatemers).
- Temperature (16 deg C overnight is the standard balance between enzyme activity and annealing).
- Buffer pH and Mg2+ (T4 buffer is 10 mM Mg2+, pH 7.6).

## G.8 PCR

Polymerase Chain Reaction (Mullis 1986): cyclic denaturation (95 deg C), primer annealing (typically 50-65 deg C), and primer extension by a thermostable polymerase (Taq, Pfu, Phusion, KOD; ~ 72 deg C). Each cycle doubles the template; 25-30 cycles amplify ~ 10^6-10^8-fold. Primer Tm is the dominant design parameter; the Toolkit calculates Tm using the SantaLucia 1998 nearest-neighbour parameters (PMID 9501958).

## G.9 Primer Tm calculation (SantaLucia 1998)

For a primer of length L:

Tm = (Sum of nearest-neighbour delta-H) / (Sum of nearest-neighbour delta-S + R ln(C / 4)) - 273.15

where delta-H and delta-S are tabulated for each nearest-neighbour dinucleotide, R is the gas constant, and C is the primer concentration in M.

Corrections for monovalent salt (Na+) and divalent (Mg2+) follow Owczarzy 2004 PMID 15154762.

In practice the Toolkit's primer designer aims for primer Tm within +/- 2 deg C of the partner; > 5 deg C divergence triggers a SOFT `WR-PRIMER-TM-DIVERGENCE` advisory.

## G.10 Gibson assembly chemistry

Gibson 2009 (PMID 19363495): T5 exonuclease chews back 5' ends to generate 3' overhangs; complementary overhangs anneal across the user-designed homology arm; Phusion polymerase fills the gap; Taq DNA ligase seals the nick. All three enzymes work at 50 deg C; the reaction goes to completion in 15-60 min.

NEBuilder HiFi is NEB's commercial implementation with higher-fidelity enzymes and a buffer optimised for inserts at the 15-40 bp homology range.

## G.11 Golden Gate fidelity (Pryor 2018)

Pryor 2018 PMID 30153100 published a comprehensive ligation-fidelity dataset for all 256 possible 4-nt overhangs at 25 / 37 deg C. The Toolkit's `engine.overhang` optimiser uses this dataset to select overhang sets that maximise correct ligations per assembly. The empirical fidelity ranges from > 99% (well-chosen orthogonal sets) to ~ 50% (clashing or repeated overhangs); the Toolkit targets fidelity >= 90% by default.

## G.12 Plasmid copy number and incompatibility

The origin of replication determines copy number:

- pUC ori (ColE1-derived, with the rop / rom mutation): 500-700 copies per cell.
- pBR322 ori (ColE1): 15-25 copies.
- p15A ori (pACYC): 10-12 copies.
- pSC101 ori: ~ 5 copies.
- Mini-F: 1-2 copies.

Incompatibility groups (Inc) are defined by the regulation of replication initiation; plasmids of the same Inc cannot coexist stably. ColE1 (Inc) plasmids cannot be co-maintained without selection on both; p15A + ColE1 (different Inc) coexist stably with dual selection.

## G.13 Selection markers (mechanism)

- **bla / Amp**: Class A beta-lactamase TEM-1; hydrolyses the beta-lactam ring of penicillins.
- **neo / Kan / Neo / G418**: Aminoglycoside 3'-phosphotransferase; ATP-dependent O-phosphorylation of kanamycin / neomycin / G418 3'-OH.
- **cat / Cm**: Chloramphenicol acetyl-transferase; acetyl-CoA-dependent acetylation of chloramphenicol.
- **tetA / Tet**: Membrane efflux pump; tetR-regulated active export.
- **aadA / Spec / Strep**: Aminoglycoside 3''-adenylyltransferase.
- **ble / Zeo**: Sh ble protein binds and sequesters bleomycin / phleomycin / zeocin.
- **aac(3)-IV / Gen**: Aminoglycoside 3-N-acetyltransferase.
- **hph / Hyg**: Hygromycin B phosphotransferase; ATP-dependent phosphorylation at 4-OH.
- **puro**: Puromycin N-acetyl-transferase; acetylates puromycin to inactive form.
- **bsd**: Blasticidin-S deaminase; deaminates blasticidin to inactive form.

Concentrations and host-specific notes are in `markers.yaml` (see Appendix Part 2.8); the canonical reference is Sambrook 4th ed. Appendix A1 with primary-literature support per entry.

## G.14 Promoter strength and induction

- **T7 promoter**: very strong; consensus TAATACGACTCACTATA; recognised by T7 RNAP; strict host requirement (DE3 lysogen carries T7 RNAP under lacUV5).
- **araBAD**: tight when uninduced (no glucose); fully active with L-arabinose; activated by AraC.
- **CMV**: strong constitutive in mammalian; can silence in some lines (e.g., long-term in CHO).
- **EF1alpha**: strong constitutive in mammalian; less silencing than CMV in some contexts.
- **CAG**: strongest constitutive in many cell lines; CMV early enhancer + chicken beta-actin promoter + rabbit beta-globin intron.
- **GAL1 / GAL10**: tight in glucose-grown S. cerevisiae; strongly induced by galactose.
- **AOX1 (Pichia)**: tight in glycerol-grown Pichia; strongly induced by methanol.

## G.15 Signal peptides and protein secretion

Secreted proteins carry an N-terminal signal peptide (~ 15-30 aa) that targets the protein to the Sec or SRP pathway for translocation across the membrane. The signal peptide is cleaved by signal peptidase I (bacterial inner membrane) or by Kex2 (yeast / Pichia secretion via the trans-Golgi). SignalP (Almagro Armenteros 2019 PMID 30778257) is the canonical signal-peptide prediction tool; the Toolkit's `SignalPeptidePredictor` port wraps it.

## G.16 N-glycosylation

Eukaryotic N-glycosylation occurs at NXS/T motifs (X != P); covalent attachment of a pre-assembled glycan to the asparagine in the ER, then trimming and elaboration in the Golgi. Different hosts produce different glycoforms: mammalian (complex, sialylated), CHO (close to human, GalT-driven), Pichia (hyper-mannosylated), insect (paucimannose), bacteria (none, glycoengineered exceptions). For glycosylation-sensitive applications (therapeutic antibodies, viral antigens), host choice matters at the design step.

## G.17 Beer-Lambert law (spectrophotometry)

A = epsilon * c * L

where A is absorbance (unitless), epsilon is the molar extinction coefficient (M^-1 cm^-1), c is concentration (M), and L is the path length (cm). For dsDNA at 260 nm, epsilon is ~ 6.7 x 10^3 M^-1 cm^-1 per bp; A_260 = 1.0 corresponds to ~ 50 ug/mL dsDNA. For ssDNA / RNA, A_260 = 1.0 is ~ 33 ug/mL / 40 ug/mL respectively. For protein, the Edelhoch / Pace formula uses tryptophan + tyrosine + cystine extinctions to compute epsilon at 280 nm.

## G.18 Centrifugation, electrophoresis, and biophysics

- **Centrifugation**: separates particles by sedimentation rate; expressed in xg (relative centrifugal force). For mini-prep: 13000-16000 xg for 1 min pellets bacterial cells; for ultracentrifugation of viral particles, 100000 xg for 90 min.
- **Agarose gel electrophoresis**: DNA migrates through agarose mesh under electric field; rate inversely related to log(size); 1% agarose resolves 0.5-10 kb; 2-3% agarose for < 500 bp.
- **SDS-PAGE**: SDS denatures and uniformly charges proteins; migration in polyacrylamide reflects size; 12% gel resolves ~ 10-100 kDa; 15% for smaller proteins; 7.5% for larger.

---

# Appendix H - Basic formulas and theorems

This appendix gathers the equations the Toolkit's engines use internally, plus the back-of-the-envelope calculations you will do at the bench. Every formula carries a canonical reference.

## H.1 Beer-Lambert law

```
A = epsilon * c * L
```

Used in: A_260 measurement of DNA concentration; A_280 of protein; spectrophotometric quantitation of enzymatic activity.

dsDNA: A_260 = 1.0 corresponds to ~ 50 ug/mL. ssDNA: ~ 33 ug/mL. RNA: ~ 40 ug/mL. Protein (assuming average epsilon = 1.0): A_280 = 1.0 ~ 1 mg/mL.

## H.2 Nearest-neighbour Tm (SantaLucia 1998)

```
Tm = (Sum_NN delta-H) / (Sum_NN delta-S + R ln(C / 4)) - 273.15
```

where:
- delta-H = enthalpy contribution from each nearest-neighbour dinucleotide, kJ/mol (SantaLucia 1998 PMID 9501958 Table 1).
- delta-S = entropy contribution, J/(K mol).
- R = 8.314 J/(K mol).
- C = primer concentration, M (typically 2 x 10^-7 M for primers in PCR).

Salt correction (Owczarzy 2004 PMID 15154762):

```
Tm_corrected = Tm + (4.29 * f_GC - 3.95) * log10([Na+]) + 0.940 * (log10([Na+]))^2
```

with the divalent correction for Mg2+ as published.

## H.3 GC content

```
f_GC = (count_G + count_C) / length
```

A useful heuristic Tm estimate for short oligos < 50 nt:

```
Tm_estimate ~ 64.9 + 41 * (count_G + count_C - 16.4) / length    (deg C)
```

(Marmur-Doty / Wallace, approximation only).

## H.4 dsDNA mass / molarity conversion

Average mass per bp = 650 g/mol (for dsDNA).

```
moles = mass_g / (length_bp * 650)
M (molarity) = moles / volume_L
ng -> pmol: pmol = ng * 1000 / (length_bp * 650 / 1000) = ng * 1.515 / length_kbp
pmol -> ng: ng = pmol * length_bp * 650 / 1000
```

Example: 100 ng of a 5 kbp plasmid = 100 * 1.515 / 5 = ~ 30.3 fmol.

## H.5 Ligation stoichiometry

For inserting one fragment into one backbone:

```
moles_insert / moles_backbone = (typically 3:1 to 5:1 for sticky-end; 5:1 to 10:1 for blunt-end)
```

For Gibson with 25 bp homology arms, 1:2 backbone:insert is standard. For Golden Gate with 5+ fragments, equimolar (50-100 ng each).

## H.6 Copy-number-derived plasmid yield estimate

For a high-copy pUC-ori plasmid in *E. coli*:

```
copies_per_cell ~ 500
plasmid_yield_per_OD_per_mL ~ 1 ug (rule of thumb)
```

For low-copy (pSC101, mini-F), expect 10-50x lower yield.

## H.7 CAI (Sharp & Li 1987)

```
CAI = (Product_i=1..L of w_i)^(1/L)
```

where w_i is the relative codon adaptedness of codon i: the frequency of codon i in highly-expressed genes divided by the frequency of the most-used synonym for the same amino acid.

CAI = 1.0 means every codon is the most-used synonym; CAI = 0.0 (limit) means every codon is unused. The Toolkit's default target is CAI >= 0.7 for the chosen host.

## H.8 Pryor fidelity (Golden Gate overhang)

The Toolkit's `engine.overhang` optimiser maximises overhang fidelity defined empirically by Pryor 2018 PMID 30153100:

```
F_set = correct_ligations / total_ligations
```

estimated by combinatorial ligation experiments at 25 deg C and 37 deg C; the dataset is integrated as the canonical lookup table.

## H.9 Lentivirus titre estimate

For functional titre by limiting dilution / GFP+ FACS:

```
TU/mL = (fraction_positive * cells_seeded) / volume_added
```

For physical titre by p24 ELISA:

```
TU/mL ~ p24_pg/mL * 10^4 (approximation; varies by prep)
```

## H.10 PCR Tm primer design (rule of thumb)

For 18-22 nt primers, the Wallace rule:

```
Tm ~ 4*(G+C) + 2*(A+T)    (deg C)
```

is a fast estimate. The Toolkit uses SantaLucia 1998 (PMID 9501958) for the canonical value.

## H.11 SHA-256 (reproducibility)

The Toolkit's `DerivationEnvironment` hash is SHA-256 over the canonicalised JSON serialisation of all relevant inputs. Properties:

- 256-bit output.
- Collision-resistant under current cryptographic assumptions.
- Deterministic given canonical input.

The hash is the canonical reproducibility identifier for an export bundle; verify it as `sha256sum derivation_environment.json` (or PowerShell `Get-FileHash`).

---

# Appendix I - Standard wet-lab protocols

This appendix collects the ~ 15 standard protocols referenced throughout Part 4 and 5. Each is condensed; consult Sambrook 4th ed. or the canonical primary citation for the full protocol.

## I.1 Plasmid mini-prep (alkaline lysis)

**Time**: 30 min plus overnight culture.

1. Inoculate 5 mL LB + antibiotic with a single colony; grow overnight at 37 deg C, 220 rpm.
2. Pellet 3-5 mL: 13000 xg, 1 min; discard supernatant.
3. Resuspend in 250 uL P1 (50 mM Tris-HCl pH 8.0, 10 mM EDTA, 100 ug/mL RNase A).
4. Add 250 uL P2 (200 mM NaOH, 1% SDS); invert 4-6 times; do not vortex.
5. Add 350 uL N3 (3 M potassium acetate pH 5.5); invert immediately; 13000 xg 10 min.
6. Transfer supernatant to a silica spin column; spin 13000 xg 1 min; discard flow-through.
7. Wash with 750 uL PE (70% EtOH-containing wash buffer); spin 13000 xg 1 min; dry spin 1 min.
8. Elute in 30-50 uL EB (10 mM Tris-HCl pH 8.5) or water at 13000 xg, 1 min.

Yield typical 5-30 ug for high-copy pUC-based plasmids; 1-5 ug for medium-copy; < 1 ug for low-copy.

## I.2 Restriction digest (diagnostic)

1. Combine: ~ 200 ng plasmid + 1 U enzyme per ug + 1x reaction buffer in 20 uL total.
2. Incubate 37 deg C 60 min (or 50 deg C for SmaI, EcoRV; check NEB chart).
3. Run on 1% agarose gel + appropriate size ladder.

## I.3 Agarose gel electrophoresis

1. Cast 1% agarose in TAE or TBE buffer + intercalator (SYBR Safe / GelRed).
2. Load samples + ladder; run at 80-120 V for 30-60 min.
3. Visualise on UV / blue-light transilluminator.

## I.4 Ligation (T4)

1. Combine backbone : insert at 1:3 to 1:5 molar ratio; ~ 50 ng backbone in 10 uL.
2. Add 1 uL T4 DNA ligase (NEB or Promega; 400 U/uL); 1 uL 10x T4 buffer.
3. Incubate 16 deg C overnight (or room temperature 1 h for sticky-end).
4. Transform 2-5 uL.

## I.5 Gibson assembly (NEBuilder HiFi)

1. Combine fragments at equimolar (~ 0.05 pmol each) in 10 uL.
2. Add 10 uL NEBuilder HiFi 2x Master Mix; total 20 uL.
3. Incubate 50 deg C: 15 min (2 fragments), 30-45 min (3-5 fragments), 60 min (5+ fragments).
4. Transform 2 uL into competent cells.

## I.6 Golden Gate (BsaI / BsmBI)

1. Combine: 50-100 ng of each donor; 50-100 ng of destination vector; 1 uL BsaI-HF v2 (or BsmBI-v2); 1 uL T4 DNA ligase; 2 uL 10x T4 buffer; water to 20 uL.
2. Cycle in thermocycler: 30 cycles of (37 deg C 2 min, 16 deg C 5 min); 60 deg C 10 min; 80 deg C 5 min.
3. Transform 2 uL into competent cells.

## I.7 E. coli transformation (heat-shock)

1. Thaw 50 uL chemically competent cells on ice.
2. Add 1-5 uL of DNA; mix gently; incubate on ice 20-30 min.
3. Heat-shock 42 deg C 30-45 s.
4. Return to ice 2 min.
5. Add 950 uL SOC; recover at 37 deg C, 220 rpm, 1 h.
6. Plate 50-100 uL on LB-agar + antibiotic; overnight at 37 deg C.

## I.8 E. coli electroporation

1. Thaw electrocompetent cells on ice; pre-chill 1-mm cuvettes.
2. Add 1-2 uL salt-free DNA to 40-50 uL cells; transfer to cuvette.
3. Pulse: 1.8 kV (1-mm) or 2.5 kV (2-mm); time constant 4.5-5.5 ms.
4. Immediately add 950 uL pre-warmed SOC; transfer to tube; recover at 37 deg C, 220 rpm, 1 h.
5. Plate.

## I.9 Mammalian transfection (Lipofectamine 3000)

Per well of 6-well, with HEK293 at 70-80% confluence in 2 mL DMEM + 10% FBS:

1. Tube A: 125 uL Opti-MEM + 2.5 ug DNA + 5 uL P3000 reagent; mix.
2. Tube B: 125 uL Opti-MEM + 7.5 uL Lipofectamine 3000; mix.
3. Combine A + B; incubate 5-10 min at room temperature.
4. Add dropwise to cells; gently rock.
5. Replace medium at 4-6 h.
6. Harvest at 24-72 h depending on cargo.

## I.10 S. cerevisiae transformation (LiAc / PEG / heat-shock)

(Gietz & Schiestl 2007 PMID 17401334)

1. Grow 5 mL YPD overnight; subculture to OD600 ~ 0.5 in 50 mL YPD for ~ 4 h.
2. Pellet (3000 xg, 5 min); wash with sterile water; wash with 100 mM LiAc; resuspend in 100 mM LiAc.
3. Aliquot 50 uL per transformation.
4. Add: 240 uL 50% PEG-3350; 36 uL 1 M LiAc; 50 uL 2 mg/mL sheared salmon-sperm carrier DNA (boiled / chilled); 5-10 uL plasmid (~ 100-500 ng).
5. Vortex; 30 deg C 30 min; heat-shock 42 deg C 25 min.
6. Pellet (3000 xg 1 min); resuspend in 100 uL water; plate on selective SD; 30 deg C 2-3 days.

## I.11 Pichia electroporation

1. Linearise 5-10 ug pPICZ-CARGO with SacI or PmeI; clean up.
2. Mix linearised DNA with 80 uL electrocompetent Pichia in pre-chilled 2-mm cuvette.
3. Pulse: 1.5 kV (2-mm).
4. Add 1 mL 1 M sorbitol; recover at 30 deg C, no shaking, 1-2 h.
5. Plate on YPDS + Zeocin (100-1000 ug/mL); 30 deg C 3-5 days.

## I.12 Colony PCR

1. Pick colony with sterile toothpick; resuspend in 20 uL PCR mix (Taq + primers flanking insert).
2. Cycle: 95 deg C 5 min initial (lyses cells); 30 cycles of 95 / 55 / 72 deg C; 72 deg C 5 min.
3. Run 5-10 uL on 1% gel.

## I.13 Sanger prep

1. Combine in 12 uL: 200-500 ng plasmid + 5 pmol primer.
2. Send to sequencing facility (Eurofins, Genewiz / Azenta, in-house core).
3. Receive `.ab1` trace files; analyse in SnapGene, ApE, or Geneious; compare to expected.

## I.14 SDS-PAGE

1. Mix protein sample with 1x Laemmli buffer; boil 95 deg C 5 min.
2. Load 10-30 ug per lane on a 10-15% Tris-glycine gel.
3. Run at 80 V (stacking) then 120-150 V (resolving) until dye front reaches bottom.
4. Stain with Coomassie blue or transfer to PVDF for Western.

## I.15 Western blot

1. Transfer SDS-PAGE gel to PVDF or nitrocellulose: 100 V 1 h or semi-dry 25 V 30 min.
2. Block: 5% non-fat milk in TBST 1 h at room temperature.
3. Primary antibody: 1:1000 to 1:10000 in TBST + 5% milk; 4 deg C overnight (or 1-2 h at room temperature).
4. Wash 3x 5 min in TBST.
5. Secondary HRP-conjugated antibody: 1:5000-1:50000 in TBST + 5% milk; 1 h at room temperature.
6. Wash 3x 5 min in TBST.
7. Develop with ECL substrate; image on chemiluminescence imager.

---

# Appendix J - Troubleshooting table

The detailed bench-failure -> design-time-rule mapping. Use this with the decision tree in Part 5.4.

| # | Symptom | Likely cause | Diagnostic | Fix | Toolkit feature to recheck |
|---|---|---|---|---|---|
| 1 | No transformants after transformation | DNA quality poor | Re-run nanodrop; gel-check DNA | Re-prep DNA from a fresh colony | Validate `construct.gb`; manual SnapGene cross-check (BR-16) |
| 2 | Very few transformants | Cells inefficient | Test cells with control DNA (e.g., pUC19) | Use fresh cells; verify selection plate | n/a |
| 3 | Few transformants with Gibson | Homology arms too short | Re-design with 25-40 bp arms | Re-build construct | `WR-GIBSON-HOMOLOGY-SHORT` |
| 4 | Many small / satellite colonies on Amp plate | Beta-lactamase degraded antibiotic | Switch to carbenicillin | n/a | `markers.yaml` for marker `bla` notes |
| 5 | Colonies on no-DNA control | Plate contamination | Re-pour; re-prep cells | n/a | n/a |
| 6 | Wrong-size band on diagnostic digest | Misassembly | Sanger-sequence to confirm | Re-do assembly | Validation Report (rebuilt) |
| 7 | Sanger trace ends prematurely | Secondary structure stalls polymerase | Re-do with different primer / dye-set | Try opposite-strand primer | `MR-RNA-STRUCTURE` advisory |
| 8 | Mutation in cargo sequence | Synthesis error or PCR error | Re-Sanger to confirm; reorder if synthesis | Confirm via reference | DerivationEnvironment hash (re-verify bundle integrity) |
| 9 | Plasmid loss in culture | Plasmid instability (LTR repeat etc.) | Switch to Stbl3 / Stbl4 strain | n/a | `WR-LENTI-LTR-RECOMB` advisory |
| 10 | Transformation works but no colonies on expression strain | DE3 lysogen needed | Confirm strain is BL21(DE3), not plain BL21 | Re-transform into correct strain | `MR-PROMOTER-HOST` (T7 requires DE3) |
| 11 | Induction with IPTG gives no expression band | Wrong inducer concentration / time | Test 0.1, 0.5, 1 mM IPTG; harvest at 2 / 4 / 6 h | Adjust induction protocol | Validation Report Notes (induction conditions) |
| 12 | Mammalian expression weak | Kozak too weak | Confirm Kozak context (gccRccATGG) | Re-design Kozak | `MR-KOZAK-WEAK` advisory |
| 13 | Mammalian expression silenced over passages | CMV silencing in long-term culture | Switch to EF1alpha or CAG | Re-design promoter | `MR-CMV-SILENCING` (informational note) |
| 14 | Pichia secreted protein undetectable | Signal peptide cleavage fails | Confirm Kex2 / Ste13 site | Re-design signal peptide / linker | `MR-SIGNAL-PEPTIDE-CLEAVAGE` advisory |
| 15 | Yeast colony does not grow on -Ura | URA3 marker not complementing | Confirm strain is ura3- | Re-confirm host strain | `markers.yaml` URA3 entry compatible_hosts |
| 16 | Bacteria insoluble protein | Inclusion bodies | Express at 18 deg C with slow induction | Switch to SHuffle / Origami if disulfide-rich | n/a (bench-level) |
| 17 | Protein degrades during purification | Protease activity | Add protease inhibitors; switch to pep4 strain (yeast) | n/a | n/a |
| 18 | Activity assay shows no enzyme activity | Mis-folded or misfolded fusion | Confirm by Western; re-design tag | n/a | n/a |
| 19 | Antibody fails to bind antigen | Mis-folded V_H / V_L | Re-purify under non-reducing; confirm by SEC | Re-design tag / signal peptide | n/a |
| 20 | Lentivirus titre very low | Producer cell health | Refresh 293T; transfect fresh DNA | Re-transfect | `WR-LENTI-CARGO-OVERSIZE` advisory |
| 21 | Lentivirus packaging fails | Cargo > 8 kb | Confirm cargo size; trim or split | Re-design | `WR-LENTI-CARGO-OVERSIZE` |
| 22 | AAV very low titre | ITR mis-annotation | Confirm ITRs in SnapGene; re-prep | Re-confirm ITR integrity | BR-16 |
| 23 | CRISPR no editing detected | sgRNA does not cut | Confirm guide via T7E1 or amplicon-seq | Re-design guide; check PAM | `MR-CAS-PAM-MISMATCH` |
| 24 | CRISPR off-target editing | Guide not unique | Re-design with off-target tool | Re-build | Off-target scan advisory |
| 25 | HDR knock-in fails | HDR template not delivered or template will be cut | Confirm PAM-disrupting mutations in arms | Re-design template | `MR-HDR-TEMPLATE-PAM` |
| 26 | Mini-prep gives white pellet only | Cell pellet too small | Scale up culture | n/a | n/a |
| 27 | Mini-prep DNA looks like RNA | RNase A missing in P1 | Add RNase A; re-prep | n/a | n/a |
| 28 | Plasmid runs as multiple bands on gel | Topoisomer / nicked / linear | Linearise with a known cutter; verify | n/a | n/a |
| 29 | Plasmid is unstable in long-term storage | Selection antibiotic degraded | Re-streak from glycerol stock | n/a | n/a |
| 30 | Sequencing trace has high background | Primer not specific | Re-design primer further into the insert | Re-design | `engine.primer` off-target scan |
| 31 | Insert "cut out" during *E. coli* growth | Repeat-mediated recombination | Switch to Stbl3 / Stbl4 / NEB Stable | n/a | `WR-REPEAT-RECOMB` advisory |
| 32 | Yeast cells small / slow-growing | Auxotrophic marker incomplete | Verify complementation by media swap | n/a | `markers.yaml` notes |
| 33 | CHO-stable line drifts in 6 weeks | Clonal heterogeneity | Re-clone by limiting dilution | n/a | n/a |
| 34 | Antibody aggregates in storage | Hydrophobic patch exposed | Re-design with different framework | n/a | n/a |
| 35 | Western band higher than expected MW | Glycosylation in eukaryotic host | Confirm by PNGase F deglycosylation | n/a | Mammalian glycosylation advisory |
| 36 | Coomassie band lower than expected MW | Internal start or partial proteolysis | Sanger to confirm full-length CDS | n/a | `MR-INTERNAL-MET-START` |
| 37 | sgRNA insert fails to ligate into pX458 | Oligo ends not phosphorylated | T4 PNK + ATP; re-ligate | n/a | n/a |
| 38 | Vector adapter throws SR-VENDOR-PROHIBITED | Repeat / homopolymer in cargo | Re-design with synonymous codons | Re-design | `SR-VENDOR-PROHIBITED` |
| 39 | Vendor rejects order for cost / length | Over single-fragment limit | Split into 2 fragments + Gibson | Re-design | `SR-LENGTH-OVER-VENDOR` |
| 40 | Toolkit complains about BR-16 missing | SnapGene cross-check not performed | Perform manual cross-check; click confirm | n/a | BR-16 |

---

# Appendix K - Glossary expansion (long form)

This is the long-form glossary. The short-form glossary in the front matter has the brief one-line definitions; this appendix gives the multi-paragraph technical entries for the terms that need them. Terms are alphabetised.

**Addgene**. A non-profit plasmid repository headquartered in Cambridge, Massachusetts, founded in 2004. Addgene distributes plasmids deposited by academic laboratories worldwide, with strict QC and standardised material-transfer terms. Addgene also publishes a series of free educational eBooks (Plasmids 101, CRISPR 101, Fluorescent Proteins 101, Viral Vectors 101, Antibodies 101) that are widely used as introductory texts. The Toolkit's documentation cites Addgene eBooks under **nominative-use** principles only: the Addgene name is acknowledged where it is the canonical reference, but no Addgene-derived text is reproduced verbatim and no Addgene-trained models are embedded. See Appendix M for the IP posture.

**Adapter**. In hexagonal architecture, a concrete implementation of a port. The Toolkit's adapter layer (`src/adapters/`) implements the port interfaces from `domain.ports/`. Example: `GenBankAdapter` implements `SequenceReader` and `SequenceWriter`; `IgscAdapter` implements `ScreeningAdapter`.

**Advisory**. A structured, signed warning emitted by the Toolkit's `engine.risk_classification` module. Each advisory carries a stable ID within its report so the acknowledgement trail can address each individually. Severities are `info`, `caution`, and `strong_caution`. Cautions and strong cautions require an active `acknowledge`, `decline`, or `escalate` action before authorisation can proceed; a "dismiss" affordance is forbidden by architecture (UR-11; FR-ADV-01..07; ARCHITECTURE.md v1.5 sponsor strengthening).

**Audit log**. An append-only event stream of all governance-relevant actions: advisory presentations, advisory acknowledgements / declines / escalations, authorisation grants / modifies / revokes, screening verdicts, reviewer sign-offs, exports, and administrator actions. Bound to cryptographic signatures and content hashes. The audit log is the canonical reproducibility artefact: given the audit log plus the DerivationEnvironment, any past design can be reconstructed exactly.

**Authorisation Profile**. An administrator-controlled object listing the scopes of operation a user may declare. Includes biosafety tiers, vector classes, cargo classes, host roles, replication competence, insert size limits, target organism scope, institutional approval scope, and any institution-specific constraints. The engine validates the user's declared intent against the profile; declarations that exceed the profile are rejected (ARCHITECTURE.md v1.2 sponsor sharpening; UR-09).

**BR-16**. Toolkit-specific biosafety rule requiring a **manual** SnapGene cross-check before any exported design is committed to synthesis. The cross-check is performed by a human in a browser; the result is recorded as a signed `DecisionRecord` bound to the construct's content hash. The Toolkit will not bypass or automate this step; the rationale is that automated parsers occasionally misinterpret unusual GenBank dialects, and a 30-second human cross-check eliminates the most common silent-corruption failure modes.

**Construct graph**. The Toolkit's canonical typed representation of a vector. Nodes are `Part`, `Feature`, or `Module` objects; edges are typed (Adjacency for physical order; Regulatory for promoter -> CDS relationships; Derivation for parent-of-design lineage; Assembly for chemistry-driven joins). The construct graph is the engine layer's primary data structure; it is canonical and the `feature_table` is a derived view.

**DerivationEnvironment**. A typed record capturing every input that materially changes the Toolkit's output: catalogue versions, adapter configurations, external database versions, SOP templates, locale, units, seeds, container image digest, user overrides, reviewer decisions, profile hashes, SOP template content hashes, screening trust policy version, plugin package hashes, LLM prompt template versions, institutional policy version, redaction policy. Hashed into every export bundle. The canonical reproducibility identifier (ARCHITECTURE.md § 1 item 6; C6; B11).

**DesignRealisationPlan**. The non-operational, always-renderable design output. Includes assembly route, required inputs, QC checkpoints, expected verification artefacts, biosafety classification, institutional-approvals list. Always renderable regardless of authorisation state; the canonical artefact for IBC review (ARCHITECTURE.md § 4.2 `engine.design_plan`).

**Hexagonal architecture**. A software architectural style introduced by Alistair Cockburn. The application core has no knowledge of external systems; all external interactions go through `Port` interfaces with concrete `Adapter` implementations. The Toolkit's domain core is pure; adapter-backed work happens in the application layer; the validator consumes a `ValidationContext` rather than calling adapters directly.

**Marker (selection marker)**. A gene whose product allows selective survival or visual identification of transformed cells. Standalone catalogue `catalogues/markers.yaml` (v0.2; FR-MARK-01..12). Each entry has per-host working concentrations (min / typical / max with medium), counter-selection options where applicable, incompatibilities, use-cases, and audit-grade citations.

**Port**. An abstract interface in hexagonal architecture. The Toolkit declares 51 ports under `domain.ports/` covering sequence I/O, biology adapters, catalogues, screening, vendor, SnapGene, LLM, SOP, authorisation, persistence, external tools, and plugin discovery. See Appendix C.4.

**Risk Group (RG)**. WHO / NIH classification of biological agents by laboratory-handling risk: RG1 (negligible), RG2 (moderate; standard practice), RG3 (high; certified facility), RG4 (very high; maximum containment). Maps to BSL-1/2/3/4 facilities.

**SBOL3**. Synthetic Biology Open Language v3.1.x. A formal data model for synthetic biology designs, using Sequence Ontology terms for feature types. The Toolkit serialises every design to SBOL3 in addition to GenBank (FR-INT-09).

**SnapGene**. A commercial molecular-biology desktop application from Insightful Science / Dotmatics. The de-facto industry standard for visualising and editing plasmid maps. The Toolkit's interoperability is via the open GenBank format (round-trip; FR-INT-01..04) and via a manual cross-check process (BR-16). The Toolkit does not redistribute SnapGene content, does not include SnapGene-derived data in the export bundle, and does not embed SnapGene-trained models. See Appendix M for the IP posture.

---

# Appendix L - References / further reading

All citations carry their PMID where available; URLs given for non-PMID resources. The Toolkit's catalogues embed many of these citations directly; this appendix consolidates them for easy reference.

## L.1 Foundational textbooks

- **Sambrook & Russell, Molecular Cloning: A Laboratory Manual, 4th edition.** Cold Spring Harbor Laboratory Press, 2001. The canonical reference for cloning protocols and working concentrations. Appendix A1 is the authoritative source for antibiotic concentrations.
- **Sambrook & Green, Molecular Cloning, 5th edition.** CSHL Press, in preparation as of 2026.
- **Ausubel et al., Current Protocols in Molecular Biology.** John Wiley & Sons.
- **Glick & Pasternak, Molecular Biotechnology.** ASM Press.

## L.2 Plasmid / vector references

- Bolivar et al. 1977 — pBR322 construction. Gene 2(2):95-113. PMID 344137.
- Yanisch-Perron et al. 1985 — pUC19 / M13 vectors. Gene 33(1):103-119. PMID 2985470.
- Studier 1990 — T7 / pET expression system. Methods Enzymol 185:60-89. PMID 2199796.
- Guzman et al. 1995 — pBAD / araBAD induction. J Bacteriol 177(14):4121-4130. PMID 7768838.
- Sikorski & Hieter 1989 — pRS series for S. cerevisiae. Genetics 122(1):19-27. PMID 2659436.
- Brachmann et al. 1998 — BY-series strain construction. Yeast 14(2):115-132. PMID 9483801.
- He et al. 1998 — AdEasy adenovirus system. Proc Natl Acad Sci USA 95(5):2509-2514. PMID 9482916.

## L.3 Cloning chemistry

- Gibson et al. 2009 — Gibson assembly. Nat Methods 6(5):343-345. PMID 19363495.
- Engler et al. 2008 — Golden Gate. PLoS One 3(11):e3647. PMID 18948503.
- Pryor et al. 2018 — Type IIS overhang fidelity. Nucleic Acids Res 46(10):5267-5276. PMID 30153100 (and Pryor 2020).
- Potapov et al. 2018 — Ligation fidelity dataset. ACS Synth Biol 7(11):2665-2674. PMID 30192978.
- Hartley et al. 2000 — Gateway cloning. Genome Res 10(11):1788-1795. PMID 10721974.

## L.4 Codon usage and translation

- Sharp & Li 1987 — CAI definition. Nucleic Acids Res 15(3):1281-1295. PMID 3447015.
- Kozak 1986 — Kozak consensus and translation initiation. Cell 44(2):283-292. PMID 3839802.
- Kozak 1989 — Cap-dependent scanning model. J Cell Biol 108(2):229-241. PMID 2657394.
- Cigan & Donahue 1988 — Yeast Kozak context. Gene 59(1):1-18. PMID 3300555.
- Owczarzy et al. 2004 — Salt-corrected Tm. Biochemistry 43(12):3537-3554. PMID 15154762.
- SantaLucia 1998 — Nearest-neighbour parameters. Proc Natl Acad Sci USA 95(4):1460-1465. PMID 9501958.

## L.5 Markers (mechanism)

- Beck et al. 1982 — Kanamycin resistance. Gene 19(3):327-336. PMID 6296021.
- Shaw 1975 — Chloramphenicol acetyl-transferase. Methods Enzymol 43:737-755. PMID 1095.
- Hollingshead & Vapnek 1985 — Spectinomycin / aadA. Plasmid 13(1):17-30. PMID 2987812.
- Drocourt et al. 1990 — Zeocin / Sh ble. Nucleic Acids Res 18(13):4009. PMID 2370666.
- Gritz & Davies 1983 — Hygromycin / hph. Gene 25(2-3):179-188. PMID 6313438.

## L.6 Yeast and Pichia

- Gietz & Schiestl 2007 — LiAc transformation. Nat Protoc 2(1):31-34. PMID 17401334.
- Cregg et al. 2009 — Pichia expression. Methods Mol Biol 824:259-285. PMID 19899091.
- Daly & Hearn 2005 — Pichia expression strategy. J Mol Recognit 18(2):119-138. PMID 15549714.

## L.7 Mammalian / viral

- Boshart et al. 1985 — CMV promoter. Cell 41(2):521-530. PMID 2999983.
- Niwa et al. 1991 — CAG promoter. Gene 108(2):193-199. PMID 1660837.
- Dull et al. 1998 — 3rd-generation lentivirus packaging. J Virol 72(11):8463-8471. PMID 9765382.
- Shaner et al. 2004 — mCherry / FP family. Nat Biotechnol 22(12):1567-1572. PMID 15558047.
- Bindels et al. 2017 — mScarlet. Nat Methods 14(1):53-56. PMID 27869816.
- Shaner et al. 2013 — mNeonGreen. Nat Methods 10(5):407-409. PMID 23685885.
- Goedhart et al. 2012 — mTurquoise2. Nat Commun 3:751. PMID 22426491.
- Filonov et al. 2011 — iRFP. Nat Biotechnol 29(8):757-761. PMID 21909076.

## L.8 CRISPR

- Cong et al. 2013 — CRISPR-Cas9 in mammalian cells. Science 339(6121):819-823. PMID 23287718.
- Ran et al. 2013 — Genome engineering CRISPR Cas9 (pX330). Nat Protoc 8(11):2281-2308. PMID 24157548.
- Mali et al. 2013 — RNA-guided human genome engineering. Science 339(6121):823-826. PMID 23287722.

## L.9 Tools

- Roberts et al. 2015 — REBASE restriction enzymes. Nucleic Acids Res 43(D1):D298-D299. PMID 25378308.
- Almagro Armenteros et al. 2019 — SignalP 5.0. Nat Biotechnol 37(4):420-423. PMID 30778257.
- Wagner et al. 2008 — Lemo21(DE3) tuneable T7 expression. Proc Natl Acad Sci USA 105(38):14371-14376. PMID 18369191.

## L.10 Architecture and software engineering (background)

- Cockburn 2005 — Hexagonal architecture (web). https://alistair.cockburn.us/hexagonal-architecture/
- Evans 2003 — Domain-Driven Design. Addison-Wesley.

## L.11 Project source documents (in this repository)

- `README.md` — overview.
- `ARCHITECTURE.md` v1.5 — binding architecture.
- `REQUIREMENTS.md` v0.2 — functional, molecular, wet-lab, vendor, biosafety, and acceptance requirements.
- `CODING_AGENDA.md` — authoritative implementation plan and task ordering.
- `TASK_BOARD.md` — war-room status board.
- `ROADMAP.md` — phase-level record.
- `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` — citation-bearing scientific knowledge base.
- `Cloning_Expression_Vector_Design_White_Paper.md` — human-readable scientific narrative.
- `docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit_v2.md` — IP-audit memo for v0.2.
- `docs/handover/2026-05-23_v0.2_collaborative_audit_synthesis.md` — collaborative audit synthesis for v0.2.

---

# Appendix M - IP / licensing / patent notice

## M.1 Toolkit licensing

The Cloning & Expression Vector Design Toolkit is licensed under **GPL-3.0-only**. This is a strong copyleft licence; derivative software that links to or extends the Toolkit's core must also be GPL-3.0-only. Read the full licence text in the repository's `LICENSE` file.

Practical consequences:

- You may use the Toolkit for academic, personal, or commercial research without payment.
- You may modify the Toolkit; modifications you distribute must be GPL-3.0-only and source must be made available.
- You may build commercial services on top of the Toolkit; if the service runs the Toolkit's code on a server (SaaS), GPL-3.0 (rather than AGPL-3.0) does **not** trigger source-availability for users of the network service. AGPL-3.0 would; GPL-3.0 does not. Confirm by reading the GPL FAQ.
- Catalogue YAML records carry their own licences; some are CC-BY-SA, which imposes share-alike on works that incorporate them. See `THIRD_PARTY_LICENSES.md`.

## M.2 GMExpression(R) trademark

GMExpression(R), GMES, and the GMExpression logo are registered trademarks of General Molecular Expression Service Pty Ltd. The trademark is not licensed under GPL-3.0; you may not use the GMExpression name or logo to imply endorsement of derivative products.

## M.3 Catalogue data licensing

- Sequence and annotation records in `catalogues/parts.yaml`, `catalogues/hosts.yaml`, `catalogues/markers.yaml`, `catalogues/enzymes.yaml`, `catalogues/vendors.yaml`: per-record licensing in the YAML record. Most records are licensed CC-BY 4.0 or public-domain; some are CC-BY-SA 4.0 (which imposes share-alike on works incorporating them).
- ML corpus records under `docs/ml_corpus/records/`: separate sequence and annotation licence blocks per record; the corpus manifest maintains `partition: full` (all records) and `partition: sa_free` (records without share-alike constraints) variants. The `sa_free` partition is the canonical training set for any future closed-source commercial deployment.

## M.4 Addgene posture (nominative use)

Addgene is a non-profit plasmid repository whose name is widely recognised in molecular biology. This Toolkit's documentation cites Addgene under **nominative-use** principles:

- The Addgene name is acknowledged where it is the canonical reference for a specific resource (e.g., "pX330 is Addgene plasmid #42230 from the Zhang lab").
- No Addgene-derived text is reproduced verbatim in this manual or in the Toolkit's catalogues.
- No Addgene-trained models are embedded.
- No Addgene-distributed plasmid sequences are redistributed via the Toolkit; the Toolkit emits the user's designed sequences only.
- Addgene's published educational eBooks (Plasmids 101, CRISPR 101, Fluorescent Proteins 101, Viral Vectors 101, Antibodies 101) are cited in the references; concepts are re-expressed in our own words.

This posture is documented in `docs/handover/2026-05-23_host_marker_ml_corpus_ip_audit_v2.md` § 5 and is enforced by editorial policy.

## M.5 SnapGene posture

SnapGene is a commercial product of Insightful Science / Dotmatics. This Toolkit's interoperability with SnapGene is via:

- The open GenBank file format (FR-INT-01..03), which both products read and write.
- An optional `snapgene-reader` third-party Python package for read-only `.dna` parsing.
- A manual cross-check process (BR-16) performed by a human in a browser.

The Toolkit does not:

- Programmatically scrape, fetch, or extract SnapGene content.
- Redistribute SnapGene-distributed plasmid records.
- Include SnapGene-derived training data in the ML corpus.
- Embed SnapGene-trained models.

The BR-16 manual SnapGene cross-check is **normative**; the Toolkit cannot bypass or automate it.

## M.6 Fork-Readiness Memo

The Fork-Readiness Memo (`docs/fork-readiness/`) is a periodically-updated assessment covering licensing posture, contributor agreement state, third-party dependencies, trademark posture, and any commercialisation-blocking issues. For any commercialisation conversation, read the latest Fork-Readiness Memo first.

## M.7 Patent / FTO

The Toolkit does **not** perform freedom-to-operate (FTO) analysis, patentability assessment, or prior-art search. These are out of scope for v0.2.1; the canonical responsible skill is `/ip-auditor`. Before any commercial submission or patent filing, engage `/ip-auditor`.

## M.8 RUO statement

All outputs are **Research Use Only**. The Toolkit does not authorise clinical, diagnostic, therapeutic, environmental-release, or commercial use of designed constructs. Users remain responsible for institutional biosafety review (IBC), vendor screening, material-transfer obligations, and local regulatory compliance.

## M.9 Disclaimer of warranty

The Toolkit and this manual are distributed AS IS, without warranty of any kind (express or implied), including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall GMExpression be liable for any claim, damages, or other liability arising from use of the Toolkit or this manual.

---

# Back matter

## Standard scientific-advisor disclaimer

This scientific manual is provided for informational, research, and advisory purposes only. It does not constitute professional engineering advice, medical advice, regulatory advice, intellectual-property advice, or formal peer review. All Toolkit outputs and bench procedures must be validated through appropriate laboratory experimentation and, where applicable, reviewed by qualified domain experts before implementation. The Toolkit's authors and the manual's editors are software / scientific-advisory roles supported by AI assistance; the analysis should be treated as a structured starting point for further investigation. Liability for use rests with the user and the user's institution.

## Revision history

| Edition | Date | Author / role | Changes |
|---|---|---|---|
| First Edition | 2026-05-23 | `/scientific-advisor` sub-modes 3 + 5 | Initial complete manuscript covering Toolkit v0.2.1; six layered reading paths; Parts 1-6; Appendices A-M. Cites the v0.2 markers catalogue, the 30-strain host expansion, the 51-port architecture, the BR-16 manual SnapGene cross-check, the v1.5 sponsor strengthening of B3 advisory mitigation, and the v0.2 ML corpus subsystem. |

Subsequent editions will track Toolkit releases.

## Colophon

This manual was produced as a Markdown source file (`docs/instructions/Cloning_Expression_Vector_Design_Toolkit_First_Edition.md`) within the Cloning & Expression Vector Design Toolkit repository. Rendered diagrams use the Mermaid syntax (mermaid-js.github.io). All citations carry PMID identifiers; users can plug each PMID into `https://pubmed.ncbi.nlm.nih.gov/<pmid>/` to retrieve the cited paper. The manual is licensed for distribution alongside the Toolkit under GPL-3.0-only.

The editorial / illustration work was performed under the `/scientific-advisor` skill sub-modes 3 (Manual / Junior Researcher Guide) and 5 (Scientific Illustration / Workflow Charts). The manual integrates concepts from the Addgene eBook series (Plasmids 101, CRISPR 101, Fluorescent Proteins 101, Viral Vectors 101, Antibodies 101) re-expressed in original language per the nominative-use IP posture documented in Appendix M.

Body type: Markdown source uses standard ASCII; biology-specific Unicode characters (alpha, beta, mu, Delta) are permitted at first use only. ASCII-safe characters are preferred throughout for compatibility with the project's cp1252-default Windows console.

(c) 2026 General Molecular Expression Service Pty Ltd (GMExpression(R), GMES). All rights reserved. GMExpression(R) is a registered trademark. Manual licensed under GPL-3.0-only.

End of First Edition.

---

# Supplementary Material A - Extended worked examples

To complement the conceptual material in Parts 1-3 and the procedural material in Parts 4-5, this supplementary appendix presents three end-to-end worked examples that exercise the Toolkit on representative real-world tasks. Each example shows the Wizard inputs, the resulting validation report, the export bundle structure, and the bench workflow. The examples are simplified for pedagogy; production designs would carry additional advisories and more conservative defaults.

## SM-A.1 Worked example 1 - pET-28a-(His6)-MyEnzyme in BL21(DE3)

### SM-A.1.1 Intent

A graduate student wishes to express a 35-kDa cytoplasmic enzyme from *Bacillus subtilis* in *E. coli* for biochemical characterisation. The enzyme is well-behaved (no disulfides, no membrane domains, no rare cofactors), so a standard pET-28a + BL21(DE3) workflow is appropriate. The student wants an N-terminal His6 tag with a thrombin cleavage site so the tag can be removed for downstream crystallography.

### SM-A.1.2 Wizard inputs

- Step 1 - Objective: Recombinant protein expression.
- Step 2 - Host: BL21(DE3); operating role: expression.
- Step 3 - Cargo: paste the *B. subtilis* CDS (or upload a FASTA); type: protein-coding ORF; source organism: *B. subtilis* 168.
- Step 4 - Promoter: T7 (pET-28a backbone); inducer: IPTG; strength target: high.
- Step 5 - Tagging: N-terminal His6 + thrombin linker (LVPRGS); C-terminal: none.
- Step 6 - Cloning chemistry: NdeI + XhoI restriction-ligation into pET-28a MCS.
- Step 7 - Biosafety: BSL-1.

Free-text channel (Step 4): "Plan to express at 18 deg C overnight to maximise soluble fraction; downstream use is crystallography so tag must be cleanable."

### SM-A.1.3 Toolkit response

After "Build construct", the engine produces a construct graph with:

- pET-28a backbone (5369 bp) including: lac repressor (LacI), T7 promoter, lac operator, RBS, ATG, N-terminal His6 + thrombin site, NdeI site, MCS, XhoI site, C-terminal His6 (optional, you would suppress this if you want only N-term), T7 terminator, pUC ori, KanR.
- Inserted *B. subtilis* enzyme CDS.

Validation report (illustrative):

- `INFO MR-CODON-CAI`: CAI = 0.74 against E. coli K-12 codon table. Pass.
- `INFO MR-GC-CONTENT`: GC = 49.3%; in acceptable range.
- `INFO MR-RESTRICTION-UNIQUE-NDEI`: NdeI site is unique in the assembled construct.
- `INFO MR-RESTRICTION-UNIQUE-XHOI`: XhoI site is unique.
- `INFO MR-MARKER-MISMATCH`: Kan (neo) marker is compatible with BL21(DE3); see `markers.yaml::marker.kanamycin`.
- `SOFT caution WR-PRIMER-TM-DIVERGENCE`: forward primer Tm = 58.2; reverse primer Tm = 64.3; divergence 6.1 deg C exceeds soft threshold (5 deg C). Suggested fix: trim reverse primer 5'-end by 2 nt to bring Tm to ~ 60.
- `INFO BR-BIOSAFETY-TIER`: BSL-1; cargo source *B. subtilis* 168 is RG1; tier consistent.

The student adjusts the reverse primer per the suggested fix; re-validates; all advisories clear except the INFOs (no action required).

### SM-A.1.4 BR-16 manual cross-check

The student opens the proposed construct GenBank in SnapGene 7.2. They confirm:

- All 14 expected features are present.
- His6 tag is in-frame with the inserted CDS.
- Thrombin cleavage site (LVPRGS) is in-frame just upstream.
- NdeI / XhoI sites are at the expected positions.
- Backbone matches pET-28a NCBI reference (~ 5369 bp).

The student clicks "BR-16 confirmed" and supplies the justification: "Cross-checked in SnapGene 7.2 on 2026-05-23; 14 features, length 6512 bp, GC 49.3%, His6+thrombin in-frame, NdeI/XhoI unique."

### SM-A.1.5 Screening + authorisation

The configured IGSC adapter returns CLEAR. The student's `AuthorisationProfile` (granted earlier by the institutional administrator) covers BSL-1 + recombinant protein expression + pET vector class + BL21(DE3); the authorisation gate passes.

### SM-A.1.6 Export bundle

The bundle (`my-pet-bsubenzyme-2026-05-23-abc123.zip`) contains the full set of files described in § 3.8. The student attaches the bundle's sequence files to a Twist order, places the order, and bookmarks the bundle's path.

### SM-A.1.7 Bench execution

Eight business days later, the Twist clonal plasmid arrives. The student:

1. Transforms 50 ng into DH5-alpha; plates on LB-Kan; picks 4 colonies overnight.
2. Mini-preps the 4; diagnostic digest with NdeI + XhoI confirms the expected fragment sizes (5369 bp backbone + 1.0 kb insert).
3. Sanger-sequences the insert with T7 promoter primer and T7 terminator primer; trace matches design.
4. Re-transforms verified plasmid into BL21(DE3); plates on LB-Kan; picks 2 colonies.
5. Inoculates 5 mL LB-Kan overnight; subcultures to 250 mL LB-Kan; grows to OD600 ~ 0.6 at 37 deg C; cools to 18 deg C; induces with 0.5 mM IPTG; expresses overnight (~ 16 h).
6. Pellets cells; lyses by sonication in lysis buffer; clarifies; runs SDS-PAGE of soluble vs insoluble fractions.
7. Observes a clear ~ 37 kDa band (35 kDa enzyme + ~ 2 kDa His6+thrombin tag) in the soluble fraction.
8. Purifies by Ni-NTA affinity (10 mM imidazole bind, 250 mM elute); pools fractions; cleaves with thrombin overnight at 4 deg C; re-passes over Ni-NTA to remove the cleaved tag; concentrates; SEC polishing.

Total time from intent to purified protein: ~ 3 weeks.

## SM-A.2 Worked example 2 - sgRNA + Cas9 in HEK293 for AAVS1 knock-in

### SM-A.2.1 Intent

A postdoc plans to knock in a 1.5-kb floxed mCherry reporter into the human AAVS1 safe-harbour locus in HEK293 cells, for downstream live-cell imaging.

### SM-A.2.2 Wizard inputs

- Objective: CRISPR knock-in.
- Host: HEK293 (target cells); operating role: target.
- Cargo: a 20-nt sgRNA targeting AAVS1 + an HDR template (1.5-kb floxed mCherry flanked by 600-bp homology arms to AAVS1).
- Promoter: U6 (for sgRNA in pX458) + CAG (for mCherry expression in the HDR template).
- Tagging: none on the genomic cargo; mCherry is the cargo itself.
- Cloning chemistry: BbsI Golden Gate ligation of the sgRNA insert into pX458 + Gibson assembly of the HDR template into a Bluescript-based pUC backbone.
- Biosafety: BSL-2 (recombinant genome modification).

Free-text channel: "Need RNP delivery option as backup; pX458 GFP+ FACS-sort within 48 h post-transfection; AAVS1 site is well-validated as safe harbour."

### SM-A.2.3 Toolkit response

The Toolkit produces two constructs:

1. pX458-sgAAVS1 with the 20-nt protospacer cloned into the BbsI site.
2. pUC-AAVS1-LHA-loxP-mCherry-loxP-RHA HDR template.

Validation:

- `INFO MR-CAS-PAM`: PAM at protospacer + 3 = "AGG" (canonical NGG); pass.
- `SOFT caution MR-HDR-TEMPLATE-PAM`: the HDR template will be cut by Cas9 because the PAM (AGG) is preserved in the donor. Suggested fix: introduce a silent G > A mutation in the third base of the PAM (NGG -> NAG, still acceptable codon synonym). The postdoc accepts the fix; the engine updates the donor.
- `SOFT caution BR-BIOSAFETY-TIER-AAVS1-CRISPR`: AAVS1 is a safe-harbour locus and BSL-2 is the standard institutional tier; reviewer sign-off recommended.
- `INFO WR-GIBSON-ARMS`: HDR donor uses 25 bp Gibson overlaps; pass.

The postdoc acknowledges the BSL-2 advisory with the institutional IBC approval number; escalation to the IBC is not required because the approval is already in place.

### SM-A.2.4 BR-16

The postdoc opens both constructs in SnapGene; confirms protospacer in-frame with U6 promoter; confirms loxP sites flank mCherry CDS in the correct orientations; clicks "BR-16 confirmed".

### SM-A.2.5 Bench execution

1. Order sgRNA insert as paired BbsI-overhang oligos from IDT; anneal; ligate into pX458; transform; mini-prep; Sanger-verify.
2. Order the 1.5-kb HDR template as a Twist clonal in pUC backbone.
3. Co-transfect HEK293 (6-well, Lipofectamine 3000): 1 ug pX458-sgAAVS1 + 1 ug HDR template.
4. After 48 h, FACS-sort GFP+ cells (pX458 marker) single-cell into 96-well; expand clones for 10-14 days.
5. Genotype clones by amplicon PCR across the AAVS1 left junction and right junction; pick correctly-targeted heterozygous and homozygous clones.
6. Live-image to confirm mCherry expression in the expanded clones.

## SM-A.2.6 Result

Total time from intent to validated knock-in clones: ~ 4-6 weeks.

## SM-A.3 Worked example 3 - Lentivirus packaging for a stable mammalian reporter line

### SM-A.3.1 Intent

A senior scientist wishes to make a CHO-K1 stable line carrying a CMV-EGFP reporter under puromycin selection. They will use third-generation lentivirus for delivery.

### SM-A.3.2 Wizard inputs

- Objective: Viral packaging (lentivirus).
- Host: CHO-K1 (target).
- Cargo: CMV-EGFP-WPRE expression cassette + Puro selection marker (PGK-puro).
- Promoter: CMV (for EGFP); PGK (for puro).
- Tagging: none on EGFP.
- Cloning chemistry: Gibson assembly of cargo into pLenti-puro backbone.
- Biosafety: BSL-2 (lentiviral packaging).

Free-text: "3rd-gen SIN packaging with psPAX2 + pMD2.G; HEK293T producer; target CHO at MOI 1-5."

### SM-A.3.3 Toolkit response

The Toolkit produces a lentivirus transfer vector (~ 9 kb) with:

- 5' SIN LTR.
- psi packaging signal.
- RRE.
- cPPT.
- CMV promoter.
- EGFP CDS.
- WPRE.
- PGK promoter.
- Puromycin resistance CDS.
- 3' SIN LTR.

Validation:

- `INFO WR-LENTI-CARGO`: cargo size 4.3 kb < 8 kb budget; pass.
- `SOFT caution WR-LENTI-LTR-RECOMB`: LTR-LTR recombination risk in propagation; recommend Stbl3 / Stbl4 strain for cloning.
- `INFO MR-PUROMYCIN`: Puromycin marker compatible with CHO-K1; concentration 5 ug/mL from `markers.yaml`.
- `SOFT strong_caution BR-LENTI-PACKAGING`: lentiviral packaging is BSL-2; institutional IBC approval and biosafety cabinet required.

The scientist acknowledges both with strong justifications including the IBC approval number.

### SM-A.3.4 BR-16 + screening

SnapGene cross-check confirms ITR-equivalents (LTRs), WPRE positioning (after CDS, before 3' LTR), and overall layout. The IGSC screening adapter returns CLEAR (EGFP is benign, puro is benign, the LTR / psi / RRE / cPPT / WPRE elements are common and not on any watchlist).

### SM-A.3.5 Bench execution

1. Clone the transfer vector in Stbl3 (NEB Stable); mini-prep; verify by digest and Sanger.
2. Triple-transfect HEK293T (10-cm dish): 9 ug pLenti-CMV-EGFP-PGK-puro + 6 ug psPAX2 + 3 ug pMD2.G; using Lipofectamine 3000.
3. At 24 h, replace medium with 6 mL fresh DMEM + 10% FBS.
4. At 48 h, collect supernatant; filter (0.45 um); titrate (FACS GFP+ on a small culture of HEK293 target cells).
5. Transduce CHO-K1 at MOI ~ 2 in the presence of 8 ug/mL polybrene; 8 h.
6. After 48 h, select with 5 ug/mL puromycin; replace medium every 3 days; surviving colonies appear in 7-10 days.
7. Pick 12 colonies; expand; FACS-sort GFP+ cells; freeze 5 vials per clone; archive the rest for assays.

Total time from intent to validated stable line: ~ 6-8 weeks.

---

# Supplementary Material B - Cheat sheets

## SM-B.1 Antibiotic cheat sheet (E. coli LB)

| Antibiotic | Stock | Working | Solvent |
|---|---|---|---|
| Ampicillin / Carbenicillin | 100 mg/mL | 100 / 50-100 ug/mL | Water |
| Kanamycin | 50 mg/mL | 50 ug/mL | Water |
| Chloramphenicol | 34 mg/mL | 34 ug/mL | Ethanol |
| Tetracycline | 12.5 mg/mL | 12.5 ug/mL | Ethanol; light-sensitive |
| Spectinomycin | 100 mg/mL | 100 ug/mL | Water |
| Zeocin | 100 mg/mL | 25 ug/mL | Water; use low-salt LB |
| Gentamicin | 50 mg/mL | 25 ug/mL | Water |
| Hygromycin B | 100 mg/mL | 200 ug/mL (bacterial) | Water |
| Erythromycin | 100 mg/mL | 100 ug/mL | Ethanol |

All from `catalogues/markers.yaml` v0.2 with Sambrook 4th ed. Appendix A1 references.

## SM-B.2 PCR cycle cheat sheet

| Step | Temperature | Time |
|---|---|---|
| Initial denaturation | 95-98 deg C | 30-180 s |
| Cycle - denaturation | 95-98 deg C | 10-30 s |
| Cycle - annealing | (primer Tm - 5) | 15-30 s |
| Cycle - extension | 72 deg C (Taq); 72 (Phusion); 68 (KOD) | 30-60 s/kb |
| Number of cycles | 25-35 | |
| Final extension | 72 deg C | 5-10 min |
| Hold | 4-10 deg C | infinite |

## SM-B.3 Transformation cheat sheet

| Step | Heat-shock | Electroporation |
|---|---|---|
| Cell volume | 50 uL | 40-50 uL |
| DNA volume | 1-5 uL | 1-2 uL salt-free |
| Cold-incubate | Yes (20-30 min) | No |
| Pulse | 42 deg C 30-45 s | 1.8 kV (1-mm) |
| Recovery | 1 h 37 deg C SOC | 1 h 37 deg C SOC |
| Plating | 50-100 uL | 50-100 uL |

## SM-B.4 Mini-prep cheat sheet

| Buffer | Components |
|---|---|
| P1 (resuspension) | 50 mM Tris-HCl pH 8.0, 10 mM EDTA, 100 ug/mL RNase A |
| P2 (lysis) | 200 mM NaOH, 1% SDS |
| N3 (neutralisation) | 3 M potassium acetate, pH 5.5 |
| PE (wash) | 80% EtOH + Tris + EDTA |
| EB (elution) | 10 mM Tris-HCl pH 8.5 |

## SM-B.5 Yeast media cheat sheet

| Medium | Composition |
|---|---|
| YPD | 1% yeast extract, 2% peptone, 2% glucose |
| YPDS | YPD + 1 M sorbitol (Pichia only) |
| SD (-Ura) | 0.67% YNB without amino acids, 2% glucose, complete drop-out minus uracil, agar 2% (plates) |
| SC (synthetic complete) | YNB + 2% glucose + complete amino acid drop-out |
| BMGY | Buffered minimal glycerol; 1% yeast extract, 2% peptone, 100 mM K-phosphate pH 6.0, 1.34% YNB, 4 x 10^-5 % biotin, 1% glycerol |
| BMMY | Same as BMGY but 0.5-1% methanol instead of glycerol |

## SM-B.6 Mammalian transfection cheat sheet (HEK293, 6-well)

| Reagent | Amount |
|---|---|
| Cells (per well, at transfection) | 0.4-0.8 x 10^6 (70-80% confluent) |
| DNA | 2.5 ug |
| Opti-MEM Tube A | 125 uL |
| Lipofectamine 3000 | 7.5 uL |
| P3000 reagent | 5 uL |
| Opti-MEM Tube B | 125 uL |
| Total medium during transfection | 2 mL DMEM + 10% FBS |
| Medium replacement | 4-6 h post-transfection |
| Harvest time | 24-72 h |

## SM-B.7 SDS-PAGE cheat sheet

| Component | Concentration |
|---|---|
| Resolving gel | 10-15% acrylamide, 0.375 M Tris pH 8.8, 0.1% SDS, 0.1% APS, 0.04% TEMED |
| Stacking gel | 4% acrylamide, 0.125 M Tris pH 6.8, 0.1% SDS, 0.1% APS, 0.1% TEMED |
| Running buffer | 25 mM Tris, 192 mM glycine, 0.1% SDS, pH 8.3 |
| Sample buffer (Laemmli) | 50 mM Tris-HCl pH 6.8, 2% SDS, 10% glycerol, 0.01% bromophenol blue, 100 mM DTT or 2-mercaptoethanol (5%) |
| Voltage | 80 V stacking, 120-150 V resolving |

---

# Supplementary Material C - Quick reference for common Toolkit warnings

## SM-C.1 MR (Molecular Rule) advisories

| Code | Meaning | Typical fix |
|---|---|---|
| `MR-PROMOTER-HOST` | Promoter not recognised by selected host | Change promoter or host |
| `MR-KOZAK-WEAK` | Kozak context lacks +1 G or -3 purine | Engineer Kozak (gccRccATGG) |
| `MR-RBS-MISSING` | No Shine-Dalgarno detected | Add canonical RBS (AGGAGG, 6-8 nt upstream of ATG) |
| `MR-RBS-WEAK` | SD-AUG distance or SD strength suboptimal | Move SD or strengthen consensus |
| `MR-RBS-OCCLUDED` | mRNA secondary structure occludes RBS | Reduce GC near RBS or engineer ribosome-friendly leader |
| `MR-MARKER-MISMATCH` | Marker not validated for host | Use compatible marker from `markers.yaml` |
| `MR-CODON-CAI` | CAI below threshold | Run codon optimiser |
| `MR-CODON-RARE-CLUSTER` | >= 3 rare codons in a window | Synonymous substitution or Rosetta(DE3) host |
| `MR-GC-CONTENT` | GC outside acceptable range | Engineer synonymous codons |
| `MR-RESTRICTION-UNIQUE-<ENZ>` | Site not unique in construct | Re-design or pick alternative enzyme |
| `MR-INFRAME-STOP` | In-frame stop in cargo | Remove or synonymous-mutate |
| `MR-INTERNAL-MET-START` | Likely internal methionine start | Engineer to suppress |
| `MR-POLYA-MISSING` | No polyA signal in mammalian cassette | Add bGH polyA or SV40 polyA |
| `MR-CAS-PAM-MISMATCH` | Wrong PAM for chosen Cas | Re-design guide or change Cas variant |
| `MR-SIGNAL-PEPTIDE-CLEAVAGE` | Signal peptide cleavage site suboptimal | Re-design signal peptide |
| `MR-HDR-TEMPLATE-PAM` | HDR template will be re-cut | PAM-disrupting silent mutation |
| `MR-CMV-SILENCING` (info) | CMV may silence in this line over passages | Consider EF1alpha / CAG |

## SM-C.2 WR (Wet-lab Rule) advisories

| Code | Meaning | Fix |
|---|---|---|
| `WR-PRIMER-TM-DIVERGENCE` | Primer Tm pair differs > 5 deg C | Adjust primer length |
| `WR-PRIMER-DIMER` | Primer self-dimer or pair-dimer | Re-design with primer3 settings |
| `WR-PRIMER-OFFTARGET` | Off-target binding in template | Re-design primer further into insert |
| `WR-GIBSON-HOMOLOGY-SHORT` | Homology arms < 20 bp | Extend to 25-40 bp |
| `WR-GIBSON-FRAGMENT-COUNT` | More than 5 fragments | Switch to Golden Gate or split into stages |
| `WR-GG-OVERHANG-FIDELITY` | Pryor 2018 fidelity < 90% | Run engine.overhang to pick better set |
| `WR-LENTI-CARGO-OVERSIZE` | Lenti cargo > 8 kb | Trim or split |
| `WR-LENTI-LTR-RECOMB` | LTR-LTR recombination risk | Use Stbl3 / Stbl4 |
| `WR-AAV-CARGO-OVERSIZE` | AAV cargo > serotype packaging limit | Trim or use larger-capacity serotype |
| `WR-REPEAT-RECOMB` | Repeat > 100 bp in cargo | Use Stbl strain or break up repeat |
| `WR-FRAGMENT-OVERSIZE` | Fragment exceeds chemistry's scale | Different chemistry |

## SM-C.3 SR (Synthesis-vendor Rule) advisories

| Code | Meaning | Fix |
|---|---|---|
| `SR-LENGTH-OVER-VENDOR` | Insert > vendor max single-fragment | Split into 2 fragments |
| `SR-VENDOR-PROHIBITED` | Sequence contains vendor-prohibited motif | Synonymous re-engineering |
| `SR-GC-WINDOW` | Sub-window GC outside vendor range | Synonymous re-engineering |
| `SR-HOMOPOLYMER` | Homopolymer > vendor limit | Break with synonymous codon |
| `SR-REPEAT-CONTENT` | Repeat content above vendor threshold | Re-design with diverse codons |
| `SR-COST` | Estimated cost above project budget | Justify or redesign |

## SM-C.4 BR (Biosafety Rule) advisories

| Code | Meaning | Required action |
|---|---|---|
| `BR-16-SNAPGENE-CROSSCHECK-MISSING` | BR-16 not confirmed | Perform manual cross-check |
| `BR-BIOSAFETY-TIER-MISMATCH` | Declared tier may be too low | IBC review |
| `BR-CARGO-RG2+` | Cargo from RG2 / RG3 organism | IBC approval |
| `BR-REPLICATION-COMPETENT` | Construct may be replication-competent | IBC, dual-control |
| `BR-VIRAL-PACKAGING` | Lentiviral / AAV / adenoviral packaging | BSL-2; IBC approval |
| `BR-DUAL-USE-CONCERN` | Cargo on dual-use research concern list | Institutional review |

## SM-C.5 MS (MS2 / VLP rule) advisories

| Code | Meaning |
|---|---|
| `MS-PACKAGING-SIGNAL` | MS2 packaging-signal handling rules |
| `MS-CAPSID-EXPRESSION` | Capsid expression policy (separation from cargo) |
| `MS-HELPER-SEPARATION` | Helper function not properly separated |
| `MS-VLP-CARGO-SIZE` | Cargo size vs capsid capacity |

---

# Supplementary Material D - Deep technical reference

This supplementary material is for advanced users and software developers who want a deeper view of the engines, the catalogues, and the validation logic. It is not required reading for routine bench users.

## SM-D.1 The validation engine in detail

### SM-D.1.1 Dependency DAG

The validation engine (`engine.validation`) is a pure DAG (directed acyclic graph) evaluator over (construct fields x derived metrics) (C5 in ARCHITECTURE.md). Each `ValidationRule` declares:

- `id` (e.g., `MR-KOZAK-STRENGTH`).
- `category` (MR / WR / SR / BR / MS).
- `severity_policy` (function from rule outputs to INFO / SOFT / HARD).
- `depends_on_metrics` (list of metric IDs the rule reads).
- `produces_metrics` (list of metric IDs the rule writes; usually empty for terminal rules).
- `invalidates` (list of metrics that must be recomputed if a rule fires).
- `preconditions` (list of construct conditions under which the rule is active).
- `target_context` (cassette element, library member, control, etc.).
- `external_adapters` (list of adapters whose output the rule consumes).
- `threshold_profile` (the parameter set used by the rule's logic).
- `last_reviewed` and `reviewed_by` (maintenance metadata).
- `test_fixtures` (golden inputs / outputs for the rule's test).

The engine constructs a DAG over rules x metrics; for any change to the construct, the `engine.dependencies` module computes the minimal set of rules whose preconditions or input metrics changed; only those rules re-run. This is what gives the Toolkit its < 2-second incremental validation latency.

### SM-D.1.2 Incremental re-eval

When the user edits the construct:

1. `engine.session` emits a `ConstructEdited` event with a diff (added / removed / modified parts).
2. `engine.dependencies` consults the field-and-metric DAG; computes the set of rules whose `depends_on_metrics` overlaps the changed fields, plus any rules transitively invalidated.
3. `app.validation_orchestrator` re-runs only those rules (and any pre-computed metrics they require).
4. The new `ValidationReport` is diff-rendered in the UI (added / removed / changed findings).

### SM-D.1.3 Lexicographic-priority fixed-point

For the codon-optimisation x validation loop (`app.assembly_orchestrator`), the engine iterates:

1. Codon-optimise CDS (with forbidden-motif and host-codon constraints).
2. Re-validate.
3. If the optimised CDS introduced a new validation issue (e.g., a new restriction site, a new repeat), apply the next constraint in the lexicographic-priority order to suppress it.
4. Repeat up to N = 5 iterations.
5. If no fixed point reached, surface as `WR-CODON-CONVERGENCE-FAIL`.

Lexicographic priority: forbidden motifs > restriction-site uniqueness > GC window > repeat content > CAI target. The order is configurable per rule manifest but defaults are conservative.

## SM-D.2 The construct graph in detail

### SM-D.2.1 SequenceRecord

A `SequenceRecord` carries:

- `id` (UUID).
- `sequence` (the raw DNA / RNA / protein string).
- `topology` (LINEAR or CIRCULAR).
- `alphabet` (DNA / RNA / protein).
- `features` (list of `Feature` objects).
- `length` (derived; redundant for fast access).
- `checksum` (SHA-256 of canonical serialisation).
- `provenance` (source: import path + format, or Wizard build).

### SM-D.2.2 Location

A `Location` is the typed coordinate range for a `Feature`:

- Simple range: `[start, end, strand]`.
- Fuzzy: `<start..>end` (uncertain boundaries).
- Between-base: `start^start+1` (cut sites).
- Compound: `join(loc1, loc2, ...)` (e.g., split CDS across an intron).
- Ordered: `order(loc1, loc2, ...)` (independent features in a specified order).
- Complement: reverse-strand.
- Remote: references an external SequenceRecord.
- Partial: 5' partial / 3' partial flags.

The `Location` algebra (M3) supports length-invariant operations: addition, subtraction, intersection, and complement.

### SM-D.2.3 Feature

A `Feature` carries:

- `id` (UUID).
- `type` (Sequence Ontology term: CDS, promoter, terminator, RBS, primer_bind, etc.).
- `location` (a `Location`).
- `qualifiers` (a typed `Qualifier` object — B6; replaces the old `dict[str, str]`).
- `provenance` (parent part if any; catalogue version).

### SM-D.2.4 ConstructGraph

A `ConstructGraph` is the canonical typed representation of a construct:

- `nodes`: dict of node-id -> `Part` / `Feature` / `Module`.
- `edges`: list of typed edges:
  - `Adjacency(parent, child)` for physical-order relationships.
  - `Regulatory(promoter, cds)` for regulatory relationships.
  - `Derivation(parent, descendant)` for the design lineage.
  - `Assembly(fragment1, fragment2, chemistry)` for chemistry-driven joins.
- `topology`: the parent `SequenceRecord` topology.
- `metadata`: free-form key/value for tags / annotations.

The `feature_table` (a flat list of features) is a **derived view** of the graph (M4); a synchronising invariant ensures the two always agree.

## SM-D.3 Host catalogue in detail (v0.2 expansion)

The v0.2 host catalogue (`catalogues/hosts.yaml`) expanded from the v0.1 baseline to 35+ strains. Each entry has the schema fields below (from `schemas/hosts.schema.json`):

- `id`, `name`, `genus`, `species`, `strain`.
- `host_class` (`ecoli`, `yeast`, `pichia`, `mammalian`, `insect`, `plant`, `cell_free`).
- `host_role` (operating role: `cloning_propagation`, `expression`, `producer`, `target`, etc.).
- `genotype` (free-text per Sambrook / vendor designation).
- `phenotype` block:
  - `t7_lysogeny` (true if carries the DE3 lysogen).
  - `protease_status` (genes deleted: `lon`, `ompT`, `clpP`, etc.).
  - `redox` (`trxB`, `gor` deletion status for cytoplasmic disulfide).
  - `rare_codon_supplementation` (carries pRARE? which rare tRNAs?).
  - `plasmid_addons` (pLysS, pLysE, pRARE, none).
  - `recombination` (recA1, recBCD, etc.).
  - `methylation` (dam, dcm, hsdRMS).
- `compatible_markers` (list of marker IDs from `markers.yaml` that work with this strain).
- `incompatible_markers` (list of markers that should NOT be used).
- `media` (recommended growth media).
- `temperature` (recommended growth temperature).
- `notes` (free-text).
- `citation` (canonical reference).
- `maintenance` block (per the maintenance schema).

### SM-D.3.1 30-strain expansion enumerated

The v0.2 Enrichment Amendment (REQUIREMENTS.md § 11.3) covers (cumulative):

**E. coli cloning strains (8):** DH5-alpha, NEB-5alpha, TOP10, DH10B, DH10beta, XL1-Blue, XL10-Gold, JM109.

**E. coli stable / unstable-insert strains (4):** Stbl3, Stbl4, NEB Stable, ClearColi.

**E. coli expression strains (12):** BL21, BL21(DE3), BL21(DE3)pLysS, BL21(DE3)pLysE, BL21(DE3)Rosetta, BL21(DE3)Rosetta2, Lemo21(DE3), Origami(DE3), Origami2(DE3), SHuffle T7 Express, C41(DE3), C43(DE3).

**E. coli specialised (3):** MG1655, W3110, ER2566.

**E. coli for plant/agro (1):** LBA4404 (Agrobacterium).

**Yeast (5):** BY4741, BY4742, W303, INVSc1, CEN.PK.

**Pichia (5):** X-33, GS115, KM71H, SMD1163, PichiaPink.

**Mammalian (12):** HEK293, HEK293T, HEK293F, Expi293F, CHO-K1, CHO-S, CHO-DG44, HeLa, U2OS, COS-7, A549, MCF-7.

**Insect (3):** Sf9, Sf21, High Five.

**Cell-free (3):** PURE, S30, TXTL.

The expansion was driven by feedback from users who hit "Other" too often; the engine's compatibility checks are stronger when the host is in the catalogue.

## SM-D.4 Markers catalogue in detail (v0.2)

The v0.2 markers catalogue (`catalogues/markers.yaml`) covers 23 markers:

**Bacterial antibiotic (9):** Amp/Carb, Kan, Cm, Tet, Spec, Zeo (bacterial), Gen, Hyg (bacterial), Erm.

**Yeast auxotrophic (6):** URA3, LEU2, HIS3, TRP1, MET15/17, LYS2.

**Yeast dominant (4):** KanMX (G418), HphMX (Hyg), NatMX (clonNAT), BleMX (Zeo).

**Mammalian (5):** puromycin, blasticidin, G418 (neo), hygromycin (mammalian), Zeocin (mammalian).

Each entry carries:

- `id`, `name`, `class` (bacterial_antibiotic / yeast_auxotrophic / yeast_dominant / mammalian).
- `gene`, `mechanism` (one-line summary of how the marker works).
- `plasmid_borne` (Y / N), `chromosomal` (Y / N).
- `working_concentrations` (list, per host_class, with `agent`, `concentration_ugml` { min, typical, max }, `medium`, `notes`, `citation`).
- `incompatibilities` (list of conditions under which the marker fails or misbehaves).
- `use_cases` (list of vector families that conventionally use the marker).
- `compatible_hosts` (cross-link list of host IDs).
- `citation` (canonical reference; typically Sambrook 4th ed. Appendix A1 plus primary literature).
- `maintenance` (per the maintenance schema).

The compatibility engine consults this catalogue via the `MarkersCataloguePort` for `MR-MARKER-MISMATCH` advisories (FR-MARK-12).

## SM-D.5 Risk-classification catalogue

`catalogues/rules/MR.yaml`, `WR.yaml`, `SR.yaml`, `BR.yaml`, `MS.yaml`, and `risk_advisories.yaml` carry the rule and advisory definitions. The risk-advisory catalogue (`risk_advisories.yaml`) is admin-controlled and signed; the Toolkit refuses to load an unsigned version.

Categories of advisory:

- **high_risk_element**: cargo contains a sequence flagged as high-risk (toxin gene, virulence factor, controlled substance precursor).
- **elevated_biosafety**: cargo or vector class indicates an elevated biosafety tier (RG2+ organism, replication-competent virus, gene-drive element).
- **requires_approval**: construct may require additional institutional approval (clinical-translation candidate, dual-use research concern).

Each advisory has:

- `id`, `category`, `pattern` (regex / motif / lookup-table reference).
- `severity` (`info`, `caution`, `strong_caution`).
- `justification_template` (the prompt shown to the user requesting justification).
- `escalation_target` (Reviewer / Administrator / IBC).
- `citation` (peer-reviewed source for why this is flagged).

## SM-D.6 Screening orchestration

The `ScreeningOrchestrator` (`app.screening_orchestrator`) runs the configured screening adapter(s) in sequence:

1. Submit assembled construct to the first adapter (default: IGSC).
2. Receive typed verdict; record `ScreeningResult` with adapter ID, version, verdict, evidence (where the adapter provides it), and timestamp.
3. If verdict is CLEAR, return CLEAR.
4. If verdict is WATCHLIST / MANUAL_REVIEW_REQUIRED, route to the Review Queue and pause the pipeline.
5. If verdict is HIT, block export and route to IBC.
6. If verdict is UNAVAILABLE, try the next configured adapter.
7. If all adapters return UNAVAILABLE, the verdict caps at MANUAL_REVIEW_REQUIRED (B10: fallbacks never silently produce CLEAR).
8. If the construct is `NOT_APPLICABLE` (e.g., a pure backbone-only design), record and proceed.

The adapter trust is determined by an institution-controlled `ScreeningProviderTrustPolicy` (B10). Trust levels: `trusted_full` (verdict authoritative), `trusted_clear_only` (a CLEAR is honoured; anything else routes to Reviewer), `untrusted` (verdict logged but does not advance the gate).

Screening runs at the **assembled-product** level by default; fragment-only screening only when the trust policy explicitly permits it.

## SM-D.7 LLM constraint translator

The `app.constraint_translator` is an application service that translates free-text user input (from the Wizard's free-text channel) into structured constraints the validator can use. Architecture:

1. User enters free-text in Step N of the Wizard.
2. `constraint_translator` dispatches to a configured LLM adapter (OpenAI, Anthropic, or LocalLlm).
3. The LLM returns a proposed structured constraint set (e.g., "preferred_temperature": 18, "preferred_solubility_tag": "MBP").
4. The Toolkit presents the proposed constraints to the user for **explicit confirmation** — the LLM's text is **never** authoritative without user confirmation (M10 in ARCHITECTURE.md).
5. User confirms (or edits); the snapshot is committed to the `DesignSession`.
6. Validator consumes the confirmed constraints alongside the user's structured selections.

The CI gate `llm-output-policy-check` enforces: LLM outputs must be wrapped in a typed snapshot; must require explicit user confirmation; must not silently bypass any rule.

## SM-D.8 Audit log schema

Each `DomainEvent` in the audit log is JSON of the form:

```json
{
  "event_id": "uuid",
  "event_type": "AdvisoryWarningPresented" | "RiskAdvisoryAcknowledged" | "AuthorisationGranted" | ...,
  "timestamp": "2026-05-23T14:35:22.123Z",
  "principal_id": "user-tocvi",
  "session_id": "uuid",
  "subject_id": "uuid",
  "subject_type": "DesignSession" | "Construct" | "RiskAdvisory" | "AuthorisationProfile",
  "payload": { ... typed per event_type ... },
  "content_hash": "sha256:...",
  "signature": { "algorithm": "Ed25519", "public_key_id": "key-tocvi", "value": "..." },
  "predecessor_event_id": "uuid",
  "predecessor_event_hash": "sha256:..."
}
```

The `predecessor_event_id` + `predecessor_event_hash` form a hash chain over the audit log; any mutation of a past event invalidates all subsequent hashes. Append-only by construction.

## SM-D.9 DerivationEnvironment fields (full)

The `DerivationEnvironment` (per C6 / B11 in ARCHITECTURE.md) captures all inputs that materially change outputs:

- `catalogue_versions`: per-catalogue version + content hash (parts, hosts, markers, enzymes, vendors, rules, screening, risk_advisories, sop_templates).
- `adapter_configurations`: per-adapter version + configuration hash (IO, biology, screening, vendor, SnapGene, LLM).
- `external_database_versions`: REBASE version, NCBI taxonomy version, GenBank format version, SO term version.
- `sop_template_content_hashes`: per-template content hash.
- `locale`, `timezone`, `units`.
- `seeds`: random seeds used by stochastic components.
- `container_image_digest`: if running in Docker, the image digest.
- `user_overrides`: any rule disables, threshold modifications, or custom catalogue entries.
- `reviewer_decisions`: hashes of all DecisionRecords in the session.
- `profile_hashes`: AuthorisationProfile content hashes.
- `screening_trust_policy_version`.
- `plugin_package_hashes`: per-plugin content hash.
- `llm_prompt_template_versions`: per-prompt version + content hash.
- `institutional_policy_version`: deployment-level policy hash.
- `redaction_policy`: which fields are redacted in exported bundles (for IP / PII protection).

The combined SHA-256 of the canonicalised JSON is the bundle's reproducibility hash.

## SM-D.10 CI gate code-level snippets

The `no-self-authorisation-check` gate is implemented in `tools/ci/no_self_authorisation_check.py` and statically asserts that:

- No call to `AuthorisationStore.grant` accepts a principal whose `SecurityRole != Administrator | Developer`.
- No HTTP endpoint accepts an `AuthorisationProfile` mutation from a user-bearer token.
- The `AuthorisationBootstrapPort` is used only at system bootstrap.

The `no-passive-advisory-bypass-check` gate (in `tools/ci/no_passive_advisory_bypass_check.py`) asserts:

- The `operational_protocol_gate` requires a corresponding `RiskAdvisoryAcknowledged` event for every `caution` / `strong_caution` advisory in the `RiskAdvisoryReport`.
- There is no code path from `validate_construct` to `OperationalProtocolAuthorised` that bypasses the acknowledgement step.

These static gates are how the Toolkit enforces the architectural invariants at compile time, not just at runtime.

---

# Supplementary Material E - Index by topic

**Antibiotic concentrations** see Appendix Part 2.8, App. K Marker entries, SM-B.1.

**Assembly chemistries** see § 3.2.6, Part 4.2, App. I.4-I.6.

**Audit trail** see § 3.10, App. K Audit log, SM-D.8.

**Authorisation** see § 3.7, § 3.9, App. K Authorisation Profile, SM-D.10.

**BR-16 manual SnapGene cross-check** see § 3.3.3, § 5.1.1, App. M.5, SM-A worked examples.

**Cassette anatomy** see § 1.2.

**Catalogues** see § 3.5, App. A.9, App. F.5, SM-D.3-D.5.

**Codon optimisation** see App. G.5, App. H.7, SM-D.1.3.

**Construct graph** see § 1.1.3, § 3.4, App. K, SM-D.2.

**CRISPR / Cas9** see Part 2.9, SM-A.2.

**Decision Wizard** see § 3.2.

**DesignRealisationPlan** see § 3.8, App. K, App. F.

**Export bundle** see § 3.8.

**E. coli protein expression** see Part 2.1, SM-A.1.

**Fluorescent proteins** see Part 2.7.

**Gateway** see § 3.2.6, Part 4.2.4.

**Gibson assembly** see § 3.2.6, Part 4.2.1, App. I.5, App. G.10.

**Golden Gate** see § 3.2.6, Part 4.2.2, App. I.6, App. G.11.

**Host strains** see Part 2 throughout, App. K, SM-D.3.

**IBC** see § 6.4, Part 1.4, Glossary.

**IP / licensing** see § 6.5, Appendix M.

**Lentivirus** see Part 2.6.2, SM-A.3.

**Mammalian expression** see Part 2.4, Part 2.5.

**Markers** see Part 2.8, App. K, SM-D.4.

**MS2 / VLP rules** see § 3.6, SM-C.5.

**Pichia / K. phaffii** see Part 2.3, App. I.11.

**Primers** see § 3.4 (binding sites), Part 4 (design), App. G.8.

**RBS / Shine-Dalgarno** see § 1.2.1, App. G.4.

**Restriction enzymes** see § 3.2.6, Part 4.2.3, App. G.6.

**SBOL3** see § 3.8 (export), Glossary, REQUIREMENTS.md FR-INT-09.

**Screening** see § 3.6 (verdict types), SM-D.6.

**SnapGene** see § 3.3.2, § 3.3.3, § 5.1.1, Part 6.1, App. M.5.

**Tags** see § 1.2, § 3.2.5.

**T7 promoter** see Part 2.1, App. G.3.

**Validation Report** see § 3.6, SM-C.

**Vector map** see § 3.4.

**Viral vectors** see Part 2.6.

**Yeast (S. cerevisiae)** see Part 2.2, App. I.10.

---

# Supplementary Material F - Common pitfalls observed in production

The following list summarises common pitfalls observed in real-world Toolkit deployments. Each pitfall is documented with the root cause and the corrective pattern; the list is updated as new patterns emerge.

## SM-F.1 Wizard inputs

1. **Forgetting to set the operating role on the host.** The compatibility engine's outputs change subtly if the operating role is unset (defaults to "expression"). For a producer cell line (e.g., HEK293T for lentivirus packaging), explicitly set role: producer.

2. **Treating "Other / specialised" as a fallback for "I don't know".** If you do not know the right value, ask a senior colleague rather than entering free-text that the engine cannot parse. Free-text is for cases where you know what you want but the catalogue lacks an entry.

3. **Confusing cargo source organism with host.** The cargo source organism is where the cDNA / CDS came from (e.g., *B. subtilis* for a bacterial enzyme); the host is where you will express it (e.g., *E. coli* BL21(DE3)). The Toolkit's codon optimiser uses the host's codon table, not the source's.

## SM-F.2 Validation report

4. **Skipping the INFO findings.** INFO findings are not blocking, but they document what the engine actually checked. Skipping them loses information that a reviewer or auditor would value.

5. **Acknowledging a SOFT advisory with a one-word justification.** The minimum is 20 characters; the spirit of the requirement is "a justification that another reviewer can evaluate". "OK to proceed" is technically 14 characters and would be rejected; "approved based on PMID 12345678 showing this is safe in this context" is a useful justification.

6. **Escalating instead of acknowledging when you have authority to acknowledge.** Escalation routes the construct to institutional sign-off, which can take days or weeks. Use acknowledgement when you have the role-level authority and a defensible justification.

## SM-F.3 Bench execution

7. **Ordering synthesis without re-verifying the construct.** Once the order is placed, the cost of changes is high. Re-read the sequence one more time before clicking submit.

8. **Skipping the diagnostic restriction digest.** It is tempting to go straight from mini-prep to Sanger to save time, but the digest catches gross misassemblies (wrong vector, swapped insert) before you spend $20 on a Sanger trace.

9. **Re-using a glycerol stock without re-streaking.** Glycerol stocks accumulate dead cells, contamination, and (for unstable inserts) recombination products. Re-streak on a fresh selection plate before any critical experiment.

10. **Inducing at OD600 too high.** For pET-BL21(DE3), induction at OD ~ 0.6-0.8 gives the best balance of biomass and induction efficiency. Induction at OD ~ 2 (overnight culture) often gives poor expression because the cells are in stationary phase.

## SM-F.4 QC

11. **Trusting a single Sanger primer.** For inserts > 800 bp, walk the sequence with multiple primers. A single primer can miss the 3' end where a frameshift would matter.

12. **Skipping the manual SnapGene cross-check (BR-16) because "the engine validated it".** The engine validates what it knows; the manual cross-check catches what neither the engine nor the user thought to check.

13. **Skipping post-purification SDS-PAGE.** Even high-titre expression often produces multiple species (full-length, truncated, glycoforms). Run a reducing and non-reducing gel.

## SM-F.5 Collaboration

14. **Sharing only the GenBank file with a collaborator.** Send the full export bundle; the validation report, decision records, and DerivationEnvironment hash are what make the design audit-grade.

15. **Forgetting to update the local Toolkit before re-running a past design.** Catalogue updates can change validation outcomes; re-running a months-old design with a newer Toolkit may produce different findings. Use the DerivationEnvironment hash to pin the catalogue version when you need exact reproducibility.

16. **Ignoring vendor screening verdicts because they are slow.** A vendor's screening verdict is a second layer of biosecurity review; treat HITs and WATCHLISTs seriously even if they delay the order.

---

# Supplementary Material G - Conceptual reference: foundations and design principles

This supplementary appendix is a long-form conceptual reference that supports Parts 1-2 of the manual. Concepts are introduced in pedagogical order: a wet-lab user who reads this section in sequence will end with a working understanding of why each Toolkit feature exists and where its assumptions sit in the broader science. All material is re-expressed in original language; the integration of concepts from publicly-available educational materials (including the Addgene eBook series) is performed under nominative-use editorial policy (see Appendix M).

## SM-G.1 Plasmids - foundations

### SM-G.1.1 What is a plasmid, biologically?

A plasmid is an extrachromosomal DNA molecule that replicates independently of its host's chromosome. In nature, plasmids are common in bacteria and archaea; they carry genes that are useful but not essential under all conditions (drug resistance, conjugation factors, virulence factors, metabolic add-ons). Plasmids range from tiny (~ 1 kb cryptic minicircles) to enormous (~ 1 Mb megaplasmids).

For molecular cloning, the relevant plasmids are engineered: a defined backbone with a tractable origin of replication, an antibiotic-selection marker, and a multiple cloning site for inserting cargo. These engineered plasmids are descended from a small number of natural ancestors (most famously, ColE1 from *E. coli* and pSC101 from *S. enterica*) but have accumulated decades of engineering modifications.

The two minimal functional elements every working plasmid must have are:

1. **An origin of replication (ori)** — the DNA element from which replication initiates. The ori determines which hosts the plasmid can replicate in (its host range) and how many copies per cell the plasmid maintains (its copy number).

2. **A selection marker** — usually a gene encoding an enzyme that detoxifies an antibiotic, or (in yeast) an enzyme that complements an auxotrophic deficiency. Selection ensures that cells carrying the plasmid have a growth advantage over cells that have lost it.

Add a multiple cloning site (MCS) and you have a working cloning vector. Add a promoter, RBS / Kozak, optional tag, terminator, and you have a working expression vector.

### SM-G.1.2 Origin of replication and copy number

The mechanism of replication initiation determines copy number. ColE1-derived origins (used in pUC, pBR322, pBluescript) initiate replication through a primer RNA (RNA II) that, after processing by RNase H, primes DNA synthesis by DNA polymerase I. The frequency of initiation is regulated by an antisense RNA (RNA I) and, in pBR322 derivatives, by the protein Rop / Rom. Strains with the rop / rom locus deleted (the pUC family) lose this negative regulation and reach 500-700 copies per cell rather than ~ 25 for the parental pBR322.

Other classes of origin:

- **p15A** (pACYC family): a separate compatibility group; 10-15 copies per cell.
- **pSC101**: a low-copy theta-type origin; 5 copies; ideal for cloning toxic genes.
- **F (Mini-F)**: 1-2 copies per cell; used for large constructs that would be unstable at high copy.
- **R6K (gamma origin)**: requires the pi protein; useful for conditional replication in pir+ strains.
- **2-mu (yeast)**: a high-copy autonomously-replicating yeast plasmid origin; 20-200 copies per cell; segregates well by partition system.
- **CEN/ARS (yeast)**: combines a centromere (CEN) with an autonomously-replicating sequence (ARS); 1-2 copies per cell; segregates as a mini-chromosome.
- **OriV (broad-host-range plasmids)**: IncP, IncQ origins for *Pseudomonas*, *Agrobacterium*, and other proteobacteria.

The Toolkit's host catalogue annotates each strain's compatibility with each ori family; the validation engine flags incompatible ori-host pairs.

### SM-G.1.3 Selection markers in depth

Beyond the brief catalogue in Part 2.8, several functional points matter for routine cloning:

- **Mechanism of resistance** influences how reliably the marker selects. Antibiotic-degrading enzymes (beta-lactamase for Amp, chloramphenicol acetyl-transferase for Cm) degrade the antibiotic from the medium, eventually allowing satellite colonies of plasmid-lacking cells to grow nearby once enough antibiotic has been destroyed. Efflux pumps (TetA) and antibiotic-binding proteins (Sh ble for Zeocin) protect only the cells that carry them.

- **Working concentration depends on medium**. Zeocin is inactivated by high NaCl; this is why Zeocin plates use low-salt LB (NaCl <= 5 g/L). Tetracycline is light-sensitive; tetracycline plates must be stored in the dark. Chloramphenicol is hydrophobic and is dissolved in ethanol; plate even-spreading requires care.

- **Working concentration depends on host**. Hygromycin works at very different concentrations in bacteria (~ 200 ug/mL), in yeast (~ 200-300 ug/mL for HphMX dominant), and in mammalian cells (50-500 ug/mL). The Toolkit's markers catalogue carries host-specific concentration blocks.

- **Counter-selection** is a powerful technique. URA3 in yeast can be counter-selected by 5-FOA, which kills cells carrying functional URA3; this is the basis of marker-recycling strategies for serial gene manipulation. Sucrose-sensitive markers (sacB) are used in *Bacillus* counter-selection. The Toolkit's catalogue annotates counter-selection options where they exist.

### SM-G.1.4 Vector backbones - lineages

Every modern plasmid backbone descends from a small number of foundational vectors. Knowing the lineage helps interpret features:

- **pBR322 lineage**: pBR322 (4361 bp, Amp + Tet, ColE1 ori); pUC18 / pUC19 (high-copy ColE1 + Amp + lacZ-alpha for blue / white screening); pBluescript (T7 / SP6 promoters flanking MCS); pET series (T7 promoter for *E. coli* expression).

- **pACYC lineage**: pACYC177 (Amp + Kan, p15A); pACYC184 (Tet + Cm, p15A). Used when you need multiple plasmids in one cell with different selections.

- **pSC101 lineage**: pSC101 (5 copies); pBeloBAC11 (single-copy F-derived bacterial artificial chromosome); pCC1FOS (fosmid).

- **pRS series (yeast)**: pRS41x (CEN/ARS, low-copy); pRS42x (2-mu, high-copy); pRS40x (integrating, no origin). Each comes in four marker variants (HIS3 / TRP1 / LEU2 / URA3) for combinatorial complementation.

- **pcDNA family (mammalian)**: pcDNA3.1 (CMV, Amp+Neo); pcDNA4 (CMV, Amp+Zeo); pcDNA5/FRT (CMV, Hygro, FRT for Flp-In stable lines).

The Toolkit's parts catalogue carries the canonical sequence for each foundational backbone; user designs typically derive from these.

## SM-G.2 Expression - foundations

### SM-G.2.1 Why "expression" is harder than "cloning"

Cloning a sequence into a plasmid is a structural task: cut, paste, verify the structure. Expressing the cargo as a functional product is a functional task: the host's transcription, translation, folding, and modification machinery must process the cargo correctly. A clone that is structurally perfect can express poorly because the host cannot fold the protein, because the codons clash with the host's tRNA pool, because the promoter is silenced in the chosen cell type, because the protein is degraded by host proteases, or for many other reasons.

The Toolkit catches most structural issues at design-time; functional issues often require iterative bench optimisation. Part 5.4 (Appendix J) is the canonical decision tree for that iteration.

### SM-G.2.2 Transcription in bacteria

Bacterial RNA polymerase (RNAP) consists of a core enzyme (alpha2 beta beta' omega) plus a sigma factor that confers promoter specificity. The major sigma factor in *E. coli* is sigma-70, which recognises -10 (TATAAT) and -35 (TTGACA) hexamers separated by 17 bp.

For heterologous expression, two strategies dominate:

1. **Use a strong sigma-70 promoter** like trc or tac (which combine the -35 of trpA and the -10 of lacUV5 for higher strength than either alone). Induction is via IPTG, which binds LacI and prevents it from binding to lacO.

2. **Use a foreign RNA polymerase** like T7 RNAP. The T7 promoter is recognised by T7 RNAP only (not by host RNAP); T7 RNAP is highly processive and produces large amounts of transcript. This is the pET / BL21(DE3) system: BL21(DE3) carries a chromosomal copy of T7 RNAP under lacUV5 control; IPTG induces T7 RNAP, which then transcribes the pET-borne cargo.

The T7 system has a known issue: leaky basal expression in the absence of IPTG (because lacUV5 is not perfectly tight). This is the reason for the pLysS / pLysE add-on (encodes T7 lysozyme, which inhibits T7 RNAP) and for the Lemo21(DE3) system (rhamnose-controlled T7 lysozyme allows fine-tuning of T7 RNAP activity per Wagner 2008 PMID 18369191).

### SM-G.2.3 Translation in bacteria

Bacterial translation requires:

- A Shine-Dalgarno (SD) sequence, typically 6-8 nt upstream of the start codon. The SD base-pairs with the 3' end of the 16S rRNA (sequence ACCUCCU in *E. coli*). Stronger SDs (closer to the consensus AGGAGG) initiate translation more efficiently.

- A start codon (ATG, GTG, or TTG; ATG is the strongest in *E. coli*).

- An open reading frame to the stop codon.

The mRNA secondary structure around the RBS can occlude the SD; mRNA with low GC near the SD generally translates more efficiently. The Toolkit's `RbsCalcV2Adapter` (when configured) wraps the Salis lab RBS calculator to predict translation initiation rate; advisory `MR-RBS-OCCLUDED` fires when occlusion is detected.

The Anti-Shine-Dalgarno occlusion check has become a routine concern in heterologous expression: a CDS that codes for a "normal" protein in its native organism may inadvertently contain an internal SD-like sequence that recruits the ribosome to a downstream methionine, producing a truncated product. The Toolkit flags this with `MR-INTERNAL-SD`.

### SM-G.2.4 Transcription in eukaryotes

Eukaryotic transcription uses three RNA polymerases: Pol I (rRNA), Pol II (mRNA + most ncRNAs), Pol III (tRNA + 5S rRNA + small RNAs including U6 snRNA). Heterologous protein expression uses Pol II promoters; CRISPR sgRNAs are usually expressed from Pol III U6 (or H1) promoters.

Pol II promoters have a basal core (typically a TATA box at ~ -25 + an initiator) and enhancer elements that can be hundreds of kb away. For ectopic expression, compact "minimal promoter + enhancer" cassettes are used:

- **CMV** is a strong constitutive promoter assembled from the human cytomegalovirus immediate-early region (Boshart 1985 PMID 2999983). Limitations: silenced over passages in some lines, particularly in CHO and embryonic stem cells.

- **CAG** combines the CMV enhancer with the chicken beta-actin promoter and the rabbit beta-globin intron (Niwa 1991 PMID 1660837). Stronger than CMV in many lines and more silencing-resistant.

- **EF1alpha** uses the human elongation factor 1-alpha promoter. Strong, broadly active, often more silencing-resistant than CMV.

- **PGK** (phosphoglycerate kinase) is medium-strength, broadly active, and famously reliable across cell types — often used for selection markers where moderate expression suffices.

- **UBC** (ubiquitin C) is broadly active and silencing-resistant.

For inducible expression in mammalian cells:

- **Tet-On / Tet-Off** systems use a tetracycline-responsive promoter (TRE) and the rtTA / tTA trans-activator. Doxycycline induces (Tet-On) or represses (Tet-Off).

- **Hormone-responsive promoters** (glucocorticoid, mineralocorticoid) for endocrine cell biology.

### SM-G.2.5 Translation in eukaryotes

Eukaryotic translation initiation is cap-dependent in most cases:

1. eIF4F (cap-binding complex) recognises the 5' m7G cap of the mRNA.
2. The 43S pre-initiation complex (small ribosomal subunit + initiator Met-tRNA + initiation factors) is recruited.
3. The complex scans 5' -> 3' until it encounters a start codon in a strong context.
4. The 60S subunit joins, forming the 80S ribosome; translation begins.

The Kozak consensus (gccRccATGG, R = A or G; Kozak 1986 PMID 3839802) defines the strong context. The most critical positions are:

- Position -3 (a purine, ideally A or G).
- Position +4 (G).

A start codon in a strong Kozak context out-competes a downstream weaker-context start; this is what suppresses leaky scanning to internal methionines. The Toolkit's `KozakScorer` (configurable adapter) emits a strength score and a categorical label; `MR-KOZAK-WEAK` fires below threshold.

Cap-independent translation is possible via Internal Ribosome Entry Sites (IRES; long viral RNA elements like EMCV IRES, HCV IRES) or via 2A peptides (short self-cleaving sequences from picornavirus family: T2A, P2A, F2A, E2A; produce two proteins from a single ORF by ribosomal skipping). The Toolkit's polycistronic cargo type supports both.

### SM-G.2.6 Polyadenylation and termination in eukaryotes

A eukaryotic mRNA needs a 3' polyadenylation signal for nuclear export, stability, and translation efficiency. The canonical signal is AATAAA (or its variant ATTAAA), located ~ 10-30 nt upstream of the cleavage / polyadenylation site. The Toolkit's `MR-POLYA-MISSING` advisory flags absence.

Standard polyA signals used in expression vectors:

- **bGH polyA**: bovine growth hormone polyA, ~ 220 bp; widely used in pcDNA family.
- **SV40 late polyA**: ~ 240 bp; widely used.
- **rabbit beta-globin polyA**: less common but compact.
- **HSV TK polyA**: used in some retroviral vectors.

## SM-G.3 Fluorescent proteins - design principles

### SM-G.3.1 The GFP family - chemistry

The original GFP from *Aequorea victoria* (Shimomura 1962; Prasher 1992 cloning; Chalfie 1994 heterologous expression) carries a chromophore formed by autocatalytic cyclisation and oxidation of three amino acids (Ser-Tyr-Gly at positions 65-67) within the protein's beta-barrel scaffold. The reaction does not require enzymes or cofactors beyond molecular oxygen.

Modern FPs are descended from GFP, DsRed (from *Discosoma sp.*), and a small number of other coelenterates / corals. Key engineering goals:

- **Monomerise** the natural dimers / tetramers (mCherry was the first widely-used monomeric red FP).
- **Brighten** by improving folding efficiency and quantum yield.
- **Shift colours** by mutations near the chromophore.
- **Improve photostability** for live imaging.
- **Reduce blinking** for single-molecule applications.

### SM-G.3.2 Modern FP family - recommendations by application

The Toolkit's catalogue carries the following recommended FPs by application:

- **Live-cell imaging (best signal-to-noise)**: mScarlet-I (red), mNeonGreen (green-yellow), mTurquoise2 (cyan), iRFP670 / iRFP713 (NIR for deep tissue).

- **Fluorescent fusion (functional protein retained)**: monomers only (mScarlet, mNeonGreen, mTurquoise2, EGFP, mCherry); avoid DsRed (tetramer) and avGFP wild-type (weak dimer).

- **FACS / cell sorting**: mNeonGreen or EGFP (matches 488 laser); mCherry or mScarlet (matches 561 laser); iRFP (matches 633 / 640 lasers, but lower brightness).

- **Multi-channel imaging (4-channel)**: mTurquoise2 + mNeonGreen + mScarlet + iRFP670.

- **FRET donor/acceptor**: mTurquoise2 (donor) + mVenus / YPet (acceptor) for high-dynamic-range FRET.

### SM-G.3.3 Design considerations

- **Linker between cargo and FP**: GGSGG (short flexible) or (GGGGS)2/3 (long flexible) work for most fusions. Rigid (EAAAK)n is for cases where you need to physically separate the cargo and FP (e.g., to avoid mutual interference).

- **Position of the FP**: usually C-terminal, because most proteins tolerate a C-terminal tag better than an N-terminal one. Exceptions: secreted proteins (signal peptide must remain N-terminal); proteins where the C-terminus is the active end (e.g., GPCR cytoplasmic tail with downstream PDZ-binding motif — fuse N-terminal in this case).

- **Avoid stop codons in the cargo**: a stop codon in the cargo terminates translation before the FP, producing a cargo-only product. The Toolkit's `MR-INFRAME-STOP` catches this.

## SM-G.4 Viral vectors - design principles in depth

### SM-G.4.1 Why use a virus to deliver DNA?

Transfection (chemical or physical introduction of DNA into a cell) is straightforward for cell lines (HEK293, CHO, HeLa) but fails or is highly inefficient for many important targets: primary cells (especially neurons), terminally-differentiated cells, slow-growing or contact-inhibited cells, and intact tissue in vivo. Viral vectors exploit a virus's natural ability to bind cell-surface receptors, enter the cell, and deliver its genome to the nucleus.

The trade-off is biosafety. Replication-competent viruses are dangerous; modern viral vectors are engineered to be replication-incompetent by splitting the viral genes onto separate plasmids that are present only in the producer cell. The recombinant virus produced is one-shot: it delivers its cargo to the target cell but cannot reproduce there.

### SM-G.4.2 Lentivirus design and packaging (third-generation)

The third-generation lentivirus system (Dull 1998 PMID 9765382) is the current standard for safety. The key engineering moves:

1. **Split the viral genome across three or four plasmids**: a transfer vector carrying the cargo, a packaging plasmid encoding the packaging functions (Gag-Pol-Rev-Tat in psPAX2), and an envelope plasmid (typically pMD2.G encoding VSV-G for broad tropism). No single plasmid encodes a complete virus.

2. **Self-inactivating (SIN) LTRs**: a deletion in the U3 region of the 3' LTR (which becomes the 5' LTR after integration) destroys the U3 promoter activity, preventing transcription from the integrated LTR. This both improves safety (cannot drive expression of adjacent genes after integration) and improves cassette expression (the internal promoter is dominant).

3. **Heterologous 5' promoter**: the 5' LTR's U3 promoter is replaced by a heterologous promoter (CMV or RSV) for the transfer vector; this allows the packaging cell to make the RNA without LTR activity.

4. **Removal of Tat**: by replacing Tat-dependent transcription with a Tat-independent heterologous promoter, the system removes the need for Tat in the packaging.

The Toolkit's lentivirus rules check for: cargo size budget (8 kb between LTRs), psi packaging signal presence, RRE, cPPT (helps nuclear import), WPRE (boosts expression and titres), SIN LTR integrity, and absence of polyA signals upstream of WPRE (which would truncate the genome).

Lentiviral integration is largely random (with a bias toward transcribed genes); insertional mutagenesis is a known risk for clinical use, mitigated by SIN designs and by using non-integrating lentiviral vectors (mutated integrase) where possible.

### SM-G.4.3 AAV design and packaging

AAV is the dominant gene-therapy vector for non-integrating delivery. Key facts:

- **Cargo size**: 4.7 kb single-stranded (the ITRs occupy ~ 145 bp each, leaving ~ 4.4 kb for cargo); for self-complementary AAV (scAAV), the cargo is half-sized but expression onset is faster.

- **Serotype matters**. AAV2 is the historical workhorse; AAV9 has broad tropism for CNS / heart; AAV-DJ is engineered for broad in-vitro tropism; AAV6 prefers muscle; AAV-PHP.B / PHP.eB cross the blood-brain barrier in C57BL/6 mice.

- **The ITRs are AAV2-derived** in most modern protocols, regardless of which capsid serotype is used. ITRs are notoriously unstable in *E. coli* (they form hairpins that recombine); cloning AAV plasmids should be done in Stbl3 or NEB-Stable cells.

- **Production** is via triple-transfection of HEK293T with the transfer vector + pRep-Cap (matching the chosen serotype) + pHelper (adenoviral helper functions: E2A, E4, VA RNA). Yields are usually 10^11-10^13 vector genomes per 15-cm dish.

The Toolkit's AAV rules check ITR presence (and flag for manual SnapGene cross-check because ITR sequence integrity is critical), cargo size against the packaging limit, and serotype-specific notes.

### SM-G.4.4 Adenovirus and retrovirus

Adenovirus offers larger cargo capacity (~ 37 kb in gutted forms) and high-titre transient transduction without integration; production is more demanding than lentivirus / AAV (requires plaque purification or column chromatography). Used clinically for vaccines (including COVID-19 vaccines from Janssen, AstraZeneca, CanSino) and for some gene-therapy applications.

Retrovirus (gammaretrovirus, MMLV-derived) was the original mammalian transduction system and is still used in some contexts (e.g., the original CD19 CAR-T constructs). Now largely superseded by lentivirus because lentivirus transduces non-dividing cells and has a slightly better safety profile.

## SM-G.5 CRISPR - design principles in depth

### SM-G.5.1 The CRISPR-Cas9 system

CRISPR-Cas9 (Cong 2013 PMID 23287718; Mali 2013 PMID 23287722; Ran 2013 PMID 24157548) is an RNA-guided DNA endonuclease system adapted from a bacterial adaptive immunity system. The minimal components for genome editing in eukaryotes:

1. **Cas9 nuclease** (most commonly SpCas9 from *Streptococcus pyogenes*, ~ 160 kDa, recognises NGG PAM).
2. **Single guide RNA (sgRNA)**: a chimeric tracrRNA-crRNA carrying a 20-nt protospacer complementary to the target.
3. **A target DNA site** of the form [20-nt protospacer][NGG PAM].

When Cas9 binds the sgRNA and finds the target, it makes a blunt double-strand break (DSB) ~ 3 nt upstream of the PAM. The cell then repairs the DSB via either non-homologous end joining (NHEJ; error-prone; produces indels that knock out the gene) or homology-directed repair (HDR; templated; allows knock-in of cargo when an HDR template is provided).

### SM-G.5.2 Guide design

Critical considerations:

- **Target uniqueness**: the protospacer should be unique in the target genome (or have only mismatches at the seed region near the PAM). Off-target prediction tools (CRISPOR, GuideScan, Cas-OFFinder) score guides; the Toolkit integrates these via configured adapters.

- **PAM availability**: SpCas9 requires NGG; for genes lacking nearby NGG, use SpCas9-VRER, SpCas9-VQR, or different Cas variants (SaCas9 with NNGRRT, Cpf1 with TTTV).

- **GC content**: 40-60% generally works well; very high or very low GC reduces activity.

- **Distance from start codon**: for knockouts via NHEJ, guides near the 5' end of the coding region produce more reliable loss-of-function alleles.

- **High-fidelity Cas variants**: eSpCas9, SpCas9-HF1, HiFi-Cas9 reduce off-target activity at the cost of slightly reduced on-target activity.

### SM-G.5.3 HDR template design

For knock-in via HDR:

- **Homology arm length**: 30-60 nt for ssODN (small insertions, point mutations); 500-1000 bp for dsDNA (larger insertions like fluorescent-protein knock-ins).

- **PAM-disrupting mutations**: the HDR template should differ from the genomic sequence at the PAM (so that the repaired locus is not re-cut). Silent codon changes are ideal because they preserve the protein sequence. If the PAM falls in a coding region, change the third base of the codon containing the PAM's last G to A (NGG -> NGA in DNA, but the codon is silent).

- **Symmetric vs asymmetric arms**: for dsDNA templates, symmetric arms are conventional; for ssODN, asymmetric (longer 3' arm complementary to the released strand at the cut site) is often more efficient (Richardson 2016).

- **Knock-in efficiency** is often low (5-20% in unselected cell populations); use selection (puro / blast) or FACS-sortable cargo (GFP) to enrich correctly-edited cells.

### SM-G.5.4 CRISPR plasmid families

- **pX330**: SpCas9 + sgRNA backbone (no selection); from Cong / Zhang lab (Addgene #42230).
- **pX458**: pX330 + GFP for FACS sorting (#48138).
- **lentiCRISPR v2**: lentiviral vector with SpCas9 + sgRNA + Puro (#52961); used for genome-scale screens.
- **lentiGuide-Puro + lentiCas9-Blast**: split system (Cas9 stably expressed in cells; sgRNAs delivered separately).
- **pX552 / pX601**: SaCas9 versions for AAV packaging (smaller, fits in AAV cargo).
- **pY016 / pY009**: Cpf1 / Cas12a versions.

## SM-G.6 Antibody design in depth

### SM-G.6.1 Antibody structure overview

A standard IgG antibody is a Y-shaped tetramer: two heavy chains (~ 50 kDa each) and two light chains (~ 25 kDa each), held together by disulfide bonds. Each chain has variable (V) and constant (C) regions; the V regions of one heavy + one light pair form the antigen-binding site (the Fab fragment); the C regions of the two heavy chains form the Fc region that mediates effector functions.

For research and pre-clinical antibody work, the common formats are:

- **scFv (single-chain variable fragment)**: V_H linked to V_L (or V_L to V_H) by a flexible (GGGGS)3 linker; minimal antigen-binding unit; expresses well in bacteria (sometimes), reliably in eukaryotes.

- **Fab**: V_H + C_H1 (the Fd fragment) plus light chain (V_L + C_L); two chains held together by an interchain disulfide; ~ 50 kDa total; expresses in eukaryotes; structurally closer to a natural antibody.

- **Full IgG**: two heavy chains (V_H + C_H1 + C_H2 + C_H3) + two light chains; ~ 150 kDa total; mediates effector functions through Fc; only expresses well in mammalian cells (HEK293, CHO).

### SM-G.6.2 Vector design choices

- **Two-vector vs single-vector**: two separate vectors (one HC, one LC) are easier to construct individually and allow flexible ratio optimisation; single bicistronic vectors (HC-IRES-LC or HC-2A-LC) ensure 1:1 stoichiometry in every cell.

- **Codon optimisation for the host**: for HEK293 / CHO, use the human or Chinese hamster codon table. Native immunoglobulin V regions often use unusual codons; the Toolkit's codon optimiser handles this routinely.

- **Signal peptide**: native immunoglobulin signal sequence works well; alternatives include human IL-2 signal peptide (commonly used in pFUSE vectors).

- **Constant region**: human IgG1 is the default; IgG2 or IgG4 if you want to reduce effector function; murine IgG2a for murine systems.

### SM-G.6.3 Production cell lines

- **Expi293F**: a HEK293-derived suspension line, optimised for transient transfection at high density (3-5 x 10^6 cells/mL). Yields 10-100 mg/L of secreted antibody in a 5-7 day shake-flask culture. Good for small-batch research production.

- **CHO-K1 / CHO-S / CHO-DG44**: the industrial standard. Stable lines yield 1-5 g/L in fed-batch bioreactors; transient yields are lower than Expi293F but the product is more representative of the eventual stable-line product.

### SM-G.6.4 Purification

The canonical workflow is Protein A (for IgG1) or Protein G (for broader IgG subclasses) affinity capture from the cleared supernatant, low-pH glycine elution, immediate neutralisation with 1 M Tris pH 9.0, buffer exchange to storage buffer (PBS or histidine), and SEC polishing. Final QC includes SDS-PAGE (reducing + non-reducing), SEC analytical, endotoxin (if downstream is cell-based), and functional binding (ELISA, BLI, SPR).

---

# End of manuscript

This is the canonical end of the First Edition of the Cloning & Expression Vector Design Toolkit User Guide. The manuscript covers:

- 6 layered reading paths for different user roles.
- Front matter with full glossary (~ 120 terms in short-form; long-form definitions in Appendix K).
- 6 chapters (Parts 1-6) covering orientation, common wet-lab needs, Toolkit walkthrough, bench execution, QC and troubleshooting, and collaboration.
- 13 appendices (A-M) covering installation, inputs, process steps, checklists, FAQ, architecture, fundamental science, formulas, standard protocols, troubleshooting tables, glossary expansion, references with PMIDs, and IP / licensing.
- 7 supplementary materials (SM-A through SM-G) with worked examples, cheat sheets, warning reference, deep technical reference, topic index, common pitfalls, and conceptual foundations.

For corrections, suggestions, or contributions, open an issue in the repository's issue tracker. The manual will be updated alongside Toolkit releases; subsequent editions will track the version number on the title page.

(c) 2026 General Molecular Expression Service Pty Ltd. GPL-3.0-only. GMExpression(R) registered trademark. Research Use Only.

---















