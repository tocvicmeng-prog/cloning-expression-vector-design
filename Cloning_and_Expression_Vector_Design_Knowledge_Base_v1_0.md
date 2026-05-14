# Cloning and Expression Vector Design Knowledge Base v1.0

**Prepared:** 2026-05-13  
**Prepared for:** phage protein design / plasmid-vector engineering workflow  
**Scope:** authentic literature and lecture/resource screening, fundamental design principles, cloning and expression-vector design techniques, verification workflow, and caution points.  
**Safety scope:** conceptual vector-design guidance only. This file does **not** provide step-by-step wet-lab protocols, culture conditions, transformation procedures, viral production procedures, or operational parameters.

---

## 1. Executive summary

A good cloning or expression vector is not just a DNA circle with an insert. It is a controlled engineering system with five interacting layers:

1. **Propagation layer** — origin/replicon, copy number, host range, plasmid stability, selectable marker, and bacterial verification sites.
2. **Assembly layer** — multiple cloning site, Type IIS acceptor, homology arms, recombination sites, negative-selection cassette, or scarless assembly interface.
3. **Expression-control layer** — promoter/enhancer/operator, RBS or Kozak context, UTRs/introns, transcription terminator/poly(A), inducibility, and insulation from backbone context.
4. **Cargo layer** — ORF/cDNA/gRNA/RNA cassette/protein domain, codon strategy, tags, localization signals, cleavage sites, linkers, stop codons, and domain boundaries.
5. **Quality/safety layer** — sequence provenance, feature annotation, sequencing primers, restriction/Type IIS audit, biosafety review, synthetic-nucleic-acid screening, antibiotic-resistance risk, and record keeping.

**Core design rule:** choose the vector architecture from the experimental objective and host system first, then choose cloning chemistry. Many failed vector projects fail because the assembly method was selected before the biological requirements were defined.

---

## 2. Literature and lecture/resource screening method

### 2.1 Source authenticity rules

Sources were accepted into this knowledge base only when they met at least one of the following criteria:

| Grade | Accepted source type | How it was used |
|---|---|---|
| A | Primary peer-reviewed paper indexed by PubMed/PMC or hosted by the journal/publisher | Main evidence for methods, vector architecture, expression systems, and historical origins. |
| A | Official database or guideline: NIH, HHS/ASPR, WHO, NCBI Bookshelf, Addgene repository/reference pages, MIT OpenCourseWare | Authoritative definitions, educational/lecture resources, safety and compliance framework. |
| B | Peer-reviewed review article indexed by PubMed/PMC | Used for synthesis and caution points, not as sole authority for sequence identity. |
| C | Vendor educational pages from reputable reagent providers | Used only as practical background when consistent with primary literature; not used as sole sequence authority. |
| Excluded | Student notes, unverified lecture-note mirrors, social media posts, random PDFs without institutional provenance, AI-generated summaries | Not used as supporting literature. |

### 2.2 Search themes used

- Plasmid vector foundations: pSC101, pBR322, pUC/M13, origin of replication, copy-number control.
- Classical and modern cloning: restriction/ligation, Golden Gate, MoClo, Gibson assembly, Gateway, LIC/SLIC, USER cloning.
- Expression-vector architecture: bacterial, mammalian, yeast, insect/baculovirus, plant binary vectors.
- Expression tuning: promoter strength, inducible promoters, RBS, Kozak context, UTRs, introns, poly(A), terminators, WPRE.
- Cargo design: codon optimization, fusion tags, solubility tags, affinity tags, linkers, secretion/localization signals.
- Quality and safety: sequencing/annotation, internal restriction-site audits, antibiotic-free selection, NIH recombinant/synthetic nucleic acid guidelines, HHS synthetic nucleic acid screening, WHO biosafety manual.
- Project-specific phage/VLP relevance: modular capsid/ligand ports, separated cargo and capsid-expression modules, and MS2 coat-protein vector lessons from uploaded project notes.

---

## 3. High-confidence literature map

### 3.1 Foundations of recombinant DNA and plasmid vectors

| Source | Authenticity check | Main lesson for vector design |
|---|---|---|
| Cohen, Chang, Boyer & Helling, 1973, *PNAS*, “Construction of biologically functional bacterial plasmids in vitro.” PMID: 4594039; DOI: 10.1073/pnas.70.11.3240 | Primary paper, PubMed/PNAS/PMC | Restriction-generated plasmid fragments can be joined in vitro and maintained as functional replicons after bacterial uptake. Foundational logic of restriction cloning. |
| Bolivar et al., 1977, *Gene*, “Construction and characterization of new cloning vehicles.” PMID: 344137 | Primary paper, PubMed | pBR322 established core vector concepts: defined ori, antibiotic markers, compact backbone, unique restriction sites. |
| Vieira & Messing, 1982, *Gene*, “The pUC plasmids, an M13mp7-derived system…” PMID: 6295879 | Primary paper, PubMed | pUC-family vectors popularized high-copy cloning, polylinkers/MCS, and convenient insert screening. |
| Yanisch-Perron, Vieira & Messing, 1985, *Gene*, “Improved M13 phage cloning vectors and host strains…” PMID: 2985470; DOI: 10.1016/0378-1119(85)90120-9 | Primary paper, PubMed | Compiled pUC/M13 sequences and host-strain improvements; important for sequence-traceable vector work. |
| del Solar et al., 1998, *Microbiol. Mol. Biol. Rev.*, “Replication and control of circular bacterial plasmids.” PMC/ASM | Peer-reviewed review | Copy number is controlled by replicon-specific regulation; ori choice is a design variable, not a default. |
| Nora et al., 2018, *Microbial Biotechnology*, “The art of vector engineering…” PMC | Peer-reviewed review | Vector design must account for host, payload, copy number, marker, transfer mode, and genetic context. |
| de Lorenzo, 2025, *Microbial Biotechnology*, “On the Choice of the Right Plasmid Vector(s)…” PMC | Peer-reviewed opinion/review | Recent reminder that origin, marker, copy number, and host-context are often more decisive than cloning method. |

### 3.2 Cloning and DNA-assembly methods

| Method | Key authentic sources | Best use cases | Main cautions |
|---|---|---|---|
| Restriction digestion + ligation | Cohen et al. 1973; MIT OCW recombinant DNA lectures; Addgene molecular biology reference | Simple insertions, legacy vectors, directional cloning with compatible unique sites | Internal restriction sites, non-directional insertion if same ends used, scars, limited modularity. |
| MCS/polylinker cloning | pUC/M13 literature; Addgene reference | Simple cloning and storage vectors | MCS sites must be unique; verify orientation and reading frame for expression vectors. |
| Gibson / overlap assembly | Gibson et al., 2009, *Nature Methods*, PMID: 19363495; DOI: 10.1038/nmeth.1318 | Scarless assembly, multi-fragment constructs, promoter/cassette replacement | Homology design, repetitive sequences, and large backbones can increase rearrangement risk. |
| Golden Gate / Type IIS | Engler et al., 2008, *PLoS ONE*, PMID: 18985154; Engler et al., 2009, PMID: 19436741; Weber et al., 2011, PMID: 21364738; Bird et al., 2022, *ACS Synth. Biol.* / PMC | Modular assembly, libraries, part-standard systems, rapid multi-part shuffling | Domesticate internal Type IIS sites; overhang fidelity matters; avoid incompatible or duplicated overhangs. |
| MoClo / hierarchical Type IIS assembly | Weber et al., 2011; Marillonnet/Golden Gate methods | Multi-gene constructs and standardized part libraries | Requires part standards; cloning scars/fusion sites must be compatible with ORF/domain design. |
| Gateway recombination | Hartley et al., 2000, *Genome Research*, PMID: 11076863; Katzen 2007; Reece-Hoyes & Walhout 2018 | High-throughput transfer of ORFs into many destination vectors | att-site scars can alter N/C-terminal fusions; proprietary enzyme systems; reading frames must match. |
| LIC | Aslanidis & de Jong, 1990, *Nucleic Acids Research*, PMID: 2235490 | Efficient directional cloning without ligase, useful for many protein-expression pipelines | Requires compatible tails/vector preparation; not as flexible for complex modular standards. |
| SLIC | Li & Elledge, 2007, *Nature Methods*, PMID: 17293868; Li & Elledge 2012 methods | Flexible homology-based assembly with fewer enzyme constraints | Homology-region design and PCR quality are critical; repetitive ends can misassemble. |
| USER / uracil-excision cloning | Bitinaite et al., 2007, PMID: 17341463; Bitinaite 2009 methods; Nour-Eldin et al. 2006 | Seamless cloning, mutagenesis, multi-fragment directional assembly | Requires dU-containing primers/fragments and compatible workflow design. |
| Yeast homologous recombination / TAR-style assembly | Yeast vector and homologous recombination literature | Large constructs, difficult repeats, library reconstruction | Host-specific, slower, and requires careful rescue/verification. |

### 3.3 Expression-vector architecture and host systems

| Host/system | Key sources | Vector-design emphasis | Typical caution points |
|---|---|---|---|
| **E. coli bacterial expression** | Tabor/Studier T7 system; Mierendorf pET system; Shilling et al. 2020 pET redesign; Francis & Page 2010 optimization; Addgene reference | Promoter/operator, RBS, terminator, tag/protease site, copy number, expression host compatibility | Toxic proteins, promoter leakiness, plasmid deletion, inclusion bodies, missing PTMs, codon/rare-tRNA issues. |
| **Mammalian transient/stable expression** | Boshart et al. 1985 CMV enhancer; Foecking & Hofstetter 1986 CMV promoter unit; Kozak/Cavener initiation context; Pfarr et al. 1986 poly(A); Makrides mammalian vectors | Mammalian promoter/enhancer, Kozak, intron/UTR, poly(A), mammalian selectable marker, episomal/integrating status | Promoter silencing, cell-type specificity, cryptic splice/polyA sites, first-AUG problems, backbone CpG/immunostimulation, antibiotic marker concerns for translational work. |
| **Yeast expression** | Vernet et al. 1987 yeast vectors; Mumberg et al. 1995 controlled expression; yeast expression-system reviews | 2µ vs CEN/ARS replication, auxotrophic or dominant selection, GAL1/TEF1/PGK1/AOX1-style promoter choice, secretion signal if needed | Promoter regulation depends on carbon source/strain; hyperglycosylation; plasmid stability; marker availability. |
| **Insect/baculovirus** | Jarvis 2009; Chambers 2018; Felberbaum 2015 | Transfer vector/bacmid strategy, polyhedrin/p10 promoters, secretion signal, epitope/purification tags | Viral vector handling and biosafety, baculovirus stability, glycosylation differences, passage-related variation. |
| **Plant binary vectors** | Bevan 1984; Komari 2006; plant vector reviews | T-DNA borders, plant promoter/terminator, plant selectable marker, bacterial + Agrobacterium replication modules | T-DNA border integrity, marker/regulatory concerns, transformation efficiency, tissue-specific promoter choice. |
| **Phage/VLP vectors and display systems** | Project MS2 notes, Addgene pMC037/pMC051 benchmarks, MS2 VLP literature | Separate capsid-expression and cargo modules; preserve capsid assembly; modular display/conjugation ports | Assembly disruption, valency control, packaging size constraints, cargo misloading, replication-function exclusion, immunogenicity. |

### 3.4 Expression tuning, cargo design, and protein tags

| Design topic | Key sources | Practical design principle |
|---|---|---|
| Bacterial RBS design | Salis et al., 2009/2011 RBS Calculator; Shine-Dalgarno literature | RBS strength depends on the local 5′ UTR and early coding sequence, not only a consensus motif. Use design libraries when exact expression level matters. |
| Mammalian translation initiation | Kozak/Cavener initiation-context literature | Include an appropriate Kozak context and avoid unintended upstream AUGs or uORFs when high expression from a cDNA is required. |
| Poly(A) / terminators | Pfarr et al. 1986; Addgene terminator/polyA resource; mammalian vector reviews | Terminator/poly(A) choice affects transcript termination, mRNA stability, and downstream readthrough. |
| WPRE and post-transcriptional elements | Loeb et al. 1999; Schambach et al. 2000; WPRE reviews | WPRE-like elements can boost expression but can be context-dependent and require safety-aware sequence selection. |
| Fusion and affinity tags | Young et al. 2012; Kimple et al. 2013; Costa et al. 2014; Köppl et al. 2022 | Tags improve purification, solubility, detection, or localization, but can change folding, activity, oligomerization, secretion, and immunogenicity. Include removable or alternative tag designs. |
| Codon optimization | Webster et al. 2017; Mauro & Chappell 2014; Bali & Bebok 2015; Moss et al. 2024 | Codon changes are not biologically silent. Optimize carefully for host expression while preserving folding-relevant pauses, mRNA features, splice avoidance, and regulatory motifs. |

### 3.5 Authentic lectures and educational resources

| Resource | Authenticity check | Use in this knowledge base |
|---|---|---|
| MIT OpenCourseWare, 7.01SC “Basic Mechanics of Cloning: Restriction Enzymes & Plasmids” | Official MIT OCW course page | Authentic lecture resource for restriction enzyme logic, DNA ligase, and recombinant DNA fundamentals. |
| MIT OpenCourseWare, 7.016 “Recombinant DNA, Cloning, & Editing” | Official MIT OCW lecture page/PDF | Authentic lecture resource for vector/insert terminology and cloning logic. |
| NCBI Bookshelf, “Studying DNA” and “Recombinant DNA” sections | Official NIH/NCBI textbook resource | Educational basis for cloning vectors, plasmid vectors, and recombinant DNA concepts. |
| Addgene Molecular Biology Reference and Plasmids 101 | Official Addgene educational/reference pages | Practical definitions for MCS, promoter, selectable marker, expression plasmid, viral plasmid, and plasmid types. |
| NEB Foundations of Molecular Cloning | Reputable reagent-provider educational article with primary references | Practical historical overview; used only when consistent with primary literature. |

---

## 4. Fundamental vector-design knowledge

### 4.1 Cloning vector vs expression vector

| Vector type | Minimum modules | Additional modules |
|---|---|---|
| Cloning/storage vector | Bacterial ori, bacterial selection marker, cloning site or recombination cassette, sequencing primer sites | Blue/white or negative selection, high-copy ori, multiple cloning sites, standardized part flanks. |
| Bacterial expression vector | Bacterial ori, bacterial marker, promoter/operator, RBS, ORF insertion site, stop codon, terminator | Fusion tag, protease site, solubility tag, secretion signal, low-copy option, toxicity-control elements. |
| Mammalian expression vector | Bacterial propagation module plus mammalian promoter/enhancer, Kozak/start context, ORF, poly(A), mammalian selection/reporter if needed | Intron, WPRE-like element, epitope tag, secretion/localization signal, inducible system, insulators. |
| Shuttle vector | Replication/selection modules for two hosts | Host-specific promoters and terminators, transfer/mobilization elements, integration cassettes. |
| Viral/vector-production plasmid | Transfer cassette plus viral-vector-specific elements | Split helper systems, packaging limits, safety deletions, ITR/LTR/border integrity. Handle under applicable biosafety rules. |
| VLP/phage-display vector | Capsid/display module, cargo module or packaging signal if relevant | Ligand ports, linker modules, purification tags, assembly controls, sequence-traceable capsid variants. |

### 4.2 Universal design architecture

```text
[Propagation module]
  bacterial ori / replicon + selectable marker + optional copy-number control

[Assembly module]
  MCS OR Type IIS acceptor OR Gateway/LIC/SLIC/USER interface
  + screening/negative-selection cassette if useful

[Expression-control module]
  promoter/enhancer/operator + RBS/Kozak/UTR/intron as host-appropriate

[Cargo module]
  ORF/RNA cassette/domain/gRNA + tags/linkers/signals + stop codon(s)

[Termination module]
  bacterial transcription terminator OR eukaryotic terminator/poly(A)

[Verification module]
  universal primer sites + feature coordinates + sequence checksum + map/version metadata

[Safety and compliance module]
  biosafety classification + sequence-screening status + antibiotic/resistance review
```

---

## 5. Practical design workflow

### Step 1 — Define the biological objective

Ask these questions before choosing the backbone:

- Is the goal DNA storage, protein expression, RNA expression, reporter activity, genome editing, phage/VLP display, or delivery?
- Which host must maintain the plasmid? Which host must express the cargo?
- Is high expression desirable, or will high expression be toxic or misleading?
- Is the final use discovery research, structural biology, cell biology, animal work, GMP/translational manufacturing, or diagnostics?

### Step 2 — Select the propagation backbone

Key choices:

- **Origin/replicon:** determines host compatibility and approximate copy number.
- **Copy number:** high copy improves DNA yield but can worsen toxicity, instability, or recombination; low/medium copy often improves stability for toxic, repetitive, or large constructs.
- **Selectable marker:** choose a marker compatible with host, downstream use, and institutional rules. For translational applications, consider antibiotic-free or removable marker strategies.
- **Backbone size:** smaller vectors often clone and sequence more easily; large vectors require stronger verification.

### Step 3 — Choose assembly method from design constraints

| Constraint | Preferred approach |
|---|---|
| Simple single insert, available unique restriction sites | Restriction/ligation or MCS cloning |
| Need scarless multi-fragment assembly | Gibson/HiFi-like overlap assembly or USER/SLIC |
| Need standardized modular part swapping or combinatorial library | Golden Gate/MoClo/Type IIS |
| Need to move same ORF into many expression contexts | Gateway or other recombinational cloning |
| Need high-throughput protein-expression entry clones | LIC/SLIC/Gateway-style pipelines |
| Need phage/VLP peptide-display library | Type IIS landing pads or recombinational part swapping, with assembly validation controls |

### Step 4 — Build expression control deliberately

#### Bacterial expression

- Choose promoter strength and inducibility based on cargo toxicity and desired expression level.
- Avoid defaulting to very strong T7 expression for proteins that are toxic, membrane-associated, disulfide-rich, multimeric, or aggregation-prone.
- Tune RBS and 5′ mRNA context; coding-sequence secondary structure near the start codon can dominate expression.
- Include a robust terminator to prevent readthrough into backbone elements.
- Use host strains appropriate for disulfide bonds, rare codons, membrane proteins, or toxic proteins when relevant.

#### Mammalian expression

- Choose promoter based on cell type, duration, and silencing risk. CMV is strong but can silence or vary by context; EF1α, CAG, PGK, UbC, tissue-specific, or inducible promoters may be better depending on the experiment.
- Add a suitable Kozak context for protein-coding ORFs.
- Check for upstream AUGs, cryptic splice sites, premature poly(A), and problematic repeats.
- Choose poly(A)/terminator elements deliberately; do not treat them as interchangeable.
- For stable expression, account for selection marker, integration strategy, promoter silencing, and copy-number variability.

#### Yeast/insect/plant expression

- Match ori/selection/promoter to host species and strain.
- Consider post-translational modifications, secretion, glycosylation, folding, and codon usage.
- For plant and baculovirus systems, verify border/viral-transfer elements and apply the relevant biosafety framework.

### Step 5 — Design cargo, tags, linkers, and boundaries

- Translate every designed ORF in silico in the intended reading frame.
- Confirm start codon, stop codon, tag frame, linker frame, signal peptide, cleavage site, and domain boundaries.
- Use flexible linkers for independent domain movement; use rigid linkers when domain spacing/orientation matters.
- Include removable tags when downstream activity, immunogenicity, crystallography, or structural analysis may be affected.
- Do not assume a tag is neutral. Test N-terminal, C-terminal, and tag-free options where function matters.

### Step 6 — Perform in silico verification before synthesis/cloning

Minimum in silico checks:

- Full plasmid map with all features annotated and versioned.
- ORF translation, reading frame, stop codon, and tag/linker boundaries.
- Internal restriction sites and Type IIS domestication status.
- Primers and sequencing coverage plan.
- GC content, repeats, homopolymers, secondary-structure risk near RBS/start, and recombination-prone elements.
- Insert orientation and promoter compatibility.
- Synthetic-nucleic-acid screening status for any ordered DNA.
- Biosafety classification and institutional approval requirements.

### Step 7 — Define controls and release criteria

At minimum:

- Empty vector or blank landing-pad control.
- Positive-expression control suitable for host system.
- Non-targeting or inert tag/ligand control for display/delivery vectors.
- Sequence-confirmed clone before biological interpretation.
- Expression and function readouts separated: expression ≠ solubility ≠ activity ≠ correct localization.

---

## 6. Core caution points for vector design

### 6.1 Origin, copy number, and stability

- **High copy number is not always better.** It can increase DNA yield but also increase metabolic burden, recombination, plasmid loss, and basal expression of toxic cargos.
- **Use compatible origins** when co-transforming multiple plasmids. Incompatible replicons can compete and destabilize plasmid maintenance.
- **Large inserts and repetitive sequences** often need low-copy or recombination-deficient propagation strategies.

### 6.2 Selectable markers

- Verify that the marker works in the propagation host and does not conflict with downstream selection.
- Ampicillin-like systems can allow satellite/background colonies in some settings; choose markers rationally.
- Translational, vaccine, gene-delivery, or environmental-release workflows should consider antibiotic-free, removable, or minimized backbones.

### 6.3 Promoters and expression toxicity

- Strong promoters can cause plasmid deletions, mutations, low transformation recovery, inclusion bodies, and misleading negative results.
- Inducible promoters may still leak; include uninduced and empty-vector controls.
- Promoter choice must match host and expression goal: a bacterial promoter will not drive mammalian expression, and a mammalian promoter will not drive bacterial propagation-marker expression.

### 6.4 Translation-initiation context

- In bacteria, the RBS/5′ UTR/start-codon region and early coding sequence act as one local mRNA-structure system.
- In mammalian cells, Kozak context and first-AUG logic matter; upstream AUGs and uORFs can reduce expression or produce wrong products.

### 6.5 Codon optimization

- Codon optimization can increase expression, but synonymous codons can affect mRNA stability, translation speed, protein folding, splicing, immune sensing, and domain behavior.
- Avoid blindly maximizing codon adaptation. Preserve known functional RNA structures, regulatory motifs, rare-codon pauses if relevant, and experimentally validated native sequences when function is sensitive.

### 6.6 Tags, linkers, localization, and cleavage sites

- Affinity and solubility tags can improve purification but alter folding, oligomerization, localization, immunogenicity, and activity.
- Test tag placement where possible. N-terminal and C-terminal tags can behave very differently.
- Protease-cleavage sites should not create unwanted residues at functional termini unless those residues are acceptable.

### 6.7 Terminators and poly(A) elements

- Weak or missing terminators can cause readthrough, unstable transcripts, and interference with downstream elements.
- Mammalian poly(A) signals differ in efficiency and sequence footprint; choose based on expression goal and vector-size constraints.

### 6.8 Assembly-method pitfalls

- Golden Gate requires removal/domestication of internal Type IIS sites and careful overhang design.
- Gibson/SLIC/USER require careful overlap/tail design; repetitive homology can misassemble.
- Gateway leaves att scars that can affect protein fusions and must be reading-frame compatible.
- Restriction cloning requires unique sites, correct orientation, and compatible ends.

### 6.9 Sequence verification and documentation

- Use versioned source sequences and record accession/URL/retrieval date.
- Sanger sequencing is usually sufficient for simple inserts, but large or repetitive constructs may require long-read, NGS, or full-plasmid sequencing.
- Maintain a change log and sequence checksum for each plasmid version.
- Do not use supplier text, screenshots, or unversioned web pages as sole sequence authority.

### 6.10 Biosafety and biosecurity

- Check institutional biosafety rules before constructing recombinant or synthetic nucleic acid molecules.
- Use current NIH Guidelines for recombinant/synthetic nucleic acid research when applicable.
- Apply synthetic-nucleic-acid sequence screening for ordered DNA/RNA, especially longer fragments and any sequences related to regulated pathogens, toxins, virulence, host range, or immune evasion.
- Be cautious with broad-host-range origins, mobilization/transfer elements, antibiotic-resistance markers, toxin genes, virulence genes, and replication-competent viral or phage systems.
- Keep therapeutic and environmental applications separate from routine research-plasmid assumptions.

---

## 7. Recommended vector templates

### 7.1 Generic cloning/storage vector

```text
[High/medium-copy bacterial ori]
[Selectable marker]
[Screening cassette or MCS]
[Universal sequencing primer sites]
[Minimal backbone annotation + checksum]
```

Use for sequence storage, mutagenesis intermediates, and simple subcloning. Keep compact and easy to sequence.

### 7.2 Bacterial expression vector

```text
[Ori chosen for stability]
[Selectable marker]
[Tunable promoter/operator]
[RBS + spacer]
[Optional N-terminal tag + protease site + linker]
[GOI/domain/ORF]
[Optional C-terminal tag]
[Stop codon(s)]
[Strong bacterial terminator]
[Sequencing primer sites]
```

Design notes:

- For toxic or aggregation-prone proteins, prioritize tunability and stability over maximal expression.
- Include tag-free or alternative-tag backup designs if activity matters.
- Confirm that the expression host supplies any required polymerase, repressor, tRNAs, chaperones, or redox environment.

### 7.3 Mammalian expression vector

```text
[Bacterial propagation ori + bacterial selectable marker]
[Mammalian promoter/enhancer]
[5' UTR / optional intron]
[Kozak + start codon]
[Signal peptide if secreted/membrane protein]
[GOI/ORF]
[Optional tag/linker/localization signal]
[Stop codon]
[3' UTR / WPRE-like element if justified]
[Poly(A)/terminator]
[Mammalian selection or reporter cassette if needed]
```

Design notes:

- Choose promoter for cell type and duration, not just peak expression.
- Avoid unnecessary viral elements in translational constructs unless justified.
- For stable cell lines, include promoter-silencing and copy-number considerations.

### 7.4 Modular Type IIS / Golden Gate vector

```text
[Propagation module]
[Negative-selection cassette flanked by outward Type IIS sites]
[Defined fusion-site/overhang standard]
[Optional barcode]
[Sequencing primer sites]
```

Design notes:

- Domesticate all parts against the chosen Type IIS enzymes.
- Document overhang standards and fusion scars.
- Use consistent part levels for promoter, UTR/RBS, coding sequence, tag, terminator, and selection modules.

### 7.5 Shuttle vector

```text
[E. coli ori + E. coli marker]
[Second-host ori/maintenance module + second-host marker]
[Host-specific expression cassette]
[Transfer/integration elements if needed]
```

Design notes:

- Separate propagation and expression modules in the map.
- Verify that selection and replication work independently in each host.
- Avoid unnecessary broad-host-range or mobilization elements if containment is important.

### 7.6 Phage/VLP display or cargo-delivery vector, project-relevant template

```text
[Safe propagation backbone]
[Inducible capsid/display expression cassette]
[Capsid protein OR capsid dimer module]
[Display landing pad: loop / terminal tag / SpyTag-like / sortase-like / click-compatible tag]
[Purification/analytics tag if needed]
[Terminator]

Separate cargo vector/cassette:
[Cargo expression or IVT module]
[Packaging/hairpin tags if relevant]
[Cargo ORF/RNA]
[UTR/poly(A) or appropriate RNA-stability elements]
```

Design notes:

- Keep capsid expression and cargo design separable during optimization.
- Avoid including full phage replication functions unless a specific, approved experiment requires them.
- Treat display insertion sites as structural hypotheses; validate assembly, size, morphology, ligand occupancy, and cargo loading separately.

---

## 8. Minimum sequence-verification workflow

| Gate | Required check | Why it matters |
|---|---|---|
| Source provenance | Accession, PMID/DOI/source URL, retrieval date | Prevents silent drift and misannotation. |
| Full-plasmid map | Annotated ori, marker, promoter, insert, tags, terminator, primers | Prevents feature confusion. |
| ORF translation | Translate from intended start to stop; verify tag/linker frame | Catches frameshifts and stop-codon errors. |
| Restriction/Type IIS audit | Internal sites, cloning sites, diagnostic digest sites | Prevents failed assembly and bad screens. |
| Primer coverage | Design sequencing primers across junctions and insert | Confirms the real construct matches the map. |
| Motif audit | RBS/Kozak, signal peptide, protease sites, epitopes, ligands, binding motifs | Protects biological function. |
| Safety audit | Synthetic sequence screening, gene class, host range, marker, vector replication status | Required for responsible recombinant DNA work. |
| Version control | Name, date, version, checksum, changelog | Makes future troubleshooting possible. |

---

## 9. Common failure modes and design-level fixes

| Failure mode | Likely vector-design causes | Design-level fixes |
|---|---|---|
| Few/no colonies | Toxic insert, wrong antibiotic, incompatible ori/host, bad linearization, large plasmid | Lower-copy backbone, negative-selection control, verify marker/host, choose less leaky expression design. |
| Many empty-vector clones | Non-directional cloning, incomplete backbone digestion, no negative selection | Use directional sites, Type IIS/Gateway/LIC, ccdB/sacB-style negative selection where appropriate. |
| Insert deletion/rearrangement | Repeats, high copy, toxic expression, recombination-prone strain | Use low-copy backbone, stable propagation strain, reduce basal expression, redesign repeats. |
| Correct DNA but no expression | Wrong promoter for host, poor RBS/Kozak, frameshift, missing start/stop, cryptic splice/polyA | Match expression module to host, translate ORF, redesign 5′ context, verify transcript. |
| Expression but insoluble/inactive protein | Too-strong expression, poor folding, tag interference, missing PTMs, wrong compartment | Use tunable promoter, solubility tags, alternative host, secretion/localization signal, lower-expression design. |
| Mammalian expression silences | Promoter choice, CpG/backbone burden, integration-site effects, selection pressure | Try EF1α/CAG/PGK/UbC/tissue-specific promoters, insulators, stable clone screening, minimized backbone. |
| Wrong fusion protein | att/MCS scar, linker frame error, extra residues after cleavage | Redesign fusion junction, verify translation, use scarless cloning or compatible reading-frame cassette. |
| Readthrough or background expression | Weak terminator, promoter leakiness, backbone promoter interference | Strong terminator, insulated promoter, repressor/tunable promoter, change backbone orientation. |

---

## 10. Project-specific notes for MS2/phage/VLP vector work

The existing project direction emphasizes MS2 coat-protein VLPs, mRNA cargo bearing MS2 hairpin/pac tags, CRC-targeting ligands, modular conjugation strategies, and Addgene pMC037-HisMS2_PLP_pac as a relevant benchmark. For this project family:

1. Use a **locked reference sequence** for any capsid protein and document every variant as explicit deltas.
2. Keep **capsid expression**, **display/ligand module**, and **cargo cassette** separable until assembly and cargo-loading behavior are understood.
3. Benchmark against published or repository vectors such as pMC037/pMC051, but avoid copying unnecessary replication or maturation functions into a therapeutic-like architecture.
4. Use **post-assembly or minimally disruptive display modules** first for ligand screening; direct loop insertions should be validated with blank-linker controls.
5. Build explicit release assays: particle identity, size/morphology, cargo loading, nuclease protection, ligand occupancy, target-positive vs target-negative uptake, translation/readout, and cytotoxicity.
6. For phage delivery concepts, apply a stricter biosafety review when adding host-range, tropism, replication, cargo-delivery, or antimicrobial payload functions.

---

## 11. Recommended repository structure

```text
Vector_Design_KB/
  00_index.md
  01_literature_screen/
    source_registry.md
    search_terms.md
    authenticity_audit.md
  02_vector_architecture/
    cloning_vectors.md
    bacterial_expression_vectors.md
    mammalian_expression_vectors.md
    yeast_insect_plant_vectors.md
    phage_vlp_vectors.md
  03_cloning_methods/
    restriction_ligation.md
    gibson_overlap_assembly.md
    golden_gate_moclo.md
    gateway.md
    lic_slic_user.md
  04_design_checklists/
    feature_map_checklist.md
    sequence_verification_checklist.md
    biosafety_checklist.md
  05_sequence_records/
    fasta/
    plasmid_maps/
    sequencing_primers/
    checksum_manifest.md
  06_project_notes/
    ms2_phage_vlp_vector_notes.md
  changelog.md
```

---

## 12. Design checklist for every new vector

Before ordering DNA or starting cloning, confirm:

- [ ] Objective and host system are defined.
- [ ] Vector type is defined: cloning, expression, shuttle, reporter, viral/VLP, genome editing, delivery.
- [ ] Origin/replicon and marker are compatible with host and downstream use.
- [ ] Promoter/enhancer/operator is correct for host and intended expression level.
- [ ] RBS/Kozak/UTR/intron/poly(A)/terminator modules are appropriate.
- [ ] ORF is translated in silico and annotated with domain boundaries.
- [ ] Tags/linkers/cleavage sites are in frame and biologically justified.
- [ ] Stop codon strategy is defined, especially for C-terminal tags.
- [ ] Assembly method is compatible with internal restriction/Type IIS/recombination sites.
- [ ] Diagnostic restriction/primer strategy is designed.
- [ ] Safety and synthetic-nucleic-acid screening are complete.
- [ ] Full plasmid map, source registry, and version record are saved.

---

## 13. Source registry

### 13.1 Primary papers and reviews

| ID | Source | PMID/DOI/URL | Category |
|---|---|---|---|
| COHEN-1973 | Cohen SN, Chang ACY, Boyer HW, Helling RB. Construction of biologically functional bacterial plasmids in vitro. *PNAS*. 1973. | PMID: 4594039; DOI: 10.1073/pnas.70.11.3240; https://pmc.ncbi.nlm.nih.gov/articles/PMC427208/ | Foundation |
| BOLIVAR-1977 | Bolivar F et al. Construction and characterization of new cloning vehicles. *Gene*. 1977. | PMID: 344137 | Foundation |
| VIEIRA-1982 | Vieira J, Messing J. The pUC plasmids. *Gene*. 1982. | PMID: 6295879 | Foundation |
| YANISCH-1985 | Yanisch-Perron C, Vieira J, Messing J. Improved M13 phage cloning vectors and host strains. *Gene*. 1985. | PMID: 2985470; DOI: 10.1016/0378-1119(85)90120-9 | Foundation |
| DELSOLAR-1998 | del Solar G et al. Replication and control of circular bacterial plasmids. *Microbiol Mol Biol Rev*. 1998. | https://pmc.ncbi.nlm.nih.gov/articles/PMC98921/ | Replication/copy number |
| DELSOLAR-2000 | del Solar G et al. Plasmid copy number control: an ever-growing story. *Mol Microbiol*. 2000. | PMID: 10931343 | Replication/copy number |
| NORA-2018 | Nora LC et al. The art of vector engineering. *Microbial Biotechnology*. 2018. | https://pmc.ncbi.nlm.nih.gov/articles/PMC6302727/ | Vector engineering |
| DELORENZO-2025 | de Lorenzo V. On the Choice of the Right Plasmid Vector(s). *Microbial Biotechnology*. 2025. | https://pmc.ncbi.nlm.nih.gov/articles/PMC12703808/ | Vector selection |
| GIBSON-2009 | Gibson DG et al. Enzymatic assembly of DNA molecules up to several hundred kilobases. *Nature Methods*. 2009. | PMID: 19363495; DOI: 10.1038/nmeth.1318 | Gibson/overlap assembly |
| ENGLER-2008 | Engler C et al. A one pot, one step, precision cloning method with high throughput capability. *PLoS ONE*. 2008. | PMID: 18985154 | Golden Gate |
| ENGLER-2009 | Engler C et al. Golden Gate shuffling. *PLoS ONE*. 2009. | PMID: 19436741 | Golden Gate |
| WEBER-2011 | Weber E et al. A modular cloning system for standardized assembly of multigene constructs. *PLoS ONE*. 2011. | PMID: 21364738 | MoClo |
| BIRD-2022 | Bird JE et al. User’s guide to Golden Gate cloning methods and standards. *ACS Synthetic Biology*. 2022. | https://pmc.ncbi.nlm.nih.gov/articles/PMC9680027/ | Golden Gate review |
| HARTLEY-2000 | Hartley JL et al. DNA cloning using in vitro site-specific recombination. *Genome Research*. 2000. | PMID: 11076863 | Gateway |
| KATZEN-2007 | Katzen F. Gateway recombinational cloning. | PMID: 23484762 | Gateway review |
| REECE-2018 | Reece-Hoyes JS, Walhout AJM. Gateway recombinational cloning. | PMID: 29295908; https://pmc.ncbi.nlm.nih.gov/articles/PMC5935001/ | Gateway review |
| ASLANIDIS-1990 | Aslanidis C, de Jong PJ. Ligation-independent cloning of PCR products. *Nucleic Acids Research*. 1990. | PMID: 2235490; https://pmc.ncbi.nlm.nih.gov/articles/PMC332407/ | LIC |
| LI-ELLEDGE-2007 | Li MZ, Elledge SJ. Harnessing homologous recombination in vitro to generate recombinant DNA via SLIC. *Nature Methods*. 2007. | PMID: 17293868 | SLIC |
| BITINAITE-2007 | Bitinaite J et al. USER friendly DNA engineering and cloning method. | PMID: 17341463; https://pmc.ncbi.nlm.nih.gov/articles/PMC1874603/ | USER |
| SALIS-2009 | Salis HM et al. Automated design of synthetic ribosome binding sites to control protein expression. | https://pmc.ncbi.nlm.nih.gov/articles/PMC2782888/ | RBS design |
| SALIS-2011 | Salis HM. The Ribosome Binding Site Calculator. | PMID: 21601672 | RBS design |
| DAVIS-2011 | Davis JH et al. Insulated bacterial promoters. *Nucleic Acids Research*. 2011. | DOI: 10.1093/nar/gkq810 | Promoter insulation |
| T7-STUDIER | Tabor S / Studier FW T7 promoter expression system literature. | PMID: 18265127; PMID: 21390849 | Bacterial expression |
| SHILLING-2020 | Shilling PJ et al. Improved pET expression plasmids increase protein production yield in E. coli. *Communications Biology*. 2020. | DOI: 10.1038/s42003-020-0939-8 | Bacterial expression |
| FRANCIS-2010 | Francis DM, Page R. Strategies to optimize protein expression in E. coli. | PMID: 20814932; https://pmc.ncbi.nlm.nih.gov/articles/PMC7162232/ | Bacterial expression |
| BOSHART-1985 | Boshart M et al. Strong enhancer upstream of HCMV immediate early gene. *Cell*. 1985. | PMID: 2985280 | Mammalian promoter |
| FOECKING-1986 | Foecking MK, Hofstetter H. Powerful and versatile enhancer-promoter unit for mammalian expression. | PMID: 3023199 | Mammalian promoter |
| KOZAK-1987 | Kozak/Cavener initiation-context literature. | PMID: 3822832; https://pmc.ncbi.nlm.nih.gov/articles/PMC340553/ | Mammalian translation |
| PFARR-1986 | Pfarr DS et al. Differential effects of polyadenylation regions on gene expression. | PMID: 2872023 | Poly(A) |
| LOEB-1999 | Loeb JE et al. WPRE enhances expression. | PMID: 10515449 | Post-transcriptional element |
| MAKRIDES-2004 | Makrides SC. Vectors for gene expression in mammalian cells. | https://pmc.ncbi.nlm.nih.gov/articles/PMC7147855/ | Mammalian expression |
| VERNET-1987 | Vernet T et al. A family of yeast expression vectors. *Gene*. 1987. | PMID: 3038686 | Yeast expression |
| MUMBERG-1995 | Mumberg D et al. Yeast vectors for controlled expression. | PMID: 7737504 | Yeast expression |
| JARVIS-2009 | Jarvis DL. Baculovirus-insect cell expression systems. | PMID: 19892174 | Insect/baculovirus |
| CHAMBERS-2018 | Chambers AC et al. Overview of the baculovirus expression system. | PMID: 29516481 | Insect/baculovirus |
| FELBERBAUM-2015 | Felberbaum RS. Baculovirus expression vector system. | https://pmc.ncbi.nlm.nih.gov/articles/PMC7159335/ | Insect/baculovirus |
| BEVAN-1984 | Bevan M. Binary Agrobacterium vectors for plant transformation. | PMID: 6095209 | Plant binary vectors |
| KOMARI-2006 | Komari T et al. Binary vectors and super-binary vectors. | PMID: 16988331 | Plant binary vectors |
| YOUNG-2012 | Young CL et al. Recombinant protein expression and purification: affinity/solubility tags. | PMID: 22442034 | Tags/purification |
| KIMPLE-2013 | Kimple ME et al. Overview of affinity tags for protein purification. | https://pmc.ncbi.nlm.nih.gov/articles/PMC4527311/ | Tags/purification |
| COSTA-2014 | Costa S et al. Fusion tags for protein solubility, purification and immunogenicity. | https://pmc.ncbi.nlm.nih.gov/articles/PMC3928792/ | Tags/purification |
| KOPPL-2022 | Köppl C et al. Fusion tag design influences soluble recombinant protein. | https://pmc.ncbi.nlm.nih.gov/articles/PMC9321918/ | Tags/purification |
| WEBSTER-2017 | Webster GR et al. Synthetic gene design—the rationale for codon optimization. | PMID: 27618314 | Codon optimization |
| MAURO-2014 | Mauro VP, Chappell SA. Critical analysis of codon optimization in human therapeutics. | https://pmc.ncbi.nlm.nih.gov/articles/PMC4253638/ | Codon caution |
| BALI-2015 | Bali V, Bebok Z. Silent codon changes affect gene expression and folding. | PMID: 25817479; https://pmc.ncbi.nlm.nih.gov/articles/PMC4461553/ | Codon caution |
| MOSS-2024 | Moss MKJ et al. Effects of codon usage on protein structure and folding. | PMID: 38134335; https://pmc.ncbi.nlm.nih.gov/articles/PMC11227313/ | Codon caution |
| WILLIAMS-2009 | Williams JA. Plasmid DNA vaccine vector design: impact on efficacy, safety and upstream production. | https://pmc.ncbi.nlm.nih.gov/articles/PMC2693335/ | Translational vector design |
| CARNES-2010 | Carnes AE et al. Antibiotic-free vector design criteria. | PMID: 20806425 | Antibiotic-free vectors |
| MIGNON-2015 | Mignon C et al. Antibiotic-free selection in biotherapeutics. | https://pmc.ncbi.nlm.nih.gov/articles/PMC4493468/ | Antibiotic-free vectors |

### 13.2 Guidelines and official educational resources

| ID | Resource | URL | Use |
|---|---|---|---|
| NIH-GUIDELINES-2024 | NIH Guidelines for Research Involving Recombinant or Synthetic Nucleic Acid Molecules, April 2024 | https://osp.od.nih.gov/wp-content/uploads/NIH_Guidelines.htm | Biosafety framework |
| HHS-SYNNA-2023 | HHS Screening Framework Guidance for Synthetic Nucleic Acids, 2023 | https://aspr.hhs.gov/S3/Pages/Synthetic-Nucleic-Acids.aspx | Synthetic DNA/RNA screening |
| WHO-LBM-2020 | WHO Laboratory Biosafety Manual, 4th edition | https://www.who.int/publications/i/item/9789240011311 | Risk assessment and biosafety |
| ADDGENE-MOLBIO | Addgene Molecular Biology Reference | https://www.addgene.org/mol-bio-reference/ | Vector-element definitions |
| ADDGENE-PLASMIDS101 | Addgene Plasmids 101 eBook/blog series | https://www.addgene.org/educational-resources/ebooks/ | Practical plasmid education |
| MIT-OCW-CLONING | MIT OCW 7.01SC Basic Mechanics of Cloning | https://ocw.mit.edu/courses/7-01sc-fundamentals-of-biology-fall-2011/pages/recombinant-dna/basic-mechanics-of-cloning/ | Authentic lecture resource |
| MIT-OCW-RDNA | MIT OCW 7.016 Recombinant DNA, Cloning, & Editing | https://ocw.mit.edu/courses/7-016-introductory-biology-fall-2018/resources/lecture-16-recombinant-dna-and-cloning/ | Authentic lecture resource |
| NCBI-STUDYING-DNA | NCBI Bookshelf, Studying DNA | https://www.ncbi.nlm.nih.gov/books/NBK21129/ | Authoritative educational reference |
| NCBI-RDNA | NCBI Bookshelf, Recombinant DNA | https://www.ncbi.nlm.nih.gov/books/NBK9950/ | Authoritative educational reference |
| NEB-FOUNDATIONS | NEB Molecular Cloning Technology — Past, Present and Future | https://www.neb.com/en-au/tools-and-resources/feature-articles/foundations-of-molecular-cloning-past-present-and-future | Background with primary references |

---

## 14. Limitations

This knowledge base is a curated technical foundation, not a formal systematic review or regulatory submission. It emphasizes authentic, high-impact, and broadly useful sources. For any specific construct, the exact sequence, host strain/cell line, biosafety classification, institutional approval path, and freedom-to-operate/IP status must be checked separately.

---

## 15. Immediate next actions for vector-design work

1. Choose the exact first-use case: bacterial protein expression, mammalian expression, MS2 VLP capsid expression, cargo cassette, or modular ligand-display vector.
2. Create a one-page design brief for each vector with objective, host, cargo, expression level, readout, and biosafety classification.
3. Build a feature map before cloning: ori, marker, promoter, RBS/Kozak, insert, tags, terminator/poly(A), primer sites.
4. Select assembly method based on modularity needs: Golden Gate for part libraries; Gibson/SLIC/USER for scarless constructs; Gateway/LIC for high-throughput ORF transfer; restriction cloning only when simple and unambiguous.
5. Define verification release criteria before DNA ordering: sequence coverage, motif audits, internal site audit, and biological controls.
6. For MS2/phage/VLP work, keep capsid, display, and cargo modules separable and verify assembly/cargo/loading independently.
