# MS rule fixtures

Generated from MS2/phage/VLP rules for T-405.

- MS-01: MS2 coat-protein reference sequence is locked; every variant is represented as explicit deltas with checksum.
- MS-02: Single-chain MS2 dimer insertions are restricted to the tolerated AB-loop half and preserve the V75E/A81G variant declaration.
- MS-03: MS2 pac/hairpin cargo tag is present, copy number is declared, and the consensus-critical residues are preserved.
- MS-04: PP7, Qbeta, and MS2 coat-protein families are not mixed with the wrong pac/hairpin tag unless an orthogonality override is documented.
- MS-05: Display/conjugation strategy is declared when Spy/Snoop/sortase/click ports are present.
- MS-06: Host-range, tropism, replication, cargo-delivery, or antimicrobial-payload functions require stricter biosafety review.
- MS-07: VLP validation package declares intended assembly verification readouts such as SEC, TEM, or native PAGE metadata.
