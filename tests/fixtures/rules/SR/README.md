# SR rule fixtures

Generated from Synthesis-vendor rules for T-405.

- SR-01: Total synthesis length within vendor-specific bounds. Twist gene fragments: 300–5 000 bp. Twist clonal genes: 300–5 000 bp. IDT gBlocks: 125–3 000 bp. IDT gBlocks HiFi: ≤ 5 000 bp. GenScript standard gene: ≤ ~10 000 bp.
- SR-02: Global GC content within vendor bounds. Twist: 25–65 %. IDT: 25–75 %. GenScript: 30–70 %.
- SR-03: Per-50-bp-window GC within bounds. Twist Express: 35–65 %, GC delta ≤ 52 %.
- SR-04: Homopolymer runs: Twist: hard ban on ≥ 14 bp. IDT: ≤ 10 nt A/T, ≤ 6 nt G/C.
- SR-05: Direct repeats: ≥ 20 bp flagged; ≥ 40 bp rejected (most vendors).
- SR-06: Inverted repeats / hairpins: strong hairpins (ΔG ≤ -20 kcal/mol on ViennaRNA) rejected.
- SR-07: Vendor-mandated 5′ / 3′ adapter sequences for certain products (e.g., Twist eBlocks have universal flanking; IDT gBlocks have no fixed flanking; clonal genes have vendor-specific cloning-site flanks). The system MUST include or strip these flanks based on vendor profile and intended assembly chemistry.
- SR-08: Vendor-mandated restriction sites for cloning into the supplied vector (e.g., a vendor's "ready-to-clone" service requires EcoRV blunt ends or specific Type IIS sites for direct subcloning).
- SR-09: Vendor-forbidden patterns (vendor blacklists, IP-protected sequences, known toxic motifs).
- SR-10: Sequence complexity / linguistic complexity (vendor ML-based scoring; for software, a low-complexity windowed filter approximation).
- SR-11: Cost / price-tier thresholds (length, complexity, turnaround). The system MUST estimate the cost tier and warn before order.
- SR-12: Pre-cloned vs linear-fragment: the user MUST be informed whether the vendor delivers the fragment ligated into a plasmid, or as a linear PCR-amplifiable fragment.
- SR-13: Synthesis-vendor-side sequence screening (IGSC v3.0 compliant). The user is informed that the vendor will screen and may reject.
- SR-14: Codon-level rescue: if a sequence fails vendor constraints, the system MUST attempt synonymous-codon rewriting within the ORF to fix the violation without changing the protein, then re-check.
- SR-15: Vendor turnaround time displayed (Twist: ~ 2 weeks; IDT: 1–2 weeks; GenScript: 2–3 weeks).
- SR-16: Twist Express-tier vs standard-tier eligibility (Express requires stricter GC, fewer repeats, no exotic adapters).
- SR-17: If the construct exceeds any vendor's clonal-gene maximum, the system MUST automatically partition it into orderable fragments and design the assembly route (Gibson or Golden Gate).
