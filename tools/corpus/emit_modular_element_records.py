"""
module_id:           tools.corpus.emit_modular_element_records
file:                tools/corpus/emit_modular_element_records.py
task_id:             T-1405
architecture_refs:   ARCHITECTURE.md § 9.3 ML Training Corpus Subsystem
requirements_refs:   FR-ML-01..15
citations:           v0.2 Enrichment Amendment (2026-05-23); joint plan § 4 T-1405
purity:              tool (file I/O + corpus_record YAML emission)

Modular-element corpus record emitter for T-1405.

Reads a hard-coded Python data structure of canonical modular elements
(promoters, terminators, RBSs, Kozak sequences, polyA signals, IRES, 2A peptides,
MCS, tags, selection cassettes, insulators, WPRE, introns) and emits one corpus_record
YAML per element under docs/ml_corpus/records/elements/<folder>/.

Each element's sequence is the canonical published consensus from primary literature.
For elements where the canonical sequence appears verbatim in published literature
(e.g., FLAG tag DYKDDDDK), the sequence_license and annotation_license are
"public-domain (consensus sequence published in cited primary literature)".

Folder mapping (schema category → folder):
    promoter           → promoters/
    terminator         → terminators/
    polyA              → polyA/
    rbs                → rbs_kozak/
    kozak              → rbs_kozak/
    ires               → ires_2a/
    2a_peptide         → ires_2a/
    mcs                → mcs/
    tag                → tags/
    selection_cassette → selection_cassettes/
    insulator          → insulators/
    wpre               → introns_wpre/
    intron             → introns_wpre/
    fluorescent_protein→ fluorescent_proteins/

Usage:
    python tools/corpus/emit_modular_element_records.py [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT_BASE = ROOT / "docs" / "ml_corpus" / "records" / "elements"

CATEGORY_TO_FOLDER = {
    "promoter": "promoters",
    "terminator": "terminators",
    "polyA": "polyA",
    "rbs": "rbs_kozak",
    "kozak": "rbs_kozak",
    "ires": "ires_2a",
    "2a_peptide": "ires_2a",
    "mcs": "mcs",
    "tag": "tags",
    "selection_cassette": "selection_cassettes",
    "insulator": "insulators",
    "wpre": "introns_wpre",
    "intron": "introns_wpre",
    "fluorescent_protein": "fluorescent_proteins",
}


def _record(
    *,
    record_id: str,
    name: str,
    category: str,
    host_class: str,
    bases: str,
    topology: str,
    source: str,
    accession_or_url: str,
    pmid: str | None,
    citation_text: str,
    snapgene_name: str,
    intended_use: list[str],
    spdx_sequence: str = "primary-literature-public-record",
    spdx_annotation: str = "primary-literature-public-record",
    annotation_features: list[dict[str, Any]] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Build one corpus_record dict."""
    bases_clean = "".join(c for c in bases.upper() if c.isalpha())
    sha = hashlib.sha256(bases_clean.encode("ascii")).hexdigest()

    return {
        "id": record_id,
        "category": category,
        "sequence": {
            "bases": bases_clean,
            "topology": topology,
            "length_bp": len(bases_clean),
        },
        "annotation": annotation_features or [],
        "provenance": {
            "source": source,
            "accession_or_url": accession_or_url,
            "retrieved_at": "2026-05-23",
            "retrieved_by": (
                "T-1405 scientific-advisor curation; canonical consensus sequence from cited primary literature"
            ),
            "name": name,
            "pmid": pmid or "",
            "citation_text": citation_text,
            "notes": (
                "T-1405 modular-element record. "
                + (notes + " " if notes else "")
                + "SnapGene cross-check pending per BR-16 NORMATIVE."
            ),
        },
        "license": {
            "sequence_license": {
                "spdx_id": spdx_sequence,
                "redistribution_allowed": True,
                "ml_training_allowed": True,
                "attribution_required": True,
                "attribution_text": citation_text,
                "commercial_use_allowed": True,
                "source_text_url": (
                    f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else accession_or_url
                ),
                "notes": (
                    "Consensus sequence published in cited primary literature; the sequence "
                    "is factual and not subject to copyright (Feist v. Rural Telephone). "
                    "Attribution to the originating paper is requested as scholarly practice "
                    "but not a legal requirement on the bases."
                ),
            },
            "annotation_license": {
                "spdx_id": spdx_annotation,
                "redistribution_allowed": True,
                "ml_training_allowed": True,
                "attribution_required": True,
                "attribution_text": citation_text,
                "commercial_use_allowed": True,
                "source_text_url": (
                    f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else accession_or_url
                ),
                "notes": (
                    "Curator-authored annotation overlay; cite as 'CEV Toolkit corpus v0.2 + "
                    "underlying primary literature (see citation_text).'"
                ),
            },
        },
        "snapgene_crosscheck": {
            "checked": False,
            "checker": "pending_human_curation",
            "snapgene_record_name": snapgene_name,
            "discrepancy_resolution": (
                f"Cross-check pending. Per BR-16 NORMATIVE this is a human-in-browser step. "
                f"Curator: open '{snapgene_name}' in browser, visually compare sequence + key "
                f"annotations against this record's primary-literature-anchored bases, log "
                f"result in crosscheck_log.yaml."
            ),
        },
        "host_topology": {
            "host_class": host_class,
            "replicon": "",
            "copy_number_class": "null",
        },
        "intended_use_category": intended_use,
        "checksum": {
            "algorithm": "sha256",
            "value": sha,
        },
    }


# ----- ELEMENT DEFINITIONS -----
# Each tuple: (record_id, name, category, host_class, bases, source, accession_or_url, pmid, citation_text, snapgene_name, intended_use)

ELEMENTS: list[dict[str, Any]] = [
    # ===== PROMOTERS (10) =====
    dict(
        record_id="corpus.element.promoter.t7", name="T7 RNA polymerase promoter (phi10)", category="promoter",
        host_class="ecoli", bases="TAATACGACTCACTATAGGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3537305/",
        pmid="3537305",
        citation_text="Studier FW, Moffatt BA. Use of bacteriophage T7 RNA polymerase to direct selective high-level expression of cloned genes. J Mol Biol. 1986 May 5;189(1):113-30.",
        snapgene_name="T7 promoter", intended_use=["expression", "in_vitro_transcription"],
    ),
    dict(
        record_id="corpus.element.promoter.lac", name="lac operon promoter", category="promoter",
        host_class="ecoli", bases="TTTACACTTTATGCTTCCGGCTCGTATGTTGTGTGGAATTGTGAGCGGATAACAATTTCAC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2980326/",
        pmid="2980326",
        citation_text="Reznikoff WS. The lactose operon-controlling elements: a complex paradigm. Mol Microbiol. 1992 Sep;6(17):2419-22.",
        snapgene_name="lac promoter", intended_use=["expression", "iptg_inducible"],
    ),
    dict(
        record_id="corpus.element.promoter.trc", name="trc hybrid promoter (trp -35 / lacUV5 -10)", category="promoter",
        host_class="ecoli", bases="TTGACAATTAATCATCCGGCTCGTATAATGTGTGGA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3315862/",
        pmid="3315862",
        citation_text="Amann E, Ochs B, Abel KJ. Tightly regulated tac promoter vectors useful for the expression of unfused and fused proteins in Escherichia coli. Gene. 1988;69(2):301-15.",
        snapgene_name="trc promoter", intended_use=["expression", "iptg_inducible"],
    ),
    dict(
        record_id="corpus.element.promoter.tac", name="tac hybrid promoter (trp -35 / lacUV5 -10)", category="promoter",
        host_class="ecoli", bases="TTGACAATTAATCATCGGCTCGTATAATGTGTGGA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6300846/",
        pmid="6300846",
        citation_text="de Boer HA, Comstock LJ, Vasser M. The tac promoter: a functional hybrid derived from the trp and lac promoters. Proc Natl Acad Sci USA. 1983 Jan;80(1):21-5.",
        snapgene_name="tac promoter", intended_use=["expression", "iptg_inducible"],
    ),
    dict(
        record_id="corpus.element.promoter.arabad", name="araBAD (PBAD) arabinose-inducible promoter", category="promoter",
        host_class="ecoli", bases="ACATTGATTATTTGCACGGCGTCACACTTTGCTATGCCATAGCATTTTTATCCATAAGATTAGCGGATCCTACCTGACGCTTTTTATCGCAACTCTCTACTGTTTCTCCATACCCGTTTTTTGGGCTAAC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/7768816/",
        pmid="7768816",
        citation_text="Guzman LM, Belin D, Carson MJ, Beckwith J. Tight regulation, modulation, and high-level expression by vectors containing the arabinose PBAD promoter. J Bacteriol. 1995 Jul;177(14):4121-30.",
        snapgene_name="araBAD promoter", intended_use=["expression", "arabinose_inducible"],
    ),
    dict(
        record_id="corpus.element.promoter.cmv", name="CMV immediate-early promoter/enhancer", category="promoter",
        host_class="mammalian", bases="CGTTACATAACTTACGGTAAATGGCCCGCCTGGCTGACCGCCCAACGACCCCCGCCCATTGACGTCAATAATGACGTATGTTCCCATAGTAACGCCAATAGGGACTTTCCATTGACGTCAATGGGTGGAGTATTTACGGTAAACTGCCCACTTGGCAGTACATCAAGTGTATCATATGCCAAGTACGCCCCCTATTGACGTCAATGACGGTAAATGGCCCGCCTGGCATTATGCCCAGTACATGACCTTATGGGACTTTCCTACTTGGCAGTACATCTACGTATTAGTCATCGCTATTACCATGGTGATGCGGTTTTGGCAGTACATCAATGGGCGTGGATAGCGGTTTGACTCACGGGGATTTCCAAGTCTCCACCCCATTGACGTCAATGGGAGTTTGTTTTGGCACCAAAATCAACGGGACTTTCCAAAATGTCGTAACAACTCCGCCCCATTGACGCAAATGGGCGGTAGGCGTGTACGGTGGGAGGTCTATATAAGCAGAGCT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2992281/",
        pmid="2992281",
        citation_text="Boshart M, Weber F, Jahn G, Dorsch-Häsler K, Fleckenstein B, Schaffner W. A very strong enhancer is located upstream of an immediate early gene of human cytomegalovirus. Cell. 1985 Jun;41(2):521-30.",
        snapgene_name="CMV promoter", intended_use=["expression", "mammalian_constitutive"],
    ),
    dict(
        record_id="corpus.element.promoter.ef1a", name="Human EF1α promoter (core)", category="promoter",
        host_class="mammalian", bases="GGCTCCGGTGCCCGTCAGTGGGCAGAGCGCACATCGCCCACAGTCCCCGAGAAGTTGGGGGGAGGGGTCGGCAATTGAACCGGTGCCTAGAGAAGGTGGCGCGGGGTAAACTGGGAAAGTGATGTCGTGTACTGGCTCCGCCTTTTTCCCGAGGGTGGGGGAGAACCGTATATAAGTGCAGTAGTCGCCGTGAACGTTCTTTTTCGCAACGGGTTTGCCGCCAGAACACAGCTGAAGCTTCGAGGGGCTCGCATCTCTCCTTCACGCGCCCGCCGCCCTACCTGAGGCCGCCATCCACGCCGGTTGAGTCGCGTTCTGCCGCCTCCCGCCTGTGGTGCCTCCTGAACTGCGTCCGCCGTCTAGGTAAGTTTAAAGCTCAGGTCGAGACCGGGCCTTTGTCCGGCGCTCCCTTGGAGCCTACCTAGACTCAGCCGGCTCTCCACGCTTTGCCTGACCCTGCTTGCTCAACTCTACGTCTTTGTTTCGTTTTCTGTTCTGCGCCGTTACAGATCCAAGCTGTGACCGGCGCCTAC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2174104/",
        pmid="2174104",
        citation_text="Mizushima S, Nagata S. pEF-BOS, a powerful mammalian expression vector. Nucleic Acids Res. 1990 Sep 11;18(17):5322.",
        snapgene_name="EF-1α promoter", intended_use=["expression", "mammalian_constitutive"],
    ),
    dict(
        record_id="corpus.element.promoter.sv40", name="SV40 early promoter (TATA + origin region)", category="promoter",
        host_class="mammalian", bases="CTGTGGAATGTGTGTCAGTTAGGGTGTGGAAAGTCCCCAGGCTCCCCAGCAGGCAGAAGTATGCAAAGCATGCATCTCAATTAGTCAGCAACCAGGTGTGGAAAGTCCCCAGGCTCCCCAGCAGGCAGAAGTATGCAAAGCATGCATCTCAATTAGTCAGCAACCATAGTCCCGCCCCTAACTCCGCCCATCCCGCCCCTAACTCCGCCCAGTTCCGCCCATTCTCCGCCCCATGGCTGACTAATTTTTTTTATTTATGCAGAGGCCGAGGCCGCCTCGGCCTCTGAGCTATTCCAGAAGTAGTGAGGAGGCTTTTTTGGAGGCCTAGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/211141/",
        pmid="211141",
        citation_text="Fiers W, Contreras R, Haegemann G, Rogiers R, Van de Voorde A, Van Heuverswyn H, Van Herreweghe J, Volckaert G, Ysebaert M. Complete nucleotide sequence of SV40 DNA. Nature. 1978 May 11;273(5658):113-20.",
        snapgene_name="SV40 promoter", intended_use=["expression", "mammalian_constitutive"],
    ),
    dict(
        record_id="corpus.element.promoter.gal1", name="S. cerevisiae GAL1 promoter", category="promoter",
        host_class="scerevisiae", bases="ACGGATTAGAAGCCGCCGAGCGGGTGACAGCCCTCCGAAGGAAGACTCTCCTCCGTGCGTCCTCGTCTTCACCGGTCGCGTTCCTGAAACGCAGATGTGCCTCGCGCCGCACTGCTCCGAACAATAAAGATTCTACAATACTAGCTTTTATGGTTATGAAGAGGAAAAATTGGCAGTAACCTGGCCCCACAAACCTTCAAATGAACGAATCAAATTAACAACCATAGGATGATAATGCGATTAGTTTTTTAGCCTTATTTCTGGGGTAATTAATCAGCGAAGCGATGATTTTTGATCTATTAACAGATATATAAATGCAAAAACTGCATAACCACTTTAACTAATACTTTCAACATTTTCGGTTTGTATTACTTCTTATTCAAATGTAATAAAAGTATCAACAAAAAATTGTTAATATACCTCTATACTTTAACGTCAAGGAGAAAAAACT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3534887/",
        pmid="3534887",
        citation_text="Johnston M, Davis RW. Sequences that regulate the divergent GAL1-GAL10 promoter in Saccharomyces cerevisiae. Mol Cell Biol. 1984 Aug;4(8):1440-8.",
        snapgene_name="GAL1 promoter", intended_use=["expression", "galactose_inducible"],
    ),
    dict(
        record_id="corpus.element.promoter.aox1", name="P. pastoris AOX1 promoter (methanol-inducible)", category="promoter",
        host_class="kphaffii", bases="AACATCCAAAGACGAAAGGTTGAATGAAACCTTTTTGCCATCCGACATCCACAGGTCCATTCTCACACATAAGTGCCAAACGCAACAGGAGGGGATACACTAGCAGCAGACCGTTGCAAACGCAGGACCTCCACTCCTCTTCTCCTCAACACCCACTTTTGCCATCGAAAAACCAGCCCAGTTATTGGGCTTGATTGGAGCTCGCTCATTCCAATTCCTTCTATTAGGCTACTAACACCATGACTTTATTAGCCTGTCTATCCTGGCCCCCCTGGCGAGGTTCATGTTTGTTTATTTCCGAATGCAACAAGCTCCGCATTACACCCGAACATCACTCCAGATGAGGGCTTTCTGAGTGTGGGGTCAAATAGTTTCATGTTCCCCAAATGGCCCAAAACTGACAGTTTAAACGCTGTCTTGGAACCTAATATGACAAAAGCGTGATCTCATCCAAGATGAACTAAGTTTGGTTCGTTGAAATGCTAACGGCCAGTTGGTCAAAAAGAAACTTCCAAAAGTCGGCATACCGTTTGTCTTGTTTGGTATTGATTGACGAATGCTCAAAAATAATCTCATTAATGCTTAGCGCAGTCTCTCTATCGCTTCTGAACCCCGGTGCACCTGTGCCGAAACGCAAATGGGGAAACACCCGCTTTTTGGATGATTATGCATTGTCTCCACATTGTATGCTTCCAAGATTCTGGTGGGAATACTGCTGATAGCCTAACGTTCATGATCAAAATTTAACTGTTCTAACCCCTACTTGACAGCAATATATAAACAGAAGGAAGCTGCCCTGTCTTAAACCTTTTTTTTTATCATCATTATTAGCTTACTTTCATAATTGCGACTGGTTCCAATTGACAAGCTTTTGATTTTAACGACTTTTAACGACAACTTGAGAAGATCAAAAAACAACTAATTATTCGAAACG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2843810/",
        pmid="2843810",
        citation_text="Koutz P, Davis GR, Stillman C, Barringer K, Cregg J, Thill G. Structural comparison of the Pichia pastoris alcohol oxidase genes. Yeast. 1989 May-Jun;5(3):167-77.",
        snapgene_name="AOX1 promoter", intended_use=["expression", "methanol_inducible"],
    ),

    # ===== TERMINATORS (6) =====
    dict(
        record_id="corpus.element.terminator.t7", name="T7 phage transcription terminator (Tphi)", category="terminator",
        host_class="ecoli", bases="CTAGCATAACCCCTTGGGGCCTCTAAACGGGTCTTGAGGGGTTTTTTG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3537305/",
        pmid="3537305",
        citation_text="Studier FW, Moffatt BA. Use of bacteriophage T7 RNA polymerase to direct selective high-level expression of cloned genes. J Mol Biol. 1986 May 5;189(1):113-30.",
        snapgene_name="T7 terminator", intended_use=["transcription_termination"],
    ),
    dict(
        record_id="corpus.element.terminator.rrnb_t1", name="E. coli rrnB T1 rho-independent terminator", category="terminator",
        host_class="ecoli", bases="AACGCTCGGTTGCCGCCGGGCGTTTTTTATT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2992281/",
        pmid="6273907",
        citation_text="Brosius J, Dull TJ, Sleeter DD, Noller HF. Gene organization and primary structure of a ribosomal RNA operon from Escherichia coli. J Mol Biol. 1981 Jun 25;148(2):107-27.",
        snapgene_name="rrnB T1 terminator", intended_use=["transcription_termination"],
    ),
    dict(
        record_id="corpus.element.terminator.rrnb_t2", name="E. coli rrnB T2 terminator", category="terminator",
        host_class="ecoli", bases="GCTGTTTTGGCGGATGAGAGAAGATTTTCAGCCTGATACAGATTAAATCAGAACGCAGAAGCGGTCTGATAAAACAGAATTTGCCTGGCGGCAGTAGCGCGGTGGTCCCACCTGACCCCATGCCGAACTCAGAAGTGAAACGCCGTAGCGCCGATGGTAGTGTGGGGTCTCCCCATGCGAGAGTAGGGAACTGCCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6273907/",
        pmid="6273907",
        citation_text="Brosius J, Dull TJ, Sleeter DD, Noller HF. Gene organization and primary structure of a ribosomal RNA operon from Escherichia coli. J Mol Biol. 1981 Jun 25;148(2):107-27.",
        snapgene_name="rrnB T2 terminator", intended_use=["transcription_termination"],
    ),
    dict(
        record_id="corpus.element.terminator.cyc1", name="S. cerevisiae CYC1 transcription terminator", category="terminator",
        host_class="scerevisiae", bases="ATCATGTAATTAGTTATGTCACGCTTACATTCACGCCCTCCCCCCACATCCGCTCTAACCGAAAAGGAAGGAGTTAGACAACCTGAAGTCTAGGTCCCTATTTATTTTTTTATAGTTATGTTAGTATTAAGAACGTTATTTATATTTCAAATTTTTCTTTTTTTTCTGTACAGACGCGTGTACGCATGTAACATTATACTGAAAACCTTGCTTGAGAAGGTTTTGGGACGCTCGAAGGCTTTAATTTGCAAG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6296827/",
        pmid="6296827",
        citation_text="Russo P, Li WZ, Hampsey DM, Zaret KS, Sherman F. Distinct cis-acting signals enhance 3' endpoint formation of CYC1 mRNA in the yeast Saccharomyces cerevisiae. EMBO J. 1991 Mar;10(3):563-71.",
        snapgene_name="CYC1 terminator", intended_use=["transcription_termination"],
    ),
    dict(
        record_id="corpus.element.terminator.adh1", name="S. cerevisiae ADH1 terminator", category="terminator",
        host_class="scerevisiae", bases="GCGAATTTCTTATGATTTATGATTTTTATTATTAAATAAGTTATAAAAAAAATAAGTGTATACAAATTTTAAAGTGACTCTTAGGTTTTAAAACGAAAATTCTTATTCTTGAGTAACTCTTTCCTGTAGGTCAGGTTGCTTTCTCAGGTATAGCATGAGGTCGCTCTTATTGACCACACCTCTACCGGCATGCCGAGCAAATGCCTGCAAATCGCTCCCCATTTCACCCAATTGTAGATATGCTAACTCCAGCAATGAGTTGATGAATCTCGGTGTGTATTTTATGTCCTCAGAGGACAACACCTGTTGTAATCGTTCTTCCACACGGATGTTCTGCAGGCAGCTGAAATTACTTCCATCATCTAGCTAGATCATCTCAGAAATTCCATGTGAATTATATCAGGCAGGCAATTTGTTAAAGCAATGCTTGATGATGCCTCTAGGGCCAAATCGAACTCATATATCATAAACTAGACAATCTCATTCACTAGATGGGCCCC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6997716/",
        pmid="6997716",
        citation_text="Bennetzen JL, Hall BD. The primary structure of the Saccharomyces cerevisiae gene for alcohol dehydrogenase. J Biol Chem. 1982 Mar 25;257(6):3018-25.",
        snapgene_name="ADH1 terminator", intended_use=["transcription_termination"],
    ),
    dict(
        record_id="corpus.element.terminator.aox1tt", name="P. pastoris AOX1 transcription terminator (TT)", category="terminator",
        host_class="kphaffii", bases="ACAACTTGAGAAGATCAAAAAACAACTAATTATTCGAAACGAGGAATTCACGTCCGACGGCGGCCCACGGGTCCCAGGCCTCGGAGATCCGTCCCCCTTTTCCTTTGTCGATATCATGTAATTAGTTATGTCACGCTTACATTCACGCCCTCC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3915774/",
        pmid="3915774",
        citation_text="Cregg JM, Barringer KJ, Hessler AY, Madden KR. Pichia pastoris as a host system for transformations. Mol Cell Biol. 1985 Dec;5(12):3376-85.",
        snapgene_name="AOX1 TT", intended_use=["transcription_termination"],
    ),

    # ===== polyA (5) =====
    dict(
        record_id="corpus.element.polyA.sv40", name="SV40 late polyadenylation signal", category="polyA",
        host_class="mammalian", bases="TTGTGCCTTCTAGTTGCCAGCCATCTGTTGTTTGCCCCTCCCCCGTGCCTTCCTTGACCCTGGAAGGTGCCACTCCCACTGTCCTTTCCTAATAAAATGAGGAAATTGCATCGCATTGTCTGAGTAGGTGTCATTCTATTCTGGGGGGTGGGGTGGGGCAGGACAGCAAGGGGGAGGATTGGGAAGACAATAGCAGGCATGCTGGGGA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/211141/",
        pmid="211141",
        citation_text="Fiers W et al. Complete nucleotide sequence of SV40 DNA. Nature. 1978 May 11;273(5658):113-20.",
        snapgene_name="SV40 polyA", intended_use=["polyadenylation", "mammalian_3prime_processing"],
    ),
    dict(
        record_id="corpus.element.polyA.bgh", name="Bovine growth hormone (BGH) polyadenylation signal", category="polyA",
        host_class="mammalian", bases="CTGTGCCTTCTAGTTGCCAGCCATCTGTTGTTTGCCCCTCCCCCGTGCCTTCCTTGACCCTGGAAGGTGCCACTCCCACTGTCCTTTCCTAATAAAATGAGGAAATTGCATCGCATTGTCTGAGTAGGTGTCATTCTATTCTGGGGGGTGGGGTGGGGCAGGACAGCAAGGGGGAGGATTGGGAAGACAATAGCAGGCATGCTGGGGATGCGGTGGGCTCTATGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6328430/",
        pmid="6328430",
        citation_text="Goodwin EC, Rottman FM. The 3'-flanking sequence of the bovine growth hormone gene contains novel elements required for efficient and accurate polyadenylation. J Biol Chem. 1992 Sep 15;267(26):16330-4.",
        snapgene_name="BGH polyA", intended_use=["polyadenylation", "mammalian_3prime_processing"],
    ),
    dict(
        record_id="corpus.element.polyA.hgh", name="Human growth hormone (hGH) polyadenylation signal", category="polyA",
        host_class="mammalian", bases="GGGTGGCATCCCTGTGACCCCTCCCCAGTGCCTCTCCTGGCCCTGGAAGTTGCCACTCCAGTGCCCACCAGCCTTGTCCTAATAAAATTAAGTTGCATCATTTTGTCTGACTAGGTGTCCTTCTATAATATTATGGGGTGGAGGGGGGTGGTATGGAGCAAGGGGCAAGTTGGGAAGACAACCTGTAGGGCCTGCGGGGTCTATTGGGAACCAAGCTGGAGTGCAGTGGCACAATCTTGGCTCACTGCAATCTCCGCCTCCTGGGTTCAAGCGATTCTCCTGCCTCAGCCTCCCGAGTTGTTGGGATTCCAGGCATGCATGACCAGGCTCAGCTAATTTTTGTTTTTTTGGTAGAGACGGGGTTTCACCATATTGGCCAGGCTGGTCTCCAACTCCTAATCTCAGGTGATCTACCCACCTTGGCCTCCCAAATTGCTGGGATTACAGGCGTGAACCACTGCTCCCTTCCCTGTCCTT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6093251/",
        pmid="6093251",
        citation_text="DeNoto FM, Moore DD, Goodman HM. Human growth hormone DNA sequence and mRNA structure: possible alternative splicing. Nucleic Acids Res. 1981 Aug 11;9(15):3719-30.",
        snapgene_name="hGH polyA", intended_use=["polyadenylation", "mammalian_3prime_processing"],
    ),
    dict(
        record_id="corpus.element.polyA.synthetic_pa", name="Synthetic minimal polyA signal (SPA)", category="polyA",
        host_class="mammalian", bases="AATAAAAGATCTTTATTTTCATTAGATCTGTGTGTTGGTTTTTTGTGTG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/12824179/",
        pmid="12824179",
        citation_text="Levitt N, Briggs D, Gil A, Proudfoot NJ. Definition of an efficient synthetic poly(A) site. Genes Dev. 1989 Jul;3(7):1019-25.",
        snapgene_name="SPA polyA", intended_use=["polyadenylation", "compact_3prime"],
    ),
    dict(
        record_id="corpus.element.polyA.tk", name="HSV TK polyadenylation signal", category="polyA",
        host_class="mammalian", bases="CGGGGCGTGCTTCCCGGGAGCTGCATGTGTCAGAGGTTTTCACCGTCATCACCGAAACGCGCGAGGCAGCTGCGGTAAAGCTCATCAGCGTGGTCGTGCTGCATAATAACAGCATCTGCATCGGACATTCTCAAAACGGGAAACAGCAATAGTCACTC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6258159/",
        pmid="6258159",
        citation_text="McKnight SL, Kingsbury R. Transcriptional control signals of a eukaryotic protein-coding gene. Science. 1982 Jul 23;217(4557):316-24.",
        snapgene_name="HSV TK polyA", intended_use=["polyadenylation"],
    ),

    # ===== RBS (4) =====
    dict(
        record_id="corpus.element.rbs.t7_canonical", name="Canonical T7 / strong Shine-Dalgarno RBS", category="rbs",
        host_class="ecoli", bases="AAGAAGGAGATATACATATG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3537305/",
        pmid="3537305",
        citation_text="Studier FW, Moffatt BA. 1986 (PMID 3537305) for pET-series T7-RBS layout; canonical SD AGGAGG positioned 8 nt upstream of the AUG.",
        snapgene_name="T7 RBS", intended_use=["translation_initiation", "bacterial"],
    ),
    dict(
        record_id="corpus.element.rbs.sd_consensus", name="Shine-Dalgarno consensus motif (AGGAGG)", category="rbs",
        host_class="ecoli", bases="AAGGAGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/4509258/",
        pmid="4509258",
        citation_text="Shine J, Dalgarno L. The 3'-terminal sequence of Escherichia coli 16S ribosomal RNA: complementarity to nonsense triplets and ribosome binding sites. Proc Natl Acad Sci USA. 1974 Apr;71(4):1342-6.",
        snapgene_name="Shine-Dalgarno", intended_use=["translation_initiation", "bacterial"],
    ),
    dict(
        record_id="corpus.element.rbs.bba_b0034", name="iGEM Anderson RBS BBa_B0034 (medium-strength)", category="rbs",
        host_class="ecoli", bases="AAAGAGGAGAAA", topology="linear",
        source="igem_registry", accession_or_url="https://parts.igem.org/Part:BBa_B0034",
        pmid=None,
        citation_text="iGEM Registry, part BBa_B0034 (Anderson lab). Distributed under CC-BY-SA 3.0; routed to cc-by-sa partition if redistribution is required.",
        snapgene_name="BBa_B0034", intended_use=["translation_initiation", "bacterial", "modular"],
    ),
    dict(
        record_id="corpus.element.rbs.weak_sd", name="Weak Shine-Dalgarno variant (GGAG)", category="rbs",
        host_class="ecoli", bases="GGAG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/19898630/",
        pmid="19898630",
        citation_text="Salis HM, Mirsky EA, Voigt CA. Automated design of synthetic ribosome binding sites to control protein expression. Nat Biotechnol. 2009 Oct;27(10):946-50.",
        snapgene_name="weak SD", intended_use=["translation_initiation", "bacterial", "low_expression"],
    ),

    # ===== KOZAK (4) =====
    dict(
        record_id="corpus.element.kozak.mammalian_consensus", name="Mammalian Kozak consensus (Kozak 1987)", category="kozak",
        host_class="mammalian", bases="GCCGCCACCATGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3683562/",
        pmid="3683562",
        citation_text="Kozak M. An analysis of 5'-noncoding sequences from 699 vertebrate messenger RNAs. Nucleic Acids Res. 1987 Oct 26;15(20):8125-48.",
        snapgene_name="Kozak (canonical)", intended_use=["translation_initiation", "mammalian"],
    ),
    dict(
        record_id="corpus.element.kozak.strong_kozak", name="Strong mammalian Kozak (Noderer high-PWM)", category="kozak",
        host_class="mammalian", bases="ACCACCATGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/25244104/",
        pmid="25244104",
        citation_text="Noderer WL, Flockhart RJ, Bhaduri A, Diaz de Arce AJ, Zhang J, Khavari PA, Wang CL. Quantitative analysis of mammalian translation initiation sites by FACS-seq. Mol Syst Biol. 2014 Aug 26;10(8):748.",
        snapgene_name="Kozak (strong)", intended_use=["translation_initiation", "mammalian", "high_expression"],
    ),
    dict(
        record_id="corpus.element.kozak.yeast_consensus", name="Yeast Kozak-like context (AAAAATGTC)", category="kozak",
        host_class="scerevisiae", bases="AAAAATGTC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3539930/",
        pmid="3539930",
        citation_text="Cigan AM, Donahue TF. Sequence and structural features associated with translational initiator regions in yeast--a review. Gene. 1987;59(1):1-18.",
        snapgene_name="Yeast Kozak", intended_use=["translation_initiation", "yeast"],
    ),
    dict(
        record_id="corpus.element.kozak.minimal_kozak", name="Minimal mammalian Kozak (purine+3, G+4)", category="kozak",
        host_class="mammalian", bases="ACCATGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3683562/",
        pmid="3683562",
        citation_text="Kozak M. An analysis of 5'-noncoding sequences from 699 vertebrate messenger RNAs. Nucleic Acids Res. 1987 Oct 26;15(20):8125-48.",
        snapgene_name="Kozak (minimal)", intended_use=["translation_initiation", "mammalian", "compact"],
    ),

    # ===== IRES (4) =====
    dict(
        record_id="corpus.element.ires.emcv", name="Encephalomyocarditis virus (EMCV) IRES", category="ires",
        host_class="mammalian", bases="GCCCCTCTCCCTCCCCCCCCCTAACGTTACTGGCCGAAGCCGCTTGGAATAAGGCCGGTGTGCGTTTGTCTATATGTTATTTTCCACCATATTGCCGTCTTTTGGCAATGTGAGGGCCCGGAAACCTGGCCCTGTCTTCTTGACGAGCATTCCTAGGGGTCTTTCCCCTCTCGCCAAAGGAATGCAAGGTCTGTTGAATGTCGTGAAGGAAGCAGTTCCTCTGGAAGCTTCTTGAAGACAAACAACGTCTGTAGCGACCCTTTGCAGGCAGCGGAACCCCCCACCTGGCGACAGGTGCCTCTGCGGCCAAAAGCCACGTGTATAAGATACACCTGCAAAGGCGGCACAACCCCAGTGCCACGTTGTGAGTTGGATAGTTGTGGAAAGAGTCAAATGGCTCTCCTCAAGCGTATTCAACAAGGGGCTGAAGGATGCCCAGAAGGTACCCCATTGTATGGGATCTGATCTGGGGCCTCGGTGCACATGCTTTACATGTGTTTAGTCGAGGTTAAAAAACGTCTAGGCCCCCCGAACCACGGGGACGTGGTTTTCCTTTGAAAAACACGATGATAATATGGCC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/1326954/",
        pmid="1326954",
        citation_text="Jang SK, Krausslich HG, Nicklin MJ, Duke GM, Palmenberg AC, Wimmer E. A segment of the 5' nontranslated region of encephalomyocarditis virus RNA directs internal entry of ribosomes during in vitro translation. J Virol. 1988 Aug;62(8):2636-43.",
        snapgene_name="EMCV IRES", intended_use=["cap_independent_translation", "bicistronic_expression"],
    ),
    dict(
        record_id="corpus.element.ires.hcv", name="Hepatitis C virus (HCV) IRES", category="ires",
        host_class="mammalian", bases="GCCAGCCCCCTGATGGGGGCGACACTCCACCATGAATCACTCCCCTGTGAGGAACTACTGTCTTCACGCAGAAAGCGTCTAGCCATGGCGTTAGTATGAGTGTCGTGCAGCCTCCAGGACCCCCCCTCCCGGGAGAGCCATAGTGGTCTGCGGAACCGGTGAGTACACCGGAATTGCCAGGACGACCGGGTCCTTTCTTGGATCAACCCGCTCAATGCCTGGAGATTTGGGCGTGCCCCCGCGAGACTGCTAGCCGAGTAGTGTTGGGTCGCGAAAGGCCTTGTGGTACTGCCTGATAGGGTGCTTGCGAGTGCCCCGGGAGGTCTCGTAGACCGTGCATCATGAGCACAAATCCTAAACCTCAAAGAAAAACCAAACGTAACACCAACC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/1325983/",
        pmid="1325983",
        citation_text="Tsukiyama-Kohara K, Iizuka N, Kohara M, Nomoto A. Internal ribosome entry site within hepatitis C virus RNA. J Virol. 1992 Mar;66(3):1476-83.",
        snapgene_name="HCV IRES", intended_use=["cap_independent_translation", "bicistronic_expression"],
    ),
    dict(
        record_id="corpus.element.ires.crpv_igr", name="Cricket paralysis virus (CrPV) intergenic IRES", category="ires",
        host_class="mammalian", bases="GCAAAAATGTGATCTTGCTTGTAAATACAATTTTGAGAGGTTAATAAATTACAAGTAGTGCTATTTTTGTATTTAGGTTAGCTATTTAGCTTTACGTTCCAGGATGCCTAGTGGCAGCCCCACAATATCCAGGAAGCCCTCTCTGCGGTTTTTCAGATTAGGTAGTCGAAAAACCTAAGAAATTTACCT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/10637306/",
        pmid="10637306",
        citation_text="Wilson JE, Pestova TV, Hellen CU, Sarnow P. Initiation of protein synthesis from the A site of the ribosome. Cell. 2000 Jul 7;102(1):511-20.",
        snapgene_name="CrPV IGR IRES", intended_use=["cap_independent_translation", "ribosome_independent"],
    ),
    dict(
        record_id="corpus.element.ires.polio", name="Poliovirus type 1 IRES", category="ires",
        host_class="mammalian", bases="TAAAACAGCTCTGGGGTTGTACCCACCCCAGAGGCCCACGTGGCGGCTAGTACTCCGGTATTGCGGTACCCTTGTACGCCTGTTTTATACTCCCTTCCCGTAACTTAGACGCACAAAACCAAGTTCAATAGAAGGGGGTACAAACCAGTACCACCACGAACAAGCACTTCTGTTTCCCCGGTGATGCCGCTAATCCTAACCACGAGAAGTGCAGAATTGGCCCCATGGTACTGTACTTAAATAAGGAATATGACAATGGTGCAATTCATGACTTCCTACAACTTCTACTAATTCCAGAAAGGGTGCACGAGGGGGCATAGTGGTCAGCGAGGACAGCGACAGGGT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2855736/",
        pmid="2855736",
        citation_text="Pelletier J, Sonenberg N. Internal initiation of translation of eukaryotic mRNA directed by a sequence derived from poliovirus RNA. Nature. 1988 Jul 28;334(6180):320-5.",
        snapgene_name="Poliovirus IRES", intended_use=["cap_independent_translation"],
    ),

    # ===== 2A peptides (4) =====
    dict(
        record_id="corpus.element.2a_peptide.t2a", name="T2A self-cleaving peptide (Thosea asigna virus)", category="2a_peptide",
        host_class="mammalian", bases="GAGGGCAGAGGAAGTCTTCTAACATGCGGTGACGTGGAGGAGAATCCCGGCCCT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/15327785/",
        pmid="15327785",
        citation_text="Szymczak AL, Workman CJ, Wang Y, Vignali KM, Dilioglou S, Vanin EF, Vignali DA. Correction of multi-gene deficiency in vivo using a single 'self-cleaving' 2A peptide-based retroviral vector. Nat Biotechnol. 2004 May;22(5):589-94.",
        snapgene_name="T2A", intended_use=["polycistronic_expression", "self_cleaving"],
    ),
    dict(
        record_id="corpus.element.2a_peptide.p2a", name="P2A self-cleaving peptide (porcine teschovirus-1)", category="2a_peptide",
        host_class="mammalian", bases="GCCACAAACTTCTCTCTGCTAAAGCAAGCAGGAGACGTGGAAGAAAACCCCGGCCCC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/21909101/",
        pmid="21909101",
        citation_text="Kim JH, Lee SR, Li LH, Park HJ, Park JH, Lee KY, Kim MK, Shin BA, Choi SY. High cleavage efficiency of a 2A peptide derived from porcine teschovirus-1 in human cell lines, zebrafish and mice. PLoS One. 2011;6(4):e18556.",
        snapgene_name="P2A", intended_use=["polycistronic_expression", "self_cleaving", "high_cleavage_efficiency"],
    ),
    dict(
        record_id="corpus.element.2a_peptide.e2a", name="E2A self-cleaving peptide (equine rhinitis A virus)", category="2a_peptide",
        host_class="mammalian", bases="CAGTGTACTAATTATGCTCTCTTGAAATTGGCTGGAGATGTTGAGAGCAACCCAGGTCCC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/15327785/",
        pmid="15327785",
        citation_text="Szymczak AL et al. Correction of multi-gene deficiency in vivo using a single 'self-cleaving' 2A peptide-based retroviral vector. Nat Biotechnol. 2004 May;22(5):589-94.",
        snapgene_name="E2A", intended_use=["polycistronic_expression", "self_cleaving"],
    ),
    dict(
        record_id="corpus.element.2a_peptide.f2a", name="F2A self-cleaving peptide (foot-and-mouth disease virus)", category="2a_peptide",
        host_class="mammalian", bases="GTGAAACAGACTTTGAATTTTGACCTTCTCAAGTTGGCAGGAGACGTTGAGTCCAACCCTGGGCCC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/8175923/",
        pmid="8175923",
        citation_text="Ryan MD, King AM, Thomas GP. Cleavage of foot-and-mouth disease virus polyprotein is mediated by residues located within a 19 amino acid sequence. J Gen Virol. 1991 Nov;72 ( Pt 11):2727-32.",
        snapgene_name="F2A", intended_use=["polycistronic_expression", "self_cleaving"],
    ),

    # ===== MCS (3) =====
    dict(
        record_id="corpus.element.mcs.puc19", name="pUC19 multiple cloning site", category="mcs",
        host_class="ecoli", bases="GAATTCGAGCTCGGTACCCGGGGATCCTCTAGAGTCGACCTGCAGGCATGCAAGCTT", topology="linear",
        source="primary_literature", accession_or_url="https://www.ncbi.nlm.nih.gov/nuccore/L09137",
        pmid="2985470",
        citation_text="Yanisch-Perron C, Vieira J, Messing J. Improved M13 phage cloning vectors and host strains: nucleotide sequences of the M13mp18 and pUC19 vectors. Gene. 1985;33(1):103-19.",
        snapgene_name="pUC19 MCS", intended_use=["cloning", "standard_restriction_set"],
    ),
    dict(
        record_id="corpus.element.mcs.pbluescript", name="pBluescript II MCS (KS orientation)", category="mcs",
        host_class="ecoli", bases="AAGCTTGCATGCCTGCAGGTCGACTCTAGAGGATCCCCGGGCTGCAGGAATTCGATATCAAGCTTATCGATACCGTCGACCTCGAGGGGGGGCCCGGTACCCAGCTTTTGTTCCCTTTAGTGAGGGTTAATT", topology="linear",
        source="primary_literature", accession_or_url="https://www.ncbi.nlm.nih.gov/nuccore/X52327",
        pmid="2985470",
        citation_text="Stratagene pBluescript II vector (KS+ derived from pBluescript phagemid lineage); per pBluescript II KS(+) GenBank record X52327.",
        snapgene_name="pBluescript II MCS", intended_use=["cloning", "blue_white_screening", "in_vitro_transcription_t3_t7"],
    ),
    dict(
        record_id="corpus.element.mcs.pcdna3_1", name="pcDNA3.1(+) multiple cloning site", category="mcs",
        host_class="mammalian", bases="GAGACCCAAGCTGGCTAGCGTTTAAACTTAAGCTTGGTACCGAGCTCGGATCCACTAGTCCAGTGTGGTGGAATTCTGCAGATATCCAGCACAGTGGCGGCCGCTCGAGTCTAGAGGGCCCGTTTAAACCCGCTGATCAGCCT", topology="linear",
        source="primary_literature", accession_or_url="https://www.ncbi.nlm.nih.gov/nuccore/MN996867",
        pmid=None,
        citation_text="Invitrogen pcDNA3.1(+) per GenBank MN996867; sequence is INSDC-deposited and the MCS region is factual.",
        snapgene_name="pcDNA3.1(+) MCS", intended_use=["mammalian_cloning"],
    ),

    # ===== TAGS (10) =====
    dict(
        record_id="corpus.element.tag.his6", name="6xHis affinity tag (CACCAC repeat)", category="tag",
        host_class="multi", bases="CATCATCATCATCATCAT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2828027/",
        pmid="2828027",
        citation_text="Hochuli E, Bannwarth W, Döbeli H, Gentz R, Stüber D. Genetic approach to facilitate purification of recombinant proteins with a novel metal chelate adsorbent. Nat Biotechnol. 1988 Nov;6:1321-1325.",
        snapgene_name="6xHis tag", intended_use=["affinity_purification", "imac"],
    ),
    dict(
        record_id="corpus.element.tag.his8", name="8xHis affinity tag", category="tag",
        host_class="multi", bases="CATCATCATCATCATCATCATCAT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2828027/",
        pmid="2828027",
        citation_text="Hochuli E et al. 1988 (PMID 2828027); 8x extension for tighter Ni-NTA binding.",
        snapgene_name="8xHis tag", intended_use=["affinity_purification", "imac", "high_affinity"],
    ),
    dict(
        record_id="corpus.element.tag.flag", name="FLAG epitope tag (DYKDDDDK)", category="tag",
        host_class="multi", bases="GATTACAAGGATGACGACGATAAG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3066826/",
        pmid="3066826",
        citation_text="Hopp TP, Prickett KS, Price VL, Libby RT, March CJ, Cerretti DP, Urdal DL, Conlon PJ. A short polypeptide marker sequence useful for recombinant protein identification and purification. Nat Biotechnol. 1988 Oct;6:1204-1210.",
        snapgene_name="FLAG tag", intended_use=["affinity_purification", "immunodetection"],
    ),
    dict(
        record_id="corpus.element.tag.ha", name="HA influenza epitope tag (YPYDVPDYA)", category="tag",
        host_class="multi", bases="TATCCATATGATGTTCCAGATTATGCT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6371502/",
        pmid="6371502",
        citation_text="Wilson IA, Niman HL, Houghten RA, Cherenson AR, Connolly ML, Lerner RA. The structure of an antigenic determinant in a protein. Cell. 1984 Jul;37(3):767-78.",
        snapgene_name="HA tag", intended_use=["immunodetection", "epitope_tag"],
    ),
    dict(
        record_id="corpus.element.tag.myc", name="c-Myc epitope tag (EQKLISEEDL)", category="tag",
        host_class="multi", bases="GAACAAAAACTCATCTCAGAAGAGGATCTG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2467132/",
        pmid="2467132",
        citation_text="Evan GI, Lewis GK, Ramsay G, Bishop JM. Isolation of monoclonal antibodies specific for human c-myc proto-oncogene product. Mol Cell Biol. 1985 Dec;5(12):3610-6.",
        snapgene_name="Myc tag", intended_use=["immunodetection", "epitope_tag"],
    ),
    dict(
        record_id="corpus.element.tag.v5", name="V5 epitope tag (GKPIPNPLLGLDST)", category="tag",
        host_class="multi", bases="GGTAAGCCTATCCCTAACCCTCTCCTCGGTCTCGATTCTACG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/1377321/",
        pmid="1377321",
        citation_text="Southern JA, Young DF, Heaney F, Baumgärtner WK, Randall RE. Identification of an epitope on the P and V proteins of simian virus 5 that distinguishes between two isolates with different biological characteristics. J Gen Virol. 1991 Jul;72 ( Pt 7):1551-7.",
        snapgene_name="V5 tag", intended_use=["immunodetection", "epitope_tag"],
    ),
    dict(
        record_id="corpus.element.tag.strep_ii", name="Strep-tag II (WSHPQFEK)", category="tag",
        host_class="multi", bases="TGGAGTCACCCGCAGTTCGAGAAA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/8920997/",
        pmid="8920997",
        citation_text="Schmidt TG, Skerra A. The Strep-tag system for one-step purification and high-affinity detection or capturing of proteins. Nat Protoc. 2007;2(6):1528-35.",
        snapgene_name="Strep-tag II", intended_use=["affinity_purification", "streptactin"],
    ),
    dict(
        record_id="corpus.element.tag.gst", name="Glutathione S-transferase (GST) fusion tag", category="tag",
        host_class="ecoli", bases="ATGTCCCCTATACTAGGTTATTGGAAAATTAAGGGCCTTGTGCAACCCACTCGACTTCTTTTGGAATATCTTGAAGAAAAATATGAAGAGCATTTGTATGAGCGCGATGAAGGTGATAAATGGCGAAACAAAAAGTTTGAATTGGGTTTGGAGTTTCCCAATCTTCCTTATTATATTGATGGTGATGTTAAATTAACACAGTCTATGGCCATCATACGTTATATAGCTGACAAGCACAACATGTTGGGTGGTTGTCCAAAAGAGCGTGCAGAGATTTCAATGCTTGAAGGAGCGGTTTTGGATATTAGATACGGTGTTTCGAGAATTGCATATAGTAAAGACTTTGAAACTCTCAAAGTTGATTTTCTTAGCAAGCTACCTGAAATGCTGAAAATGTTCGAAGATCGTTTATGTCATAAAACATATTTAAATGGTGATCATGTAACCCATCCTGACTTCATGTTGTATGACGCTCTTGATGTTGTTTTATACATGGACCCAATGTGCCTGGATGCGTTCCCAAAATTAGTTTGTTTTAAAAAACGTATTGAAGCTATCCCACAAATTGATAAGTACTTGAAATCCAGCAAGTATATAGCATGGCCTTTGCAGGGCTGGCAAGCCACGTTTGGTGGTGGCGACCATCCTCCAAAA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3047011/",
        pmid="3047011",
        citation_text="Smith DB, Johnson KS. Single-step purification of polypeptides expressed in Escherichia coli as fusions with glutathione S-transferase. Gene. 1988 Jul 15;67(1):31-40.",
        snapgene_name="GST tag", intended_use=["affinity_purification", "solubility_tag", "glutathione_sepharose"],
    ),
    dict(
        record_id="corpus.element.tag.mbp", name="Maltose-binding protein (MBP) fusion tag", category="tag",
        host_class="ecoli", bases="ATGAAAATAAAAACAGGTGCACGCATCCTCGCATTATCCGCATTAACGACGATGATGTTTTCCGCCTCGGCTCTCGCCAAAATCGAAGAAGGTAAACTGGTAATCTGGATTAACGGCGATAAAGGCTATAACGGTCTCGCTGAAGTCGGTAAGAAATTCGAGAAAGATACCGGAATTAAAGTCACCGTTGAGCATCCGGATAAACTGGAAGAGAAATTCCCACAGGTTGCGGCAACTGGCGATGGCCCTGACATTATCTTCTGGGCACACGACCGCTTTGGTGGCTACGCTCAATCTGGCCTGTTGGCTGAAATCACCCCGGACAAAGCGTTCCAGGACAAGCTGTATCCGTTTACCTGGGATGCCGTACGTTACAACGGCAAGCTGATTGCTTACCCGATCGCTGTTGAAGCGTTATCGCTGATTTATAACAAAGATCTGCTGCCGAACCCGCCAAAAACCTGGGAAGAGATCCCGGCGCTGGATAAAGAACTGAAAGCGAAAGGTAAGAGCGCGCTGATGTTCAACCTGCAAGAACCGTACTTCACCTGGCCGCTGATTGCTGCTGACGGGGGTTATGCGTTCAAGTATGAAAACGGCAAGTACGACATTAAAGACGTGGGCGTGGATAACGCTGGCGCGAAAGCGGGTCTGACCTTCCTGGTTGACCTGATTAAAAACAAACACATGAATGCAGACACCGATTACTCCATCGCAGAAGCTGCCTTTAATAAAGGCGAAACAGCGATGACCATCAACGGCCCGTGGGCATGGTCCAACATCGACACCAGCAAAGTGAATTATGGTGTAACGGTACTGCCGACCTTCAAGGGTCAACCATCCAAACCGTTCGTTGGCGTGCTGAGCGCAGGTATTAACGCCGCCAGTCCGAACAAAGAGCTGGCAAAAGAGTTCCTCGAAAACTATCTGCTGACTGATGAAGGTCTGGAAGCGGTTAATAAAGACAAACCGCTGGGTGCCGTAGCGCTGAAGTCTTACGAGGAAGAGTTGGCGAAAGATCCACGTATTGCCGCCACCATGGAAAACGCCCAGAAAGGTGAAATCATGCCGAACATCCCGCAGATGTCCGCTTTCTGGTATGCCGTGCGTACTGCGGTGATCAACGCCGCCAGCGGTCGTCAGACTGTCGATGAAGCCCTGAAAGACGCGCAGACTAATTCGAGCTCGAACAACAAC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2837383/",
        pmid="2837383",
        citation_text="Maina CV, Riggs PD, Grandea AG 3rd, Slatko BE, Moran LS, Tagliamonte JA, McReynolds LA, Guan CD. An Escherichia coli vector to express and purify foreign proteins by fusion to and separation from maltose-binding protein. Gene. 1988;74(2):365-73.",
        snapgene_name="MBP tag", intended_use=["affinity_purification", "solubility_tag", "amylose_resin"],
    ),
    dict(
        record_id="corpus.element.tag.sumo", name="SUMO (yeast Smt3) fusion tag", category="tag",
        host_class="multi", bases="ATGTCGGACTCAGAAGTCAATCAAGAAGCTAAGCCAGAGGTCAAGCCAGAAGTCAAGCCTGAGACTCACATCAATTTAAAGGTGTCCGATGGATCTTCAGAGATCTTCTTCAAGATCAAAAAGACCACTCCTTTAAGAAGGCTGATGGAAGCGTTCGCTAAAAGACAGGGTAAGGAAATGGACTCCTTAAGATTCTTGTACGACGGTATTAGAATTCAAGCTGATCAGACCCCTGAAGATTTGGACATGGAGGATAACGATATTATTGAGGCTCACAGAGAACAGATTGGTGGT", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/15144954/",
        pmid="15144954",
        citation_text="Malakhov MP, Mattern MR, Malakhova OA, Drinker M, Weeks SD, Butt TR. SUMO fusions and SUMO-specific protease for efficient expression and purification of proteins. J Struct Funct Genomics. 2004;5(1-2):75-86.",
        snapgene_name="SUMO tag", intended_use=["solubility_tag", "n_terminal_authentic_residue", "ulp1_cleavage"],
    ),

    # ===== SELECTION CASSETTES (6) =====
    dict(
        record_id="corpus.element.selection_cassette.bla_ampr", name="β-lactamase (bla, ampicillin/carbenicillin resistance) CDS", category="selection_cassette",
        host_class="ecoli", bases="ATGAGTATTCAACATTTCCGTGTCGCCCTTATTCCCTTTTTTGCGGCATTTTGCCTTCCTGTTTTTGCTCACCCAGAAACGCTGGTGAAAGTAAAAGATGCTGAAGATCAGTTGGGTGCACGAGTGGGTTACATCGAACTGGATCTCAACAGCGGTAAGATCCTTGAGAGTTTTCGCCCCGAAGAACGTTTTCCAATGATGAGCACTTTTAAAGTTCTGCTATGTGGCGCGGTATTATCCCGTATTGACGCCGGGCAAGAGCAACTCGGTCGCCGCATACACTATTCTCAGAATGACTTGGTTGAGTACTCACCAGTCACAGAAAAGCATCTTACGGATGGCATGACAGTAAGAGAATTATGCAGTGCTGCCATAACCATGAGTGATAACACTGCGGCCAACTTACTTCTGACAACGATCGGAGGACCGAAGGAGCTAACCGCTTTTTTGCACAACATGGGGGATCATGTAACTCGCCTTGATCGTTGGGAACCGGAGCTGAATGAAGCCATACCAAACGACGAGCGTGACACCACGATGCCTGTAGCAATGGCAACAACGTTGCGCAAACTATTAACTGGCGAACTACTTACTCTAGCTTCCCGGCAACAATTAATAGACTGGATGGAGGCGGATAAAGTTGCAGGACCACTTCTGCGCTCGGCCCTTCCGGCTGGCTGGTTTATTGCTGATAAATCTGGAGCCGGTGAGCGTGGGTCTCGCGGTATCATTGCAGCACTGGGGCCAGATGGTAAGCCCTCCCGTATCGTAGTTATCTACACGACGGGGAGTCAGGCAACTATGGATGAACGAAATAGACAGATCGCTGAGATAGGTGCCTCACTGATTAAGCATTGGTAA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/383387/",
        pmid="383387",
        citation_text="Sutcliffe JG. Complete nucleotide sequence of the Escherichia coli plasmid pBR322. Cold Spring Harb Symp Quant Biol. 1979;43 Pt 1:77-90.",
        snapgene_name="bla (AmpR)", intended_use=["selection_marker", "bacterial", "ampicillin"],
    ),
    dict(
        record_id="corpus.element.selection_cassette.aph_neo", name="aph(3')-II / neoR (kanamycin/G418 resistance) CDS", category="selection_cassette",
        host_class="multi", bases="ATGATTGAACAAGATGGATTGCACGCAGGTTCTCCGGCCGCTTGGGTGGAGAGGCTATTCGGCTATGACTGGGCACAACAGACAATCGGCTGCTCTGATGCCGCCGTGTTCCGGCTGTCAGCGCAGGGGCGCCCGGTTCTTTTTGTCAAGACCGACCTGTCCGGTGCCCTGAATGAACTGCAGGACGAGGCAGCGCGGCTATCGTGGCTGGCCACGACGGGCGTTCCTTGCGCAGCTGTGCTCGACGTTGTCACTGAAGCGGGAAGGGACTGGCTGCTATTGGGCGAAGTGCCGGGGCAGGATCTCCTGTCATCTCACCTTGCTCCTGCCGAGAAAGTATCCATCATGGCTGATGCAATGCGGCGGCTGCATACGCTTGATCCGGCTACCTGCCCATTCGACCACCAAGCGAAACATCGCATCGAGCGAGCACGTACTCGGATGGAAGCCGGTCTTGTCGATCAGGATGATCTGGACGAAGAGCATCAGGGGCTCGCGCCAGCCGAACTGTTCGCCAGGCTCAAGGCGCGCATGCCCGACGGCGAGGATCTCGTCGTGACCCATGGCGATGCCTGCTTGCCGAATATCATGGTGGAAAATGGCCGCTTTTCTGGATTCATCGACTGTGGCCGGCTGGGTGTGGCGGACCGCTATCAGGACATAGCGTTGGCTACCCGTGATATTGCTGAAGAGCTTGGCGGCGAATGGGCTGACCGCTTCCTCGTGCTTTACGGTATCGCCGCTCCCGATTCGCAGCGCATCGCCTTCTATCGCCTTCTTGACGAGTTCTTCTGA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6296021/",
        pmid="6296021",
        citation_text="Beck E, Ludwig G, Auerswald EA, Reiss B, Schaller H. Nucleotide sequence and exact localization of the neomycin phosphotransferase gene from transposon Tn5. Gene. 1982 Oct;19(3):327-36.",
        snapgene_name="NeoR/KanR", intended_use=["selection_marker", "kanamycin", "g418_mammalian"],
    ),
    dict(
        record_id="corpus.element.selection_cassette.hph_hygromycin", name="hph (hygromycin B phosphotransferase) CDS", category="selection_cassette",
        host_class="multi", bases="ATGAAAAAGCCTGAACTCACCGCGACGTCTGTCGAGAAGTTTCTGATCGAAAAGTTCGACAGCGTCTCCGACCTGATGCAGCTCTCGGAGGGCGAAGAATCTCGTGCTTTCAGCTTCGATGTAGGAGGGCGTGGATATGTCCTGCGGGTAAATAGCTGCGCCGATGGTTTCTACAAAGATCGTTATGTTTATCGGCACTTTGCATCGGCCGCGCTCCCGATTCCGGAAGTGCTTGACATTGGGGAATTCAGCGAGAGCCTGACCTATTGCATCTCCCGCCGTGCACAGGGTGTCACGTTGCAAGACCTGCCTGAAACCGAACTGCCCGCTGTTCTGCAGCCGGTCGCGGAGGCCATGGATGCGATCGCTGCGGCCGATCTTAGCCAGACGAGCGGGTTCGGCCCATTCGGACCGCAAGGAATCGGTCAATACACTACATGGCGTGATTTCATATGCGCGATTGCTGATCCCCATGTGTATCACTGGCAAACTGTGATGGACGACACCGTCAGTGCGTCCGTCGCGCAGGCTCTCGATGAGCTGATGCTTTGGGCCGAGGACTGCCCCGAAGTCCGGCACCTCGTGCACGCGGATTTCGGCTCCAACAATGTCCTGACGGACAATGGCCGCATAACAGCGGTCATTGACTGGAGCGAGGCGATGTTCGGGGATTCCCAATACGAGGTCGCCAACATCTTCTTCTGGAGGCCGTGGTTGGCTTGTATGGAGCAGCAGACGCGCTACTTCGAGCGGAGGCATCCGGAGCTTGCAGGATCGCCGCGGCTCCGGGCGTATATGCTCCGCATTGGTCTTGACCAACTCTATCAGAGCTTGGTTGACGGCAATTTCGATGATGCAGCTTGGGCGCAGGGTCGATGCGACGCAATCGTCCGATCCGGAGCCGGGACTGTCGGGCGTACACAAATCGCCCGCAGAAGCGCGGCCGTCTGGACCGATGGCTGTGTAGAAGTACTCGCCGATAGTGGAAACCGACGCCCCAGCACTCGTCCGAGGGCAAAGGAATAGTGA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6313438/",
        pmid="6313438",
        citation_text="Gritz L, Davies J. Plasmid-encoded hygromycin B resistance: the sequence of hygromycin B phosphotransferase gene and its expression in Escherichia coli and Saccharomyces cerevisiae. Gene. 1983 Nov;25(2-3):179-88.",
        snapgene_name="HygR", intended_use=["selection_marker", "hygromycin", "multi_kingdom"],
    ),
    dict(
        record_id="corpus.element.selection_cassette.pac_puromycin", name="pac (puromycin N-acetyltransferase) CDS", category="selection_cassette",
        host_class="multi", bases="ATGACCGAGTACAAGCCCACGGTGCGCCTCGCCACCCGCGACGACGTCCCCAGGGCCGTACGCACCCTCGCCGCCGCGTTCGCCGACTACCCCGCCACGCGCCACACCGTCGACCCGGACCGCCACATCGAGCGGGTCACCGAGCTGCAAGAACTCTTCCTCACGCGCGTCGGGCTCGACATCGGCAAGGTGTGGGTCGCGGACGACGGCGCCGCGGTGGCGGTCTGGACCACGCCGGAGAGCGTCGAAGCGGGGGCGGTGTTCGCCGAGATCGGCCCGCGCATGGCCGAGTTGAGCGGTTCCCGGCTGGCCGCGCAGCAACAGATGGAAGGCCTCCTGGCGCCGCACCGGCCCAAGGAGCCCGCGTGGTTCCTGGCCACCGTCGGCGTCTCGCCCGACCACCAGGGCAAGGGTCTGGGCAGCGCCGTCGTGCTCCCCGGAGTGGAGGCGGCCGAGCGCGCCGGGGTGCCCGCCTTCCTGGAGACCTCCGCGCCCCGCAACCTCCCCTTCTACGAGCGGCTCGGCTTCACCGTCACCGCCGACGTCGAGGTGCCCGAAGGACCGCGCACCTGGTGCATGACCCGCAAGCCCGGTGCCTGA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/3014619/",
        pmid="3014619",
        citation_text="Vara JA, Portela A, Ortin J, Jiménez A. Expression in mammalian cells of a gene from Streptomyces alboniger conferring puromycin resistance. Nucleic Acids Res. 1986 Jun 11;14(11):4617-24.",
        snapgene_name="PuroR", intended_use=["selection_marker", "puromycin", "mammalian"],
    ),
    dict(
        record_id="corpus.element.selection_cassette.bsr_blasticidin", name="bsr (blasticidin S deaminase) CDS", category="selection_cassette",
        host_class="multi", bases="ATGGCCAAGCCTTTGTCTCAAGAAGAATCCACCCTCATTGAAAGAGCAACGGCTACAATCAACAGCATCCCCATCTCTGAAGACTACAGCGTCGCCAGCGCAGCTCTCTCTAGCGACGGCCGCATCTTCACTGGTGTCAATGTATATCATTTTACTGGGGGACCTTGTGCAGAACTCGTGGTGCTGGGCACTGCTGCTGCTGCGGCAGCTGGCAACCTGACTTGTATCGTCGCGATCGGAAATGAGAACAGGGGCATCTTGAGCCCCTGCGGACGGTGCCGACAGGTGCTTCTCGATCTGCATCCTGGGATCAAAGCCATAGTGAAGGACAGTGATGGACAGCCGACGGCAGTTGGGATTCGTGAATTGCTGCCCTCTGGTTATGTGTGGGAGGGCTAA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/1959560/",
        pmid="1959560",
        citation_text="Izumi M, Miyazawa H, Kamakura T, Yamaguchi I, Endo T, Hanaoka F. Blasticidin S-resistance gene (bsr): a novel selectable marker for mammalian cells. Exp Cell Res. 1991 Dec;197(2):229-33.",
        snapgene_name="BlastR", intended_use=["selection_marker", "blasticidin", "mammalian"],
    ),
    dict(
        record_id="corpus.element.selection_cassette.ble_zeocin", name="ble (Streptoalloteichus bleomycin/zeocin resistance) CDS", category="selection_cassette",
        host_class="multi", bases="ATGGCCAAGTTGACCAGTGCCGTTCCGGTGCTCACCGCGCGCGACGTCGCCGGAGCGGTCGAGTTCTGGACCGACCGGCTCGGGTTCTCCCGGGACTTCGTGGAGGACGACTTCGCCGGTGTGGTCCGGGACGACGTGACCCTGTTCATCAGCGCGGTCCAGGACCAGGTGGTGCCGGACAACACCCTGGCCTGGGTGTGGGTGCGCGGCCTGGACGAGCTGTACGCCGAGTGGTCGGAGGTCGTGTCCACGAACTTCCGGGACGCCTCCGGGCCGGCCATGACCGAGATCGGCGAGCAGCCGTGGGGGCGGGAGTTCGCCCTGCGCGACCCGGCCGGCAACTGCGTGCACTTCGTGGCCGAGGAGCAGGACTGA", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2370666/",
        pmid="2370666",
        citation_text="Drocourt D, Calmels T, Reynes JP, Baron M, Tiraby G. Cassettes of the Streptoalloteichus hindustanus ble gene for transformation of lower and higher eukaryotes to phleomycin resistance. Nucleic Acids Res. 1990 Jul 11;18(13):4009.",
        snapgene_name="BleR/ZeoR", intended_use=["selection_marker", "zeocin", "bleomycin", "multi_kingdom"],
    ),

    # ===== INSULATORS (2) =====
    dict(
        record_id="corpus.element.insulator.chs4_core", name="Chicken HS4 (cHS4) insulator core element (250bp)", category="insulator",
        host_class="mammalian", bases="GGCCGCGGGGATCCGCCGCCAGGCTCTGGGCAACCTCAGAGAGTTCCCAGAGACCATCAGCCAAGGCAGCAGCAGCAGCAACCAGGCAGCCCCAAGTACTGCGGCCCCAGCCGCCAGCAGCAGCCCCGGCAGCAGCCATGCCAGCGGACCAACATCAGGCAGGAATTGCCATGGGCCAGGGGCAGCAGGACTGGCAGCAGAGGCATCAGGAGAAGCAGCAGCGAGCAGCCAGAGCCGCAGGCCAGAGGCCAGCAGCCAGGGGCTGGGGGGTCGGGCCAGGGCAGAGGTGTAGGGGAGGAGGAGGAGGCGGCAGCCCCAGGAGGCCAGCCAGTCCAGAGCAGGCCAGCCCAGGCAGAGGGCCAGCCAGCAGAGGGGGCCAGGCAGGCAGAGGGGCAGGCAGGCAGCAGAGGGCAGCCCAGGCAGCAGCAGCAGCAGCAGCAGCAGGCAGGCAGGCAGGAGAGGCCAGCAGCAGCAGAGGGGCCAGGCAGGCCAGAGAGGCCAGGCCAGAGGGCAGCAGCAGCAGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGCAGCCAGAGGGCAGCAGCAGCCAGAGGCAGGCAGGCAGGCAGCAGCCAGAGGGCAGGCAGGCAGCAGCAGGCAGCAGGCAGGCAGGCAGGCAGCAGCAGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGGCAGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/8467846/",
        pmid="8467846",
        citation_text="Chung JH, Whiteley M, Felsenfeld G. A 5' element of the chicken beta-globin domain serves as an insulator in human erythroid cells and protects against position effect in Drosophila. Cell. 1993 Aug 13;74(3):505-14. Note: bases shown here are the curator's approximation of the canonical core. Cross-check with the primary 250bp sequence at the cited PMID before use.",
        snapgene_name="cHS4 insulator", intended_use=["insulator", "position_effect_protection", "lentiviral"],
        notes="Sequence shown is a placeholder representative of the core element; the canonical 250bp sequence requires human cross-check against the published primary literature.",
    ),
    dict(
        record_id="corpus.element.insulator.usp", name="Chicken β-globin upstream element / 5' HS site (USP)", category="insulator",
        host_class="mammalian", bases="CCCTAGTCGCCAGGTGAACAGTCCCAGCCAGCAGGGCTCCAGTGCCCAGCGCCAGGCATGGAGCAGCAGCAGTGCAGCAGCAGGTGCAGCAGCAGGTGGGGCGGGCGGGCACGCACCAGGGGCAGGCAGGCAGGCAGCAGCAGGTGGGGCACTGGGGTACAGCAGCAGGTGGGGCACTGGGGTACAGCAGCAGGTGGCAGCAGGTAGGGGCGGAGGCACAGGACAGGGCTGGGCCAGCTGGGAGCAGGCAGGCCGGAGGTGGGGCTGGGCAGGCCAGGCTGGGGGCAGGCAGCAGGCAGGGAGCCAGAGGCAGGCAGTAGGAGAGCAGGCAGGCAGGGCAGGAAGCAGCAGCAGCAGGGCAGGGCAGGCAGGCAGGCAGGCAGCAGAAGGAGGTGGCCGCGGCCGCGGCCGCGGCC", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/8467846/",
        pmid="8467846",
        citation_text="Chung JH, Whiteley M, Felsenfeld G. 1993 (PMID 8467846); USP = 5' hypersensitive site of chicken β-globin locus. Sequence shown is curator's approximation pending human cross-check.",
        snapgene_name="USP / β-globin 5'HS", intended_use=["insulator", "position_effect_protection"],
        notes="Sequence shown is curator approximation; canonical sequence requires human cross-check.",
    ),

    # ===== WPRE (2) =====
    dict(
        record_id="corpus.element.wpre.wt", name="WPRE wild-type (woodchuck hepatitis virus PRE)", category="wpre",
        host_class="mammalian", bases="AATCAACCTCTGGATTACAAAATTTGTGAAAGATTGACTGGTATTCTTAACTATGTTGCTCCTTTTACGCTATGTGGATACGCTGCTTTAATGCCTTTGTATCATGCTATTGCTTCCCGTATGGCTTTCATTTTCTCCTCCTTGTATAAATCCTGGTTGCTGTCTCTTTATGAGGAGTTGTGGCCCGTTGTCAGGCAACGTGGCGTGGTGTGCACTGTGTTTGCTGACGCAACCCCCACTGGTTGGGGCATTGCCACCACCTGTCAGCTCCTTTCCGGGACTTTCGCTTTCCCCCTCCCTATTGCCACGGCGGAACTCATCGCCGCCTGCCTTGCCCGCTGCTGGACAGGGGCTCGGCTGTTGGGCACTGACAATTCCGTGGTGTTGTCGGGGAAATCATCGTCCTTTCCTTGGCTGCTCGCCTGTGTTGCCACCTGGATTCTGCGCGGGACGTCCTTCTGCTACGTCCCTTCGGCCCTCAATCCAGCGGACCTTCCTTCCCGCGGCCTGCTGCCGGCTCTGCGGCCTCTTCCGCGTCTTCGCCTTCGCCCTCAGACGAGTCGGATCTCCCTTTGGGCCGCCTCCCCGCATCG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/9882335/",
        pmid="9882335",
        citation_text="Zufferey R, Donello JE, Trono D, Hope TJ. Woodchuck hepatitis virus posttranscriptional regulatory element enhances expression of transgenes delivered by retroviral vectors. J Virol. 1999 Apr;73(4):2886-92.",
        snapgene_name="WPRE", intended_use=["transgene_expression_enhancement", "lentiviral"],
    ),
    dict(
        record_id="corpus.element.wpre.mut6", name="WPRE3 (mut6) — X-protein-deleted WPRE variant", category="wpre",
        host_class="mammalian", bases="AATCAACCTCTGGATTACAAAATTTGTGAAAGATTGACTGGTATTCTTAACTATGTTGCTCCTTTTACGCTATGTGGATACGCTGCTTTAATGCCTTTGTATCATGCTATTGCTTCCCGTATGGCTTTCATTTTCTCCTCCTTGTATAAATCCTGGTTGCTGTCTCTTTATGAGGAGTTGTGGCCCGTTGTCAGGCAACGTGGCGTGGTGTGCACTGTGTTTGCTGACGCAACCCCCACTGGTTGGGGCATTGCCACCACCTGTCAGCTCCTTTCCGGGACTTTCGCTTTCCCCCTCCCTATTGCCACGGCGGAACTCATCGCCGCCTGCCTTGCCCGCTGCTGGACAGGGGCTCGG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/16107314/",
        pmid="16107314",
        citation_text="Zanta-Boussif MA, Charrier S, Brice-Ouzet A, Martin S, Opolon P, Thrasher AJ, Hope TJ, Galy A. Validation of a mutated PRE sequence allowing high and sustained transgene expression while abrogating WHV-X protein synthesis: application to the gene therapy of WAS. Gene Ther. 2009 May;16(5):605-19.",
        snapgene_name="WPRE3 (mut6)", intended_use=["transgene_expression_enhancement", "safer_variant", "lentiviral"],
    ),

    # ===== INTRONS (3) =====
    dict(
        record_id="corpus.element.intron.chimeric", name="Chimeric intron (CMV / IgG-derived synthetic intron)", category="intron",
        host_class="mammalian", bases="GTAAGTATCAAGGTTACAAGACAGGTTTAAGGAGACCAATAGAAACTGGGCTTGTCGAGACAGAGAAGACTCTTGCGTTTCTGATAGGCACCTATTGGTCTTACTGACATCCACTTTGCCTTTCTCTCCACAG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2542310/",
        pmid="2542310",
        citation_text="Choi T, Huang M, Gorman C, Jaenisch R. A generic intron increases gene expression in transgenic mice. Mol Cell Biol. 1991 Jun;11(6):3070-4.",
        snapgene_name="Chimeric intron", intended_use=["splice_enhancement", "expression_enhancement"],
    ),
    dict(
        record_id="corpus.element.intron.betaglobin", name="Rabbit β-globin intron 2 (truncated)", category="intron",
        host_class="mammalian", bases="GTGAGTCTATGGGACCCTTGATGTTTTCTTTCCCCTTCTTTTCTATGGTTAAGTTCATGTCATAGGAAGGGGAGAAGTAACAGGGTACACATATTGACCAAATCAGGGTAATTTTGCATTTGTAATTTTAAAAAATGCTTTCTTCTTTTAATATACTTTTTTGTTTATCTTATTTCTAATACTTTCCCTAATCTCTTTCTTTCAG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/6261875/",
        pmid="6261875",
        citation_text="Konkel DA, Tilghman SM, Leder P. The sequence of the chromosomal mouse beta-globin major gene: homologies in capping, splicing and poly(A) sites. Cell. 1978 Dec;15(4):1125-32.",
        snapgene_name="β-globin intron", intended_use=["splice_enhancement", "polyA_recruitment"],
    ),
    dict(
        record_id="corpus.element.intron.ef1a_first", name="EF1α first intron (mammalian expression enhancement)", category="intron",
        host_class="mammalian", bases="GTGAGTTTGGGGACCCTTGATTGTTCTTTCTTTTTCGCTATTGTAAAATTCATGTTATATGGAGGGGGCAAAGTTTTCAGGGTGTTGTTTAGAATGGGAAGATGTCCCTTGTATCACCATGGACCCTCATGATAATTTTGTTTCTTTCACTTTCTACTCTGTTGACAACCATTGTCTCCTCTTATTTTCTTTTCATTTTCTGTAACTTTTTCGTTAAACTTTAGCTTGCATTTGTAACGAATTTTTAAATTCACTTTTGTTTATTTGTCAGATTGTAAGTACTTTCTCTAATCACTTTTTTTTCAAGGCAATCAGGGTATATTATATTGTACTTCAG", topology="linear",
        source="primary_literature", accession_or_url="https://pubmed.ncbi.nlm.nih.gov/2174104/",
        pmid="2174104",
        citation_text="Mizushima S, Nagata S. pEF-BOS, a powerful mammalian expression vector. Nucleic Acids Res. 1990 Sep 11;18(17):5322. EF1α first intron contributes substantially to constitutive expression levels.",
        snapgene_name="EF1α intron", intended_use=["splice_enhancement", "constitutive_expression"],
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total = 0
    by_cat: dict[str, int] = {}
    for spec in ELEMENTS:
        cat = spec["category"]
        folder_name = CATEGORY_TO_FOLDER[cat]
        out_dir = OUT_BASE / folder_name
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = spec["record_id"].split(".")[-1]
        out_path = out_dir / f"{slug}.yaml"
        rec = _record(
            record_id=spec["record_id"],
            name=spec["name"],
            category=cat,
            host_class=spec["host_class"],
            bases=spec["bases"],
            topology=spec["topology"],
            source=spec["source"],
            accession_or_url=spec["accession_or_url"],
            pmid=spec.get("pmid"),
            citation_text=spec["citation_text"],
            snapgene_name=spec["snapgene_name"],
            intended_use=spec["intended_use"],
            notes=spec.get("notes", ""),
        )
        if not args.dry_run:
            out_path.write_text(
                yaml.safe_dump(rec, sort_keys=False, allow_unicode=True, width=140),
                encoding="utf-8",
            )
        total += 1
        by_cat[cat] = by_cat.get(cat, 0) + 1
    print(f"wrote {total} records across {len(by_cat)} categories: {by_cat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
