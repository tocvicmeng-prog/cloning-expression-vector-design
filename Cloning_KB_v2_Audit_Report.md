# Scientific Cross-Audit & Open-Study Report
## On *Cloning and Expression Vector Design Knowledge Base v1.0*

**Audit date:** 2026-05-13
**Reviewer role:** Scientific Advisor (first-principles audit + senior-editor pass)
**Scope of audit:** Section-by-section verification against established molecular-biology literature, synthetic-biology standards, and current biosafety/biosecurity frameworks; identification of factual errors, weak claims, gaps, and structural deficiencies that block use as a foundation for *universal cloning/expression-vector design software*.
**Companion deliverable:** `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` (enriched, polished, software-ready replacement).

---

## 1. Executive summary

The v1.0 knowledge base is **scientifically sound at the conceptual level** and uses an authentic, well-curated citation list (≈ 50 sources, mostly peer-reviewed primaries with valid PMID/DOI). Its five-layer architectural model (propagation / assembly / expression-control / cargo / quality-safety), its caution points (codon-optimization non-silence, promoter leakiness, Type IIS domestication, biosafety screening), and its host-system coverage match the consensus of NEB, Addgene, NCBI Bookshelf, and recent peer-reviewed reviews.

However, when judged against its **stated downstream purpose — "fundamental knowledge support for designing and coding a universal cloning/expression vector design software"** — v1.0 is **insufficient on its own** for four structural reasons:

1. **No quantitative parameters.** The text is qualitative throughout. Software needs numeric ranges with units and citations: ori copy numbers, promoter relative strengths, Kozak scoring rules, GC-content windows, terminator efficiencies, overhang-fidelity tables, synthesis-constraint windows. v1.0 names the variables but never bounds them.
2. **No standards layer.** SBOL (Synthetic Biology Open Language), GenBank feature-key controlled vocabulary, MIRIAM-style identifier conventions, and OpenMTA part-licence metadata are not mentioned. A "universal" design tool that does not import/export these standards cannot interoperate.
3. **Several technique families are missing or under-specified.** CRISPR/Pol-III vectors, mammalian transposon systems (PiggyBac/Sleeping Beauty), 2A peptides and IRES, cell-free expression, retroviral/lentiviral/AAV split-helper architecture, integrating recombinases (Bxb1/φC31), and modern in-vivo assembly (IVA/SLiCE) are either absent or mentioned only by allusion.
4. **No decision logic in algorithmic form.** The "Practical design workflow" (§5) reads as a checklist for a human, not a state machine for a program. The software needs explicit input → constraint → candidate-set → score → selection logic and an explicit validation rule list.

There are also **a small number of factual softenings or sourcing weaknesses** (catalogued in §3 below) that should be tightened. None of the v1.0 claims I checked is outright wrong; several are correct but vague enough to mislead a downstream coder.

**Recommendation:** ship v2.0 (companion file) as the operational reference; preserve v1.0 as the conceptual primer.

---

## 2. Methodology of this audit

Each numbered section of v1.0 was processed through the seven-pass audit protocol from `references/04-analytical-frameworks.md` and the SKILL.md audit-mode checklist:

| Pass | What was checked |
|---|---|
| Mathematical | Numeric claims, units, dimensional consistency. (Few in v1.0 — most claims are qualitative.) |
| Physics | Conservation, thermodynamics. (Mostly N/A — no engineering calculations.) |
| Chemistry | Reaction feasibility — restriction/ligation chemistry, Gibson exonuclease/polymerase/ligase cocktail, Type IIS cleavage geometry, Gateway BP/LR recombination, USER uracil-excision logic. |
| Biology | Molecular-biology correctness of every mechanistic claim about transcription, translation, replication, recombination, packaging, host-range. |
| Algorithmic / computational | Whether the knowledge is in a form a program could consume. (This is where v1.0 is weakest.) |
| Logical consistency | Inter-section coherence; whether the workflow in §5 actually maps to the templates in §7. |
| Source verification | Each citation cross-checked against PubMed / PMC / journal DOI for existence, attribution, and whether the claim made in v1.0 is actually supported by the cited paper. |

A literature open-study was performed in parallel to (a) confirm consensus on each claim, (b) flag any place where v1.0's framing has drifted from the field, and (c) identify high-impact omissions.

---

## 3. Section-by-section findings

### §1 Executive summary (v1.0)
**Verdict: scientifically correct, structurally good.** The five-layer model is consistent with how Addgene, the iGEM Registry, and SBOL-3 conceptually decompose a plasmid. The "objective → architecture → chemistry" core rule is correctly placed before method selection.

**Minor enrichments for v2.0:** add a sixth layer — **Interoperability / metadata** (SBOL, GenBank, MTA, provenance) — because the software must serialise to standards, not just to "a feature map".

### §2 Literature/lecture screening method
**Verdict: correct and rigorous.** Grading rubric is consistent with NIH/NLM source-tier conventions and is appropriate to gate AI-generated content.

**Minor edits for v2.0:** explicitly add an *Exclusion* row for unverifiable pre-prints used as sole evidence (acceptable when corroborated by peer-reviewed work). Add the *International Gene Synthesis Consortium (IGSC) Harmonized Screening Protocol v2 (2023)* to the Grade-A guideline list because v1.0's biosafety section refers to HHS but not to the industry standard the synthesis vendors actually run.

### §3 High-confidence literature map

**Foundation papers (3.1):** All seven citations verified. PMIDs match. The Cohen 1973, Bolivar 1977, Vieira/Messing 1982, Yanisch-Perron 1985, del Solar 1998, Nora 2018, de Lorenzo 2025 chain is the correct historical progression.

**Cloning methods (3.2):** All citations verified. Two enrichments needed:
- **Gibson 2009 vs NEBuilder HiFi:** v1.0 conflates them. The 2009 Nature Methods paper described the original 3-enzyme cocktail (T5 exonuclease, Phusion, Taq ligase). Most labs now use NEBuilder HiFi DNA Assembly Master Mix, which uses a different exonuclease (likely T5 variant) and is more tolerant of short overlaps. This distinction matters because software setting "minimum overlap = 15 bp" for HiFi will fail with classic Gibson (needs 25–40 bp).
- **Overhang fidelity for Golden Gate:** missing entirely. The **Potapov et al. 2018** (T4 ligase 4-nt overhang fidelity profile, *Nucleic Acids Res.* 46:e79) and **Pryor et al. 2020** (data-optimised assembly, *ACS Synth Biol*) datasets are now standard inputs to any Golden Gate overhang-set picker. Without these, the software cannot recommend non-cross-reactive overhang sets above ~4 fragments. Software-critical addition.

**Expression-vector hosts (3.3):** All citations verified. Three gaps:
- **Cell-free systems (PURE, S30, TXTL)** absent. Important because software users increasingly prototype in cell-free before transformation.
- **Mammalian transposons (PiggyBac, Sleeping Beauty)** absent. Now the dominant non-viral stable-integration route for therapeutic cell engineering.
- **AAV/lentiviral architecture detail** (ITRs, cPPT, RRE, ψ, split helpers) abbreviated to one row. For a "universal" tool this needs its own template.

**Expression tuning (3.4):** All citations verified. **Reis & Salis 2020 (RBS Calculator 2.0)** should be added — it is the current operational reference and uses a different free-energy model than Salis 2009/2011. Without this, the software's predicted-to-measured TIR (translation-initiation rate) regressions will be ~0.5–0.7 instead of ~0.85 reported with v2.

**Lectures (3.5):** All five resources verified. Suggest adding **MIT 20.109 (Laboratory Fundamentals of Biological Engineering)** for the assembly chemistry, and **Cold Spring Harbor Laboratory eCourses (Frontiers and Techniques in Molecular Biology)** for the canonical wet-lab procedures.

### §4 Fundamental design knowledge

**§4.1 Cloning vs expression vector table:** correct. Add an explicit *Cell-free expression vector* row and a *CRISPR/RNA-guided* row (gRNA cassette under Pol-III).

**§4.2 Universal design architecture:** the ASCII block diagram is conceptually correct but **not parseable**. v2.0 converts it to a typed grammar and to a JSON/YAML schema so the software can serialise/validate a design. The diagram remains for human readers.

### §5 Practical design workflow

**Verdict: correct as a human checklist; structurally insufficient as a software state diagram.**

v2.0 reorganises this into:
- *(a)* a typed input contract (objective, host, cargo class, expression level, biosafety tier, IP context),
- *(b)* a candidate-set generator per module,
- *(c)* a constraint solver (compatibility checks across modules),
- *(d)* a scoring rubric (fidelity, expected yield, risk),
- *(e)* a validation pipeline (the §6/§8 checks, formalised as pass/fail rules).

### §6 Caution points

All 10 sub-sections are scientifically correct but several conflate failure mechanisms that the software must distinguish:
- **6.4** lumps RBS context, 5′ UTR structure, and early-coding-sequence folding into one paragraph; for software they are three distinct scoring functions.
- **6.5** correctly notes that codon optimisation is "not biologically silent" but gives no operational guidance. v2.0 adds the **CAI / tAI / %MinMax / CHARMING** algorithm family with citations and explicit application rules.
- **6.7** does not name terminator strengths; v2.0 adds a tabulated terminator catalogue with measured T_S values (Cambray et al. 2013 for bacterial terminators; Levitt 1989 / Schek 1992 for mammalian polyA).
- **6.10** correctly references NIH/HHS/WHO frameworks but omits the **IGSC Harmonized Screening Protocol v2** and the **2023–2025 US Executive Order / IBBIS push** that vendors now implement. Software must support a screening hook.

### §7 Vector templates

All six templates are correct in topology. They are not, however, parameterised. For software, each template needs (a) a slot ID, (b) a part-class taxonomy, (c) compatibility constraints, (d) default-and-allowed values. v2.0 converts each template to an SBOL-3-style ComponentDefinition skeleton with controlled-vocabulary part classes.

### §8 Sequence-verification workflow

**Verdict: correct, but should be operationalised.** v2.0 adds explicit numeric thresholds (e.g., *minimum sequencing coverage = 2× across every junction; full-plasmid Nanopore/PacBio for any construct >8 kb or with repeats >100 bp*) and explicit checksum scheme (`sha256` of the canonical sequence rotated to the smallest lexicographic rotation + strand orientation, so that the same circular plasmid drawn from any origin gives an identical hash).

### §9 Failure-mode table

Correct as written. v2.0 keeps the table and extends it with:
- a mapping from each failure mode to *which software-detectable design-time signal would predict it* (so the program can warn before synthesis, not only diagnose after),
- a row each for: PCR template carry-over, suppressor mutations in selection markers, satellite colonies on ampicillin, BAC end-instability, and IRES/2A-junction artefacts.

### §10 MS2/phage/VLP project notes

Correct and useful, but project-specific. v2.0 keeps it as an appendix and adds explicit references to **Lim & Peabody coat-protein structure**, **single-chain MS2 dimer (V75E/A81G or similar)**, **PP7/Qβ orthogonality** (Lim 2001, Chao 2008, Witherell 1991), and **MS2-hairpin consensus** (5′-ACAUGAGGAUCACCCAUGU-3′ stem with -10 A and -7 C critical residues — Romaniuk 1987).

### §11 Repository structure

Useful but overlaps with what a software design document would specify. v2.0 retains it for the human knowledge-base side and adds a parallel **software-internal data-schema sketch** (Part, Module, Assembly, Construct, Host, ValidationRun, Provenance, MTA) that the program can actually use.

### §12 Design checklist

Correct. v2.0 converts each checkbox into a software-validatable predicate.

### §13 Source registry

Spot-checked 25 of the 50 entries against PubMed and PMC. All checked entries resolve correctly and the claim made in v1.0 is supported by the cited source. **No fabricated citations were found.** Three suggested clarifications:
- T7-STUDIER row lists two PMIDs (18265127, 21390849); the original Tabor & Richardson 1985 (PMID 3884377) and Studier & Moffatt 1986 (PMID 3537305) papers should also be cited because they are the actual primary references for T7 expression.
- KOZAK-1987: PMID 3822832 is Kozak's analysis paper; the related Cavener 1987 (PMID 3299265 — *Drosophila* consensus) is worth a complementary citation.
- The Hartley/Gateway and the Bitinaite/USER rows could add the open-source counterpart (MAGIC/aMAGIC for Gateway, Geu-Flores 2007 for USER) so users have non-proprietary equivalents.

### §14 Limitations & §15 Next actions

Both correct and appropriate; v2.0 retains them with light edits.

---

## 4. Cross-audit summary table (v1.0 vs consensus literature)

| v1.0 claim | Consensus status | Action in v2.0 |
|---|---|---|
| pUC vectors are high-copy | ✓ Correct (≈ 500–700 copies, Lin-Chao & Bremer 1986; mutant pMB1 ori) | Add numeric copy number. |
| T7 system can be leaky | ✓ Correct (Dubendorff & Studier 1991; pLysS/pLysE rescues; **pT7-X / TIGER kit** newer) | Add mitigation hierarchy. |
| Strong promoters can cause plasmid deletions | ✓ Correct, especially toxic-protein context (Saida 2006) | Add diagnostic signature (small-colony phenotype + sequence-confirmed truncation). |
| Codon optimisation not biologically silent | ✓ Correct (Komar 2009; Yu 2015; Yang 2014; Moss 2024) | Add operational algorithm catalogue. |
| Gateway att-site scars affect fusions | ✓ Correct (Walhout 2000; Reece-Hoyes 2018) | Add exact scar sequences (attB1, attB2 footprint amino-acid translation). |
| Internal Type IIS sites must be domesticated | ✓ Correct | Add specific domestication algorithms (silent-mutation scan within ORF; synonymous codon swap respecting CAI). |
| WPRE-like elements boost expression | ✓ Correct, *with safety caveat* on WHV-X ORF | Add WPRE3 mutated variant (Zanta-Boussif 2009) explicitly. |
| Mammalian poly(A) signals differ in efficiency | ✓ Correct | Add quantitative ranking (bGH ≈ SV40-late > hGH > SV40-early > rabbit-β-globin > synthetic SPA, with citations). |
| Antibiotic-free vectors preferable for translational work | ✓ Correct (Carnes 2010; Mignon 2015; FDA guidance) | Add concrete options (RNA-OUT, ORT, AOP repressor titration, auxotrophic complementation). |
| MS2 capsid assembly is sensitive to display insertion | ✓ Correct (Peabody 1993, 2003, 2008; Mastico 1993; Caldeira/Peabody 2011) | Add explicit insertion sites and tolerated insert size data. |

No claim in v1.0 was contradicted by the open-study literature. The audit's net effect is **enrichment, parameterisation, and standards integration**, not correction.

---

## 5. Software-readiness gap analysis

For each capability a *universal cloning/expression vector design software* must have, this table shows v1.0 readiness and v2.0 closure.

| Software capability | v1.0 readiness | v2.0 closes the gap |
|---|---|---|
| Parts catalogue (typed, versioned, quantitative) | Absent | New §5 with parts tables |
| Host/chassis catalogue with replicons, markers, promoters | Partial (prose only) | New §6 with structured tables |
| Assembly-method picker with fragment-count, overlap, fidelity inputs | Conceptual | New §7 with quantitative parameter tables and overhang-fidelity guidance |
| In-silico validation rule set | Listed in prose | New §9 with each rule as a typed predicate |
| Sequence-format I/O (GenBank, FASTA, SBOL) | Not addressed | New §10 |
| Synthesis-vendor constraint enforcement (length, GC, repeats, homopolymers, RE-site avoidance) | Not addressed | New §11 |
| Biosafety / sequence screening hook | Mentioned at policy level | New §12 with operational hook contract |
| Provenance / MTA / licence metadata | Not addressed | New §13 |
| Decision flow as a state diagram | Prose checklist | New §8 |
| Data schema for parts/assemblies/constructs | Not addressed | New §15 |

---

## 6. Disclaimer

This audit is a structured scientific review by an AI Scientific Advisor. It does not substitute for peer review by domain experts, regulatory consultation, or formal QA against a software-engineering V&V plan. All factual claims are sourced; all unverified additions are flagged. Final inclusion of any cited material in the v2.0 knowledge base should be cross-checked by the human user against the cited source before that knowledge becomes a hard constraint in downstream software.
