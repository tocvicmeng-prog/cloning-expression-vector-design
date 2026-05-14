# Cloning and Expression Vector Design — A First-Principles White Paper
### A Conceptual Foundation for Designing and Building Vectors in Bacterial, Plant, and Mammalian Cells

**Author:** Scientific Advisor (in the role of a Senior Molecular Biology scientist)
**Audience:** Project orchestrators (the dev-orchestrator), software architects (the architect), and first-time learners of molecular cloning. No prior molecular-biology background is assumed.
**Companion source-of-truth document:** `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` (quantitative parameters, citations, parts catalogues).
**This document:** the conceptual story written from the beginning. Every term is defined on first use. Every complex process is preceded by a workflow diagram.
**Prepared:** 2026-05-13.

---

## Preface — How to read this paper

This paper is not a list of recipes; it is a *map of the territory*. Once you can hold the map in your head, every choice the software has to make — which origin, which promoter, which assembly chemistry, which terminator — becomes obvious from the requirements rather than learned by rote.

We will build the picture in six movements:

```
   I.  THE SETTING
       What problem are we solving, and inside which kind of cell?

  II.  THE OBJECT
       What is a vector? What does it have to contain, and why?

 III.  THE CHEMISTRY
       How do we physically put a new piece of DNA into a vector?

  IV.  THE THREE HOSTS
       Why bacteria, plant cells, and mammalian cells are different
       chassis with different rules.

   V.  THE WORKFLOW
       The end-to-end path from a biological question to a verified
       working construct.

  VI.  THREE WORKED EXAMPLES
       One bacterial, one plant, one mammalian.
```

A short glossary appears in the appendix and links back to the section where each term is introduced.

---

# PART I — THE SETTING

## 1. Why we need vectors

Every modern molecular-biology experiment, every protein-based medicine, every engineered crop, every diagnostic kit, and every gene therapy has the same underlying need: we want a particular cell to do something it was not natively programmed to do. To do that, we have to deliver a new instruction — a piece of DNA carrying that instruction — into the cell, and we have to make sure that instruction is *read*, *interpreted*, and *acted upon*.

A naked piece of DNA, by itself, cannot survive the journey. The cell's own machinery will destroy unfamiliar DNA, dilute it as the cell divides, and ignore it because it has no recognisable signals to tell the cell how to read it. So we package our instruction inside a **vector**: a small, self-sufficient piece of DNA that carries everything the cell needs to (1) keep the DNA from being destroyed, (2) copy it as the cell grows, and (3) read it correctly.

> **Vector** — a piece of DNA engineered to carry another piece of DNA (the cargo) into a living cell, where the vector ensures that the cargo is preserved and, optionally, expressed (read out into RNA and/or protein).
>
> **Cargo** — the piece of DNA the experimenter wants the cell to host. Often a single gene (the *Gene Of Interest*, GOI), sometimes a small RNA, sometimes a regulatory cassette.

A vector is *not* a delivery vehicle in the same sense as a pill or an injection — it is a piece of DNA that, once inside the cell, behaves like a small extra chromosome.

Two related but distinct jobs that a vector might do:

| Job | What the vector does | Common name |
|---|---|---|
| Keep a piece of DNA safe so we can grow more of it | Maintains the DNA in a fast-growing host like *E. coli*; we make millions of copies, then purify them. | **Cloning vector** |
| Cause the host cell to produce the encoded RNA or protein | Same as above *plus* contains the signals that make the host's transcription and translation machinery read the gene. | **Expression vector** |

Every expression vector is also a cloning vector (you have to grow it up first); not every cloning vector is an expression vector.

## 2. A primer on cells — three chassis we will design for

A **cell** is the smallest unit of life. It is enclosed by a membrane, contains DNA that encodes its operating instructions, and runs a metabolism that turns nutrients into energy and into more cells. For our purposes, three classes of cell matter:

### 2.1 Bacterial cells (the worker)

Bacteria such as *Escherichia coli* are **prokaryotes**: a single compartment, no nucleus, a single circular chromosome floating in the cytoplasm, and the ability to maintain extra small circular DNAs called **plasmids**.

```
              BACTERIAL CELL (E. coli, schematic)

                  ┌──────────────────────────────┐
                  │  outer membrane              │
                  │   ┌────────────────────────┐ │
                  │   │ inner membrane         │ │
                  │   │  ┌──────────────────┐  │ │
                  │   │  │ cytoplasm        │  │ │
                  │   │  │                  │  │ │
                  │   │  │   ◯ chromosome   │  │ │
                  │   │  │      ⌒           │  │ │
                  │   │  │   ○ ○ ○ plasmids │  │ │
                  │   │  │  (the vector!)   │  │ │
                  │   │  │  ribosomes:      │  │ │
                  │   │  │   • • • • • • •  │  │ │
                  │   │  └──────────────────┘  │ │
                  │   └────────────────────────┘ │
                  └──────────────────────────────┘
                       (≈ 2 µm long, ~ 1 hour generation time)
```

Why bacteria are central:

- They divide very fast (≈ 20 min per generation under good conditions); we can grow up huge amounts of DNA from a single colony overnight.
- They are easy to grow in cheap medium.
- They naturally maintain plasmids, and we have a century of accumulated tools to manipulate them.
- They lack a nucleus, so transcription and translation happen in the same compartment, and ribosomes can attach to mRNA as soon as it is being made.

What bacteria cannot do well:

- They cannot perform most **eukaryotic post-translational modifications** (modifications added to a protein after it is made), including N-linked glycosylation (sugar attachment), proper disulfide-bond formation in the cytoplasm (without engineered strains), and many phosphorylation patterns.
- They use **σ-factor**-based transcription and have different promoter recognition rules from eukaryotes.
- They have small ribosomes that recognise an entirely different start-of-translation signal (the Shine–Dalgarno sequence) than eukaryotes do.

### 2.2 Plant cells (the green factory)

Plant cells are **eukaryotes**: they have a nucleus that holds the chromosomes, a complex internal structure with organelles (mitochondria, chloroplasts, vacuole), and — uniquely — a rigid cellulose cell wall outside the plasma membrane.

```
                  PLANT CELL (schematic)

      ┌──────────────────────────────────────────────────┐
      │  cell wall (cellulose)                          │
      │   ┌────────────────────────────────────────────┐ │
      │   │ plasma membrane                            │ │
      │   │  ┌──────────────────────────────────────┐  │ │
      │   │  │ cytoplasm                            │  │ │
      │   │  │   ┌─────────┐                        │  │ │
      │   │  │   │ nucleus │  (chromosomes inside)  │  │ │
      │   │  │   │   DNA   │                        │  │ │
      │   │  │   └─────────┘                        │  │ │
      │   │  │   ▮▮ chloroplasts (photosynthesis)   │  │ │
      │   │  │   ◇ mitochondria (energy)            │  │ │
      │   │  │   ◯◯◯◯ vacuole (large central)       │  │ │
      │   │  │   • • ribosomes • •                  │  │ │
      │   │  └──────────────────────────────────────┘  │ │
      │   └────────────────────────────────────────────┘ │
      └──────────────────────────────────────────────────┘
```

The features that change vector design:

- The cell wall is a physical barrier; we cannot simply heat-shock or electroporate naked DNA into a plant cell as we do in bacteria. We typically deliver DNA via a **soil bacterium**, *Agrobacterium tumefaciens*, which has evolved to inject a piece of DNA (called the **T-DNA**) into plant cells. Our vector mimics that natural T-DNA.
- The nucleus and the cytoplasm are separated, so the **mRNA** (messenger RNA, the working copy of a gene) is made in the nucleus and exported to the cytoplasm before it is read into protein.
- Plants perform glycosylation and other modifications differently from mammals; some — but not all — therapeutic proteins are compatible with plant-style glycosylation.

### 2.3 Mammalian cells (the most complex chassis)

Mammalian cells (e.g., HEK293 cells from a human kidney lineage, CHO cells from Chinese hamster ovary, or primary cells from a tissue donor) are eukaryotes like plant cells, but without a cell wall. They are used because they perform **human-like post-translational modifications**, making them the chassis of choice for antibody manufacturing, gene therapy, and most therapeutic-protein work.

```
                  MAMMALIAN CELL (schematic)

                   ┌──────────────────────────────┐
                   │ plasma membrane              │
                   │  ┌────────────────────────┐  │
                   │  │ cytoplasm              │  │
                   │  │   ┌───────────┐        │  │
                   │  │   │  nucleus  │        │  │
                   │  │   │   DNA     │        │  │
                   │  │   └───────────┘        │  │
                   │  │   ER (folding)         │  │
                   │  │   Golgi (sorting)      │  │
                   │  │   ◇ mitochondria       │  │
                   │  │   • • ribosomes • •    │  │
                   │  └────────────────────────┘  │
                   └──────────────────────────────┘
```

Important consequences for vector design:

- Mammalian transcription requires a **promoter** that the mammalian polymerase II machinery recognises (bacterial promoters do nothing in mammalian cells).
- Mammalian translation starts at a **Kozak context** rather than a Shine–Dalgarno sequence.
- Mammalian transcripts need a **5′ cap** and a **polyadenylation (polyA) signal** at the 3′ end to be stable and exported.
- Mammalian cells contain machinery that *splices* RNA — removes some sections, joins others. Hidden splice signals inside a designed gene can cause silent destruction of the transcript.

A single side-by-side comparison is the foundation of host-specific design:

```
    BACTERIA              PLANT CELL              MAMMALIAN CELL
    ─────────────         ──────────              ────────────────
    No nucleus            Nucleus + walls          Nucleus, no wall
    Shine-Dalgarno        Kozak (eukaryotic)       Kozak (eukaryotic)
    No splicing           Splices                  Splices
    No mRNA cap           5′ cap + polyA           5′ cap + polyA
    No N-glycosylation    Plant-type N-glyc        Mammalian N-glyc
    σ-factor promoters    Pol II promoters         Pol II promoters
    20-min generation     Days–weeks growth        ~24 h generation
    Easy DNA uptake       Via Agrobacterium        Via transfection / virus
```

These differences explain why a vector that works perfectly in bacteria will produce *no protein at all* in a mammalian cell — and vice versa — even though both vectors carry the same coding sequence.

## 3. A primer on DNA, RNA, and protein — the central dogma

To design vectors, we have to keep in mind a flow of information that every cell on Earth performs. This flow is called the **central dogma of molecular biology**.

```
   ╔══════════════════════════════════════════════════════╗
   ║                  THE CENTRAL DOGMA                   ║
   ╚══════════════════════════════════════════════════════╝

   ┌───────┐    transcription    ┌───────┐    translation     ┌──────────┐
   │  DNA  │ ──────────────────► │  RNA  │ ─────────────────► │ PROTEIN  │
   │       │                     │ (mRNA)│                    │          │
   └───────┘                     └───────┘                    └──────────┘
       ▲                                                            │
       │                                                            │
       └────── replication (DNA copies itself, cell-cycle dependent)
```

Let me unfold this:

**DNA (deoxyribonucleic acid)** is a long double-stranded molecule made of four chemical letters: A, T, G, C. The two strands are held together by specific base-pairings (A pairs with T; G pairs with C) and run in opposite directions ("5′ to 3′" and "3′ to 5′"). The letters' sequence is the information.

```
   5'  ── A T G G C T A G A T C C ──  3'        (sense / coding strand)
          │ │ │ │ │ │ │ │ │ │ │ │
   3'  ── T A C C G A T C T A G G ──  5'        (antisense / template strand)
```

**Transcription** is the process by which an enzyme called **RNA polymerase** reads a DNA template strand and produces a single-stranded copy in **RNA**. RNA has the same four-letter alphabet except T is replaced by U (uracil).

```
   DNA template:    3'  T A C C G A T C T A G G  5'
                          │ │ │ │ │ │ │ │ │ │ │ │
   mRNA produced:   5'  A U G G C U A G A U C C  3'
```

In bacteria, transcription is started by RNA polymerase binding to a **promoter** sequence and ending at a **terminator** sequence. In eukaryotes, transcription is performed by three different polymerases (Pol I, II, III) for three different categories of RNA. Protein-coding genes are transcribed by **Pol II**, which requires a Pol-II-class promoter, makes a primary RNA that is then **capped**, **spliced**, and **polyadenylated** before it leaves the nucleus as a mature mRNA.

**Translation** is the process by which **ribosomes** read the mRNA in groups of three letters (called **codons**) and assemble a protein from the corresponding amino acids. Every three RNA letters specify one amino acid (or a stop signal). There are 64 possible codons and 20 standard amino acids plus three stop codons (UAA, UAG, UGA), so most amino acids are encoded by more than one codon — this redundancy is what allows **codon optimisation** later.

```
   mRNA:    5'  A U G   G C U   A G A   U C C   U A A  3'
                 │       │       │       │       │
   amino-acid:   Met     Ala     Arg     Ser    STOP
```

The first AUG of an mRNA is the start of translation in most cases; the protein chain elongates until a stop codon is reached. The first amino acid is **methionine** (Met) in eukaryotes and most bacterial proteins.

**Protein** is a linear chain of amino acids that folds into a three-dimensional shape determined by its sequence. The shape is what does the biological work: enzyme catalysis, structural support, signalling, transport, immune recognition.

**Why this matters for vector design.** Every layer of a vector exists to control some step in this flow:

| Vector element | Step it controls |
|---|---|
| Origin of replication | DNA replication (copy the plasmid as the cell divides) |
| Promoter | Transcription start (RNA polymerase loading) |
| 5′ UTR / RBS / Kozak | Translation start (ribosome loading) |
| ORF / cargo | What protein gets made |
| Stop codon | Translation end |
| Terminator / polyA | Transcription end (and, in eukaryotes, mRNA stability) |
| Selectable marker | Survival (cells that lost the vector get killed by the selection agent) |

If you remember the central dogma diagram and which vector element controls which step, vector design is no longer mysterious — it is a list of decisions, one per step.

## 4. The plasmid — biology's natural circular DNA

Before the engineers, bacteria had already invented the plasmid: a small circular DNA, separate from the main chromosome, that replicates independently and often carries useful "extra" genes (antibiotic resistance, virulence factors, metabolic capabilities) which the bacterium can share with neighbours.

Three structural facts about plasmids matter:

1. **Circular**. There are no ends. Replication initiates at a defined origin and proceeds around the circle. (Some viral and synthetic vectors are linear, but the canonical cloning vector is circular.)
2. **Double-stranded**. Like the chromosome.
3. **Small**. Natural plasmids are typically 1–100 kilobases (kb); engineered vectors are typically 3–10 kb but can reach hundreds of kb (BAC, YAC).

A modern cloning vector is a *minimal plasmid* in which the natural "extras" have been replaced with engineered modules. Let us draw one.

```
              A GENERIC PLASMID (annotated)

                         ╭────────╮
                       ╭─┤ MCS    ├─╮      ← where we put new DNA
                      │  │ (cloning  │
                      │  │  site)    │
                      │  ╰─────────╯  │
                      │               │
                      │  ╭──────────╮ │
                      │  │ promoter │ │     ← turns the gene on
                      │  │ + RBS    │ │
                      │  ╰──────────╯ │
                  ╭───┤               ├──╮
                  │   │                  │
   start ────►    │   │       ORF        │   ← the gene (cargo)
   replication    │   │       (where      │
   here           │   │       protein-   │
   ◯ ori          │   │       coding     │
                  │   │       DNA goes)  │
                  │   │                  │
                  ╰───┤                  ├──╯
                      │  ╭───────────╮  │
                      │  │ terminator│  │   ← turns the gene off
                      │  ╰───────────╯  │
                      │                 │
                      │  ╭────────────╮ │
                      │  │ selectable │ │   ← lets us pick cells
                      │  │ marker     │ │     that took up the vector
                      │  │ (Abx res)  │ │
                      │  ╰────────────╯ │
                      ╰─────────────────╯
                       (typically 3–10 kb total)
```

Every clamour of the rest of this paper is, in some way, an answer to: *what should I put in each of those boxes?*

---

# PART II — THE OBJECT: WHAT A VECTOR ACTUALLY CONTAINS

## 5. Cloning vs expression — sharpening the distinction

It is worth pausing on the distinction we glossed in §1.

| Property | Cloning vector | Expression vector |
|---|---|---|
| Job | Preserve and replicate DNA in a host (usually *E. coli*) | Same *plus* drive the cargo's transcription and translation in a target host |
| Required parts | Origin, selectable marker, cloning site | Origin, selectable marker, cloning site, promoter, RBS or Kozak, terminator/polyA |
| Cargo readout | The cargo is *not* expressed in the cloning host (or only weakly and incidentally) | The cargo *is* expressed in the target host |
| Typical hosts | *E. coli* (DH5α, TOP10, XL1-Blue) | Any of: *E. coli* (BL21), yeast, mammalian (HEK293, CHO), plant (via *Agrobacterium*), insect (via baculovirus) |

In practice, almost every modern expression vector is a **shuttle vector** — it can both (a) replicate in *E. coli* for amplification and storage and (b) express its cargo in the target host. So an expression vector has *two* origin/marker pairs in most designs: one bacterial side, one target-host side.

## 6. The six-layer architecture

Any cloning or expression vector can be analysed as six interacting layers. Picture them like the floors of a building; each is independent in function, but the whole only works if they are stacked correctly.

```
┌────────────────────────────────────────────────────────┐
│ LAYER 6.  QUALITY & METADATA                          │
│   feature annotation, sequence checksum, provenance,  │
│   licence (MTA), version control                      │
├────────────────────────────────────────────────────────┤
│ LAYER 5.  TERMINATION                                 │
│   bacterial terminator OR eukaryotic polyA + term.    │
├────────────────────────────────────────────────────────┤
│ LAYER 4.  CARGO (the GOI)                             │
│   start codon, ORF, tags, signal peptides, linkers,   │
│   protease sites, stop codon(s)                       │
├────────────────────────────────────────────────────────┤
│ LAYER 3.  EXPRESSION CONTROL                          │
│   promoter / enhancer / operator                      │
│   + RBS (bacteria) or Kozak + 5′ UTR (eukaryotes)     │
├────────────────────────────────────────────────────────┤
│ LAYER 2.  ASSEMBLY INTERFACE                          │
│   MCS, Type IIS acceptor cassette, recombination      │
│   sites, homology arms — how the cargo gets in        │
├────────────────────────────────────────────────────────┤
│ LAYER 1.  PROPAGATION                                 │
│   origin of replication, selectable marker, copy      │
│   number control, host range                          │
└────────────────────────────────────────────────────────┘
```

The rest of Part II expands each layer and shows the parts catalogue (curated in the companion knowledge base) you will choose from.

## 7. Layer 1 — Propagation

The propagation layer is the answer to: *how does this DNA survive and multiply once it enters a host cell?*

### 7.1 The origin of replication (ori)

> **Origin of replication (ori)** — a specific DNA sequence at which the host's replication machinery initiates copying of the plasmid. Every plasmid must have at least one ori for the host it needs to replicate in. Different oris work in different hosts.

The ori does two jobs:

1. It is *recognised* by the host's replication initiator proteins.
2. Its built-in regulatory elements *set the copy number* — the number of plasmid molecules per cell.

Copy number is a design parameter:

| Ori family | Host | Copies per cell | Typical use |
|---|---|---|---|
| pMB1 mutant (pUC) | *E. coli* | 500–700 | Standard cloning; lots of DNA in a miniprep. |
| ColE1 (pBR322) | *E. coli* | 15–20 | Stable; useful for sensitive constructs. |
| p15A | *E. coli* | 10–12 | Compatible with ColE1 — can co-exist in one cell. |
| pSC101 | *E. coli* | ~ 5 | Very low copy; stable for difficult inserts. |
| F-factor (BAC) | *E. coli* | 1–2 | For inserts up to 300 kb (Bacterial Artificial Chromosome). |
| 2µ | *S. cerevisiae* | 30–50 | Yeast multi-copy. |
| CEN/ARS | *S. cerevisiae* | 1–2 | Yeast single-copy, stable. |
| SV40 ori (+ Large T-Ag) | mammalian | transient amplification | Only in cells expressing Large T-antigen. |
| EBV oriP (+ EBNA1) | mammalian | stable episomal | Long-term episomal maintenance. |
| AAV ITRs | mammalian (in AAV) | template for AAV packaging | 145-nt inverted-terminal-repeats flank cargo. |

**Why "copy number is a design parameter, not a default":** more copies = more DNA per cell = more product when expression is active. *But* more copies = more metabolic burden, more recombination of repeats, more plasmid loss when expression is leaky and toxic. For a stable, large, or toxic construct, fewer copies are usually better. For a small, friendly cargo where we want maximum DNA yield, more copies are better.

### 7.2 The selectable marker

> **Selectable marker** — a gene on the vector that, when expressed, lets the host cell survive a condition that kills cells lacking the vector. Almost always an antibiotic-resistance gene (in bacteria) or a drug-resistance / auxotrophy-rescue gene (in eukaryotes).
>
> **Antibiotic** — a small-molecule drug that kills bacteria (or, in some cases, eukaryotic cells).
>
> **Auxotrophy** — the inability of a strain to make a particular metabolite (e.g., the amino acid uracil); the strain can only grow if the missing metabolite is provided or if the missing gene is restored on a plasmid.

Common bacterial markers and their working concentrations:

| Marker | Working concentration | Note |
|---|---|---|
| Ampicillin (β-lactamase, *bla*) | 50–100 µg/mL | The β-lactamase is secreted; over long incubations the antibiotic is degraded in the medium and "satellite colonies" appear. Carbenicillin (50 µg/mL) is more stable. |
| Kanamycin (aminoglycoside phosphotransferase, *aph*) | 25–50 µg/mL | Intracellular; no satellites. Common default. |
| Chloramphenicol (CAT) | 25–34 µg/mL | Bacteriostatic; pairs well with low-copy origins. |
| Spectinomycin | 50–100 µg/mL | Plant binary vectors (Agrobacterium side). |
| Gentamicin | 10–15 µg/mL | Agrobacterium binary vectors. |

Common mammalian markers:

| Marker | Working concentration | Kill kinetics |
|---|---|---|
| Puromycin (*pac*) | 0.5–10 µg/mL | Fast (2–4 days). |
| Blasticidin (*bsr*) | 2–25 µg/mL | Moderate (5–7 days). |
| G418 / Geneticin (*neo*) | 200–1000 µg/mL | Slow (7–14 days). |
| Hygromycin B (*hph*) | 100–600 µg/mL | Moderate. |
| Zeocin (*sh ble*) | 50–500 µg/mL | Light-sensitive; protect from light. |

**Auxotrophic markers** are the antibiotic-free alternative — common in yeast (URA3, LEU2, HIS3, TRP1, LYS2, ADE2). Used with strains that have a deletion in the corresponding gene; the plasmid restores function.

### 7.3 Host range

A plasmid only replicates in cells whose machinery matches its ori. pUC-class vectors replicate in most *E. coli* lab strains. RK2/RP4-class plasmids replicate in many Gram-negative bacteria. A mammalian episomal vector with EBV oriP works in some human cell lines (B-cell-derived, kidney) but not others. **Shuttle vectors** carry *two* origins so they can move between hosts (e.g., *E. coli* for cloning + yeast for expression).

## 8. Layer 2 — The assembly interface

The assembly interface is the answer to: *how do we physically get the cargo into the vector?*

### 8.1 The classical multiple-cloning site (MCS)

> **Multiple cloning site (MCS)** — a short region of DNA, also called a *polylinker*, that contains unique recognition sites for several different **restriction enzymes**. The MCS is the "loading dock" where the user can cut the vector open and insert a cargo.
>
> **Restriction enzyme** — a bacterial enzyme that cuts DNA at a specific short recognition sequence. Some leave **sticky ends** (single-stranded overhangs); others leave **blunt ends**.

A typical MCS looks like a list of palindromic recognition sequences in close succession:

```
   ...EcoRI...BamHI...HindIII...XhoI...NotI...PstI...XbaI...
   
   GAATTC  GGATCC   AAGCTT   CTCGAG  GCGGCCGC  CTGCAG  TCTAGA
```

You pick an enzyme whose site is in the MCS but *not* inside your cargo, cut both vector and cargo with that enzyme, then join them with **DNA ligase** (an enzyme that re-seals sugar-phosphate bonds).

### 8.2 Modern assembly interfaces

Restriction + ligation has limits (the site has to be unique, the cut leaves a "scar" sequence in the join). Modern interfaces use:

- **Type IIS sites** for **Golden Gate** assembly. A Type IIS enzyme cuts *outside* its recognition sequence — so the cut leaves user-designed sticky ends and removes the enzyme site from the product. This makes assembly **scarless** (no leftover sequence) and **modular** (many fragments at once).
- **Homology arms** for **Gibson** / **NEBuilder HiFi** assembly. The vector and cargo are designed so their ends share 15–40 base pairs of identical sequence; an enzyme mix chews back one strand at each end, the complementary single strands anneal, and a polymerase + ligase seals everything.
- **Recombination sites** for **Gateway** cloning. The vector carries *att* sites that a viral integrase swaps with *att* sites on the cargo. Scars are left but assembly is fast.

Each method has its own anatomy, explained in §13–17.

### 8.3 Negative selection cassettes (optional but useful)

Many modern vectors place a **negative selection** gene between the assembly sites. The most famous is **ccdB**, a bacterial toxin that poisons DNA gyrase and kills *E. coli* — except in special "*ccdB*-tolerant" strains used for amplifying empty vector. When a user replaces the ccdB cassette with their cargo, the *resulting* clones survive on a normal *E. coli* strain because the toxin is gone; un-recombined parental vectors kill themselves.

```
              EMPTY VECTOR                AFTER USER CLONES IN GOI
              ────────────                ─────────────────────────
                                                
                ╱──ccdB──╲                       ╱──GOI──╲
               ╱          ╲                     ╱          ╲
              [   vector   ]      ───►         [   vector   ]
               ╲          ╱                     ╲          ╱
                ╲────────╱                       ╲────────╱
              (kills DH5α,                     (DH5α survives;
               grows on DB3.1)                  unrearranged vector
                                                still has ccdB → dies)
```

## 9. Layer 3 — Expression control

This layer is the answer to: *how does the host cell know to read the cargo, and how loudly?*

### 9.1 The promoter

> **Promoter** — a DNA sequence upstream of a gene that recruits RNA polymerase to initiate transcription. Different organisms have different promoter rules; a bacterial promoter does nothing in a mammalian cell, and vice versa.

In *E. coli*, the canonical promoter has two short conserved blocks at positions −10 and −35 from the transcription start, recognised by the σ⁷⁰ subunit of RNA polymerase:

```
   ── TTGACA ──── 16-19 bp ──── TATAAT ── 5-7 bp ── [+1 transcription start]
       (−35)                     (−10)
```

The strongest commonly-used bacterial promoter is the **T7 promoter** (from bacteriophage T7), which is recognised by a phage-encoded RNA polymerase. T7 RNA polymerase is not made by *E. coli* itself; the host strain (typically BL21(DE3)) carries a copy of the T7 polymerase gene under the control of the *lacUV5* promoter, which is induced by adding **IPTG** (isopropyl β-D-1-thiogalactopyranoside) to the medium. The T7 RNA polymerase then transcribes the cargo from the T7 promoter on the plasmid at a very high rate.

In eukaryotes (plant and mammalian), three different RNA polymerases each have their own kinds of promoters:

- **Pol II**: protein-coding mRNAs; needs a Pol-II promoter (e.g., CMV, EF1α, CAG in mammalian; 35S in plants).
- **Pol III**: short non-coding RNAs (tRNAs, U6 snRNA, gRNAs for CRISPR); the U6 promoter is the workhorse for CRISPR guide RNA expression.
- **Pol I**: ribosomal RNA; rarely used in vector design.

The strength and inducibility of the chosen promoter directly set the expression level — and therefore many downstream design choices (low copy if expression is toxic; tight inducible if the cargo would burden growth; etc.).

### 9.2 The ribosome-binding signal — bacteria vs eukaryotes

Once an mRNA exists, the ribosome has to find the start codon. Bacteria and eukaryotes use different signals.

**Bacterial Shine–Dalgarno (SD) sequence.** A short purine-rich block (consensus AGGAGG) is placed 5–13 nucleotides upstream of the AUG. The ribosome's 16S rRNA has the complementary sequence; the two anneal, positioning the ribosome on the AUG.

```
   mRNA:    5' ... AGGAGG ... [5-13 nt spacer] ... AUG ... ORF ...   3'
                       └──complementary to 16S rRNA──┘
```

**Eukaryotic Kozak context.** Eukaryotic ribosomes do not have a Shine–Dalgarno mechanism; they scan from the cap until they find an AUG in a suitable sequence context. The canonical Kozak consensus is:

```
                  −6  −5  −4  −3  −2  −1  +1  +2  +3  +4
   mRNA:    5' ...  g   c   c   R   c   c   A   U   G   G  ...   3'
                                  ▲                       ▲
                              purine                  G  (key)
                              at −3 is               at +4 is
                              the strongest          the second
                              determinant            strongest
```

(R = purine, A or G.) Software should score by a position weight matrix (Noderer 2014) rather than by a binary consensus match.

**Practical rule.** A bacterial RBS works in bacteria and *only* in bacteria. A Kozak context works in eukaryotes and *only* in eukaryotes. A bacterial expression vector for *E. coli* must have a properly placed SD/RBS; a mammalian or plant expression vector must place the cargo's AUG in a good Kozak context.

### 9.3 5′ UTR, introns, and the cap (eukaryotic)

The eukaryotic primary RNA gets a chemical **cap** (a modified guanosine) added to its 5′ end almost as soon as transcription begins. The **5′ untranslated region (UTR)** is the part of the mRNA between the cap and the start codon. It can affect translation efficiency dramatically:

- **Length**: typically 50–300 nt; very short or very long UTRs reduce translation.
- **Upstream AUGs** ("uAUGs"): any AUG in the 5′ UTR with a good Kozak context will be used by the ribosome instead of the intended start.
- **Hidden splice signals**: eukaryotic cells contain a spliceosome that recognises particular sequences (5′ donor, 3′ acceptor); a cryptic match inside the cargo will cause some of the mRNA to be cut up before it can be translated.
- **Introns**: a deliberately included synthetic intron just upstream of the ORF can actually *boost* expression (an effect called "intron-mediated enhancement") and helps the mRNA export properly.

### 9.4 Operators and inducible control

> **Operator** — a short DNA sequence next to a promoter; a regulator protein (repressor or activator) binds it and tunes the rate of transcription.

In *E. coli* the **lac operator** is the canonical example. The bacterial **LacI repressor** binds the operator and prevents RNA polymerase from transcribing; adding **IPTG** (a chemical that mimics the natural inducer allolactose) releases LacI and transcription resumes.

```
      ─── lacI gene ───   ────── promoter ── lacO ── ORF ──────
                           (transcription blocked when LacI bound)
      
      + IPTG  →  LacI changes shape, falls off  →  transcription ON
```

Other inducible systems used in expression vectors:

| System | Inducer | Where used |
|---|---|---|
| *araBAD* / pBAD | L-arabinose | tight, tunable expression in *E. coli* |
| *rhaBAD* | L-rhamnose | very tight in *E. coli* |
| *tetA* / aTc / TetR | anhydrotetracycline | bacteria and mammalian (Tet-On/Off) |
| GAL1 | galactose | yeast |
| heat-shock / cI857 | 42 °C | bacteria |
| Tet-On 3G | doxycycline | mammalian, tight |
| TRE3G | doxycycline + rtTA | mammalian, programmable |

The decision of *whether* to use induction is driven by toxicity: if your cargo would damage the host's growth, you want expression silent until the cells have reached high density, then induced just before harvest.

## 10. Layer 4 — The cargo

The cargo is the answer to: *what is the actual gene or RNA we want the cell to make?*

### 10.1 Defining the gene of interest (GOI)

> **Gene of interest (GOI)** — the DNA sequence the experimenter wants the host to host. For protein-encoding work, this is an **open reading frame (ORF)**: a stretch of DNA that begins with an ATG (start) codon, contains a frame of codons with no premature stop, and ends with a stop codon (TAA, TAG, or TGA).

The first design question for the cargo is *whether the natural DNA sequence is the right DNA sequence*. If the GOI was found in a mammal but you want to express it in *E. coli*, the codon frequencies are different, the GC-content profile is different, and you may need a re-coded version (**codon-optimised**) that maintains the same amino-acid sequence while shifting codons to match the host.

```
   Original (e.g., human):   ATG  GTG  TTG  CAC  CTG  ACT  CCG  GAA  CGC  TAA
   Same amino acids,
   re-coded for E. coli:     ATG  GTC  CTC  CAT  CTG  ACG  CCT  GAA  AGA  TAA
                             Met  Val  Leu  His  Leu  Thr  Pro  Glu  Arg  STOP
```

**Caveat.** Codon optimisation is *not* biologically neutral. The same amino-acid sequence encoded by different codons can fold into different protein structures, can be translated at different speeds, and can change mRNA stability. Algorithms (CAI, %MinMax, CHARMING) try to balance these factors. Software should never simply maximise CAI; it should preserve known regulatory and structural RNA features.

### 10.2 Affinity tags, solubility tags, detection tags

Pure protein from a cell extract is rarely the goal in one step. Vectors typically fuse the GOI to a **tag** — a small extra protein domain that makes purification, detection, or solubilisation easier.

| Tag class | Examples | Function |
|---|---|---|
| Affinity (purification) | **His6/His10** (binds Ni²⁺ resin), FLAG (anti-FLAG), Strep-II / Twin-Strep (Strep-Tactin), HA, Myc, V5 | Bind a specific resin or antibody → fast purification or detection. |
| Solubility / folding | MBP, SUMO, NusA, Trx, TF | Keep insoluble proteins in solution while they fold. |
| Covalent self-labelling | SNAP, CLIP, HaloTag | Bind small-molecule probes covalently → imaging, pulldown. |
| Covalent conjugation | SpyTag/SpyCatcher, sortase motif | Couple to other tagged components after purification. |
| Detection only | small fluorescent proteins (eGFP, mScarlet, mNeonGreen) | Light-up readout of expression and localisation. |

**Where to place a tag.** Tags can go at the N-terminus (start of the protein), the C-terminus (end of the protein), or internally. They are *not* always neutral: a tag at one terminus may inhibit folding or activity even if the same tag at the other terminus works fine. A common rule is: try both, plus a tag-free design, when activity is required.

**Removing a tag.** Cleavable linkers carry a protease-recognition motif between the tag and the GOI:

```
                                                            ┌── protease cuts here
                                                            ▼
   ── His6 ── linker ── ENLYFQ G ── GOI ──                 (TEV protease)
   ── His6 ── linker ── LEVLFQ GP ── GOI ──                (3C/PreScission)
   ── His6 ── linker ── LVPR GS ── GOI ──                  (Thrombin)
```

Each protease leaves its own "scar" residues at the cut site (e.g., TEV leaves a G or S; PreScission leaves a G followed by P). Software must account for these scars when computing the final amino-acid sequence.

### 10.3 Signal peptides and localisation signals

The protein your gene produces will start somewhere in the cytoplasm. If you want it elsewhere — secreted out of the cell, anchored to a membrane, targeted to the nucleus or mitochondria — the cell needs an address label.

| Address label | Function |
|---|---|
| **IgG signal peptide** (mammalian) | N-terminal short hydrophobic stretch → directs the ribosome to the ER → protein is secreted (after the signal peptide is cleaved off). |
| **pelB / OmpA / DsbA** (E. coli) | Direct the protein to the periplasm (between inner and outer membrane). |
| **α-factor leader** (yeast) | Yeast secretion via the secretory pathway. |
| **NLS** (SV40 PKKKRKV) | Nuclear localisation. |
| **NES** (HIV-Rev LPPLERLTL) | Nuclear export. |
| **Mitochondrial presequence** | Targets the protein to the mitochondrial matrix. |
| **KDEL/HDEL** | C-terminal ER-retention signal. |

Wrong location = no useful product. A secreted growth factor that ends up in the cytoplasm is doing nothing for you; a transcription factor that ends up secreted is doing nothing either.

### 10.4 Stop codons and reading frame

A single missing or extra base in the cargo design moves the reading frame by one and turns the entire downstream sequence into nonsense (most likely with a premature stop within ~20 codons). This **frameshift** is the single most common cause of "I expected protein X but I got no protein at all".

Software must:

1. Translate the entire cargo *in silico* in the intended frame from the chosen start codon.
2. Verify there are no premature stops.
3. Verify that every fused tag, linker, signal peptide, and protease site is in the correct frame.
4. Make sure the construct ends with an in-frame stop codon — preferably two in tandem (TAA TAA) for robustness, because a single stop codon can occasionally be read through.

## 11. Layer 5 — Termination

Once the ribosome has hit the stop codon and the protein has been released, the mRNA itself still needs to end somewhere. Layer 5 controls that.

### 11.1 Bacterial transcription terminators

Bacterial **intrinsic terminators** are short DNA elements (typically 30–60 bp) that form an RNA hairpin followed by a run of uracils; the polymerase falls off the template at the U-run. Common examples include the *rrnB* T1T2 tandem terminator and the T7 terminator. Strength of a terminator is its termination efficiency (T_E), usually quoted as the fraction of polymerases that stop there: T1T2 ≈ 0.99, T7 terminator ≈ 0.93.

Why this matters: if the terminator is weak, the polymerase reads through into the downstream backbone, generating long, unstable, and sometimes anti-sense transcripts. This is a common cause of mysterious low expression.

### 11.2 Eukaryotic polyadenylation signals

Eukaryotic mRNAs do not have hairpin terminators; they are cleaved at a defined site and a long string of adenines is added (the polyA tail). The instruction to do this is the polyadenylation signal — the consensus AAUAAA followed about 15–30 nt later by a GU-rich element.

```
                          ↓ cleavage and polyA added here
   ... ORF ... STOP ... AAUAAA ──── GU-rich ────  -AAAAA...AAA  3' polyA tail
```

Common mammalian polyA signals (with relative strengths, bGH = 1.0):

| Signal | Strength | Notes |
|---|---|---|
| bGH (bovine growth hormone) | 1.0 (reference) | Default in pcDNA3-family vectors. |
| Rabbit β-globin | 0.8–1.0 | Strong, common. |
| Synthetic poly(A) (SPA) | 0.8–1.0 | ~50 nt; very compact, useful when vector size is constrained (e.g., AAV cargo). |
| SV40 late | 0.7–1.0 | Strong; common in viral-vector contexts. |
| SV40 early | 0.4–0.5 | Weaker, more compact. |
| hGH | 0.4–0.7 | Used in some lentiviral and Sleeping Beauty designs. |

### 11.3 Post-transcriptional regulatory elements (eukaryotic)

A separate type of element — the **WPRE** (Woodchuck hepatitis virus Posttranscriptional Regulatory Element) — sits between the ORF and the polyA and boosts expression 2–5×. The wild-type WPRE contains a truncated viral X-protein ORF with potential oncogenic activity, so therapeutic constructs should use the **WPRE3** or **mut6** variant which removes the X-ORF translation potential while preserving the enhancer activity.

## 12. Layer 6 — Quality and metadata

The sixth layer is invisible to the cell — but it is what lets *humans and software* trust the construct.

The minimum metadata for any vector under version control:

| Field | Why it matters |
|---|---|
| Construct UUID + version | Disambiguate one vector from a nearly-identical sibling. |
| Sequence checksum (SHA256 of canonical-orientation circular sequence) | Detects silent edits between supposedly-identical files. |
| Full feature table with controlled-vocabulary keys (GenBank / Sequence Ontology) | Software can reason about which part is which. |
| Source provenance (accession, retrieval date, URL) for every imported sequence | Reproducibility; forensic accountability. |
| Sequencing-primer plan | How we will verify the actual molecule matches the design. |
| Biosafety classification | What rules apply to handling this construct. |
| Licence / MTA (e.g., OpenMTA) | Who is allowed to use/distribute the part. |
| Design history (parent UUIDs, branch lineage) | Why this version exists and what it replaces. |
| SBOL serialisation | Machine-readable interchange so other software can consume the design. |

A construct without metadata is, in a real sense, not a construct — it is an anecdote.

---

# PART III — THE CHEMISTRY: HOW WE BUILD A VECTOR

We now know what a vector *contains*. The next question is: *how does the new DNA actually get in?*

Six families of cloning chemistry are in routine use. They are not interchangeable; each has a domain in which it is the right answer.

## 13. Method 1 — Restriction enzyme + DNA ligase (the classical method)

### 13.1 The chemistry

Restriction enzymes are bacterial proteins that cut double-stranded DNA at very specific 4–8-base recognition sites. **EcoRI**, for example, recognises `GAATTC` and cuts between the G and A on each strand, leaving a four-base 5′ overhang:

```
                          ┌── cut here on top
                          ▼
              5' ─ G   A A T T C ─ 3'           5' ─ G          AATTC ─ 3'
              3' ─ C T T A A   G ─ 5'    ──►    3' ─ CTTAA          G ─ 5'
                              ▲                       
                              └── cut here on bottom

                                                       (sticky 5' overhang
                                                        on each fragment)
```

The fragments now have *sticky ends* — single-stranded 5′ overhangs of the sequence `AATT` — and any two pieces cut with EcoRI can be joined because their sticky ends are complementary.

> **DNA ligase** — an enzyme that seals the sugar-phosphate backbone at a nick between two pieces of DNA. T4 DNA ligase is the lab standard.

### 13.2 The workflow

```
            VECTOR                              CARGO (PCR product)
            ─────────                           ──────────────────────
           (circle)                                  ── insert ──
              │                                        │
              ▼                                        ▼
       Cut with EcoRI                            Cut with EcoRI
              │                                        │
              ▼                                        ▼
          Linear backbone                       Linear insert
       (sticky ends)                           (matching sticky ends)
              │                                        │
              └────────────────────┬───────────────────┘
                                   │
                                   ▼
                          Mix + T4 DNA ligase
                          (overnight at 16 °C
                          or 1 h at 22 °C)
                                   │
                                   ▼
                          Transform into E. coli
                                   │
                                   ▼
                          Pick colonies on antibiotic
                                   │
                                   ▼
                          Miniprep + sequence-verify
```

### 13.3 Strengths and limitations

**Strengths.** Simple, well-understood, robust, no special enzymes beyond the restriction enzyme and ligase.

**Limitations.**

- The chosen restriction site must be unique in the vector and absent from the insert. If `GAATTC` appears in the middle of your cargo, you cannot cut with EcoRI without breaking your cargo.
- The cut site is *retained* in the final construct — it is a small "scar" between vector and insert.
- Joining only two fragments at a time is straightforward; joining four or more in one tube is messy.

## 14. Method 2 — Gibson assembly / NEBuilder HiFi

### 14.1 The chemistry

In Gibson assembly, the vector and the insert are designed so their *ends share 15–40 base pairs of identical sequence* (the **homology arms**). A three-enzyme cocktail does the rest:

1. **T5 exonuclease** chews back the 5′ ends of every fragment, exposing single-stranded 3′ overhangs.
2. The complementary single-stranded regions of any two fragments find each other and anneal.
3. **A high-fidelity polymerase** fills in the remaining gap.
4. **A thermostable ligase** seals the nicks.

```
           ┌─ fragment A ─┐    ┌─ fragment B ─┐
           ──────────────●●●●●●               ──────────────
                          shared
                          homology

      step 1: T5 exo chews back 5' ends, exposing 3' overhangs
      
           ────────                                 ──────────────
                   ●●●●●●─►                  ◄─●●●●●●
                                       
      step 2: complementary single strands anneal
      
           ────────────────●●●●●●●●●●──────────────
                            (annealed)

      step 3: polymerase fills the gap
      step 4: ligase seals the nicks
                                       
                   ┌──── joined product ────┐
           ──────────────●●●●●●●●●●──────────────
                                       
```

NEBuilder HiFi is a refined commercial variant of Gibson that uses an improved polymerase and tolerates shorter overlaps (15–20 nt for 2–3 fragments; 20–30 nt for 4–6 fragments).

### 14.2 The workflow

```
                Design overhangs (15-40 bp homology)
                            │
                            ▼
            Amplify each fragment by PCR with primers
            that carry the homology arms as 5' extensions
                            │
                            ▼
              Mix all fragments + Gibson mix (50 °C, 1 h)
                            │
                            ▼
              Transform E. coli, pick colonies, verify
```

### 14.3 Strengths and limitations

**Strengths.** Scarless. Multiple fragments can be assembled at once (2–6 routinely with original Gibson; up to ~15 with HiFi). No restriction sites required.

**Limitations.** Repetitive sequences within or near the overlaps can misassemble. PCR errors in the homology region can prevent correct annealing. Not the best choice for combinatorial libraries (where Golden Gate excels).

## 15. Method 3 — Golden Gate / Type IIS modular assembly

### 15.1 The chemistry

A Type IIS restriction enzyme like **BsaI** recognises `GGTCTC` but *cuts at a fixed distance away* from its recognition sequence — one nucleotide away on the top strand, five on the bottom — leaving a four-nucleotide overhang whose sequence is **whatever the user designed** in those four nucleotides:

```
              5' ─ G G T C T C N N N N N ─ 3'      5' ─ GGTCTCN
              3' ─ C C A G A G N N N N N ─ 5'      3' ─ CCAGAGNNNNN
                  └─ recognition ─┘
                      site
                                                   →  the recognition site
                                                      goes AWAY into the
                                                      flanking piece, and
                                                      the overhang is the
                                                      user-chosen 4 nt
```

Crucially, the recognition site (`GGTCTC`) is **not present in the final ligated product** — it ended up in the trimmed-off pieces. This is what makes Golden Gate scarless and one-pot: you can mix many fragments, each flanked by outward-facing BsaI sites, with BsaI + T4 ligase in a single tube; the enzyme cuts each fragment, exposing its user-chosen overhangs, the matching overhangs ligate, and once a junction is ligated the BsaI site is gone, so the enzyme cannot cut it again.

### 15.2 The cycle

```
                      ╭──────────────╮
                      │  Mix all     │
                      │ fragments +  │
                      │ vector + BsaI│
                      │ + T4 ligase  │
                      ╰──────┬───────┘
                             │
                             ▼
                  Thermocycle: 37 °C ↔ 16 °C
                  for ~ 30 cycles, then 50 °C (heat-kill)
                             │
                             ▼
                  ─ BsaI cuts each fragment, exposing
                    user-chosen 4-nt overhangs
                  ─ Matching overhangs from neighbouring
                    fragments anneal
                  ─ T4 ligase seals the junction
                  ─ Once junctions are sealed, the BsaI
                    site is gone — they cannot re-cut
                  ─ Product accumulates as cycles proceed
                             │
                             ▼
                  Transform, pick, verify
```

### 15.3 Designing the overhangs — and why fidelity data matters

The four-nucleotide overhang space has 256 possibilities. Not all of them ligate equally well; some pair with their reverse complement and others; some palindromic sequences self-ligate. To assemble *N* fragments in one pot, you need *N+1* (linear) or *N* (circular) overhangs that do not cross-ligate.

The Potapov 2018 / Pryor 2020 datasets (peer-reviewed measurements of how often every 4-nt overhang ligates with every other overhang) underpin the modern overhang-set picker. With optimised sets, single-pot Golden Gate assemblies of **up to 35 fragments** are now routine.

### 15.4 MoClo: standardised hierarchical Golden Gate

Once parts (promoters, RBSs, ORFs, terminators, ...) are domesticated into a Golden Gate format with a fixed set of overhangs, they become **interoperable LEGO blocks**. The MoClo standard (Weber 2011) uses three nested levels:

```
   Level 0     Level 1                        Level 2
   (parts)     (transcription units)          (multi-gene constructs)
   ────────    ──────────────────────────     ───────────────────────────
   promoter ┐
   5' UTR    │   ┌─ promoter+RBS+ORF1+term ─┐
   RBS       ├─► │                          │
   ORF       │   │   transcription unit 1   │
   terminator┘   └──────────────────────────┘
                                                   ┌── TU1 ──┐
                                                   │         │
                  ┌─ promoter+RBS+ORF2+term ─┐ ──► │  Multi  │
                  │                          │     │  gene   │
                  │   transcription unit 2   │ ──► │ vector  │
                  └──────────────────────────┘     │         │
                                                   └── TU2 ──┘
                  
   Enzyme:        Level 0 → 1 uses BsaI         Level 1 → 2 uses BsmBI
```

By alternating Type IIS enzymes between levels, you can do as many rounds as you want and the products of one round are immediately ready as parts for the next round. This is the foundation of modern combinatorial synthetic biology.

## 16. Methods 4, 5, 6 — Gateway, LIC, USER (briefer treatments)

- **Gateway.** Two specific recombination reactions (BP and LR), each catalysed by a viral integrase, swap a cargo between an entry vector and a destination vector via *att* recombination sites. Strength: extremely fast for transferring one ORF into many destination vectors (parallel tagging, parallel host-switching). Limitation: the *att* sites leave a scar (~8 aa N-terminal, ~25 aa C-terminal) that may affect the protein's structure or activity.

- **LIC (Ligation-Independent Cloning).** PCR products with engineered 3′ overhangs are joined to a complementary linearised vector without ligase; T4 DNA polymerase's 3′→5′ exonuclease activity chews back the ends to expose complementary single-stranded overhangs that anneal.

- **USER (Uracil-Specific Excision Reagent).** PCR primers contain deoxyuracil (dU) at chosen positions; a uracil-removing enzyme generates single-stranded overhangs. Scarless, supports multi-fragment assembly, but requires dU-containing oligos and a specific polymerase.

## 17. Choosing the right method — a decision tree

```
                    ┌─ Need scarless? ─────────────────────────┐
                    │                                          │
                    NO                                         YES
                    │                                          │
                    ▼                                          ▼
            ┌─ Unique sites?         ┌─ Many fragments? ──────────────────┐
            │  for one of the                              │              │
            │  six common REs                              NO             YES
            │  in MCS and not                              │              │
            │  in cargo?                                   ▼              ▼
            │                                  ┌─ Need library? ──┐  Golden Gate
            YES                                │                  │  (preferred for
            │                                  YES                NO   high fragment
            ▼                                  │                  │    count)
       Restriction/                            ▼                  ▼
       ligation                          Golden Gate /        Gibson / 
       (simple, fast)                    MoClo                NEBuilder HiFi
                                         (combinatorial,      (single design,
                                         standardised parts)  not library)

            NO (no unique sites)
            │
            ▼
       Gibson, Gateway,
       LIC, USER, or IVA
```

The cleanest mapping in practice:

| Task | First-choice method |
|---|---|
| Drop one new ORF into a one-of-a-kind expression vector | Gibson or NEBuilder HiFi |
| Build a panel of 50 promoter–RBS–ORF combinations | Golden Gate / MoClo |
| Move the same ORF into 20 different destination vectors (tagging panel) | Gateway |
| One PCR product into one vector, fast and ligase-free | LIC |
| Multi-fragment scarless build with no Type IIS domestication | USER or Gibson |
| Single classical job with a friendly MCS | Restriction + ligase |

---

# PART IV — THE THREE HOSTS

Now we have a vocabulary (Part II) and a chemistry (Part III). The remaining puzzle is: a vector that works in *E. coli* will not work in a maize cell, and a vector that works in a maize cell will not work in HEK293. Why, and what changes per host?

## 18. Designing for bacteria

### 18.1 The biology recap

*E. coli*'s simplicity is its strength. A single cytoplasmic compartment. No nucleus. RNA polymerase loads onto a promoter and ribosomes start translating mRNA as it is being made — there is no nuclear export step, no splicing, no cap, no polyA. The signal that recruits the ribosome is the **Shine–Dalgarno** sequence; the signal that ends transcription is an **intrinsic terminator hairpin**.

### 18.2 The minimum required parts for a bacterial expression vector

```
   ┌──────────────────────────────────────────────────────────────┐
   │  bacterial origin  (pMB1 / pSC101 / p15A / etc.)             │
   │  selectable marker (kan / amp / cam)                         │
   │  promoter ± operator (T7lac / trc / araBAD / rhaBAD)         │
   │  Shine-Dalgarno sequence (AGGAGG-like)                       │
   │  5-13 nt spacer                                              │
   │  start codon (ATG)                                           │
   │  optional N-terminal tag + linker + protease site            │
   │  ORF / GOI                                                   │
   │  optional C-terminal tag                                     │
   │  stop codon (tandem TAA TAA preferred)                       │
   │  bacterial transcription terminator (rrnB T1T2)              │
   └──────────────────────────────────────────────────────────────┘
```

### 18.3 Three decisions that dominate

1. **Promoter and induction.** If the cargo is non-toxic, a strong constitutive promoter and a high-copy ori give the most protein. If the cargo is toxic or aggregation-prone, use a tight inducible promoter (T7lac with pLysS, or pBAD/araBAD) and consider a low-copy ori (pSC101 or p15A).
2. **Codon usage.** *E. coli* prefers different codons than a mammalian source organism. Re-code if expressing a mammalian/plant ORF; preserve known functional RNA features (frameshift sites, regulatory motifs).
3. **Folding / disulfide / membrane environment.** For disulfide-rich proteins use a SHuffle or Origami strain (oxidative cytoplasm). For membrane proteins use C41/C43 strains. For rare-codon-heavy ORFs use a Rosetta strain.

### 18.4 The end-to-end bacterial workflow

```
            ┌──── Design construct ────┐
            │ promoter + RBS + ATG +   │
            │ tag + ORF + stop + term  │
            │ in chosen E. coli host   │
            └────────────┬─────────────┘
                         │
                         ▼
              Order DNA or assemble parts
              (synthesis fragments → Gibson
               or Golden Gate → ligated)
                         │
                         ▼
              Transform DH5α (cloning host),
              pick colonies, miniprep, sequence
                         │
                         ▼
              Transform BL21(DE3) (expression
              host); single colony in pre-culture
                         │
                         ▼
              Grow to OD₆₀₀ ≈ 0.6 → induce
              (IPTG / arabinose / heat) → grow
              for 3-18 h
                         │
                         ▼
              Harvest pellet → lyse → run SDS-PAGE
              → protein band at expected size?
                         │
                         ▼
              IMAC / affinity purify by tag
                         │
                         ▼
              Cleave tag (if needed), buffer-exchange,
              concentration, activity assay
```

## 19. Designing for plant cells

### 19.1 The biology recap

Plant cells are eukaryotic — they have a nucleus, transcribe protein-coding genes via Pol II, splice, cap, and polyadenylate their mRNAs. *But* they have two things bacteria and mammalian cells do not:

1. A rigid cell wall, so DNA delivery has to either pierce or be smuggled through it.
2. **Plastids** (chloroplasts) — semi-autonomous prokaryote-like organelles whose own genome can be engineered separately.

For nuclear transgenes (the most common case), DNA is delivered via the soil bacterium **Agrobacterium tumefaciens**. Agrobacterium naturally infects plant wounds and transfers a defined piece of its own DNA (the **T-DNA**, flanked by 25-bp imperfect direct repeats called the **left border (LB)** and **right border (RB)**) into the plant cell, where it integrates into the chromosome.

### 19.2 The binary vector system

Engineers exploited this by splitting Agrobacterium's natural Ti (tumour-inducing) plasmid into two:

- A **disarmed Ti helper** (in the Agrobacterium strain) carrying the *vir* genes that drive transfer, but with the original T-DNA's tumour genes removed.
- A small **binary vector** the user designs, containing two replication origins (one for *E. coli* cloning, one for Agrobacterium maintenance) and the T-DNA borders flanking the cargo cassette.

```
                BINARY VECTOR (schematic)

       ┌──── E. coli ori ────┐
       │                     │
       │     ┌── kan_R ──┐   │
       │     │ (marker)  │   │
       │     └───────────┘   │
       │                     │
       │     ┌── Agro ori ──┐│
       │     │ (e.g., pVS1) │ (or RK2)
       │     └──────────────┘│
       │                     │
       │    ┌─── LB ─────┐   │   ◄── 25-bp left border
       │    │            │   │
       │    │ plant      │   │
       │    │ selectable │   │  (often: 35S::nptII::nos
       │    │ marker     │   │   or 35S::bar::nos for plant
       │    │            │   │   antibiotic / herbicide selection)
       │    │            │   │
       │    │ promoter   │   │  ◄── 35S, ubiquitin, or 
       │    │            │   │      tissue-specific
       │    │   GOI      │   │
       │    │ terminator │   │  ◄── nos terminator
       │    │            │   │
       │    └─── RB ─────┘   │  ◄── 25-bp right border
       │                     │
       └─────────────────────┘
       
       Only the DNA between LB and RB gets transferred to the plant.
       Everything outside stays in the Agrobacterium and is discarded.
```

### 19.3 The plant-vector parts that differ from bacterial/mammalian

| Part | Plant choice |
|---|---|
| Promoter (constitutive) | **CaMV 35S** (cauliflower mosaic virus, very strong, broadly active); maize/rice ubiquitin promoter (very strong in monocots). |
| Promoter (tissue-specific) | seed-specific (napin, β-conglycinin), root-specific (RolD), pollen-specific (LAT52). |
| Terminator | **nos** (nopaline synthase) terminator (the classic), or ocs terminator. |
| Plant selectable marker | **nptII** (kanamycin), **hpt** (hygromycin), **bar** (glufosinate/Basta). |
| 5′ enhancer | the omega leader from TMV, or the AMV enhancer, boost translation. |
| Splicing | introns work — and can boost expression, especially in monocots ("intron-mediated enhancement"). |

### 19.4 The end-to-end plant workflow

```
            ┌──── Design binary vector ────┐
            │ 35S::GOI::nos                │
            │ + 35S::nptII::nos (selection)│
            │ between LB and RB borders    │
            └────────────┬─────────────────┘
                         │
                         ▼
              Assemble in E. coli, sequence-verify
                         │
                         ▼
              Transform Agrobacterium tumefaciens
              (GV3101, EHA105, LBA4404) by
              freeze-thaw or electroporation
                         │
                         ▼
              ┌── Transient route ─────────────┐
              │  Agroinfiltration into          │
              │  Nicotiana benthamiana leaves   │
              │  + p19 silencing suppressor     │
              │  → measure at 3-7 days          │
              └─────────────────────────────────┘
                         │
                         ▼ (or)
              ┌── Stable route ────────────────┐
              │  Floral dip (Arabidopsis) /     │
              │  callus transformation (rice,   │
              │  maize, tobacco) → regeneration │
              │  on selection medium → seeds    │
              └─────────────────────────────────┘
                         │
                         ▼
              Screen by PCR / Southern / western
              → segregate to homozygous line
```

### 19.5 Two practical reminders for plant work

- *Agrobacterium* transformation transfers everything between LB and RB into the plant chromosome at random sites; expression depends on the integration locus ("position effect"). Stable transgenic studies need to screen many independent insertion events to find the right expression level.
- Silencing is common — plants have powerful RNA-interference defences against repeated or virus-like sequences. Including a co-expressed RNAi suppressor like **p19** (from tomato bushy stunt virus) is standard in transient leaf experiments.

## 20. Designing for mammalian cells

### 20.1 The biology recap

Mammalian cells perform the full eukaryotic central-dogma machinery: Pol II makes a primary transcript that is capped, spliced, and polyadenylated before export. The first AUG in a good Kozak context is used as the start of translation. Post-translational modifications — N-linked glycosylation, disulfide formation in the ER, phosphorylation, ubiquitylation — are extensive and species-appropriate.

There are two design routes:

- **Transient transfection.** A plasmid is introduced into the cells using a chemical (lipofectamine, PEI) or physical method (electroporation). The plasmid stays episomal (not integrated), expression peaks at ~ 48 h and declines as the plasmid is diluted by cell division. Best for fast small-scale protein production, screening, and short-term assays.
- **Stable transduction or integration.** The cargo is introduced into the chromosome (by viral integration — lentivirus, AAV with integration aid, or transposon-based PiggyBac/Sleeping Beauty), then selected with a drug until a clonal line carries the integrated copy. Best for long-term consistent expression, manufacturing, and *in-vivo* therapies.

### 20.2 The minimum required parts for a mammalian expression vector

```
   ┌──────────────────────────────────────────────────────────────┐
   │  bacterial side                                              │
   │    bacterial origin (pMB1)                                   │
   │    bacterial marker (kan or amp)                             │
   │                                                              │
   │  mammalian side                                              │
   │    mammalian promoter (CMV / EF1α / CAG / PGK / UBC / TRE3G) │
   │    optional intron + 5' UTR                                  │
   │    Kozak context around the ATG                              │
   │    optional signal peptide                                   │
   │    GOI / ORF                                                 │
   │    optional tag / linker / localisation signal               │
   │    stop codon                                                │
   │    optional WPRE3 (post-transcriptional booster)             │
   │    polyA signal (bGH / SV40-late / SPA / rabbit β-globin)    │
   │                                                              │
   │  optional mammalian selectable cassette                      │
   │    second promoter + neo / puro / hygro / blast / zeo        │
   └──────────────────────────────────────────────────────────────┘
```

### 20.3 Three decisions that dominate

1. **Promoter — match to cell type and duration.**
   - HEK293 transient expression: CMV is fastest and strongest.
   - iPSC, ES cells, primary cells, long-term: **EF1α** (most stable against silencing); CAG for strong *in-vivo*; CMV is silenced in most stem-cell and differentiated contexts.
   - Tissue-specific *in-vivo*: synapsin (neurons), CaMKIIα (excitatory neurons), MBP (oligodendrocytes), albumin (liver), cTnT (cardiomyocytes).
2. **PolyA — match to vector size and downstream context.**
   - Default: bGH (225 nt, strongest in many transient assays).
   - When space is tight (AAV cargo limit 4.7 kb): SPA (~50 nt).
   - For viral-vector contexts: SV40 late or rabbit β-globin.
3. **Delivery vehicle — transient plasmid vs lentivirus vs AAV.**
   - Transient plasmid: cheap, fast, large cargo.
   - Lentivirus: stable integration, broad cell types, ~ 9 kb payload limit.
   - AAV: in-vivo gene therapy, broad serotype-defined tropism, hard 4.7 kb cargo limit between ITRs.

### 20.4 The end-to-end mammalian workflow (transient)

```
            ┌──── Design plasmid ────┐
            │ CMV::Kozak::GOI::bGH    │
            │ + bacterial side       │
            └──────────┬─────────────┘
                       │
                       ▼
            Assemble in E. coli, sequence-verify
            (use Stbl3 if LTR-containing)
                       │
                       ▼
            Maxiprep DNA (need µg-level for transfection)
                       │
                       ▼
            Plate HEK293 (or chosen cell line)
            → ~70 % confluent at transfection
                       │
                       ▼
            Transfect with PEI / lipofectamine /
            electroporation (DNA + carrier)
                       │
                       ▼
            Incubate 24-72 h → harvest cells or
            collect medium (if secreted protein)
                       │
                       ▼
            Confirm expression by western,
            flow cytometry, fluorescence, activity assay
                       │
                       ▼
            Purify (affinity chromatography by tag)
```

### 20.5 Stable cell-line workflow (lentivirus path)

```
        Design 3rd-gen SIN lentiviral transfer plasmid
        (RSV-promoter-replaced 5' LTR, Ψ, RRE, cPPT, 
         internal promoter::GOI, WPRE3, SIN 3' LTR)
                       │
                       ▼
        Co-transfect HEK293T with transfer + packaging
        (psPAX2 = gag/pol/rev) + envelope (pMD2.G = VSV-G)
                       │
                       ▼
        Collect virus-containing supernatant at 48-72 h
        → titre (e.g., qPCR or FACS of transduction
        marker)
                       │
                       ▼
        Transduce target cells with desired MOI
        (multiplicity of infection)
                       │
                       ▼
        Select with antibiotic (puro / blast / hygro)
        → expand surviving cells
                       │
                       ▼
        Optional: single-cell clone → screen by
        copy-number and expression level
```

### 20.6 Practical reminders for mammalian work

- **Splice-site scan**: a cryptic splice donor or acceptor inside your ORF will silently destroy a fraction of your transcripts. Run SpliceAI or a similar predictor.
- **Premature-polyA scan**: an AAUAAA hexamer inside your ORF can cause premature transcript termination.
- **uORF scan**: an ATG in the 5′ UTR with a good Kozak context will steal ribosomes from the intended start. Either remove it or place it deliberately for regulation.
- **CpG content**: very CpG-rich constructs are prone to DNA methylation and silencing over time. Some modern designs deliberately reduce CpG count.
- **Promoter silencing**: CMV silencing is the single most common cause of "we made the stable line, expression was great at week one, gone at week six". Use EF1α, CAG, or A2UCOE-buffered designs for long-term stability.

---

# PART V — THE WORKFLOW: FROM IDEA TO VERIFIED CONSTRUCT

## 21. The decision flow

A construct begins with a *biological objective* and ends with a *verified molecule*. The full path:

```
   ┌────────────────────────────────────┐
   │ 1. STATE THE OBJECTIVE             │
   │    What do you want a cell to do?  │
   │    Which cell? How much? When?     │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 2. SELECT THE TARGET HOST          │
   │    Bacteria / plant / mammalian /  │
   │    yeast / insect / cell-free      │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 3. CHOOSE THE PROPAGATION BACKBONE │
   │    Ori, marker, copy number,       │
   │    biosafety constraints           │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 4. DESIGN EXPRESSION CONTROL       │
   │    Promoter, RBS or Kozak,         │
   │    induction, insulation           │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 5. DESIGN THE CARGO                │
   │    ORF, codon strategy, tags,      │
   │    linkers, signal peptides,       │
   │    cleavage sites, stops           │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 6. CHOOSE THE ASSEMBLY METHOD      │
   │    Restriction / Gibson / Golden   │
   │    Gate / Gateway / LIC / USER     │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 7. RUN IN-SILICO VALIDATION        │
   │    Translate, scan, check, score   │
   │    (see §22)                       │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 8. SAFETY & SCREENING              │
   │    Biosafety classification +      │
   │    sequence screening (see §23)    │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 9. ORDER / ASSEMBLE / TRANSFORM    │
   │    Synthesis or PCR + ligation     │
   │    + bacterial transformation      │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 10. SEQUENCE-VERIFY                │
   │    Sanger (small inserts) or       │
   │    Nanopore/PacBio (whole plasmid) │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 11. FUNCTIONAL TEST                │
   │    Transform expression host,      │
   │    induce, measure expression,     │
   │    measure function                │
   └─────────────┬──────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │ 12. ARCHIVE                        │
   │    Sequence + checksum + SBOL +    │
   │    metadata in repository          │
   └────────────────────────────────────┘
```

## 22. In-silico validation rules (what the software checks before any DNA is ordered)

Before any DNA is ordered or any cloning reaction is set up, the proposed sequence is run through a validation pipeline. Each rule is a (predicate, severity, citation) tuple. Hard violations block; soft warnings prompt the designer.

```
   ┌──────────────────────────────────────────────────────────────┐
   │   Proposed sequence                                          │
   └────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  HARD CHECKS (block on failure)                              │
   │  ─────────────                                               │
   │  • valid alphabet (ACGT)                                     │
   │  • ORF starts with ATG, ends with stop                       │
   │  • no internal stops in ORF                                  │
   │  • all tags/linkers/protease sites in frame                  │
   │  • promoter ↔ host compatibility                             │
   │  • internal Type IIS sites absent (if Golden Gate)           │
   │  • restriction-enzyme conflicts absent                       │
   │  • direct repeats < 100 bp                                   │
   │  • total construct within host capacity                      │
   │  • viral replication elements absent (unless approved)       │
   │  • screening hook returns "clear"                            │
   └────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  SOFT CHECKS (warn on failure, do not block)                 │
   │  ─────────────                                               │
   │  • RBS folding ΔG (-30..+30) > -10 kcal/mol                  │
   │  • Kozak PWM score acceptable                                │
   │  • uORF scan negative                                        │
   │  • splice-site scan (SpliceAI) negative                      │
   │  • premature polyA scan negative                             │
   │  • direct repeats < 20 bp                                    │
   │  • homopolymer runs ≤ 9 nt                                   │
   │  • GC content 25-65 % global, 15-80 % per 50-bp window       │
   │  • CAI 0.7 - 0.95, %MinMax close to native                   │
   │  • signal-peptide prediction matches compartment             │
   │  • antibiotic marker not restricted for downstream use       │
   │  • no mobilisation elements (if not intended)                │
   └────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────────────────┐
   │   Report: pass / pass-with-warnings / fail                   │
   │   Each item attached to its citation in the KB.              │
   └──────────────────────────────────────────────────────────────┘
```

## 23. Biosafety and biosecurity

> **Biosafety** — protecting people, animals, and the environment from harmful organisms in the laboratory.
>
> **Biosecurity** — protecting harmful organisms and dangerous DNA sequences from misuse.

Every modern vector-design pipeline must call out to a screening service before a DNA order is placed:

```
                ┌── proposed sequence ──┐
                                ▼
                ╭───────────────────────╮
                │ screening adaptor     │
                │ (IGSC v3.0 / IBBIS    │
                │ Common Mechanism /    │
                │ SecureDNA / internal) │
                ╰────────┬──────────────╯
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        "clear"      "watchlist"   "hit"
            │            │            │
            │            ▼            ▼
            │     manual review  block + alert
            │     by institutional biosafety officer
            ▼
        proceed to synthesis
```

Frameworks in force as of 2026:

- NIH Guidelines for Research Involving Recombinant or Synthetic Nucleic Acid Molecules (April 2024).
- OSTP Framework for Nucleic Acid Synthesis Screening (September 2024).
- IGSC Harmonized Screening Protocol v3.0 (September 2024).
- IBBIS Common Mechanism (launched February 2024).
- SecureDNA (parallel community screening).
- WHO Laboratory Biosafety Manual, 4th edition (2020).

The software does not decide biosafety on its own; it routes the question to a configured adaptor and records the verdict in the construct's metadata.

## 24. Wet-lab realisation (a quick map of what happens in the lab)

This paper is about *design*, not *protocols*. But to make design decisions sensibly, you have to know roughly what happens after the design leaves software:

```
            DESIGN                              REALISATION
            ──────                              ────────────
            Plasmid map +                       Order synthesis fragments
            assembly plan                       (Twist, IDT, GenScript)
                                                          │
                                                          ▼
                                                Receive linear DNA
                                                          │
                                                          ▼
                                                PCR-amplify backbone
                                                (or order it)
                                                          │
                                                          ▼
                                                Mix fragments + enzymes
                                                (Gibson / Golden Gate / etc.)
                                                          │
                                                          ▼
                                                Transform competent E. coli
                                                (heat-shock or electroporation)
                                                          │
                                                          ▼
                                                Plate on antibiotic LB agar
                                                          │
                                                          ▼
                                                Pick colonies (overnight)
                                                          │
                                                          ▼
                                                Miniprep DNA
                                                          │
                                                          ▼
                                                Diagnostic restriction digest
                                                + agarose gel
                                                          │
                                                          ▼
                                                Sanger or Nanopore sequencing
                                                          │
                                                          ▼
                                                Glycerol-stock the verified
                                                clone for archival
                                                          │
                                                          ▼
                                                Use the verified plasmid in
                                                downstream host (bacteria
                                                expression / Agrobacterium /
                                                mammalian transfection)
```

Key wet-lab terms a designer should at least recognise:

> **Transformation** — moving DNA into a bacterium (heat-shock or electroporation).
> **Transfection** — moving DNA into a mammalian cell (lipofection, PEI, electroporation).
> **Transduction** — moving DNA into a cell using a viral vector.
> **Competent cells** — bacteria treated chemically (CaCl₂) or grown to a state that lets DNA enter.
> **Miniprep** — a small-scale purification of plasmid DNA from a single overnight bacterial culture.
> **Maxiprep / Midiprep** — larger-scale plasmid purifications (mg level).
> **Glycerol stock** — frozen suspension of bacteria in 15–25 % glycerol at −80 °C; survives indefinitely.
> **Restriction digest** — cutting DNA with one or more restriction enzymes; the resulting fragment pattern on a gel confirms (or rejects) the predicted map.
> **Agarose gel** — a horizontal electrophoresis gel that separates DNA fragments by size.
> **Sanger sequencing** — chain-termination DNA sequencing; reads ~ 800 bp from a single primer with high accuracy.
> **Nanopore / PacBio** — long-read sequencing technologies that can read full plasmid sequences in one run.

## 25. Failure modes and what they mean

When something goes wrong, the design itself usually contains the clue. The mapping from symptom to design defect:

| Symptom | Most likely design defects |
|---|---|
| No colonies after transformation | toxic cargo with leaky promoter; wrong antibiotic; ori incompatible with host; plasmid too large; bad linearisation. |
| Many colonies, all empty vector | non-directional cloning; incomplete backbone cut; no negative selection. |
| Insert present but truncated or rearranged | repetitive sequences; high copy combined with toxicity; recombination-prone host (use a *recA-* strain). |
| Construct correct but no protein in E. coli | wrong promoter for host; weak RBS; bad mRNA folding near start; rare codons; missing T7 RNAP in host. |
| Construct correct but no protein in mammalian | wrong promoter for cell type; bad Kozak; uORF stealing ribosomes; cryptic splice site; premature polyA. |
| Protein expressed but insoluble | promoter too strong; folding-disruptive tag placement; missing chaperone host; should try MBP/SUMO/NusA. |
| Mammalian stable line silenced over weeks | CMV in stem-cell / primary context; integration site effect; no insulator. |
| AAV titre very low | cargo > 4.7 kb between ITRs; problematic sequences disturbing ITR replication. |
| Wrong fusion protein | reading frame error at att / MCS / linker; unexpected scar residues; check translation in silico. |
| Background expression in OFF state | weak terminator; promoter leak; backbone read-through. |

When the construct works on paper but the cell disagrees, return to the in-silico validation: the symptom maps to a rule, and the rule maps to a fix.

---

# PART VI — THREE WORKED EXAMPLES

To make the abstract concrete, three end-to-end designs are sketched: one bacterial, one plant, one mammalian.

## 26. Example A — Bacterial expression of an enzyme

**Objective.** Produce ~ 10 mg of a 35 kDa cytosolic enzyme (call it EnzymeA, originally from a thermophilic bacterium) for activity assays.

**Decisions.**

| Decision | Choice | Reason |
|---|---|---|
| Host (propagation) | DH5α | Standard cloning strain. |
| Host (expression) | BL21(DE3) | T7 system; standard high-yield strain. |
| Ori | pMB1 (high copy) | Friendly cargo; want lots of DNA. |
| Marker | kan | Robust; no satellite colonies. |
| Promoter | T7lac | Strong + lac-repressible; tight when uninduced. |
| RBS | Salis-designed for medium TIR | Avoid ribosome jam. |
| Cargo | EnzymeA ORF | Codon-optimised for E. coli (CAI ≈ 0.85). |
| Tag | N-terminal His6 + TEV site | Affinity purification + tag removal possible. |
| Stop | tandem TAA TAA | Robust. |
| Terminator | rrnB T1T2 | High efficiency. |
| Assembly | Gibson 3-fragment (backbone + His6-TEV + ORF) | Scarless and fast. |

**Construct sketch:**

```
   ┌── pMB1 ori ── kan_R ── T7 promoter ── lacO ── RBS ── ATG ─┐
                                                                │
                                                              His6
                                                                │
                                                            linker
                                                                │
                                                          TEV site
                                                                │
                                                          EnzymeA ORF
                                                                │
                                                            TAA TAA
                                                                │
                                                          rrnB T1T2
                                                                │
                                                       (back to ori)
```

**Workflow:**
1. Design + in-silico validate.
2. Order three synthesis fragments + primers.
3. Gibson-assemble in DH5α; pick + miniprep + Sanger-verify.
4. Transform BL21(DE3); single colony in 5 mL LB + kan overnight.
5. Inoculate 1 L LB + kan; grow to OD₆₀₀ = 0.6; induce with 0.5 mM IPTG at 18 °C for 16 h.
6. Pellet, lyse, Ni-IMAC purify, cleave TEV, second Ni column to remove cleaved His6-tag + TEV protease, size-exclusion chromatography.
7. Activity assay.

**Expected yield:** 5–50 mg per litre culture for a friendly soluble enzyme; less if the protein aggregates.

## 27. Example B — Transient mammalian expression of a fluorescent protein

**Objective.** Express mCherry (a red fluorescent protein) transiently in HEK293T for 48 h to test a new cell-imaging protocol.

**Decisions.**

| Decision | Choice | Reason |
|---|---|---|
| Host (propagation) | DH5α | Cloning. |
| Host (expression) | HEK293T (transient) | Standard for transient imaging. |
| Bacterial ori / marker | pMB1 / amp | Default. |
| Mammalian promoter | CMV | Strong in HEK293T; transient is fine. |
| Kozak | gccRccATGG enforced around the start codon | Standard. |
| Cargo | mCherry ORF | Default. |
| Tag | none | Fluorescence is the readout. |
| PolyA | bGH | Strong; default. |
| Mammalian marker | none (transient) | Not needed. |
| Assembly | Golden Gate (MoClo level-1) | Re-use parts library. |

**Construct sketch:**

```
   ┌── pMB1 ori ── amp_R ─── CMV ─── Kozak ATG ── mCherry ORF ── STOP ── bGH polyA ─┐
                                                                                     │
                                                                              (back to ori)
```

**Workflow:**
1. Design + in-silico validate.
2. Golden Gate assemble from existing MoClo level-0 parts.
3. Pick + miniprep + sequence-verify.
4. Maxiprep DNA (~ 1 mg) for transfection.
5. Plate HEK293T at 70 % confluence in 6-well dish; transfect with PEI (1:3 DNA:PEI mass ratio).
6. Image at 24 / 48 / 72 h on a fluorescence microscope.

**Expected outcome:** Bright red cells at 24–48 h with 30–70 % transfection efficiency by visual count.

## 28. Example C — Plant transient expression of a reporter

**Objective.** Test whether a candidate plant promoter drives detectable GUS (β-glucuronidase) expression in *N. benthamiana* leaves.

**Decisions.**

| Decision | Choice | Reason |
|---|---|---|
| Host (propagation) | DH5α | Bacterial cloning side. |
| Host (delivery) | *Agrobacterium tumefaciens* GV3101 | Standard transient strain. |
| Host (target) | *N. benthamiana* leaf, 4–6 weeks old | Standard transient host. |
| Binary vector backbone | pCAMBIA1300 derivative | E. coli ori (pBR322), Agro ori (pVS1), kan in E. coli, hygro in plant. |
| Plant promoter | candidate test promoter ("pTest") | Whole point of the experiment. |
| Cargo | uidA (GUS) ORF | Standard reporter. |
| Terminator | nos | Standard. |
| Co-infiltration | p19 silencing suppressor (in a second Agro strain) | Standard. |
| Assembly | Gibson (3 fragments: backbone, pTest, uidA-nos) | Scarless. |

**Construct sketch (the T-DNA region):**

```
   ── LB ── 35S::hpt::nos (plant selectable marker) ── pTest::uidA::nos ── RB ──
```

(Plus the backbone bacterial-side modules outside the borders, not transferred to the plant.)

**Workflow:**
1. Design + in-silico validate.
2. Assemble in *E. coli* DH5α; sequence-verify.
3. Transform Agrobacterium GV3101 by freeze-thaw.
4. Pre-culture Agrobacterium overnight, dilute to OD₆₀₀ = 0.5 in infiltration buffer (10 mM MgCl₂, 10 mM MES pH 5.6, 200 µM acetosyringone).
5. Co-infiltrate test strain + p19 strain into *N. benthamiana* leaves with a needleless syringe.
6. At 3 days post-infiltration: harvest leaf discs, stain with X-Gluc (substrate for GUS) overnight at 37 °C, clear chlorophyll with ethanol, photograph blue staining intensity.

**Expected outcome:** Blue staining proportional to promoter strength; un-infiltrated regions remain white.

---

# APPENDIX A — Glossary (terms used in this paper, in alphabetical order)

- **Affinity tag.** A short protein domain fused to the GOI to allow purification on a specific resin (e.g., His6 → Ni²⁺; FLAG → anti-FLAG antibody).
- **Agrobacterium tumefaciens.** A soil bacterium that naturally transfers a defined DNA segment (T-DNA) into plant cells; the workhorse of plant transformation.
- **Antibiotic.** A small-molecule drug that kills bacteria; used in vector design as the basis for selectable markers.
- **Assembly method.** The chemistry used to join the cargo to the vector (§13–17).
- **att sites.** Short DNA sequences recognised by phage integrases; used in Gateway cloning.
- **BAC (Bacterial Artificial Chromosome).** A very-low-copy *E. coli* plasmid (F-factor based) capable of carrying inserts up to 300 kb.
- **BL21(DE3).** *E. coli* strain commonly used for T7-driven protein expression; carries a chromosomal copy of T7 RNA polymerase under IPTG control.
- **Binary vector.** Plant-transformation vector that separates the T-DNA region (replicates and is transferred) from the *vir* helper machinery (stays in Agrobacterium).
- **Biosafety.** Protecting people, animals, and the environment from harmful organisms.
- **Biosecurity.** Preventing misuse of dangerous DNA sequences.
- **Blue/white screening.** Use of *lacZα* complementation: vectors that have an insert disrupting *lacZα* form white colonies on X-gal; intact vectors form blue colonies. (Historical, used in pUC-family cloning.)
- **CAG promoter.** Chimeric promoter combining CMV early enhancer, chicken β-actin promoter, and rabbit β-globin splice acceptor. Strong and broadly active in mammalian cells.
- **CAI (Codon Adaptation Index).** A scalar measure of how well a coding sequence matches the codon-usage profile of a host organism; range 0–1.
- **Cap (5′ cap).** A modified guanosine added to the 5′ end of eukaryotic mRNAs; needed for nuclear export and ribosome loading.
- **Cargo.** The piece of DNA the experimenter wants the cell to host; usually a GOI plus its tags and signals.
- **CCD-B (ccdB).** A bacterial toxin used as a negative-selection marker on parental vectors; *ccdB*-tolerant strains (DB3.1, Survival 2) are needed to grow ccdB-containing plasmids.
- **CHO cells.** Chinese Hamster Ovary cells; the dominant mammalian chassis for therapeutic-protein manufacturing.
- **CMV promoter.** Strong constitutive mammalian promoter from human cytomegalovirus immediate-early gene; silenced in many stem-cell and primary contexts.
- **Codon.** A group of three RNA nucleotides that specifies one amino acid (or a stop) during translation.
- **Codon optimisation.** Re-coding a gene so it uses codons preferred by the chosen host, while preserving the amino-acid sequence.
- **Copy number.** Number of plasmid molecules per host cell; determined by the origin of replication.
- **CRISPR / Cas9.** RNA-guided DNA-cleaving system; used in vector design for genome editing.
- **Destination vector (in Gateway).** The vector into which the cargo is transferred from an entry vector via LR recombination.
- **DNA ligase.** Enzyme that seals the sugar-phosphate backbone at a nick between two DNA pieces.
- **EF1α promoter.** Mammalian constitutive promoter from elongation factor 1α; resists silencing better than CMV.
- **Endotoxin.** Lipopolysaccharide from Gram-negative bacterial cell walls; contaminates *E. coli* plasmid preps and must be removed for *in-vivo* use.
- **Entry vector (in Gateway).** The vector that holds the cargo flanked by attL sites, used as the donor in LR reactions.
- **Episomal.** Maintained as a free (non-integrated) circle inside the host cell; loses copies if not under selection.
- **Eukaryote.** A cell with a true nucleus enclosing chromosomes; plants, animals, fungi, protists.
- **Expression vector.** A vector carrying the elements needed to drive transcription and translation of the cargo in a target host.
- **FLAG tag.** Short peptide DYKDDDDK; affinity-purifiable with anti-FLAG antibody.
- **Frameshift.** A change in the reading frame caused by insertion or deletion of bases not divisible by three; usually destroys the downstream protein.
- **GAL1 promoter.** Yeast inducible promoter, induced by galactose, repressed by glucose.
- **Gateway cloning.** Site-specific recombination-based cloning using *att* sites and viral integrase enzymes.
- **Gibson assembly.** Isothermal scarless cloning using a three-enzyme cocktail (T5 exonuclease, polymerase, ligase) on fragments with shared end homology.
- **Glycerol stock.** Frozen bacterial culture in 15–25 % glycerol at −80 °C; long-term archival.
- **Golden Gate.** One-pot scarless cloning using a Type IIS restriction enzyme + T4 ligase + user-designed 4-nt overhangs.
- **GOI (Gene Of Interest).** The specific gene the experimenter wants the host to host.
- **GS / GS-null.** Glutamine synthetase based selection system used in CHO cells; GS-null CHO cells require functional GS on the vector to survive in glutamine-free medium.
- **HEK293, HEK293T.** Human Embryonic Kidney 293 cells; HEK293T expresses SV40 large T-antigen and supports SV40-ori amplification.
- **His6 / His10.** Short polyhistidine tag; binds Ni²⁺/Co²⁺ resin (IMAC) for affinity purification.
- **HRP.** Horseradish peroxidase; an enzyme used as a reporter or detection tag (often coupled to a secondary antibody).
- **Hygromycin (hyg).** Selection antibiotic; *hph* gene confers resistance in both bacteria and many eukaryotes.
- **IMAC.** Immobilised Metal-ion Affinity Chromatography; standard method for purifying His-tagged proteins.
- **Inducible promoter.** A promoter whose activity is controlled by adding/removing a small molecule (e.g., IPTG, arabinose, doxycycline) or a stimulus (heat).
- **Insulator.** A DNA element that buffers a transgene against position effects in the chromosome (e.g., chicken HS4).
- **Integration.** Incorporation of a transgene into the host chromosome; permanent.
- **IPTG.** Isopropyl β-D-1-thiogalactopyranoside; a chemical that binds LacI repressor and de-represses lac-controlled promoters in *E. coli*.
- **IRES (Internal Ribosome Entry Site).** A structured RNA element that recruits ribosomes to start translation cap-independently; used for polycistronic constructs.
- **Kanamycin.** Antibiotic; *aph* / *nptII* gene confers resistance.
- **Kozak context.** The sequence context around an AUG that determines whether a eukaryotic ribosome initiates translation there.
- **lacI.** Gene encoding the LacI repressor that binds the lac operator and silences lac-controlled promoters until IPTG is added.
- **Lentivirus.** A retrovirus subfamily (HIV-derived in lab vectors) used to deliver and stably integrate transgenes; 3rd-generation self-inactivating (SIN) lentivirus is the standard safe form.
- **Linker.** A short flexible (or rigid) peptide between two domains in a fusion protein, designed to allow them to function independently.
- **MBP (Maltose-Binding Protein).** A 396-aa solubility tag; cleave to remove after purification.
- **MCS (Multiple Cloning Site).** A short region in a vector containing multiple unique restriction-enzyme recognition sites.
- **mCherry.** A bright red monomeric fluorescent protein; common reporter.
- **Miniprep / Maxiprep.** Small-/large-scale plasmid purification from bacterial culture.
- **MoClo.** Hierarchical Golden Gate cloning standard with defined Level 0 / 1 / 2 part classes and BsaI / BpiI / BsmBI enzyme alternation.
- **NEBuilder HiFi.** Commercial refined Gibson assembly mix.
- **Negative selection.** A gene (e.g., ccdB, sacB) that kills the host when expressed; used to eliminate parental (un-recombined) vectors.
- **Nicotiana benthamiana.** A tobacco relative; the standard model species for transient plant agroinfiltration experiments.
- **nptII.** Gene for kanamycin resistance; used as plant selectable marker (kanamycin / G418 / paromomycin).
- **Nucleus.** Membrane-bound organelle in eukaryotes that contains the chromosomes; site of transcription and pre-mRNA processing.
- **ORF (Open Reading Frame).** A DNA segment that reads from a start codon to an in-frame stop codon without internal stops.
- **Ori (origin of replication).** DNA sequence at which replication initiates and which sets the copy number.
- **p19.** A silencing-suppressor protein from tomato bushy stunt virus; co-infiltrated with binary vectors to boost transient plant expression.
- **PCR (Polymerase Chain Reaction).** In-vitro DNA amplification using a thermostable polymerase and primer pairs; the bedrock molecular tool.
- **Plasmid.** A small circular DNA molecule that replicates independently of the chromosome; the natural ancestor of cloning vectors.
- **Pol II / Pol III.** Eukaryotic RNA polymerases — Pol II transcribes mRNAs, Pol III transcribes small RNAs (tRNAs, U6 snRNA, gRNAs).
- **POI (Protein Of Interest).** The protein the experimenter wants to produce.
- **PolyA signal.** Eukaryotic 3′ sequence (AAUAAA + GU-rich downstream) that directs cleavage and polyadenylation of the mRNA.
- **Promoter.** DNA sequence at which RNA polymerase is recruited to initiate transcription.
- **Prokaryote.** Cell type without a nucleus; bacteria and archaea.
- **Protease site.** A short amino-acid motif recognised and cleaved by a specific protease (e.g., TEV, 3C, thrombin).
- **PTM (Post-Translational Modification).** Chemical modification of a protein after translation: glycosylation, phosphorylation, disulfide formation, ubiquitylation, etc.
- **RBS (Ribosome Binding Site).** Generic name for the sequence on an mRNA that recruits the ribosome; in bacteria, primarily the Shine–Dalgarno sequence.
- **Recombinant DNA.** DNA molecule produced by joining sequences from different sources in vitro.
- **Restriction enzyme.** Bacterial endonuclease that cuts DNA at a specific recognition site; the original cloning tool.
- **Reverse genetics.** Approach where the experimenter changes the DNA and then observes the phenotype (as opposed to forward genetics, which starts from phenotype).
- **Ribosome.** Ribonucleoprotein machine that translates mRNA into protein.
- **SBOL.** Synthetic Biology Open Language; the standard data format for interchange of vector designs between software.
- **Selectable marker.** A gene that confers survival under a selection condition; lets the experimenter pick cells that carry the vector.
- **Shine–Dalgarno sequence.** Short purine-rich sequence (consensus AGGAGG) on bacterial mRNAs, 5–13 nt upstream of the start codon; complementary to the 16S rRNA's anti-Shine–Dalgarno.
- **Shuttle vector.** A vector that can replicate in two different hosts (e.g., *E. coli* + yeast); carries two oris and two markers.
- **Signal peptide.** N-terminal protein sequence (~ 15–30 aa) that directs the nascent polypeptide to a secretion pathway and is cleaved off during processing.
- **Stable line.** A cell line carrying a chromosomally integrated transgene that persists across generations.
- **Stop codon.** Codon (UAA, UAG, UGA) that signals the end of translation; release of the protein from the ribosome.
- **SUMO.** Small protein used as a fusion tag for solubility; cleaved by SUMO protease (Ulp1) to leave a native N-terminus.
- **T-DNA.** Transfer DNA; the segment between LB and RB borders of an Agrobacterium binary vector that integrates into plant chromosomes.
- **T4 DNA ligase.** Standard DNA ligase used in cloning.
- **TEV protease.** Tobacco Etch Virus protease; cleaves at ENLYFQ↓G/S; used to remove fusion tags.
- **Termination layer.** Layer 5 of the six-layer architecture — terminator or polyA signal.
- **Terminator.** Bacterial DNA element causing RNA polymerase to dissociate; typically an intrinsic hairpin + U-run.
- **Tet-On / Tet-Off.** Doxycycline-inducible mammalian expression systems.
- **Titration.** Series of dilutions; in vector design, often refers to determining viral-vector concentration.
- **Transcription.** Synthesis of RNA from a DNA template by RNA polymerase.
- **Transcription factor.** A protein that regulates transcription by binding regulatory DNA elements.
- **Transduction.** Viral-mediated DNA delivery into a cell.
- **Transfection.** Non-viral DNA delivery into a eukaryotic cell.
- **Transformation.** DNA delivery into a bacterial cell.
- **Translation.** Synthesis of protein from an mRNA template by ribosomes.
- **Type II vs Type IIS restriction enzymes.** Type II enzymes (e.g., EcoRI) cut within their palindromic recognition site; Type IIS enzymes (e.g., BsaI) cut at a defined offset *outside* their recognition site, leaving user-chosen overhangs.
- **Untranslated region (UTR).** Region of mRNA flanking the ORF; the 5′ UTR is between the cap and the start codon, the 3′ UTR is between the stop codon and the polyA tail.
- **Vector.** A piece of DNA engineered to carry another piece of DNA into a cell.
- **VLP (Virus-Like Particle).** A self-assembling protein shell made from a viral capsid protein, with no viral genome; used for vaccines and targeted delivery.
- **WPRE.** Woodchuck hepatitis virus Posttranscriptional Regulatory Element; a 3′ cis element that boosts mammalian transgene expression 2–5×. WPRE3 / mut6 variants remove the truncated WHV-X ORF for safety.
- **Yeast.** Single-celled fungus; *Saccharomyces cerevisiae* and *Komagataella phaffii* (Pichia) are the common chassis.

---

# APPENDIX B — Diagram index

| Diagram | Section |
|---|---|
| The bacterial cell | §2.1 |
| The plant cell | §2.2 |
| The mammalian cell | §2.3 |
| Cell-type comparison table | §2 (end) |
| The central dogma | §3 |
| The generic plasmid | §4 |
| The six-layer architecture | §6 |
| Negative-selection logic (ccdB) | §8.3 |
| Bacterial −35 / −10 promoter | §9.1 |
| Shine–Dalgarno positioning | §9.2 |
| Kozak context | §9.2 |
| Lac operator + IPTG induction | §9.4 |
| Tagging — N-term His6 + TEV linker | §10.2 |
| Restriction cut and re-ligation | §13.1 |
| Restriction cloning workflow | §13.2 |
| Gibson assembly chemistry | §14.1 |
| Gibson workflow | §14.2 |
| Golden Gate chemistry (BsaI) | §15.1 |
| Golden Gate cycle | §15.2 |
| MoClo hierarchical levels | §15.4 |
| Method-choice decision tree | §17 |
| Bacterial-vector module diagram | §18.2 |
| Bacterial end-to-end workflow | §18.4 |
| Plant binary-vector diagram | §19.2 |
| Plant end-to-end workflow | §19.4 |
| Mammalian-vector module diagram | §20.2 |
| Mammalian transient workflow | §20.4 |
| Lentivirus stable workflow | §20.5 |
| Full design decision flow | §21 |
| In-silico validation pipeline | §22 |
| Biosafety / screening hook | §23 |
| Design → realisation handoff | §24 |
| Bacterial example construct (EnzymeA) | §26 |
| Mammalian example construct (mCherry) | §27 |
| Plant example T-DNA (GUS reporter) | §28 |

---

# APPENDIX C — A note to the dev-orchestrator and architect

This white paper is the *human-understandable* layer of the vector-design knowledge. The companion document `Cloning_and_Expression_Vector_Design_Knowledge_Base_v2_0.md` is the *machine-actionable* layer: every concept here has a corresponding parameter table, validation rule, or schema field there.

When designing the universal cloning/expression-vector design software, treat the relationship as:

```
   ┌─────────────────────────────────────────────────────────────┐
   │  THIS WHITE PAPER                                          │
   │  - first-principles narrative                              │
   │  - pedagogical explanations                                │
   │  - diagrams of every concept                               │
   │  - glossary                                                │
   │  ────────────►  drives the UI, in-app help, tutorials,    │
   │                  onboarding, and the conceptual model the │
   │                  designer (the human user) carries.       │
   └─────────────────────────────────────────────────────────────┘
                                  │
                                  │ corresponds 1:1 to
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  KNOWLEDGE BASE v2.0                                       │
   │  - quantitative parts catalogues                           │
   │  - validation rules (V001–V025+)                           │
   │  - host / chassis catalogues                               │
   │  - assembly-method matrices with fidelity data             │
   │  - data schema (Part / Module / Construct / Host / ...)    │
   │  - SBOL / GenBank / FASTA interchange                      │
   │  - synthesis-constraint and screening hooks                │
   │  ────────────►  drives the data model, the rule engine,   │
   │                  the validation pipeline, the file I/O,   │
   │                  and the part library.                    │
   └─────────────────────────────────────────────────────────────┘
```

Read this paper to understand *why* every rule is what it is. Consult v2.0 to find *what* numbers to enforce. When the two seem to disagree, the citation chain in v2.0 is the source of truth; this paper will be updated to match.

---

*End of Cloning and Expression Vector Design — First-Principles White Paper.*
