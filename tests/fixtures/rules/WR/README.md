# WR rule fixtures

Generated from Wet-lab workflow rules for T-405.

- WR-01: The chosen polymerase is high-fidelity (Phusion / Q5 / KAPA HiFi / PrimeSTAR) when the PCR product will be cloned; Taq is not used for cloning amplicons.
- WR-02: PCR template type is declared (plasmid / genomic / cDNA / synthetic).
- WR-03: If template is plasmid, DpnI digestion of the PCR product is included before transformation to remove template carry-over.
- WR-04: For restriction-ligation, vector and insert are gel-purified before ligation (or PCR-cleaned if both produce clean amplicons).
- WR-05: For single-cut linearised vectors, dephosphorylation (CIP / rSAP / Antarctic phosphatase) is included to suppress religation.
- WR-06: For double-digest, both enzymes are buffer-compatible (or sequential digestion is specified).
- WR-07: For methylation-sensitive enzymes, the host genotype is dam+ / dcm+ or dam− / dcm− as required by the enzyme.
- WR-08: For Gibson assembly, fragments are mixed at 1:1 molar ratio (or 1:3 vector:insert for 2-piece); total DNA 50–100 ng.
- WR-09: For Golden Gate, BsaI/BsmBI/SapI/BbsI is paired with T4 DNA ligase in the same reaction (one-pot).
- WR-10: For Golden Gate, the cycling programme alternates 37 °C and 16 °C and ends with a heat-inactivation step (60–80 °C).
- WR-11: For Gateway BP / LR, Proteinase K stop step is included before transformation.
- WR-12: Transformation step specifies competent-cell type (chemical vs electro) and matches it to expected transformation efficiency target (≥ 10⁸ cfu/µg for high-throughput Golden Gate libraries; ≥ 10⁶ acceptable for routine cloning).
- WR-13: Selection plate antibiotic concentration matches the host × marker matrix (FR-HOST-09).
- WR-14: Colony screening includes both colony PCR (rapid) and diagnostic restriction digest (more reliable).
- WR-15: Sequencing strategy covers every junction with ≥ 50 bp upstream and ≥ 50 bp downstream within Sanger read length.
- WR-16: Constructs > 8 kb or containing repeats > 100 bp are sequenced by long-read (Nanopore / PacBio whole plasmid).
- WR-17: Glycerol stocks are made at 15–25 % glycerol final and stored at −80 °C.
- WR-18: For lentiviral and AAV transfer plasmid amplification, use a recombination-deficient host (Stbl3, Stbl4, NEB Stable).
- WR-19: For BAC propagation, use DH10B / EPI300 (recA-) at 30 °C if instability is observed.
- WR-20: For very large constructs, use electroporation rather than chemical transformation.
- WR-21: For ccdB-bearing destination vectors, propagate in DB3.1 or ccdB Survival 2 only.
- WR-22: For toxic-protein expression, the inducer is added when OD₆₀₀ ≈ 0.5–0.8, then growth at 16–25 °C overnight for solubility.
- WR-23: For disulfide-containing proteins, use SHuffle / Origami or co-express DsbC.
- WR-24: For mammalian transient transfection, plate cells at 60–80 % confluence the day before; DNA:PEI mass ratio 1:3, 1 µg DNA per 1 × 10⁶ cells (default; per cell line).
- WR-25: For lentivirus packaging, use HEK293T at 70–90 % confluence; co-transfect transfer + psPAX2 + pMD2.G; collect supernatant 48–72 h post-transfection.
- WR-26: For agroinfiltration, OD₆₀₀ of Agrobacterium in infiltration buffer is typically 0.3–0.8; co-infiltrate p19 silencing suppressor at 1:1.
- WR-27: For Sanger sequencing, sequencing primers anneal 50–100 bp upstream of the region of interest.
- WR-28: DNA quality for sequencing must be > 50 ng/µL and A260/A280 in [1.8, 2.0].
- WR-29: For chemical transformation, heat shock at 42 °C for 30–45 s, then 2-min ice, then SOC recovery.
- WR-30: For electroporation, DNA in salt-free buffer; cuvette gap matches voltage setting (1 mm = 1.8 kV, 2 mm = 2.5 kV).
