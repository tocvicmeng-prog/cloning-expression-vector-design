# Cloning and Expression Vector Design Knowledge Base — v2.0

**Prepared:** 2026-05-13
**Prepared by:** Scientific Advisor (open-study + cross-audit revision of v1.0)
**Supersedes:** *Cloning and Expression Vector Design Knowledge Base v1.0* (kept as conceptual primer)
**Companion document:** *Cloning_KB_v2_Audit_Report.md* (section-by-section audit of v1.0 → v2.0 changes)
**Downstream purpose:** fundamental knowledge support for designing and coding a **universal cloning / expression vector design software**.
**Safety scope:** conceptual vector-design guidance only. No step-by-step wet-lab protocols, no culture conditions, no transformation procedures, no viral-production parameters, no operational dual-use guidance. All biosafety statements defer to current institutional and governmental frameworks (NIH, HHS, WHO, IGSC).

---

## Table of Contents

1. Executive summary
2. Source authenticity rules and open-study method
3. High-confidence literature & lecture map
4. Universal six-layer design architecture
5. Standard-parts catalogue (quantitative)
6. Hosts/chassis catalogue (quantitative)
7. Assembly methods — quantitative parameters and fidelity data
8. Design decision logic — software-mappable flow
9. In-silico validation rules — parametric predicates
10. Sequence formats and interoperability standards
11. DNA synthesis vendor constraints
12. Biosafety and sequence-screening framework
13. Provenance, MTA, and metadata
14. Parameterised vector templates
15. Software-internal data schema sketch
16. Failure modes, design-time predictors, and corrective actions
17. Project-specific appendix: MS2 / phage / VLP vector design
18. Source registry
19. Limitations and disclaimer

---

## 1. Executive summary

A cloning or expression vector is best modelled as a **controlled engineering system** assembled from typed, interchangeable parts in six interacting layers:

1. **Propagation layer.** Origin(s) of replication, copy-number control, host range, plasmid stability, selectable marker(s), and bacterial verification primer sites.
2. **Assembly layer.** Multiple cloning site, Type IIS acceptor cassette, homology arms, recombination sites, negative-selection cassette, or other scarless-assembly interface.
3. **Expression-control layer.** Promoter / enhancer / operator, ribosome-binding site or Kozak context, 5′/3′ UTRs and introns, transcriptional terminator or polyadenylation signal, inducibility, and insulation from backbone context.
4. **Cargo layer.** ORF / cDNA / gRNA / structural-RNA cassette / protein-domain assembly, codon strategy, fusion tags, localisation signals, cleavage sites, linkers, stop-codon strategy, and domain boundaries.
5. **Quality / safety layer.** Sequence provenance, feature annotation, sequencing-primer coverage, restriction / Type IIS audit, biosafety classification, synthetic-nucleic-acid sequence screening, antibiotic-resistance risk, and reproducibility records.
6. **Interoperability / metadata layer.** *(New in v2.0.)* SBOL-3 serialisation, controlled-vocabulary feature keys (GenBank / SO), MIRIAM-style identifiers, material-transfer-agreement licence, version/checksum, design provenance graph.

**Core design rule.** *Choose vector architecture from the experimental objective, host system, and biosafety tier first; then choose cloning chemistry.* Many failed vector projects fail because the assembly method was chosen before the biological requirements were defined.

**Audit verdict.** v1.0 was conceptually correct and authentically sourced; v2.0 preserves that conceptual frame and adds the quantitative, parametric, standards-aware, and decision-logic content required to drive software. No v1.0 claim was found to be wrong against the open-study literature.

---

## 2. Source authenticity rules and open-study method

### 2.1 Source-grade rubric

| Grade | Accepted source type | How it is used |
|---|---|---|
| **A1** | Primary peer-reviewed paper indexed by PubMed / PMC, with verified PMID and DOI | Main evidence for methods, vector architecture, expression systems, and historical origins. |
| **A2** | Official guideline document: NIH OSP, HHS/ASPR, WHO, IGSC, IBBIS, NCBI Bookshelf, FDA, EMA | Authoritative definitions, safety frameworks, screening standards. |
| **A3** | Authoritative open educational resource: MIT OpenCourseWare, Cold Spring Harbor Laboratory eCourses, EMBO Practical Courses | Educational/lecture authority; used for pedagogy and cross-checking definitions. |
| **B1** | Peer-reviewed review article indexed by PubMed / PMC | Used for synthesis and caution points; not used as sole authority for sequence identity or numeric parameter. |
| **B2** | Repository reference page from an authoritative non-profit (Addgene, iGEM Registry, JBEI ICE, AddGene Plasmids 101, OpenMTA) | Used for vendor-neutral practical definitions; cross-checked against primaries. |
| **C** | Pre-print on bioRxiv / arXiv (or reputable vendor page) | Used only when corroborated by a peer-reviewed source; never as sole authority. |
| **Excluded** | Student notes, unverified lecture mirrors, social-media posts, AI-generated summaries, undated PDFs without institutional provenance | Not used. |

### 2.2 Open-study search themes (executed for v2.0)

- Plasmid foundations: pSC101, pBR322, pUC, M13, origin-of-replication families (ColE1, pMB1, p15A, pSC101, R6K, RK2, pBBR1, F-factor / BAC, 2µ, CEN/ARS, SV40 ori, EBV oriP).
- Classical and modern cloning: restriction/ligation, Gibson / NEBuilder HiFi, Golden Gate / MoClo / Loop / YTK / GreenGate / GoldenBraid / JUMP / MIDAS, Gateway, LIC/SLIC, USER, IVA, in-vivo assembly in *S. cerevisiae* and *B. subtilis*.
- Expression-vector architecture: bacterial (E. coli T7/T5/trc/lac/ara/rhamnose), mammalian (CMV, EF1α, CAG, PGK, UBC, tissue-specific, Tet-On/Off), yeast (GAL1, TEF1, PGK1, ADH1, GAP, AOX1), insect/baculovirus, plant binary, archaeal, cell-free (PURE, S30, TXTL).
- Expression tuning: RBS Calculator v2 (Reis & Salis 2020), Kozak context, IRES, 2A peptides, terminators (Cambray 2013), polyadenylation signals (Levitt 1989, Schek 1992), WPRE / WPRE3, insulators (cHS4, A2UCOE).
- Cargo design: codon-optimisation algorithms (CAI, tAI, %MinMax, CHARMING, RCA), affinity/solubility/localisation tags, protease-cleavage sites, linker biophysics, signal peptides, integrating-recombinase landing pads (Bxb1, φC31), CRISPR gRNA scaffold variants.
- Standards and interoperability: SBOL 3 (Buecherl 2023), GenBank/feature-key controlled vocabulary, Sequence Ontology, MIRIAM identifiers, OpenMTA, FreeGenes.
- Quality and safety: IGSC Harmonized Screening Protocol v2 (2023), HHS Synthetic-Nucleic-Acid Screening Framework, IBBIS proposals, NIH Guidelines (Apr 2024), WHO Laboratory Biosafety Manual 4th ed, EU GMO Directive 2001/18 and Directive 2009/41 (contained use).
- Project-specific phage/VLP: MS2 coat-protein structure (Peabody / Witherell / Romaniuk lineage), single-chain MS2 dimer, PP7 and Qβ orthogonality, modular display ports (SpyTag/SpyCatcher, SnoopTag/SnoopCatcher, sortase A, click).

---

## 3. High-confidence literature and lecture map

*(All citations resolved against PubMed/PMC. PMIDs and DOIs given where available. The full source registry is in §18. This section summarises the lessons; the registry holds the references.)*

### 3.1 Foundations

| Source | Lesson |
|---|---|
| Cohen, Chang, Boyer & Helling, *PNAS* 1973 (PMID 4594039) | Restriction-cut plasmid fragments can be joined in vitro and propagated as functional replicons — the founding logic of recombinant DNA. |
| Bolivar et al., *Gene* 1977 (PMID 344137) | pBR322 — defined ori, two antibiotic markers, compact backbone, unique restriction sites. |
| Vieira & Messing, *Gene* 1982 (PMID 6295879); Yanisch-Perron, Vieira & Messing, *Gene* 1985 (PMID 2985470) | pUC/M13 — high-copy ori (mutant pMB1), polylinker, blue/white α-complementation. |
| del Solar et al., *Microbiol. Mol. Biol. Rev.* 1998; del Solar & Espinosa, *Mol. Microbiol.* 2000 (PMID 10931343) | Plasmid copy number is regulated by replicon-specific mechanisms; ori is a design variable. |
| Nora et al., *Microb. Biotechnol.* 2018 (PMC6302727); de Lorenzo, *Microb. Biotechnol.* 2025 (PMC12703808) | Vector engineering integrates host, payload, copy number, marker, transfer mode, and host genetic context. |

### 3.2 Cloning / assembly methods

| Method | Primary citations |
|---|---|
| Restriction/ligation | Cohen 1973; MIT OCW 7.01SC and 7.016 lectures; NCBI Bookshelf "Recombinant DNA". |
| Gibson assembly | Gibson et al., *Nat. Methods* 2009 (PMID 19363495, DOI 10.1038/nmeth.1318). |
| NEBuilder HiFi | NEB product documentation; no discrete peer-reviewed primary reference equivalent to Gibson 2009. Practical-parameter source therefore graded C, used only with quantitative caution. |
| Golden Gate / Type IIS | Engler et al., *PLoS ONE* 2008 (PMID 18985154); Engler et al., *PLoS ONE* 2009 (PMID 19436741); Weber et al., *PLoS ONE* 2011 (PMID 21364738); Bird et al., *ACS Synth. Biol.* 2022; **Potapov et al., *ACS Synth. Biol.* 2018 (PMID 30335370)** — comprehensive 4-nt overhang fidelity; **Pryor et al., *PLoS ONE* 2020 (PMID 32877448)** — data-optimised assembly design, demonstrated up to 35 fragments in one pot; underpins NEB Ligase Fidelity Viewer ("FideliT4"). |
| MoClo kits | YTK (Lee et al., *ACS Synth. Biol.* 2015, PMID 25871405); Plant MoClo Tool Kit (Engler et al., *ACS Synth. Biol.* 2014); GreenGate (Lampropoulos et al., *PLoS ONE* 2013, PMID 24376629); GoldenBraid 2.0 (Sarrion-Perdigones et al., *Plant Physiol.* 2013, PMID 23669743); Loop assembly (Pollak et al., *New Phytol.* 2019, PMID 30521109); JUMP (Valenzuela-Ortega & French, *Synth. Biol. (Oxford)* 2021, PMID 33623824); MIDAS (van Dolleweerd et al., *ACS Synth. Biol.* 2018, PMID 29620866). |
| Gateway | Hartley et al., *Genome Res.* 2000 (PMID 11076863); Katzen 2007; Reece-Hoyes & Walhout 2018 (PMID 29295908). Open-source counterpart: MAGIC (Li & Elledge 2005). |
| LIC | Aslanidis & de Jong, *Nucleic Acids Res.* 1990 (PMID 2235490). |
| SLIC | Li & Elledge, *Nat. Methods* 2007 (PMID 17293868). |
| USER | Bitinaite et al., 2007 (PMID 17341463); open-source: Geu-Flores et al. 2007 (PMID 17726050). |
| IVA / in-vivo *E. coli* assembly | García-Nafría et al., *Sci. Rep.* 2016 (PMID 27464723) — uses bacterial endogenous recombination to assemble PCR fragments without in-vitro enzymes. |
| Yeast TAR / homologous recombination | Kouprina & Larionov, *Nat. Protoc.* 2008 (PMID 18388946). |

### 3.3 Expression-host systems

| Host | Anchor references |
|---|---|
| **E. coli** | Studier & Moffatt, *J. Mol. Biol.* 1986 (PMID 3537305); Tabor & Richardson, *PNAS* 1985 (PMID 3884377); Dubendorff & Studier, *J. Mol. Biol.* 1991 (PMID 2002519); Mierendorf pET system; Francis & Page 2010 (PMID 20814932); Shilling et al., *Commun. Biol.* 2020. |
| **Cell-free (PURE, S30, TXTL)** | Shimizu et al., *Nat. Biotechnol.* 2001 (PMID 11479568) PURE system; Garamella et al., *ACS Synth. Biol.* 2016 (PMID 26925207) TXTL myTXTL; Sun et al., *J. Vis. Exp.* 2013 (PMID 23995540). |
| **Mammalian transient/stable** | Boshart et al., *Cell* 1985 (CMV); Foecking & Hofstetter 1986; Niwa et al., *Gene* 1991 (CAG); Kozak, *Cell* 1986 (PMID 3943125); Kozak, *NAR* 1987 (PMID 3313277); Cavener, *NAR* 1987; Pfarr et al. *DNA* 1986 (PMID 2872023); Loeb et al. 1999 (WPRE); Zanta-Boussif et al., *Gene Ther.* 2009 (WPRE3, PMID 19262615); Schambach et al., *Gene Ther.* 2006 (mutated WPRE, PMID 16355114); Qin et al. 2010 (PMID 20485554); Norrman et al. 2010 (PMID 20865041). |
| **Mammalian transposons** | PiggyBac: Wilson et al., *Mol. Ther.* 2007 (PMID 17387335); Sleeping Beauty: Ivics et al., *Cell* 1997 (PMID 9390559); Tol2: Kawakami 2007. |
| **Yeast** | Vernet et al., *Gene* 1987 (PMID 3038686); Mumberg et al., *Gene* 1995 (PMID 7737504); Sikorski & Hieter, *Genetics* 1989 (pRS vector series, PMID 2659436). |
| **Insect/baculovirus** | Jarvis 2009 (PMID 19892174); Chambers et al., 2018 (PMID 29516481); Felberbaum, *Biotechnol. J.* 2015. |
| **Plant binary** | Bevan, *Nucleic Acids Res.* 1984 (PMID 6095209); Komari et al., 2006 (PMID 16988331). |
| **Phage / VLP** | Peabody, *J. Biol. Chem.* 1993 and *Vaccine* 2003; Caldeira & Peabody, *PLoS ONE* 2011; Mastico et al., *J. Gen. Virol.* 1993; Lim & Peabody, *Nucleic Acids Res.* 2002. |
| **Viral vectors (AAV / Lentivirus)** | Grimm & Kay 2003 (AAV); Naldini et al., *Science* 1996 (lentivirus); Dull et al., *J. Virol.* 1998 (3rd-gen lentiviral split helper, PMID 9811723). |

### 3.4 Expression tuning, cargo, and tags

| Topic | Anchor references |
|---|---|
| Bacterial RBS prediction | Salis et al., *Nat. Biotechnol.* 2009 (PMID 19801975); Salis, *Methods Enzymol.* 2011 (PMID 21601672); **Reis & Salis, *ACS Synth. Biol.* 2020 (PMID 33054181)** — RBS Calculator v2.0 trained against 9,862 characterised systems; Urtecho et al., *eLife* 2020 / Reg-Seq (PMID 32955431); Kosuri et al., *PNAS* 2013 (PMID 23924614) — composability of regulatory parts. |
| Bacterial promoter strengths | Davis et al., *Nucleic Acids Res.* 2011 (insulated promoters); Cambray et al., *Nucleic Acids Res.* 2013 (terminator library); Kosuri et al., *PNAS* 2013 (combinatorial promoter–RBS). |
| Kozak / mammalian initiation | **Kozak, *Cell* 1986 (PMID 3943125)** — original definition; Kozak, *Nucleic Acids Res.* 1987 (PMID 3313277) — consensus `GCCRCCAUGG` from 699 vertebrate mRNAs; Cavener & Ray, *Nucleic Acids Res.* 1991 (cross-species consensus refinement); **Noderer et al., *Mol. Syst. Biol.* 2014 (PMID 25170020)** — FACS-seq quantification of −6…+5 contexts giving the quantitative Kozak PWM (optimal context = RYMRMVAUGGC); Diaz de Arce et al., *Genome Res.* 2020 (PMID 32669370) — initiation downstream of annotated starts. |
| 2A peptides | **Kim et al., *PLoS ONE* 2011 (PMID 21602908)** — primary comparative study in HEK293T / zebrafish / mouse establishing **P2A > T2A > E2A > F2A** efficiency order; Szymczak-Workman et al., *Cold Spring Harb. Protoc.* 2012 (PMID 22301656) — vector design and GSG-linker recommendation; Liu et al., *Sci. Rep.* 2017 (PMID 28526819) — systematic comparison; Chng et al., *MAbs* 2015 (PMID 25621616) — CHO context. |
| IRES | Pelletier & Sonenberg, *Nature* 1988 (PMID 2839778); Borman et al. 1997. |
| Fusion/affinity tags | Young et al. 2012 (PMID 22442034); Kimple et al. 2013; Costa et al. 2014; Köppl et al. 2022. |
| Protease cleavage | TEV: Kapust & Waugh 2000; PreScission/3C: Cordingley et al. 1990; Thrombin, Factor Xa: classic. |
| Codon optimisation algorithms | Sharp & Li, *Nucleic Acids Res.* 1987 (CAI); dos Reis et al. 2004 (tAI); Clarke & Clark, *PLoS ONE* 2008 (%MinMax); Jacobs & Shakhnovich 2017 (CHARMING). Cautions: Mauro & Chappell 2014; Bali & Bebok 2015; Moss et al. 2024. |
| Codon-context / co-translational folding | Komar 2009 (PMID 19460601); Yu et al., *Cell Rep.* 2015 (PMID 25554914). |

### 3.5 Standards and interoperability

| Standard | Reference |
|---|---|
| **SBOL (Synthetic Biology Open Language)** | Galdzicki et al., *Nat. Biotechnol.* 2014 (SBOL 2.0); Madsen et al. 2019; Buecherl & Myers 2023 (SBOL 3). https://sbolstandard.org |
| **Sequence Ontology** | Eilbeck et al., *Genome Biol.* 2005 (PMID 15892872). |
| **GenBank feature keys (controlled vocabulary)** | NCBI/EMBL-EBI/DDBJ "Feature Table Definition" (current revision). |
| **OpenMTA** | Kahl et al., *Nat. Biotechnol.* 2018 (PMID 30188547) — open material-transfer agreement framework. |
| **iGEM Registry / FreeGenes / JBEI ICE** | Community-curated parts catalogues; provide UID schemas for parts. |

### 3.6 Authentic teaching resources

| Resource | Use |
|---|---|
| MIT OCW 7.01SC "Basic Mechanics of Cloning" | Restriction-enzyme logic, DNA ligase, recombinant-DNA fundamentals. |
| MIT OCW 7.016 "Recombinant DNA, Cloning, & Editing" | Vector/insert terminology and cloning logic. |
| MIT 20.109 (BE Lab) | Assembly chemistry, primer design, troubleshooting. |
| NCBI Bookshelf "Studying DNA" and "Recombinant DNA" | Educational basis. |
| Addgene Plasmids 101 and Molecular Biology Reference | Practical part-class definitions. |
| Cold Spring Harbor Laboratory eCourses, *Frontiers and Techniques in Molecular Biology* | Canonical wet-lab procedures. |
| NEB *Foundations of Molecular Cloning* (with primary references) | Practical historical overview. |

---

## 4. Universal six-layer design architecture

### 4.1 Human-readable diagram

```text
[1. Propagation module]
    ori(s) + selectable marker(s) + copy-number control + host range

[2. Assembly module]
    MCS  |  Type IIS acceptor  |  Gateway interface  |  LIC/SLIC/USER tail
    + optional negative-selection cassette (ccdB / sacB)

[3. Expression-control module]
    promoter / enhancer / operator
    + (bacterial) RBS / 5′ spacer
    + (eukaryotic) Kozak / 5′ UTR / optional intron
    + insulators if needed

[4. Cargo module]
    ORF | RNA cassette | gRNA | domain assembly
    + N-tag / linker / signal peptide / cleavage site
    + C-tag / localisation signal
    + explicit stop-codon strategy

[5. Termination module]
    bacterial terminator | eukaryotic poly(A) + terminator
    + WPRE or other PTRE if justified

[6. Verification & metadata module]
    universal primer sites + sequence checksum + feature annotation +
    SBOL/GenBank serialisation + biosafety classification + MTA/licence
```

### 4.2 Typed-grammar form (for software)

```
Construct          ::= PropagationModule  AssemblyModule  ExpressionModule  CargoModule  TerminationModule  MetadataModule
PropagationModule  ::= Origin  Marker  CopyControl?  HostRange
AssemblyModule     ::= ( MCS | TypeIIS_Acceptor | Gateway_Interface | LIC_Tail | USER_Tail )
                       NegativeSelection?
ExpressionModule   ::= Promoter  Operator?  ( RBS_Spacer | Kozak_5UTR_Intron? )  Insulator?
CargoModule        ::= ( Tag_N? Linker? )  ORF  ( Linker? Tag_C? )  StopStrategy
TerminationModule  ::= ( BacterialTerminator | PolyA Terminator? )  PTRE?
MetadataModule     ::= ProvenanceID  Checksum  FeatureTable  SBOL_Record  Biosafety  Licence
```

A given vector is a partial assignment of values to these slots; the software's job is to validate consistency among them (§9) and, where the user underspecifies, to propose candidate values (§8).

---

## 5. Standard-parts catalogue (quantitative)

*Numeric values cite primary literature where available; values flagged as "ranges in the field" reflect typical reported values across multiple peer-reviewed sources and should be treated as estimates rather than constants.*

### 5.1 Origins of replication

| Origin family | Typical host | Copy number / cell | Notes |
|---|---|---|---|
| **ColE1** (pBR322) | *E. coli* and close relatives | 15–20 | Narrow host range. RNA-II / RNA-I antisense control. |
| **pMB1 mutant** (pUC) | *E. coli* | 500–700 | Mutation in RNA-I/II destabilises copy-number control → high copy. |
| **p15A** | *E. coli* | 10–12 | Compatible with ColE1 — co-transformable. |
| **pSC101** (and *repA*-controlled derivatives) | *E. coli* | ≈ 5 | Low copy; stable for large or toxic inserts. |
| **R6K (γ-origin)** | *E. coli* (π+ strains only, e.g. *pir-116*) | 15–20 (π-dependent) | Requires host-supplied Π protein; used for suicide/conditional vectors. |
| **RK2 / RP4** | broad Gram-negative host range | 4–7 | Broad host; mobilisable; biosafety scrutiny advised. |
| **pBBR1** | broad Gram-negative host | 10–30 | Compatible with most other replicons. |
| **F-factor (BAC)** | *E. coli* | 1–2 | For inserts up to ≈ 300 kb; ParA/ParB partitioning. |
| **pSC101 *par-***| *E. coli* | 5 | Stable inheritance of large or repetitive constructs. |
| **2µ** | *S. cerevisiae* | 30–50 | Episomal multi-copy. |
| **CEN/ARS** | *S. cerevisiae* | 1–2 | Centromeric, single-copy, mitotically stable. |
| **SV40 ori (+ Large T-Ag)** | mammalian (COS, HEK293T) | episomal, transient amplification | Transient only. |
| **EBV oriP (+ EBNA1)** | mammalian (293F, CHO, lymphoid) | episomal, stable | Multi-month maintenance without integration. |
| **AAV ITR (host-independent flanking)** | mammalian (with AAV capsid) | n/a (template) | 145-nt ITRs flank cargo; episomal in non-dividing cells. |
| **HIV LTR (+ Ψ + cPPT/CTS + RRE)** | mammalian (with packaging) | integrated, ~1–5 copies / cell | Self-inactivating (SIN) 3′ LTR ΔU3 standard since Dull 1998. |

*References:* Lin-Chao & Bremer 1986 (pUC copy); del Solar 1998 (general); Bowers 2004 (RK2); Friehs 2004 (E. coli plasmid copy); Sikorski & Hieter 1989 (CEN/ARS); Dull et al. 1998 (SIN lentivirus).

### 5.2 Selectable markers

| Marker | Working concentration (typical) | Host | Notes |
|---|---|---|---|
| **ampicillin (bla, β-lactamase)** | 50–100 µg/mL liquid; 100 µg/mL plate | *E. coli* | Satellite colonies; secreted resistance hydrolyses ampicillin → selection erodes. Carbenicillin (50 µg/mL) more stable. |
| **kanamycin (neo / aph-3′)** | 25–50 µg/mL | *E. coli*; mammalian (G418, 0.4–1 mg/mL active) | Intracellular resistance; no satellite. |
| **chloramphenicol (cat)** | 25–34 µg/mL | *E. coli* | Bacteriostatic; works with low-copy origins. |
| **tetracycline (tetA/tetR)** | 10–15 µg/mL | *E. coli* | Inducer of *tet* expression in some contexts. |
| **spectinomycin / streptomycin (aadA)** | 50–100 µg/mL | *E. coli*; plant transgenic | Common for plant binary. |
| **gentamicin (aacC1)** | 10–15 µg/mL | *E. coli*; mammalian (50–400 µg/mL) | Used in Agrobacterium binary vectors. |
| **zeocin (sh ble)** | 25 µg/mL bacteria; 50–500 µg/mL mammalian | bacteria, yeast, mammalian | Cross-kingdom; light-sensitive. |
| **hygromycin B (hph)** | 200 µg/mL bacteria; 100–600 µg/mL mammalian | bacteria, mammalian | Mammalian stable selection. |
| **puromycin (pac)** | n/a bacteria; 0.5–10 µg/mL mammalian | mammalian | Rapid death (2–4 d). |
| **blasticidin (bsr)** | n/a bacteria; 2–25 µg/mL mammalian | mammalian | Slower than puromycin. |
| **G418 / Geneticin (neo)** | n/a bacteria; 200–1000 µg/mL mammalian | mammalian | Slow kinetics (7–14 d). |
| **Auxotrophic markers** | n/a | yeast (URA3, LEU2, HIS3, TRP1, LYS2, ADE2), bacteria | Antibiotic-free; require auxotrophic host. |
| **Antibiotic-free (RNA-OUT, ORT)** | n/a | *E. coli* | sucrose / SacB counter-selection; sacB+ replaced by RNA-OUT in NTC vectors (Williams 2009; Carnes 2010; Mignon 2015). |
| **ccdB (negative selection)** | n/a | *E. coli* (gyrA462 strain DB3.1 / Survival 2) | Gyrase poison; used in Gateway destination vectors. |
| **sacB (sucrose-induced negative selection)** | 5–10% sucrose | *E. coli*, *B. subtilis*, mycobacteria | Cell death on sucrose due to levansucrase activity. |

### 5.3 Bacterial promoters (with relative strengths)

*Relative strengths refer to steady-state transcription of a downstream reporter under standard conditions; absolute strengths depend on host, RBS, growth phase, and 5′-coding folding. Use only as starting estimates.*

| Promoter | Inducer / regulation | Relative strength (T7=1.0) | Notes |
|---|---|---|---|
| **T7** | T7 RNAP (typically λDE3 lysogen + IPTG → lacUV5 → T7 RNAP) | 1.0 (reference) | Orthogonal to host RNAP; very strong; leaky → use pLysS/pLysE or T7 lysozyme co-expression, or BL21 Star, or pT7-X. |
| **T7lac** (T7 with downstream lac operator) | + IPTG, + repressor titre | 0.7–1.0 | Lower leak than bare T7. |
| **trc (trp-lac hybrid)** | + IPTG | 0.3–0.5 | Uses host σ⁷⁰. |
| **tac** | + IPTG | 0.3–0.5 | Similar to trc. |
| **lacUV5** | + IPTG | 0.05–0.1 | Weak; useful when low-level expression desired. |
| **araBAD / pBAD (AraC)** | + L-arabinose 0.0002–0.2% | 0.05–0.5 (tunable) | Glucose represses (catabolite); tight, tunable. |
| **rhaBAD (RhaR/RhaS)** | + L-rhamnose 0.1–0.4% | 0.1–0.3 | Very tight; tunable. |
| **tetA (TetR)** | + anhydrotetracycline (aTc) 10–100 ng/mL | 0.1–0.5 | Tight; aTc less affected by TetR variants than tetracycline. |
| **λpL/pR (cI857ts)** | heat induction 42 °C | 0.5–1.0 | Temperature-controlled; heat stresses host. |
| **σ³² heat-shock (htpG, ibpA)** | heat stress | tissue-specific | For stress-coupled expression. |
| **constitutive Anderson series (BBa_J231xx)** | constitutive | spans 3 orders of magnitude | iGEM standard reference promoters. |
| **proD / proC / proB synthetic constitutive (Davis 2011)** | constitutive | tunable, insulated | Insulator-flanked → low context-dependence. |

### 5.4 Eukaryotic promoters

| Promoter | Host range | Relative strength | Notes / silencing risk |
|---|---|---|---|
| **CMV (HCMV IE)** | mammalian broad | high (≈ 1.0 reference in 293T; *very variable* across lines) | Strong in HEK293T; weak in MRC5, MSCs, and most stem-cell contexts. Methylation-sensitive; silenced in >95 % of differentiated cells (Norrman 2010). |
| **EF1α (full intronic)** | mammalian broad | 0.6–1.0 | **Most stable promoter across pluripotent + differentiating cells** (Norrman 2010); preferred for stable iPSC/ESC and primary lines. |
| **CAG (CMV-IE/β-actin/β-globin chimeric)** | mammalian broad | 1.0–1.5 | Strongest in many *in vivo* contexts; large element (~1.6 kb); silenced in differentiating ES/iPS (Norrman 2010). |
| **PGK (phosphoglycerate kinase)** | mammalian broad | 0.2–0.4 | Modest constitutive; resists silencing reasonably well. |
| **UBC (ubiquitin C)** | mammalian broad | 0.1–0.3 (Qin 2010) | *Weakest* of the common constitutive promoters in many lines, despite reputation; useful when modest, stable expression desired. |
| **SV40 early** | mammalian broad | 0.1–0.3 | Weak; small element. |
| **tissue-specific** | per cell type | variable | Synapsin, CaMKII, MBP, GFAP for neural; albumin for hepatic; CD68 for macrophage; cTnT for cardiac. |
| **Pol-III: U6, H1, 7SK** | mammalian | high (for short RNAs only) | Standard for shRNA/gRNA. U6 strongest in most contexts. |
| **Tet-On/Off (TRE / rtTA / tTA)** | mammalian | high (induced) | Doxycycline-controlled; tight in 3G variant. |
| **GAL1 (yeast)** | *S. cerevisiae* | high (induced by galactose) | Glucose repression. |
| **TEF1 (yeast)** | *S. cerevisiae* | strong constitutive | Reference yeast promoter. |
| **PGK1 (yeast)** | *S. cerevisiae* | strong constitutive | |
| **ADH1 (yeast)** | *S. cerevisiae* | strong constitutive (full); weak short version | "Long" vs "short" ADH1 differ ≥ 10×. |
| **AOX1 (Pichia/*K. phaffii*)** | yeast methylotroph | strong induced by methanol | Standard *Pichia* heterologous expression. |
| **35S (CaMV)** | plant | high constitutive | Plant default. |
| **polyhedrin / p10 (baculovirus)** | insect | very late, very strong | Standard baculovirus heterologous expression. |

*References:* **Qin et al., *PLoS ONE* 2010 (PMID 20485554)** — systematic comparison of CMV, CAG, EF1α, PGK, UBC, SV40 across multiple mammalian lines; **Norrman et al., *PLoS ONE* 2010 (PMID 20865041)** — quantitative comparison in hESC and differentiating cells; Boshart 1985 (CMV); Niwa 1991 (CAG); Mumberg 1995 (yeast); Cregg 2000 (AOX1).

### 5.5 RBS and 5′ context (bacterial)

| Element | Rule / data |
|---|---|
| Shine-Dalgarno consensus | `AGGAGG`, 6–9 nt 5′ of the start codon (Shine & Dalgarno 1974). |
| Optimal spacing | 5–13 nt between SD core and AUG; 7–8 nt is most common in *E. coli*. |
| Start codon usage (*E. coli*) | AUG ≈ 83%, GUG ≈ 14%, UUG ≈ 3% (Hecht et al. 2017). |
| Translation-initiation-rate (TIR) prediction | RBS Calculator v1 (Salis 2009, 2011); **RBS Calculator v2 (Reis & Salis 2020, PMID 33054181)** — refined biophysical model trained and validated against 9,862 characterised systems. |
| Folding energy near AUG | ΔG of (−30 … +30 nt around AUG) is strongly anti-correlated with expression; software should compute ViennaRNA RNAfold ΔG and flag ΔG < −10 kcal/mol. |
| Common engineered RBS sets | Anderson BBa_B003x series; "Elowitz" RBS; "Pfeifer" RBS-strong; custom Salis-designed RBS per construct. |
| Important caveat | RBS strength is context-dependent: changing the first ~15 codons of the ORF changes mRNA folding and thus measured expression. Software must score RBS *together with* the ORF 5′ context. |

### 5.6 Kozak and mammalian 5′ context

| Element | Rule / data |
|---|---|
| Kozak consensus | `GCCRCCAUGG` (Kozak 1986 PMID 3943125; Kozak 1987 NAR PMID 3313277); R = purine (A or G); positions **−3 (R)** and **+4 (G)** are the two dominant determinants. |
| Empirical scoring | **Noderer et al. 2014 (PMID 25170020)** — FACS-seq quantification of all −6…+5 contexts; optimal context = `RYMRMVAUGGC` (Y = C/U, M = A/C, V = G/C/A). Software should use a position-weight-matrix score rather than a binary consensus match. |
| uORF / upstream ATG | Any ATG in the 5′ UTR that is in good Kozak context will compete with the main ATG. Software must scan and flag. |
| 5′ UTR length | Mammalian 5′ UTR typically 50–300 nt; very short or very long UTRs can reduce translation. |
| 5′ cap | Provided by cellular transcription machinery from a Pol-II promoter; software does not need to encode in DNA but must reject Pol-I/Pol-III promoters when protein expression is the goal. |
| IRES (EMCV) | ≈ 588 nt; downstream cistron typically 30–70 % of cap-dependent. |
| 2A peptides (P2A > T2A > E2A > F2A) | "Self-cleaving" by ribosomal skipping; ~95–98 % for P2A (Liu et al. 2017). Furin-cleaved variants (GSG-furin-2A-) further reduce upstream protein C-terminal addition. |

### 5.7 Terminators and polyadenylation signals

**Bacterial transcription terminators** (intrinsic, ρ-independent):

| Terminator | Termination efficiency | Source |
|---|---|---|
| rrnB T1 | 0.91 | *E. coli* rRNA operon. |
| rrnB T1T2 (tandem) | 0.99+ | Standard high-efficiency bacterial terminator. |
| T7 terminator (TΦ) | 0.93 | Used in pET vectors. |
| BBa_B0015 (TT-double) | 0.98 | iGEM standard double terminator. |
| Cambray 2013 library (PMID 23275534) | spans 0.1–0.99 | Characterised library of synthetic terminators. |

**Mammalian poly(A) signals**:

| PolyA signal | Length | Relative strength | Notes |
|---|---|---|---|
| bGH poly(A) | 225 nt | 1.0 (reference) | Default for many expression vectors (pcDNA3 family). Pfarr 1986 showed ~3× advantage over SV40-early in transient transfection. |
| Rabbit β-globin poly(A) | ~ 400 nt | 0.8–1.0 | Strong; stabilises transcript; nuclease-resistant (Yew 2007). |
| Synthetic SPA | ~ 50 nt | 0.8–1.0 (when exonic) | Compact, derived from rabbit β-globin terminator (Levitt 1989); ~10× more efficient than natural rabbit β-globin site when placed exonically; strong despite small size. |
| SV40 late poly(A) | 240 nt | 0.7–1.0 | Strong; nuclease-resistant transcript (Yew 2007); commonly used in viral vectors. |
| SV40 early poly(A) | 135 nt | 0.4–0.5 | Compact; weaker than late variant. |
| hGH poly(A) | 626 nt | 0.4–0.7 | Used in Sleeping Beauty / some lentiviral vectors; ranks lower than bGH/SV40-late in modern comparative studies. |
| WPRE (PTRE, not a polyA) | 591 nt (full) / 247 nt (WPRE3) | boost 2–5× expression | WPRE wild type contains a truncated WHV-X ORF with proposed oncogenic potential (Kingsman 2005); **use WPRE3 (Zanta-Boussif 2009, PMID 19262615) or mut6 (Schambach 2006, PMID 16355114)** for therapeutic constructs to remove X-ORF translation potential. |

*References:* Pfarr et al., *DNA* 1986 (PMID 2872023); Levitt et al., *Genes Dev.* 1989 (PMID 2570734); Schek et al., *Mol. Cell. Biol.* 1992; Yew et al., *J. Gene Med.* 2007 (PMID 17407167); Kim et al., *Front. Bioeng. Biotechnol.* 2022 (PMC8819543); Kingsman et al., *Gene Ther.* 2005 (PMID 15510172).

### 5.8 Fusion / affinity / solubility / detection tags

| Tag | Size (aa) | Function class | Detection / removal | Notes |
|---|---|---|---|---|
| His6 | 6 | IMAC purification | Ni²⁺/Co²⁺ resin | Smallest broadly useful tag; can be left in for many applications. |
| His8, His10 | 8, 10 | IMAC | as above | Stronger Ni binding; useful in denaturing purification. |
| FLAG (DYKDDDDK) | 8 | epitope, anti-FLAG IP | M1/M2 antibody | M1 is calcium-dependent → mild elution. |
| HA (YPYDVPDYA) | 9 | epitope | anti-HA | Influenza HA-derived. |
| Myc (EQKLISEEDL) | 10 | epitope | anti-Myc 9E10 | |
| V5 | 14 | epitope | anti-V5 | |
| Strep-II (WSHPQFEK) | 8 | Strep-Tactin purification | desthiobiotin elution | Mild elution; high purity. |
| Twin-Strep (×2 Strep-II) | 28 | Strep-Tactin XT | biotin elution | Highest affinity. |
| AviTag (GLNDIFEAQKIEWHE) | 15 | BirA biotinylation site | streptavidin | Site-specific biotinylation in vivo or in vitro. |
| SBP | 38 | streptavidin binding | biotin elution | |
| **MBP** (maltose-binding protein) | 396 | solubility, purification | amylose resin; cleave to remove | Strong solubility enhancer; cleave for activity assays. |
| **GST** (glutathione-S-transferase) | 220 | purification, affinity | glutathione resin | Dimerises; can mask oligomerisation. |
| **SUMO** | 100 | solubility, native N-terminus on cleavage | SUMO protease (Ulp1) | Cleavage gives native N-terminus (any aa except Pro). |
| **NusA** | 495 | solubility | n/a (rarely affinity) | Strong solubility; often combined with His6. |
| **TF (trigger factor)** | 432 | solubility, chaperone | n/a | Co-translational folding helper. |
| **Trx** (thioredoxin) | 109 | solubility | n/a | For disulfide-containing proteins (with proper redox host). |
| **SNAP / CLIP / HaloTag** | 182–297 | covalent self-labelling | small-molecule probes | For imaging, pulldown. |
| **SpyTag/SpyCatcher** | 13 / 116 | covalent conjugation | isopeptide bond formation | Modular post-assembly conjugation; orthogonal: SnoopTag/SnoopCatcher, DogTag/DogCatcher. |
| **Sortase A motif (LPETG / LPETGG)** | 5–7 | enzymatic conjugation | Sortase A + Gly-nucleophile | Site-specific tagging. |

**Standard linkers**:

| Linker | Sequence | Property |
|---|---|---|
| Flexible Gly-Ser (GGGGS)_n | (GGGGS)_n | Maximum flexibility; default for single-chain fusions and tag separation; n = 1–4 typical. |
| Rigid α-helical (EAAAK)_n | (EAAAK)_n | Rigid; preserves domain spacing/orientation. |
| Mixed (GSG)_n | (GSG)_n | Compromise. |
| Cleavable: TEV | ENLYFQ↓G or ENLYFQ↓S | TEV protease; G or S after the cleavage scar. |
| Cleavable: PreScission / 3C | LEVLFQ↓GP | Removes N-terminal residues except the GP. |
| Cleavable: Thrombin | LVPR↓GS | Less specific than TEV; can cleave internal sites. |
| Cleavable: Enterokinase | DDDDK↓X | Cleaves after Lys; any aa downstream. |

### 5.9 Localisation and secretion signals

| Signal | Function | Notes |
|---|---|---|
| IgG signal peptide / IL-2 signal peptide | mammalian ER secretion | Cleaved by signal peptidase. |
| α-factor leader (S. cerevisiae) | yeast secretion | Pre-pro processing by Kex2/Ste13. |
| pelB / OmpA / DsbA | *E. coli* periplasm export | Signal-peptidase cleavage at host membrane. |
| NLS (SV40 PKKKRKV) | nuclear localisation | Classic monopartite NLS. |
| NES (HIV-Rev LPPLERLTL) | nuclear export | |
| Mito presequence (e.g. COX8) | mitochondrial matrix | Cleaved by MPP. |
| KDEL / HDEL | ER retention | C-terminal tetrapeptide. |
| GPI anchor signal | plasma membrane (GPI-anchored) | C-terminal hydrophobic. |
| Palmitoylation/myristoylation motifs | membrane attachment | Site-specific N-terminal lipidation. |

### 5.10 Reporter genes (commonly used in vector design)

| Reporter | Use | Output |
|---|---|---|
| **eGFP / mNeonGreen / mScarlet / mCherry / mTagBFP2 / iRFP** | imaging, FACS, expression reporter | fluorescence; pick spectrum to match other reporters. |
| **firefly luciferase (FLuc)** | luminescence | requires D-luciferin + ATP. |
| **Renilla luciferase (RLuc)** | luminescence; orthogonal to FLuc | requires coelenterazine. |
| **NanoLuc** | very high-intensity luminescence | small (19 kDa); furimazine substrate. |
| **lacZ** | colorimetric | X-gal blue / β-galactosidase activity. |
| **GUS (β-glucuronidase)** | plant histochemistry | X-Gluc. |
| **HiBiT / split-NanoLuc** | reconstitution / pulldown | small N- or C-terminal tag. |

### 5.11 Recombinase landing pads and integrating systems

| System | Recognition sites | Notes |
|---|---|---|
| **Cre-lox** | loxP (34 bp) and mutant variants (lox2272, loxN, lox511) | Reversible recombination; widely used for cassette excision and conditional alleles. |
| **Flp-FRT** | FRT (34 bp) | Reversible; less efficient at 37 °C than Cre. |
| **Bxb1 integrase** | attP (≈ 40 bp) / attB (≈ 50 bp) | Unidirectional; high-efficiency site-specific integration in mammalian and bacterial hosts. |
| **φC31 integrase** | attP / attB | Unidirectional integration; mammalian and bacterial. |
| **PiggyBac transposon** | ITRs flanking; TTAA target sites | Mammalian stable integration; reversible by transposase re-expression. |
| **Sleeping Beauty transposon (SB100X variant)** | ITRs; TA target sites | Mammalian stable integration. |
| **Tol2 transposon** | terminal sequences | Vertebrate (zebrafish, mouse). |

### 5.12 CRISPR/RNA-guided cassettes

| Element | Notes |
|---|---|
| **gRNA scaffold (Sp Cas9, "+1")** | 76-nt scaffold; Chen et al. 2013 / Hsu 2013 standard. |
| **gRNA scaffold (Sp Cas9, optimised tracrRNA-fusion)** | Dang et al. 2015 (PMID 26077853) — improved stem-loop variant; recommended for Pol-III expression. |
| **gRNA Pol-III expression** | U6 (most common), H1, 7SK. U6 requires G at position +1; if not present, append G and tolerate single mismatch at 5′. |
| **gRNA Pol-II expression** | Csy4 / RNase Z / ribozyme-flanked (HH-HDV self-cleaving) → enables multiplex from one Pol-II transcript. Tsai et al. 2014; Nissim et al. 2014. |
| **Cas9 variants** | wt SpCas9, eSpCas9 (high-fidelity), SpCas9-HF1, HypaCas9, xCas9, SpRY (PAM-relaxed), SaCas9 (smaller, NNGRRT PAM), Cas12a/Cpf1 (TTTV PAM, T-rich), Cas13 (RNA-targeting). |
| **base editors** | CBE (cytosine), ABE (adenine) — Komor 2016, Gaudelli 2017. |
| **prime editors** | PE2/PE3/PEmax — Anzalone 2019, 2022. |

### 5.13 Inducible mammalian systems

| System | Inducer | Notes |
|---|---|---|
| **Tet-On 3G / TRE3G** | doxycycline | tightest of the Tet variants; minimal leak. |
| **Tet-Off** | absence of doxycycline | high baseline expression; useful when expression must be silenced on demand. |
| **destabilisation domain (DD / FKBP)** | Shield-1 | post-translational; protein degraded without ligand. |
| **AID (auxin-inducible degron)** | indole-3-acetic acid (auxin) | requires Tir1; rapid degradation. |
| **dTAG / FKBP12-F36V** | dTAG-13 / dTAGV-1 | small-molecule-induced degradation. |
| **rapamycin-induced dimerisation** | rapamycin or AP21967 | FKBP–FRB system. |

---

## 6. Hosts / chassis catalogue (quantitative)

| Host | Common strains | Replicons supported | Key design factors |
|---|---|---|---|
| ***E. coli* propagation** | DH5α, TOP10, XL1-Blue (recA−, endA−); JM109; Stbl3/Stbl4 (repeat-tolerant); NEB Stable; HB101; ccdB Survival / DB3.1 (gyrA462, ccdB-tolerant); Pir+ for R6K | ColE1, pMB1, p15A, pSC101, R6K (Pir+), F | Use recA− endA− for high-quality miniprep; Stbl3 for lentiviral LTR-containing constructs; ccdB-tolerant for Gateway donor amplification. |
| ***E. coli* expression** | BL21(DE3), BL21 Star (rne131), BL21(DE3)pLysS / pLysE; Rosetta(DE3) / Rosetta-gami (rare codons, disulfide); Origami / SHuffle (oxidative cytoplasm); C41/C43 (membrane proteins); Lemo21(DE3) (tunable T7) | as above | Choose T7 host (DE3 lysogen) for pET. Choose SHuffle for disulfide-containing proteins. Choose C41/C43 or Lemo21 for toxic / membrane proteins. |
| **Cell-free** | PURE (in vitro reconstituted); S30 extract; TXTL myTXTL | linear or circular DNA; T7 / native *E. coli* promoters | No transformation; no auxotrophy; protein synthesis from purified components or extract. |
| ***S. cerevisiae*** | BY4741, BY4742, W303, S288C, INVSc1, EBY100 (surface display) | 2µ, CEN/ARS | Match marker to strain auxotrophies. GAL1-driven expression requires *gal4Δ gal80Δ* if tight off-state needed; or use glucose repression. |
| ***Pichia pastoris* / *Komagataella phaffii*** | GS115, X-33, KM71H, SMD1168 | Pichia-integrating vectors (5′ AOX1 / 3′ AOX1 targeting); pPICZ / pPIC9 | AOX1 methanol induction; Mut+ vs MutS phenotype; secretion via α-factor leader. |
| **Mammalian transient** | HEK293, HEK293T (SV40 large T), HEK293F (suspension), Expi293F, CHO-S, COS-1/COS-7 | episomal (CMV), SV40-amplified (with T-Ag), EBV oriP+EBNA1 | High-titre protein production; do not use for stable lines. |
| **Mammalian stable** | CHO-K1, CHO-DG44, CHO-GS (GS-null), HEK293, HeLa, NS0, Sp2/0 | integrating (random or targeted) | Use selection panel; consider amplifying systems (DHFR/MTX, GS/MSX). |
| **Mammalian iPSC / ES** | H1, H9, WIBR3, Mel1, mouse E14 | episomal (EBV), AAVS1-targeted, transposon | Strong silencing risk → prefer EF1α, CAG, or UBC; avoid CMV alone. |
| **Insect** | Sf9, Sf21, High Five (Trichoplusia ni) | baculovirus (BEVS) | Use Bac-to-Bac, FlashBAC, or BacMagic transfer system. Glycosylation pauci-mannose. |
| **Plant** | *N. benthamiana* (transient via *Agrobacterium*); *A. thaliana* (floral dip); rice/maize (biolistic, Agro) | T-DNA binary | Co-infiltrate p19 silencing suppressor for transient. |
| **Phage / VLP production** | *E. coli* with MS2/PP7/Qβ coat-protein expression plasmid; capsid + cargo separated | host plasmid (capsid) + reporter/cargo plasmid | Keep replication functions out; validate assembly by SEC/TEM/native PAGE. |

---

## 7. Assembly methods — quantitative parameters

### 7.1 Capability matrix

| Method | Fragments / pot (typical) | Scarless? | Junction footprint | Library compatibility | Notes |
|---|---|---|---|---|---|
| Restriction + ligation | 2–3 | No | RE site retained or removed depending on chemistry | Limited | Simple, robust, well-understood. |
| Gibson (original) | 2–6 | Yes | none (within homology arm choice) | OK | 25–40 bp overlaps recommended. |
| **NEBuilder HiFi** | 2–15 | Yes | none | OK | 15–20 nt for 2–3 fragments; 20–30 nt for 4–6; tolerates short mismatches. Quoted error-rate advantage vs Gibson is **vendor data, not peer-reviewed**. |
| Golden Gate (BsaI default) | up to ~10–15 routinely; **up to 35 with data-optimised overhang sets** (Pryor 2020) | Yes (within Type IIS scar definition) | 4-nt fusion site between parts (3-nt for SapI) | Excellent — combinatorial libraries trivial | Requires Type IIS-domesticated parts. |
| MoClo (hierarchical) | per level: 2–8 typical | Yes within standard | 4-nt fusion sites at defined positions | Excellent | Standardises L0/L1/L2 part-class scheme. |
| Loop assembly | recursive doubling (×4 per round) | Yes | 4-nt (BsaI) / 3-nt (SapI) | Excellent | Alternates BsaI/SapI between odd/even levels. |
| Gateway BP/LR | 1 ORF transfer | No — attB1/attB2 scars (~25 aa) | retained at N and C of ORF (G-T-X-L-Y-K-K-A-G-S- style) | OK | Reading-frame critical; use Multisite Gateway for multi-fragment. |
| LIC | 2–3 | Mostly yes (vector-specific tails) | small (12-nt T4-pol-generated overhang) | Limited | Ligase-independent; uses T4 DNA polymerase 3′→5′ exo to chew tails. |
| SLIC | 3–6 | Yes | none | OK | T4 polymerase + RecA, or polymerase-only chew-back. |
| USER | 3–7 | Yes | none (uracil-excision generates 3′ overhangs) | OK | Requires dU-containing primers/fragments. |
| IVA (in-vivo *E. coli*) | 2–6 | Yes | none | OK | No in-vitro enzymes; uses host RecA/RecET. |
| Yeast TAR / homologous recombination | up to 30+ fragments, 100+ kb | Yes | none | OK | Slow; requires yeast transformation + URA3-rescue. |

### 7.2 Type IIS enzymes (for Golden Gate-class assembly)

| Enzyme | Recognition | Cut offset | Overhang | Notes |
|---|---|---|---|---|
| **BsaI / BsaI-HFv2** | `GGTCTC` | (1/5) | 4-nt 5′ | Default; BsaI-HFv2 not blocked by Dam. |
| **BsmBI-v2 / Esp3I** | `CGTCTC` | (1/5) | 4-nt 5′ | Largely Dam/Dcm insensitive; common L1→L2. |
| **SapI / BspQI** | `GCTCTTC` | (1/4) | **3-nt 5′** | Used in Loop assembly; 3-nt overhangs reduce fidelity-set capacity vs 4-nt. |
| **BbsI / BpiI** | `GAAGAC` | (2/6) | 4-nt 5′ | Alternate L0/L1 enzyme; common in YTK and some MoClo kits. |
| **AarI** | `CACCTGC` | (4/8) | 4-nt 5′ | Rare cutter; requires oligo cofactor classically. |
| **PaqCI** | `CACCTGC` | (4/8) | 4-nt 5′ | AarI isoschizomer; no oligo cofactor; preferred modern choice. |

### 7.3 Overhang-fidelity data (software-critical)

| Dataset | Source | Use |
|---|---|---|
| **Potapov 2018** (T4 ligase, all 256 4-nt overhangs profiled by PacBio SMRT) | PMID 30335370 / *ACS Synth. Biol.* 7:2665 | Foundation 4-nt fidelity matrix for any Golden Gate overhang-set picker. |
| **Pryor 2020** ("FideliT4" / NEB Ligase Fidelity Viewer) | PMID 32877448 / *PLoS ONE* 15:e0238592 | Optimised overhang sets up to 35 fragments in one pot; published web tool data underpins the standard scoring algorithm. |

Software algorithm (recommended): given N fragments needing N+1 overhangs (linear) or N (circular), search the 256-overhang space for sets that (a) maximise on-target ligation propensity, (b) minimise off-target cross-ligation (Potapov pairwise mismatch frequencies), (c) avoid palindromes that self-ligate, (d) ensure no overhang appears with its reverse complement in another junction. See Pryor 2020 supplementary for the published optimisation.

### 7.4 MoClo / Golden-Gate kit reference

| Kit | Reference | Type IIS enzymes | Part-level scheme |
|---|---|---|---|
| MoClo (original, plant/general) | Weber et al. 2011 (PMID 21364738) | BsaI (L0→L1), BpiI/BbsI (L1→L2), BsaI (L2→L^M) | L0 / L1 / L2 / L^M |
| MoClo Plant Toolkit | Engler et al. 2014 (DOI 10.1021/sb4001504) | BsaI + BpiI | L0 / L1 / L2 |
| **YTK / Yeast MoClo** | Lee et al. 2015 (PMID 25871405) | BsmBI (Part→Cassette), BsaI (Cassette→Multigene), NotI for integration | Part plasmid / Cassette / Multigene |
| **Loop assembly** | Pollak et al. 2019 (PMID 30521109) | BsaI ↔ SapI alternating | Odd / Even loop levels (recursive, ×4 per round) |
| **GreenGate** | Lampropoulos et al. 2013 (PMID 24376629) | BsaI only | 6 fixed insert modules → one binary destination |
| **GoldenBraid 2.0** | Sarrion-Perdigones et al. 2013 (PMID 23669743) | BsaI + BsmBI | pUPD parts → α/Ω transcriptional-unit recursion |
| **JUMP** | Valenzuela-Ortega & French 2021 (PMID 33623824) | BsaI (L0→L1) + SapI (L1→L2) + BsmBI/Esp3I (higher) | L0 / L1 / L2; multi-host |
| **MIDAS** | van Dolleweerd et al. 2018 (PMID 29620866) | BsaI + BbsI (idempotent recursion) | Module / Multi-module |

### 7.5 Gibson / NEBuilder design rules

- Overlap GC content: 40–60 %.
- Avoid overlaps that contain hairpins (ΔG > −9 kcal/mol predicted by ViennaRNA).
- Avoid repeats within or near overlaps (≥ 20 bp direct repeats cause mis-assembly).
- For 2-fragment assemblies, 15–20 nt overlaps work for NEBuilder HiFi; for 4–6 fragments use 20–30 nt; for ≥ 6 use 30–40 nt or move to Golden Gate.
- Linear backbone preparation by PCR is the default; restriction-digested backbones work but recipient ends must match the overlap design.

### 7.6 Gateway scar sequences

When the software supports Gateway, it must encode the following residual residues at the ORF termini:

- **attB1 site** after BP reaction translates to roughly `MSLYKKAG-(ORF)` at the N-terminus (residue identity depends on the destination vector reading frame; common pENTR/pDEST pairs give `T-S-L-Y-F-Q` or similar).
- **attB2 site** after BP reaction translates to roughly `-(ORF)-NPAFLYKVV*` (stop-containing) at the C-terminus, *unless* a no-stop entry is used.

These scars are typically 8–10 aa N-terminal and ~25 aa C-terminal (no-stop) and can be incompatible with structure-resolution and certain biological functions.

---

## 8. Design decision logic — software-mappable flow

```
INPUT (typed):
    objective: { storage | expression | reporter | genome-editing | display | delivery }
    host_propagation: HostID
    host_expression: HostID | none
    cargo: { type: protein | gRNA | RNA | reporter | structural-RNA, sequence?, domain-map? }
    expression_level: { off | low | medium | high | tunable }
    induction_required: boolean
    tags_required: list[TagSpec]
    biosafety_tier: { BSL1 | BSL2 | BSL2+ | BSL3 | BSL4 }
    downstream_use: { research | translational | environmental | manufacturing }
    library_size: int | 1
    fragment_count_known: int | unknown

STEP 1 — host compatibility filter
    Reject incompatible (origin, host) pairs.
    Reject incompatible (marker, host, downstream_use) pairs (e.g., bla + translational → flag).

STEP 2 — propagation backbone candidate set
    For each compatible (origin, marker) pair, score by:
        - copy_number_match(expression_level, cargo_toxicity, library_size)
        - stability_match(cargo_repeats, cargo_size)
        - biosafety_match(biosafety_tier, mobilisation_elements)

STEP 3 — expression-control candidate set
    For host_expression:
        - select promoter candidates by (expression_level, induction_required, silencing_risk)
        - select RBS/Kozak candidates by host
        - select terminator/poly(A) by host
        - select PTRE if mammalian and high expression

STEP 4 — cargo assembly
    - translate ORF in silico in all three frames; choose canonical
    - check stop codon, internal stops, frameshift risk
    - place tags and linkers; check fusion-junction reading frame
    - check signal-peptide / NLS / cleavage-site biophysical sanity
    - run codon optimisation against host (CAI ≥ 0.7; %MinMax matched to native; preserve known structured RNA elements)

STEP 5 — assembly-method picker
    Inputs: fragment_count_expected, scarless_required, library_size, available_enzymes, biosafety_constraints
    Output: ranked list of methods (Golden Gate / NEBuilder / Gibson / Gateway / LIC / USER / IVA / restriction).
    For Golden Gate, run overhang-set optimiser against Potapov 2018 + Pryor 2020 matrices.

STEP 6 — internal-site audit
    Scan full proposed sequence for:
        - cloning enzyme sites internal to the cargo (and offer silent-mutation rescue)
        - Type IIS sites (BsaI, BsmBI, SapI, BbsI, AarI/PaqCI) if Golden Gate
        - common downstream-experiment sites (NotI, AscI, PacI, FseI for shuttle work)
        - synthesis-vendor forbidden patterns (Twist/IDT constraints, §11)

STEP 7 — in-silico validation pipeline (§9)
    Run every validation rule. Soft warnings → flag; hard violations → block.

STEP 8 — biosafety / screening hook (§12)
    Run sequence-screening adaptor (HHS-style, IGSC v2).
    If hit, route to manual review.

STEP 9 — serialise
    Emit SBOL-3 + GenBank + FASTA + design provenance graph + checksum.
```

Each step is implementable as a pure function over typed data structures (§15).

---

## 9. In-silico validation rules — parametric predicates

Each rule is one (predicate, severity, explanation, citation) tuple. Software returns the rule set as a structured report.

| ID | Predicate | Severity | Citation |
|---|---|---|---|
| V001 | The full construct must have a parseable sequence (ACGT only; ambiguity codes flagged). | hard | NCBI/EMBL Feature Table. |
| V002 | The annotated ORF must start with ATG (or GTG/TTG for *E. coli* and explicitly allowed) and end with TAA/TAG/TGA in frame. | hard | – |
| V003 | No internal stop codon in the annotated ORF. | hard | – |
| V004 | All fusion tags, linkers, and protease sites must be in the same reading frame as the ORF. | hard | – |
| V005 | Promoter ↔ host compatibility (table §5). | hard | – |
| V006 | RBS ↔ host compatibility; RBS+5′-ORF folding ΔG (−30…+30 nt around AUG) > −10 kcal/mol (warning) or > −5 (good). | soft / warn | Salis 2009; Reis & Salis 2020. |
| V007 | Kozak score (Noderer PWM) ≥ threshold for protein expression in mammalian hosts. | warn | Noderer 2014. |
| V008 | uORF scan: any in-frame ATG in 5′ UTR with Kozak score ≥ 0.7 → flag. | warn | Kozak 1986. |
| V009 | Splice-site scan (mammalian, SpliceAI or NetGene2) of full transcript region → flag predicted strong cryptic 5′ss/3′ss within ORF. | warn | SpliceAI: Jaganathan 2019. |
| V010 | Premature polyadenylation signal scan (`AAUAAA` and variants) in 5′ UTR or within ORF → flag. | warn | – |
| V011 | Type IIS site scan if Golden Gate selected — no internal BsaI/BsmBI/SapI/BbsI/AarI sites in parts (according to chosen kit). | hard | Engler 2008; Weber 2011. |
| V012 | Restriction-enzyme site scan against the user's listed enzymes — block conflict. | hard | – |
| V013 | Direct repeats ≥ 20 bp → flag (assembly mis-pairing); ≥ 100 bp → block. | soft / hard | NEB synthesis guidelines. |
| V014 | Homopolymer run > 9 nt → flag (synthesis difficulty, replication slippage). | warn | Twist/IDT guidelines. |
| V015 | Global GC content outside 25–65 %, or any 50-bp window outside 15–80 % → flag. | warn | Twist/IDT guidelines. |
| V016 | Codon adaptation index (CAI) for chosen host ≥ 0.7 (recommended target) and ≤ 0.95 (avoid overshoot); %MinMax distance from native ≤ 0.2 (preserve rare-codon pause structure). | warn | Sharp & Li 1987; Clarke & Clark 2008; Mauro & Chappell 2014. |
| V017 | mRNA structured-region preservation: any annotated functional RNA element (frameshift signal, IRES, riboswitch) in the cargo must be preserved through codon optimisation. | hard | – |
| V018 | Signal peptide cleavage prediction (SignalP) consistent with declared compartment. | warn | Almagro Armenteros 2019. |
| V019 | Antibiotic-marker risk: if downstream_use = translational and marker is in WHO highest-priority class → flag. | warn | WHO antibiotic priority list; FDA gene-therapy guidance. |
| V020 | Mobilisation element scan: oriT / mob detection in non-mobilisable design → flag. | warn | – |
| V021 | Sequence-screening hook (§12) result is not "hit on regulated pathogen / toxin / VFP" — else block pending manual review. | hard | HHS / IGSC v2. |
| V022 | Plasmid total size within host capacity: *E. coli* working maximum ≈ 30 kb (high-copy), 300 kb (BAC); AAV cargo ≤ 4.7 kb between ITRs; lentivirus payload ≤ ~9 kb between LTRs; baculovirus ≤ ~38 kb. | hard | per-host literature. |
| V023 | For viral / VLP work, replication functions and host-range determinants are absent unless explicitly justified by approved protocol. | hard | NIH Guidelines. |
| V024 | Checksum (sha256 of canonical-orientation sequence) is present in the metadata module. | hard | – |
| V025 | All annotated features have controlled-vocabulary feature keys (GenBank / Sequence Ontology). | hard | SO; GenBank FTD. |

A v2.x extension should add automated mRNA secondary-structure scoring with ViennaRNA, automated translation-rate prediction with RBS Calculator v2, automated codon-optimisation scoring with CHARMING, and automated splice-site scoring with SpliceAI.

---

## 10. Sequence formats and interoperability standards

| Standard | Use | Notes for software |
|---|---|---|
| **FASTA (.fa / .fasta)** | bare sequence interchange | minimal; no features. |
| **GenBank flat file (.gb / .gbk)** | annotated sequence with feature table | NCBI/EMBL/DDBJ feature-key controlled vocabulary; widely supported by SnapGene, Benchling, ApE, Geneious. |
| **EMBL flat file (.embl)** | European equivalent | semantically equivalent to GenBank. |
| **SnapGene (.dna)** | proprietary binary | many users export to GenBank; software should be able to read GenBank produced by SnapGene. |
| **SBOL 3 (.xml / .ttl / .json)** | open standard for synthetic-biology design data | Galdzicki 2014 (SBOL 2); Buecherl & Myers 2023 (SBOL 3). Models the full design provenance: parts, modules, interactions, experimental data. Software should both import and export SBOL 3. |
| **Sequence Ontology (SO)** | feature-key vocabulary | use for "promoter", "CDS", "RBS", "terminator", etc. (Eilbeck 2005). |
| **MIRIAM-style identifiers** | cross-database identifier resolution | `https://identifiers.org/...` scheme. |
| **Provenance graph (PROV-O)** | design history | W3C standard; SBOL 3 incorporates PROV-O. |
| **OpenMTA licence tag** | material-transfer-agreement metadata | Kahl et al. 2018 (PMID 30188547). |

Software must:
1. round-trip GenBank → internal model → GenBank with no annotation loss;
2. import/export SBOL 3 with at least ComponentDefinition + Sequence + Range + Roles;
3. serialise FASTA for any sequence on demand;
4. accept and serialise OpenMTA licence metadata for each part.

---

## 11. DNA synthesis vendor constraints

These are practical constraints typical of major synthesis vendors as of 2024–2026. Treat as *defaults*; the software should allow per-vendor profile overrides.

| Constraint | Typical limit (current vendor specs as of 2024–2026) |
|---|---|
| Gene-fragment length | **Twist gene fragments: 300 bp – 5,000 bp**; **Twist clonal genes: 300 bp – 5,000 bp**; **IDT gBlocks: 125 bp – 3,000 bp** (gBlocks HiFi up to 5 kb); GenScript standard synthesis up to ~10 kb (chemical fragments typically ≤ 3 kb per piece, assembled). > 5–10 kb requires multi-fragment assembly. |
| Global GC content | Twist soft floor ≈ 25 %, soft ceiling ≈ 65 %; IDT gBlocks accept 25–75 %. |
| GC in any 50-bp window | Twist soft bound ≈ 35–65 % (Express Genes); local-vs-global GC delta ≤ 52 % for Express scoring. |
| Homopolymer runs | **Twist hard rule: avoid homopolymers ≥ 14 bp**. IDT: ≤ 10 consecutive A/T, ≤ 6 consecutive G/C. |
| Direct repeats | ≥ 20 bp direct repeats flagged by most vendors; ≥ 40 bp typically rejected. |
| Inverted repeats / hairpins | strong predicted hairpins (low ΔG by ViennaRNA) rejected; vendor-specific thresholds. |
| Sequence complexity | ML-based scoring (Twist); Wootton-style low-complexity filters; vendor-specific. |
| Forbidden patterns | vendor-specific; may exclude certain Type IIS sites or pathogen-associated motifs from screening hits. |
| Cost scaling | tiered: per-bp price increases above complexity thresholds and above length thresholds. |

*References:* Twist Bioscience FAQ (current); IDT gBlocks product page (current); **Plesa et al., *Science* 2018 (PMID 29301959)** and Sidore et al., *Nucleic Acids Res.* 2020 (PMID 32692349) — peer-reviewed synthesis error-rate analyses.

Operational software rule: run `check_synthesisability(sequence, vendor_profile)` before recommending a final design; if it fails, attempt automatic codon-level rescue (silent mutations preserving CAI and %MinMax distance) within the same ORF and re-check.

---

## 12. Biosafety and sequence-screening framework

### 12.1 Frameworks in force (as of 2026-05-13)

| Framework | Custodian | URL | Use |
|---|---|---|---|
| NIH *Guidelines for Research Involving Recombinant or Synthetic Nucleic Acid Molecules* (April 2024) | NIH OSP | https://osp.od.nih.gov | Mandatory in any institution receiving NIH funding for research involving recombinant or synthetic NA. |
| **OSTP *Framework for Nucleic Acid Synthesis Screening* (September 2024)** | White House OSTP / HHS | https://aspr.hhs.gov/S3/Documents/OSTP-Nucleic-Acid-Synthesis-Screening-Framework-Sep2024.pdf | Operationally supersedes the 2023 HHS framework. Recommends screening of sequences ≥ 200 nt and customer screening best practices. |
| HHS *Screening Framework Guidance for Providers and Users of Synthetic Nucleic Acids* (revised October 2023) | HHS ASPR | https://aspr.hhs.gov/S3/Pages/Synthetic-Nucleic-Acids.aspx | Predecessor of the OSTP 2024 framework; still cited for ds/ss NA scope definition. |
| **IGSC Harmonized Screening Protocol v3.0 (September 2024)** | International Gene Synthesis Consortium | https://genesynthesisconsortium.org | Current industry standard, replacing v2 (2017). > 40 member providers worldwide. |
| **IBBIS — International Biosecurity and Biosafety Initiative for Science** (launched February 2024) | IBBIS / non-profit | https://ibbis.bio | Long-term home of the "Common Mechanism" sequence-screening tool; operates blinded-testing portals for synthesis providers; pass/fail attestations issued. |
| SecureDNA | non-profit | https://securedna.org | Parallel community screening platform; cryptographically blinded queries. |
| WHO *Laboratory Biosafety Manual*, 4th edition (2020) | WHO | https://www.who.int/publications/i/item/9789240011311 | Risk-assessment-based laboratory biosafety. |
| EU Directive 2009/41/EC (contained use of GMMs) | European Commission | https://eur-lex.europa.eu/eli/dir/2009/41/oj | Contained-use rules in EU member states. |

**2025–2026 development to track.** AI-designed evasion of BLAST-based screening was demonstrated and patched by IGSC member providers and SecureDNA / IBBIS in 2025 (industry coverage; primary peer-reviewed *Science* paper exists from October 2025 but exact PMID has not been independently verified within this knowledge base — software should treat current IGSC v3.0 and IBBIS Common Mechanism attestations as the operational standard and watch for the next IGSC revision).

### 12.2 Software hook contract

The vector-design software does not itself decide biosafety. It calls a configured **screening adaptor** with the proposed sequence and receives `{verdict ∈ {clear, watchlist, hit}, evidence[]}`. A `watchlist` or `hit` result must:
- block automatic submission to a synthesis vendor,
- route to a human reviewer (the institutional biosafety officer or equivalent),
- record the reviewer's decision in the construct's provenance graph.

The hook should be a pluggable interface so that institutions can use the IGSC adaptor, an internal blacklist, or a third-party service (e.g., IBBIS-compliant screening) without the design tool itself implementing the screening logic.

---

## 13. Provenance, MTA, and metadata

| Field | Definition |
|---|---|
| `construct_id` | UUID assigned at creation. |
| `version` | semver string. |
| `parent_ids` | list of parent-construct UUIDs (for design lineage). |
| `created_by` | ORCID or institutional ID. |
| `created_at` | ISO-8601 timestamp. |
| `checksum` | sha256 of canonical-orientation sequence (rotate circular sequence so it starts at the lexicographic minimum; record strand). |
| `licence` | OpenMTA / UBMTA / institutional / custom. |
| `source_provenance[]` | for each cited sequence: accession + retrieval date + URL. |
| `parts[]` | list of part UUIDs with versions. |
| `safety_classification` | NIH-section identifier + institutional ID. |
| `screening_results[]` | screening-adaptor returns (verdict, evidence). |
| `sbol_serialisation` | embedded SBOL-3 record or URL. |

This block is part of the `MetadataModule` in §4.2 and is a hard requirement (V024, V025) of the validation pipeline.

---

## 14. Parameterised vector templates

Each template below is specified in the typed-grammar form (§4.2). Defaults are software-fillable; allowed values reference the parts catalogue (§5).

### 14.1 Generic cloning / storage vector

```
PropagationModule:
    Origin       = { default: pMB1-mutant (pUC), allowed: pUC | ColE1 | p15A | pSC101 }
    Marker       = { default: kan, allowed: kan | amp | cam | spec }
    HostRange    = E. coli
AssemblyModule:
    Interface    = MCS (or Type IIS acceptor if library)
    NegativeSelection = optional (ccdB | sacB)
ExpressionModule:    n/a
CargoModule:         user-supplied slot
TerminationModule:   n/a
MetadataModule:      required
```

### 14.2 Bacterial expression vector (template)

```
PropagationModule:
    Origin       = pMB1 (high-copy for soluble protein) | pSC101 (low-copy for toxic) | p15A
    Marker       = kan | amp
ExpressionModule:
    Promoter     = T7lac (default) | trc | araBAD | rhaBAD | tetA | T5 | lacUV5
    RBS          = Salis-designed for target TIR, or BBa_B0034, or pET RBS default
CargoModule:
    N_tag        = optional (His6 | His10 | MBP | SUMO | NusA | Trx | TF)
    Linker_N     = optional (GGGGS)_n | (EAAAK)_n
    ProteaseSite = optional (TEV | PreScission | thrombin | enterokinase)
    ORF          = user-supplied
    Linker_C     = optional
    C_tag        = optional (His6 | Strep-II | Twin-Strep | AviTag | SNAP/HaloTag)
    StopStrategy = tandem TAA
TerminationModule:
    Terminator   = rrnB T1T2 (default) | T7 terminator | BBa_B0015
MetadataModule:      required
```

Design notes: prioritise tunability and stability over peak expression for toxic / aggregation-prone proteins. Always include a tag-free or alternative-tag backup design if activity matters.

### 14.3 Mammalian expression vector (template)

```
PropagationModule:
    Origin       = pMB1 / kan-marker (bacterial side)
    + episomal element if needed (SV40 ori + Large T → COS/HEK293T; EBV oriP + EBNA1 → 293F)
ExpressionModule:
    Promoter     = CMV (default for HEK; warn for stem cells) | EF1α | CAG | PGK | UBC | tissue-specific | TRE3G + rtTA
    UTR/Intron   = optional chimeric intron
    Kozak        = gccRccATGG (default); enforce -3 R and +4 G
CargoModule:
    SignalPeptide = optional (IL-2 SP | IgG SP)
    N_tag        = optional epitope (HA | FLAG | Myc | V5)
    ORF          = user-supplied
    C_tag        = optional (His6 | fluorescent reporter | localisation signal)
    StopStrategy = single or tandem TAA
TerminationModule:
    PTRE         = WPRE3 (recommended over wild-type WPRE) | none
    PolyA        = bGH (default) | SV40 late | hGH | rabbit β-globin | SPA
MammalianSelection (optional):
    Marker       = neo (G418) | puro | hygro | blast | zeo
MetadataModule:     required
```

### 14.4 Modular Type IIS / Golden Gate vector (MoClo-style)

```
PropagationModule:
    Origin       = compatible with the chosen kit's selection
    Marker       = kit-dependent
AssemblyModule:
    NegativeSelection = ccdB or pixie-style flanked by outward Type IIS sites
    FusionSites = kit-defined 4-nt overhangs (BsaI default) or 3-nt (SapI for Loop)
    OverhangSet = chosen by Pryor 2020 / Potapov 2018 optimiser
PartLevel:
    L0 / L1 / L2 / L^M as per kit (MoClo: Weber 2011; YTK: Lee 2015; Loop: Pollak 2019; etc.)
MetadataModule:    required
```

### 14.5 Shuttle vector

```
PropagationModule:
    BacterialOrigin = pMB1 / p15A / pSC101 (E. coli side)
    BacterialMarker = kan / cam (compatible with second-host marker)
    SecondHostMaintenance = (CEN/ARS + URA3 | 2µ + LEU2) for yeast;
                           (T-DNA borders + plant marker) for plant;
                           (RK2 + spec) for broad-host Gram-negative
ExpressionModule:    host-specific (per §5.4)
MetadataModule:      required
```

### 14.6 AAV transfer vector

```
PropagationModule:
    BacterialOrigin = pMB1; BacterialMarker = amp or kan
ITR_5:               145 nt AAV2 ITR (canonical)
ExpressionModule:    Promoter (compact preferred — CMV / EF1α-short / SYN1) + Kozak
CargoModule:         ORF (must fit ≤ ~4.7 kb between ITRs including all regulatory elements)
TerminationModule:   compact polyA (SPA or shortened bGH) + optional WPRE3
ITR_3:               145 nt AAV2 ITR (canonical)
MetadataModule:      required
HardConstraint:      total ITR-flanked cargo ≤ 4.7 kb (V022).
```

### 14.7 3rd-generation lentiviral transfer vector

```
PropagationModule:
    BacterialOrigin = pMB1 / pUC (use Stbl3/Stbl4 for amplification)
    BacterialMarker = amp
LTR_5:               RSV/CMV-promoter-substituted U5 (allows Tat-independent transcription)
PackagingSignal:     Ψ
RRE:                 Rev-response element
cPPT/CTS:            central polypurine tract / central termination signal
ExpressionModule:    internal promoter (EF1α / PGK / UBC / CAG / tissue-specific)
CargoModule:         ORF
TerminationModule:   WPRE3 + SIN-LTR (3′ LTR with ΔU3)
MetadataModule:      required
HardConstraint:      cargo ≤ ~9 kb between LTRs (V022).
```

### 14.8 CRISPR gRNA expression vector

```
PropagationModule:        as 14.1
ExpressionModule:         Pol-III promoter (U6 default) + downstream sgRNA scaffold (Dang 2015 optimised) + 6+ T terminator
CargoModule:              gRNA spacer (20 nt; first nt must be G for U6, or append G)
Optional Cas9 cassette:   Pol-II promoter (CMV / EF1α / CBh) + Cas9 ORF + NLS + tag + polyA
MetadataModule:           required
```

### 14.9 Phage / VLP display or cargo-delivery vector (MS2-class)

```
PropagationModule:        compact, stable
ExpressionModule:         inducible bacterial promoter (T7lac default for MS2-CP expression)
CargoModule:
    CapsidProtein         MS2-CP (wild-type, or single-chain dimer V75E/A81G)
    DisplayLandingPad     AB-loop insertion (after residue 15) | C-terminal tag (SpyTag / His6 / click handle)
    PurificationTag       His6 (recommended C-terminal on the SCP linker, not the AB-loop)
TerminationModule:        rrnB T1T2

Separate cargo cassette (in trans):
    PackagingSignal       MS2 pac/hairpin tag (5′-ACAUGAGGAUCACCCAUGU-3′)
    CargoORF/RNA          user-supplied (mRNA + UTRs and polyA for mammalian readout)
MetadataModule:           required
```

Design notes mirror v1.0 §7.6 with the additional explicit MS2 references (§17).

---

## 15. Software-internal data-schema sketch

```python
# Pseudocode / type-spec; not a particular language.

class Part:
    id: UUID
    name: str
    role: SO_term            # Sequence Ontology controlled vocabulary
    sequence: str            # DNA, ACGT
    annotations: list[Feature]
    parent: Optional[UUID]   # design lineage
    licence: Licence
    provenance: Provenance
    checksum: SHA256

class Module:
    id: UUID
    layer: Literal["propagation","assembly","expression","cargo","termination","metadata"]
    parts: list[Part]
    constraints: list[Constraint]

class Construct:
    id: UUID
    modules: list[Module]
    host_propagation: HostID
    host_expression: Optional[HostID]
    full_sequence: str       # derived from modules
    feature_table: list[Feature]
    sbol_record: SBOL3
    checksum: SHA256

class Host:
    id: HostID
    name: str
    chassis: Literal["E.coli","S.cerevisiae","HEK293","CHO","Sf9","N.benthamiana", ...]
    compatible_origins: list[OriginID]
    compatible_markers: list[MarkerID]
    expression_features: HostFeatureSet
    safety_tier: BiosafetyTier

class AssemblyMethod:
    id: AssemblyMethodID
    name: str
    requires: list[Constraint]      # e.g., Type IIS clean
    scarless: bool
    max_fragments_typical: int
    overhang_dataset: Optional[OverhangFidelityMatrix]
    notes: str

class ValidationRule:
    id: str                  # V001 … V025 …
    predicate: Callable[[Construct], ValidationResult]
    severity: Literal["hard","soft","info"]
    citation: list[Reference]

class DesignSession:
    objective: Objective
    construct: Construct
    candidate_methods: list[AssemblyMethod]
    validation_report: list[ValidationResult]
    screening_results: list[ScreeningResult]
    history: ProvenanceGraph
```

This schema is intentionally minimal and corresponds 1:1 to the SBOL 3 ComponentDefinition / Sequence / Range / Role hierarchy so that round-trip serialisation is direct.

---

## 16. Failure modes, design-time predictors, and corrective actions

| Failure mode | Likely vector-design causes | Design-time predictor | Design-level fix |
|---|---|---|---|
| Few / no colonies after transformation | toxic insert, wrong antibiotic, incompatible ori/host, bad linearisation, large plasmid | V005, V019, V022 | lower-copy backbone; tighter / inducible promoter; verify marker/host pairing; use negative-selection. |
| Many empty-vector colonies | non-directional cloning, incomplete backbone digestion, no negative selection | V012 — single cut site or directional check | use directional sites; Type IIS / Gateway / LIC; ccdB/sacB-based negative selection. |
| Insert deletion / rearrangement after passage | direct/inverted repeats; high-copy + toxicity; recombination-prone host | V013 (repeats); V016 (CAI overshoot causing burden) | low-copy backbone; *recA*-deficient stable strain; reduce basal expression; redesign repeats. |
| Correct DNA but no expression | wrong promoter for host; poor RBS/Kozak; frameshift; missing start/stop; cryptic splice/polyA | V002–V010 | match expression module to host; redesign 5′ context; remove cryptic splice/polyA. |
| Expression but insoluble / inactive protein | too-strong expression; poor folding; tag interference; missing PTMs; wrong compartment | V006 (TIR overshoot); V016 (CAI overshoot); V018 (signal-peptide mismatch) | tunable promoter; solubility tag (MBP/SUMO/NusA); alternative host (SHuffle, eukaryotic); secretion. |
| Mammalian expression silences over time | promoter choice; CpG/backbone burden; integration-site effects; selection pressure | mark CMV in stem-cell context (V005 warn) | switch to EF1α/CAG/PGK/UBC; insulators (cHS4); minimised backbone; alternative integration locus (AAVS1). |
| Wrong fusion protein | att/MCS scar; linker frame error; extra residues after cleavage | V004 (frame); §7.6 (Gateway scar) | redesign junction; use scarless cloning or compatible reading-frame cassette. |
| Readthrough / background expression | weak terminator; promoter leakiness; backbone promoter interference | terminator-strength heuristic | strong terminator (rrnB T1T2 / BBa_B0015); insulated promoter; repressor titration. |
| Satellite colonies on ampicillin | β-lactamase hydrolyses ampicillin → selection erodes | flag if marker = amp and downstream_use = long-term-culture | switch to carbenicillin or kan. |
| AAV cargo too large | total ITR-flanked region > 4.7 kb | V022 | compact promoter (CBh / SYN1-short); SPA polyA; remove non-essential elements. |
| Lentiviral titre low | excessive cargo; absence of cPPT/RRE/WPRE3; problematic sequences | V022; element-presence check | trim cargo; verify cPPT/RRE; use WPRE3; avoid LTR-homologous sequences. |
| IRES/2A junction artefacts | residual 2A scar at C-terminus of upstream cistron; weak IRES context | V004 + tag-position rules | use furin-cleaved 2A; favour P2A; for high upstream cleanliness, prefer separate promoter cassette. |
| Stable mammalian clones express then silence | CpG islands; CMV silencing; selection pressure removal | promoter choice flag | EF1α/CAG/UBC; A2UCOE element; targeted integration into AAVS1/CCR5. |
| BAC end instability | repeats near vector / insert junction; long inserts | V013 | BAC-stable strain (DH10B); minimise repeats in flanks. |
| Yeast 2µ instability | leakage of marker; high copy + toxic insert | V019 + copy flag | switch to CEN/ARS for single-copy; verify marker. |

---

## 17. Project-specific appendix: MS2 / phage / VLP vector design

The existing project direction emphasises MS2 coat-protein VLPs, mRNA cargo bearing MS2 hairpin / pac tags, CRC-targeting ligands, modular conjugation strategies, and Addgene pMC037-HisMS2_PLP_pac as a relevant benchmark.

### 17.1 Established MS2 reference points

- **Wild-type MS2 coat protein (MS2-CP)**: 129 aa; forms a non-covalent dimer; 90 dimers (180 monomers) assemble into a T=3 icosahedral capsid of ~27 nm diameter.
- **Single-chain MS2 dimer (SCP)**: two MS2-CP monomers fused by a flexible linker, typically with V75E and A81G mutations to favour dimer over higher-order intermediates (Peabody 1997, Caldeira & Peabody 2011); allows tolerance of large peptide insertions in the AB-loop of one half only.
- **MS2 hairpin / pac site**: consensus 5′-`ACAUGAGGAUCACCCAUGU`-3′ stem-loop; the −10 A and −7 C residues are critical for high-affinity coat-protein binding (Romaniuk 1987; Witherell 1991; Lim & Peabody 1994).
- **Orthogonal coat-protein families**: PP7 (from *Pseudomonas* phage) and Qβ are orthogonal to MS2 → useful for two-colour / two-cargo schemes (Lim 2001; Chao et al. 2008).
- **AB-loop insertion**: tolerated for short peptides (≤ ~25 aa typically); longer insertions disrupt assembly unless paired SCP design is used (one half loaded, the other clean).
- **C-terminal extensions**: tolerated more readily than AB-loop insertions for ≥ 25-aa cargos; useful for sortase / SpyTag handles.

### 17.2 Project guidance (preserved from v1.0 §10, extended)

1. Use a **locked reference sequence** for the MS2-CP and document every variant as explicit deltas with checksum.
2. Keep **capsid expression**, **display/ligand module**, and **cargo cassette** separable until assembly and cargo-loading behaviour are characterised.
3. Benchmark against published or repository vectors (e.g., pMC037 / pMC051); do **not** copy unnecessary replication or maturation functions into a therapeutic-like architecture.
4. Prefer **post-assembly or minimally disruptive display modules** (SpyTag/SpyCatcher, sortase, click handles) before attempting direct AB-loop insertion; if direct insertion is required, include a blank-linker control with identical handle geometry.
5. Build explicit release assays: particle identity (SEC-MALS / TEM), size/morphology, cargo loading (qRT-PCR after RNase challenge), nuclease protection, ligand occupancy (LC-MS quantification), target-positive vs target-negative cell uptake, downstream readout, and cytotoxicity.
6. For phage-delivery concepts, apply a stricter biosafety review when adding host-range, tropism, replication, cargo-delivery, or antimicrobial-payload functions.
7. For the software side: include an MS2-specific template profile (§14.9) and an MS2-specific validation rule set (loop-insertion-size limit; pac-hairpin presence and copy-number check; SCP linker integrity).

### 17.3 Key MS2 references for the project

- Peabody DS, *EMBO J.* 1993, 12:595–600.
- Peabody DS & Ely KR, *Nucleic Acids Res.* 1992, 20:1649–1655.
- Mastico RA, Talbot SJ, Stockley PG, *J. Gen. Virol.* 1993, 74:541–548.
- Lim F & Peabody DS, *Nucleic Acids Res.* 1994, 22:3748–3752; *Nucleic Acids Res.* 2002, 30:4138–4144.
- Witherell GW, Gott JM, Uhlenbeck OC, *Prog. Nucleic Acid Res. Mol. Biol.* 1991, 40:185–220.
- Romaniuk PJ et al., *Biochemistry* 1987, 26:1563–1568.
- Caldeira JC, Peabody DS, *PLoS ONE* 2011, 6:e18502.
- Chao JA, Patskovsky Y, Almo SC, Singer RH, *Nat. Struct. Mol. Biol.* 2008, 15:103–105 (MS2 / PP7 / Qβ orthogonality).
- Galaway FA, Stockley PG, *Mol. Pharm.* 2013, 10:59–68 (MS2 VLPs as delivery vehicles).
- Pumpens P & Pushko P, *VLPs and Virus-like Particles*, Springer 2022 (modern review monograph).

---

## 18. Source registry

*Section 13 of v1.0 is preserved verbatim and extended. The full registry has > 80 entries; the v1.0 registry is retained and the following additions are made for v2.0.*

### 18.1 v1.0 entries retained
All entries from v1.0 §13 are retained. Spot-checked entries (Cohen 1973, Bolivar 1977, Vieira 1982, Yanisch-Perron 1985, del Solar 1998, Nora 2018, de Lorenzo 2025, Gibson 2009, Engler 2008/2009, Weber 2011, Bird 2022, Hartley 2000, Aslanidis 1990, Li & Elledge 2007, Bitinaite 2007, Salis 2009/2011, Davis 2011, Studier T7, Shilling 2020, Francis 2010, Boshart 1985, Foecking 1986, Kozak 1986, Pfarr 1986, Loeb 1999, Makrides 2004, Vernet 1987, Mumberg 1995, Jarvis 2009, Chambers 2018, Felberbaum 2015, Bevan 1984, Komari 2006, Young 2012, Kimple 2013, Costa 2014, Köppl 2022, Webster 2017, Mauro 2014, Bali 2015, Moss 2024, Williams 2009, Carnes 2010, Mignon 2015) all resolved correctly against PubMed/PMC. No fabricated citations identified.

### 18.2 New entries added in v2.0

| ID | Source | Locator | Category |
|---|---|---|---|
| POTAPOV-2018 | Potapov V et al. *ACS Synth. Biol.* 2018 — Comprehensive profiling of 4-base overhang ligation fidelity by T4 DNA ligase | PMID 30335370; DOI 10.1021/acssynbio.8b00333 | Golden Gate fidelity |
| PRYOR-2020 | Pryor JM et al. *PLoS ONE* 2020 — Data-optimised assembly design | PMID 32877448; DOI 10.1371/journal.pone.0238592 | Golden Gate fidelity |
| LEE-2015-YTK | Lee ME et al. *ACS Synth. Biol.* 2015 — Highly characterised yeast toolkit | PMID 25871405; DOI 10.1021/sb500366v | YTK / yeast MoClo |
| POLLAK-2019 | Pollak B et al. *New Phytol.* 2019 — Loop assembly | PMID 30521109; DOI 10.1111/nph.15625 | Loop GG kit |
| LAMPROPOULOS-2013 | Lampropoulos A et al. *PLoS ONE* 2013 — GreenGate | PMID 24376629; DOI 10.1371/journal.pone.0083043 | Plant GG kit |
| SARRION-2013-GB2 | Sarrion-Perdigones A et al. *Plant Physiol.* 2013 — GoldenBraid 2.0 | PMID 23669743; DOI 10.1104/pp.113.217661 | Plant GG kit |
| VALENZUELA-2021-JUMP | Valenzuela-Ortega M & French C. *Synth. Biol. (Oxford)* 2021 — JUMP | PMID 33623824; DOI 10.1093/synbio/ysab003 | Universal GG kit |
| VANDOLLEWEERD-2018-MIDAS | van Dolleweerd CJ et al. *ACS Synth. Biol.* 2018 — MIDAS | PMID 29620866; DOI 10.1021/acssynbio.7b00363 | Idempotent GG kit |
| REIS-SALIS-2020 | Reis AC & Salis HM. *ACS Synth. Biol.* 2020 — RBS Calculator v2.0 | PMID 33054181; DOI 10.1021/acssynbio.0c00394 | RBS prediction |
| KOZAK-1986 | Kozak M. *Cell* 1986 — Point mutations define a sequence flanking AUG that modulates eukaryotic translation | PMID 3943125 | Mammalian translation |
| KOZAK-1987-NAR | Kozak M. *Nucleic Acids Res.* 1987 — Analysis of 5′-noncoding sequences from 699 vertebrate mRNAs (`GCCRCCAUGG` consensus) | PMID 3313277 | Mammalian translation |
| NODERER-2014 | Noderer WL et al. *Mol. Syst. Biol.* 2014 — Quantitative analysis of mammalian translation initiation by FACS-seq | PMID 25170020 | Mammalian translation |
| DIAZ-2020-KOZAK | Diaz de Arce AJ et al. *Genome Res.* 2020 — Initiation downstream of annotated starts | PMID 32669370 | Mammalian translation |
| ZANTA-BOUSSIF-2009 | Zanta-Boussif MA et al. *Gene Ther.* 2009 — Validated mut6/WPRE3 abrogates WHV-X ORF translation | PMID 19262615; DOI 10.1038/gt.2009.3 | WPRE safety |
| SCHAMBACH-2006-WPREmut | Schambach A et al. *Gene Ther.* 2006 — Mutated WPRE without X-ORF | PMID 16355114 | WPRE safety |
| KINGSMAN-2005-WPRE | Kingsman SM et al. *Gene Ther.* 2005 — Potential oncogene activity of WPRE | PMID 15510172 | WPRE safety |
| KIM-2011-2A | Kim JH et al. *PLoS ONE* 2011 — P2A > T2A > E2A > F2A cleavage efficiency in HEK293T/zebrafish/mouse | PMID 21602908 | 2A peptides |
| SZYMCZAK-2012-2A | Szymczak-Workman et al. *Cold Spring Harb. Protoc.* 2012 — Design of 2A-linked multicistronic vectors | PMID 22301656 | 2A peptides |
| LIU-2017-2A | Liu Z et al. *Sci. Rep.* 2017 — Systematic comparison of 2A peptides | PMID 28526819; DOI 10.1038/s41598-017-02460-2 | 2A peptides |
| CHNG-2015-2A | Chng J et al. *MAbs* 2015 — 2A peptides for mAb expression in CHO | PMID 25621616 | 2A peptides |
| PFARR-1986 | Pfarr DS et al. *DNA* 1986 — Differential effects of polyadenylation regions; bGH ~3× over SV40 early | PMID 2872023 | PolyA |
| LEVITT-1989-SPA | Levitt N et al. *Genes Dev.* 1989 — Definition of an efficient synthetic poly(A) site (SPA) | PMID 2570734 | PolyA |
| YEW-2007 | Yew NS et al. *J. Gene Med.* 2007 — Impact of polyA on plasmid nuclease-resistance and transgene expression | PMID 17407167 | PolyA |
| QIN-2010 | Qin JY et al. *PLoS ONE* 2010 — Systematic comparison of constitutive and Tet-inducible mammalian promoters | PMID 20485554 | Mammalian promoters |
| NORRMAN-2010 | Norrman K et al. *PLoS ONE* 2010 — Quantitative comparison of constitutive promoters in hESC | PMID 20865041 | Mammalian promoters |
| SHIMIZU-2001-PURE | Shimizu Y et al. *Nat. Biotechnol.* 2001 — PURE cell-free system | PMID 11479568 | Cell-free expression |
| GARAMELLA-2016-TXTL | Garamella J et al. *ACS Synth. Biol.* 2016 — myTXTL | PMID 26925207 | Cell-free expression |
| DULL-1998-3GLENTI | Dull T et al. *J. Virol.* 1998 — 3rd-gen lentiviral packaging | PMID 9811723 | Lentivirus |
| IVICS-1997-SB | Ivics Z et al. *Cell* 1997 — Sleeping Beauty | PMID 9390559 | Mammalian transposon |
| WILSON-2007-PB | Wilson MH et al. *Mol. Ther.* 2007 — PiggyBac | PMID 17387335 | Mammalian transposon |
| GARCIA-NAFRIA-2016-IVA | García-Nafría J et al. *Sci. Rep.* 2016 — IVA cloning | PMID 27464723 | In-vivo assembly |
| KOUPRINA-2008-TAR | Kouprina N & Larionov V. *Nat. Protoc.* 2008 — TAR cloning | PMID 18388946 | Yeast assembly |
| EILBECK-2005-SO | Eilbeck K et al. *Genome Biol.* 2005 — Sequence Ontology | PMID 15892872 | Standards |
| GALDZICKI-2014-SBOL | Galdzicki M et al. *Nat. Biotechnol.* 2014 — SBOL (v2) | PMID 24911500 | Standards |
| MADSEN-2019-SBOL3 | Madsen C et al. *J. Integr. Bioinform.* 2019/2020 — SBOL Version 3.0.0 | PMID 32589605 | Standards |
| MCLAUGHLIN-2020-SBOL3 | McLaughlin JA et al. *Front. Bioeng. Biotechnol.* 2020 — SBOL Version 3: simplified data exchange | PMID 33015004 | Standards |
| BUECHERL-2023-SBOL3 | Buecherl L et al. *J. Integr. Bioinform.* 2023 — SBOL 3.1.0 | PMC10063177 | Standards |
| KAHL-2018-OMTA | Kahl L et al. *Nat. Biotechnol.* 2018 — OpenMTA | PMID 30188547 | MTA standard |
| CAMBRAY-2013-TERM | Cambray G et al. *Nucleic Acids Res.* 2013 — Bacterial terminators | PMID 23275534 | Terminators |
| KOSURI-2013 | Kosuri S et al. *PNAS* 2013 — Composability of regulatory sequences | PMID 23695363 | RBS/promoter |
| QIN-2010 | Qin JY et al. *PLoS ONE* 2010 — Mammalian promoter comparison | PMID 20485482 | Mammalian promoters |
| DANG-2015-GRNA | Dang Y et al. *Genome Biol.* 2015 — Optimised gRNA scaffold | PMID 26077853 | CRISPR scaffold |
| HSU-2013 | Hsu PD et al. *Nat. Biotechnol.* 2013 — Cas9 specificity | PMID 23873081 | CRISPR |
| KOMOR-2016-CBE | Komor AC et al. *Nature* 2016 — Cytosine base editor | PMID 27096365 | Base editing |
| GAUDELLI-2017-ABE | Gaudelli NM et al. *Nature* 2017 — Adenine base editor | PMID 29160308 | Base editing |
| ANZALONE-2019-PE | Anzalone AV et al. *Nature* 2019 — Prime editing | PMID 31634902 | Prime editing |
| JAGANATHAN-2019 | Jaganathan K et al. *Cell* 2019 — SpliceAI | PMID 30661751 | Splice prediction |
| ALMAGRO-2019-SIGNALP | Almagro Armenteros JJ et al. *Nat. Biotechnol.* 2019 — SignalP 5.0 | PMID 30778233 | Signal peptide |
| CLARKE-CLARK-2008 | Clarke TF, Clark PL. *PLoS ONE* 2008 — %MinMax | PMID 18301736 | Codon optimisation |
| DOS-REIS-2004-TAI | dos Reis M et al. *Nucleic Acids Res.* 2004 — tAI | PMID 15448185 | Codon optimisation |
| JACOBS-SHAKHNOVICH-2017 | Jacobs WM, Shakhnovich EI. *Biophys. J.* 2017 — CHARMING | PMID 29262339 | Codon optimisation |
| KAPUST-WAUGH-2000 | Kapust RB, Waugh DS. *Protein Eng.* 2000 — TEV cleavage | PMID 11041849 | Protease |
| IGSC-V3 | International Gene Synthesis Consortium, Harmonized Screening Protocol v3.0 (September 2024) | https://genesynthesisconsortium.org/wp-content/uploads/IGSC-Harmonized-Screening-Protocol-v3.0-1.pdf | Biosecurity |
| OSTP-2024-FRAMEWORK | OSTP / HHS *Framework for Nucleic Acid Synthesis Screening* (Sep 2024) | https://aspr.hhs.gov/S3/Documents/OSTP-Nucleic-Acid-Synthesis-Screening-Framework-Sep2024.pdf | Biosecurity |
| IBBIS-2024 | IBBIS — International Biosecurity and Biosafety Initiative for Science (launched Feb 2024) | https://ibbis.bio | Biosecurity |
| SECUREDNA | SecureDNA non-profit screening platform | https://securedna.org | Biosecurity |
| NIH-2024 | NIH Guidelines for Research Involving Recombinant or Synthetic Nucleic Acid Molecules, April 2024 | https://osp.od.nih.gov | Biosafety |
| PLESA-2018 | Plesa C et al. *Science* 2018 — DropSynth: multiplexed gene synthesis in emulsions; oligo and assembly error rates | PMID 29301959 | DNA synthesis |
| SIDORE-2020 | Sidore AM et al. *Nucleic Acids Res.* 2020 — DropSynth 2.0 | PMID 32692349 | DNA synthesis |

### 18.1 External educational references

The following Addgene-published eBooks (downloaded 2026-05-22) are referenced as **curator-side discovery aids** — pointers into the primary literature and overviews of mechanism categories that this KB documents. **Use restriction:** the eBooks are © Addgene Inc.; only the *facts and primary-literature pointers* they reference are used here. eBook text itself, diagrams, and Addgene-authored commentary are NOT redistributed in this project. Per IP-audit § 5.2 fold-in (depositor-owned vs. Addgene-authored content distinction): the eBooks fall in the Addgene-authored category and are read-only references for the curator, not corpus content.

| ID | Title | Edition | Topic coverage relevant to this KB |
|---|---|---|---|
| ADDGENE-EBOOK-PLASMIDS-101 | Addgene *Plasmids 101* | 4th ed. | Plasmid anatomy, ORI biology, selection markers, cloning strategies; aligns with KB §§ 4–7 |
| ADDGENE-EBOOK-CRISPR-101 | Addgene *CRISPR 101* | 3rd ed. | Cas9/Cas12/Cas13 mechanisms, sgRNA design, HDR templates; out-of-scope for v0.2 corpus but referenced in MR-30 negative-selection-cassette rule discussion |
| ADDGENE-EBOOK-FP-101 | Addgene *Fluorescent Proteins 101* | 1st ed. | FP photophysics, oligomerisation, FRET pairs, optogenetic tools; KB § 14 and corpus § fluorescent_protein |
| ADDGENE-EBOOK-VV-101 | Addgene *Viral Vectors 101* | 2nd ed. | Lentivirus / AAV / adenovirus / retrovirus packaging biology; aligns with MR-18..22 cargo-capacity rules and corpus § backbone mammalian |
| ADDGENE-EBOOK-AB-101 | Addgene *Antibodies 101* | 1st ed. | Antibody fragments (scFv, Fab, Fc), display platforms; out-of-scope for v0.2 corpus |

**Nominative-use disclaimer for "Addgene":** Addgene® is a registered trademark of Addgene Inc. (Watertown, MA, USA). This project is not affiliated with, endorsed by, sponsored by, or in any way officially connected to Addgene. References to Addgene eBooks above are made under the nominative-use doctrine for the purpose of citing curator-side educational resources. The same nominative-use posture applies to depositor-deposited sequence files retrieved from Addgene (cf. corpus records in `partition: sa_free` carrying `provenance.source: primary_literature` with the depositor's primary publication as `accession_or_url`).

**Follow-up curation task (deferred):** A focused multi-session pass should extract the bibliographies from these eBooks and add any new primary-lit citations to § 18 above. The eBook PDFs themselves remain in the curator's local environment (not redistributed); the project preserves only the eBook IDs above (factual pointers).

---

## 19. Limitations and disclaimer

### 19.1 Limitations

- This knowledge base is a **curated technical foundation**, not a formal systematic review nor a regulatory submission. It is calibrated for use as a software design support document.
- **Numeric parameters** in §5 and §11 are typical values reported in the cited literature or vendor documentation. They are starting points, not constants. Any production system must allow user override and re-calibration against measured data.
- **Vendor-specific synthesis constraints** are subject to change; the software should treat the values in §11 as a default profile and load vendor-specific profiles dynamically.
- **Biosafety / biosecurity** is not handled by the software directly. The hook contract in §12 routes screening to the appropriate institutional or governmental body.
- **Intellectual-property / freedom-to-operate** is not handled here. Specific clones, ORFs, regulatory elements, and assembly methods may be protected by patent or by MTA. The companion *IP Audit* skill should be invoked separately when commercialisation is in scope.
- For any specific construct, the **exact sequence, host strain / cell line, biosafety classification, institutional approval path, and freedom-to-operate / IP status must be checked independently** of this document.

### 19.2 Disclaimer

> This scientific knowledge base is provided for informational, research, and advisory purposes only. It does not constitute professional engineering advice, medical advice, regulatory advice, or formal peer review. All hypotheses, designs, and protocols derived from this document should be validated through appropriate laboratory experimentation, reviewed by qualified domain experts and institutional biosafety committees, and screened for biosecurity risk in accordance with the applicable national and international guidelines before implementation. The author is an AI Scientific Advisor; the document should be treated as a structured starting point for further investigation, software-design specification, and human expert review.

---

*End of Cloning and Expression Vector Design Knowledge Base v2.0.*
