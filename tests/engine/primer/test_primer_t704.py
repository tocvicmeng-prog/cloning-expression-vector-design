"""
module_id: tests.engine.primer
file: tests/engine/primer/test_primer_t704.py
task_id: T-704
"""

from __future__ import annotations

import pytest

from engine.assembly import AssemblyPart
from engine.primer import (
    DiagnosticPrimerDesigner,
    PrimerDesigner,
    PrimerDesignParameters,
    SequencingPrimerDesigner,
    SequencingPrimerRequest,
    reverse_complement,
    scan_off_targets,
)
from engine.sequence_analysis import RestrictionEnzyme, WrongCloneModel


def _template() -> str:
    return "ATGCGTACGTAGCTAGCTAGAAAACCCCGGGGTTTTGCGCGCAATTAACCGGTT"


def test_primer_parameters_validate_ranges() -> None:
    assert PrimerDesignParameters().target_tm_midpoint_C == 60.0

    with pytest.raises(ValueError, match="length_range"):
        PrimerDesignParameters(length_range=(8, 20))


def test_primer_designer_returns_pair_with_tm_and_backend() -> None:
    designer = PrimerDesigner()
    pair = designer.design_pair(_template(), target_id="insert")

    assert pair.target_id == "insert"
    assert pair.product_size == len(_template())
    assert pair.forward.tm_C >= 55.0
    assert pair.reverse.sequence == reverse_complement(_template())[: len(pair.reverse.sequence)]
    assert designer.backend in {"primer3", "deterministic-fallback"}


def test_primer_designer_handles_assembly_parts_and_off_target_warnings() -> None:
    repeated = _template() + "GGTT" + _template()
    parts = (AssemblyPart(id="part-a", sequence=_template()),)
    primer_set = PrimerDesigner(
        PrimerDesignParameters(max_off_target_seed_hits=1)
    ).design_for_parts(parts, full_plasmid=repeated)

    assert len(primer_set.pairs) == 1
    assert primer_set.warnings
    assert "multiple plasmid hits" in primer_set.warnings[0]


def test_scan_off_targets_finds_forward_and_reverse_seed_hits() -> None:
    primer = "AACCCCGGGTTA"
    template = f"TTT{primer}AAA{reverse_complement(primer)}CCC"

    hits = scan_off_targets(primer, template, seed_length=12)

    assert tuple(hit.strand for hit in hits) == ("+", "-")


def test_sequencing_primer_designer_places_primers_upstream_of_junctions() -> None:
    sequence = "A" * 120 + "C" * 120 + "G" * 120
    primers = SequencingPrimerDesigner().design(
        SequencingPrimerRequest(
            target_id="construct",
            template=sequence,
            junction_positions=(150, 250),
        )
    )

    assert len(primers) == 2
    assert all(primer.direction == "sequencing" for primer in primers)
    assert all(18 <= len(primer.sequence) <= 35 for primer in primers)


def test_diagnostic_primer_designer_wraps_distinguishing_digest() -> None:
    ecori = RestrictionEnzyme.from_cut_notation("EcoRI", "G^AATTC")
    bamhi = RestrictionEnzyme.from_cut_notation("BamHI", "G^GATCC")
    design = DiagnosticPrimerDesigner().design(
        "AAAAGAATTCCCCCGGATCCGGGTTTTAAAACCCCGGGGTTTT",
        (
            WrongCloneModel("empty_vector", "AAAAGAATTCCCCCGGGTTTTAAAACCCCGGGGTTTT"),
            WrongCloneModel("reverse_insert", "AAAAGAATTCCGGATCCGGGTTTTAAAACCCCGGGGTTTT"),
        ),
        (ecori, bamhi),
        topology="linear",
    )

    assert design is not None
    assert design.digest.distinguishes_all
    assert design.primer_pair.target_id == "diagnostic"
